"""Shape C — orchestrator plus read-only investigators.

The orchestrator builds an allowlisted handoff, lets read-only investigators
fetch the order and quote, then calls the host gate (`durability.issue_refund`)
itself. The ticket text is never used to decide money; only the order row is.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim_row = conn.execute(
        "SELECT claim_id, principal_id, order_id FROM claims WHERE claim_id = ?",
        (claim_id,),
    ).fetchone()
    if claim_row is None:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", reason="unknown_claim")

    if not claim_row["order_id"]:
        trace.add("decision", {"status": "needs_info"})
        return done("needs_info", reason="missing_order_id")

    # Orchestrator -> investigator: allowlisted facts only, read-only tools.
    # lookup_order must come before compute_compensation (the quote needs the order).
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    complete(budget, seed=seed, purpose="plan", prompt=f"handoff:{claim_id}")

    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim_row["principal_id"]
    )
    order_view = investigated["tools"].get("lookup_order", {})
    trace.add(
        "investigator",
        {
            "lookup_order": order_view,
            "policy_count": len((investigated["tools"].get("lookup_policy") or {}).get("policies") or []),
        },
    )
    if not order_view.get("visible"):
        trace.add("decision", {"status": "escalated", "reason": order_view.get("reason")})
        return done("escalated", reason=order_view.get("reason"))

    quote_payload = investigated["tools"].get("compute_compensation") or {}
    trace.add("quote", quote_payload)
    proposal = int(quote_payload.get("amount_vnd") or 0)
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return done("denied", reason=quote_payload.get("reason"))

    try:
        # Full quote: the host subtracts refunds already paid on the same order.
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal)
