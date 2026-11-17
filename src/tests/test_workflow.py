"""Focused tests for the deterministic workflow shape."""

from __future__ import annotations

import json

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import check_trace
from lab8.shapes.workflow import run_claim


@pytest.mark.parametrize(
    ("claim_id", "status"),
    [
        ("C-004", "needs_info"),
        ("C-005", "escalated"),
        ("C-002", "denied"),
    ],
)
def test_non_refundable_paths_do_not_write_ledger(public_db, claim_id, status):
    result = run_claim(claim_id, seed=11, store_path=str(public_db))

    assert result.status == status
    conn = connect(public_db)
    try:
        assert get_refund(conn, claim_id) is None
        assert committed_audit_count(conn, claim_id) == 0
    finally:
        conn.close()


def test_success_uses_host_refund_gate_and_writes_one_audit(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    conn = connect(public_db)
    try:
        refund = get_refund(conn, "C-001")
        assert refund["amount_vnd"] == 35000
        assert committed_audit_count(conn, "C-001") == 1
    finally:
        conn.close()


def test_missing_approval_is_denied_without_refund(public_db):
    result = run_claim("C-007", seed=11, store_path=str(public_db))

    assert result.status == "denied"
    assert result.proposal_amount == 35000
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-007") is None
        assert committed_audit_count(conn, "C-007") == 0
        denied = conn.execute(
            "SELECT 1 FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
            ("C-007",),
        ).fetchone()
        assert denied is not None
    finally:
        conn.close()


def test_crash_then_retry_is_idempotent(public_db):
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-012",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

    result = run_claim("C-012", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-012")["amount_vnd"] == 35000
        assert committed_audit_count(conn, "C-012") == 1
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?", ("C-012",)
        ).fetchone()["n"]
        assert count == 1
    finally:
        conn.close()


def test_trace_is_written_and_contains_no_parent_secret(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db)).as_dict()

    assert check_trace(result)[0] is True
    trace = json.loads(open(result["trace_path"], encoding="utf-8").read())
    serialized = json.dumps(trace, ensure_ascii=False)
    assert "CANARY_SECRET_PARENT_C-001" not in serialized
    assert "Bearer CANARY_SECRET_PARENT_C-001" not in serialized
