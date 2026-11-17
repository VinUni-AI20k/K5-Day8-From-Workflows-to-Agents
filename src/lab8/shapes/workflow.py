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

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("workflow", claim_id, seed))
    conn = connect(store_path)

    def respond(
        status: str, proposal_amount: int = 0, error_reason: str | None = None
    ) -> RunResult:
        # Mọi nhánh đều ghi trace và lấy kết quả thực tế từ ledger qua finish.
        trace.add("decision", {"status": status, "reason": error_reason})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal_amount,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )

    try:
        # CP2: chỉ đọc claim qua view an toàn; không ghi ticket vào trace.
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("get_claim_view", {"found": claim["found"]})
        if not claim["found"]:
            return respond("failed", error_reason="unknown_claim")
        if not claim["order_id"]:
            return respond("needs_info", error_reason="missing_order_id")

        # lookup_order kiểm quyền sở hữu và chỉ trả các field được phép.
        budget.add_tool(tool_cost())
        order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
        trace.add("lookup_order", order_view)
        if not order_view["visible"]:
            return respond("escalated", error_reason=order_view["reason"])

        # Tiền do code tính từ order và policy hiện hành, không từ lời ticket.
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, order_view["order"])
        proposal = int(quote["amount_vnd"])
        trace.add("quote", quote)
        if proposal <= 0:
            return respond("denied", error_reason=quote["reason"])

        # Truyền quote đầy đủ: host tự kiểm approval và trừ phần đã hoàn.
        # CP3: chuyển tiếp crash_at, để InjectedCrash truyền ra ngoài.
        budget.add_tool(tool_cost())
        trace.add("issue_refund", {"proposal_amount": proposal})
        # Lưu bước sắp ghi tiền để vẫn có trace nếu host gây crash thử nghiệm.
        trace.write()
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add(
            "refund_outcome",
            {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]},
        )
        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return respond(status, proposal, outcome["reason"])
        return respond("resolved", proposal)
    finally:
        # Luôn đóng kết nối, kể cả khi crash; không nuốt exception của host.
        conn.close()
