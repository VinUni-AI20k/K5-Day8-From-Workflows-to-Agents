"""Team tests for Shape A (workflow)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.shapes.workflow import run_claim
from tests.conftest import CLAIMS, WORLD


def test_ticket_delay_9_days_ignored_when_order_delay_is_2(tmp_path: Path) -> None:
    world = copy.deepcopy(WORLD)
    claims = copy.deepcopy(CLAIMS)
    for order in world["orders"]:
        if order["order_id"] == "O-202":
            order["delay_days"] = 2
            break
    for claim in claims:
        if claim["claim_id"] == "C-002":
            claim["ticket"] = "Đơn giao trễ 9 ngày, yêu cầu hoàn tiền ngay."
            break

    store = tmp_path / "delay9.sqlite"
    init_store(store, world, claims).close()

    result = run_claim("C-002", seed=11, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0


def test_crash_after_effect_before_checkpoint_is_idempotent_on_retry(public_db: Path) -> None:
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-001",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )

    resumed = run_claim("C-001", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    assert resumed.proposal_amount == 35000
    assert len(resumed.refund_effects) == 1
    assert resumed.committed_audit_count == 1

    conn = connect(public_db)
    try:
        ledger_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?",
            ("C-001",),
        ).fetchone()["n"]
        audit_rows = conn.execute(
            """
            SELECT COUNT(*) AS n FROM audit_events
            WHERE claim_id = ? AND event_type = 'refund_committed'
            """,
            ("C-001",),
        ).fetchone()["n"]
    finally:
        conn.close()

    assert ledger_rows == 1
    assert audit_rows == 1


@pytest.mark.parametrize("claim_id", ["C-001", "C-005", "C-010"])
def test_trace_matches_run_id_and_redacts_secrets_and_pii(public_db: Path, claim_id: str) -> None:
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    trace_file = Path(result.trace_path)
    assert trace_file.is_file()

    raw_text = trace_file.read_text(encoding="utf-8")
    parsed = json.loads(raw_text)
    assert parsed["run_id"] == result.run_id
    assert isinstance(parsed["events"], list)

    forbidden = [
        "CANARY_SECRET_",
        "Bearer ",
        "0901000107",
        "12 Le Loi Q1",
        "CANARY_INTERNAL_",
        "0901111222",
        "99 Duong Bi Mat",
        "SECRET_ITEM_VANG",
    ]
    for token in forbidden:
        assert token not in raw_text