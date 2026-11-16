"""Individual technical test suite by Nguyen Khoi Vinh (vinhnk).

Verifies core idempotency and policy bounds:
1. Re-running the same claim multiple times across shapes produces exactly one refund ledger row.
2. An order with zero entitlement or unverified damage is rejected with status 'denied' and creates no ledger row.
"""

from __future__ import annotations

import pytest
import time

from lab8.db import connect, init_store
from lab8.metrics import trial_pass
from lab8.shapes import SHAPES
from tests.conftest import BY_ID, CLAIMS, WORLD

SHAPES_TO_TEST = ["workflow", "single", "orchestrator"]


def _init_store(tmp_path, name: str):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


@pytest.mark.parametrize("shape", SHAPES_TO_TEST)
def test_individual_idempotency_multi_run(tmp_path, shape):
    """Test that repeatedly invoking run_claim on C-001 never creates duplicate refunds."""
    store = _init_store(tmp_path, f"{shape}_indiv_idem.sqlite")
    
    # Run 1
    res1 = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    assert res1.status == "resolved"
    assert res1.proposal_amount == 35000
    
    # Run 2 (immediate replay)
    res2 = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    assert res2.status == "resolved"
    assert res2.proposal_amount == 35000

    conn = connect(store)
    try:
        rows = conn.execute(
            "SELECT COUNT(*) AS n, SUM(amount_vnd) AS total FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchone()
        assert rows["n"] == 1, "Must have exactly 1 ledger row after multiple runs"
        assert rows["total"] == 35000, "Refunded total must equal entitlement"
        
        audits = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-001' AND event_type = 'refund_committed'"
        ).fetchone()
        assert audits["n"] == 1, "Must record exactly 1 refund_committed audit event"
    finally:
        conn.close()


@pytest.mark.parametrize("shape", SHAPES_TO_TEST)
def test_individual_policy_denial_no_ledger_side_effects(tmp_path, shape):
    """Test that a claim with zero entitlement (C-002: delay < 3 days) produces no ledger rows."""
    store = _init_store(tmp_path, f"{shape}_indiv_denied.sqlite")
    
    res = SHAPES[shape]("C-002", seed=11, store_path=str(store))
    assert res.status == "denied"
    assert res.proposal_amount == 0
    
    conn = connect(store)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-002'"
        ).fetchone()["n"]
        assert count == 0, "No ledger rows must be inserted for denied claim"
    finally:
        conn.close()
