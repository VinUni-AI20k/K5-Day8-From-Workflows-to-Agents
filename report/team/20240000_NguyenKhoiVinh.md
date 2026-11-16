# Báo cáo cá nhân — 20240000_NguyenKhoiVinh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Khởi Vinh
- MSSV: 20240000 (Vui lòng cập nhật MSSV chính xác của bạn)
- Email: vinh.nk.2753@gmail.com
- GitHub: vinhnk2753-blip

## 2. Phần việc phụ trách

- Cài đặt và tích hợp các Shape xử lý claim: Shape A (Workflow), Shape B (Single Agent ReAct), Shape C (Orchestrator).
- Đảm bảo tính Idempotency, crash-safety và tuân thủ các quy tắc nghiệp vụ LogiX-VN.
- Xây dựng bộ test kỹ thuật cá nhân kiểm thử Idempotency và Policy denial.

## 3. Đóng góp cụ thể

- Hoàn thiện code cho 3 shape tại `src/lab8/shapes/workflow.py`, `single.py`, `orchestrator.py`:
  - Giữ nguyên hợp đồng chữ ký `run_claim`.
  - Đảm bảo tiền được tính bằng code (`compute_compensation`), không do model quyết định.
  - Chuyển `crash_at` vào `durability.issue_refund` và flush trace trước khi re-raise `InjectedCrash`.
  - Tách bạch ranh giới dữ liệu và bảo mật PII/secret (chỉ sử dụng tool đọc cho investigator/worker, sanitize handoff).
- Viết test kỹ thuật độc lập tại `src/tests/test_individual_vinhnk.py` kiểm chứng:
  - Idempotency khi gọi lại cùng claim nhiều lần không phát sinh dòng ledger mới.
  - Claim có entitlement bằng 0 (trễ < 3 ngày) bị từ chối và không ghi ledger.
- Chạy benchmark 4 shape x 14 claim x 5 seed và kiểm thử độ an toàn crash đạt 20/20.

## 4. Bằng chứng

- Bộ test cá nhân: `src/tests/test_individual_vinhnk.py` (6/6 tests passed).
- Ma trận test học viên: `pytest -q -m student -o addopts=` đạt 248/248 passed.
- Crash test suite: `reports/crash.json` đạt `crash_safety: 20/20`.
- Benchmark report: `reports/benchmark.json` (workflow, single, orchestrator đạt pass rate 1.000, pass^5 1.000).

## 5. Công cụ AI đã dùng

- Antigravity AI Assistant: Hỗ trợ rà soát hợp đồng `contracts.md`, dựng mã nguồn 3 shape tuân thủ chuẩn ReAct / Handoff / Durability, và viết test case kiểm tra biên.
- Tự kiểm tra: Chạy kiểm thử pytest độc lập, đối chiếu trực tiếp với database SQLite, chạy crash test suite 20 lần và benchmark toàn diện trước khi xác nhận.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các yêu cầu cá nhân và các tiêu chí kỹ thuật C1, C3, C4, C5, C8 theo Rubric.
