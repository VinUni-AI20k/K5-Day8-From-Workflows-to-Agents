"""Ledger, crash and approval checks run through the shapes, not just the host.

Owner: ledger + evaluation. The public matrix already covers one retry (T11) and one
crash point (T12). This file covers what it does not:

- every crash point (before_effect, after_effect_before_checkpoint, after_checkpoint),
  then resume: one ledger row, one refund_committed audit, one checkpoint;
- several retries of a paying claim and of a claim the host denies;
- approvals that are missing, revoked, or issued for another claim: the shape must
  still call durability.issue_refund so the host writes policy_denied;
- two claims on the same order in one store: the order is paid once;
- all 14 public claims in one shared store: ledger invariants and no leaked secret/PII.

Not marked `student`: these tests run in the host gate (`python -m pytest -q`) and must
stay green. Run only this file:

    python -m pytest -q tests/test_ledger_shapes.py
    python -m pytest -q tests/test_ledger_shapes.py -k workflow

Swarm is included as the reference: its rows must pass, which shows the tests themselves
are correct. All runs use seed 11 (the swarm weakness only fires on seed % 5 == 0).
"""

from __future__ import annotations

import json
import time

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, idempotency_key
from lab8.metrics import artifact_blob, check_trace, trial_pass, unexpected_ledger_rows
from lab8.shapes import SHAPES
from tests.conftest import BY_ID, CLAIMS, WORLD

SHAPES_UNDER_TEST = ["workflow", "single", "orchestrator", "swarm"]
SEED = 11
CRASH_POINTS = ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]


# ---------------------------------------------------------------- helpers


def _store(tmp_path, name: str):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def _ledger_rows(conn, claim_id: str) -> list[dict]:
    rows = conn.execute("SELECT * FROM refund_ledger WHERE claim_id = ?", (claim_id,)).fetchall()
    return [dict(row) for row in rows]


def _audit_count(conn, claim_id: str, event_type: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = ? AND event_type = ?",
        (claim_id, event_type),
    ).fetchone()
    return int(row["n"])


def _denial_reasons(conn, claim_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
        (claim_id,),
    ).fetchall()
    return [json.loads(row["details_json"]).get("reason", "") for row in rows]


def _has_checkpoint(conn, claim_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'",
        (claim_id,),
    ).fetchone()
    return row is not None


def _add_late_claim(store, claim_id: str, approval_id: str | None) -> None:
    """A claim on O-107 (P-100, 4 days late, fee 35000): quote is 35000 > 0."""
    conn = connect(store)
    try:
        conn.execute(
            """
            INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
            VALUES (?, 'P-100', 'O-107', ?, ?, ?, ?)
            """,
            (
                claim_id,
                "Đơn O-107 giao trễ, xin hoàn phí ship.",
                f"CANARY_SECRET_PARENT_{claim_id}",
                json.dumps({"Authorization": f"Bearer CANARY_SECRET_PARENT_{claim_id}"}),
                approval_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def _add_approval(store, approval_id: str, claim_id: str, amount: int, status: str = "valid") -> None:
    conn = connect(store)
    try:
        conn.execute(
            "INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at) VALUES (?, ?, ?, ?, '2027-12-31')",
            (approval_id, claim_id, amount, status),
        )
        conn.commit()
    finally:
        conn.close()


def _assert_no_leak(result, claim_id: str) -> None:
    blob = artifact_blob(result.as_dict())
    assert f"CANARY_SECRET_PARENT_{claim_id}" not in blob, f"{claim_id}: parent secret leaked"


# ---------------------------------------------------------------- crash at every point


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
@pytest.mark.parametrize("crash_at", CRASH_POINTS)
def test_crash_at_every_point_then_resume_pays_once(tmp_path, shape, crash_at):
    store = _store(tmp_path, f"{shape}-{crash_at}.sqlite")

    with pytest.raises(InjectedCrash):
        SHAPES[shape]("C-012", seed=SEED, store_path=str(store), crash_at=crash_at)

    conn = connect(store)
    try:
        rows_after_crash = _ledger_rows(conn, "C-012")
        checkpoint_after_crash = _has_checkpoint(conn, "C-012")
    finally:
        conn.close()
    if crash_at == "before_effect":
        assert rows_after_crash == [], "nothing may be written before the effect point"
    else:
        assert len(rows_after_crash) == 1, "the effect is committed before this crash point"
    assert checkpoint_after_crash == (crash_at == "after_checkpoint")

    started_at = time.time()
    result = SHAPES[shape]("C-012", seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started_at)
        rows = _ledger_rows(conn, "C-012")
        committed = _audit_count(conn, "C-012", "refund_committed")
        checkpoint = _has_checkpoint(conn, "C-012")
    finally:
        conn.close()
    assert passed, reason
    assert len(rows) == 1 and int(rows[0]["amount_vnd"]) == 35000
    assert rows[0]["idempotency_key"] == idempotency_key("C-012")
    assert committed == 1
    assert checkpoint, "resume must leave the issue_refund checkpoint"
    _assert_no_leak(result, "C-012")


# ---------------------------------------------------------------- retries


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_three_retries_of_a_paying_claim_keep_one_row(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-retry3.sqlite")
    results = []
    for _ in range(3):
        started_at = time.time()
        results.append(SHAPES[shape]("C-001", seed=SEED, store_path=str(store)))
        ok, reason = check_trace(results[-1].as_dict(), started_at=started_at)
        assert ok, f"every retry writes its own fresh trace: {reason}"

    conn = connect(store)
    try:
        rows = _ledger_rows(conn, "C-001")
        committed = _audit_count(conn, "C-001", "refund_committed")
        extra = unexpected_ledger_rows(conn, "C-001")
    finally:
        conn.close()
    assert [r.status for r in results] == ["resolved"] * 3
    assert [r.proposal_amount for r in results] == [35000] * 3
    assert len(rows) == 1 and int(rows[0]["amount_vnd"]) == 35000
    assert committed == 1
    assert extra == 0


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_retry_of_an_already_refunded_order_stays_denied(tmp_path, shape):
    """T13 twice: the order was paid by an earlier claim, so no row ever appears."""
    store = _store(tmp_path, f"{shape}-t13-retry.sqlite")
    first = SHAPES[shape]("C-013", seed=SEED, store_path=str(store))
    second = SHAPES[shape]("C-013", seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        rows = _ledger_rows(conn, "C-013")
        reasons = _denial_reasons(conn, "C-013")
    finally:
        conn.close()
    for result in (first, second):
        assert result.status == "denied"
        assert result.proposal_amount == 35000, "proposal_amount is the full quote"
    assert rows == []
    assert "order_already_refunded" in reasons


# ---------------------------------------------------------------- approval gate


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_approval_borrowed_from_another_claim_is_denied(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-borrowed.sqlite")
    _add_late_claim(store, "C-L01", approval_id="A-001")  # A-001 belongs to C-001
    result = SHAPES[shape]("C-L01", seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        rows = _ledger_rows(conn, "C-L01")
        reasons = _denial_reasons(conn, "C-L01")
        total = int(conn.execute("SELECT COUNT(*) AS n FROM refund_ledger").fetchone()["n"])
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert rows == []
    assert "approval_claim_mismatch" in reasons, "shape must call issue_refund so the host audits the denial"
    assert total == 2, "only the two seeded prior refunds may exist"
    _assert_no_leak(result, "C-L01")


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_missing_approval_is_denied_with_audit(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-noapproval.sqlite")
    _add_late_claim(store, "C-L02", approval_id=None)
    result = SHAPES[shape]("C-L02", seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        rows = _ledger_rows(conn, "C-L02")
        reasons = _denial_reasons(conn, "C-L02")
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert rows == []
    assert "missing_approval" in reasons


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_revoked_approval_is_denied_with_audit(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-revoked.sqlite")
    _add_approval(store, "A-L03", "C-L03", 35000, status="revoked")
    _add_late_claim(store, "C-L03", approval_id="A-L03")
    result = SHAPES[shape]("C-L03", seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        rows = _ledger_rows(conn, "C-L03")
        reasons = _denial_reasons(conn, "C-L03")
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert rows == []
    assert "approval_revoked" in reasons


# ---------------------------------------------------------------- per-order cap


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_two_claims_on_one_order_pay_once(tmp_path, shape):
    """C-001 and C-010 are both on O-107. In one store only the first one pays."""
    store = _store(tmp_path, f"{shape}-sameorder.sqlite")
    first = SHAPES[shape]("C-001", seed=SEED, store_path=str(store))
    second = SHAPES[shape]("C-010", seed=SEED, store_path=str(store))
    conn = connect(store)
    try:
        o107 = int(
            conn.execute("SELECT COALESCE(SUM(amount_vnd), 0) AS t FROM refund_ledger WHERE order_id = 'O-107'")
            .fetchone()["t"]
        )
        second_rows = _ledger_rows(conn, "C-010")
        reasons = _denial_reasons(conn, "C-010")
    finally:
        conn.close()
    assert first.status == "resolved"
    assert second.status == "denied"
    assert second.proposal_amount == 35000, "pass the full quote; the host subtracts, not the shape"
    assert second_rows == []
    assert "order_already_refunded" in reasons
    assert o107 == 35000


# ---------------------------------------------------------------- whole corpus, one store


@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
def test_public_corpus_in_one_store_keeps_ledger_invariants(tmp_path, shape):
    store = _store(tmp_path, f"{shape}-corpus.sqlite")
    results = {}
    for claim in CLAIMS:
        claim_id = claim["claim_id"]
        started_at = time.time()
        result = SHAPES[shape](claim_id, seed=SEED, store_path=str(store))
        ok, reason = check_trace(result.as_dict(), started_at=started_at)
        assert ok, f"{claim_id}: {reason}"
        assert result.claim_id == claim_id
        results[claim_id] = result

    conn = connect(store)
    try:
        ledger = [dict(row) for row in conn.execute("SELECT * FROM refund_ledger").fetchall()]
        audits = {
            claim_id: _audit_count(conn, claim_id, "refund_committed") for claim_id in [row["claim_id"] for row in ledger]
        }
        orders = {
            row["order_id"]: int(row["paid_vnd"])
            for row in conn.execute("SELECT order_id, paid_vnd FROM orders").fetchall()
        }
    finally:
        conn.close()

    by_claim: dict[str, list[dict]] = {}
    per_order: dict[str, int] = {}
    for row in ledger:
        by_claim.setdefault(row["claim_id"], []).append(row)
        per_order[row["order_id"]] = per_order.get(row["order_id"], 0) + int(row["amount_vnd"])
        assert row["idempotency_key"] == idempotency_key(row["claim_id"])
        assert audits[row["claim_id"]] == 1, f"{row['claim_id']}: one refund_committed per ledger row"

    assert all(len(rows) == 1 for rows in by_claim.values()), "at most one row per claim"
    for order_id, total in per_order.items():
        assert total <= orders[order_id], f"{order_id}: refunded {total} > paid {orders[order_id]}"
    assert per_order.get("O-107") == 35000, "four claims on O-107, but the shipping fee is paid once"
    assert per_order.get("O-515") == 150000, "prior 30000 + T14 top-up 120000"

    for claim_id, result in results.items():
        own = by_claim.get(claim_id, [])
        if result.status == "resolved":
            assert len(own) == 1, f"{claim_id}: resolved without a ledger row"
        else:
            assert own == [], f"{claim_id}: {result.status} but a refund was written"
        forbidden = BY_ID[claim_id]["expected"].get("forbid_substrings", [])
        blob = artifact_blob(result.as_dict())
        leaked = [needle for needle in forbidden if needle in blob]
        assert not leaked, f"{claim_id}: leaked {leaked}"
