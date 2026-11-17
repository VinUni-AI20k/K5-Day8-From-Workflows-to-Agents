"""Safety & Testing test: Invariant enforcement for refund approval.

A refund must NEVER be committed to the ledger without a valid approval,
even when the order qualifies for compensation (e.g. delivered late).
"""

from __future__ import annotations

import json
from lab8.db import connect
from lab8.durability import committed_audit_count, get_refund, issue_refund


def test_rejected_approval_blocks_refund_and_leaves_ledger_empty(public_db):
    """Host invariant: when an approval has status 'rejected', issue_refund must fail,
    record policy_denied, and commit no row to the refund ledger."""
    conn = connect(public_db)
    claim_id = "C-TEST-REJECTED"
    approval_id = "A-TEST-REJECTED"
    order_id = "O-107"  # Valid delivered_late order (delay_days=4, shipping_fee_vnd=35000)
    principal_id = "P-100"

    # Count rows in ledger before attempt
    ledger_count_before = conn.execute("SELECT COUNT(*) AS c FROM refund_ledger").fetchone()["c"]

    # Insert an approval with status 'rejected' bound to this claim
    conn.execute(
        """
        INSERT INTO approvals (approval_id, claim_id, approved_vnd, status, expires_at)
        VALUES (?, ?, 35000, 'rejected', '2027-12-31')
        """,
        (approval_id, claim_id),
    )

    # Insert a claim pointing to the rejected approval
    conn.execute(
        """
        INSERT INTO claims (claim_id, principal_id, order_id, ticket, parent_secret, raw_headers_json, approval_id)
        VALUES (?, ?, ?, 'Đơn giao trễ 4 ngày, yêu cầu hoàn phí ship', 'CANARY_SECRET_PARENT_TEST', '{}', ?)
        """,
        (claim_id, principal_id, order_id, approval_id),
    )
    conn.commit()

    # Attempt to issue refund with a positive proposed quote (full entitlement = 35000)
    outcome = issue_refund(conn, claim_id, 35000)

    # Invariant checks:
    # 1. Host refuses the refund
    assert outcome["ok"] is False
    assert outcome["reason"] == "approval_rejected"
    assert outcome["effect"] is None
    assert outcome["conflict"] is False

    # 2. Ledger has NO refund for this claim
    assert get_refund(conn, claim_id) is None

    # 3. Ledger has NO new rows committed
    ledger_count_after = conn.execute("SELECT COUNT(*) AS c FROM refund_ledger").fetchone()["c"]
    assert ledger_count_after == ledger_count_before

    # 4. No refund_committed audit event is logged
    assert committed_audit_count(conn, claim_id) == 0

    # 5. Host recorded policy_denied with reason approval_rejected
    denials = conn.execute(
        "SELECT event_type, details_json FROM audit_events WHERE claim_id = ?",
        (claim_id,),
    ).fetchall()
    assert any(
        row["event_type"] == "policy_denied" and json.loads(row["details_json"]).get("reason") == "approval_rejected"
        for row in denials
    )

    conn.close()
