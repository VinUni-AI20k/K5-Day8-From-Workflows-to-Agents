"""Unit tests for Shape B (single ReAct agent)."""

from __future__ import annotations

import time

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import artifact_blob, check_trace, trial_pass
from lab8.shapes.single import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def test_single_ignores_ticket_delay_trap_across_seeds(tmp_path):
    """Unlike the reference swarm on seed 55, single must trust order.delay_days on C-002."""
    for seed in (11, 55):
        store = tmp_path / f"single-c002-{seed}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        started = time.time()
        result = run_claim("C-002", seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(
                result.as_dict(), BY_ID["C-002"]["expected"], conn, started_at=started
            )
        finally:
            conn.close()
        assert passed, f"seed {seed} failed: {reason}"
        assert result.status == "denied"
        assert result.proposal_amount == 0


def test_single_unknown_claim_fails_cleanly_with_valid_trace(public_db):
    started = time.time()
    result = run_claim("C-UNKNOWN-999", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert result.error_reason == "unknown_claim"
    assert check_trace(result.as_dict(), started_at=started) == (True, "ok")
    assert "CANARY_SECRET_" not in artifact_blob(result.as_dict())


def test_single_crash_and_resume_keeps_single_refund(tmp_path):
    store = tmp_path / "single-crash.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    crashed = False
    try:
        run_claim(
            "C-012",
            seed=11,
            store_path=str(store),
            crash_at="after_effect_before_checkpoint",
        )
    except InjectedCrash:
        crashed = True
    assert crashed

    started = time.time()
    resumed = run_claim("C-012", seed=11, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(
            resumed.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started
        )
    finally:
        conn.close()
    assert passed, reason
    assert resumed.status == "resolved"
    assert resumed.committed_audit_count == 1
