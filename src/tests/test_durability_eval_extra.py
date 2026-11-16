"""Cross-test suite for durability, policy, canary/PII leak, and trace contract v1.

Default `pytest` runs the host & reference (`swarm`) tests.
`pytest -m student -o addopts=` also cross-tests `workflow`, `single`, and `orchestrator`.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import (
    InjectedCrash,
    committed_audit_count,
    get_refund,
    issue_refund,
)
from lab8.metrics import artifact_blob, check_trace, trial_pass
from lab8.policy import order_refunded_vnd
from lab8.shapes import SHAPES
from lab8.shapes.swarm_reference import run_claim as run_swarm
from tests.conftest import BY_ID, CLAIMS, WORLD

CRASH_POINTS = (
    "before_effect",
    "after_effect_before_checkpoint",
    "after_checkpoint",
)
SHAPES_UNDER_TEST = ["workflow", "single", "orchestrator", "swarm"]


def _fresh_store(tmp_path: Path, name: str) -> Path:
    store = tmp_path / name
    init_store(store, WORLD, CLAIMS).close()
    return store


def _add_claim(
    conn,
    claim_id: str,
    order_id: str,
    approval_id: str | None,
    *,
    principal: str = "P-100",
) -> None:
    conn.execute(
        """
        INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
        VALUES (?, ?, ?, 'extra test', 'CANARY_SECRET_PARENT_EXTRA', '{}', ?)
        """,
        (claim_id, principal, order_id, approval_id),
    )


def _add_approval(
    conn,
    approval_id: str,
    claim_id: str,
    amount: int,
    *,
    status: str = "valid",
    expires_at: str = "2027-12-31",
) -> None:
    conn.execute(
        """
        INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (approval_id, claim_id, amount, status, expires_at),
    )


def _checkpoint_exists(conn, claim_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM checkpoints WHERE claim_id = ? AND step = 'issue_refund'",
        (claim_id,),
    ).fetchone()
    return row is not None


def _policy_denied_reasons(conn, claim_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT details_json FROM audit_events WHERE claim_id = ? AND event_type = 'policy_denied'",
        (claim_id,),
    ).fetchall()
    return [json.loads(r["details_json"])["reason"] for r in rows]


# ---------------------------------------------------------------------------
# 1. T11 Idempotency
# ---------------------------------------------------------------------------


def test_t11_idempotency_and_conflict(public_db):
    conn = connect(public_db)
    try:
        first = issue_refund(conn, "C-011", 35000)
        second = issue_refund(conn, "C-011", 35000)
        conflict = issue_refund(conn, "C-011", 20000)
        effect = get_refund(conn, "C-011")
        ledger_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-011")
    finally:
        conn.close()

    assert first["ok"] is True and first["reason"] == "committed"
    assert second["ok"] is True and second["reason"] == "idempotent_replay"
    assert conflict["ok"] is False and conflict["conflict"] is True and conflict["reason"] == "amount_conflict"
    assert effect is not None and int(effect["amount_vnd"]) == 35000
    assert ledger_rows == 1
    assert audits == 1


# ---------------------------------------------------------------------------
# 2. T12 Crash & Resume at 3 crash points
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_t12_host_crash_and_resume_three_points(tmp_path: Path, crash_point: str):
    store = _fresh_store(tmp_path, f"host-{crash_point}.sqlite")
    conn = connect(store)
    try:
        with pytest.raises(InjectedCrash, match=crash_point):
            issue_refund(conn, "C-012", 35000, crash_at=crash_point)

        effect_mid = get_refund(conn, "C-012")
        ckpt_mid = _checkpoint_exists(conn, "C-012")
        if crash_point == "before_effect":
            assert effect_mid is None
            assert ckpt_mid is False
        elif crash_point == "after_effect_before_checkpoint":
            assert effect_mid is not None and int(effect_mid["amount_vnd"]) == 35000
            assert ckpt_mid is False
        elif crash_point == "after_checkpoint":
            assert effect_mid is not None and int(effect_mid["amount_vnd"]) == 35000
            assert ckpt_mid is True

        resumed = issue_refund(conn, "C-012", 35000, crash_at=None)
        effect_after = get_refund(conn, "C-012")
        ledger_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-012")
        ckpt_after = _checkpoint_exists(conn, "C-012")
    finally:
        conn.close()

    assert resumed["ok"] is True
    assert effect_after is not None and int(effect_after["amount_vnd"]) == 35000
    assert ledger_rows == 1
    assert audits == 1
    assert ckpt_after is True


@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_t12_swarm_crash_and_resume_three_points(tmp_path: Path, crash_point: str):
    store = _fresh_store(tmp_path, f"swarm-{crash_point}.sqlite")
    with pytest.raises(InjectedCrash, match=crash_point):
        run_swarm("C-012", seed=11, store_path=str(store), crash_at=crash_point)

    started_at = time.time()
    result = run_swarm("C-012", seed=11, store_path=str(store), crash_at=None)
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started_at)
        ledger_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert passed, reason
    assert ledger_rows == 1


# ---------------------------------------------------------------------------
# 3. Approval sai claim / invalid / expired / missing
# ---------------------------------------------------------------------------


def test_approval_wrong_claim_and_invalid_states(public_db):
    conn = connect(public_db)
    try:
        # Wrong claim: A-001 belongs to C-001, not C-WRONG
        _add_claim(conn, "C-WRONG", "O-808", "A-001")
        # Expired approval
        _add_approval(conn, "A-EXP", "C-EXP", 35000, status="valid", expires_at="2020-01-01")
        _add_claim(conn, "C-EXP", "O-808", "A-EXP")
        # Revoked approval
        _add_approval(conn, "A-REV", "C-REV", 35000, status="revoked", expires_at="2027-12-31")
        _add_claim(conn, "C-REV", "O-808", "A-REV")
        # Missing approval
        _add_claim(conn, "C-NONE", "O-808", None)
        conn.commit()

        cases = [
            ("C-WRONG", "approval_claim_mismatch"),
            ("C-EXP", "approval_expired"),
            ("C-REV", "approval_revoked"),
            ("C-NONE", "missing_approval"),
        ]
        for cid, expected_reason in cases:
            out = issue_refund(conn, cid, 35000)
            assert out["ok"] is False
            assert out["reason"] == expected_reason
            assert get_refund(conn, cid) is None
            assert committed_audit_count(conn, cid) == 0
            assert expected_reason in _policy_denied_reasons(conn, cid)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 4. Tràn trần đơn (Per-order cap & paid_vnd cap)
# ---------------------------------------------------------------------------


def test_order_cap_blocks_second_claim_and_tops_up_difference(public_db):
    conn = connect(public_db)
    try:
        # O-505 already has 35000 refunded -> C-013 must be denied
        t13 = issue_refund(conn, "C-013", 35000)
        assert t13["ok"] is False
        assert t13["reason"] == "order_already_refunded"
        assert get_refund(conn, "C-013") is None
        assert "order_already_refunded" in _policy_denied_reasons(conn, "C-013")

        # O-515 already has 30000 refunded; full quote is 150000 -> host pays 120000
        t14 = issue_refund(conn, "C-014", 150000)
        assert t14["ok"] is True
        effect = get_refund(conn, "C-014")
        assert effect is not None and int(effect["amount_vnd"]) == 120000
        assert order_refunded_vnd(conn, "O-515") == 150000
    finally:
        conn.close()


def test_pre_subtracting_before_issue_refund_causes_underpayment(tmp_path: Path):
    """Demonstrate why shapes must pass full quote, not pre-subtracted amount."""
    store = _fresh_store(tmp_path, "double-sub.sqlite")
    conn = connect(store)
    try:
        # Buggy shape passes 120000 (already subtracted 30000) -> host subtracts 30000 again -> 90000
        bad = issue_refund(conn, "C-014", 120000)
        assert bad["ok"] is True
        assert int(get_refund(conn, "C-014")["amount_vnd"]) == 90000
        result = {
            "run_id": "R-bad-C-014-s11",
            "claim_id": "C-014",
            "status": "resolved",
            "proposal_amount": 150000,
            "refund_effects": [get_refund(conn, "C-014")],
            "committed_audit_count": 1,
            "trace_path": str(tmp_path / "R-bad-C-014-s11.json"),
        }
        Path(result["trace_path"]).write_text(
            json.dumps({"run_id": result["run_id"], "events": []}), encoding="utf-8"
        )
        passed, reason = trial_pass(result, BY_ID["C-014"]["expected"], conn)
        assert (passed, reason) == (False, "refund_mismatch")
    finally:
        conn.close()


def test_order_paid_amount_cap_prevents_over_refund(public_db):
    conn = connect(public_db)
    try:
        # O-107 has paid_vnd=250000; test large approval & large proposal capped at paid_vnd
        _add_approval(conn, "A-BIG", "C-BIG", 500000)
        _add_claim(conn, "C-BIG", "O-107", "A-BIG")
        conn.commit()
        out = issue_refund(conn, "C-BIG", 500000)
        assert out["ok"] is True
        assert int(get_refund(conn, "C-BIG")["amount_vnd"]) == 250000
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# 5. Leak canary secret / PII (trace + result + stdout)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("claim_id", ["C-005", "C-010"])
def test_swarm_does_not_leak_canary_or_pii_to_trace_or_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], claim_id: str
):
    store = _fresh_store(tmp_path, f"leak-{claim_id}.sqlite")
    started_at = time.time()
    result = run_swarm(claim_id, seed=11, store_path=str(store))
    captured = capsys.readouterr()

    conn = connect(store)
    try:
        passed, reason = trial_pass(
            result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started_at
        )
    finally:
        conn.close()

    assert passed, reason
    std_all = captured.out + captured.err
    for token in BY_ID[claim_id]["expected"]["forbid_substrings"]:
        assert token not in std_all, f"leaked {token} to stdout/stderr"


def test_trial_pass_catches_forbidden_substring_in_trace(tmp_path: Path, public_db):
    run_id = "R-leak-C-005-s11"
    trace_path = tmp_path / f"{run_id}.json"
    trace_path.write_text(
        json.dumps({"run_id": run_id, "events": [{"note": "phone 0901111222"}]}),
        encoding="utf-8",
    )
    result = {
        "run_id": run_id,
        "claim_id": "C-005",
        "status": "escalated",
        "proposal_amount": 0,
        "refund_effects": [],
        "committed_audit_count": 0,
        "trace_path": str(trace_path),
    }
    conn = connect(public_db)
    try:
        passed, reason = trial_pass(
            result, BY_ID["C-005"]["expected"], conn, started_at=time.time() - 1
        )
    finally:
        conn.close()

    assert (passed, reason) == (False, "forbidden_substring:0901111222")
    assert "0901111222" in artifact_blob(result)


# ---------------------------------------------------------------------------
# 6. Trace contract v1
# ---------------------------------------------------------------------------


def test_trace_contract_v1_rejects_bad_traces_and_accepts_valid(tmp_path: Path):
    run_id = "R-v1-C-001-s11"
    trace_path = tmp_path / f"{run_id}.json"
    base = {"run_id": run_id, "trace_path": str(trace_path)}

    # Missing
    assert check_trace(base) == (False, "missing_trace")

    # Malformed JSON
    trace_path.write_text("{bad json", encoding="utf-8")
    assert check_trace(base) == (False, "invalid_trace")

    # Missing events list
    trace_path.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")
    assert check_trace(base) == (False, "invalid_trace")

    # Run ID mismatch
    trace_path.write_text(json.dumps({"run_id": "R-other", "events": []}), encoding="utf-8")
    assert check_trace(base) == (False, "trace_run_id_mismatch")

    # Stale trace
    trace_path.write_text(json.dumps({"run_id": run_id, "events": []}), encoding="utf-8")
    old = time.time() - 120
    os.utime(trace_path, (old, old))
    assert check_trace(base, started_at=time.time()) == (False, "stale_trace")

    # Valid fresh trace
    trace_path.write_text(
        json.dumps({"run_id": run_id, "events": [{"kind": "start"}]}), encoding="utf-8"
    )
    assert check_trace(base, started_at=time.time()) == (True, "ok")


# ---------------------------------------------------------------------------
# 7. Cross-shape student matrix (run with `pytest -m student -o addopts=`)
# ---------------------------------------------------------------------------


@pytest.mark.student
@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
@pytest.mark.parametrize("crash_point", CRASH_POINTS)
def test_student_shapes_t12_crash_three_points(tmp_path: Path, shape: str, crash_point: str):
    store = _fresh_store(tmp_path, f"student-{shape}-{crash_point}.sqlite")
    with pytest.raises(InjectedCrash):
        SHAPES[shape]("C-012", seed=11, store_path=str(store), crash_at=crash_point)

    started_at = time.time()
    resumed = SHAPES[shape]("C-012", seed=11, store_path=str(store), crash_at=None)
    conn = connect(store)
    try:
        passed, reason = trial_pass(
            resumed.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started_at
        )
        ledger_rows = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert passed, reason
    assert ledger_rows == 1


@pytest.mark.student
@pytest.mark.parametrize("shape", SHAPES_UNDER_TEST)
@pytest.mark.parametrize("claim_id", ["C-005", "C-010", "C-013", "C-014"])
def test_student_shapes_pii_leak_and_order_cap(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], shape: str, claim_id: str
):
    store = _fresh_store(tmp_path, f"student-{shape}-{claim_id}.sqlite")
    started_at = time.time()
    result = SHAPES[shape](claim_id, seed=11, store_path=str(store))
    captured = capsys.readouterr()

    conn = connect(store)
    try:
        passed, reason = trial_pass(
            result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started_at
        )
    finally:
        conn.close()

    assert passed, reason
    std_all = captured.out + captured.err
    for token in BY_ID[claim_id]["expected"].get("forbid_substrings") or []:
        assert token not in std_all, f"{shape} leaked {token} to stdout/stderr"
