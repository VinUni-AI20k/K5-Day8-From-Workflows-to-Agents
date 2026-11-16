"""Shape B guards: ticket text is not trusted, the step cap holds, the model cannot write."""

from __future__ import annotations

import pytest

from lab8.db import connect, init_store
from lab8.runtime import ToolRejected, dispatch, run_react
from lab8.schemas import Budget
from lab8.shapes import single
from tests.conftest import CLAIMS, WORLD


def _store(tmp_path):
    path = tmp_path / "single.sqlite"
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_single_ignores_ticket_delay_on_swarm_weak_seed(tmp_path):
    # C-002 ticket says 5 days late, order row says 2. Seed 55 is where the swarm trusts the ticket.
    store = _store(tmp_path)
    result = single.run_claim("C-002", seed=55, store_path=str(store))
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert 0 < result.model_calls <= single.MAX_STEPS


def test_model_cannot_dispatch_issue_refund(tmp_path):
    conn = connect(_store(tmp_path))
    try:
        with pytest.raises(ToolRejected):
            dispatch(conn, Budget(), "issue_refund", {"claim_id": "C-001"}, worker=False)
        looping = run_react(conn, Budget(), observation={}, decide=lambda _: {"tool": "lookup_policy"}, max_steps=8)
        assert looping["stopped"] == "step_cap"
    finally:
        conn.close()
