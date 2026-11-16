"""Focused contract checks for the deterministic workflow shape."""

from __future__ import annotations

import json

from lab8.db import connect
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID


def test_workflow_ignores_delay_claimed_in_ticket_and_keeps_trace_clean(public_db):
    result = run_claim("C-002", seed=55, store_path=str(public_db))

    assert result.status == "denied"
    assert result.proposal_amount == 0
    trace = json.loads(open(result.trace_path, encoding="utf-8").read())
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)
    serialized = json.dumps(trace, ensure_ascii=False)
    assert "CANARY_SECRET_" not in serialized
    assert BY_ID["C-002"]["ticket"] not in serialized


def test_workflow_sends_full_quote_to_host_for_order_with_prior_refund(public_db):
    result = run_claim("C-013", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        refund_count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-013'"
        ).fetchone()["n"]
        denied_count = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events "
            "WHERE claim_id = 'C-013' AND event_type = 'policy_denied'"
        ).fetchone()["n"]
    finally:
        conn.close()

    assert result.status == "denied"
    assert result.proposal_amount == 35_000
    assert refund_count == 0
    assert denied_count == 1


def test_workflow_writes_trace_on_missing_order_early_return(public_db):
    result = run_claim("C-004", seed=11, store_path=str(public_db))

    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    with open(result.trace_path, encoding="utf-8") as handle:
        trace = json.load(handle)
    assert trace["run_id"] == result.run_id
    assert trace["events"][-1] == {
        "kind": "decision",
        "payload": {"status": "needs_info"},
    }
    serialized = json.dumps(trace, ensure_ascii=False)
    assert "CANARY_SECRET_" not in serialized
    assert BY_ID["C-004"]["ticket"] not in serialized
