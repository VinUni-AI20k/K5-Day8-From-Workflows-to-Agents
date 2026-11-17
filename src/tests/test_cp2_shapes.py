"""Unit tests for CP2 student shapes (workflow, single, orchestrator)."""

from __future__ import annotations

import time

import pytest

from lab8.db import connect, init_store
from lab8.metrics import check_trace
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

STUDENT_SHAPES = ("workflow", "single", "orchestrator")


def _fresh_store(tmp_path, name: str):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_cp2_shapes_ignore_ticket_delay_at_seed_55(tmp_path, shape):
    """T02 (C-002) at seed 55 has ticket delay=5 but order delay_days=2 -> must deny."""
    store = _fresh_store(tmp_path, f"cp2-{shape}-c002.sqlite")
    started = time.time()
    result = SHAPES[shape]("C-002", seed=55, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_cp2_shapes_unknown_claim_returns_failed_with_valid_trace(tmp_path, shape):
    """Unknown claim_id must not raise; must return failed + valid contract-v1 trace."""
    store = _fresh_store(tmp_path, f"cp2-{shape}-unknown.sqlite")
    started = time.time()
    result = SHAPES[shape]("C-999", seed=11, store_path=str(store))
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert result.error_reason == "unknown_claim"
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_cp2_shapes_pass_full_quote_on_partially_refunded_order(tmp_path, shape):
    """T14 (C-014): shape passes full quote (150000) and host caps effect to difference (120000)."""
    store = _fresh_store(tmp_path, f"cp2-{shape}-c014.sqlite")
    started = time.time()
    result = SHAPES[shape]("C-014", seed=11, store_path=str(store))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 120000
    conn = connect(store)
    try:
        total = conn.execute(
            "SELECT SUM(amount_vnd) AS s FROM refund_ledger WHERE order_id = 'O-515'"
        ).fetchone()["s"]
    finally:
        conn.close()
    assert total == 150000
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")
