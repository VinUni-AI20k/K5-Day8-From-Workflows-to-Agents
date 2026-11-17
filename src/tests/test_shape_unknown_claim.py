"""Shared result and trace contract for a claim id that is not in the store."""

import time

import pytest

from lab8.db import connect
from lab8.durability import get_refund
from lab8.metrics import check_trace
from lab8.shapes import SHAPES


@pytest.mark.student
@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator", "swarm"])
def test_unknown_claim_fails_without_a_refund_and_writes_trace(shape, public_db):
    started_at = time.time()
    result = SHAPES[shape]("C-UNKNOWN", seed=11, store_path=str(public_db))
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-UNKNOWN") is None
    finally:
        conn.close()

    assert result.status == "failed"
    assert result.proposal_amount == 0
    valid, reason = check_trace(result.as_dict(), started_at=started_at)
    assert valid, reason
