"""Cross-shape integration and compatibility with the three-file grader overlay."""

import json
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest

from lab8.durability import InjectedCrash
from lab8.shapes import SHAPES, single


@pytest.fixture(autouse=True)
def isolated_traces(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_shapes_run_without_student_ledger_module(public_db, shape):
    # The hidden grader overlays only workflow.py, single.py, orchestrator.py.
    # A fresh process must import and execute them without the added helper.
    script = """
import importlib.abc
import sys
class OfficialModulesOnly(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'lab8.shapes.ledger':
            raise ImportError('student ledger module is not in the grader overlay')
sys.meta_path.insert(0, OfficialModulesOnly())
from lab8.shapes import SHAPES
result = SHAPES[sys.argv[1]]('C-001', seed=11, store_path=sys.argv[2])
assert result.status == 'resolved', result.error_reason
assert result.proposal_amount == 35000
assert len(result.refund_effects) == result.committed_audit_count == 1
"""
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    completed = subprocess.run(
        [sys.executable, "-c", script, shape, str(public_db)],
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert completed.returncode == 0, completed.stderr


@pytest.mark.parametrize("order", [
    ["workflow", "single", "orchestrator"],
    ["single", "orchestrator", "workflow"],
    ["orchestrator", "workflow", "single"],
])
def test_switching_shapes_does_not_duplicate_refund(public_db, order):
    effects = []
    for shape in order:
        result = SHAPES[shape]("C-011", seed=11, store_path=str(public_db))
        assert result.status == "resolved"
        assert len(result.refund_effects) == result.committed_audit_count == 1
        effects.append(result.refund_effects)
    assert effects[0] == effects[1] == effects[2]


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
@pytest.mark.parametrize("crash_at", [
    "before_effect", "after_effect_before_checkpoint", "after_checkpoint",
])
def test_each_shape_resumes_all_crash_windows(public_db, shape, crash_at):
    with pytest.raises(InjectedCrash, match=crash_at):
        SHAPES[shape]("C-012", seed=11, store_path=str(public_db), crash_at=crash_at)
    trace = json.loads(Path(f"traces/R-{shape}-C-012-s11.json").read_text(encoding="utf-8"))
    assert trace["run_id"] == f"R-{shape}-C-012-s11"
    resumed = SHAPES[shape]("C-012", seed=11, store_path=str(public_db))
    assert resumed.status == "resolved"
    assert len(resumed.refund_effects) == resumed.committed_audit_count == 1


def test_single_react_is_bounded_readonly_and_counts_refund(public_db, monkeypatch):
    react = Mock(wraps=single.run_react)
    monkeypatch.setattr(single, "run_react", react)
    result = single.run_claim("C-001", seed=11, store_path=str(public_db))
    react.assert_called_once()
    assert react.call_args.kwargs["max_steps"] == 8
    assert react.call_args.kwargs["worker"] is True
    assert result.status == "resolved"
    assert result.tool_calls == 4  # claim, order, compensation, refund
    assert 0 < result.model_calls <= 8


def test_single_step_cap_cannot_commit_refund(public_db, monkeypatch):
    monkeypatch.setattr(single, "run_react", lambda *args, **kwargs: {
        "stopped": "step_cap", "final": {"status": "failed"},
    })
    refund = Mock(side_effect=AssertionError("refund must stay outside a failed loop"))
    monkeypatch.setattr(single, "issue_refund", refund)
    result = single.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    assert result.error_reason == "step_cap"
    assert result.refund_effects == []
    refund.assert_not_called()
