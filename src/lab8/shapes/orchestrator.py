"""Shape C: a planner delegates sanitized, read-only investigation to workers."""

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
    shape = "orchestrator"
    budget = Budget()
    trace = Trace(make_run_id(shape, claim_id, seed))

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("claim", {key: claim.get(key) for key in ("found", "claim_id", "order_id")})
    if not claim["found"]:
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="failed",
                      proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim")
    if not claim.get("order_id"):
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="needs_info",
                      proposal_amount=0, budget=budget, trace=trace, error_reason="missing_order_id")

    handoff = make_handoff(
        request_id=f"REQ-{claim_id}", claim_id=claim_id,
        task="verify_order_policy_and_compensation", facts={},
        allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"],
    )
    trace.add("handoff", safe_dump(handoff))
    plan = complete(budget, seed=seed, purpose="orchestrate", prompt=f"Investigate refund claim {claim_id}")
    trace.add("plan", {"request_id": handoff["request_id"], "ref": plan.rsplit(" ", 1)[-1]})

    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim["principal_id"]
    )
    trace.add("investigation", safe_dump(investigated))
    tools = investigated["tools"]
    order_result = tools.get("lookup_order", {})
    if not order_result.get("visible"):
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="escalated",
                      proposal_amount=0, budget=budget, trace=trace,
                      error_reason=order_result.get("reason", "order_not_visible"))

    quote = tools.get("compute_compensation", {})
    proposal = int(quote.get("amount_vnd", 0))
    trace.add("quote", quote)
    if proposal <= 0:
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="denied",
                      proposal_amount=0, budget=budget, trace=trace,
                      error_reason=quote.get("reason", "not_eligible"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed,
                      status="failed" if outcome["conflict"] else "denied",
                      proposal_amount=proposal, budget=budget, trace=trace,
                      error_reason=outcome["reason"])
    return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="resolved",
                  proposal_amount=proposal, budget=budget, trace=trace)
