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

Code / model boundary in this shape:
- Code decides: status, quote (compute_compensation), the call to issue_refund.
- MockLLM only plans the routing note and drafts the reply text. Its output is
  never parsed back into an amount, an order_id or a delay.
- The ticket text is user data. It is never put into the handoff or the trace.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_refund_history", "compute_compensation"]
# Fields of the order view that are safe to trace (lookup_order already drops PII).
TRACE_ORDER_FIELDS = (
    "order_id",
    "status",
    "delay_days",
    "shipping_fee_vnd",
    "paid_vnd",
    "damage_verified",
    "carrier",
)


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

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
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

    # 1. Orchestrator reads the claim through the allowlisted view (no parent_secret).
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim")
    trace.add("claim", {"claim_id": claim_id, "has_order_id": bool(claim.get("order_id"))})

    # 2. Missing order_id -> needs_info. Never mine an order id out of the ticket text.
    if not claim.get("order_id"):
        complete(budget, seed=seed, purpose="draft", prompt="needs_info")
        return done("needs_info", 0, "missing_order_id")

    # 3. Plan step (model). Output is a routing note only; nothing is parsed from it.
    complete(budget, seed=seed, purpose="plan", prompt=f"route claim {claim_id} to investigator")

    # 4. Typed handoff: allowlisted fields, read-only tools, no facts from the ticket.
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="investigate_order_and_quote",
        facts={},
        allowed_tools=list(INVESTIGATOR_TOOLS),
    )
    trace.add("handoff", safe_dump(handoff))

    # 5. Read-only investigators.
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    tools: dict[str, Any] = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    history = tools.get("lookup_refund_history") or {}

    if not order_view.get("visible"):
        trace.add("investigator", {"order_visible": False, "reason": order_view.get("reason")})
        complete(budget, seed=seed, purpose="draft", prompt="escalated")
        return done("escalated", 0, order_view.get("reason") or "order_not_visible")

    order = dict(order_view["order"])
    trace.add(
        "investigator",
        {
            "order_visible": True,
            "order": {key: order.get(key) for key in TRACE_ORDER_FIELDS},
            "refund_history": {
                "refund_count": int(history.get("refund_count") or 0),
                "refunded_vnd": int(history.get("refunded_vnd") or 0),
            },
        },
    )

    # 6. Orchestrator quotes from the DB order row in code. Ticket numbers are ignored.
    budget.add_tool(tool_cost())
    quote_payload = compute_compensation(conn, order)
    proposal = int(quote_payload["amount_vnd"])
    trace.add("quote", safe_dump(quote_payload))

    if proposal <= 0:
        complete(budget, seed=seed, purpose="draft", prompt="denied")
        return done("denied", 0, quote_payload.get("reason"))

    # 7. Host gate. FULL quote; the host checks approval and subtracts earlier refunds.
    complete(budget, seed=seed, purpose="draft", prompt=f"proposal={proposal}")
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])
    trace.add("refund", {"reason": outcome["reason"], "amount_vnd": int((outcome["effect"] or {}).get("amount_vnd") or 0)})
    return done("resolved", proposal, None)
