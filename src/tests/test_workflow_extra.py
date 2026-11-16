"""Extra checks for shape A (workflow), added by the team.

They pin the four behaviours the workflow must keep:
- the order row beats the ticket text on every seed (where the swarm slips on seed 55),
- the full quote goes to the host, which subtracts earlier refunds on the order,
- a host refusal still reports the full quote and leaves a policy_denied audit,
- a retry keeps one ledger row, and the trace carries no parent secret or ticket text.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID

SEEDS = [11, 22, 33, 44, 55]


def _ledger_rows(store: Path, claim_id: str) -> list[int]:
    conn = connect(store)
    try:
        rows = conn.execute(
            "SELECT amount_vnd FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchall()
    finally:
        conn.close()
    return [int(row["amount_vnd"]) for row in rows]


def _audit_count(store: Path, claim_id: str, event_type: str) -> int:
    conn = connect(store)
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = ? AND event_type = ?",
            (claim_id, event_type),
        ).fetchone()
    finally:
        conn.close()
    return int(row["n"])


@pytest.mark.parametrize("seed", SEEDS)
def test_workflow_ignores_delay_written_in_ticket(public_db: Path, seed: int) -> None:
    # T02: ticket says 5 days late, the order row says 2. No seed may pay.
    result = run_claim("C-002", seed=seed, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert _ledger_rows(public_db, "C-002") == []
    assert _audit_count(public_db, "C-002", "policy_denied") == 0


def test_workflow_passes_full_quote_and_host_pays_difference(public_db: Path) -> None:
    # T14: entitlement 150000, the order already got 30000 from an earlier claim.
    result = run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert _ledger_rows(public_db, "C-014") == [120000]


def test_workflow_host_denial_keeps_quote_and_writes_audit(public_db: Path) -> None:
    # T07: quote is 35000 but the approval is not valid. The host must be the one to refuse.
    result = run_claim("C-007", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert _ledger_rows(public_db, "C-007") == []
    assert _audit_count(public_db, "C-007", "policy_denied") == 1


def test_workflow_retry_keeps_one_refund_and_clean_trace(public_db: Path) -> None:
    first = run_claim("C-011", seed=11, store_path=str(public_db))
    second = run_claim("C-011", seed=11, store_path=str(public_db))
    assert first.status == second.status == "resolved"
    assert _ledger_rows(public_db, "C-011") == [35000]
    assert second.committed_audit_count == 1

    trace_text = Path(second.trace_path).read_text(encoding="utf-8")
    trace = json.loads(trace_text)
    assert trace["run_id"] == second.run_id
    assert isinstance(trace["events"], list)
    claim = BY_ID["C-011"]
    assert claim["parent_secret"] not in trace_text
    assert claim["ticket"] not in trace_text
    assert "CANARY_" not in trace_text
