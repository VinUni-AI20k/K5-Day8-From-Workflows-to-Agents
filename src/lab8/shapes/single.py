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
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

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
    run_id = make_run_id("single", claim_id, seed)
    trace = Trace(run_id)

    # Đọc claim bằng tool đọc. get_claim_view không trả parent_secret.
    claim = get_claim_view(conn, claim_id)
    budget.add_tool(tool_cost())
    if not claim.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed, status="failed",
            proposal_amount=0, budget=budget, trace=trace, error_reason="unknown_claim",
        )

    principal_id = claim["principal_id"]
    order_id = claim["order_id"]
    step = {"n": 0}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        """Một bước ReAct. Chỉ chọn tool đọc; không đọc ticket; không có tool ghi."""
        step["n"] += 1
        complete(budget, seed=seed, purpose="react", prompt=f"step={step['n']}")
        last = observation.get("last_tool")
        result = observation.get("last_result") or {}

        if last is None:
            if not order_id:
                trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
            trace.add("action", {"tool": "lookup_order"})
            return {"tool": "lookup_order", "args": {"order_id": order_id, "principal_id": principal_id}}

        if last == "lookup_order":
            trace.add("observation", {"tool": "lookup_order", "visible": bool(result.get("visible")), "reason": result.get("reason")})
            if not result.get("visible"):
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            trace.add("action", {"tool": "compute_compensation"})
            return {"tool": "compute_compensation", "args": {"order": result["order"]}}

        if last == "compute_compensation":
            trace.add(
                "observation",
                {
                    "tool": "compute_compensation",
                    "amount_vnd": result.get("amount_vnd"),
                    "reason": result.get("reason"),
                    "clause_ids": result.get("clause_ids"),
                },
            )
            return {"final": {"status": "quote", "quote": result}}

        return {"final": {"status": "failed", "error_reason": "unexpected_state"}}

    outcome = run_react(
        conn,
        budget,
        observation={"claim": {"claim_id": claim_id, "has_order_id": bool(order_id)}},
        decide=decide,
        max_steps=MAX_STEPS,
        worker=False,
    )
    final = outcome["final"]
    status = final.get("status")

    # Các nhánh không có quote: needs_info / escalated / failed (kể cả step_cap).
    if status in ("needs_info", "escalated", "failed"):
        complete(budget, seed=seed, purpose="draft", prompt=status)
        trace.add("result", {"status": status, "reason": final.get("error_reason")})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed, status=status,
            proposal_amount=0, budget=budget, trace=trace, error_reason=final.get("error_reason"),
        )

    # Có quote. Tiền do code (compute_compensation) tính, model không quyết.
    quote = final["quote"]
    proposal = int(quote["amount_vnd"])
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    if proposal <= 0:
        trace.add("result", {"status": "denied", "reason": quote.get("reason")})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed, status="denied",
            proposal_amount=0, budget=budget, trace=trace, error_reason=quote.get("reason"),
        )

    # Host là nơi duy nhất ghi tiền. Truyền quote đầy đủ, truyền crash_at.
    try:
        refund = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not refund["ok"]:
        status = "failed" if refund["conflict"] else "denied"
        trace.add("result", {"status": status, "reason": refund["reason"]})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed, status=status,
            proposal_amount=proposal, budget=budget, trace=trace, error_reason=refund["reason"],
        )

    trace.add("result", {"status": "resolved", "proposal_amount": proposal})
    return finish(
        conn, shape="single", claim_id=claim_id, seed=seed, status="resolved",
        proposal_amount=proposal, budget=budget, trace=trace, error_reason=None,
    )
