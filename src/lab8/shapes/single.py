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

from lab8.schemas import RunResult
import json

from lab8.db import connect
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.shapes.workflow import ClaimRun
from lab8.tools import get_claim_view


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        run = ClaimRun(conn, "single", claim_id, seed)
        claim = run.read("get_claim_view", get_claim_view, claim_id)
        state = {}

        def decide(observation):
            # MockLLM has no tool-JSON output: a bounded adapter maps observations
            # to actions. Charge every think turn; never let text supply money.
            last = observation.get("last_tool")
            if last:
                state[last] = observation["last_result"]
                run.trace.add("observation", {"tool": last, "result": state[last]})
            complete(run.budget, seed=seed, purpose="react",
                     prompt=json.dumps({"claim_id": claim_id, "observed": sorted(state)}))
            run.trace.add("react_think", {"turn": run.budget.model_calls})
            if not claim["found"]:
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            if not claim.get("order_id"):
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
            if "lookup_order" not in state:
                return {"tool": "lookup_order", "args": {
                    "order_id": claim["order_id"], "principal_id": claim["principal_id"]}}
            view = state["lookup_order"]
            if not view["visible"]:
                return {"final": {"status": "escalated", "error_reason": view["reason"]}}
            if "compute_compensation" not in state:
                return {"tool": "compute_compensation", "args": {"order": view["order"]}}
            return {"final": {"quote": state["compute_compensation"]}}

        result = run_react(conn, run.budget, observation={"claim": claim}, decide=decide, max_steps=8)
        final = result["final"]
        if "quote" not in final:
            return run.finish(final["status"], reason=final.get("error_reason"))
        return run.settle(final["quote"], crash_at)
    finally:
        conn.close()
