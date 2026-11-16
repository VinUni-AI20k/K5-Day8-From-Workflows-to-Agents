from __future__ import annotations

import time
from pathlib import Path

from lab8.db import connect, init_store
from lab8.metrics import artifact_blob, check_trace
from lab8.shapes.workflow import run_claim
from tests.conftest import CLAIMS, WORLD


def _make_store(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_workflow_ignores_ticket_delay_across_all_seeds(tmp_path: Path):
    """Unlike reference swarm on seed 55, workflow always quotes from the order row."""
    for seed in (11, 22, 33, 44, 55):
        store = _make_store(tmp_path, f"wf-c002-{seed}.sqlite")
        started = time.time()
        res = run_claim("C-002", seed=seed, store_path=str(store))
        assert res.status == "denied"
        assert res.proposal_amount == 0
        assert res.refund_effects == []
        assert check_trace(res.as_dict(), started_at=started) == (True, "ok")


def test_workflow_early_returns_and_unknown_claim_keep_clean_trace(tmp_path: Path):
    store = _make_store(tmp_path, "wf-early.sqlite")
    started = time.time()
    unknown = run_claim("C-999", seed=11, store_path=str(store))
    assert unknown.status == "failed"
    assert unknown.proposal_amount == 0
    assert check_trace(unknown.as_dict(), started_at=started) == (True, "ok")

    needs_info = run_claim("C-004", seed=11, store_path=str(store))
    assert needs_info.status == "needs_info"
    assert needs_info.proposal_amount == 0
    blob = artifact_blob(needs_info.as_dict())
    assert "CANARY_SECRET" not in blob


def test_workflow_passes_full_quote_for_per_order_cap(tmp_path: Path):
    store = _make_store(tmp_path, "wf-cap.sqlite")
    t13 = run_claim("C-013", seed=11, store_path=str(store))
    assert t13.status == "denied"
    assert t13.proposal_amount == 35000
    assert t13.refund_effects == []

    t14 = run_claim("C-014", seed=11, store_path=str(store))
    assert t14.status == "resolved"
    assert t14.proposal_amount == 150000
    assert len(t14.refund_effects) == 1
    assert t14.refund_effects[0]["amount_vnd"] == 120000
    conn = connect(store)
    try:
        denied = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-013' AND event_type = 'policy_denied'"
        ).fetchone()["n"]
        assert int(denied) == 1
    finally:
        conn.close()
