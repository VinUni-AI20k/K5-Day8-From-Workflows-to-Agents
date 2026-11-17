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

import json
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.shapes.workflow import SAFE_DENIAL_REASONS
from lab8.tools import compute_compensation, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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


def _run(conn, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # Facts the agent collected from read tools. run_react only keeps the last
    # tool result in `seen`, so the agent's memory lives here.
    facts: dict[str, Any] = {}

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        # One model call per step, so cost is comparable with the other shapes.
        # The prompt is only hashed for token counting, never written to the trace.
        complete(budget, seed=seed, purpose="decide", prompt=json.dumps(seen, ensure_ascii=False, default=str))
        last = seen.get("last_tool")
        if last:
            facts[last] = seen["last_result"]
            trace.add("tool", {"name": last, "reason": seen["last_result"].get("reason")})

        if "get_claim_view" not in facts:
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
        claim = facts["get_claim_view"]
        if not claim.get("found"):
            return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
        if "lookup_order" not in facts:
            return {
                "tool": "lookup_order",
                "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
            }
        order_view = facts["lookup_order"]
        if not order_view.get("visible"):
            return {"final": {"status": "escalated", "error_reason": order_view.get("reason")}}
        # Enough facts. The amount is decided by code below, not by the model.
        return {"final": {"status": "quote"}}

    loop = run_react(
        conn,
        budget,
        observation={"claim": {"claim_id": claim_id}},
        decide=decide,
        max_steps=MAX_STEPS,
    )
    final = loop["final"]
    if loop["stopped"] == "step_cap":
        return done("escalated", reason="step_cap")
    if final["status"] != "quote":
        complete(budget, seed=seed, purpose="draft", prompt=final["status"])
        return done(final["status"], reason=final.get("error_reason"))

    # Money stays in code: quote from the order row (allowlisted fields),
    # never from the delay written in the ticket.
    order_view = facts["lookup_order"]
    trace.add("order", order_view)
    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order_view["order"])
    trace.add("quote", quote_payload)
    proposal = int(quote_payload["amount_vnd"])
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        return done("denied", reason=quote_payload.get("reason"))

    # Full quote: the host checks approval and subtracts earlier refunds on the same order.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if outcome["conflict"]:
        return done("failed", proposal, "amount_conflict")
    if not outcome["ok"]:
        # The host builds some reasons from stored data (approval_<status>): keep only known ones.
        reason = outcome["reason"]
        return done("denied", proposal, reason if reason in SAFE_DENIAL_REASONS else "policy_denied")
    return done("resolved", proposal)
