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
"""

from __future__ import annotations

import sqlite3

from lab8 import durability
from lab8.db import connect
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

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        # The only model call: draft the customer reply from a decision code already made.
        # The prompt never contains the ticket, so ticket text cannot steer anything.
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status} amount={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
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

    # 1. Allowlisted claim view: no parent_secret, no raw headers. The ticket is never traced.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    trace.add("get_claim_view", {"found": claim["found"], "has_order_id": bool(claim.get("order_id"))})
    if not claim["found"]:
        return done("failed", 0, "unknown_claim")

    # 2. order_id comes from the claim row only, never parsed out of the ticket text.
    if not claim["order_id"]:
        return done("needs_info", 0, "missing_order_id")

    # 3. Ownership + existence. lookup_order already drops phone, address, item, internal note.
    budget.add_tool(tool_cost())
    view = lookup_order(conn, claim["order_id"], claim["principal_id"])
    if not view["visible"]:
        trace.add("lookup_order", {"visible": False, "reason": view["reason"]})
        return done("escalated", 0, view["reason"])
    order = view["order"]
    trace.add("lookup_order", {"visible": True, "order": order})

    # 4-5. Quote from the order row and current policy only. Delay written in the ticket is ignored.
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order)
    amount = int(quote["amount_vnd"])
    trace.add(
        "compute_compensation",
        {"amount_vnd": amount, "reason": quote["reason"], "clause_ids": quote["clause_ids"]},
    )
    if amount <= 0:
        return done("denied", 0, quote["reason"])

    # 6. Full quote to the host. The host checks approval and subtracts earlier refunds on this order.
    try:
        outcome = durability.issue_refund(conn, claim_id, amount, crash_at=crash_at)
    except durability.InjectedCrash:
        # Flush the trace, then let the crash propagate (T12 / crash suite need it).
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add(
        "issue_refund",
        {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]},
    )
    if not outcome["ok"]:
        # proposal_amount stays the full quote, even when the host refuses.
        return done("failed" if outcome["conflict"] else "denied", amount, outcome["reason"])

    # 7. One ledger row and one refund_committed audit; finish() reads both from the ledger.
    return done("resolved", amount, None)
