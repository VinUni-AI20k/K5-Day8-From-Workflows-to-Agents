"""Shape B — one ReAct agent.

Boundary between model and code:

- `decide` (the model's turn) may only pick READ tools (`lookup_order`,
  `lookup_refund_history`) or stop with a final status. It never sees a write
  tool and never chooses an amount.
- Facts come from tool results, kept in a code-side `state` dict. Ticket text is
  user data: delay numbers or "ignore policy" in the ticket are never used.
- After the loop, code quotes with `compute_compensation` from the order row and
  calls `durability.issue_refund` with the FULL quote. The host checks approval,
  the per-order cap and idempotency, and is the only writer.
- `crash_at` is forwarded to the host and `InjectedCrash` is not swallowed.

Caps: at most 8 ReAct steps; every model call goes through MockLLM and is
counted in the Budget so cost stays comparable with the other shapes.

Trace (contract v1): written on every return path. It records tool names,
loop stop reason, quote amount/reason/clauses, host outcome and the final
decision. It deliberately does NOT record the ticket text, the claim row,
the order row, parent_secret or headers.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import dispatch, run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "single"
MAX_STEPS = 8


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

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
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

    # 1. Read the claim through the allowlisted view (never SELECT *).
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        return done("failed", 0, "unknown_claim")
    trace.add("claim", {"claim_id": claim_id, "has_order_id": bool(claim["order_id"])})

    # 2. ReAct loop. run_react replaces the observation after each tool, so the
    #    facts are kept here in code, not in the model.
    state: dict[str, Any] = {"order_view": None, "history": None}

    def decide(obs: dict[str, Any]) -> dict[str, Any]:
        if obs.get("last_tool") == "lookup_order":
            state["order_view"] = obs["last_result"]
        elif obs.get("last_tool") == "lookup_refund_history":
            state["history"] = obs["last_result"]

        # One model call per step for comparable cost. Its text is not used
        # to choose amounts or to override facts from the database.
        complete(budget, seed=seed, purpose="react", prompt=claim["ticket"])

        if not claim["order_id"]:
            return {"final": {"status": "needs_info", "reason": "missing_order_id"}}
        args = {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
        if state["order_view"] is None:
            trace.add("act", {"tool": "lookup_order"})
            return {"tool": "lookup_order", "args": args}
        if not state["order_view"].get("visible"):
            return {"final": {"status": "escalated", "reason": state["order_view"].get("reason")}}
        if state["history"] is None:
            trace.add("act", {"tool": "lookup_refund_history"})
            return {"tool": "lookup_refund_history", "args": args}
        return {"final": {"status": "propose"}}

    loop = run_react(conn, budget, observation={"claim": claim_id}, decide=decide, max_steps=MAX_STEPS)
    final = loop["final"]
    trace.add("react_stop", {"stopped": loop["stopped"], "final_status": final.get("status")})

    if final.get("status") in ("needs_info", "escalated", "failed"):
        return done(final["status"], 0, final.get("reason") or final.get("error_reason"))

    # 3. Money is computed by code from the order row, never from ticket text.
    order = state["order_view"]["order"]
    quote = dispatch(conn, budget, "compute_compensation", {"order": order}, worker=False)
    proposal = int(quote["amount_vnd"])
    trace.add("quote", {"amount_vnd": proposal, "reason": quote["reason"], "clause_ids": quote["clause_ids"]})

    if proposal <= 0:
        return done("denied", 0, quote["reason"])

    # 4. Host is the only writer. Pass the full quote; the host subtracts earlier
    #    refunds on the same order. Do not swallow an injected crash.
    try:
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"]})

    complete(budget, seed=seed, purpose="draft", prompt=f"status={outcome['reason']}")
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal)
