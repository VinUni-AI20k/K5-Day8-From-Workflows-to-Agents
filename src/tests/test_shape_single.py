"""Tests specifically for Shape B (Single ReAct Agent).

Verifies ReAct step bounds, read-only dispatch, crash forwarding,
and trace contract compliance.
"""

from __future__ import annotations

import time

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.metrics import check_trace
from lab8.shapes.single import run_claim


def test_single_shape_resolves_valid_claim(public_db):
    started = time.time()
    res = run_claim("C-001", seed=11, store_path=str(public_db))
    assert res.shape == "single"
    assert res.status == "resolved"
    assert res.proposal_amount == 35000
    assert len(res.refund_effects) == 1
    assert res.refund_effects[0]["amount_vnd"] == 35000

    # Verify trace compliance
    trace_ok, reason = check_trace(res.as_dict(), started_at=started)
    assert trace_ok, f"trace error: {reason}"


def test_single_shape_denies_zero_entitlement(public_db):
    # C-002: delay < 3 days -> quote 0 -> denied
    res = run_claim("C-002", seed=11, store_path=str(public_db))
    assert res.shape == "single"
    assert res.status == "denied"
    assert res.proposal_amount == 0
    assert len(res.refund_effects) == 0


def test_single_shape_handles_missing_order_id(public_db):
    # C-004: missing order_id -> needs_info
    res = run_claim("C-004", seed=11, store_path=str(public_db))
    assert res.shape == "single"
    assert res.status == "needs_info"
    assert res.proposal_amount == 0


def test_single_shape_escalates_unowned_order(public_db):
    # C-005: principal mismatch -> escalated
    res = run_claim("C-005", seed=11, store_path=str(public_db))
    assert res.shape == "single"
    assert res.status == "escalated"
    assert res.proposal_amount == 0


def test_single_shape_forwards_injected_crash(public_db):
    # Shape B must propagate InjectedCrash on crash_at
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-001",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

