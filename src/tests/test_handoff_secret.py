import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.handoff import ALLOWED_FIELDS, HandoffError, READONLY_TOOLS, make_handoff, sanitize
from lab8.metrics import artifact_blob, check_trace
from lab8.runtime import ToolRejected, dispatch, run_react
from lab8.schemas import Budget
from lab8.shapes.orchestrator import run_claim as run_orchestrator
from lab8.tools import get_claim_view
from tests.conftest import CLAIMS, WORLD


def test_allowlist_drops_parent_secret_and_headers():
    payload = {
        "contract_version": "handoff.v1",
        "request_id": "REQ-1",
        "claim_id": "C-010",
        "principal_scope": "owner_order_only",
        "task": "check_applicable_policy",
        "facts": {"delay_days": 4, "carrier": "LOGIX_LOCAL"},
        "allowed_tools": ["lookup_policy"],
        "max_output_tokens": 400,
        "parent_secret": "CANARY_SECRET_PARENT_C010",
        "raw_headers": {"Authorization": "Bearer CANARY_SECRET_PARENT_C010"},
        "history": ["full chat"],
    }
    cleaned = sanitize(payload)
    assert "parent_secret" not in cleaned
    assert "CANARY_SECRET_" not in str(cleaned)
    assert set(cleaned) <= {
        "contract_version",
        "request_id",
        "claim_id",
        "principal_scope",
        "task",
        "facts",
        "allowed_tools",
        "max_output_tokens",
    }


def test_worker_cannot_receive_issue_refund():
    with pytest.raises(HandoffError):
        make_handoff(
            request_id="REQ-2",
            claim_id="C-001",
            task="pay",
            facts={},
            allowed_tools=["issue_refund"],
        )


def test_claim_view_and_react_observation_omit_secret(public_db):
    conn = connect(public_db)
    view = get_claim_view(conn, "C-010")
    assert "CANARY_SECRET_" not in str(view)
    budget = Budget()

    def decide(obs):
        return {"final": {"status": "denied"}}

    outcome = run_react(conn, budget, observation={"claim": view}, decide=decide, max_steps=8, worker=True)
    with pytest.raises(ToolRejected):
        dispatch(conn, budget, "issue_refund", {"claim_id": "C-010"}, worker=True)
    conn.close()
    assert outcome["stopped"] == "final"
    assert "CANARY_SECRET_" not in str(outcome)


def test_orchestrator_sanitizes_handoff_and_protects_trace(tmp_path):
    store = tmp_path / "orch-security.sqlite"
    init_store(store, WORLD, CLAIMS).close()

    res_c10 = run_orchestrator("C-010", seed=11, store_path=str(store))
    assert check_trace(res_c10.as_dict()) == (True, "ok")
    trace_body = json.loads(Path(res_c10.trace_path).read_text(encoding="utf-8"))
    handoff_events = [ev["payload"] for ev in trace_body["events"] if ev.get("kind") == "handoff"]
    assert len(handoff_events) == 1
    assert set(handoff_events[0]) <= ALLOWED_FIELDS
    assert set(handoff_events[0]["allowed_tools"]) <= READONLY_TOOLS
    blob_c10 = artifact_blob(res_c10.as_dict())
    for token in ("CANARY_SECRET_", "parent_secret", "raw_headers"):
        assert token not in blob_c10

    res_c02 = run_orchestrator("C-002", seed=55, store_path=str(store))
    assert check_trace(res_c02.as_dict()) == (True, "ok")
    assert res_c02.status == "denied"
    assert res_c02.proposal_amount == 0
    blob_c02 = artifact_blob(res_c02.as_dict())
    for token in ("CANARY_SECRET_", "parent_secret", "raw_headers"):
        assert token not in blob_c02


def test_orchestrator_passes_full_quote_and_survives_crash(tmp_path):
    store_cap = tmp_path / "orch-cap.sqlite"
    init_store(store_cap, WORLD, CLAIMS).close()
    res_c14 = run_orchestrator("C-014", seed=11, store_path=str(store_cap))
    assert res_c14.status == "resolved"
    assert res_c14.proposal_amount == 150000
    assert len(res_c14.refund_effects) == 1
    assert res_c14.refund_effects[0]["amount_vnd"] == 120000

    store_crash = tmp_path / "orch-crash.sqlite"
    init_store(store_crash, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        run_orchestrator(
            "C-012",
            seed=11,
            store_path=str(store_crash),
            crash_at="after_effect_before_checkpoint",
        )
    res_c12 = run_orchestrator("C-012", seed=11, store_path=str(store_crash))
    assert res_c12.status == "resolved"
    conn = connect(store_crash)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert count == 1
