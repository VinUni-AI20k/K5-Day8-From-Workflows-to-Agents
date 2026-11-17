"""B3: adversarial labels, repair boundary, and durable effects."""
import json
import time
from pathlib import Path

import pytest

from bonus.swarm_verified import run_claim
from bonus.verifier import verify_order
from lab8.db import connect, init_store, load_json, load_jsonl
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import trial_pass
from lab8.schemas import Budget
from lab8.shapes.swarm_reference import run_claim as swarm
from lab8.tools import compute_compensation, lookup_order
from lab8.trace import Trace
from tests.conftest import BY_ID

BONUS_WORLD = load_json("bonus/world.json")
BONUS_CASES = load_jsonl("bonus/cases.jsonl")


@pytest.mark.parametrize("case", BONUS_CASES, ids=lambda c: c["claim_id"])
@pytest.mark.parametrize("seed", [11, 55])
def test_verified_matches_handwritten_adversarial_labels(tmp_path, case, seed):
    store = tmp_path / "bonus.sqlite"
    init_store(store, BONUS_WORLD, BONUS_CASES).close()
    started = time.time()
    result = run_claim(case["claim_id"], seed=seed, store_path=str(store))
    conn = connect(store)
    try:
        passed, reason = trial_pass(result.as_dict(), case["expected"], conn, started_at=started)
        assert passed, reason
    finally:
        conn.close()
    events = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))["events"]
    assert sum(e["kind"] == "verifier_override" for e in events) <= 1


@pytest.mark.parametrize("field,value", [("delay_days", 1), ("status", "cancelled"), ("damage_verified", True)])
def test_verifier_rechecks_each_fact_from_fresh_order(public_db, field, value):
    conn = connect(public_db)
    try:
        candidate = dict(lookup_order(conn, "O-107", "P-100")["order"])
        candidate[field] = value
        trace, budget = Trace(f"R-unit-{field}"), Budget()
        order, quote = verify_order(conn, budget, trace, candidate=candidate,
            quote_payload=compute_compensation(conn, candidate), order_id="O-107", principal_id="P-100")
        assert order[field] != value
        assert quote["amount_vnd"] == 35000
        assert budget.tool_calls == 2  # one fresh read, one bounded requote
        assert [e["kind"] for e in trace.events] == ["verifier_check", "verifier_override"]
    finally:
        conn.close()


def test_verifier_does_not_requote_matching_facts(public_db):
    conn = connect(public_db)
    try:
        order = lookup_order(conn, "O-107", "P-100")["order"]
        quote, budget, trace = compute_compensation(conn, order), Budget(), Trace("R-match")
        _, actual = verify_order(conn, budget, trace, candidate=order, quote_payload=quote,
                                order_id="O-107", principal_id="P-100")
        assert actual is quote
        assert budget.tool_calls == 1
        assert all(e["kind"] != "verifier_override" for e in trace.events)
    finally:
        conn.close()


def test_seed55_reference_misses_and_verifier_repairs_before_write(public_db, monkeypatch):
    import bonus.verifier as verifier
    original = verifier.verify_order
    calls = []

    def checked(conn, *args, **kwargs):
        assert get_refund(conn, "C-002") is None
        calls.append(True)
        return original(conn, *args, **kwargs)

    monkeypatch.setattr(verifier, "verify_order", checked)
    fixed = run_claim("C-002", seed=55, store_path=str(public_db))
    assert fixed.status == "denied" and fixed.proposal_amount == 0
    assert calls == [True]
    conn = connect(public_db)
    try:
        assert get_refund(conn, "C-002") is None
    finally:
        conn.close()
    broken = swarm("C-002", seed=55, store_path=str(public_db))
    assert broken.status == "resolved" and broken.proposal_amount == 20000


@pytest.mark.parametrize("point", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"])
def test_verified_crash_replay_and_audit(public_db, point):
    with pytest.raises(InjectedCrash):
        run_claim("C-012", seed=55, store_path=str(public_db), crash_at=point)
    first = run_claim("C-012", seed=55, store_path=str(public_db))
    second = run_claim("C-012", seed=55, store_path=str(public_db))
    assert first.refund_effects == second.refund_effects
    conn = connect(public_db)
    try:
        assert trial_pass(second.as_dict(), BY_ID["C-012"]["expected"], conn)[0]
        assert committed_audit_count(conn, "C-012") == 1
    finally:
        conn.close()
