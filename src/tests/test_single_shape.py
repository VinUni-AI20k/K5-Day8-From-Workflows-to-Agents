"""Focused contract tests for the single ReAct shape."""

import json

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash
from lab8.metrics import artifact_blob
from lab8.shapes.single import run_claim
from tests.conftest import CLAIMS, WORLD


def _store(tmp_path, name):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def test_single_uses_order_data_and_does_not_trace_ticket(tmp_path):
    store = _store(tmp_path, "single-order-source.sqlite")
    result = run_claim("C-002", seed=55, store_path=str(store))

    assert result.status == "denied"
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    claim = next(row for row in CLAIMS if row["claim_id"] == "C-002")
    order = next(row for row in WORLD["orders"] if row["order_id"] == claim["order_id"])
    blob = artifact_blob(result.as_dict())
    assert claim["ticket"] not in blob
    assert claim["parent_secret"] not in blob
    assert all(value not in blob for value in claim["raw_headers"].values())
    assert all(
        order[field] not in blob
        for field in ("phone", "address", "internal_note", "item_name")
    )

    trace = json.loads(open(result.trace_path, encoding="utf-8").read())
    assert trace["run_id"] == result.run_id
    assert isinstance(trace["events"], list)
    assert any(event["kind"] == "quote" for event in trace["events"])


def test_single_passes_full_quote_and_host_applies_order_cap(tmp_path):
    store = _store(tmp_path, "single-order-cap.sqlite")
    result = run_claim("C-014", seed=11, store_path=str(store))

    assert result.status == "resolved"
    assert result.proposal_amount == 150_000
    assert result.refund_effects[0]["amount_vnd"] == 120_000
    conn = connect(store)
    try:
        total = conn.execute(
            "SELECT SUM(amount_vnd) AS amount FROM refund_ledger WHERE order_id = 'O-515'"
        ).fetchone()["amount"]
    finally:
        conn.close()
    assert total == 150_000


def test_single_forwards_crash_and_retry_keeps_one_refund(tmp_path):
    store = _store(tmp_path, "single-crash.sqlite")
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-012",
            seed=11,
            store_path=str(store),
            crash_at="after_effect_before_checkpoint",
        )

    result = run_claim("C-012", seed=11, store_path=str(store))
    assert result.status == "resolved"
    conn = connect(store)
    try:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
    finally:
        conn.close()
    assert count == 1

