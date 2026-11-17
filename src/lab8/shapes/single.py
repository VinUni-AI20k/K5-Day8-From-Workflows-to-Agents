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

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import tool_cost
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
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))

    def result(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": proposal})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    def decide(observation: dict) -> dict:
        # A seeded mock model accounts for model usage. The prompt contains no
        # ticket text, customer data or raw tool response.
        last_tool = observation.get("last_tool")
        complete(budget, seed=seed, purpose="decide", prompt=f"claim-review:{last_tool or 'start'}")

        if last_tool is None:
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

        payload = observation["last_result"]
        if last_tool == "get_claim_view":
            if not payload.get("found"):
                return {"final": {"status": "failed", "reason": "unknown_claim"}}
            if not payload.get("order_id"):
                return {"final": {"status": "needs_info", "reason": "missing_order_id"}}
            return {
                "tool": "lookup_order",
                "args": {"order_id": payload["order_id"], "principal_id": payload["principal_id"]},
            }

        if last_tool == "lookup_order":
            if not payload.get("visible"):
                return {"final": {"status": "escalated", "reason": payload.get("reason")}}
            return {"tool": "compute_compensation", "args": {"order": payload["order"]}}

        if last_tool == "compute_compensation":
            proposal = int(payload["amount_vnd"])
            trace.add("quote", {"amount_vnd": proposal, "clause_ids": payload.get("clause_ids", [])})
            if proposal <= 0:
                return {"final": {"status": "denied", "proposal": 0, "reason": payload.get("reason")}}
            # Quote comes from the scoped order and current policy, never the ticket.
            # This is the *full* quote; the host enforces remaining per-order cap.
            return {"final": {"status": "quote_ready", "proposal": proposal}}

        return {"final": {"status": "failed", "reason": "unexpected_tool"}}

    try:
        loop = run_react(
            conn,
            budget,
            observation={"claim_id": claim_id},
            decide=decide,
            max_steps=8,
            worker=False,
        )
        final = loop["final"]
        status = final.get("status", "failed")
        proposal = int(final.get("proposal", 0))
        if loop["stopped"] != "final":
            return result("failed", reason="step_cap")
        if status != "quote_ready":
            return result(status, proposal, final.get("reason"))

        # Commit is host-only, outside the ReAct loop.
        budget.add_tool(tool_cost())
        try:
            # TODO CP3 (student): truyền crash_at vào durability.issue_refund, không bắt InjectedCrash.
            outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise
        if not outcome["ok"]:
            return result(
                "failed" if outcome.get("conflict") else "denied",
                proposal,
                outcome.get("reason"),
            )
        return result("resolved", proposal)
    finally:
        conn.close()
