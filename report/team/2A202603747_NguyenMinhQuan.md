# Báo cáo cá nhân — Nguyễn Minh Quân

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Quân
- MSSV: 2A202603747
- Email: 26ai.quannm8@vinuni.edu.vn
- GitHub: `minhquannm0905-cloud`

## 2. Phần việc phụ trách

Tôi phụ trách Shape A — deterministic workflow trong `src/lab8/shapes/workflow.py`. Mục tiêu là xử lý yêu cầu hoàn tiền theo luồng cố định, không để mô hình quyết định số tiền hoặc thực hiện side effect.

Luồng đã triển khai:

1. Đọc claim bằng `get_claim_view` thay vì truy vấn toàn bộ row.
2. Trả `needs_info` khi thiếu `order_id`.
3. Dùng `lookup_order` để kiểm tra order tồn tại và thuộc đúng principal.
4. Dùng `compute_compensation` để tính full entitlement từ order và policy đáng tin cậy.
5. Không gọi `issue_refund` khi quote bằng 0.
6. Truyền full quote và `crash_at` vào `issue_refund` khi quote lớn hơn 0.
7. Ánh xạ kết quả thành `resolved`, `denied` hoặc `failed` đúng output contract.
8. Ghi trace tối thiểu, không chứa ticket, secret, PII hoặc row thô.

## 3. Đóng góp cụ thể

- Commit kỹ thuật chính: `34900b4` — `Implement deterministic refund workflow`.
- Hoàn thiện `run_claim` và `_run` trong `src/lab8/shapes/workflow.py`.
- Giữ ranh giới code/model rõ ràng: workflow có `model_calls=0`; tiền chỉ do `compute_compensation` tính và host `issue_refund` kiểm soát.
- Truyền full quote cho host để host tự áp approval, `paid_vnd`, phần đã hoàn trên cùng order và idempotency.
- Truyền nguyên `crash_at` và không nuốt `InjectedCrash`, cho phép kiểm thử crash/resume thật.
- Thêm `src/tests/test_workflow_student.py` với test `test_workflow_is_deterministic_and_model_free`.
- Thêm `.pytest-tmp/` vào `.gitignore` để tránh commit dữ liệu tạm khi chạy pytest trên Windows.

## 4. Bằng chứng

- Test riêng: `test_workflow_is_deterministic_and_model_free` — 1 passed.
- Public student matrix cho workflow: 62 passed, 241 deselected sau khi thêm test riêng.
- Host gate trước khi thêm test riêng: 54 passed, 248 deselected.
- Run `R-workflow-C-001-s11`: `resolved`, proposal 35.000 VND, một refund effect, một committed audit, ba tool calls và không có model call.
- Retry `R-workflow-C-001-s11` trên cùng store vẫn có đúng một refund và `committed_audit_count=1`.
- Run `R-workflow-C-012-s11` với crash tại `after_effect_before_checkpoint`, sau đó resume thành công với một refund và một committed audit.
- Trace resume chỉ có ba event `quote`, `refund_request`, `decision`; không chứa secret hoặc PII.

## 5. Công cụ AI đã dùng

Tôi dùng ChatGPT/Codex để:

- Giải thích contract của workflow, idempotency và crash/resume.
- Gợi ý cấu trúc hàm và các nhánh status.
- Rà soát trace và viết test bằng chứng cho phần đóng góp.
- Hỗ trợ soạn báo cáo dựa trên kết quả thực tế.

Tôi tự kiểm tra kết quả bằng cách đọc lại code, chạy `py_compile`, chạy test riêng, chạy 62 public workflow trials, chạy host gate, chạy claim C-001 hai lần trên cùng database và mô phỏng crash/resume với C-012. Các số liệu trong báo cáo lấy từ output đã chạy, không suy đoán benchmark của toàn nhóm.

## 6. Tự đánh giá

Phần workflow đã đáp ứng public contract, an toàn khi retry và crash, không để dữ liệu trong ticket ảnh hưởng đến số tiền, và không ghi dữ liệu nhạy cảm vào trace. Điểm mạnh của shape là hành vi ổn định theo seed, dễ kiểm toán và không phát sinh chi phí model. Giới hạn là workflow có mức tự chủ thấp và chỉ phù hợp khi quy trình nghiệp vụ đã được mô tả rõ bằng code và policy. Benchmark bốn shape, crash suite toàn nhóm và quyết định kiến trúc cuối cùng cần chờ `single` và `orchestrator` hoàn thành.
