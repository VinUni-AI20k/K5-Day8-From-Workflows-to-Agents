"""Shape B — one bounded ReAct agent with host controlled refund writes."""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import dispatch, run_react
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

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        """Use MockLLM for bounded orchestration; business decisions stay in code."""
        if "claim" not in observation:
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

        claim = observation["claim"]
        if not claim.get("found"):
            return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
        if not claim.get("order_id"):
            return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}

        last_tool = observation.get("last_tool")
        result = observation.get("last_result") or {}
        if last_tool in (None, "get_claim_view"):
            return {
                "tool": "lookup_order",
                "args": {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
            }
        if last_tool == "lookup_order":
            if not result.get("visible"):
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            return {"tool": "compute_compensation", "args": {"order": result["order"]}}
        if last_tool == "compute_compensation":
            return {"final": {"status": "quoted", "quote": result}}
        return {"final": {"status": "failed", "error_reason": "unexpected_agent_state"}}

    # Account for the model's bounded decision calls. run_react delegates every
    # tool call to the read-only dispatcher and enforces the eight-step limit.
    def bounded_decide(observation: dict[str, Any]) -> dict[str, Any]:
        complete(budget, seed=seed, purpose="single_decide", prompt=_safe_prompt(observation))
        return decide(observation)

    # Read a minimal claim view through the read-only dispatcher, then let the
    # bounded loop choose subsequent read tools. Raw ticket text is not traced.
    claim = dispatch(conn, budget, "get_claim_view", {"claim_id": claim_id}, worker=True)
    agent = run_react(
        conn,
        budget,
        observation={"claim": claim},
        decide=bounded_decide,
        max_steps=8,
        worker=True,
    )
    # Trace only allowlisted identifiers and decisions, never raw ticket text
    # or parent context supplied to the model.
    if agent["stopped"] == "step_cap":
        final = agent["final"]
        trace.add("agent", {"status": "failed", "reason": "step_cap"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason"),
        )

    final = agent["final"]
    trace.add("agent", {"status": final.get("status")})
    status = final.get("status")
    if status in ("failed", "needs_info", "escalated"):
        reason = final.get("error_reason")
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

    # The quote result is returned only after the runtime's read-only tool
    # call. The claim and order payloads remain out of the trace.
    quote = final["quote"]
    proposal = int(quote["amount_vnd"])
    trace.add("quote", quote)
    if proposal <= 0:
        trace.add("decision", {"status": "denied"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=quote.get("reason"),
        )

    trace.add("refund_attempt", {"proposal_amount": proposal})
    trace.write()
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add(
        "refund_result",
        {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]},
    )
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        trace.add("decision", {"status": status, "reason": outcome["reason"]})
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
    trace.add("decision", {"status": "resolved"})
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


def _safe_prompt(observation: dict[str, Any]) -> str:
    """Prompt from state labels only; user ticket text is untrusted data."""
    if not observation:
        return "start claim review"
    if "claim" not in observation:
        return "read claim view"
    return f"continue after {observation.get('last_tool', 'claim_view')}"
