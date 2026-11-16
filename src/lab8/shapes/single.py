"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import (
    compute_compensation,
    get_claim_view,
    lookup_order,
    tool_cost,
)
from lab8.trace import Trace
from lab8.mock_llm import complete


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
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)
    trace.add("shape", {"status": "started"})

    # Step 1: read claim
    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status="failed", proposal_amount=0, budget=budget, trace=trace,
            error_reason="unknown_claim",
        )

    # Model call: analyse the ticket
    complete(budget, seed=seed, purpose="analyse", prompt=claim_view.get("ticket", ""))

    # Step 2: missing order_id
    if not claim_view.get("order_id"):
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status="needs_info", proposal_amount=0, budget=budget, trace=trace,
        )

    # Step 3: lookup order
    budget.add_tool(tool_cost())
    order_res = lookup_order(conn, claim_view.get("order_id"), claim_view["principal_id"])
    if not order_res.get("visible"):
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        trace.add("decision", {"status": "escalated"})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status="escalated", proposal_amount=0, budget=budget, trace=trace,
            error_reason=order_res.get("reason"),
        )

    # Step 4: compute compensation
    order = order_res.get("order", {})
    budget.add_tool(tool_cost())
    quote_res = compute_compensation(conn, order)
    amount = int(quote_res.get("amount_vnd", 0))
    trace.add("quote", quote_res)

    # Step 5: zero → denied
    if amount <= 0:
        complete(budget, seed=seed, purpose="draft", prompt="denied")
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status="denied", proposal_amount=amount, budget=budget, trace=trace,
            error_reason=quote_res.get("reason"),
        )

    # Step 6: host issues refund
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={amount}")
    try:
        refund_res = issue_refund(conn, claim_id, amount, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if refund_res.get("ok"):
        final_status = "resolved"
        err = None
    else:
        final_status = "failed" if refund_res.get("conflict") else "denied"
        err = refund_res.get("reason")

    return finish(
        conn, shape="single", claim_id=claim_id, seed=seed,
        status=final_status, proposal_amount=amount, budget=budget, trace=trace,
        error_reason=err,
    )
