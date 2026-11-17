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
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
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
    # TODO CP2 (student): thay stub này bằng shape single theo các bước ở docstring đầu file.
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
    crash_at: str | None = None,
) -> RunResult:
    # Khởi tạo budget, trace, đọc claim
    budget = Budget()
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)

    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view.get("found"):
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

    # React Agent Loop (max_steps = 8, only read tools)

    step_count = 0

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        nonlocal step_count
        step_count += 1

        last_tool = seen.get("last_tool")
        last_result = seen.get("last_result") or {}
        claim = seen.get("claim") or claim_view

        # Check missing order_id -> needs_info
        if not claim.get("order_id"):
            complete(budget, seed=seed, purpose="draft", prompt="needs_info")
            return {
                "final": {
                    "status": "needs_info",
                    "proposal_amount": 0,
                    "reason": "missing_order_id",
                }
            }

        # Step 1: Initial call -> lookup order
        if last_tool is None:
            thought = complete(budget, seed=seed, purpose="decide", prompt=f"lookup_order {claim.get('order_id')}")
            trace.add("react_thought", {"step": step_count, "thought": thought})
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim.get("order_id"),
                    "principal_id": claim.get("principal_id"),
                },
            }

        # Step 2: After lookup_order -> check visibility and compute compensation
        if last_tool == "lookup_order":
            trace.add("react_observation", {"tool": "lookup_order", "visible": last_result.get("visible")})
            if not last_result.get("visible"):
                complete(budget, seed=seed, purpose="draft", prompt="escalated")
                return {
                    "final": {
                        "status": "escalated",
                        "proposal_amount": 0,
                        "reason": last_result.get("reason", "order_not_found"),
                    }
                }
            order = dict(last_result.get("order") or {})
            thought = complete(budget, seed=seed, purpose="decide", prompt=f"compute_compensation {order.get('order_id')}")
            trace.add("react_thought", {"step": step_count, "thought": thought})
            return {
                "tool": "compute_compensation",
                "args": {"order": order},
            }

        # Step 3: After compute_compensation -> final decision (quote do code tính)
        if last_tool == "compute_compensation":
            quote_payload = last_result
            proposal = int(quote_payload.get("amount_vnd", 0))
            trace.add("quote", quote_payload)
            if proposal <= 0:
                complete(budget, seed=seed, purpose="draft", prompt="denied")
                return {
                    "final": {
                        "status": "denied",
                        "proposal_amount": 0,
                        "reason": quote_payload.get("reason", "no_entitlement"),
                        "quote": quote_payload,
                    }
                }
            complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
            return {
                "final": {
                    "status": "resolved",
                    "proposal_amount": proposal,
                    "quote": quote_payload,
                }
            }

        # Fallback to avoid infinite loop
        return {"final": {"status": "failed", "proposal_amount": 0, "reason": "unexpected_react_state"}}

    react_res = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=decide,
        max_steps=8,
        worker=False,
    )

    final = react_res.get("final") or {}
    status = final.get("status", "failed")
    proposal = int(final.get("proposal_amount", 0))
    reason = final.get("reason")

    if react_res.get("stopped") == "step_cap":
        trace.add("decision", {"status": "failed", "reason": "step_cap"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="step_cap",
        )

    # result of needs_info, escalated, denied q=0

    if status in ("needs_info", "escalated"):
        trace.add("decision", {"status": status, "reason": reason})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    if status == "denied" and proposal <= 0:
        trace.add("decision", {"status": "denied", "reason": reason})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # TODO CP3 (student): truyền crash_at vào durability.issue_refund, không bắt InjectedCrash.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        final_status = "failed" if outcome["conflict"] else "denied"
        trace.add("decision", {"status": final_status, "reason": outcome["reason"]})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=final_status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=outcome["reason"],
        )

    trace.add("decision", {"status": "resolved", "proposal_amount": proposal})
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

