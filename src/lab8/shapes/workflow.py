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

Implementation notes
--------------------
* The steps above run in this fixed order, with no loop and no model-chosen branch.
  The only model call is one reply draft at the end. Its text is never read back, so
  it cannot change the status or the amount.
* The ticket is never parsed. `order_id` comes from the claim row, the delay from the
  order row, the clauses from the current policy. This is why the workflow has no
  seed-dependent behaviour (it does not copy the swarm's REFERENCE_WEAKNESS).
* Tools go through `lab8.runtime.dispatch` so the Budget counts every call. They are
  all read tools. The only write is `durability.issue_refund`, called from here.
* The trace records only allowlisted views: the claim id, the allowlisted order fields
  (`tools.ORDER_FIELDS`), the quote and the host verdict. It never records the claim
  row, the ticket text, an approval or the host's `effect` row.
* `crash_at` is forwarded untouched. `InjectedCrash` is not swallowed; the trace is
  flushed first so a crashed run still leaves a readable file, then the crash re-raises.
"""

from __future__ import annotations

import sqlite3

from lab8 import durability
from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.mock_llm import complete
from lab8.runtime import dispatch
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
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

    def done(status: str, proposal: int, reason: str | None, *, draft: bool = True) -> RunResult:
        # The reply draft is text only. Nothing below reads it back.
        if draft:
            complete(budget, seed=seed, purpose="draft", prompt=f"status={status};proposal={proposal}")
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

    # 1. Claim, through the allowlisted view (no parent_secret, no raw headers).
    claim = dispatch(conn, budget, "get_claim_view", {"claim_id": claim_id}, worker=False)
    trace.add("claim", {"claim_id": claim_id, "found": bool(claim.get("found")), "order_id": claim.get("order_id")})
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim", draft=False)

    # 2. No order id on the claim row. The ticket is not searched for one.
    if not claim.get("order_id"):
        return done("needs_info", 0, "missing_order_id")

    # 3. The order must exist and belong to the claim's principal.
    order_view = dispatch(
        conn,
        budget,
        "lookup_order",
        {"order_id": claim["order_id"], "principal_id": claim["principal_id"]},
        worker=False,
    )
    if not order_view.get("visible"):
        trace.add("order", {"visible": False, "reason": order_view.get("reason")})
        return done("escalated", 0, order_view.get("reason"))
    order = order_view["order"]
    trace.add("order", {"visible": True, "order": order})

    # 4. Quote from the order row and current policy. Code owns the money.
    quote = dispatch(conn, budget, "compute_compensation", {"order": order}, worker=False)
    proposal = int(quote["amount_vnd"])
    trace.add(
        "quote",
        {
            "amount_vnd": proposal,
            "reason": quote.get("reason"),
            "clause_ids": quote.get("clause_ids"),
            "parts": quote.get("parts"),
        },
    )

    # 5. Nothing owed: refuse here. The host is not called, so it writes no audit.
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # 6. Full quote to the host. It checks approval, per-order cap and idempotency.
    try:
        outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add(
        "host",
        {"ok": bool(outcome["ok"]), "reason": outcome["reason"], "conflict": bool(outcome["conflict"])},
    )

    if outcome["ok"]:
        return done("resolved", proposal, None)
    if outcome["conflict"]:
        return done("failed", proposal, outcome["reason"])
    return done("denied", proposal, outcome["reason"])
