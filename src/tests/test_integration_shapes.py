"""Integration checks across all four shapes.

The public matrix grades each shape alone. These tests check the shapes
*together*: one signature, one contract, the same decision on the same claim,
and no shape leaks a secret or PII string from the world into its trace.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from lab8.db import connect, init_store
from lab8.shapes import SHAPES
from tests.conftest import CLAIMS, WORLD

TEAM_SHAPES = ["workflow", "single", "orchestrator"]
ALL_SHAPES = TEAM_SHAPES + ["swarm"]
SEEDS = [11, 22, 33, 44, 55]
STATUSES = {"resolved", "needs_info", "escalated", "denied", "failed"}

# Every string a trace must never contain: parent secrets, headers, and the
# PII / internal fields of every order in the public world.
FORBIDDEN = sorted(
    {s for claim in CLAIMS for s in claim["expected"]["forbid_substrings"]}
    | {
        str(order[key])
        for order in WORLD["orders"]
        for key in ("phone", "address", "internal_note", "item_name")
        if order.get(key)
    }
)


def _fresh_store(db: Path) -> Path:
    init_store(db, WORLD, CLAIMS).close()
    return db


def _ledger(db: Path, claim_id: str) -> list[int]:
    conn = connect(str(db))
    try:
        rows = conn.execute("SELECT amount_vnd FROM refund_ledger WHERE claim_id = ?", (claim_id,))
        return [int(r["amount_vnd"]) for r in rows]
    finally:
        conn.close()


def test_all_shapes_share_one_signature() -> None:
    reference = inspect.signature(SHAPES["swarm"])
    for shape in TEAM_SHAPES:
        assert inspect.signature(SHAPES[shape]) == reference, shape


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("claim", CLAIMS, ids=lambda c: c["claim_id"])
def test_team_shapes_agree_on_every_public_claim(tmp_path: Path, claim: dict, seed: int) -> None:
    """Same claim + seed -> same status, proposal and ledger amount on A, B and C."""
    outcomes = {}
    for shape in TEAM_SHAPES:
        db = _fresh_store(tmp_path / f"{shape}.sqlite")
        result = SHAPES[shape](claim["claim_id"], seed=seed, store_path=str(db))
        assert result.status in STATUSES
        assert result.claim_id == claim["claim_id"]
        assert isinstance(result.proposal_amount, int)
        outcomes[shape] = (result.status, result.proposal_amount, _ledger(db, claim["claim_id"]))
    assert len(set(map(repr, outcomes.values()))) == 1, outcomes
    status, proposal, _ = outcomes["workflow"]
    assert (status, proposal) == (claim["expected"]["status"], claim["expected"]["proposal_amount"])


@pytest.mark.parametrize("shape", ALL_SHAPES)
def test_no_shape_leaks_secret_or_pii(tmp_path: Path, shape: str) -> None:
    for claim in CLAIMS:
        db = _fresh_store(tmp_path / f"{claim['claim_id']}.sqlite")
        result = SHAPES[shape](claim["claim_id"], seed=55, store_path=str(db))
        trace_path = Path(result.trace_path)
        trace = json.loads(trace_path.read_text(encoding="utf-8"))
        assert trace["run_id"] == result.run_id
        assert isinstance(trace["events"], list)
        blobs = [p.read_text(encoding="utf-8") for p in trace_path.parent.glob(f"{result.run_id}*")]
        blobs.append(json.dumps(result.__dict__, ensure_ascii=False, default=str))
        for blob in blobs:
            leaked = [s for s in FORBIDDEN if s in blob]
            assert not leaked, f"{shape} {claim['claim_id']} leaked {leaked}"
