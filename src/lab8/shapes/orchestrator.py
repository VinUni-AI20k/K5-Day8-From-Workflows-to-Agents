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

from lab8.schemas import RunResult
from lab8.db import connect
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import run_readonly_investigators
from lab8.shapes.workflow import ClaimRun
from lab8.tools import get_claim_view


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        run = ClaimRun(conn, "orchestrator", claim_id, seed)
        claim = run.read("get_claim_view", get_claim_view, claim_id)
        if not claim["found"]:
            return run.finish("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return run.finish("needs_info", reason="missing_order_id")
        complete(run.budget, seed=seed, purpose="plan", prompt="investigate owner order and current policy")
        run.trace.add("plan", {"mode": "readonly_investigation"})
        handoff = make_handoff(request_id=f"REQ-{claim_id}", claim_id=claim_id,
                               task="check_applicable_policy", facts={},
                               allowed_tools=["lookup_order", "lookup_policy", "compute_compensation"])
        run.trace.add("handoff", handoff)
        result = run_readonly_investigators(conn, run.budget, handoff, claim["principal_id"])
        run.trace.add("investigator", result)
        view = result["tools"]["lookup_order"]
        if not view["visible"]:
            return run.finish("escalated", reason=view["reason"])
        quote = result["tools"]["compute_compensation"]
        complete(run.budget, seed=seed, purpose="aggregate", prompt=f"quote={quote['amount_vnd']}")
        run.trace.add("aggregate", {"proposal_amount": quote["amount_vnd"]})
        return run.settle(quote, crash_at)
    finally:
        conn.close()
