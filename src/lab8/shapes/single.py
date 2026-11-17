"""Shape B: one bounded ReAct agent with read tools and a host-only write."""

from __future__ import annotations

import json
import sqlite3

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
    shape = "single"
    try:
        conn = connect(store_path)
    except Exception:
        return _failed_result(shape, claim_id, seed)
    try:
        try:
            return _run(conn, claim_id, seed=seed, crash_at=crash_at)
        except InjectedCrash:
            raise
        except Exception:
            return _failed_result(shape, claim_id, seed, conn)
    finally:
        conn.close()


def _failed_result(
    shape: str, claim_id: str, seed: int, conn: sqlite3.Connection | None = None
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(shape, claim_id, seed))
    trace.add("error", {"reason": "internal_error"})
    if conn is not None:
        try:
            return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="failed",
                          proposal_amount=0, budget=budget, trace=trace,
                          error_reason="internal_error")
        except Exception:
            pass
    path = trace.write()
    return RunResult(
        run_id=trace.run_id, claim_id=claim_id, shape=shape, seed=seed, status="failed",
        proposal_amount=0, refund_effects=[], committed_audit_count=0,
        model_calls=0, tool_calls=0, input_tokens=0, output_tokens=0,
        cost_estimate=0.0, trace_path=path, error_reason="internal_error",
    )


def _safe_result(tool: str, result: dict) -> dict:
    if tool == "get_claim_view":
        return {key: result.get(key) for key in ("found", "claim_id", "order_id")}
    if tool == "lookup_order":
        return {key: result.get(key) for key in ("visible", "reason", "order")}
    if tool == "compute_compensation":
        return {key: result.get(key) for key in ("amount_vnd", "reason", "clause_ids", "parts")}
    return {"reason": "unsupported_result"}


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    shape = "single"
    budget = Budget()
    trace = Trace(make_run_id(shape, claim_id, seed))

    def decide(observation: dict) -> dict:
        previous = observation.get("last_tool")
        result = observation.get("last_result", {})
        if previous:
            trace.add("tool_result", {"tool": previous, "result": _safe_result(previous, result)})
        prompt = json.dumps({"claim_id": claim_id, "last_tool": previous,
                             "last_result": _safe_result(previous, result) if previous else {}},
                            sort_keys=True, ensure_ascii=False)
        complete(budget, seed=seed, purpose="react", prompt=prompt)

        if previous is None:
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
        if previous == "get_claim_view":
            if not result.get("found"):
                return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": "unknown_claim"}}
            if not result.get("order_id"):
                return {"final": {"status": "needs_info", "proposal_amount": 0, "error_reason": "missing_order_id"}}
            return {"tool": "lookup_order", "args": {
                "order_id": result["order_id"], "principal_id": result["principal_id"]}}
        if previous == "lookup_order":
            if not result.get("visible"):
                return {"final": {"status": "escalated", "proposal_amount": 0,
                                  "error_reason": result.get("reason")}}
            return {"tool": "compute_compensation", "args": {"order": result["order"]}}
        if previous == "compute_compensation":
            return {"final": {"status": "denied" if int(result["amount_vnd"]) <= 0 else "quoted",
                              "proposal_amount": int(result["amount_vnd"]),
                              "error_reason": result.get("reason")}}
        return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": "invalid_agent_state"}}

    trace.add("agent", {"max_steps": 8, "tools": ["get_claim_view", "lookup_order", "compute_compensation"]})
    result = run_react(conn, budget, observation={"claim": {"claim_id": claim_id}},
                       decide=decide, max_steps=8)
    final = result["final"]
    status = final["status"]
    proposal = int(final.get("proposal_amount", 0))
    reason = final.get("error_reason")
    trace.add("decision", {"status": status, "proposal_amount": proposal})
    if status != "quoted":
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status=status,
                      proposal_amount=proposal, budget=budget, trace=trace, error_reason=reason)
    if proposal <= 0:
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="denied",
                      proposal_amount=0, budget=budget, trace=trace, error_reason=reason)

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        return finish(conn, shape=shape, claim_id=claim_id, seed=seed,
                      status="failed" if outcome["conflict"] else "denied",
                      proposal_amount=proposal, budget=budget, trace=trace,
                      error_reason=outcome["reason"])
    return finish(conn, shape=shape, claim_id=claim_id, seed=seed, status="resolved",
                  proposal_amount=proposal, budget=budget, trace=trace)
