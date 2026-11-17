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
from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
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


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
) -> RunResult:
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)

    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view["found"]:
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    if not claim_view.get("order_id"):
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    order_id = claim_view["order_id"]
    principal_id = claim_view["principal_id"]

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        last_tool = seen.get("last_tool")
        if last_tool is None:
            complete(budget, seed=seed, purpose="decide", prompt=f"claim={claim_id}")
            return {
                "tool": "lookup_order",
                "args": {"order_id": order_id, "principal_id": principal_id},
            }
        if last_tool == "lookup_order":
            order_view = seen["last_result"]
            trace.add(
                "react_step",
                {
                    "tool": "lookup_order",
                    "visible": order_view.get("visible"),
                    "reason": order_view.get("reason"),
                },
            )
            if not order_view.get("visible"):
                complete(budget, seed=seed, purpose="draft", prompt="escalated")
                return {
                    "final": {
                        "status": "escalated",
                        "proposal": 0,
                        "error_reason": order_view.get("reason"),
                    }
                }
            complete(budget, seed=seed, purpose="decide", prompt=f"order={order_id}")
            return {
                "tool": "compute_compensation",
                "args": {"order": order_view["order"]},
            }
        if last_tool == "compute_compensation":
            quote_payload = seen["last_result"]
            proposal = int(quote_payload["amount_vnd"])
            trace.add("quote", quote_payload)
            complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
            return {
                "final": {
                    "status": "quoted",
                    "proposal": proposal,
                    "error_reason": quote_payload.get("reason"),
                }
            }
        return {"final": {"status": "failed", "proposal": 0, "error_reason": "unexpected_step"}}

    react_out = run_react(
        conn,
        budget,
        observation={"claim": {"claim_id": claim_id, "order_id": order_id}},
        decide=decide,
        max_steps=8,
        worker=False,
    )
    final = react_out["final"]

    if react_out["stopped"] == "step_cap" or final.get("status") == "failed":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason", "step_cap"),
        )

    if final.get("status") == "escalated":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason"),
        )

    proposal = int(final.get("proposal", 0))
    if proposal <= 0:
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason"),
        )

    # TODO CP3 (student): truyền crash_at vào durability.issue_refund, không bắt InjectedCrash.
    del crash_at
    outcome = issue_refund(conn, claim_id, proposal)

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape="single",
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
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
