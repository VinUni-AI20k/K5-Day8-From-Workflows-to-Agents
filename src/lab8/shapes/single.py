"""Shape B — one bounded ReAct agent with host-owned refund writes."""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def _decide(observation: dict) -> dict:
    """Choose read tools in a fixed, bounded order; ticket text is never authority."""
    claim = observation.get("claim") or {}
    if not claim.get("found"):
        return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
    if not claim.get("order_id"):
        return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}

    last_tool = observation.get("last_tool")
    if last_tool is None:
        return {
            "tool": "lookup_order",
            "args": {
                "order_id": claim["order_id"],
                "principal_id": claim["principal_id"],
            },
        }
    if last_tool == "lookup_order":
        order_result = observation.get("last_result") or {}
        if not order_result.get("visible"):
            return {"final": {"status": "escalated", "error_reason": order_result.get("reason")}}
        return {"tool": "compute_compensation", "args": {"order": order_result["order"]}}
    if last_tool == "compute_compensation":
        return {"final": {"status": "quoted", "quote": observation.get("last_result") or {}}}
    return {"final": {"status": "failed", "error_reason": "unexpected_tool_result"}}


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

        # Read only the contract's allowlisted claim view. Do not trace the ticket.
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        safe_claim = {
            key: claim[key]
            for key in ("found", "claim_id", "principal_id", "order_id")
            if key in claim
        }
        trace.add("claim_view", safe_dump(safe_claim))
        if not claim.get("found"):
            trace.add("decision", {"status": "failed", "reason": "unknown_claim"})
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status="failed", proposal_amount=0, budget=budget, trace=trace,
                error_reason="unknown_claim",
            )

        if not claim.get("order_id"):
            trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status="needs_info", proposal_amount=0, budget=budget, trace=trace,
                error_reason="missing_order_id",
            )

        # MockLLM provides the single agent's bounded decision step. Its output
        # is deliberately not used for policy facts or refund amounts.
        prompt = "Select read-only tools to verify an order and compute its policy quote."
        complete(budget, seed=seed, purpose="single", prompt=prompt)
        observation = {"claim": safe_claim}
        result = run_react(conn, budget, observation=observation, decide=_decide, max_steps=8)
        trace.add("react", {"stopped": result["stopped"], "steps": budget.steps})

        final = result.get("final") or {}
        status = final.get("status")
        if status == "needs_info":
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status="needs_info", proposal_amount=0, budget=budget, trace=trace,
                error_reason=final.get("error_reason"),
            )
        if status == "escalated":
            trace.add("decision", {"status": "escalated", "reason": final.get("error_reason")})
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status="escalated", proposal_amount=0, budget=budget, trace=trace,
                error_reason=final.get("error_reason"),
            )
        if status != "quoted":
            trace.add("decision", {"status": "failed", "reason": final.get("error_reason") or "step_cap"})
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status="failed", proposal_amount=0, budget=budget, trace=trace,
                error_reason=final.get("error_reason") or "step_cap",
            )

        quote = final.get("quote") or {}
        proposal = int(quote.get("amount_vnd", 0))
        trace.add("quote", safe_dump(quote))
        if proposal <= 0:
            trace.add("decision", {"status": "denied", "reason": quote.get("reason")})
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status="denied", proposal_amount=0, budget=budget, trace=trace,
                error_reason=quote.get("reason"),
            )

        try:
            outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        except InjectedCrash:
            trace.add("crash", {"at": crash_at})
            trace.write()
            raise

        if not outcome["ok"]:
            status = "failed" if outcome.get("conflict") else "denied"
            trace.add("decision", {"status": status, "reason": outcome.get("reason")})
            return finish(
                conn, shape="single", claim_id=claim_id, seed=seed,
                status=status, proposal_amount=proposal, budget=budget, trace=trace,
                error_reason=outcome.get("reason"),
            )
        trace.add("decision", {"status": "resolved"})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status="resolved", proposal_amount=proposal, budget=budget, trace=trace,
        )
    except sqlite3.Error as exc:
        # Keep the public contract exception-free while avoiding sensitive DB details.
        budget = locals().get("budget", Budget())
        trace = locals().get("trace")
        if trace is None:
            run_id = make_run_id("single", claim_id, seed)
            trace = Trace(run_id)
        trace.add("error", {"reason": "storage_error"})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed,
            status="failed", proposal_amount=0, budget=budget, trace=trace,
            error_reason="storage_error",
        )
    finally:
        conn.close()
