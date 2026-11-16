import json
from pathlib import Path
from unittest.mock import Mock

from lab8.handoff import ALLOWED_FIELDS
from lab8.metrics import artifact_blob
from lab8.shapes import orchestrator
from tests.conftest import BY_ID


def test_orchestrator_delegates_through_sanitized_readonly_handoff(public_db, monkeypatch, capsys):
    investigator = Mock(wraps=orchestrator.run_readonly_investigators)
    monkeypatch.setattr(orchestrator, "run_readonly_investigators", investigator)

    result = orchestrator.run_claim("C-010", seed=55, store_path=str(public_db))

    assert result.status == "resolved"
    investigator.assert_called_once()
    handoff = investigator.call_args.args[2]
    assert set(handoff) == ALLOWED_FIELDS
    assert handoff["contract_version"] == "handoff.v1"
    assert handoff["principal_scope"] == "owner_order_only"
    assert handoff["claim_id"] == result.claim_id
    assert handoff["facts"] == {}
    assert handoff["allowed_tools"] == ["lookup_order"]

    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert {"kind": "handoff", "payload": handoff} in trace["events"]
    captured = capsys.readouterr()
    artifacts = artifact_blob(result.as_dict()) + captured.out + captured.err
    for token in BY_ID["C-010"]["expected"]["forbid_substrings"]:
        assert token not in artifacts
