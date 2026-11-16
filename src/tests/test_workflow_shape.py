"""Extra checks for shape A (workflow) beyond the public matrix."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID, CLAIMS

SEEDS = [11, 22, 33, 44, 55]


@pytest.mark.parametrize("seed", SEEDS)
def test_ticket_delay_never_overrides_order_row(public_db: Path, seed: int) -> None:
    # C-002: ticket says 5 days late, order row says 2. Workflow must deny on every seed,
    # including seed 55 where the reference swarm trusts the ticket.
    result = run_claim("C-002", seed=seed, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []


@pytest.mark.parametrize("claim_id", [row["claim_id"] for row in CLAIMS])
def test_trace_has_no_secret_or_ticket_text(public_db: Path, claim_id: str) -> None:
    result = run_claim(claim_id, seed=55, store_path=str(public_db))
    body = Path(result.trace_path).read_text(encoding="utf-8")
    trace = json.loads(body)
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)
    claim = BY_ID[claim_id]
    for forbidden in [claim["parent_secret"], "CANARY_SECRET", "Bearer", claim["ticket"]]:
        assert forbidden not in body
        assert forbidden not in json.dumps(result.__dict__, ensure_ascii=False, default=str)


@pytest.mark.parametrize("crash_at", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_crash_then_resume_pays_once(public_db: Path, crash_at: str) -> None:
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(public_db), crash_at=crash_at)
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.committed_audit_count == 1
    conn = connect(str(public_db))
    try:
        rows = conn.execute("SELECT amount_vnd FROM refund_ledger WHERE claim_id = 'C-001'").fetchall()
    finally:
        conn.close()
    assert [int(r["amount_vnd"]) for r in rows] == [35000]


def test_unknown_claim_fails_without_exception(public_db: Path) -> None:
    result = run_claim("C-DOES-NOT-EXIST", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert Path(result.trace_path).exists()
