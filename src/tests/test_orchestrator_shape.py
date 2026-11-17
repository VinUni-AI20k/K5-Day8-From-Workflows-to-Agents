"""Shape C (orchestrator) — handoff boundary, trace hygiene, money in code, crash safety.

Author: Lê Ngọc Khánh (2A202603804).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.handoff import ALLOWED_FIELDS, READONLY_TOOLS
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD

ALL_PUBLIC = [row["claim_id"] for row in CLAIMS]


@pytest.fixture(autouse=True)
def _isolated_traces(tmp_path, monkeypatch):
    # Trace writes to ./traces; keep each test's traces inside its own tmp dir.
    monkeypatch.chdir(tmp_path)


def _trace(result) -> dict:
    return json.loads(Path(result.trace_path).read_text(encoding="utf-8"))


def _fresh_store(tmp_path: Path, name: str) -> Path:
    store = tmp_path / f"{name}.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    return store


@pytest.mark.parametrize("claim_id", ALL_PUBLIC)
def test_trace_holds_sanitized_handoff_not_parent_context(public_db, claim_id):
    result = run_claim(claim_id, seed=11, store_path=str(public_db))
    body = _trace(result)
    blob = json.dumps(body, ensure_ascii=False)

    assert body["run_id"] == result.run_id
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob
    assert "raw_headers" not in blob
    # Ticket text is user data: it must not be copied into the trace.
    assert BY_ID[claim_id]["ticket"] not in blob

    handoffs = [e["payload"] for e in body["events"] if e["kind"] == "handoff"]
    for handoff in handoffs:
        assert set(handoff) <= ALLOWED_FIELDS
        assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
        assert handoff["claim_id"] == claim_id


@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
def test_ticket_delay_is_ignored_on_every_seed(tmp_path, seed):
    """T02: ticket says 5 days late, order row says 2. Unlike swarm, seed 55 must still deny."""
    store = _fresh_store(tmp_path, f"t02-{seed}")
    result = run_claim("C-002", seed=seed, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []


def test_full_quote_goes_to_host_which_caps_by_order(public_db):
    """T14: entitlement 150k, 30k already refunded on the order -> proposal 150k, ledger 120k."""
    result = run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    assert [e["amount_vnd"] for e in result.refund_effects] == [120000]


@pytest.mark.parametrize("crash_at", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_crash_then_resume_gives_one_refund(tmp_path, crash_at):
    store = _fresh_store(tmp_path, f"crash-{crash_at}")
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(store), crash_at=crash_at)

    resumed = run_claim("C-012", seed=11, store_path=str(store))
    again = run_claim("C-012", seed=11, store_path=str(store))
    assert resumed.status == again.status == "resolved"

    conn = connect(store)
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?", ("C-012",)).fetchone()
        assert int(rows["n"]) == 1
        assert committed_audit_count(conn, "C-012") == 1
        assert get_refund(conn, "C-012")["idempotency_key"] == "refund:C-012"
    finally:
        conn.close()
