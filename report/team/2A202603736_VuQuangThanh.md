# Báo cáo cá nhân — 2A202603736_TV

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Thanh
- MSSV: 2A202603736
- Email: 26ai.thanhvq@vinuni.edu.vn
- GitHub: [@thanhvu101](https://github.com/thanhvu101)

## 2. Phần việc phụ trách

Phụ trách triển khai shape **workflow** cho Checkpoint 2 và Checkpoint 3 trong
[`src/lab8/shapes/workflow.py`](../../src/lab8/shapes/workflow.py).

- CP2: triển khai quy trình đọc claim, kiểm tra order theo principal, tính
  compensation từ dữ liệu order và policy hiện hành, xử lý các trạng thái
  `needs_info`, `escalated`, `denied`, `resolved` và `failed`.
- CP3: tích hợp `durability.issue_refund` với full quote và `crash_at`, giữ
  idempotency khi retry, cho phép `InjectedCrash` lan truyền, đồng thời ghi
  trace an toàn cho cả nhánh thành công, lỗi và crash.

## 3. Đóng góp cụ thể

- Thay stub `not_implemented` bằng workflow deterministic dùng các helper và
  host API có sẵn.
- Dùng `get_claim_view` và `lookup_order` thay vì đọc trực tiếp dữ liệu nhạy
  cảm; trace chỉ ghi các field allowlist.
- Dùng `compute_compensation` để code quyết định số tiền, không để model hoặc
  ticket quyết định refund.
- Gọi `issue_refund` với quote đầy đủ để host xử lý approval, giới hạn theo
  order và idempotency.
- Flush trace tại cửa sổ crash rồi re-raise `InjectedCrash`, giúp lần chạy
  tiếp theo resume an toàn mà không tạo refund thứ hai.

Commit chính: chưa tạo commit riêng tại thời điểm lập báo cáo.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow`:
  **62 passed**.
- `python -m pytest -q`:
  **54 passed, 248 deselected**.
- Bộ test workflow bao phủ các nhánh CP2 và CP3, gồm retry T11 và crash-resume
  T12.
- Trace được tạo theo contract với `run_id` khớp kết quả trả về; không ghi
  `parent_secret`, raw headers, số điện thoại, địa chỉ hoặc ghi chú nội bộ.

## 5. Công cụ AI đã dùng

Đã dùng Copilot SDK trong VS Code để hỗ trợ đọc contract, đối chiếu các shape
tham chiếu, viết phần triển khai workflow và kiểm tra lỗi. Kết quả được tự
kiểm tra bằng test workflow và toàn bộ test mặc định của repository; không
chấp nhận kết quả chỉ dựa trên gợi ý của AI.

## 6. Tự đánh giá

Hoàn thành phần workflow của CP2 và CP3 theo đúng contract chung. Mức độ đóng
góp: hoàn thành triển khai và xác minh bằng test; chưa tạo commit riêng và
chưa phụ trách các shape `single` hoặc `orchestrator`.
