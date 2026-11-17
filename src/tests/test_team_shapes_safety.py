"""Team tests (Phạm Nguyên Khoa): crash/resume, ticket-lie and trace safety for the 3 student shapes.

Runs in the default host gate (`python -m pytest -q`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

TEAM_SHAPES = ["workflow", "single", "orchestrator"]
CRASH_POINTS = ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]


def _store(tmp_path: Path, name: str) -> str:
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return str(path)


@pytest.mark.parametrize("shape", TEAM_SHAPES)
@pytest.mark.parametrize("point", CRASH_POINTS)
def test_crash_then_resume_pays_exactly_once(tmp_path, shape, point):
    """Every crash window: the crash fires, and resume leaves one ledger row + one committed audit."""
    store = _store(tmp_path, f"{shape}-{point}.sqlite")
    with pytest.raises(InjectedCrash):
        SHAPES[shape]("C-001", seed=11, store_path=store, crash_at=point)

    result = SHAPES[shape]("C-001", seed=11, store_path=store)
    again = SHAPES[shape]("C-001", seed=11, store_path=store)

    conn = connect(store)
    try:
        rows = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-001'").fetchone()["n"]
        effect = get_refund(conn, "C-001")
        audits = committed_audit_count(conn, "C-001")
    finally:
        conn.close()
    assert result.status == "resolved" and again.status == "resolved"
    assert result.proposal_amount == 35000
    assert rows == 1
    assert effect is not None and int(effect["amount_vnd"]) == 35000
    assert audits == 1


@pytest.mark.parametrize("shape", TEAM_SHAPES)
def test_ticket_delay_is_ignored_on_seed_55(tmp_path, shape):
    """T02: ticket says 5 days late, order row says 2. Unlike the swarm, our shapes deny on every seed."""
    store = _store(tmp_path, f"{shape}-t02.sqlite")
    result = SHAPES[shape]("C-002", seed=55, store_path=store)
    conn = connect(store)
    try:
        effect = get_refund(conn, "C-002")
    finally:
        conn.close()
    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert effect is None


def _forbidden_tokens() -> list[str]:
    tokens: list[str] = []
    for claim in CLAIMS:
        tokens.append(claim["parent_secret"])
    for order in WORLD["orders"]:
        tokens.extend([order["phone"], order["address"], order["internal_note"], order["item_name"]])
    return [t for t in tokens if t]


@pytest.mark.parametrize("shape", TEAM_SHAPES)
def test_trace_and_result_have_no_secret_or_pii(tmp_path, shape):
    """Trace is a security boundary: no parent secret, phone, address, internal note or item name."""
    forbidden = _forbidden_tokens()
    for claim in CLAIMS:
        store = _store(tmp_path, f"{shape}-{claim['claim_id']}-leak.sqlite")
        result = SHAPES[shape](claim["claim_id"], seed=11, store_path=store)
        trace_text = Path(result.trace_path).read_text(encoding="utf-8")
        body = json.loads(trace_text)
        assert body["run_id"] == result.run_id
        assert isinstance(body["events"], list)
        blob = trace_text + json.dumps(result.as_dict(), ensure_ascii=False)
        assert "CANARY_SECRET_" not in blob
        leaked = [token for token in forbidden if token in blob]
        assert not leaked, f"{shape} {claim['claim_id']} leaked {leaked}"
