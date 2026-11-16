"""Presentation API: true shape execution, isolated effects, no fixture PII."""

import json

import pytest

from demo_ui.server import catalog, run_demo
from demo_ui.runner import validate
from lab8.config_loader import repo_path


def test_catalog_drops_private_columns_and_respects_principal():
    payload = catalog()
    blob = json.dumps(payload)
    for token in ("CANARY_SECRET_", "parent_secret", "raw_headers", "phone", "address", "internal_note", "item_name"):
        assert token not in blob
    assert len(payload["datasets"]["public"]) == 14
    assert len(payload["datasets"]["bonus"]) == 12
    outsider = next(row for row in payload["datasets"]["bonus"] if row["claim_id"] == "B3-012")
    assert outsider["visible"] is False
    assert outsider["order"] is None


def test_bonus_demo_shows_real_before_and_after_without_changing_reports():
    report = repo_path("reports", "benchmark.json")
    before = report.read_bytes()
    response = run_demo({"dataset":"public", "claim_id":"C-002", "seed":55,
                         "shapes":["swarm", "swarm_verified", "workflow"], "mode":"fresh"})
    results = {row["shape"]:row for row in response["results"]}
    assert results["swarm"]["passed"] is False
    assert results["swarm"]["ledger"]["refund_amount"] == 20000
    assert results["swarm_verified"]["passed"] is True
    assert results["swarm_verified"]["ledger"]["refund_count"] == 0
    override = next(e for e in results["swarm_verified"]["trace"]["events"] if e["kind"] == "verifier_override")
    assert override["payload"]["previous_amount_vnd"] == 20000
    assert override["payload"]["verified_amount_vnd"] == 0
    assert report.read_bytes() == before
    blob = json.dumps(response)
    assert "CANARY_SECRET_" not in blob
    assert "trace_path" not in blob


def test_demo_crash_and_resume_use_same_ledger():
    response = run_demo({"dataset":"public", "claim_id":"C-012", "seed":11,
                         "shapes":["workflow"], "mode":"crash", "crash_at":"after_effect_before_checkpoint"})
    result = response["results"][0]
    assert result["crash_observed"] is True
    assert result["passed"] is True
    assert [row["phase"] for row in result["attempts"]] == ["crashed", "resume", "retry"]
    assert all(row["refund_count"] == row["committed_audit_count"] == 1 for row in result["attempts"])
    assert result["ledger"]["refund_amount"] == 35000


def test_demo_requests_start_with_independent_databases():
    request = {"dataset":"bonus", "claim_id":"B3-011", "seed":55, "shapes":["swarm_verified"], "mode":"retry"}
    first = run_demo(request)["results"][0]
    second = run_demo(request)["results"][0]
    assert first["ledger"] == second["ledger"]
    assert first["ledger"]["refund_amount"] == 120000
    assert first["ledger"]["refund_count"] == 1


@pytest.mark.parametrize("changes", [
    {"dataset":"../data"}, {"claim_id":"../world.json"},
    {"shapes":["eval"]}, {"shapes":["workflow", "workflow"]},
    {"seed":True}, {"seed":999}, {"mode":"delete"}, {"crash_at":"bad"},
    {"dataset":[]}, {"claim_id":{}}, {"crash_at":[]},
])
def test_demo_rejects_invalid_inputs(changes):
    request = {"dataset":"public", "claim_id":"C-001", "seed":11, "shapes":["workflow"]}
    request.update(changes)
    with pytest.raises(ValueError):
        validate(request)
