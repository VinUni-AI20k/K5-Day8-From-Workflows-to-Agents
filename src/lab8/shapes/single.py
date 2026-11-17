"""Shape B — one bounded, read-only ReAct agent with a host-owned writer.

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
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
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


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))
    claim: dict[str, Any] = {}
    order: dict[str, Any] = {}
    quote: dict[str, Any] = {}

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": proposal})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    def read(name: str, **args: Any) -> dict[str, Any]:
        # This private adapter only receives the literal read-tool names below.
        # Arguments and raw observations never enter the trace.
        trace.add("action", {"tool": name})
        return {"tool": name, "args": args}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        nonlocal claim, order, quote
        last_tool = observation.get("last_tool")
        result = observation.get("last_result") or {}

        # MockLLM emits seeded acknowledgements, not tool-call JSON. The action
        # adapter below interprets observations and constrains the next action.
        # complete() accounts for every model call in this run's Budget.
        complete(
            budget,
            seed=seed,
            purpose="react",
            prompt=f"Read-only investigation; previous tool: {last_tool or 'start'}",
        )

        if last_tool is None:
            return read("get_claim_view", claim_id=claim_id)

        if last_tool == "get_claim_view":
            # Ticket text is untrusted, including order IDs and policy claims.
            # Keep only structured routing fields; never forward the ticket.
            claim = {key: result.get(key) for key in ("found", "order_id", "principal_id")}
            trace.add("claim", {"found": bool(claim["found"]), "has_order_id": bool(claim["order_id"])})
            if not claim["found"]:
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            if not claim["order_id"]:
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}
            return read("lookup_order", order_id=claim["order_id"], principal_id=claim["principal_id"])

        if last_tool == "lookup_order":
            trace.add("order_scope", {"visible": bool(result.get("visible"))})
            if not result.get("visible"):
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            # Only the scoped tool's structured order can feed the calculator.
            order = dict(result["order"])
            return read("lookup_policy")

        if last_tool == "lookup_policy":
            # lookup_policy filters is_current and effective_date using the
            # pinned lab date. Never fetch a clause cited by the ticket.
            trace.add("policy", {"current_policy_count": len(result.get("policies") or [])})
            return read(
                "lookup_refund_history",
                order_id=claim["order_id"],
                principal_id=claim["principal_id"],
            )

        if last_tool == "lookup_refund_history":
            if not result.get("visible"):
                return {"final": {"status": "escalated", "error_reason": result.get("reason")}}
            trace.add(
                "refund_history",
                {"refund_count": int(result["refund_count"]), "refunded_vnd": int(result["refunded_vnd"])},
            )
            # History is evidence, not a deduction from the quote: the host
            # excludes this claim's own effect and applies the order cap once.
            return read("compute_compensation", order=order)

        if last_tool == "compute_compensation":
            # This result comes from deterministic code, never model text.
            quote = dict(result)
            amount = int(quote["amount_vnd"])
            trace.add("quote", {"amount_vnd": amount})
            if amount <= 0:
                return {"final": {"status": "denied", "error_reason": quote.get("reason")}}
            return {"final": {"status": "quoted"}}

        return {"final": {"status": "failed", "error_reason": "unexpected_observation"}}

    investigated = run_react(
        conn,
        budget,
        observation={},
        decide=decide,
        max_steps=8,
        worker=True,
    )
    final = investigated["final"]
    if final["status"] != "quoted":
        return done(final["status"], reason=final.get("error_reason"))

    # Host boundary: use the code-produced full quote, not a model amount or
    # a net amount. Only durability writes, checks approval and enforces caps.
    proposal = int(quote["amount_vnd"])
    trace.add("host", {"tool": "issue_refund", "proposal_amount": proposal})
    # Flush before the crash window without catching InjectedCrash.
    trace.write()
    budget.add_tool(tool_cost())
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])
    return done("resolved", proposal)
