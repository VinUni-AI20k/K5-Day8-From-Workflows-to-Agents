"""Tests for CP3: Idempotency, crash resilience, and handoff safety across student shapes."""

from __future__ import annotations

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.handoff import HandoffError, make_handoff
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

STUDENT_SHAPES = ["workflow", "single", "orchestrator"]


def _init_test_store(tmp_path, name: str):
    store = tmp_path / name
    init_store(store, WORLD, CLAIMS).close()
    return store


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_cp3_idempotent_replay_preserves_single_ledger_row(tmp_path, shape):
    """Calling run_claim multiple times on the same claim must produce exactly 1 ledger row."""
    store = _init_test_store(tmp_path, f"{shape}_idempotent.sqlite")
    first = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    assert first.status == "resolved"
    assert first.proposal_amount == 35000

    second = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    assert second.status == "resolved"
    assert second.proposal_amount == 35000

    conn = connect(store)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-001")
        effect = get_refund(conn, "C-001")
    finally:
        conn.close()

    assert count == 1, "Ledger must never contain more than one row per claim"
    assert audits == 1, "Only one refund_committed audit event should exist"
    assert effect is not None and int(effect["amount_vnd"]) == 35000


@pytest.mark.parametrize("shape", STUDENT_SHAPES)
def test_cp3_crash_recovery_does_not_duplicate_refund(tmp_path, shape):
    """Shapes must propagate InjectedCrash and resume safely without double-paying."""
    store = _init_test_store(tmp_path, f"{shape}_crash.sqlite")
    crashed = False
    try:
        SHAPES[shape](
            "C-001",
            seed=11,
            store_path=str(store),
            crash_at="after_effect_before_checkpoint",
        )
    except InjectedCrash:
        crashed = True

    assert crashed, "Shape must forward crash_at to issue_refund and let InjectedCrash propagate"

    # Resume after crash
    resumed = SHAPES[shape]("C-001", seed=11, store_path=str(store))
    assert resumed.status == "resolved"
    assert resumed.proposal_amount == 35000

    conn = connect(store)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-001")
    finally:
        conn.close()

    assert count == 1, "Post-crash resume must not create duplicate ledger rows"
    assert audits == 1, "Post-crash resume must not duplicate audit events"


def test_cp3_handoff_rejects_write_tools_and_drops_unallowed_facts():
    """Handoff must reject any write tool and sanitize disallowed fact fields."""
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-TEST",
            claim_id="C-001",
            task="investigate",
            facts={},
            allowed_tools=["lookup_order", "issue_refund"],
        )

    handoff = make_handoff(
        request_id="REQ-TEST-CLEAN",
        claim_id="C-001",
        task="investigate",
        facts={
            "delay_days": 4,
            "carrier": "LOGIX_LOCAL",
            "forbidden_note": "Confidential internal note",
            "parent_secret": "CANARY_SECRET_LEAK",
        },
        allowed_tools=["lookup_order", "compute_compensation"],
    )
    assert "forbidden_note" not in handoff["facts"]
    assert "parent_secret" not in handoff["facts"]
    assert "CANARY_SECRET_" not in str(handoff)
