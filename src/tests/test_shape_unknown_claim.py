"""Shared result and trace contract for a claim id that is not in the store."""

import time
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import get_refund
from lab8.metrics import check_trace
from lab8.shapes import SHAPES


@pytest.mark.student
@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator", "swarm"])
def test_unknown_claim_fails_without_a_refund_and_writes_trace(shape, public_db):
    started_at = time.time()
    result = SHAPES[shape]("C-UNKNOWN", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-UNKNOWN") is None
    finally:
        conn.close()

    assert result.status == "failed"
    assert result.proposal_amount == 0
    valid, reason = check_trace(result.as_dict(), started_at=started_at)
    assert valid, reason


@pytest.mark.student
@pytest.mark.parametrize("shape,target", [
    ("workflow", "lab8.shapes.workflow.get_claim_view"),
    ("single", "lab8.runtime.get_claim_view"),
    ("orchestrator", "lab8.shapes.orchestrator.get_claim_view"),
])
def test_internal_error_returns_failed_result_without_leaking_error(shape, target, public_db, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("private reader failure")

    monkeypatch.setattr(target, fail)
    started_at = time.time()
    result = SHAPES[shape]("C-ERROR", seed=11, store_path=str(public_db))
    valid, reason = check_trace(result.as_dict(), started_at=started_at)

    assert result.status == "failed"
    assert result.error_reason == "internal_error"
    assert valid, reason
    assert "private reader failure" not in Path(result.trace_path).read_text(encoding="utf-8")


@pytest.mark.student
@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_unopenable_store_returns_failed_result(shape, tmp_path):
    started_at = time.time()
    result = SHAPES[shape]("C-STORE-ERROR", seed=11,
                           store_path=str(tmp_path / "missing" / "store.sqlite"))
    valid, reason = check_trace(result.as_dict(), started_at=started_at)

    assert result.status == "failed"
    assert result.error_reason == "internal_error"
    assert valid, reason
