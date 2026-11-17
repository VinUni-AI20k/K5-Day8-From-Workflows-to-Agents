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
from lab8.runtime import dispatch, run_readonly_investigators
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
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("orchestrator", claim_id, seed)
    trace = Trace(run_id)

    def finish_result(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        # Draft from the decision only; raw ticket text never enters the trace.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}; proposal={proposal}")
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

    claim = dispatch(conn, budget, "get_claim_view", {"claim_id": claim_id}, worker=False)
    if not claim["found"]:
        return finish_result("failed", reason="unknown_claim")
    if not claim.get("order_id"):
        return finish_result("needs_info", reason="missing_order_id")

    # The plan is bounded by code. Neither the ticket nor model output grants tools.
    handoff = make_handoff(
        request_id=f"REQ-{run_id}",
        claim_id=claim_id,
        task="check_applicable_policy",
        facts={},
        allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history"],
    )
    complete(budget, seed=seed, purpose="plan", prompt=handoff["task"])
    trace.add("handoff", handoff)
    investigated = run_readonly_investigators(
        conn, budget, handoff, principal_id=claim["principal_id"]
    )
    tools = investigated["tools"]
    order_view = tools["lookup_order"]
    # Record only operational summaries, never the claim/ticket or raw DB rows.
    trace.add("investigator", {
        "visible": order_view["visible"],
        "reason": order_view["reason"],
        "policy_count": len(tools["lookup_policy"]["policies"]),
        "refunded_vnd": tools["lookup_refund_history"].get("refunded_vnd"),
    })
    if not order_view["visible"]:
        return finish_result("escalated", reason=order_view["reason"])

    # Quote from the structured order, even when the ticket claims otherwise.
    quoted = dispatch(
        conn, budget, "compute_compensation", {"order": order_view["order"]}, worker=False
    )
    proposal = int(quoted["amount_vnd"])
    trace.add("quote", quoted)
    if proposal <= 0:
        return finish_result("denied", reason=quoted["reason"])

    # Pass the FULL quote. Only the host subtracts earlier refunds and checks approval.
    trace.add("refund_request", {"proposal_amount": proposal})
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    finally:
        # Flush a safe trace on crash too, without swallowing InjectedCrash.
        trace.write()
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return finish_result(status, proposal, outcome["reason"])
    return finish_result("resolved", proposal)
