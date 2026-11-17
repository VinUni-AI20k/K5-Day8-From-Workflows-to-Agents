"""Team tests (Nguyễn Ngọc Ninh - 2A202603774): policy gate, per-order cap, and boundary checks for the 3 student shapes.

Runs in the default host gate (`python -m pytest -q`).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import committed_audit_count, get_refund
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

TEAM_SHAPES = ["workflow", "single", "orchestrator"]
PRIOR_REFUND_COUNT = len(WORLD.get("prior_refunds") or [])


def _store(tmp_path: Path, name: str) -> str:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return str(path)


def _policy_denied_count(conn, claim_id: str) -> int:
    row = conn.execute(
        """
        SELECT COUNT(*) AS n FROM audit_events
        WHERE claim_id = ? AND event_type = 'policy_denied'
        """,
        (claim_id,),
    ).fetchone()
    return int(row["n"])


def _ledger_row_count(conn) -> int:
    row = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger").fetchone()
    return int(row["n"])


@pytest.mark.parametrize("shape", TEAM_SHAPES)
def test_missing_order_id_returns_needs_info_without_ledger_write(tmp_path: Path, shape: str) -> None:
    """C-004 (missing order_id) -> status needs_info, proposal_amount 0, no ledger write."""
    store = _store(tmp_path, f"{shape}-c004.sqlite")
    result = SHAPES[shape]("C-004", seed=11, store_path=store)

    conn = connect(store)
    try:
        effect = get_refund(conn, "C-004")
        total_rows = _ledger_row_count(conn)
        committed = committed_audit_count(conn, "C-004")
    finally:
        conn.close()

    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert effect is None
    assert total_rows == PRIOR_REFUND_COUNT
    assert committed == 0


@pytest.mark.parametrize("shape", TEAM_SHAPES)
def test_order_already_fully_refunded_is_denied_with_policy_audit(tmp_path: Path, shape: str) -> None:
    """C-013 (O-505 already refunded 35,000) -> denied, full quote 35,000, policy_denied audit, no new ledger row."""
    store = _store(tmp_path, f"{shape}-c013.sqlite")
    result = SHAPES[shape]("C-013", seed=11, store_path=store)

    conn = connect(store)
    try:
        effect = get_refund(conn, "C-013")
        total_rows = _ledger_row_count(conn)
        committed = committed_audit_count(conn, "C-013")
        denied_audits = _policy_denied_count(conn, "C-013")
    finally:
        conn.close()

    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert effect is None
    assert total_rows == PRIOR_REFUND_COUNT
    assert committed == 0
    assert denied_audits >= 1


@pytest.mark.parametrize("shape", TEAM_SHAPES)
def test_partial_prior_refund_pays_only_remaining_entitlement(tmp_path: Path, shape: str) -> None:
    """C-014 (O-515 prior 30,000 ship refund, now 150,000 damage) -> resolved, proposal 150,000, ledger 120,000."""
    store = _store(tmp_path, f"{shape}-c014.sqlite")
    result = SHAPES[shape]("C-014", seed=11, store_path=store)

    conn = connect(store)
    try:
        effect = get_refund(conn, "C-014")
        total_rows = _ledger_row_count(conn)
        committed = committed_audit_count(conn, "C-014")
        denied_audits = _policy_denied_count(conn, "C-014")
    finally:
        conn.close()

    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert effect is not None
    assert int(effect["amount_vnd"]) == 120000
    assert total_rows == PRIOR_REFUND_COUNT + 1
    assert committed == 1
    assert denied_audits == 0


@pytest.mark.parametrize("shape", TEAM_SHAPES)
def test_expired_approval_and_approval_cap_enforced_by_host(tmp_path: Path, shape: str) -> None:
    """C-007 (expired approval) -> denied + policy_denied; C-008 (partial approval 20k on 35k quote) -> ledger 20k."""
    store_c007 = _store(tmp_path, f"{shape}-c007.sqlite")
    res_c007 = SHAPES[shape]("C-007", seed=11, store_path=store_c007)
    conn = connect(store_c007)
    try:
        assert res_c007.status == "denied"
        assert res_c007.proposal_amount == 35000
        assert get_refund(conn, "C-007") is None
        assert _policy_denied_count(conn, "C-007") >= 1
    finally:
        conn.close()

    store_c008 = _store(tmp_path, f"{shape}-c008.sqlite")
    res_c008 = SHAPES[shape]("C-008", seed=11, store_path=store_c008)
    conn = connect(store_c008)
    try:
        effect_c008 = get_refund(conn, "C-008")
        assert res_c008.status == "resolved"
        assert res_c008.proposal_amount == 35000
        assert effect_c008 is not None and int(effect_c008["amount_vnd"]) == 20000
        assert committed_audit_count(conn, "C-008") == 1
    finally:
        conn.close()
