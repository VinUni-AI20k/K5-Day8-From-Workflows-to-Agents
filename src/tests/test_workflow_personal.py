import json
from pathlib import Path

import pytest

from lab8.shapes.workflow import run_claim


@pytest.mark.student
def test_workflow_trace_redacts_claim_and_order_sensitive_fields(public_db):
    result = run_claim("C-001", seed=11, store_path=str(public_db))

    assert result.status == "resolved"
    trace = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    trace_blob = json.dumps(trace, ensure_ascii=False)

    for forbidden in (
        "CANARY_SECRET_PARENT_C-001",
        "Bearer CANARY_SECRET_PARENT_C-001",
        "0901000107",
        "12 Le Loi Q1",
        "CANARY_INTERNAL_O107",
        "Ao thun",
    ):
        assert forbidden not in trace_blob
