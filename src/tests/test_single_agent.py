"""Focused checks for the Single agent's trusted data and trace contract."""

import json

from lab8.db import connect
from lab8.shapes.single import run_claim


def test_single_uses_order_facts_instead_of_ticket_delay(public_db):
    # C-002's ticket claims a longer delay than its order row. The single agent
    # must quote from the verified order, so no refund is due.
    result = run_claim("C-002", seed=55, store_path=str(public_db))

    assert result.status == "denied"
    assert result.proposal_amount == 0
    conn = connect(public_db)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = ?",
            ("C-002",),
        ).fetchone()["n"]
    finally:
        conn.close()
    assert count == 0

    trace = json.loads(open(result.trace_path, encoding="utf-8").read())
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)
    assert "CANARY_SECRET_" not in json.dumps(trace)
