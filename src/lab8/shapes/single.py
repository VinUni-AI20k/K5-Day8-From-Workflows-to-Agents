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
        proposal = 0

        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("tool", {"name": "get_claim_view", "found": claim["found"]})

        if not claim["found"]:
            status = "failed"
            reason = "unknown_claim"
        elif not claim.get("order_id"):
            status = "needs_info"
            reason = "missing_order_id"
        else:
            def decide(observation):
                last_tool = observation.get("last_tool")
                complete(
                    budget,
                    seed=seed,
                    purpose="decide",
                    prompt=f"claim={claim_id}; last_tool={last_tool or 'start'}",
                )
                trace.add("model", {"purpose": "decide", "last_tool": last_tool})

                if last_tool is None:
                    trace.add("action", {"tool": "lookup_order"})
                    return {
                        "tool": "lookup_order",
                        "args": {
                            "order_id": claim["order_id"],
                            "principal_id": claim["principal_id"],
                        },
                    }

                result = observation["last_result"]
                if last_tool == "lookup_order":
                    trace.add("order_scope", {"visible": result["visible"], "reason": result["reason"]})
                    if not result["visible"]:
                        return {"final": {"status": "escalated", "error_reason": result["reason"]}}
                    trace.add("action", {"tool": "compute_compensation"})
                    return {"tool": "compute_compensation", "args": {"order": result["order"]}}

                if last_tool == "compute_compensation":
                    trace.add("quote", result)
                    return {"final": {"quote": result}}

                return {"final": {"status": "failed", "error_reason": "unexpected_tool"}}

            outcome = run_react(
                conn,
                budget,
                observation={"claim": claim},
                decide=decide,
                max_steps=8,
                worker=True,
            )
            final = outcome["final"]
            if "quote" in final:
                quote = final["quote"]
                proposal = int(quote["amount_vnd"])
                if proposal <= 0:
                    status = "denied"
                    reason = quote["reason"]
                else:
                    refund = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
                    trace.add("host", {"ok": refund["ok"], "reason": refund["reason"]})
                    if refund["ok"]:
                        status = "resolved"
                        reason = None
                    elif refund["conflict"]:
                        status = "failed"
                        reason = refund["reason"]
                    else:
                        status = "denied"
                        reason = refund["reason"]
            else:
                status = final["status"]
                reason = final["error_reason"]

        trace.add("decision", {"status": status, "reason": reason})
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
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    finally:
        conn.close()
