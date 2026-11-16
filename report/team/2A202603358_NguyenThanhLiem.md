# Báo cáo cá nhân — 2A202603358_NguyenThanhLiem

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thanh Liêm
- MSSV: 2A202603358
- Email: liemt0165@gmail.com
- GitHub: Liemt0165

## 2. Phần việc phụ trách

Vai trò: `ledger + evaluation`.
- Kiểm soát tính toàn vẹn dữ liệu ghi Ledger SQLite, khóa Idempotency (`refund:{claim_id}`) và cơ chế phục hồi sau Crash (Crash Recovery).
- Phụ trách chạy Crash Suite (`reports/crash.json`), đảm bảo 3 điều kiện Must-Pass (Crash safety 20/20, approval bypass = 0, secret leak = 0).
- Chạy Benchmark đối chuẩn 4 Shape qua 5 Seed (`reports/benchmark.json`), tổng hợp số liệu, phân tích phương sai và chi phí.
- Chịu trách nhiệm chính cho các file báo cáo: `report/team/decision_adr.md` và `report/team/research_card.md`.

## 3. Đóng góp cụ thể

- Commit chính (hash): 64d4366
- Test đã thêm: test_client_retry_after_unacknowledged_checkpoint_crash_replays_safely (trong src/tests/test_refund_idempotency.py)
- Quyết định kỹ thuật: Khẳng định tính an toàn giao dịch của SQLite Ledger kết hợp khóa Idempotency vượt trội hơn cơ chế checkpoint đơn lẻ; lựa chọn Shape A (Workflow) làm kiến trúc tối ưu theo nguyên lý "ít tự chủ nhất nhưng làm được việc".

## 4. Bằng chứng

- Crash safety: `20/20` tại `src/reports/crash.json`.
- Benchmark report: `src/reports/benchmark.json`.
- Kiểm tra hợp lệ: `python -m lab8.check_submission` ra `0 FAIL`.

## 5. Công cụ AI đã dùng

- Công cụ: Antigravity Assistant.
- Mục đích: Giải thích các luật nghiệp vụ LogiX-VN, cấu trúc 4 kiến trúc và gợi ý viết test case kiểm tra biên cho Ledger/Durability.
- Tự kiểm tra: Toàn bộ test case và script chạy qua pytest và bộ kiểm tra `check_submission` độc lập của repo.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các nhiệm vụ được giao về kiểm thử Ledger, đánh giá Benchmark và hoàn thiện hồ sơ nộp bài của nhóm.
