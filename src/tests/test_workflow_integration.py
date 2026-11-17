"""Focused integration coverage for the deterministic workflow shape."""

from __future__ import annotations

import time

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import trial_pass
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def _store(tmp_path, name: str):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_workflow_integrates_public_claims_with_host(tmp_path):
    """Exercise successful, denied, needs-info, and escalated host paths."""
    for claim_id, expected_case in BY_ID.items():
        store = _store(tmp_path, f"{claim_id}.sqlite")
        started_at = time.time()
        result = run_claim(claim_id, seed=11, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(
                result.as_dict(), expected_case["expected"], conn, started_at=started_at
            )
        finally:
            conn.close()
        assert passed, f"{claim_id}: {reason}"


def test_workflow_retry_keeps_one_refund(tmp_path):
    store = _store(tmp_path, "retry.sqlite")
    first = run_claim("C-011", seed=11, store_path=str(store))
    started_at = time.time()
    second = run_claim("C-011", seed=11, store_path=str(store))

    conn = connect(store)
    try:
        passed, reason = trial_pass(
            second.as_dict(), BY_ID["C-011"]["expected"], conn, started_at=started_at
        )
        refunds = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert first.status == "resolved"
    assert passed, reason
    assert refunds == 1


def test_workflow_crash_resume_keeps_one_refund(tmp_path):
    store = _store(tmp_path, "crash-resume.sqlite")
    try:
        run_claim(
            "C-012",
            seed=11,
            store_path=str(store),
            crash_at="after_effect_before_checkpoint",
        )
    except InjectedCrash:
        pass
    else:
        raise AssertionError("workflow did not forward crash_at to issue_refund")

    started_at = time.time()
    result = run_claim("C-012", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(
            result.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started_at
        )
        refunds = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert passed, reason
    assert refunds == 1
