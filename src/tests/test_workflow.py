"""Additional workflow cases contributed by Nguyen Duc Minh (2A202603765)."""

import json
import time
from contextlib import closing

import pytest

from lab8.db import connect
from lab8.metrics import check_trace
from lab8.shapes.workflow import run_claim

pytestmark = pytest.mark.student


@pytest.fixture
def workflow_db(public_db, tmp_path, monkeypatch):
    # Keep generated traces inside each test's temporary directory.
    monkeypatch.chdir(tmp_path)
    return str(public_db)


def test_workflow_unknown_claim_writes_trace_without_changing_ledger(workflow_db):
    with closing(connect(workflow_db)) as conn:
        before = [tuple(row) for row in conn.execute("SELECT * FROM refund_ledger ORDER BY claim_id")]

    started_at = time.time()
    result = run_claim("C-UNKNOWN", seed=11, store_path=workflow_db)

    assert result.claim_id == "C-UNKNOWN"
    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    assert check_trace(result.as_dict(), started_at=started_at) == (True, "ok")
    with closing(connect(workflow_db)) as conn:
        after = [tuple(row) for row in conn.execute("SELECT * FROM refund_ledger ORDER BY claim_id")]
    assert after == before


def test_workflow_missing_approval_keeps_full_quote_and_records_denial(workflow_db):
    with closing(connect(workflow_db)) as conn:
        conn.execute("UPDATE claims SET approval_id = NULL WHERE claim_id = 'C-001'")
        conn.commit()

    result = run_claim("C-001", seed=11, store_path=workflow_db)

    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    with closing(connect(workflow_db)) as conn:
        denials = conn.execute(
            "SELECT details_json FROM audit_events "
            "WHERE claim_id = 'C-001' AND event_type = 'policy_denied'"
        ).fetchall()
        count = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchone()[0]
    assert count == 0
    assert len(denials) == 1
    assert json.loads(denials[0]["details_json"])["reason"] == result.error_reason


def test_workflow_changed_quote_on_retry_preserves_original_refund(workflow_db):
    first = run_claim("C-001", seed=11, store_path=workflow_db)
    assert first.status == "resolved"
    assert first.refund_effects[0]["amount_vnd"] == 35000

    # Simulate corrected shipping data after the original refund was committed.
    with closing(connect(workflow_db)) as conn:
        conn.execute("UPDATE orders SET shipping_fee_vnd = 20000 WHERE order_id = 'O-107'")
        conn.commit()

    retried = run_claim("C-001", seed=11, store_path=workflow_db)

    assert retried.status == "failed"
    assert retried.error_reason == "amount_conflict"
    assert retried.proposal_amount == 20000
    assert retried.refund_effects == first.refund_effects
    assert retried.committed_audit_count == 1
    with closing(connect(workflow_db)) as conn:
        rows = conn.execute(
            "SELECT amount_vnd FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchall()
    assert [row["amount_vnd"] for row in rows] == [35000]
