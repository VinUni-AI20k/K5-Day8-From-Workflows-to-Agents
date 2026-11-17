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

Implementation notes (team):
- The orchestrator makes one "plan" model call and one "draft" call. The plan
  text is not used for any decision; the investigator tool list is fixed in code.
- Handoff facts are empty: the investigator re-reads the order itself through
  lookup_order (principal-scoped), so nothing from the parent context crosses
  the boundary except ids and the allowlisted task fields.
- No REFERENCE_WEAKNESS: the delay always comes from the order row.
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
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]


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

    def done(status: str, amount: int, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(amount), "reason": reason})
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=amount,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim")
    if not claim.get("order_id"):
        return done("needs_info", 0, "missing_order_id")

    # Orchestrator plans. The plan text does not choose tools or money.
    complete(budget, seed=seed, purpose="plan", prompt=f"claim={claim_id}|task=check_applicable_policy")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=list(INVESTIGATOR_TOOLS),
    )
    trace.add("handoff", safe_dump(handoff))

    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    history = tools.get("lookup_refund_history") or {}
    trace.add(
        "investigator",
        {
            "order_visible": bool(order_view.get("visible")),
            "order": dict(order_view["order"]) if order_view.get("visible") else None,
            "policy_count": len((tools.get("lookup_policy") or {}).get("policies") or []),
            "refunded_vnd": history.get("refunded_vnd") if history.get("visible") else None,
        },
    )
    if not order_view.get("visible"):
        return done("escalated", 0, order_view.get("reason"))

    quote = tools.get("compute_compensation") or {}
    trace.add("quote", quote)
    proposal = int(quote.get("amount_vnd") or 0)
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # Only the orchestrator writes, and only through the host.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": bool(outcome["ok"]), "reason": outcome["reason"]})

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])
    return done("resolved", proposal, None)
