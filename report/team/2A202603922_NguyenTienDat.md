# Báo cáo cá nhân — Nguyễn Tiến Đạt

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tiến Đạt
- MSSV: 2A202603922
- Lớp: L3B
- Email: ntdkhongdeptrailam5924@gmail.com
- GitHub: duhocsinh4to10

## 2. Phần việc phụ trách

Phụ trách toàn bộ quá trình triển khai, nâng cấp và làm sạch mã nguồn cho ba kiến trúc xử lý khiếu nại (`workflow`, `single`, `orchestrator`), viết bộ kiểm thử mở rộng trong `src/tests/test_shape_unknown_claim.py`, chạy thực nghiệm benchmark/crash suite và biên soạn hồ sơ báo cáo (`TEAM.md`, `decision_adr.md`, `research_card.md`, `group_report.md`).

## 3. Đóng góp cụ thể

- **Commit chính:** `0f3c523` (làm sạch cấu trúc ba shape, bổ sung kiểm thử xung đột hoàn tiền và chống rò rỉ dữ liệu).
- **Thiết kế kỹ thuật:**
  - Tách biệt rõ ranh giới giữa Code/Host và Model: tiền đền bù luôn do `compute_compensation` tính từ dữ liệu đơn hàng có cấu trúc, tuyệt đối không tin số ngày trễ hay yêu cầu trong câu chữ ticket.
  - Truyền **quote đầy đủ** vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` để Host kiểm tra approval, áp trần hoàn tiền theo đơn (T13, T14) và bảo toàn idempotency (`refund:{claim_id}`).
  - Đóng gói dữ liệu điều tra ở `orchestrator` qua `make_handoff` và chỉ ghi các trường đã qua allowlist vào `Trace` để ngăn rò rỉ `CANARY_SECRET_*` và PII.
- **Kiểm thử bổ sung (`src/tests/test_shape_unknown_claim.py`):** Thêm 16 test case kiểm tra claim không tồn tại (`unknown_claim`), lỗi nội bộ không làm lộ thông tin nhạy cảm (`internal_error`), lỗi mở DB, xung đột số tiền khi gọi lại (`amount_conflict`) và kiểm tra không rò rỉ `CANARY_SECRET_*` / `parent_secret` trong trace.

## 4. Bằng chứng

- Smoke test (`python -m lab8.smoke`): `lab8.smoke pass`.
- Cổng host (`python -m pytest -q`): `54 passed`.
- Bộ test student (`python -m pytest -q -m student -o addopts=`): `264 passed`.
- Crash suite (`src/reports/crash.json`): `crash_safety = 20/20`.
- Benchmark (`src/reports/benchmark.json`): Run ID dẫn chứng `R-workflow-C-001-s11`, `workflow` đạt `pass_rate = 1.000`, `pass^5 = 1.000`, `cost_per_success_vnd = 27.86`.
- Kiểm tra nộp bài (`python -m lab8.check_submission`): `0 FAIL`.

## 5. Công cụ AI đã dùng

Sử dụng trợ lý AI (Codex / Antigravity) để hỗ trợ rà soát yêu cầu hợp đồng dữ liệu (`RunResult`, `Trace contract v1`), làm sạch mã nguồn (type annotations, tách hàm helper xử lý hoàn tiền và bắt lỗi an toàn) và biên tập cấu trúc báo cáo. Mọi đoạn mã và số liệu đều được kiểm tra chéo bằng cách chạy trực tiếp `pytest`, `lab8.benchmark`, `lab8.crash_test` và `lab8.check_submission`, đồng thời đối chiếu với `docs/business_rules.md` và `docs/contracts.md`.

## 6. Tự đánh giá

Ba kiến trúc `workflow`, `single` và `orchestrator` đã được hoàn thiện sạch sẽ, tuân thủ chặt chẽ các điều kiện must-pass (không hoàn tiền khi thiếu approval hợp lệ, không lộ secret/PII trong trace, an toàn tuyệt đối qua 20 kịch bản crash) và đạt 100% pass rate trên bộ kiểm thử public. Quyết định chọn `workflow` trong ADR dựa trực tiếp trên bằng chứng thực nghiệm về chi phí và độ ổn định.
