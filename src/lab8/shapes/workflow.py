"""Shape A — deterministic workflow.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Steps (money stays in code, `lab8.tools.compute_compensation`):

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. MockLLM only drafts the reply text, from the decision (never from the ticket).

The model never chooses the refund amount and never commits the refund.

Trace contract v1 (docs/contracts.md): every return path, including early ones
and an injected crash, writes `traces/<run_id>.json` with
{"run_id": <same run_id>, "events": [...]}. Events only carry allowlisted
fields: no ticket text, no parent_secret, no headers, no order PII.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8 import durability
from lab8.db import connect
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace

SHAPE = "workflow"


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    run_id = make_run_id(SHAPE, claim_id, seed)
    trace = Trace(run_id)
    budget = Budget()
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at, trace=trace, budget=budget)
    except durability.InjectedCrash:
        # Fault lab: flush the trace, then let the crash reach the caller (T12).
        trace.write()
        raise
    except Exception as exc:  # run_claim must not raise; report a failed trial instead.
        reason = f"exception:{type(exc).__name__}"
        trace.add("error", {"reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
    trace: Trace,
    budget: Budget,
) -> RunResult:
    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        _draft_reply(budget, seed=seed, status=status, proposal=proposal)
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

    # Step 1 — allowlisted claim view. Ticket text is user data; it is never parsed for
    # order ids or delays and never copied into the trace.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add(
        "get_claim_view",
        {
            "claim_id": claim_id,
            "found": bool(claim.get("found")),
            "order_id": claim.get("order_id"),
        },
    )
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim")

    # Step 2 — no order id on the claim row: ask for it, never guess from the ticket.
    order_id = claim.get("order_id")
    if not order_id:
        return done("needs_info", 0, "missing_order_id")

    # Step 3 — ownership check. lookup_order already strips phone/address/item/note.
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, order_id, claim["principal_id"])
    trace.add("lookup_order", safe_dump(order_view))
    if not order_view.get("visible"):
        return done("escalated", 0, order_view.get("reason"))

    # Step 4 — quote from the order row and current policy only.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    trace.add("compute_compensation", safe_dump(quote))
    proposal = int(quote["amount_vnd"])

    # Step 5 — nothing owed: deny without touching the host write path.
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # Step 6 — host gate: approval, per-order cap, idempotency. FULL quote, crash_at forwarded,
    # InjectedCrash deliberately not caught here.
    trace.add("issue_refund_request", {"claim_id": claim_id, "proposed_vnd": proposal, "crash_at": crash_at})
    outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add(
        "issue_refund_result",
        {
            "ok": bool(outcome["ok"]),
            "reason": outcome["reason"],
            "conflict": bool(outcome["conflict"]),
            "amount_vnd": _effect_amount(outcome.get("effect")),
        },
    )
    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])

    # Step 7 — committed (or idempotent replay of the same amount).
    return done("resolved", proposal, None)


def _draft_reply(budget: Budget, *, seed: int, status: str, proposal: int) -> str:
    """One model call for the customer-facing text. Prompt holds the decision only."""
    return complete(budget, seed=seed, purpose="draft", prompt=f"status={status} proposal={proposal}")


def _effect_amount(effect: dict[str, Any] | None) -> int | None:
    if not effect:
        return None
    return int(effect["amount_vnd"])
