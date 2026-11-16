"""Dedicated test suite for Role 3: Shape C - Orchestrator.

Matches pytest filter: -k orchestrator
Includes unit and integration tests covering:
- Bounded read-only tools in handoff
- No leak of parent secrets or PII in traces
- Proper proposal quoting and delegation to durability.issue_refund
- Error branches (missing order_id, out of scope, zero compensation, approval failure)
- Idempotency and crash safety (T11, T12)
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def _make_store(tmp_path: Path, name: str) -> Path:
    store_file = tmp_path / name
    init_store(store_file, WORLD, CLAIMS).close()
    return store_file


@pytest.mark.student
def test_orchestrator_resolved_c001(tmp_path: Path):
    """Test standard valid claim (C-001) resolves with full compensation."""
    store = _make_store(tmp_path, "orch_c001.sqlite")
    result = run_claim("C-001", seed=11, store_path=str(store))

    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert result.shape == "orchestrator"
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 35000
    assert result.committed_audit_count == 1
    assert result.error_reason is None

    # Check trace content
    trace_path = Path(result.trace_path)
    assert trace_path.exists()
    trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace_data["run_id"] == result.run_id
    assert "CANARY_SECRET_" not in json.dumps(trace_data)


@pytest.mark.student
def test_orchestrator_needs_info_missing_order_id(tmp_path: Path):
    """Test missing order_id returns needs_info without ledger writes."""
    store = _make_store(tmp_path, "orch_c004.sqlite")
    result = run_claim("C-004", seed=11, store_path=str(store))

    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    assert result.error_reason == "missing_order_id"


@pytest.mark.student
def test_orchestrator_escalated_scope_or_not_found(tmp_path: Path):
    """Test cross-principal order access escalates cleanly without leaking PII."""
    store = _make_store(tmp_path, "orch_c005.sqlite")
    result = run_claim("C-005", seed=11, store_path=str(store))

    assert result.status == "escalated"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0

    trace_text = Path(result.trace_path).read_text(encoding="utf-8")
    forbid = ["0901111222", "99 Duong Bi Mat", "SECRET_ITEM_VANG", "CANARY_INTERNAL_O110"]
    for secret in forbid:
        assert secret not in trace_text


@pytest.mark.student
def test_orchestrator_denied_zero_quote(tmp_path: Path):
    """Test zero compensation (e.g., delay < 3 days) returns denied directly."""
    store = _make_store(tmp_path, "orch_c002.sqlite")
    result = run_claim("C-002", seed=11, store_path=str(store))

    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0


@pytest.mark.student
def test_orchestrator_denied_policy_expired_approval(tmp_path: Path):
    """Test quote > 0 but approval fails; host writes policy_denied audit."""
    store = _make_store(tmp_path, "orch_c007.sqlite")
    result = run_claim("C-007", seed=11, store_path=str(store))

    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []

    conn = connect(store)
    try:
        denied_audit = conn.execute(
            "SELECT COUNT(*) AS c FROM audit_events WHERE claim_id = 'C-007' AND event_type = 'policy_denied'"
        ).fetchone()["c"]
    finally:
        conn.close()
    assert denied_audit == 1


@pytest.mark.student
def test_orchestrator_order_already_refunded_t13(tmp_path: Path):
    """Test T13: order already reached cap in previous claim."""
    store = _make_store(tmp_path, "orch_c013.sqlite")
    result = run_claim("C-013", seed=11, store_path=str(store))

    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.refund_effects == []

    conn = connect(store)
    try:
        denied_audit = conn.execute(
            "SELECT COUNT(*) AS c FROM audit_events WHERE claim_id = 'C-013' AND event_type = 'policy_denied'"
        ).fetchone()["c"]
    finally:
        conn.close()
    assert denied_audit == 1


@pytest.mark.student
def test_orchestrator_pay_difference_t14(tmp_path: Path):
    """Test T14: order partially refunded previously; pays only difference."""
    store = _make_store(tmp_path, "orch_c014.sqlite")
    result = run_claim("C-014", seed=11, store_path=str(store))

    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 120000


@pytest.mark.student
def test_orchestrator_retry_idempotency_t11(tmp_path: Path):
    """Test T11: calling run_claim multiple times for C-011 yields exactly 1 refund."""
    store = _make_store(tmp_path, "orch_t11.sqlite")
    res1 = run_claim("C-011", seed=11, store_path=str(store))
    res2 = run_claim("C-011", seed=11, store_path=str(store))

    assert res1.status == "resolved"
    assert res2.status == "resolved"
    conn = connect(store)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert count == 1


@pytest.mark.student
def test_orchestrator_crash_safety_t12(tmp_path: Path):
    """Test T12: crash injection propagates and resume avoids double payment."""
    store = _make_store(tmp_path, "orch_t12.sqlite")

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
    assert crashed, "Orchestrator must propagate InjectedCrash"

    # Resumed call
    res_resumed = run_claim("C-012", seed=11, store_path=str(store))
    assert res_resumed.status == "resolved"

    conn = connect(store)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert count == 1


@pytest.mark.student
def test_orchestrator_unknown_claim_fails(tmp_path: Path):
    """Test unknown claim_id cleanly returns status failed."""
    store = _make_store(tmp_path, "orch_unknown.sqlite")
    result = run_claim("C-999", seed=11, store_path=str(store))

    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
