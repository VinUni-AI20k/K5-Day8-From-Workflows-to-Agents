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

from lab8 import durability
from lab8.db import connect
from lab8.mock_llm import complete
from lab8.schemas import RunResult
from lab8.runtime import run_react
from lab8.schemas import Budget, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace

SHAPE = "single"


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

    def decide(observation: dict) -> dict:
        last_tool = observation.get("last_tool")
        last_result = observation.get("last_result") or {}
        if last_tool is None:
            action = {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
        elif last_tool == "get_claim_view":
            if not last_result.get("found"):
                action = {"final": {"status": "failed", "proposal_amount": 0, "reason": "unknown_claim"}}
            elif not last_result.get("order_id"):
                action = {"final": {"status": "needs_info", "proposal_amount": 0, "reason": "missing_order_id"}}
            else:
                action = {
                    "tool": "lookup_order",
                    "args": {
                        "order_id": last_result["order_id"],
                        "principal_id": last_result["principal_id"],
                    },
                }
        elif last_tool == "lookup_order":
            if not last_result.get("visible"):
                action = {
                    "final": {
                        "status": "escalated",
                        "proposal_amount": 0,
                        "reason": last_result.get("reason"),
                    }
                }
            else:
                action = {
                    "tool": "compute_compensation",
                    "args": {"order": last_result["order"]},
                }
        elif last_tool == "compute_compensation":
            amount = int(last_result.get("amount_vnd") or 0)
            action = {
                "final": {
                    "status": "denied" if amount <= 0 else "quoted",
                    "proposal_amount": amount,
                    "reason": last_result.get("reason"),
                }
            }
        else:
            action = {"final": {"status": "failed", "proposal_amount": 0, "reason": "invalid_agent_state"}}

        complete(
            budget,
            seed=seed,
            purpose="react",
            prompt=f"state={last_tool or 'start'} action={action.get('tool') or action['final']['status']}",
        )
        if "tool" in action:
            trace.add("agent_action", {"tool": action["tool"]})
        else:
            trace.add(
                "agent_decision",
                {
                    "status": action["final"]["status"],
                    "proposal_amount": action["final"]["proposal_amount"],
                    "reason": action["final"].get("reason"),
                },
            )
        return action

    result = run_react(
        conn,
        budget,
        observation={"claim_id": claim_id},
        decide=decide,
        max_steps=8,
    )
    final = result["final"]
    status = final["status"]
    proposal = int(final.get("proposal_amount") or 0)
    reason = final.get("reason")

    if status != "quoted":
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

    try:
        outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except durability.InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    trace.add(
        "issue_refund",
        {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]},
    )
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish(
            conn,
            shape=SHAPE,
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
        shape=SHAPE,
        claim_id=claim_id,
        seed=seed,
        status="resolved",
        proposal_amount=proposal,
        budget=budget,
        trace=trace,
        error_reason=None,
    )
