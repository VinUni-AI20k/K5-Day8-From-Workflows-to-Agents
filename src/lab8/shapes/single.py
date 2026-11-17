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
from lab8.runtime import dispatch, run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
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

    claim_view = dispatch(conn, budget, "get_claim_view", {"claim_id": claim_id}, worker=True)
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    trace.add(
        "claim_view",
        {
            "claim_id": claim_view["claim_id"],
            "principal_id": claim_view["principal_id"],
            "order_id": claim_view["order_id"],
        },
    )

    def decide(seen: dict[str, Any]) -> dict[str, Any]:
        claim = seen["claim"]
        last_tool = seen.get("last_tool")
        last_result = seen.get("last_result") or {}

        if last_tool is None:
            if not claim.get("order_id"):
                complete(budget, seed=seed, purpose="draft", prompt="needs_info")
                trace.add("decision", {"status": "needs_info", "reason": "missing_order_id"})
                return {
                    "final": {
                        "status": "needs_info",
                        "proposal_amount": 0,
                        "error_reason": "missing_order_id",
                    }
                }
            complete(budget, seed=seed, purpose="react", prompt=f"lookup_order:{claim['order_id']}")
            return {
                "tool": "lookup_order",
                "args": {
                    "order_id": claim["order_id"],
                    "principal_id": claim["principal_id"],
                },
            }

        if last_tool == "lookup_order":
            trace.add("lookup_order", safe_dump(last_result))
            if not last_result.get("visible"):
                reason = last_result.get("reason")
                complete(budget, seed=seed, purpose="draft", prompt="escalated")
                trace.add("decision", {"status": "escalated", "reason": reason})
                return {
                    "final": {
                        "status": "escalated",
                        "proposal_amount": 0,
                        "error_reason": reason,
                    }
                }
            order = last_result["order"]
            complete(budget, seed=seed, purpose="react", prompt=f"compute_compensation:{order['order_id']}")
            return {
                "tool": "compute_compensation",
                "args": {"order": order},
            }

        if last_tool == "compute_compensation":
            trace.add("quote", safe_dump(last_result))
            proposal = int(last_result["amount_vnd"])
            complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
            if proposal <= 0:
                reason = last_result.get("reason")
                trace.add("decision", {"status": "denied", "reason": reason})
                return {
                    "final": {
                        "status": "denied",
                        "proposal_amount": 0,
                        "error_reason": reason,
                    }
                }
            return {
                "final": {
                    "status": "propose",
                    "proposal_amount": proposal,
                    "error_reason": None,
                }
            }

        return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": "unexpected_state"}}

    outcome = run_react(
        conn,
        budget,
        observation={"claim": claim_view},
        decide=decide,
        max_steps=8,
        worker=True,
    )
    final = outcome["final"]
    status = final["status"]
    proposal = int(final.get("proposal_amount", 0))
    error_reason = final.get("error_reason")

    if status != "propose":
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )

    try:
        refund_outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not refund_outcome["ok"]:
        final_status = "failed" if refund_outcome["conflict"] else "denied"
        trace.add("host_gate", {"ok": False, "reason": refund_outcome["reason"], "status": final_status})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=final_status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=refund_outcome["reason"],
        )

    trace.add("host_gate", {"ok": True, "reason": refund_outcome["reason"], "status": "resolved"})
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

