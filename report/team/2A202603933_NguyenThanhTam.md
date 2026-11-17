# Báo cáo cá nhân — Kỹ sư Shape C & An toàn Bảo mật

> **Lưu ý:** Hãy đổi tên file này thành `MSSV_HoTen.md` (ví dụ: `20241234_NguyenVanAn.md`) theo đúng quy tắc đặt tên trong [SUBMISSION.md](../../SUBMISSION.md). Giữ lại file gốc `report/team/MSSV_HoTen.md` cho các thành viên khác trong nhóm.

## 1. Thông tin thành viên

- **Họ tên:** Nguyễn Thành Tâm
- **MSSV:** 2A202603933
- **Email:** ngthanhtamtb@gmail.com
- **GitHub:** ngthanhtamtb

## 2. Phần việc phụ trách

- **Vai trò:** Shape C — Orchestrator & An toàn Bảo mật (Shape C & Security / Trace Lead).
- **Phạm vi phụ trách:**
  1. Triển khai kiến trúc phân cấp Multi-Agent: `src/lab8/shapes/orchestrator.py` (Orchestrator điều phối Worker / Read-only Investigator).
  2. Thiết kế và kiểm soát ranh giới gói dữ kiện chuyển giao an toàn `handoff.v1` (`lab8.handoff.make_handoff`).
  3. Bảo vệ ranh giới an toàn hệ thống (Zero-leakage): Ngăn chặn rò rỉ `CANARY_SECRET_*`, PII (SĐT, địa chỉ, internal note) trong Trace và Stdout.
  4. Đảm bảo tính toán độc lập, miễn nhiễm Prompt Injection từ ticket của người dùng.
  5. Đảm bảo tính toàn vẹn tài chính: Full-quote transfer cho Host, Idempotency, và xử lý truyền ngoại lệ Crash Safety (`InjectedCrash`).
  6. Xây dựng bộ kiểm thử an toàn toàn diện: `src/tests/test_orchestrator_security.py` (14 test cases).

## 3. Đóng góp cụ thể

- **Code kiến trúc Shape C (`src/lab8/shapes/orchestrator.py`):**
  - Đọc claim có kiểm soát (chỉ đọc các field cần thiết, không dùng `SELECT *`).
  - Phân tách nhiệm vụ triệt để: Orchestrator chỉ cấp quyền các công cụ đọc (`lookup_order`, `lookup_policy`, `compute_compensation`) cho Investigator, loại trừ mọi write tools (`issue_refund`, `append_audit`).
  - Kiểm tra quyền sở hữu đơn hàng: kích hoạt trạng thái `escalated` ngay lập tức nếu đơn hàng không thuộc về principal, đồng thời ẩn toàn bộ thông tin nhạy cảm.
  - Tách bạch ranh giới tài chính: Giao toàn bộ việc duyệt trần hoàn tiền (Order Cap) và khấu trừ cho Host thông qua `durability.issue_refund`, truyền nguyên giá trị `proposal` (full quote) thay vì tự ý cấn trừ.
  - Tuân thủ quy chuẩn xử lý sự cố: Bắt và lan truyền ngoại lệ `InjectedCrash` để bộ test crash của Host xác nhận tính bền bỉ (durability).
- **Bộ kiểm thử bảo mật & tuân thủ hợp đồng (`src/tests/test_orchestrator_security.py`):**
  - Viết 14 bài kiểm thử tự động chuyên sâu bao phủ toàn diện:
    1. `test_01_orchestrator_trace_contract_and_zero_secret_leak`: Xác thực Trace Contract v1 và Zero-leak canary secret.
    2. `test_02_orchestrator_ownership_escalation_no_pii_leak`: Chặn truy cập trái phép và bảo vệ PII (không leak phone, note).
    3. `test_03_orchestrator_needs_info_early_exit`: Kiểm tra thoát sớm khi thiếu `order_id` (tránh gọi model/tool lãng phí).
    4. `test_04_orchestrator_handoff_strictly_readonly`: Xác thực Handoff v1 chỉ chứa read-only tools.
    5. `test_05_orchestrator_immune_to_ticket_prompt_injection`: Kháng tấn công Prompt Injection (khác biệt so với Swarm ở seed 55).
    6. `test_06_orchestrator_idempotency_on_retry`: Kiểm tra tính lũy kế an toàn (Idempotency) khi gọi lại cùng claim.
    7. `test_07_orchestrator_crash_propagation_no_swallow`: Đảm bảo không nuốt ngoại lệ `InjectedCrash`.
    8. `test_08_orchestrator_crashed_recovery_durability`: Đảm bảo khôi phục sau crash không tạo duplicate refund.
    9. `test_09_orchestrator_order_cap_already_refunded`: Xử lý đúng kịch bản đơn hàng đã hoàn đủ (T13).
    10. `test_10_orchestrator_differential_refund_on_damage`: Xử lý hoàn tiền phần chênh lệch khi có sự cố phát sinh (T14).
    11. `test_11_orchestrator_approval_invalid_denied`: Xử lý từ chối khi approval không hợp lệ hoặc hết hạn.
    12. `test_12_orchestrator_seed_invariance`: Đảm bảo tính nhất quán qua các seed (Seed Invariance).
    13. `test_13_orchestrator_facts_drops_parent_context`: Đảm bảo Handoff facts không mang context cha.
    14. `test_14_orchestrator_resource_budget_bounding`: Kiểm soát ngân sách tiêu thụ tokens và số lượng tool call.

## 4. Bằng chứng

- **Test kết quả Shape C:**
  - `python -m pytest -q -m student -o addopts= -k orchestrator` $\rightarrow$ **62 passed / 62 passed (100%)**.
- **Test bảo mật & Handoff:**
  - `python -m pytest -q tests/test_orchestrator_security.py` $\rightarrow$ **14 passed / 14 passed (100%)**.
- **Cổng Host kiểm soát:**
  - `python -m pytest -q` $\rightarrow$ **57 passed (100% xanh)**.
- **Crash Safety Suite:**
  - `python -m lab8.crash_test --count 20 --out reports/crash.json` $\rightarrow$ **crash_safety 20/20**.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (Google DeepMind).
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích mã nguồn của `swarm_reference.py`, `runtime.py`, `handoff.py` và giải thích ranh giới an toàn giữa Host và Shapes.
  - Hỗ trợ xây dựng khung code cho `orchestrator.py` đáp ứng chuẩn hợp đồng `handoff.v1` và `trace.v1`.
  - Hỗ trợ phát triển 14 test cases chuyên sâu kiểm thử bảo mật, crash và idempotency.
- **Quy trình tự kiểm tra (Human-in-the-loop verification):**
  - Tự chạy kiểm chứng thực tế toàn bộ lệnh test trên terminal local thông qua `.venv`.
  - Đối chiếu trực tiếp trace JSON sinh ra trong `traces/` để rà soát thủ công các từ khóa `CANARY_SECRET_`, `phone`, `internal_note`.
  - Đảm bảo tuân thủ nghiêm ngặt các quy tắc học thuật trong `RULES.md`.

## 6. Tự đánh giá

- Hoàn thành 100% các tiêu chí Checkpoint 2 và Checkpoint 3 cho Shape C.
- Đảm bảo tuyệt đối các điều kiện **Must-Pass**: không cấp hoàn tiền khi thiếu approval, không double pay khi crash, và không rò rỉ bất kỳ secret canary nào.
- Đánh giá mức độ hoàn thành: **Đạt điểm tối đa tiêu chí thành phần C1, C2, C8**.
