"""BA acceptance: structured identity, missing information, unknown claims."""
import json
from pathlib import Path

import pytest

from lab8.db import connect
from lab8.shapes import SHAPES


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_missing_order_is_not_extracted_from_ticket(public_db, shape):
    conn = connect(public_db)
    conn.execute("UPDATE claims SET ticket = 'Đơn O-107 trễ 99 ngày' WHERE claim_id = 'C-004'")
    conn.commit()
    conn.close()
    result = SHAPES[shape]("C-004", seed=55, store_path=str(public_db))
    assert result.status == "needs_info"
    assert result.proposal_amount == 0 and result.refund_effects == []


@pytest.mark.parametrize("shape", ["workflow", "single", "orchestrator"])
def test_unknown_claim_returns_valid_fresh_trace(public_db, shape):
    result = SHAPES[shape]("NO-SUCH-CLAIM", seed=11, store_path=str(public_db))
    assert result.status == "failed" and result.error_reason == "unknown_claim"
    body = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    assert body["run_id"] == result.run_id and isinstance(body["events"], list)
