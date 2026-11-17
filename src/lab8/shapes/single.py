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
import sqlite3
from typing import Any

from lab8 import durability
from lab8.db import connect
from lab8.mock_llm import complete
from lab8.runtime import ToolRejected, run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8
# Order-scoped read tools the agent may pick. issue_refund is never in this set.
AGENT_TOOLS = ("lookup_order", "lookup_refund_history", "compute_compensation")


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

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        # The model only drafts the reply text; status and amount are already fixed by code.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status} proposal={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
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

    # Allowlisted claim view: no parent_secret, no raw headers.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", 0, "unknown_claim")

    # The ticket is user data. The agent may read it, but every number it acts on
    # comes from a read tool. The ticket itself is never written to the trace.
    # What the agent is allowed to see. The ticket is user data: the agent may read it
    # for tone, but every number it acts on comes from a read tool.
    observation = {
        "claim": {
            "claim_id": claim["claim_id"],
            "principal_id": claim["principal_id"],
            "order_id": claim["order_id"],
            "ticket": claim["ticket"],
        }
    }
    memory: dict[str, Any] = {}
    decide = _make_decide(budget, trace, seed=seed, memory=memory)
    try:
        loop = run_react(conn, budget, observation=observation, decide=decide, max_steps=MAX_STEPS)
    except ToolRejected as exc:
        trace.add("error", {"reason": "tool_rejected", "detail": str(exc)})
        return done("failed", 0, "tool_rejected")
    final = loop["final"]
    trace.add("react_stop", {"stopped": loop["stopped"], "final_status": final.get("status")})

    if loop["stopped"] == "step_cap":
        return done("failed", 0, "step_cap")
    if final.get("status") in ("needs_info", "escalated"):
    if final["status"] in ("needs_info", "escalated"):
        return done(final["status"], 0, final.get("reason"))

    # The model only says "quote ready". The amount is the compute_compensation tool
    # result captured by code, never a number the model wrote in its final answer.
    quote = memory.get("quote")
    if quote is None:
        return done("failed", 0, "no_quote")
    proposal = int(quote["amount_vnd"])
    if proposal <= 0:
        return done("denied", 0, quote["reason"])

    # Host gate is the only writer. Full quote (host subtracts earlier refunds on the order).
    # crash_at is forwarded; InjectedCrash is re-raised after flushing the trace.
    try:
        outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except durability.InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal, None)


def _make_decide(budget: Budget, trace: Trace, *, seed: int, memory: dict[str, Any]):
    """ReAct policy. Each step costs one MockLLM call; only read tools are ever chosen."""

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        claim = seen.get("claim") or {}
        last_tool = seen.get("last_tool")
        last = seen.get("last_result") or {}
        steps = memory.setdefault("steps", [])
        complete(
            budget,
            seed=seed,
            purpose="react",
            prompt=json.dumps({"last_tool": last_tool, "step": len(steps)}),
        )
        steps.append(last_tool)

        # Observe the last tool result.
            prompt=json.dumps({"last_tool": last_tool, "step": len(memory.get("steps", []))}),
        )
        memory.setdefault("steps", []).append(last_tool)

        if last_tool == "lookup_order":
            trace.add("observe", {"tool": last_tool, "visible": last.get("visible"), "reason": last.get("reason")})
            if not last.get("visible"):
                return {"final": {"status": "escalated", "reason": last.get("reason")}}
            memory["order"] = last["order"]
        elif last_tool == "lookup_refund_history":
            history = {k: last.get(k) for k in ("visible", "refund_count", "refunded_vnd")}
            memory["history"] = history
            trace.add("observe", {"tool": last_tool, **history})
        elif last_tool == "compute_compensation":
            memory["quote"] = last
            trace.add("observe", {"tool": last_tool, "quote": safe_dump(last)})
            return {"final": {"status": "quote_ready"}}

        # Pick the next action. Never take an order id from the ticket text.
        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "reason": "missing_order_id"}}
        scope = {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
        if "order" not in memory:
            return _act(trace, "lookup_order", scope)
        if "history" not in memory:
            return _act(trace, "lookup_refund_history", scope)
        # Quote from the DB order row, not from delay numbers or clauses in the ticket.
        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "reason": "missing_order_id"}}
        if "order" not in memory:
            return _act(trace, "lookup_order", {"order_id": claim["order_id"], "principal_id": claim["principal_id"]})
        if "history" not in memory:
            return _act(
                trace, "lookup_refund_history", {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
            )
        # Quote from the DB order row, not from delay numbers in the ticket.
        return _act(trace, "compute_compensation", {"order": memory["order"]})

    return decide


def _act(trace: Trace, tool: str, args: dict[str, Any]) -> dict[str, Any]:
    assert tool in AGENT_TOOLS, tool
    trace.add("act", {"tool": tool})
    return {"tool": tool, "args": args}
