"""Custom Day 8 tests for the Orchestrator handoff contract.

The tests use the starter handoff module without changing its implementation.
"""

import pytest

from lab8.handoff import (
    CONTRACT_VERSION,
    HandoffError,
    READONLY_TOOLS,
    WRITE_TOOLS,
    make_handoff,
    sanitize,
)


def test_handoff_only_forwards_approved_facts():
    """A worker must not receive parent context or customer private details."""
    handoff = make_handoff(
        request_id="REQ-HANDOFF-1",
        claim_id="C-008",
        task="investigate_refund_eligibility",
        facts={
            "delay_days": 3,
            "carrier": "LOGIX_LOCAL",
            "parent_secret": "CANARY_SECRET_SHOULD_BE_DROPPED",
            "customer_phone": "PRIVATE_PHONE",
            "raw_headers": {"Authorization": "PRIVATE_TOKEN"},
        },
        allowed_tools=["lookup_order", "lookup_refund_history"],
    )

    assert handoff["contract_version"] == CONTRACT_VERSION
    assert handoff["principal_scope"] == "owner_order_only"
    assert handoff["facts"] == {"delay_days": 3, "carrier": "LOGIX_LOCAL"}
    assert "CANARY_SECRET_" not in str(handoff)
    assert "PRIVATE_PHONE" not in str(handoff)
    assert "PRIVATE_TOKEN" not in str(handoff)


def test_handoff_rejects_every_write_tool_and_unknown_tool():
    """Investigators receive only names from the read-only tool registry."""
    for tool in sorted(WRITE_TOOLS | {"nonexistent_tool"}):
        with pytest.raises(HandoffError):
            make_handoff(
                request_id="REQ-HANDOFF-2",
                claim_id="C-008",
                task="investigate_refund_eligibility",
                facts={},
                allowed_tools=["lookup_order", tool],
            )

    approved = make_handoff(
        request_id="REQ-HANDOFF-3",
        claim_id="C-008",
        task="investigate_refund_eligibility",
        facts={},
        allowed_tools=sorted(READONLY_TOOLS),
    )
    assert set(approved["allowed_tools"]) == READONLY_TOOLS
    assert not (set(approved["allowed_tools"]) & WRITE_TOOLS)


def test_sanitize_rejects_secret_inside_allowed_fact():
    """Allowed field names cannot be used to smuggle secret text to workers."""
    payload = make_handoff(
        request_id="REQ-HANDOFF-4",
        claim_id="C-008",
        task="investigate_refund_eligibility",
        facts={"carrier": "LOGIX_LOCAL"},
        allowed_tools=["lookup_order"],
    )
    payload["facts"]["carrier"] = "CANARY_SECRET_NESTED"
    with pytest.raises(HandoffError):
        sanitize(payload)
