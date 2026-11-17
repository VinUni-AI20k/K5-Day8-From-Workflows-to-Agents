"""Paired checks of draft on/off, including ledger, trace, accounting and cleanup."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from bonus import research_draft_ablation as variant
from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import trial_pass
from lab8.shapes import workflow
from tests.conftest import CLAIMS, WORLD


@pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
@pytest.mark.parametrize("claim", CLAIMS, ids=lambda claim: claim["claim_id"])
def test_draft_removal_preserves_business_behavior(tmp_path, claim, seed):
    original_complete, original_shape = workflow.complete, workflow.SHAPE
    results, events = [], []
    for name, runner in [("baseline", workflow.run_claim), ("no_draft", variant.run_claim)]:
        store = tmp_path / f"{name}.sqlite"
        init_store(store, WORLD, CLAIMS).close()
        started = time.time()
        result = runner(claim["claim_id"], seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), claim["expected"], conn, started_at=started)
            assert passed, reason
        finally:
            conn.close()
        events.append(json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"])
        results.append(result)
    baseline, no_draft = results
    for field in ("status", "proposal_amount", "refund_effects", "committed_audit_count", "error_reason", "tool_calls"):
        assert getattr(baseline, field) == getattr(no_draft, field), field
    assert events[0] == events[1]
    assert baseline.model_calls == 1
    assert no_draft.model_calls == no_draft.input_tokens == no_draft.output_tokens == 0
    assert no_draft.cost_estimate < baseline.cost_estimate
    assert no_draft.shape == variant.SHAPE
    assert baseline.run_id != no_draft.run_id
    assert baseline.trace_path != no_draft.trace_path
    assert workflow.complete is original_complete
    assert workflow.SHAPE == original_shape


def test_ablation_restores_workflow_globals_after_crash(public_db):
    original_complete, original_shape = workflow.complete, workflow.SHAPE
    with pytest.raises(InjectedCrash):
        variant.run_claim("C-001", seed=11, store_path=str(public_db), crash_at="after_effect_before_checkpoint")
    assert workflow.complete is original_complete
    assert workflow.SHAPE == original_shape
    result = variant.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert len(result.refund_effects) == result.committed_audit_count == 1
    assert result.model_calls == 0


def test_ablation_rejects_disabling_a_non_draft_call():
    from lab8.schemas import Budget

    with pytest.raises(ValueError, match="only a draft"):
        variant._skip_draft(Budget(), seed=11, purpose="decide", prompt="")
