"""Security and output-contract checks for the orchestrator handoff."""

from __future__ import annotations

import json

import pytest

from lab8.db import connect
from lab8.handoff import READONLY_TOOLS, WRITE_TOOLS
from lab8.schemas import make_run_id
from lab8.shapes.orchestrator import run_claim


def _read_trace(result):
    with open(result.trace_path, encoding="utf-8") as handle:
        return json.load(handle)


def test_orchestrator_handoff_and_trace_are_allowlisted(public_db):
    conn = connect(public_db)
    try:
        claim = conn.execute(
            "SELECT parent_secret, raw_headers_json FROM claims WHERE claim_id = 'C-010'"
        ).fetchone()
        order = conn.execute(
            "SELECT phone, address, internal_note, item_name FROM orders WHERE order_id = 'O-107'"
        ).fetchone()
        forbidden = [claim["parent_secret"], *json.loads(claim["raw_headers_json"]).values()]
        forbidden.extend(order[key] for key in ("phone", "address", "internal_note", "item_name"))
    finally:
        conn.close()

    result = run_claim("C-010", seed=11, store_path=str(public_db))
    trace = _read_trace(result)

    assert result.status == "resolved"
    assert result.run_id == make_run_id("orchestrator", "C-010", 11)
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)

    handoff_events = [event for event in trace["events"] if event["kind"] == "handoff"]
    assert len(handoff_events) == 1
    handoff = handoff_events[0]["payload"]
    assert set(handoff) == {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert not set(handoff["allowed_tools"]) & WRITE_TOOLS
    assert "parent_secret" not in str(trace)
    assert "raw_headers" not in str(trace)
    assert all(value not in str(trace) for value in forbidden if value)
    assert "CANARY_SECRET_" not in str(result.as_dict())


@pytest.mark.parametrize(
    ("claim_id", "expected_status"),
    [("C-004", "needs_info"), ("C-DOES-NOT-EXIST", "failed")],
)
def test_orchestrator_writes_a_valid_trace_for_early_returns(
    public_db, claim_id, expected_status
):
    result = run_claim(claim_id, seed=22, store_path=str(public_db))

    assert result.status == expected_status
    trace = _read_trace(result)
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)
