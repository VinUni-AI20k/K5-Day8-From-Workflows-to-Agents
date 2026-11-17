# Báo cáo cá nhân — Nguyễn Năng Thịnh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Năng Thịnh
- MSSV: 2A202604028
- Email: thinh010705@gmail.com
- GitHub: [Thinh010705](https://github.com/Thinh010705)

## 2. Phần việc phụ trách

Tôi phụ trách Shape C — `orchestrator` và phần `handoff` giữa orchestrator với investigator.

Phạm vi công việc gồm:

- Implement `src/lab8/shapes/orchestrator.py`.
- Tạo handoff bằng `make_handoff()` với allowlist rõ ràng.
- Giới hạn investigator ở các read-only tools.
- Tính quote từ order view và truyền quote đầy đủ cho host.
- Truyền `crash_at` vào `issue_refund()` và giữ đúng cơ chế crash/resume.
- Đảm bảo trace không chứa secret hoặc dữ liệu cá nhân.

## 3. Đóng góp cụ thể

- Thay thế stub `not_implemented` trong `orchestrator.py` bằng luồng xử lý claim hoàn chỉnh.
- Xử lý các nhánh `failed`, `needs_info`, `escalated`, `denied` và `resolved`.
- Dùng `get_claim_view()` thay vì truyền nguyên claim row sang investigator.
- Tạo handoff chỉ cấp các tool:
  - `lookup_order`
  - `lookup_policy`
  - `compute_compensation`
- Không truyền `parent_secret`, raw headers hoặc dữ liệu order nhạy cảm vào handoff và trace.
- Gọi `issue_refund()` bằng quote đầy đủ để host tự kiểm approval, idempotency và trần refund theo order.
- Thêm test `src/tests/test_orchestrator_security.py` để kiểm tra trace không lộ secret, `parent_secret` và `raw_headers`.
- Commit chính: sẽ bổ sung sau khi commit code và test lên branch nhóm.

## 4. Bằng chứng

- File triển khai: `src/lab8/shapes/orchestrator.py`.
- Test cá nhân: `src/tests/test_orchestrator_security.py`.
- Run id kiểm tra thành công: `R-orchestrator-C-001-s11`.
- Run id kiểm tra crash/resume: `R-orchestrator-C-012-s11`.
- Kết quả test shape: `62 passed` với `-k orchestrator`.
- Kết quả host test: `55 passed, 248 deselected`.
- Kết quả crash suite: `crash_safety 20/20`.
- Trace kiểm tra: `src/traces/R-orchestrator-C-001-s11.json`.
- Trace crash/resume: `src/traces/R-orchestrator-C-012-s11.json`.

Kết quả crash/resume cho thấy sau crash tại `after_effect_before_checkpoint`, lần chạy lại vẫn chỉ có một dòng refund, một audit `refund_committed` và một checkpoint.

## 5. Công cụ AI đã dùng

- ChatGPT/Codex: dùng để đọc và diễn giải yêu cầu trong README, CHECKPOINTS, RUBRIC, SUBMISSION và TEAM; lập kế hoạch triển khai; gợi ý cấu trúc orchestrator; rà soát các điều kiện handoff, trace, approval và crash.
- Tôi tự kiểm tra kết quả bằng cách đọc code liên quan, chạy test riêng, chạy test shape, chạy host test, chạy crash suite và kiểm tra trực tiếp trace/SQLite.
- Tôi không sử dụng AI để thay thế việc kiểm tra kết quả chạy hoặc sửa các file thước đo của đề bài.

## 6. Tự đánh giá

Tôi đã hoàn thành phần triển khai và kiểm thử của Orchestrator + Handoff. Phần còn lại là tạo commit kỹ thuật, cập nhật commit hash vào `TEAM.md` và phối hợp với nhóm để chạy benchmark, hoàn thiện báo cáo chung và chạy `check_submission`.

