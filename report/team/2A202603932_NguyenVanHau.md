# Báo cáo cá nhân — 2A202603932_NguyenVanHau

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Hậu
- MSSV: 2A202603932
- Email: nguyenhau230303@gmail.com
- GitHub: common-maker

## 2. Phần việc phụ trách

- Thiết kế, cài đặt và kiểm thử **Shape B (`single` — Single ReAct Agent)** tại `src/lab8/shapes/single.py`.
- Viết bộ unit test bổ sung cho Shape B tại `src/tests/test_single_shape.py`.

## 3. Đóng góp cụ thể

- **Commit chính:** `6e201de` (`complete shape B`) — cài đặt hoàn chỉnh `run_claim` cho Shape B trong `src/lab8/shapes/single.py`.
- **Test đã thêm:** `src/tests/test_single_shape.py` gồm 3 test case:
  - `test_single_ignores_ticket_delay_trap_across_seeds`: kiểm chứng Shape B bỏ qua số ngày trễ giả mạo trong ticket (C-002) trên cả seed `11` và `55`.
  - `test_single_unknown_claim_fails_cleanly_with_valid_trace`: kiểm chứng xử lý `unknown_claim`, đảm bảo Trace contract v1 và không rò `CANARY_SECRET_*`.
  - `test_single_crash_and_resume_keeps_single_refund`: kiểm chứng cơ chế crash ở `after_effect_before_checkpoint` (`C-012`) và resume giữ đúng 1 dòng refund, 1 audit `refund_committed`.
- **Quyết định kỹ thuật:**
  - Dùng `lab8.runtime.run_react` với `max_steps=8` và `worker=True` để model chỉ được gọi các read-only tool (`get_claim_view`, `lookup_order`, `compute_compensation`), không có quyền gọi write tool.
  - Luôn tính tiền bằng `compute_compensation` trên dòng `order` có cấu trúc, không tin số liệu hay câu lệnh từ `ticket` (tránh bẫy T02, T06, T09).
  - Truyền **quote đầy đủ** (`proposal`) và `crash_at` vào `durability.issue_refund` ở lớp host sau khi vòng ReAct kết thúc; không tự trừ phần đã hoàn trước đó (để host tự xử lý ở T13, T14) và không bắt `InjectedCrash` (để T12 kiểm tra đúng điểm crash).
  - Ghi trace theo Trace contract v1 qua `lab8.trace.Trace` và `lab8.shapes.common.finish` trên mọi nhánh return (kể cả khi `InjectedCrash` xảy ra), chỉ log các field đã qua allowlist (không ghi `parent_secret`, `raw_headers`, SĐT, địa chỉ, tên hàng, ghi chú nội bộ).

## 4. Bằng chứng

- Commit cài đặt Shape B: `6e201de` trên nhánh `Hau`.
- File code và test: `src/lab8/shapes/single.py`, `src/tests/test_single_shape.py`.
- Kết quả tự kiểm tra chạy trong `src/`:
  - `python -m pytest -q`: `57 passed` (54 test cổng host + 3 test mới trong `test_single_shape.py`).
  - `python -m pytest -q -m student -o addopts= -k "single]"`: `62 passed` (12 single-run claims × 5 seeds `11,22,33,44,55` + T11 retry idempotency + T12 crash & resume).
  - `check_shapes` (`lab8.check_submission`): `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.
  - Run ID mẫu kiểm chứng: `R-single-C-001-s11`, `R-single-C-002-s55`, `R-single-C-012-s11`, `R-single-C-014-s11`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI trong IDE (Antigravity).
- **Mục đích sử dụng:** Đọc hiểu contract hệ thống (`docs/business_rules.md`, `docs/contracts.md`, `lab8/runtime.py`, `lab8/durability.py`), gợi ý cấu trúc vòng lặp ReAct cho Shape B (`src/lab8/shapes/single.py`), viết unit test (`src/tests/test_single_shape.py`) và tổng hợp checklist nộp bài.
- **Cách tự kiểm tra kết quả:**
  - Chạy lại toàn bộ cổng host (`python -m pytest -q`), ma trận student cho Shape B (`python -m pytest -q -m student -o addopts= -k "single]"`) và `check_shapes` từ `lab8.check_submission` để xác minh tất cả test đều pass.
  - Đối chiếu trực tiếp code trong `single.py` với các ràng buộc: `max_steps=8`, `worker=True`, không bắt `InjectedCrash`, truyền full quote vào `issue_refund`, và không ghi field nhạy cảm vào `Trace`.

## 6. Tự đánh giá

- Hoàn thành đúng hạn phần cài đặt và kiểm thử Shape B (`single`) với 62/62 test student và 57/57 test host pass.
- Sẵn sàng phối hợp cùng nhóm hoàn thiện phần tích hợp benchmark 4 shape, crash suite và tài liệu nhóm (`TEAM.md`, `decision_adr.md`, `group_report.md`) khi các shape còn lại hoàn tất.
