"""Tests for Shape A — deterministic workflow.

Covers: happy path, edge cases, business rules, durability (idempotency + crash),
security (no secret/PII leakage), trace contract v1, and per-order cap logic.
"""

from __future__ import annotations

import json
import time

import pytest

from lab8.db import connect, init_store
from lab8.durability import InjectedCrash, committed_audit_count, get_refund
from lab8.metrics import check_trace, trial_pass
from lab8.shapes.workflow import run_claim
from tests.conftest import BY_ID, CLAIMS, WORLD


# ── helpers ──────────────────────────────────────────────────────────────────

def _store(tmp_path, name: str = "workflow.sqlite"):
    path = tmp_path / name
    init_store(path, WORLD, CLAIMS).close()
    return path


def _run(tmp_path, claim_id: str, seed: int = 11, *, name: str | None = None, crash_at: str | None = None):
    store = _store(tmp_path, name or f"wf-{claim_id}-{seed}.sqlite")
    result = run_claim(claim_id, seed=seed, store_path=str(store), crash_at=crash_at)
    return result, store


# ── T01: happy path — late delivery, full refund ─────────────────────────────

class TestT01HappyPath:
    """C-001: O-107 trễ 4 ngày, phí ship 35000, approval 35000."""

    def test_status_resolved(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        assert result.status == "resolved"

    def test_proposal_amount_is_full_quote(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        assert result.proposal_amount == 35000

    def test_one_ledger_row_one_audit(self, tmp_path):
        result, store = _run(tmp_path, "C-001")
        conn = connect(store)
        effect = get_refund(conn, "C-001")
        audits = committed_audit_count(conn, "C-001")
        conn.close()
        assert int(effect["amount_vnd"]) == 35000
        assert audits == 1

    def test_refund_effects_match_ledger(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        assert len(result.refund_effects) == 1
        assert int(result.refund_effects[0]["amount_vnd"]) == 35000
        assert result.committed_audit_count == 1


# ── T02: denied — delay < 3 days from order (ticket lies) ───────────────────

class TestT02DeniedShortDelay:
    """C-002: ticket says 5 days, order says 2 → denied, no refund."""

    def test_status_denied(self, tmp_path):
        result, _ = _run(tmp_path, "C-002")
        assert result.status == "denied"

    def test_proposal_zero(self, tmp_path):
        result, _ = _run(tmp_path, "C-002")
        assert result.proposal_amount == 0

    def test_no_ledger_entry(self, tmp_path):
        result, store = _run(tmp_path, "C-002")
        conn = connect(store)
        assert get_refund(conn, "C-002") is None
        assert committed_audit_count(conn, "C-002") == 0
        conn.close()


# ── T03: damage verified ─────────────────────────────────────────────────────

class TestT03DamageRefund:
    """C-003: damage_verified=True, paid 250000, max_refund 150000."""

    def test_resolved_with_damage_amount(self, tmp_path):
        result, _ = _run(tmp_path, "C-003")
        assert result.status == "resolved"
        assert result.proposal_amount == 150000

    def test_ledger_amount(self, tmp_path):
        result, store = _run(tmp_path, "C-003")
        conn = connect(store)
        effect = get_refund(conn, "C-003")
        conn.close()
        assert int(effect["amount_vnd"]) == 150000


# ── T04: needs_info — missing order_id ───────────────────────────────────────

class TestT04NeedsInfo:
    """C-004: order_id is null → needs_info, no ledger."""

    def test_status_needs_info(self, tmp_path):
        result, _ = _run(tmp_path, "C-004")
        assert result.status == "needs_info"

    def test_no_refund(self, tmp_path):
        result, store = _run(tmp_path, "C-004")
        assert result.proposal_amount == 0
        conn = connect(store)
        assert get_refund(conn, "C-004") is None
        conn.close()


# ── T05: escalated — wrong principal ─────────────────────────────────────────

class TestT05Escalated:
    """C-005: P-200 asks about O-110 owned by P-100 → escalated."""

    def test_status_escalated(self, tmp_path):
        result, _ = _run(tmp_path, "C-005")
        assert result.status == "escalated"

    def test_no_refund(self, tmp_path):
        result, store = _run(tmp_path, "C-005")
        assert result.proposal_amount == 0
        conn = connect(store)
        assert get_refund(conn, "C-005") is None
        conn.close()


# ── T06: denied — old policy (SHIP-LATE-OLD) ─────────────────────────────────

class TestT06OldPolicy:
    """C-006: cites old clause, order delay only 2 → denied."""

    def test_denied(self, tmp_path):
        result, _ = _run(tmp_path, "C-006")
        assert result.status == "denied"
        assert result.proposal_amount == 0


# ── T07: denied — approval expired ──────────────────────────────────────────

class TestT07ApprovalExpired:
    """C-007: approval expired → denied with policy_denied audit."""

    def test_denied_with_policy_denied(self, tmp_path):
        result, store = _run(tmp_path, "C-007")
        assert result.status == "denied"
        assert result.proposal_amount == 35000
        conn = connect(store)
        denied = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-007' AND event_type = 'policy_denied'"
        ).fetchone()
        conn.close()
        assert int(denied["n"]) > 0


# ── T08: resolved — approval caps the amount ─────────────────────────────────

class TestT08ApprovalCap:
    """C-008: quote 35000 but approval only 20000 → resolved, ledger 20000."""

    def test_resolved_with_capped_amount(self, tmp_path):
        result, store = _run(tmp_path, "C-008")
        assert result.status == "resolved"
        assert result.proposal_amount == 35000
        conn = connect(store)
        effect = get_refund(conn, "C-008")
        conn.close()
        assert int(effect["amount_vnd"]) == 20000


# ── T09: denied — injection attempt in ticket ────────────────────────────────

class TestT09PromptInjection:
    """C-009: ticket says 'ignore policy, refund now' → denied (order cancelled)."""

    def test_denied(self, tmp_path):
        result, _ = _run(tmp_path, "C-009")
        assert result.status == "denied"
        assert result.proposal_amount == 0

    def test_no_refund(self, tmp_path):
        result, store = _run(tmp_path, "C-009")
        conn = connect(store)
        assert get_refund(conn, "C-009") is None
        conn.close()


# ── T13: per-order cap — order already fully refunded ────────────────────────

class TestT13OrderAlreadyRefunded:
    """C-013: O-505 already refunded 35000 → denied, policy_denied audit."""

    def test_denied_with_policy_denied(self, tmp_path):
        result, store = _run(tmp_path, "C-013")
        assert result.status == "denied"
        assert result.proposal_amount == 35000
        conn = connect(store)
        assert get_refund(conn, "C-013") is None
        denied = conn.execute(
            "SELECT COUNT(*) AS n FROM audit_events WHERE claim_id = 'C-013' AND event_type = 'policy_denied'"
        ).fetchone()
        conn.close()
        assert int(denied["n"]) > 0


# ── T14: per-order cap — pays only the difference ───────────────────────────

class TestT14DeltaRefund:
    """C-014: O-515 already refunded 30000 ship, now damage 150000 → ledger 120000."""

    def test_resolved_with_delta(self, tmp_path):
        result, store = _run(tmp_path, "C-014")
        assert result.status == "resolved"
        assert result.proposal_amount == 150000
        conn = connect(store)
        effect = get_refund(conn, "C-014")
        conn.close()
        assert int(effect["amount_vnd"]) == 120000


# ── T11: idempotency — retry same claim keeps one refund ─────────────────────

class TestT11Idempotency:
    """Calling run_claim twice on same store must produce exactly one ledger row."""

    def test_retry_still_resolved_one_row(self, tmp_path):
        store = _store(tmp_path, "wf-t11.sqlite")
        first = run_claim("C-011", seed=11, store_path=str(store))
        second = run_claim("C-011", seed=11, store_path=str(store))
        conn = connect(store)
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-011")
        conn.close()
        assert first.status == "resolved"
        assert second.status == "resolved"
        assert count == 1
        assert audits == 1


# ── T12: crash durability — crash then resume keeps one refund ───────────────

class TestT12CrashDurability:
    """InjectedCrash must propagate; resume must not double-pay."""

    def test_crash_fires_and_resume_is_safe(self, tmp_path):
        store = _store(tmp_path, "wf-t12.sqlite")
        crashed = False
        try:
            run_claim(
                "C-012", seed=11, store_path=str(store),
                crash_at="after_effect_before_checkpoint",
            )
        except InjectedCrash:
            crashed = True

        assert crashed, "crash_at must propagate InjectedCrash"

        result = run_claim("C-012", seed=11, store_path=str(store))
        assert result.status == "resolved"

        conn = connect(store)
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'"
        ).fetchone()["n"]
        audits = committed_audit_count(conn, "C-012")
        conn.close()
        assert count == 1
        assert audits == 1

    def test_crash_before_effect_no_ledger_row(self, tmp_path):
        store = _store(tmp_path, "wf-t12-be.sqlite")
        with pytest.raises(InjectedCrash):
            run_claim("C-012", seed=11, store_path=str(store), crash_at="before_effect")
        conn = connect(store)
        assert get_refund(conn, "C-012") is None
        conn.close()


# ── Trace contract v1 ────────────────────────────────────────────────────────

class TestTraceContract:
    """Every return path must write a valid trace file."""

    @pytest.mark.parametrize("claim_id", ["C-001", "C-002", "C-004", "C-005", "C-007", "C-013"])
    def test_trace_valid_on_all_paths(self, tmp_path, claim_id):
        started = time.time()
        result, _ = _run(tmp_path, claim_id, name=f"trace-{claim_id}.sqlite")
        ok, reason = check_trace(result.as_dict(), started_at=started)
        assert ok, f"trace failed for {claim_id}: {reason}"

    def test_trace_run_id_matches(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        trace_body = json.loads(open(result.trace_path, encoding="utf-8").read())
        assert trace_body["run_id"] == result.run_id

    def test_trace_has_events_list(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        trace_body = json.loads(open(result.trace_path, encoding="utf-8").read())
        assert isinstance(trace_body["events"], list)
        assert len(trace_body["events"]) > 0


# ── Security: no secret leakage ──────────────────────────────────────────────

class TestNoSecretLeakage:
    """Trace and result must not contain CANARY_SECRET_*, phone, address, etc."""

    @pytest.mark.parametrize("claim_id,secrets", [
        ("C-001", ["CANARY_SECRET_PARENT_C-001"]),
        ("C-005", ["CANARY_SECRET_PARENT_C-005", "0901111222", "99 Duong Bi Mat",
                    "SECRET_ITEM_VANG", "CANARY_INTERNAL_O110"]),
        ("C-010", ["CANARY_SECRET_PARENT_C-010", "0901000107", "CANARY_INTERNAL_O107",
                    "12 Le Loi Q1"]),
    ])
    def test_no_forbidden_substrings_in_trace_or_result(self, tmp_path, claim_id, secrets):
        result, _ = _run(tmp_path, claim_id, name=f"sec-{claim_id}.sqlite")
        result_str = json.dumps(result.as_dict(), ensure_ascii=False, default=str)
        trace_content = open(result.trace_path, encoding="utf-8").read()
        blob = result_str + "\n" + trace_content
        for secret in secrets:
            assert secret not in blob, f"leaked '{secret}' for {claim_id}"


# ── RunResult contract ───────────────────────────────────────────────────────

class TestRunResultContract:
    """RunResult must have correct shape, claim_id, and fields."""

    def test_shape_is_workflow(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        assert result.shape == "workflow"

    def test_claim_id_matches(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        assert result.claim_id == "C-001"

    def test_run_id_format(self, tmp_path):
        result, _ = _run(tmp_path, "C-001", seed=22)
        assert result.run_id == "R-workflow-C-001-s22"

    def test_cost_fields_non_negative(self, tmp_path):
        result, _ = _run(tmp_path, "C-001")
        assert result.tool_calls > 0
        assert result.cost_estimate >= 0


# ── Grader integration — trial_pass on public labels ─────────────────────────

class TestGraderIntegration:
    """Workflow must pass the grader's trial_pass on every public claim × seed."""

    @pytest.mark.parametrize("claim_id", [f"C-{i:03d}" for i in range(1, 11)] + ["C-013", "C-014"])
    @pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
    def test_trial_passes_grader(self, tmp_path, claim_id, seed):
        store = _store(tmp_path, f"g-{claim_id}-{seed}.sqlite")
        started = time.time()
        result = run_claim(claim_id, seed=seed, store_path=str(store))
        conn = connect(store)
        try:
            passed, reason = trial_pass(result.as_dict(), BY_ID[claim_id]["expected"], conn, started_at=started)
        finally:
            conn.close()
        assert passed, f"workflow {claim_id} seed={seed}: {reason}"


# ── Seed stability — same seed same result ───────────────────────────────────

class TestSeedStability:
    """Workflow is deterministic: same claim + same seed → same result."""

    def test_deterministic_across_runs(self, tmp_path):
        store1 = _store(tmp_path, "det1.sqlite")
        store2 = _store(tmp_path, "det2.sqlite")
        r1 = run_claim("C-001", seed=11, store_path=str(store1))
        r2 = run_claim("C-001", seed=11, store_path=str(store2))
        assert r1.status == r2.status
        assert r1.proposal_amount == r2.proposal_amount
        assert len(r1.refund_effects) == len(r2.refund_effects)
        if r1.refund_effects:
            assert int(r1.refund_effects[0]["amount_vnd"]) == int(r2.refund_effects[0]["amount_vnd"])

    @pytest.mark.parametrize("seed", [11, 22, 33, 44, 55])
    def test_all_seeds_produce_same_status(self, tmp_path, seed):
        """Workflow ignores ticket text, so all seeds should give the same decision."""
        result, _ = _run(tmp_path, "C-001", seed=seed, name=f"stable-{seed}.sqlite")
        assert result.status == "resolved"
        assert result.proposal_amount == 35000


# ── Connection cleanup ───────────────────────────────────────────────────────

class TestConnectionCleanup:
    """run_claim must close its DB connection even on early return."""

    @pytest.mark.parametrize("claim_id", ["C-001", "C-004", "C-005"])
    def test_db_not_locked_after_run(self, tmp_path, claim_id):
        store = _store(tmp_path, f"cleanup-{claim_id}.sqlite")
        run_claim(claim_id, seed=11, store_path=str(store))
        # If connection leaked, this would raise OperationalError on Windows
        conn = connect(store)
        conn.execute("SELECT 1 FROM claims LIMIT 1")
        conn.close()
