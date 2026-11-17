"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8 import durability
from lab8.db import connect
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
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

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        # Orchestrator drafts the final reply based on the verified decision only.
        # Ticket text is never included in the prompt.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status} amount={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
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

    # 1. Read allowlisted claim view. Never trace raw claim row, parent_secret, raw_headers, or ticket.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("get_claim_view", {"found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
    if not claim["found"]:
        return done("failed", 0, "unknown_claim")

    if not claim["order_id"]:
        return done("needs_info", 0, "missing_order_id")

    # 2. Build a typed, allowlisted handoff with read-only tools for the investigator.
    complete(budget, seed=seed, purpose="orchestrate", prompt=f"delegate claim={claim_id}")
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="investigate_order_and_quote",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))

    # 3. Run read-only investigators across the handoff boundary.
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim["principal_id"]
    )
    tools_out = investigated["tools"]
    order_view = tools_out.get("lookup_order") or {}
    history_view = tools_out.get("lookup_refund_history") or {}
    policies = (tools_out.get("lookup_policy") or {}).get("policies") or []

    if not order_view.get("visible"):
        trace.add(
            "investigator",
            {
                "visible": False,
                "reason": order_view.get("reason"),
                "policy_count": len(policies),
            },
        )
        return done("escalated", 0, order_view.get("reason"))

    quote = tools_out.get("compute_compensation") or {}
    amount = int(quote.get("amount_vnd") or 0)
    trace.add(
        "investigator",
        {
            "visible": True,
            "order": order_view["order"],
            "policy_count": len(policies),
            "refund_history": {
                "refund_count": history_view.get("refund_count", 0),
                "refunded_vnd": history_view.get("refunded_vnd", 0),
            },
            "quote": {
                "amount_vnd": amount,
                "reason": quote.get("reason"),
                "clause_ids": quote.get("clause_ids"),
            },
        },
    )

    if amount <= 0:
        return done("denied", 0, quote.get("reason"))

    # 4. Orchestrator calls host durability gate with the FULL quote.
    #    Host enforces approval, per-order cap, idempotency, and crash points.
    try:
        outcome = durability.issue_refund(conn, claim_id, amount, crash_at=crash_at)
    except durability.InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    trace.add(
        "issue_refund",
        {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]},
    )
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", amount, outcome["reason"])

    return done("resolved", amount, None)
