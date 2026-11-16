"""Shape C (orchestrator) — test riêng của nhóm cho issue #4.

Chạy: python -m pytest -q tests/test_orchestrator_shape_c.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.handoff import READONLY_TOOLS
from lab8.shapes.orchestrator import INVESTIGATOR_TOOLS, run_claim


def _trace(result) -> dict:
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))


def _events(result, kind: str) -> list[dict]:
    return [e["payload"] for e in _trace(result)["events"] if e["kind"] == kind]


def test_investigator_tools_are_read_only():
    assert set(INVESTIGATOR_TOOLS) <= READONLY_TOOLS
    assert "issue_refund" not in INVESTIGATOR_TOOLS


@pytest.mark.parametrize("claim_id", ["C-001", "C-005", "C-010"])
def test_handoff_in_trace_is_allowlisted_and_has_no_secret_or_pii(public_db, claim_id):
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    handoffs = _events(result, "handoff")
    assert handoffs, "orchestrator phải ghi handoff đã sanitize vào trace"
    for handoff in handoffs:
        assert set(handoff) <= {
            "contract_version", "request_id", "claim_id", "principal_scope",
            "task", "facts", "allowed_tools", "max_output_tokens",
        }
        assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    blob = json.dumps(_trace(result), ensure_ascii=False)
    for forbidden in ("CANARY_SECRET_", "parent_secret", "raw_headers", "ticket",
                      "0901", "Duong Bi Mat", "12 Le Loi", "SECRET_ITEM", "CANARY_INTERNAL"):
        assert forbidden not in blob, forbidden


def test_ticket_delay_is_ignored_even_on_seed_55(public_db):
    # C-002: ticket ghi "trễ 5 ngày" nhưng order row chỉ trễ 2 → denied, không ghi ledger.
    result = run_claim("C-002", seed=55, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    conn = connect(public_db)
    try:
        n = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-002'").fetchone()["n"]
    finally:
        conn.close()
    assert n == 0


def test_full_quote_passed_and_host_pays_only_difference(public_db):
    # T14: đã hoàn 30.000 ship, nay hỏng hàng verify (150.000) → proposal 150.000, ledger 120.000.
    result = run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert sum(e["amount_vnd"] for e in result.refund_effects) == 120000


def test_crash_propagates_then_resume_keeps_one_refund(public_db):
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(public_db), crash_at="after_effect_before_checkpoint")
    again = run_claim("C-012", seed=11, store_path=str(public_db))
    assert again.status == "resolved"
    assert again.committed_audit_count == 1
    assert len(again.refund_effects) == 1