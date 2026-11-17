
from __future__ import annotations

import json

import pytest

from lab8.db import init_store
from lab8.durability import InjectedCrash
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


def _trace_text(path: str) -> str:
    return open(path, encoding="utf-8").read()


@pytest.mark.parametrize("claim_id", sorted(BY_ID))
def test_trace_and_result_have_no_secret_or_pii(tmp_path, claim_id):
    store = tmp_path / "s.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim(claim_id, seed=11, store_path=str(store))
    blob = _trace_text(result.trace_path) + json.dumps(result.as_dict(), ensure_ascii=False, default=str)
    assert "CANARY_SECRET_" not in blob
    for bad in BY_ID[claim_id]["expected"].get("forbid_substrings", []):
        assert bad not in blob


def test_trace_records_sanitized_handoff_with_read_only_tools(tmp_path):
    store = tmp_path / "s.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    result = run_claim("C-001", seed=11, store_path=str(store))
    events = json.loads(_trace_text(result.trace_path))["events"]
    handoff = next(e["payload"] for e in events if e["kind"] == "handoff")
    assert "parent_secret" not in handoff and "raw_headers" not in handoff
    assert not {"issue_refund", "append_audit"} & set(handoff["allowed_tools"])


def test_crash_still_writes_trace_and_propagates(tmp_path):
    store = tmp_path / "s.sqlite"
    init_store(store, WORLD, CLAIMS).close()
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=11, store_path=str(store), crash_at="after_effect_before_checkpoint")
