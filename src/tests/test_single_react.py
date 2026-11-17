"""Unit tests for Shape B (Single ReAct Agent) and its bounded ReAct loop.

Student test suite added by Member 2 (Single Agent).
Validates:
1. ReAct loop bounds (step cap at 8).
2. Worker rejection of unauthorized or write tools.
3. Decision progression and trace contract compliance without secret leakage.
4. Immunity to misleading ticket text (not trusting delay written in ticket).
5. Proper early stops (unknown claim, missing order_id, unowned order).
"""

from __future__ import annotations

import time
import pytest

from lab8.db import connect
from lab8.durability import get_refund
from lab8.metrics import check_trace
from lab8.runtime import ToolRejected, dispatch, run_react
from lab8.schemas import Budget
from lab8.shapes.single import run_claim
from tests.conftest import BY_ID


def test_react_loop_enforces_step_cap(public_db):
    """ReAct loop must terminate with step_cap when max_steps=8 is reached without final."""
    conn = connect(public_db)
    budget = Budget()
    step_counter = 0

    def looping_decide(seen):
        nonlocal step_counter
        step_counter += 1
        # Continually request lookup_policy without ever returning 'final'
        return {"tool": "lookup_policy", "args": {}}

    try:
        outcome = run_react(
            conn,
            budget,
            observation={"claim_id": "C-001"},
            decide=looping_decide,
            max_steps=8,
            worker=True,
        )
        assert outcome["stopped"] == "step_cap"
        assert outcome["final"]["status"] == "failed"
        assert outcome["final"]["error_reason"] == "step_cap"
        assert step_counter == 8
    finally:
        conn.close()


def test_react_loop_blocks_write_tools_for_worker(public_db):
    """The ReAct worker must never be allowed to call write tools like issue_refund."""
    conn = connect(public_db)
    budget = Budget()

    try:
        with pytest.raises(ToolRejected) as exc_info:
            dispatch(conn, budget, "issue_refund", {"claim_id": "C-001"}, worker=True)
        assert "issue_refund" in str(exc_info.value) or "write tools" in str(exc_info.value)
    finally:
        conn.close()


def test_react_loop_rejects_unknown_tools(public_db):
    """Dispatch must raise ToolRejected for unregistered tool names."""
    conn = connect(public_db)
    budget = Budget()

    try:
        with pytest.raises(ToolRejected):
            dispatch(conn, budget, "unknown_tool", {}, worker=True)
    finally:
        conn.close()


def test_single_agent_resolves_valid_claim(tmp_path, public_db):
    """C-001: 4 days late on 35k shipping fee -> resolved with 35k proposal."""
    started = time.time()
    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 35000
    assert result.committed_audit_count == 1
    assert result.error_reason is None

    # Trace contract validation
    trace_ok, trace_reason = check_trace(result.as_dict(), started_at=started)
    assert trace_ok, trace_reason


def test_single_agent_ignores_misleading_ticket_delay(public_db):
    """C-002: Customer claims 5 days delay, but order delay is 2 days (< 3 days required).
    Single agent must check verified order and deny, not trust ticket text."""
    result = run_claim("C-002", seed=55, store_path=str(public_db))

    assert result.status == "denied"
    assert result.proposal_amount == 0

    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-002") is None
    finally:
        conn.close()


def test_single_agent_stops_early_on_missing_order_id(public_db):
    """C-004: Claim has no order_id -> early stop with needs_info and 0 refund."""
    result = run_claim("C-004", seed=11, store_path=str(public_db))

    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert result.error_reason == "missing_order_id"

    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-004") is None
    finally:
        conn.close()


def test_single_agent_stops_early_on_unknown_claim(public_db):
    """Non-existent claim -> early stop with failed and unknown_claim."""
    result = run_claim("C-999", seed=11, store_path=str(public_db))

    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert result.error_reason == "unknown_claim"


def test_single_agent_escalates_unowned_order(public_db):
    """C-005: Principal does not own the order -> escalated without exposing secret data."""
    result = run_claim("C-005", seed=11, store_path=str(public_db))

    assert result.status == "escalated"
    assert result.proposal_amount == 0
    assert result.error_reason == "outside_principal_scope"

    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-005") is None
    finally:
        conn.close()
