"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3
from functools import partial

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Run one claim through the deterministic workflow shape.

    Args:
        claim_id: Claim to process.
        seed: Run seed, only used to build the run_id (no model call here).
        store_path: Path to the SQLite store.
        crash_at: Crash injection point for durability tests (wired in CP3).

    Returns:
        RunResult with status needs_info / escalated / denied / resolved / failed
        and a trace_path written on every return path.
    """
    # TODO CP3 (student): truyền crash_at vào durability.issue_refund, không bắt InjectedCrash.
    del crash_at
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int) -> RunResult:
    """Execute the workflow steps on an open connection."""
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))
    done = partial(
        finish, conn, shape=SHAPE, claim_id=claim_id, seed=seed, budget=budget, trace=trace
    )

    # 1. Read the claim through the view (not SELECT *).
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        trace.add("decision", {"status": "failed", "reason": "unknown_claim"})
        return done(status="failed", proposal_amount=0, error_reason="unknown_claim")
    trace.add("claim", {"claim_id": claim_id, "has_order_id": bool(claim["order_id"])})

    # 2. Missing order_id -> needs_info. No ledger write.
    if not claim["order_id"]:
        trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
        return done(status="needs_info", proposal_amount=0, error_reason="missing_order_id")

    # 3. lookup_order inside the principal's scope.
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    # Only visible/reason go to the trace: no phone, address, item, internal note.
    trace.add("lookup_order", {"visible": order_view["visible"], "reason": order_view["reason"]})
    if not order_view["visible"]:
        trace.add("decision", {"status": "escalated", "reason": order_view["reason"]})
        return done(status="escalated", proposal_amount=0, error_reason=order_view["reason"])

    # 4. Quote from the order row. The ticket text is never parsed for numbers.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    proposal = int(quote["amount_vnd"])
    trace.add("quote", safe_dump(quote))

    # 5. Nothing owed -> denied, issue_refund is not called.
    if proposal <= 0:
        trace.add("decision", {"status": "denied", "reason": quote["reason"]})
        return done(status="denied", proposal_amount=0, error_reason=quote["reason"])

    # 6. Pass the FULL quote. The host checks approval and subtracts earlier refunds.
    outcome = issue_refund(conn, claim_id, proposal)
    trace.add("issue_refund", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        trace.add("decision", {"status": status, "reason": outcome["reason"]})
        return done(status=status, proposal_amount=proposal, error_reason=outcome["reason"])

    # 7. Committed (or idempotent replay) -> resolved.
    trace.add("decision", {"status": "resolved", "reason": outcome["reason"]})
    return done(status="resolved", proposal_amount=proposal, error_reason=None)
