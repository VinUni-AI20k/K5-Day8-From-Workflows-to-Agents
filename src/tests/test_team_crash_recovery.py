"""Thanh: recovery across connections, repeated retries, top-up and approval."""

from __future__ import annotations

import json
import time

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import trial_pass
from lab8.policy import order_refunded_vnd
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID


@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
@pytest.mark.parametrize("claim_id,quote,paid", [("C-001", 35000, 35000), ("C-014", 150000, 120000)])
def test_workflow_reopens_and_retries_after_each_crash(public_db, point, claim_id, quote, paid):
    with pytest.raises(InjectedCrash, match=point):
        run_claim(claim_id, seed=11, store_path=str(public_db), crash_at=point)

    # This is a new connection after workflow has closed its crashed connection.
    conn = connect(public_db)
    try:
        effect = get_refund(conn, claim_id)
        checkpoint = conn.execute(
            "SELECT result_json FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'", (claim_id,)
        ).fetchone()
        if point == "before_effect":
            assert effect is None
            assert committed_audit_count(conn, claim_id) == 0
        else:
            assert effect["amount_vnd"] == paid
            assert committed_audit_count(conn, claim_id) == 1
        assert (checkpoint is not None) == (point == "after_checkpoint")
    finally:
        conn.close()

    # Resume, then replay repeatedly, with a fresh connection on every run.
    for _ in range(4):
        started = time.time()
        result = run_claim(claim_id, seed=11, store_path=str(public_db))
        assert result.proposal_amount == quote
        conn = connect(public_db)
        try:
            passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started)
            assert passed, reason
            assert conn.execute(
                "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = ?", (claim_id,)
            ).fetchone()[0] == 1
            assert get_refund(conn, claim_id)["idempotency_key"] == f"refund:{claim_id}"
            checkpoint = conn.execute(
                "SELECT result_json FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'", (claim_id,)
            ).fetchone()
            assert json.loads(checkpoint["result_json"])["amount_vnd"] == paid
            if claim_id == "C-014":
                assert order_refunded_vnd(conn, "O-515") == 150000
        finally:
            conn.close()


@pytest.mark.parametrize("approval,reason", [(None, "missing_approval"), ("A-014", "approval_claim_mismatch")])
def test_workflow_repeated_denial_never_writes_money(public_db, approval, reason):
    conn = connect(public_db)
    try:
        conn.execute("UPDATE claims SET approval_id = ? WHERE claim_id = 'C-001'", (approval,))
        conn.commit()
    finally:
        conn.close()
    for _ in range(3):
        result = run_claim("C-001", seed=11, store_path=str(public_db))
        assert result.status == "denied"
        assert result.error_reason == reason
        conn = connect(public_db)
        try:
            assert get_refund(conn, "C-001") is None
            assert committed_audit_count(conn, "C-001") == 0
            assert conn.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE claim_id = 'C-001'"
            ).fetchone()[0] == 0
            assert conn.execute(
                "SELECT COUNT(*) FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'policy_denied'"
            ).fetchone()[0] == 1
        finally:
            conn.close()
