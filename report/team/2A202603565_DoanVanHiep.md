# Báo cáo cá nhân — 2A202603565_DoanVanHiep

## 1. Thông tin thành viên

- Họ tên: Đoàn Văn Hiệp
- MSSV: 2A202603565
- Email: hiep24042002@gmail.com
- GitHub: https://github.com/hiep0405

## 2. Phần việc phụ trách

- **Kiến trúc Shape C — Orchestrator**: Phụ trách thiết kế và triển khai shape Orchestrator kết hợp với Read-only Investigators theo đúng chuẩn bài toán LogiX-VN.
- **Hợp đồng Handoff v1 & Khử nhạy cảm (Sanitization)**: Đảm bảo gói `handoff.v1` chuyển cho investigator chỉ chứa các trường trong allowlist; không chuyển `parent_secret`, headers, thông tin bảo mật hay ticket thô của khách hàng.
- **Trace Contract v1**: Thiết lập hệ thống ghi trace cho toàn bộ các nhánh rẽ (kể cả early return `needs_info`, `escalated`, `failed`), loại bỏ hoàn toàn các thông tin PII và `CANARY_SECRET_*`.
- **An toàn sự cố và tính lũy kế (Durability & Crash Safety)**: Xử lý `crash_at` trực tiếp xuống `durability.issue_refund`, không bắt `InjectedCrash` để bảo đảm tính nguyên tử và chống trùng lặp hoàn tiền (idempotency).

## 3. Đóng góp cụ thể

- **Triển khai `src/lab8/shapes/orchestrator.py`**:
  - Dùng `make_handoff` với danh sách tool chỉ đọc: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`.
  - Gọi `run_readonly_investigators` với quyền chỉ đọc.
  - Tách bạch ranh giới: chỉ Orchestrator (chạy trên host) mới được quyền gọi `durability.issue_refund` với đầy đủ số tiền quote (để host tự trừ phần hoàn tiền trước đó trên đơn hàng).
  - Truyền thẳng tham số `crash_at` vào host refund method, không nuốt `InjectedCrash`.
- **Viết bộ kiểm thử `src/tests/test_orchestrator_handoff_trace.py`**:
  - `test_orchestrator_handoff_and_trace_are_allowlisted`: Kiểm tra tính toàn vẹn của handoff contract, khẳng định chỉ có `READONLY_TOOLS`, không có `WRITE_TOOLS`, không rò rỉ secret / PII và canary token.
  - `test_orchestrator_writes_a_valid_trace_for_early_returns`: Đảm bảo các trường hợp claim thiếu thông tin hoặc không tồn tại vẫn sinh trace JSON hợp lệ theo Trace Contract v1.
- **Đồng biên soạn báo cáo nhóm (`report/team/group_report.md`)**:
  - Tổng hợp số liệu so sánh giữa 4 kiến trúc và làm rõ ranh giới kiến trúc của Orchestrator.

## 4. Bằng chứng

- **Commit**: `6b386ed`
- **Bộ kiểm thử tự động**:
  - Kiểm thử máy chủ (Host tests): `python -m pytest -q` đạt `63/63 passed`.
  - Kiểm thử sinh viên (Student tests): `python -m pytest -q -m student -o addopts=` đạt `248/248 passed` (trong đó 62 test case dành riêng cho shape Orchestrator đều vượt qua 100%).
- **Kiểm định bài nộp**: `python -m lab8.check_submission` xác nhận `shape orchestrator` format đúng và vượt qua 12/12 claim public ở seed 11.
- **Bảo mật và chống rò rỉ**: `secret_leak_count = 0`, `pii_leak_count = 0`, `approval_bypass_count = 0` trên toàn bộ tập dữ liệu public.
- **Crash Safety**: Đạt `20/20` qua `src/reports/crash.json`.
- **Run ID dẫn chứng**: `R-orchestrator-C-001-s11`.

## 5. Công cụ AI đã dùng

- **Công cụ**: Trợ lý AI (Antigravity / Gemini) được sử dụng để hỗ trợ rà soát mã nguồn, chuẩn hóa các ràng buộc của Trace Contract v1, hỗ trợ sinh khung test case cho allowlist handoff.
- **Phương pháp tự kiểm tra**:
  - Tuân thủ quy định: Không để AI bịa đặt số liệu hay tự tiện chỉnh sửa file thước đo.
  - Chạy thực nghiệm độc lập toàn bộ các lệnh kiểm thử trên môi trường Python 3.13 nội bộ (`pytest`, `smoke`, `check_submission`).
  - Đối chiếu từng sự kiện trong trace JSON đầu ra với quy định tại `docs/contracts.md`.

## 6. Tự đánh giá

- **Mức độ hoàn thành**: 100% các tiêu chí yêu cầu cho Shape C (Orchestrator).
- **Đáp ứng các điều kiện Must-Pass**: Đảm bảo không bypass approval, không lộ canary secret, và an toàn tuyệt đối khi xảy ra crash.
