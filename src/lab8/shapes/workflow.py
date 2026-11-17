"""Shape A — quote from order data and send eligible refunds through the host."""

from __future__ import annotations

from contextlib import closing
import sqlite3

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


# The host can include a stored approval status in its reason.
SAFE_DENIAL_REASONS = {
    "approval_claim_mismatch",
    "approval_expired",
    "approval_revoked",
    "capped_to_zero",
    "missing_approval",
    "missing_order",
    "non_positive_amount",
    "order_already_refunded",
    "order_total_changed",
    "outside_principal_scope",
    "unknown_claim",
}


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("workflow", claim_id, seed))
    with closing(connect(store_path)) as conn:
        status, proposal, reason = _resolve(conn, claim_id, budget, trace, crash_at)
        trace.add("decision", {"status": status, "reason": reason})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )


def _resolve(
    conn: sqlite3.Connection,
    claim_id: str,
    budget: Budget,
    trace: Trace,
    crash_at: str | None,
) -> tuple[str, int, str | None]:
    cost = tool_cost()
    budget.add_tool(cost)
    trace.add("get_claim_view", {})
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        return "failed", 0, "unknown_claim"
    if not claim["order_id"]:
        return "needs_info", 0, "missing_order_id"

    budget.add_tool(cost)
    trace.add("lookup_order", {})
    order = lookup_order(conn, claim["order_id"], claim["principal_id"])
    if not order["visible"]:
        return "escalated", 0, order["reason"]

    budget.add_tool(cost)
    trace.add("compute_compensation", {})
    proposal = compute_compensation(conn, order["order"])["amount_vnd"]
    if proposal == 0:
        return "denied", 0, "no_entitlement"

    budget.add_tool(cost)
    trace.add("issue_refund", {})
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    if outcome["ok"]:
        return "resolved", proposal, None
    if outcome["conflict"]:
        return "failed", proposal, "amount_conflict"

    reason = outcome["reason"]
    return "denied", proposal, reason if reason in SAFE_DENIAL_REASONS else "policy_denied"
