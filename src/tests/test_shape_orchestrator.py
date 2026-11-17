"""Orchestrator-specific tests beyond the shared public matrix."""

import json

import pytest

from lab8.db import init_store
from lab8.handoff import HandoffError, sanitize
from lab8.shapes.orchestrator import run_claim
from tests.conftest import CLAIMS, WORLD


def test_handoff_removes_secrets(tmp_path):
    """Verify handoff sanitization strips parent secrets and headers."""
    dirty = {
        "contract_version": "handoff.v1",
        "claim_id": "C-001",
        "task": "test",
        "facts": {},
        "allowed_tools": ["lookup_order"],
        "parent_secret": "CANARY_SECRET_PARENT",
        "raw_headers": {"X-Internal": "secret"},
    }
    cleaned = sanitize(dirty)

    # Check field removal
    assert "parent_secret" not in cleaned
    assert "raw_headers" not in cleaned

    # Check string scanning
    blob = json.dumps(cleaned)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob
    assert "raw_headers" not in blob


def test_handoff_rejects_write_tools(tmp_path):
    """Verify make_handoff raises HandoffError for privileged tools."""
    from lab8.handoff import make_handoff

    with pytest.raises(HandoffError, match="read-only"):
        make_handoff(
            request_id="REQ-001",
            claim_id="C-001",
            task="test",
            facts={},
            allowed_tools=["issue_refund"],  # Write tool
        )


def test_orchestrator_no_secret_in_trace(tmp_path):
    """End-to-end: orchestrator trace never contains parent secrets."""
    store = tmp_path / "test.sqlite"
    init_store(store, WORLD, CLAIMS).close()

    result = run_claim("C-001", seed=11, store_path=str(store))

    # Read trace file
    with open(result.trace_path, encoding="utf-8") as f:
        trace_content = f.read()

    # Scan for secrets
    assert "CANARY_SECRET_" not in trace_content
    assert "parent_secret" not in trace_content
    assert "raw_headers" not in trace_content

    # Verify we got a valid result
    assert result.status in ["resolved", "denied", "needs_info", "escalated", "failed"]
