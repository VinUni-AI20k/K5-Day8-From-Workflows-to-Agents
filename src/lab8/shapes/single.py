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

from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
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
        budget = Budget()
        run_id = make_run_id("single", claim_id, seed)
        trace = Trace(run_id)

        state: dict[str, Any] = {
            "claim_view": None,
            "order_view": None,
            "quote": None,
        }

        def decide(seen: dict[str, Any]) -> dict[str, Any]:
            last_tool = seen.get("last_tool")
            last_result = seen.get("last_result")

            if last_tool == "get_claim_view":
                state["claim_view"] = last_result
            elif last_tool == "lookup_order":
                state["order_view"] = last_result
            elif last_tool == "compute_compensation":
                state["quote"] = last_result

            # 1. Fetch claim view if not yet acquired
            if state["claim_view"] is None:
                complete(budget, seed=seed, purpose="think", prompt="fetch_claim")
                trace.add("thought", {"action": "fetch_claim"})
                return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

            claim = state["claim_view"]
            if not claim.get("found"):
                trace.add("decision", {"status": "failed", "reason": "unknown_claim"})
                return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": "unknown_claim"}}

            if not claim.get("order_id"):
                trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
                return {"final": {"status": "needs_info", "proposal_amount": 0, "error_reason": "missing_order_id"}}

            # 2. Lookup order if not yet acquired
            if state["order_view"] is None:
                complete(budget, seed=seed, purpose="think", prompt="fetch_order")
                trace.add("thought", {"action": "fetch_order"})
                return {
                    "tool": "lookup_order",
                    "args": {
                        "order_id": claim["order_id"],
                        "principal_id": claim["principal_id"],
                    },
                }

            order_view = state["order_view"]
            if not order_view.get("visible"):
                reason = order_view.get("reason")
                trace.add("decision", {"status": "escalated", "reason": reason})
                return {"final": {"status": "escalated", "proposal_amount": 0, "error_reason": reason}}

            # 3. Calculate compensation based on verified order (not ticket text)
            if state["quote"] is None:
                complete(budget, seed=seed, purpose="think", prompt="compute_compensation")
                trace.add("thought", {"action": "compute_compensation"})
                return {
                    "tool": "compute_compensation",
                    "args": {"order": order_view["order"]},
                }

            # 4. Evaluate quote outcome
            quote = state["quote"]
            proposal = int(quote["amount_vnd"])
            trace.add("quote", {"amount_vnd": proposal, "reason": quote.get("reason")})

            if proposal <= 0:
                trace.add("decision", {"status": "denied", "reason": quote.get("reason")})
                return {"final": {"status": "denied", "proposal_amount": 0, "error_reason": quote.get("reason")}}

            trace.add("decision", {"status": "ready_to_refund", "proposal_amount": proposal})
            return {"final": {"status": "ready_to_refund", "proposal_amount": proposal}}

        react_result = run_react(
            conn,
            budget,
            observation={"claim_id": claim_id},
            decide=decide,
            max_steps=8,
            worker=True,
        )

        final = react_result.get("final", {})
        status = final.get("status", "failed")
        proposal = int(final.get("proposal_amount", 0))
        error_reason = final.get("error_reason")

        if status != "ready_to_refund":
            complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
            return finish(
                conn,
                shape="single",
                claim_id=claim_id,
                seed=seed,
                status=status,
                proposal_amount=proposal,
                budget=budget,
                trace=trace,
                error_reason=error_reason,
            )

        # Host acts as the sole writer and enforces policy/approval/idempotency/cap.
        try:
            outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise

        if not outcome["ok"]:
            final_status = "failed" if outcome["conflict"] else "denied"
            complete(budget, seed=seed, purpose="draft", prompt=f"denied:{outcome['reason']}")
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

        complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="resolved",
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
        )
    finally:
        conn.close()
