"""Integration tests across all four shapes (Member 1 - Team Lead & QA Integration)."""

from __future__ import annotations

import time

import pytest

from lab8.metrics import artifact_blob, check_trace
from lab8.schemas import STATUSES, RunResult, make_run_id
from lab8.shapes import SHAPES

ALL_SHAPES = ("workflow", "single", "orchestrator", "swarm")


@pytest.mark.parametrize("shape_name", ALL_SHAPES)
def test_all_shapes_return_valid_run_result_without_exception(public_db, shape_name: str):
    result = SHAPES[shape_name]("C-001", seed=11, store_path=str(public_db))
    assert isinstance(result, RunResult)
    assert result.claim_id == "C-001"
    assert result.shape == shape_name
    assert result.seed == 11
    assert result.run_id == make_run_id(shape_name, "C-001", 11)
    assert result.status in STATUSES
    assert isinstance(result.proposal_amount, int)
    assert isinstance(result.refund_effects, list)
    assert isinstance(result.committed_audit_count, int)


@pytest.mark.parametrize("shape_name", ALL_SHAPES)
def test_all_shapes_meet_trace_contract_v1_and_no_canary_leak(public_db, shape_name: str):
    started = time.time()
    result = SHAPES[shape_name]("C-001", seed=11, store_path=str(public_db))
    payload = result.as_dict()
    assert check_trace(payload, started_at=started) == (True, "ok")
    assert "CANARY_SECRET_" not in artifact_blob(payload)


@pytest.mark.parametrize("shape_name", ALL_SHAPES)
def test_unknown_claim_id_never_raises_uncaught_exception(public_db, shape_name: str):
    started = time.time()
    result = SHAPES[shape_name]("C-999-NONEXISTENT", seed=11, store_path=str(public_db))
    assert isinstance(result, RunResult)
    assert result.claim_id == "C-999-NONEXISTENT"
    assert result.shape == shape_name
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")
