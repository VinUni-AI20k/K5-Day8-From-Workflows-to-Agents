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
  compensation từ order và policy hiện hành, xử lý các trạng thái.
- CP3: tích hợp `durability.issue_refund` với full quote và `crash_at`, giữ
  idempotency khi retry, cho phép `InjectedCrash` lan truyền, đồng thời ghi
  trace an toàn cho cả nhánh thành công, lỗi và crash.
- CP8: thêm test kiểm tra trace workflow không chứa secret, header, số điện
  thoại, địa chỉ, ghi chú nội bộ hoặc tên sản phẩm.

## 3. Đóng góp cụ thể

- Thay stub `not_implemented` bằng workflow deterministic dùng helper và host
  API có sẵn.
- Dùng `get_claim_view` và `lookup_order` thay vì đọc trực tiếp dữ liệu nhạy
  cảm; trace chỉ ghi các field allowlist.
- Dùng `compute_compensation` để code quyết định số tiền, không để model hoặc
  ticket quyết định refund.
- Gọi `issue_refund` với quote đầy đủ để host xử lý approval, giới hạn theo
  order và idempotency.
- Flush trace tại cửa sổ crash rồi re-raise `InjectedCrash`, giúp lần chạy
  tiếp theo resume an toàn mà không tạo refund thứ hai.
- Thêm test
  [`test_workflow_personal.py`](../../src/tests/test_workflow_personal.py)
  để bảo vệ yêu cầu redaction của trace.

Commit chính: chưa tạo commit riêng tại thời điểm lập báo cáo.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow`:
  **63 passed**.
- `python -m pytest -q`:
  **54 passed, 249 deselected**.
- Test cá nhân:
  `test_workflow_trace_redacts_claim_and_order_sensitive_fields` đạt với
  marker `student`.
- Bộ test workflow bao phủ retry T11 và crash-resume T12.
- Trace được tạo theo contract với `run_id` khớp kết quả trả về và không chứa
  các trường nhạy cảm của claim/order.

## 5. Công cụ AI đã dùng

Đã dùng Copilot SDK trong VS Code để hỗ trợ đọc contract, đối chiếu shape tham
chiếu, viết workflow, thêm test và kiểm tra lỗi. Kết quả được tự kiểm tra bằng
test cá nhân, test workflow và toàn bộ test mặc định của repository.

## 6. Tự đánh giá

Hoàn thành phần workflow của CP2, CP3 và bổ sung test cá nhân cho CP8. Đã xác
minh bằng test tự động; chưa phụ trách các shape `single` hoặc `orchestrator`.