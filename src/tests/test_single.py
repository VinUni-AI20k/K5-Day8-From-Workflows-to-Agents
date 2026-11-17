import json

import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.metrics import check_trace
from lab8.runtime import ToolRejected, run_react
from lab8.schemas import Budget
from lab8.shapes.single import run_claim
from lab8.tools import tool_cost


@pytest.mark.parametrize(
    "claim_id, status, reason",
    [
        ("C-UNKNOWN", "failed", "unknown_claim"),
        ("C-004", "needs_info", "missing_order_id"),
    ],
)
def test_single_preflight_returns_safe_result_without_refund(
    public_db, tmp_path, monkeypatch, claim_id, status, reason
):
    monkeypatch.chdir(tmp_path)
    conn = connect(public_db)
    try:
        before = conn.execute("SELECT COUNT(*) FROM refund_ledger").fetchone()[0]
        result = run_claim(claim_id, seed=11, store_path=str(public_db))
        after = conn.execute("SELECT COUNT(*) FROM refund_ledger").fetchone()[0]
    finally:
        conn.close()

    assert result.claim_id == claim_id
    assert result.status == status
    assert result.error_reason == reason
    assert result.proposal_amount == 0
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    assert after == before
    assert result.tool_calls == 1
    assert result.model_calls == 0
    assert result.cost_estimate == tool_cost()
    assert check_trace(result.as_dict()) == (True, "ok")

    with open(result.trace_path, encoding="utf-8") as handle:
        trace = json.load(handle)
    assert trace["events"] == [
        {"kind": "tool", "payload": {"name": "get_claim_view", "found": claim_id != "C-UNKNOWN"}},
        {"kind": "decision", "payload": {"status": status, "reason": reason}},
    ]


@pytest.mark.parametrize("claim_id", ["C-002", "C-005", "C-006", "C-009"])
def test_single_react_handles_scope_and_untrusted_ticket(public_db, tmp_path, monkeypatch, claim_id):
    from lab8.metrics import trial_pass
    from tests.conftest import BY_ID

    monkeypatch.chdir(tmp_path)
    result = run_claim(claim_id, seed=55, store_path=str(public_db))
    conn = connect(public_db)
    try:
        assert trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn) == (True, "ok")
    finally:
        conn.close()
    assert 0 < result.model_calls <= 8
    assert result.input_tokens > 0
    assert result.output_tokens > 0
    assert result.cost_estimate > result.tool_calls * tool_cost()


def test_single_host_subtracts_prior_refund_from_full_quote(public_db, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.proposal_amount == 150000
    assert result.status == "resolved"
    assert result.error_reason is None
    assert len(result.refund_effects) == 1
    assert result.refund_effects[0]["amount_vnd"] == 120000
    assert result.committed_audit_count == 1
    assert result.model_calls == 3
    assert result.tool_calls == 3


def test_single_uses_eight_step_readonly_loop(public_db, tmp_path, monkeypatch):
    import lab8.shapes.single as single

    monkeypatch.chdir(tmp_path)
    calls = []

    def repeat_reads(conn, budget, *, observation, decide, max_steps, worker):
        assert max_steps == 8
        assert worker is True

        def keep_reading(seen):
            calls.append(seen)
            return {"tool": "lookup_policy", "args": {}}

        return run_react(
            conn, budget, observation=observation, decide=keep_reading,
            max_steps=max_steps, worker=worker,
        )

    monkeypatch.setattr(single, "run_react", repeat_reads)
    result = single.run_claim("C-001", seed=11, store_path=str(public_db))
    assert len(calls) == 8
    assert result.status == "failed"
    assert result.error_reason == "step_cap"
    assert result.refund_effects == []


def test_react_rejects_model_write_tool(public_db):
    conn = connect(public_db)
    try:
        with pytest.raises(ToolRejected):
            run_react(
                conn, Budget(), observation={},
                decide=lambda observation: {"tool": "issue_refund", "args": {}},
                max_steps=8, worker=True,
            )
    finally:
        conn.close()


@pytest.mark.parametrize(
    "crash_at", ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]
)
def test_single_resumes_all_crash_windows(public_db, tmp_path, monkeypatch, crash_at):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(InjectedCrash):
        run_claim("C-001", seed=11, store_path=str(public_db), crash_at=crash_at)

    trace_path = tmp_path / "traces" / "R-single-C-001-s11.json"
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["events"][-1] == {"kind": "crash", "payload": {"at": crash_at}}

    resumed = run_claim("C-001", seed=11, store_path=str(public_db))
    replay = run_claim("C-001", seed=11, store_path=str(public_db))
    assert resumed.status == replay.status == "resolved"
    assert len(replay.refund_effects) == 1
    assert replay.refund_effects[0]["amount_vnd"] == 35000
    assert replay.committed_audit_count == 1


def test_single_conflicting_quote_keeps_committed_refund(public_db, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    first = run_claim("C-001", seed=11, store_path=str(public_db))
    assert first.status == "resolved"

    conn = connect(public_db)
    try:
        conn.execute("UPDATE orders SET shipping_fee_vnd = 10000 WHERE order_id = 'O-107'")
        conn.commit()
    finally:
        conn.close()

    retry = run_claim("C-001", seed=11, store_path=str(public_db))
    assert retry.status == "failed"
    assert retry.error_reason == "amount_conflict"
    assert retry.proposal_amount == 10000
    assert retry.refund_effects == first.refund_effects
    assert retry.committed_audit_count == 1
