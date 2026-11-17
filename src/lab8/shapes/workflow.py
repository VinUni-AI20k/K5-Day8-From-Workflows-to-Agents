"""Shape A — deterministic workflow.

Money calculation, policy enforcement, per-order cap, and idempotency stay in code/host.
No model calls are made in this shape.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"
CLAIM_TRACE_KEYS = ("found", "claim_id", "order_id")
ORDER_TRACE_KEYS = ("visible", "reason", "order")


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    """Execute deterministic claim resolution workflow."""
    try:
        conn = connect(store_path)
    except Exception:
        return _failed_result(claim_id, seed)

    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    except InjectedCrash:
        raise
    except Exception:
        return _failed_result(claim_id, seed, conn)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("claim", {key: claim.get(key) for key in CLAIM_TRACE_KEYS})
    if not claim.get("found"):
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )
    if not claim.get("order_id"):
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    budget.add_tool(tool_cost())
    visible = lookup_order(conn, claim["order_id"], claim["principal_id"])
    trace.add("order", {key: visible.get(key) for key in ORDER_TRACE_KEYS})
    if not visible.get("visible"):
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=visible.get("reason"),
        )

    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, visible["order"])
    proposal = int(quote["amount_vnd"])
    trace.add("quote", quote)
    if proposal <= 0:
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote.get("reason"),
        )

    return _commit_or_deny(
        conn,
        claim_id=claim_id,
        seed=seed,
        proposal=proposal,
        budget=budget,
        trace=trace,
        crash_at=crash_at,
    )


def _commit_or_deny(
    conn: sqlite3.Connection,
    *,
    claim_id: str,
    seed: int,
    proposal: int,
    budget: Budget,
    trace: Trace,
    crash_at: str | None,
) -> RunResult:
    try:
        outcome: dict[str, Any] = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )
    return finish(
        conn,
        shape=SHAPE,
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
    )


def _failed_result(
    claim_id: str,
    seed: int,
    conn: sqlite3.Connection | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))
    trace.add("error", {"reason": "internal_error"})
    if conn is not None:
        try:
            return finish(
                conn,
                shape=SHAPE,
                claim_id=claim_id,
                seed=seed,
                status="failed",
                proposal_amount=0,
                budget=budget,
                trace=trace,
                error_reason="internal_error",
            )
        except Exception:
            pass
    path = trace.write()
    return RunResult(
        run_id=trace.run_id,
        claim_id=claim_id,
        shape=SHAPE,
        seed=seed,
        status="failed",
        proposal_amount=0,
        refund_effects=[],
        committed_audit_count=0,
        model_calls=0,
        tool_calls=0,
        input_tokens=0,
        output_tokens=0,
        cost_estimate=0.0,
        trace_path=path,
        error_reason="internal_error",
    )
