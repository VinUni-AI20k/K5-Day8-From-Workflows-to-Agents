"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, tool_cost
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
    trace = Trace(make_run_id("orchestrator", claim_id, seed))

    def respond(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        # Neither the model nor the trace receives ticket text or raw database rows.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status};proposal={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("claim", {"found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
    if not claim["found"]:
        return respond("failed", reason="unknown_claim")
    if not claim.get("order_id"):
        return respond("needs_info", reason="missing_order_id")

    # MockLLM accounts for planning; capabilities and all money decisions stay in code.
    complete(budget, seed=seed, purpose="plan", prompt="check_owner_order_current_policy_refund_history")
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history"],
    )
    trace.add("handoff", handoff)
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim["principal_id"]
    )
    tools = investigated["tools"]
    order_view = tools["lookup_order"]
    # Log only operational facts, never order_id, carrier or other free-form values.
    trace.add(
        "investigator",
        {
            "visible": bool(order_view["visible"]),
            "policy_count": len(tools["lookup_policy"]["policies"]),
            "refunded_vnd": tools["lookup_refund_history"].get("refunded_vnd", 0),
        },
    )
    if not order_view["visible"]:
        return respond("escalated", reason=order_view["reason"])

    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    proposal = int(quote["amount_vnd"])
    trace.add("quote", {"amount_vnd": proposal})
    if proposal <= 0:
        return respond("denied", reason=quote["reason"])

    # Flush before the write so an injected crash still leaves a safe trace.
    trace.add("refund_request", {"proposal_amount": proposal})
    trace.write()
    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add("refund_outcome", {"ok": outcome["ok"], "reason": outcome["reason"]})
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return respond(status, proposal, outcome["reason"])
    return respond("resolved", proposal)
