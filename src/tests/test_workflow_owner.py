"""Owner tests for Shape A (workflow) — TEAM.md member 1.

Cases: ticket delay ignored; missing order_id; order outside principal.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lab8.db import init_store
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def _store(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


@pytest.mark.student
def test_workflow_ignores_wrong_ticket_delay(tmp_path: Path) -> None:
    """C-002 ticket says 5 days; order O-202 has delay_days=2 → deny, do not trust ticket."""
    store = _store(tmp_path, "workflow-owner-c002.sqlite")
    result = run_claim("C-002", seed=11, store_path=str(store))
    expected = BY_ID["C-002"]["expected"]
    assert result.status == expected["status"] == "denied"
    assert result.proposal_amount == expected["proposal_amount"] == 0


@pytest.mark.student
def test_workflow_missing_order_id_needs_info(tmp_path: Path) -> None:
    store = _store(tmp_path, "workflow-owner-c004.sqlite")
    result = run_claim("C-004", seed=11, store_path=str(store))
    assert result.status == "needs_info"
    assert result.proposal_amount == 0
    assert result.error_reason == "missing_order_id"


@pytest.mark.student
def test_workflow_outside_principal_escalated_no_pii(tmp_path: Path) -> None:
    store = _store(tmp_path, "workflow-owner-c005.sqlite")
    result = run_claim("C-005", seed=11, store_path=str(store))
    expected = BY_ID["C-005"]["expected"]
    assert result.status == "escalated"
    assert result.proposal_amount == 0
    blob = f"{result.as_dict()}{Path(result.trace_path).read_text(encoding='utf-8')}"
    for forbidden in expected["forbid_substrings"]:
        assert forbidden not in blob, f"leaked {forbidden!r}"
