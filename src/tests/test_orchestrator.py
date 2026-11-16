"""Tests for Shape C: Orchestrator + read-only investigators."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.handoff import HandoffError, make_handoff
from lab8.shapes.orchestrator import run_claim


def test_orchestrator_trace_records_sanitized_handoff(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 35000

    trace_path = Path(result.trace_path)
    assert trace_path.is_file()
    trace_data = json.loads(trace_path.read_text(encoding="utf-8"))

    handoff_events = [e for e in trace_data["events"] if e["kind"] == "handoff"]
    assert len(handoff_events) == 1
    handoff_payload = handoff_events[0]["payload"]
    assert handoff_payload["claim_id"] == "C-001"
    assert "parent_secret" not in handoff_payload
    assert "CANARY_SECRET_" not in str(handoff_payload)
    assert set(handoff_payload["allowed_tools"]) == {
        "lookup_order",
        "lookup_policy",
        "compute_compensation",
    }


def test_orchestrator_rejects_worker_write_tools():
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-TEST",
            claim_id="C-001",
            task="malicious_investigation",
            facts={},
            allowed_tools=["lookup_order", "issue_refund"],
        )


def test_orchestrator_escalates_on_unowned_order(public_db):
    result = run_claim("C-005", seed=11, store_path=str(public_db))
    assert result.status == "escalated"
    assert result.proposal_amount == 0
    assert result.error_reason in ("outside_principal_scope", "not_found")
