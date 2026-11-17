"""Additional student tests for unknown claims, internal errors, conflicts, and trace safety."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import get_refund
from lab8.metrics import artifact_blob, check_trace
from lab8.shapes import SHAPES


@pytest.mark.student
@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator", "swarm"])
def test_unknown_claim_fails_without_a_refund_and_writes_trace(shape: str, public_db: Path) -> None:
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
@pytest.mark.parametrize(
    "shape,target",
    [
        ("workflow", "lab8.shapes.workflow.get_claim_view"),
        ("single", "lab8.runtime.get_claim_view"),
        ("orchestrator", "lab8.shapes.orchestrator.get_claim_view"),
    ],
)
def test_internal_error_returns_failed_result_without_leaking_error(
    shape: str,
    target: str,
    public_db: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> dict[str, object]:
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
def test_unopenable_store_returns_failed_result(shape: str, tmp_path: Path) -> None:
    started_at = time.time()
    result = SHAPES[shape](
        "C-STORE-ERROR",
        seed=11,
        store_path=str(tmp_path / "missing" / "store.sqlite"),
    )
    valid, reason = check_trace(result.as_dict(), started_at=started_at)

    assert result.status == "failed"
    assert result.error_reason == "internal_error"
    assert valid, reason


@pytest.mark.student
@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_amount_conflict_on_replay_returns_failed_and_preserves_ledger(
    shape: str,
    public_db: Path,
) -> None:
    first = SHAPES[shape]("C-001", seed=11, store_path=str(public_db))
    assert first.status == "resolved"

    conn = connect(public_db)
    try:
        conn.execute(
            "UPDATE refund_ledger SET amount_vnd = 10000 WHERE claim_id = 'C-001'"
        )
        conn.commit()
    finally:
        conn.close()

    started_at = time.time()
    second = SHAPES[shape]("C-001", seed=11, store_path=str(public_db))
    valid, reason = check_trace(second.as_dict(), started_at=started_at)

    conn = connect(public_db)
    try:
        ledger = get_refund(conn, "C-001")
    finally:
        conn.close()

    assert valid, reason
    assert second.status == "failed"
    assert second.error_reason == "amount_conflict"
    assert ledger is not None and int(ledger["amount_vnd"]) == 10000


@pytest.mark.student
@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_traces_never_leak_canary_secrets_or_pii(shape: str, public_db: Path) -> None:
    for claim_id in ("C-001", "C-005", "C-006", "C-009"):
        result = SHAPES[shape](claim_id, seed=11, store_path=str(public_db))
        blob = artifact_blob(result.as_dict())
        assert "CANARY_SECRET_" not in blob
        assert "CANARY_INTERNAL_" not in blob
        assert "parent_secret" not in blob
