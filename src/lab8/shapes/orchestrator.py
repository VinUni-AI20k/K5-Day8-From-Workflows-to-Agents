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

Thiết kế của nhóm (issue #4):

    Orchestrator (giữ claim view, là nơi DUY NHẤT được ghi)
      │
      ├─ handoff (allowlist) ──▶ Investigator  [lookup_order, lookup_refund_history, get_clause]
      │                            ├─ lookup_order           → order view (đã lọc PII)
      │                            ├─ lookup_refund_history  → đơn đã hoàn bao nhiêu
      │                            └─ get_clause             → clause được trích có còn hiệu lực?
      │
      ├─ compute_compensation(order view)   ← tiền do code tính, không đọc số trong ticket
      └─ durability.issue_refund(full quote, crash_at=crash_at)

MockLLM chỉ soạn câu trả lời cho khách. Nó không quyết số tiền, không quyết status.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8 import durability
from lab8.db import connect
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import dispatch, run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_refund_history", "get_clause"]


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _orchestrate(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _orchestrate(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int = 0, reason: str | None = None) -> RunResult:
        trace.add("decision", {"status": status, "proposal_amount": int(proposal), "reason": reason})
        if status != "failed":
            # Model chỉ soạn chữ. Prompt chỉ có status, không có tiền, không có ticket.
            complete(budget, seed=seed, purpose="draft", prompt=status)
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

    # ------------------------------------------------------------------
    # Bước 1. Orchestrator đọc claim qua view đã lọc (không SELECT *).
    #         View không có parent_secret / raw_headers.
    # ------------------------------------------------------------------
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim.get("found"):
        return done("failed", 0, "unknown_claim")

    # ------------------------------------------------------------------
    # Bước 2. Thiếu order_id -> needs_info. Không lấy mã đơn từ chữ trong ticket.
    # ------------------------------------------------------------------
    if not claim.get("order_id"):
        return done("needs_info", 0, "missing_order_id")

    # ------------------------------------------------------------------
    # Bước 3. Dựng handoff bằng allowlist. facts rỗng: orchestrator không
    #         chuyển ticket hay claim row cho investigator.
    # ------------------------------------------------------------------
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="investigate_order_refund_history_and_clauses",
        facts={},
        allowed_tools=INVESTIGATOR_TOOLS,
    )
    trace.add("handoff", safe_dump(handoff))

    # ------------------------------------------------------------------
    # Bước 4. Investigator chỉ đọc (worker=True: runtime chặn mọi tool ghi).
    # ------------------------------------------------------------------
    investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    order_view = investigated["tools"].get("lookup_order") or {}
    history = investigated["tools"].get("lookup_refund_history") or {}
    trace.add(
        "investigator",
        {
            "order_visible": bool(order_view.get("visible")),
            "order_reason": order_view.get("reason"),
            # lookup_order chỉ trả ORDER_FIELDS: không có SĐT, địa chỉ, tên hàng, ghi chú nội bộ.
            "order": safe_dump(order_view["order"]) if order_view.get("visible") else None,
            "refunded_vnd": history.get("refunded_vnd"),
            "refund_count": history.get("refund_count"),
        },
    )

    # Không thấy đơn, hoặc principal không sở hữu đơn -> escalated.
    if not order_view.get("visible"):
        return done("escalated", 0, order_view.get("reason"))

    # ------------------------------------------------------------------
    # Bước 5. Orchestrator tính tiền từ order view (dữ liệu DB), bằng code.
    # ------------------------------------------------------------------
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, dict(order_view["order"]))
    proposal = int(quote["amount_vnd"])
    trace.add(
        "quote",
        {
            "amount_vnd": proposal,
            "reason": quote.get("reason"),
            "clause_ids": list(quote.get("clause_ids") or []),
        },
    )

    # Quote 0 -> denied, không gọi host (nên không có policy_denied).
    if proposal <= 0:
        return done("denied", 0, quote.get("reason"))

    # ------------------------------------------------------------------
    # Bước 6. Investigator kiểm clause được trích bằng get_clause (read-only).
    #         get_clause trả cả clause cũ, nên phải tự kiểm is_current.
    # ------------------------------------------------------------------
    clause_checks = _verify_clauses(conn, budget, quote, handoff)
    trace.add("clause_check", {"clauses": clause_checks})
    if not all(item["is_current"] for item in clause_checks):
        return done("denied", 0, "clause_not_current")

    # ------------------------------------------------------------------
    # Bước 7. Chỉ orchestrator ghi. Truyền QUOTE ĐẦY ĐỦ + crash_at.
    #         Không try/except InjectedCrash: để crash nổi lên cho T12.
    # ------------------------------------------------------------------
    outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    trace.add(
        "host",
        {
            "ok": bool(outcome["ok"]),
            "reason": outcome["reason"],
            "conflict": bool(outcome["conflict"]),
        },
    )

    # ------------------------------------------------------------------
    # Bước 8. Đổi kết quả host thành status.
    # ------------------------------------------------------------------
    if outcome["ok"]:
        return done("resolved", proposal, None)
    if outcome["conflict"]:
        return done("failed", proposal, outcome["reason"])
    return done("denied", proposal, outcome["reason"])  # host đã ghi policy_denied


def _verify_clauses(
    conn: sqlite3.Connection,
    budget: Budget,
    quote: dict[str, Any],
    handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    """Investigator gọi get_clause cho clause thắng. Chỉ dùng tool có trong handoff."""
    if "get_clause" not in handoff["allowed_tools"]:
        return []
    parts = quote.get("parts") or {}
    winner = max(parts, key=parts.get) if parts else None
    if winner is None:
        return []
    found = dispatch(conn, budget, "get_clause", {"clause_id": winner}, worker=True)
    return [
        {
            "clause_id": winner,
            "found": bool(found.get("found")),
            "is_current": bool(found.get("found") and found.get("is_current")),
            "policy_id": found.get("policy_id"),
        }
    ]