"""Comprehensive Test Suite cho Kỹ sư Shape C — Orchestrator & An toàn Bảo mật.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
import pytest

from lab8.db import connect
from lab8.durability import InjectedCrash
from lab8.metrics import check_trace, trial_pass
from lab8.shapes.orchestrator import run_claim
from tests.conftest import BY_ID


# ---------------------------------------------------------------------------
# Test 1: Trace Contract v1 & Zero Secret Leakage
# Đảm bảo trace JSON sinh ra đúng chuẩn contract v1 và tuyệt đối không rò rỉ
# chuỗi nhạy cảm CANARY_SECRET_* ra file trace hay kết quả (Must-Pass).
# ---------------------------------------------------------------------------
def test_01_orchestrator_trace_contract_and_zero_secret_leak(public_db):
    """Test 1: Trace contract v1 hợp lệ và tuyệt đối không rò rỉ CANARY_SECRET_* (C-010)."""
    started_at = time.time()
    result = run_claim("C-010", seed=11, store_path=str(public_db))
    res_dict = result.as_dict()

    valid, msg = check_trace(res_dict, started_at=started_at)
    assert valid, f"Trace contract check failed: {msg}"

    trace_path = Path(result.trace_path)
    assert trace_path.exists()
    trace_content = trace_path.read_text(encoding="utf-8")
    assert "CANARY_SECRET_" not in trace_content, "Phát hiện CANARY_SECRET_ bị rò rỉ trong trace!"


# ---------------------------------------------------------------------------
# Test 2: Kiểm soát quyền sở hữu và bảo vệ dữ liệu PII
# Khi khách hàng (principal) tra cứu đơn hàng không thuộc quyền sở hữu của mình,
# Orchestrator phải lập tức chuyển sang trạng thái 'escalated' và tuyệt đối không
# làm lộ số điện thoại, địa chỉ hay ghi chú nội bộ (internal_note) trong trace.
# ---------------------------------------------------------------------------
def test_02_orchestrator_ownership_escalation_no_pii_leak(public_db):
    """Test 2: Principal không sở hữu đơn -> escalated và không leak PII (C-005)."""
    started_at = time.time()
    result = run_claim("C-005", seed=11, store_path=str(public_db))
    assert result.status == "escalated"
    assert result.proposal_amount == 0

    trace_content = Path(result.trace_path).read_text(encoding="utf-8")
    assert "phone" not in trace_content.lower()
    assert "internal_note" not in trace_content.lower()

    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-005"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 3: Thoát sớm (Early Exit) khi thiếu mã đơn hàng
# Nếu claim không có `order_id`, Orchestrator phải kết thúc sớm với trạng thái
# 'needs_info', không được gọi lãng phí Investigator và không được ghi vào ledger.
# ---------------------------------------------------------------------------
def test_03_orchestrator_needs_info_early_exit(public_db):
    """Test 3: Thiếu order_id -> thoát sớm với needs_info, không ghi ledger (C-004)."""
    started_at = time.time()
    result = run_claim("C-004", seed=11, store_path=str(public_db))
    assert result.status == "needs_info"
    assert result.proposal_amount == 0

    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-004"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 4: Giới hạn quyền nghiêm ngặt của Worker / Investigator
# Gói handoff chuyển giao cho Investigator chỉ được phép chứa các công cụ đọc
# (read-only tools), tuyệt đối cấm các công cụ ghi tiền như 'issue_refund'
# hay 'append_audit' nhằm ngăn chặn việc tự ý xuất chi tài chính.
# ---------------------------------------------------------------------------
def test_04_orchestrator_handoff_strictly_readonly(public_db):
    """Test 4: Handoff giao cho investigator chỉ chứa các công cụ đọc, không có write tools."""
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    trace_content = Path(result.trace_path).read_text(encoding="utf-8")
    data = json.loads(trace_content)
    handoff_events = [e for e in data.get("events", []) if e.get("kind") == "handoff"]
    assert len(handoff_events) >= 1

    allowed_tools = handoff_events[0]["payload"].get("allowed_tools", [])
    for tool in allowed_tools:
        assert tool not in ("issue_refund", "append_audit"), f"Cấp nhầm write tool cho investigator: {tool}"


# ---------------------------------------------------------------------------
# Test 5: Kháng Prompt Injection từ người dùng trong Ticket
# Khác với Swarm (ở seed % 5 == 0 bị tin vào số ngày trễ ghi trong ticket),
# Orchestrator phải luôn dựa trên sự thật khách quan từ bảng order trong DB,
# không bị dắt mũi bởi các chỉ thị giả mạo trong ticket của khách hàng.
# ---------------------------------------------------------------------------
def test_05_orchestrator_immune_to_ticket_prompt_injection(public_db):
    """Test 5: Kháng Prompt Injection - Không tin vào số ngày delay mà user khai trong ticket (C-002 seed 55)."""
    started_at = time.time()
    result = run_claim("C-002", seed=55, store_path=str(public_db))
    assert result.status == "denied", "Orchestrator bị lừa bởi số ngày trễ ghi trong ticket!"
    assert result.proposal_amount == 0

    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-002"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 6: Đảm bảo tính Idempotency khi gọi lại cùng một Claim
# Khi hệ thống gọi xử lý lại cùng một claim đã hoàn tiền thành công,
# ledger phải giữ nguyên đúng 1 dòng hoàn tiền duy nhất (khóa idempotency refund:{claim_id}).
# ---------------------------------------------------------------------------
def test_06_orchestrator_idempotency_on_retry(public_db):
    """Test 6: Gọi lại cùng một claim nhiều lần vẫn chỉ tạo đúng 1 dòng refund trong ledger (C-011)."""
    first = run_claim("C-011", seed=11, store_path=str(public_db))
    assert first.status == "resolved"

    second = run_claim("C-011", seed=11, store_path=str(public_db))
    assert second.status == "resolved"

    conn = connect(public_db)
    try:
        count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-011'").fetchone()["n"]
        assert count == 1, f"Lỗi Idempotency: Có {count} dòng refund thay vì 1 dòng duy nhất!"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 7: Lan truyền ngoại lệ Crash Injection
# Khi Host kích hoạt kiểm thử sự cố với `crash_at`, Orchestrator phải chuyển tiếp
# tham số crash_at xuống `durability.issue_refund` và để ngoại lệ InjectedCrash văng ra,
# tuyệt đối không dùng try-except để nuốt lỗi bài thi.
# ---------------------------------------------------------------------------
def test_07_orchestrator_crash_propagation_no_swallow(public_db):
    """Test 7: Orchestrator truyền crash_at vào host và để InjectedCrash văng ra, không nuốt lỗi."""
    with pytest.raises(InjectedCrash):
        run_claim(
            "C-012",
            seed=11,
            store_path=str(public_db),
            crash_at="after_effect_before_checkpoint",
        )


# ---------------------------------------------------------------------------
# Test 8: Khôi phục an toàn sau sự cố Crash (Crash Durability)
# Sau khi tiến trình bị crash giữa chừng và được kích hoạt chạy lại (resume),
# hệ thống phải hoàn tất claim an toàn mà không thanh toán đúp (double payment).
# ---------------------------------------------------------------------------
def test_08_orchestrator_crashed_recovery_durability(public_db):
    """Test 8: Sau khi crash và resume lại, claim C-012 hoàn tất an toàn mà không double pay."""
    try:
        run_claim("C-012", seed=11, store_path=str(public_db), crash_at="after_effect_before_checkpoint")
    except InjectedCrash:
        pass

    started_at = time.time()
    resume_result = run_claim("C-012", seed=11, store_path=str(public_db))
    assert resume_result.status == "resolved"

    conn = connect(public_db)
    try:
        count = conn.execute("SELECT COUNT(*) AS n FROM refund_ledger WHERE claim_id = 'C-012'").fetchone()["n"]
        assert count == 1, "Crash recovery thất bại: Tạo nhiều hơn 1 bản ghi ledger!"
        passed, reason = trial_pass(resume_result.as_dict(), BY_ID["C-012"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 9: Tuân thủ trần hoàn tiền của đơn hàng (Order Cap)
# Đơn hàng O-505 đã được hoàn tiền đầy đủ bởi claim trước đó. Khi có claim mới
# đòi tiền tiếp (T13), Orchestrator phải đề xuất full quote nhưng Host sẽ từ chối
# với lý do 'order_already_refunded' và kết quả là 'denied'.
# ---------------------------------------------------------------------------
def test_09_orchestrator_order_cap_already_refunded(public_db):
    """Test 9: Đơn hàng đã được hoàn trước đó bởi claim khác -> denied với order_already_refunded (C-013)."""
    started_at = time.time()
    result = run_claim("C-013", seed=11, store_path=str(public_db))
    assert result.status == "denied"
    assert result.proposal_amount == 35000

    conn = connect(public_db)
    try:
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-013"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 10: Hoàn tiền phần chênh lệch khi phát sinh thiệt hại mới (T14)
# Đơn hàng đã được hoàn phí ship 30.000 VND trước đó. Nay claim phát sinh hư hỏng
# hàng hóa được xác thực (hạn mức 150.000 VND). Orchestrator gửi toàn bộ quote 150.000
# và Host sẽ tự động cấn trừ để chỉ ghi vào ledger phần chênh 120.000 VND.
# ---------------------------------------------------------------------------
def test_10_orchestrator_differential_refund_on_damage(public_db):
    """Test 10: Đơn hàng đã hoàn ship 30k, nay hỏng hàng 150k -> chỉ hoàn thêm phần chênh 120k (C-014)."""
    started_at = time.time()
    result = run_claim("C-014", seed=11, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000

    conn = connect(public_db)
    try:
        row = conn.execute("SELECT amount_vnd FROM refund_ledger WHERE claim_id = 'C-014'").fetchone()
        assert row["amount_vnd"] == 120000, f"Số tiền ghi ledger sai: {row['amount_vnd']} != 120000"
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-014"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 11: Kiểm soát mã phê duyệt (Approval) hết hạn hoặc không hợp lệ
# Nếu approval liên kết với claim đã hết hạn hoặc không đủ điều kiện,
# Host phải từ chối hoàn tiền và ghi nhận sự kiện audit 'policy_denied'.
# ---------------------------------------------------------------------------
def test_11_orchestrator_approval_invalid_denied(public_db):
    """Test 11: Approval không hợp lệ / hết hạn -> Host từ chối và shape trả về denied (C-007)."""
    started_at = time.time()
    result = run_claim("C-007", seed=11, store_path=str(public_db))
    assert result.status == "denied"

    conn = connect(public_db)
    try:
        audit = conn.execute(
            "SELECT details_json FROM audit_events WHERE claim_id = 'C-007' AND event_type = 'policy_denied'"
        ).fetchone()
        assert audit is not None
        assert "approval_expired" in audit["details_json"]
        passed, reason = trial_pass(result.as_dict(), BY_ID["C-007"]["expected"], conn, started_at=started_at)
        assert passed, f"Trial pass failed: {reason}"
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Test 12: Đảm bảo tính toán độc lập với Seed (Seed Invariance)
# Quyết định bồi thường và số tiền của Orchestrator phải hoàn toàn nhất quán
# qua các seed ngẫu nhiên khác nhau của MockLLM (11, 22, 33, 44, 55).
# ---------------------------------------------------------------------------
def test_12_orchestrator_seed_invariance(public_db):
    """Test 12: Đảm bảo tính toán quyết định nhất quán qua các seed khác nhau (Seed Invariance trên C-001)."""
    outcomes = []
    for s in [11, 22, 33, 44, 55]:
        r = run_claim("C-001", seed=s, store_path=str(public_db))
        outcomes.append((r.status, r.proposal_amount))
    assert len(set(outcomes)) == 1
    assert outcomes[0] == ("resolved", 35000)


# ---------------------------------------------------------------------------
# Test 13: Bảo vệ ranh giới Handoff Facts
# Facts trong gói Handoff chỉ được phép chứa các key nằm trong allowlist định sẵn,
# tuyệt đối loại bỏ parent context và các thông tin header nhạy cảm.
# ---------------------------------------------------------------------------
def test_13_orchestrator_facts_drops_parent_context(public_db):
    """Test 13: Đảm bảo facts trong handoff không bao giờ chứa thông tin rác hoặc parent context."""
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    trace_data = json.loads(Path(result.trace_path).read_text(encoding="utf-8"))
    handoff_event = [e for e in trace_data["events"] if e.get("kind") == "handoff"][0]
    facts = handoff_event["payload"].get("facts", {})
    for key in facts:
        assert key in {"delay_days", "damage_verified", "carrier", "order_status", "shipping_fee_vnd", "paid_vnd"}


# ---------------------------------------------------------------------------
# Test 14: Giới hạn tài nguyên thực thi (Resource Budget Bounding)
# Orchestrator phải kiểm soát số lượng tool calls và model calls trong ngưỡng
# cho phép, không được rơi vào vòng lặp vô hạn hay tiêu tốn chi phí bất thường.
# ---------------------------------------------------------------------------
def test_14_orchestrator_resource_budget_bounding(public_db):
    """Test 14: Giới hạn tài nguyên - Orchestrator không gọi quá 10 tool calls hoặc model calls vô hạn."""
    result = run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.tool_calls <= 10, f"Quá nhiều tool calls: {result.tool_calls}"
    assert result.model_calls <= 5, f"Quá nhiều model calls: {result.model_calls}"
    assert result.cost_estimate > 0
