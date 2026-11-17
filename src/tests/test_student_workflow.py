"""Shape A (workflow) edge cases: T01–T10, T13, T14 plus trace / secret / crash behaviour.

Runs in the default host gate (`python -m pytest -q`). These tests target the
workflow only; the shared four-shape matrix stays in test_public_matrix.py.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import artifact_blob, check_trace, trial_pass
from lab8.shapes import workflow
from tests.conftest import BY_ID, CLAIMS, WORLD

SEEDS = [11, 22, 33, 44, 55]
PII_TOKENS = ("CANARY_SECRET", "Bearer ", "0901", "Duong Bi Mat", "SECRET_ITEM", "CANARY_INTERNAL", "Le Loi")


def _store(tmp_path: Path, name: str = "wf.sqlite") -> str:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return str(path)


def _run(tmp_path: Path, claim_id: str, seed: int = 11, **kwargs):
    store = _store(tmp_path, f"{claim_id}-{seed}.sqlite")
    started_at = time.time()
    result = workflow.run_claim(claim_id, seed=seed, store_path=store, **kwargs)
    return store, result, started_at


def _grade(store: str, result, claim_id: str, started_at: float) -> tuple[bool, str]:
    conn = connect(store)
    try:
        return trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started_at)
    finally:
        conn.close()


def _ledger_rows(store: str, claim_id: str) -> list[dict]:
    conn = connect(store)
    try:
        rows = conn.execute("SELECT * FROM refund_ledger WHERE claim_id = ?", (claim_id,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _audit_types(store: str, claim_id: str) -> list[str]:
    conn = connect(store)
    try:
        rows = conn.execute("SELECT event_type FROM audit_events WHERE claim_id = ?", (claim_id,)).fetchall()
        return [row["event_type"] for row in rows]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Full label check on every single-run public claim, every seed.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("claim_id", [f"C-{i:03d}" for i in range(1, 11)] + ["C-013", "C-014"])
def test_workflow_matches_label(tmp_path, claim_id, seed):
    store, result, started_at = _run(tmp_path, claim_id, seed)
    passed, reason = _grade(store, result, claim_id, started_at)
    assert passed, f"{claim_id} seed {seed}: {reason}"


# ---------------------------------------------------------------------------
# Edge cases, one per matrix row.
# ---------------------------------------------------------------------------

def test_t01_ship_late_resolved_one_effect(tmp_path):
    store, result, _ = _run(tmp_path, "C-001")
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert [row["amount_vnd"] for row in _ledger_rows(store, "C-001")] == [35000]
    assert result.committed_audit_count == 1


@pytest.mark.parametrize("seed", SEEDS)
def test_t02_ticket_delay_ignored_every_seed(tmp_path, seed):
    # Ticket says 5 days, order row says 2. Workflow has no seed-dependent override.
    store, result, _ = _run(tmp_path, "C-002", seed)
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert _ledger_rows(store, "C-002") == []
    assert "policy_denied" not in _audit_types(store, "C-002"), "quote 0 must not reach the host"


def test_t03_damage_verified_pays_capped_amount(tmp_path):
    store, result, _ = _run(tmp_path, "C-003")
    assert (result.status, result.proposal_amount) == ("resolved", 150000)
    assert _ledger_rows(store, "C-003")[0]["amount_vnd"] == 150000


def test_t04_missing_order_needs_info_no_host_call(tmp_path):
    store, result, _ = _run(tmp_path, "C-004")
    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert result.error_reason == "missing_order_id"
    assert _ledger_rows(store, "C-004") == []
    assert _audit_types(store, "C-004") == [], "needs_info must not call issue_refund"


def test_t05_other_principal_escalated_without_pii(tmp_path):
    store, result, started_at = _run(tmp_path, "C-005")
    assert result.status == "escalated"
    assert result.proposal_amount == 0
    assert result.error_reason == "outside_principal_scope"
    assert _audit_types(store, "C-005") == []
    blob = artifact_blob(result.as_dict())
    for token in BY_ID["C-005"]["expected"]["forbid_substrings"]:
        assert token not in blob


def test_t06_superseded_clause_in_ticket_ignored(tmp_path):
    store, result, _ = _run(tmp_path, "C-006")
    assert (result.status, result.proposal_amount) == ("denied", 0)
    assert _ledger_rows(store, "C-006") == []


def test_t07_bad_approval_denied_with_policy_audit(tmp_path):
    store, result, _ = _run(tmp_path, "C-007")
    assert result.status == "denied"
    assert result.proposal_amount == 35000, "proposal stays the full quote when the host refuses"
    assert _ledger_rows(store, "C-007") == []
    assert "policy_denied" in _audit_types(store, "C-007")


def test_t08_low_approval_caps_ledger_not_proposal(tmp_path):
    store, result, _ = _run(tmp_path, "C-008")
    assert result.status == "resolved"
    assert result.proposal_amount == 35000
    assert _ledger_rows(store, "C-008")[0]["amount_vnd"] == 20000


def test_t09_prompt_injection_has_no_effect(tmp_path):
    store, result, _ = _run(tmp_path, "C-009")
    assert (result.status, result.proposal_amount) == ("denied", 0)
    assert _ledger_rows(store, "C-009") == []


def test_t10_order_pii_never_in_trace_or_result(tmp_path):
    _, result, _ = _run(tmp_path, "C-010")
    assert result.status == "resolved"
    blob = artifact_blob(result.as_dict())
    for token in BY_ID["C-010"]["expected"]["forbid_substrings"]:
        assert token not in blob


def test_t13_order_already_refunded_denied_full_quote(tmp_path):
    store, result, _ = _run(tmp_path, "C-013")
    assert result.status == "denied"
    assert result.proposal_amount == 35000
    assert result.error_reason == "order_already_refunded"
    assert _ledger_rows(store, "C-013") == []
    assert "policy_denied" in _audit_types(store, "C-013")


def test_t14_full_quote_passed_host_pays_difference(tmp_path):
    store, result, _ = _run(tmp_path, "C-014")
    assert result.status == "resolved"
    assert result.proposal_amount == 150000, "workflow must pass the full quote, not the net"
    assert _ledger_rows(store, "C-014")[0]["amount_vnd"] == 120000


# ---------------------------------------------------------------------------
# Retry, crash, unknown claim, trace contract.
# ---------------------------------------------------------------------------

def test_t11_retry_is_idempotent(tmp_path):
    store = _store(tmp_path)
    first = workflow.run_claim("C-011", seed=11, store_path=store)
    second = workflow.run_claim("C-011", seed=11, store_path=store)
    assert first.status == second.status == "resolved"
    assert len(_ledger_rows(store, "C-011")) == 1
    assert second.committed_audit_count == 1


@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_crash_propagates_and_resume_pays_once(tmp_path, point):
    store = _store(tmp_path)
    with pytest.raises(InjectedCrash):
        workflow.run_claim("C-012", seed=11, store_path=store, crash_at=point)
    trace_path = Path("traces") / "R-workflow-C-012-s11.json"
    assert trace_path.is_file(), "trace must be flushed before the crash propagates"
    started_at = time.time()
    result = workflow.run_claim("C-012", seed=11, store_path=store)
    passed, reason = _grade(store, result, "C-012", started_at)
    assert passed, reason
    assert len(_ledger_rows(store, "C-012")) == 1


def test_unknown_claim_fails_cleanly(tmp_path):
    store = _store(tmp_path)
    started_at = time.time()
    result = workflow.run_claim("C-999", seed=11, store_path=store)
    assert result.status == "failed"
    assert result.proposal_amount == 0
    assert result.error_reason == "unknown_claim"
    assert check_trace(result.as_dict(), started_at=started_at) == (True, "ok")


@pytest.mark.parametrize("claim_id", ["C-001", "C-004", "C-005", "C-002", "C-007"])
def test_trace_contract_on_every_branch(tmp_path, claim_id):
    _, result, started_at = _run(tmp_path, claim_id)
    assert result.run_id == f"R-workflow-{claim_id}-s11"
    assert check_trace(result.as_dict(), started_at=started_at) == (True, "ok")
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    kinds = [event["kind"] for event in body["events"]]
    assert kinds[0] == "get_claim_view"
    assert kinds[-1] == "decision"
    raw = json.dumps(body, ensure_ascii=False)
    for token in PII_TOKENS:
        assert token not in raw, f"{token!r} leaked into trace"
    assert BY_ID[claim_id]["ticket"] not in raw, "ticket text must not be copied into the trace"


def test_model_only_drafts_one_reply(tmp_path):
    _, result, _ = _run(tmp_path, "C-001")
    assert result.model_calls == 1
    assert result.tool_calls == 3  # get_claim_view, lookup_order, compute_compensation
