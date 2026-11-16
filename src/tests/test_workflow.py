from __future__ import annotations

from lab8.db import connect
from lab8.durability import committed_audit_count, get_refund
from lab8.shapes.workflow import run_claim


def test_workflow_quotes_full_entitlement_and_host_pays_remaining_cap(public_db):
    result = run_claim("C-014", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    assert result.proposal_amount == 150_000

    conn = connect(public_db)
    try:
        effect = get_refund(conn, "C-014")
        assert effect is not None
        assert effect["amount_vnd"] == 120_000
        assert committed_audit_count(conn, "C-014") == 1
    finally:
        conn.close()
