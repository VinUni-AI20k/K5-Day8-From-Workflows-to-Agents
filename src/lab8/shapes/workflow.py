"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

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
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.

Implementation notes (team):
- The trace only records allowlisted views: claim id / order id, the order view
  from `lookup_order` (no phone, address, item, internal note), the quote, and
  the host outcome. The ticket text, parent_secret and raw headers are never
  traced or printed.
- The single model call drafts the customer reply after the decision is made.
  Its text is not used for any decision.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
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
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, amount: int, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(amount), "reason": reason})
        # Model only drafts reply text, after code has decided. Text is not used.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status}")
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=amount,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # Step 1: read the claim through the safe view (no parent_secret / headers).
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim")
    trace.add("claim", {"claim_id": claim_id, "has_order_id": bool(claim.get("order_id"))})

    # Step 2: missing order_id -> needs_info. Never guess the order id from ticket text.
    if not claim.get("order_id"):
        return done("needs_info", 0, "missing_order_id")

    # Step 3: order lookup scoped to the claim's principal.
    budget.add_tool(tool_cost())
    view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    if not view.get("visible"):
        return done("escalated", 0, view.get("reason"))
    order = view["order"]
    trace.add("order", dict(order))  # allowlisted fields only

    # Step 4: quote from the structured order row + current policy. Ticket text is ignored.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order)
    trace.add("quote", quote)
    proposal = int(quote["amount_vnd"])

    # Step 5: nothing to pay -> denied, the host is not called.
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # Step 6: the host is the only writer. Full quote + crash_at; InjectedCrash propagates.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": bool(outcome["ok"]), "reason": outcome["reason"]})

    if not outcome["ok"]:
        status = "failed" if outcome["conflict"] else "denied"
        return done(status, proposal, outcome["reason"])
    # Step 7: committed (or idempotent replay of the same amount).
    return done("resolved", proposal, None)
