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

from lab8.schemas import RunResult
from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, make_run_id
from lab8.shapes.common import finish
from lab8.tools import tool_cost
from lab8.trace import Trace


class ClaimRun:
    def __init__(self, conn, shape, claim_id, seed):
        self.conn, self.shape, self.claim_id, self.seed = conn, shape, claim_id, seed
        self.budget = Budget()
        self.trace = Trace(make_run_id(shape, claim_id, seed))

    def read(self, name, function, *args):
        self.budget.add_tool(tool_cost())
        result = function(self.conn, *args)
        if name != "get_claim_view":
            self.trace.add(name, result)
        else:
            self.trace.add(name, {key: result[key] for key in ("found", "claim_id", "order_id") if key in result})
        return result

    def finish(self, status, proposal=0, reason=None):
        self.trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
        return finish(self.conn, shape=self.shape, claim_id=self.claim_id, seed=self.seed,
                      status=status, proposal_amount=proposal, budget=self.budget,
                      trace=self.trace, error_reason=reason)

    def settle(self, quote, crash_at):
        proposal = int(quote["amount_vnd"])
        if proposal <= 0:
            return self.finish("denied", reason=quote.get("reason"))
        outcome = issue_refund(self.conn, self.claim_id, proposal, crash_at=crash_at)
        self.trace.add("host_outcome", {"ok": outcome["ok"], "reason": outcome["reason"]})
        if outcome["ok"]:
            return self.finish("resolved", proposal)
        return self.finish("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])

from lab8.tools import compute_compensation, get_claim_view, lookup_order


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        run = ClaimRun(conn, "workflow", claim_id, seed)
        claim = run.read("get_claim_view", get_claim_view, claim_id)
        if not claim["found"]:
            return run.finish("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return run.finish("needs_info", reason="missing_order_id")
        view = run.read("lookup_order", lookup_order, claim["order_id"], claim["principal_id"])
        if not view["visible"]:
            return run.finish("escalated", reason=view["reason"])
        quote = run.read("compute_compensation", compute_compensation, view["order"])
        return run.settle(quote, crash_at)
    finally:
        conn.close()
