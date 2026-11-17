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

Implementation notes (team):
- `decide` is the "model". Each call is charged as one MockLLM call. It only
  picks read tools in a fixed plan: lookup_order -> lookup_refund_history ->
  compute_compensation -> final. The order passed to compute_compensation is
  the structured order view, never numbers parsed from the ticket.
- The ticket is not sent into the loop: the observation holds only claim_id,
  order_id and principal_id. Ticket text cannot steer tool choice.
- After the loop, code checks the quote and calls durability.issue_refund.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import ToolRejected, run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
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


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, amount: int, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(amount), "reason": reason})
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=amount,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim")

    # Only ids go into the loop. No ticket text, no secret.
    safe_claim = {
        "claim_id": claim_id,
        "order_id": claim.get("order_id"),
        "principal_id": claim["principal_id"],
    }
    memory: dict[str, Any] = {}

    def decide(obs: dict[str, Any]) -> dict[str, Any]:
        last_tool = obs.get("last_tool")
        if last_tool:
            memory[last_tool] = obs.get("last_result")
        step = len(memory)
        complete(budget, seed=seed, purpose="decide", prompt=f"{claim_id}|step={step}|last={last_tool}")
        trace.add("react_step", {"step": step, "last_tool": last_tool})

        if not safe_claim["order_id"]:
            return {"final": {"status": "needs_info", "reason": "missing_order_id"}}
        if "lookup_order" not in memory:
            return {
                "tool": "lookup_order",
                "args": {"order_id": safe_claim["order_id"], "principal_id": safe_claim["principal_id"]},
            }
        order_view = memory["lookup_order"] or {}
        if not order_view.get("visible"):
            return {"final": {"status": "escalated", "reason": order_view.get("reason")}}
        if "lookup_refund_history" not in memory:
            return {
                "tool": "lookup_refund_history",
                "args": {"order_id": safe_claim["order_id"], "principal_id": safe_claim["principal_id"]},
            }
        if "compute_compensation" not in memory:
            return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
        return {"final": {"status": "quote", "quote": memory["compute_compensation"]}}

    try:
        loop = run_react(
            conn,
            budget,
            observation={"claim": safe_claim},
            decide=decide,
            max_steps=MAX_STEPS,
        )
    except ToolRejected as exc:
        return done("failed", 0, f"tool_rejected:{exc}")

    if loop["stopped"] != "final":
        return done("failed", 0, "step_cap")

    order_view = memory.get("lookup_order") or {}
    if order_view.get("visible"):
        trace.add("order", dict(order_view["order"]))
    history = memory.get("lookup_refund_history") or {}
    if history.get("visible"):
        trace.add("refund_history", {"refund_count": history["refund_count"], "refunded_vnd": history["refunded_vnd"]})

    final = loop["final"]
    if final.get("status") in ("needs_info", "escalated"):
        return done(final["status"], 0, final.get("reason"))

    # Code, not the model, validates the quote and calls the host.
    quote = final.get("quote") or {}
    trace.add("quote", quote)
    proposal = int(quote.get("amount_vnd") or 0)
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": bool(outcome["ok"]), "reason": outcome["reason"]})

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])
    return done("resolved", proposal, None)
