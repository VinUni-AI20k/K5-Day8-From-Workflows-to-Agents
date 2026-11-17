# Báo cáo cá nhân — Vũ Thanh Toàn

## 1. Thông tin thành viên

- Họ tên: Vũ Thanh Toàn
- MSSV: 2A202603654
- Email: thanhtoana7hha@gmail.com
- GitHub:Kyo708

## 2. Phần việc phụ trách

Shape A `workflow` (`src/lab8/shapes/workflow.py`) và integration: gộp các nhánh vào `main`, kiểm cổng host, bộ test student và `check_submission` sau khi gộp, điền thông tin nhóm trong `TEAM.md`.

## 3. Đóng góp cụ thể

- Viết workflow các bước cố định, không gọi model:

  | Bước | Kết quả |
  |---|---|
  | `get_claim_view` không thấy claim | `failed`, proposal 0, `unknown_claim` |
  | Thiếu `order_id` | `needs_info`, proposal 0 |
  | `lookup_order` không visible | `escalated`, proposal 0, reason từ tool |
  | `compute_compensation` = 0 | `denied`, proposal 0, không gọi host |
  | Quote > 0 → `issue_refund(conn, claim_id, quote_đầy_đủ, crash_at=crash_at)` | ok → `resolved`; conflict → `failed`; còn lại → `denied` |

- Quyết định kỹ thuật:
  - **Tiền do code tính** từ order row bằng `compute_compensation`, không đọc ticket. Câu "trễ 5 ngày" hay "ignore policy" trong ticket không ảnh hưởng gì (đúng chỗ swarm fail C-002 ở seed 55).
  - **Truyền quote đầy đủ** cho host, để host tự trừ phần đơn đã được hoàn. Nếu shape trừ trước thì phần đó bị trừ hai lần.
  - **Quote > 0 luôn gọi host**, kể cả khi approval có vẻ hỏng, vì chỉ host ghi audit `policy_denied`.
  - **Crash:** truyền `crash_at` cho host, bắt `InjectedCrash` chỉ để ghi trace rồi `raise` lại. Không bọc `except Exception` quanh host.
  - **Trace allowlist:** chỉ ghi `claim_id`, `has_order_id`, 6 field order cần cho quote (`_TRACE_ORDER_FIELDS`), quote, kết quả host và decision. Không ghi ticket, `principal_id`, `parent_secret`, header.
  - Mọi nhánh return đi qua `common.finish()`; `conn` đóng trong `try/finally`.
- Commit chính: `8300fcc3fb7f9bb5bf062e98b588b24809f0a111` (PR #2, nhánh `VuThanhToan-2A202603654`).
- Thêm `src/tests/test_workflow_extra.py`:
  - `test_workflow_ignores_delay_written_in_ticket` (C-002 × 5 seed): ticket ghi trễ 5 ngày, DB ghi 2 → luôn `denied`, không có refund, `model_calls=0`.
  - `test_workflow_trace_has_no_secret_or_ticket` (mọi claim public): trace đúng `run_id`, không chứa `CANARY_SECRET`, `Bearer` hay nguyên văn ticket.
  - Gắn marker `student` để không đổi cổng host chung.
- Integration: sau khi PR #1–#4 vào `main`, chạy lại toàn bộ bước kiểm tra trên `main` (kết quả ở mục 4), điền bảng thành viên và URL repo trong `TEAM.md`.

## 4. Bằng chứng

- Commit `8300fcc`, PR #2.
- `python -m pytest -q -o addopts= tests/test_workflow_extra.py`: 19 passed.
- `python -m pytest -q -m student -o addopts= -k workflow`: 81 passed.
- Benchmark workflow (`src/reports/benchmark.json`): pass 1.000, pass^5 1.000, variance 0, cost/success 27.86. Đây là shape nhóm chọn trong `decision_adr.md`.
- Run id: `R-workflow-C-002-s55` (denied đúng, nơi swarm fail), `R-workflow-C-007-s55` (approval hết hạn → denied).
- Kiểm integration trên `main` @ `ab5f33a`: `python -m lab8.smoke` pass; `python -m pytest -q` 83 passed; `python -m pytest -q -m student -o addopts=` 267 passed; `python -m lab8.check_submission` 0 FAIL, 0 WARN.

## 5. Công cụ AI đã dùng

Claude Code hỗ trợ viết `workflow.py`, test và rà các bước integration. Đã tự đọc diff, đối chiếu với `docs/business_rules.md` và `docs/contracts.md`, chạy smoke, cổng host, bộ test student, benchmark và `check_submission` để kiểm kết quả.

## 6. Tự đánh giá

Hoàn thành shape `workflow`: pass toàn bộ claim public ở 5 seed với chi phí thấp nhất trong 4 shape, trace sạch, crash không tạo refund trùng. Phần integration đã gộp đủ 4 nhánh vào `main` mà cổng host và `check_submission` vẫn xanh.
