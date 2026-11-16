import json
from contextlib import closing
from pathlib import Path

from lab8.db import connect
from lab8.shapes.workflow import run_claim


def test_workflow_unknown_claim_returns_failed_without_refund(
    public_db, tmp_path, monkeypatch
):
    # Keep the trace inside pytest's temporary directory.
    monkeypatch.chdir(tmp_path)
    claim_id = "C-UNKNOWN"

    with closing(connect(public_db)) as conn:
        ledger_count_before = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger"
        ).fetchone()[0]

        result = run_claim(claim_id, seed=11, store_path=str(public_db))

        ledger_count_after = conn.execute(
            "SELECT COUNT(*) FROM refund_ledger"
        ).fetchone()[0]

    assert result.status == "failed"
    assert result.error_reason == "unknown_claim"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    assert ledger_count_after == ledger_count_before

    trace_path = Path(result.trace_path)
    assert trace_path.is_file()
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)