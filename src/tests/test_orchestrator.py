"""Tests for Shape C: Orchestrator + Handoff (Student role C)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, get_refund
from lab8.metrics import trial_pass
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


@pytest.mark.parametrize(
    "claim_id",
    ["C-001", "C-002", "C-003", "C-004", "C-005", "C-006", "C-007", "C-008", "C-009", "C-010", "C-013", "C-014"],
)
def test_orchestrator_passes_public_claims(public_db, claim_id):
    """Orchestrator must correctly resolve or deny all standard public claims."""
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn)
    finally:
        conn.close()
    assert passed, reason


def test_orchestrator_robust_on_t02_seed55(tmp_path):
    """Unlike swarm reference which fails seed 55 due to peer ticket hallucination,
    orchestrator relies strictly on investigator order data and correctly denies C-002 on all seeds.
    """
    for seed in (11, 55):
        store = tmp_path / f"t02-orch-{seed}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        result = run_claim("C-002", seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), BY_ID["C-002"]["expected"], conn)
        finally:
            conn.close()
        assert passed, f"Orchestrator should pass C-002 on seed {seed}: {reason}"
        assert result.status == "denied"
        assert result.proposal_amount == 0


def test_orchestrator_trace_and_handoff_security(public_db):
    """Trace and handoff must not leak parent secrets, raw headers, or canary tokens."""
    result = run_claim("C-010", seed=11, store_path=str(public_db))
    assert Path(result.trace_path).exists()
    trace_data = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    
    blob = json.dumps(trace_data, ensure_ascii=False)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob
    assert "raw_headers" not in blob

    # Verify handoff event is logged and sanitized
    handoff_events = [e for e in trace_data.get("events", []) if e.get("kind") == "handoff"]
    assert len(handoff_events) == 1
    handoff = handoff_events[0]["payload"]
    assert handoff["principal_scope"] == "owner_order_only"
    assert "issue_refund" not in handoff["allowed_tools"]


def test_orchestrator_handles_missing_order_id(tmp_path):
    """Missing order_id (C-004) must transition to needs_info without ledger modification."""
    store = tmp_path / "needs_info.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim("C-004", seed=11, store_path=str(store))
    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert result.error_reason == "missing_order_id"


def test_orchestrator_handles_outside_principal_scope(tmp_path):
    """Order not owned by principal (C-005) must escalate without leaking sensitive fields."""
    store = tmp_path / "escalated.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim("C-005", seed=11, store_path=str(store))
    assert result.status == "escalated"
    assert result.proposal_amount == 0
    assert result.error_reason == "outside_principal_scope"


def test_orchestrator_handles_unknown_claim(tmp_path):
    """Unknown claim id returns failed with error_reason unknown_claim."""
    store = tmp_path / "unknown.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim("C-NONEXISTENT", seed=11, store_path=str(store))
    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"


def test_orchestrator_crash_propagation_and_idempotent_recovery(tmp_path):
    """Verifies that InjectedCrash propagates unhandled, and subsequent run recovers idempotently."""
    store = tmp_path / "crash_recovery.sqlite"
    init_store(store, WORLD, CLAIMS).close()

    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")

    # Resume without crash
    resumed = run_claim("C-001", seed=11, store_path=str(store), crash_at=None)
    assert resumed.status == "resolved"
    assert resumed.proposal_amount == 35000

    conn = connect(store)
    try:
        refund = get_refund(conn, "C-001")
        assert refund is not None
        assert refund["amount_vnd"] == 35000
    finally:
        conn.close()
