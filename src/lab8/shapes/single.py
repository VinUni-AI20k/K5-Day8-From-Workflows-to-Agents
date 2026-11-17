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
    trace = _Trace(run_id)

    context: dict[str, Any] = {
        "step_count": 0,
        "claim": None,
        "order": None,
        "quote": None,
    }

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        context["step_count"] += 1
        last_tool = seen.get("last_tool")
        complete(budget, seed=seed, purpose="react_step", prompt=f"step={context['step_count']}|last={last_tool}")

        if last_tool is None:
            trace.add("react_action", {"tool": "get_claim_view"})
            return {"tool": "get_claim_view", "args": {"claim_id": claim_id}}

        if last_tool == "get_claim_view":
            claim_view = seen.get("last_result") or {}
            trace.add("react_observation", {"tool": "get_claim_view", "found": claim_view.get("found")})
            if not claim_view.get("found"):
                return {"final": {"status": "failed", "error_reason": "unknown_claim", "proposal": 0}}
            if not claim_view.get("order_id"):
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id", "proposal": 0}}
            context["claim"] = claim_view
            trace.add("react_action", {"tool": "lookup_order"})
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim_view["order_id"],
                    "principal_id": claim_view["principal_id"],
                },
            }

        if last_tool == "lookup_order":
            order_view = seen.get("last_result") or {}
            trace.add(
                "react_observation",
                {"tool": "lookup_order", "visible": order_view.get("visible"), "reason": order_view.get("reason")},
            )
            if not order_view.get("visible"):
                return {
                    "final": {
                        "status": "escalated",
                        "error_reason": order_view.get("reason"),
                        "proposal": 0,
                    }
                }
            order = dict(order_view["order"])
            context["order"] = order
            trace.add("react_action", {"tool": "compute_compensation"})
            return {"tool": "compute_compensation", "args": {"order": order}}

        if last_tool == "compute_compensation":
            quote_payload = seen.get("last_result") or {}
            trace.add("react_observation", {"tool": "compute_compensation", "amount": quote_payload.get("amount_vnd")})
            proposal = int(quote_payload.get("amount_vnd", 0))
            context["quote"] = quote_payload
            if proposal <= 0:
                return {
                    "final": {
                        "status": "denied",
                        "error_reason": quote_payload.get("reason"),
                        "proposal": 0,
                    }
                }
            return {
                "final": {
                    "status": "proceed",
                    "proposal": proposal,
                    "quote": quote_payload,
                }
            }

        return {"final": {"status": "failed", "error_reason": f"unexpected_tool_{last_tool}", "proposal": 0}}

    react_outcome = run_react(
        conn,
        budget,
        observation={"claim_id": claim_id},
        decide=decide,
        max_steps=8,
        worker=False,
    )
    final = react_outcome.get("final") or {}
    final_status = final.get("status")

    if final_status in ("failed", "needs_info", "escalated", "denied"):
        complete(budget, seed=seed, purpose="draft", prompt=final_status)
        trace.add("decision", {"status": final_status, "reason": final.get("error_reason")})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=final_status,
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=final.get("error_reason"),
        )

    proposal = int(final.get("proposal", 0))
    trace.add("quote", final.get("quote", {}))
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")

    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
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

    return finish(
        conn,
        shape="single",
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )


class _Trace:
    """Local alias so a crash can still flush. Wraps lab8.trace.Trace."""

    def __init__(self, run_id: str) -> None:
        from lab8.trace import Trace

        self._inner = Trace(run_id)

    def add(self, kind: str, payload: dict) -> None:
        self._inner.add(kind, payload)

    def write(self) -> str:
        return self._inner.write()

    @property
    def run_id(self) -> str:
        return self._inner.run_id
