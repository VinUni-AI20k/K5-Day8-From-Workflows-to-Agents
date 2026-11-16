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
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, make_run_id
from lab8.schemas import RunResult
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
        budget = Budget()
        trace = Trace(make_run_id("single", claim_id, seed))
        claim = get_claim_view(conn, claim_id)
        budget.add_tool(tool_cost())
        if not claim.get("found"):
            trace.add("error", {"reason": "unknown_claim"})
            return finish(conn, shape="single", claim_id=claim_id, seed=seed, status="failed",
                          proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim")

        def decide(observation: dict) -> dict:
            complete(budget, seed=seed, purpose="react", prompt=str(observation))
            if "last_result" not in observation:
                if not claim.get("order_id"):
                    return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
                return {"tool": "lookup_order", "args": {
                    "order_id": claim["order_id"], "principal_id": claim["principal_id"]}}
            if observation["last_tool"] == "lookup_order":
                order_view = observation["last_result"]
                if not order_view.get("visible"):
                    return {"final": {"status": "escalated", "error_reason": order_view.get("reason")}}
                return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
            quote = observation["last_result"]
            return {"final": {"status": "ready", "proposal_amount": int(quote["amount_vnd"]),
                               "error_reason": quote.get("reason"), "quote": quote}}

        outcome = run_react(conn, budget, observation={"claim": claim}, decide=decide, max_steps=8)
        final = outcome["final"]
        trace.add("react", {"stopped": outcome["stopped"], "status": final.get("status")})
        if final.get("status") != "ready":
            return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                          status=final["status"], proposal_amount=0, budget=budget,
                          trace=trace, error_reason=final.get("error_reason"))
        proposal = int(final["proposal_amount"])
        trace.add("quote", final["quote"])
        if proposal <= 0:
            return finish(conn, shape="single", claim_id=claim_id, seed=seed, status="denied",
                          proposal_amount=0, budget=budget, trace=trace,
                          error_reason=final.get("error_reason"))
        try:
            refund = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise
        if not refund["ok"]:
            return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                          status="failed" if refund["conflict"] else "denied",
                          proposal_amount=proposal, budget=budget, trace=trace,
                          error_reason=refund["reason"])
        return finish(conn, shape="single", claim_id=claim_id, seed=seed, status="resolved",
                      proposal_amount=proposal, budget=budget, trace=trace)
    finally:
        conn.close()
