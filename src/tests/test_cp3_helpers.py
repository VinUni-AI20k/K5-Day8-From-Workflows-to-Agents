import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash, get_refund
from lab8.schemas import Budget
from lab8.shapes.cp3 import finish_refund
from lab8.trace import Trace


@pytest.mark.parametrize("crash_at", [None, "before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_refund_helper_retry_and_crash_resume(public_db, tmp_path, crash_at):
    def run(conn, attempt, crash=None):
        return finish_refund(
            conn,
            shape="workflow",
            claim_id="C-011",
            seed=11,
            proposal_amount=35000,
            budget=Budget(),
            trace=Trace(f"cp3-{attempt}", directory=tmp_path),
            crash_at=crash,
        )

    conn = connect(public_db)
    try:
        if crash_at is None:
            assert run(conn, "first").status == "resolved"
        else:
            with pytest.raises(InjectedCrash, match=crash_at):
                run(conn, "crash", crash_at)
            if crash_at == "after_effect_before_checkpoint":
                assert get_refund(conn, "C-011") is not None
                assert conn.execute(
                    "SELECT 1 FROM checkpoints WHERE claim_id = 'C-011'"
                ).fetchone() is None
    finally:
        conn.close()

    # Resume with a new connection, so no in-memory state can prevent duplication.
    conn = connect(public_db)
    try:
        result = run(conn, "resume")
        assert result.status == "resolved"
        assert result.proposal_amount == 35000
        assert result.committed_audit_count == 1
        assert result.refund_effects[0]["idempotency_key"] == "refund:C-011"
        assert conn.execute(
            "SELECT COUNT(*) FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()[0] == 1
    finally:
        conn.close()
