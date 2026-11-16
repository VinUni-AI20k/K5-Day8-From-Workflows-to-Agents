# Báo cáo cá nhân — 2A202603598-Nguyễn Hữu Tiến

## 1. Thông tin thành viên

- Họ tên: Nguyễn Hữu Tiến
- MSSV: 2A202603598
- Email: tiennguyen0606@gmail.com
- GitHub: https://github.com/tiennguyen0606

## 2. Phần việc phụ trách

- **Vai trò**: Orchestrator (Shape C & Handoff Security)
- **Phần việc**:
  - Đọc và phân tích cơ chế khử khuẩn (sanitization) và phân quyền công cụ trong `lab8/handoff.py` và `lab8/runtime.py`.
  - Triển khai Shape C trong `src/lab8/shapes/orchestrator.py`.
  - Đảm bảo ranh giới bảo mật: Handoff chỉ truyền thông tin qua allowlist, ngăn chặn rò rỉ Canary Secret (`CANARY_SECRET_*`, `parent_secret`, `raw_headers`).
  - Đảm bảo các investigator chỉ sở hữu tool đọc (`READONLY_TOOLS`), quyền ghi duy nhất (`issue_refund`) thuộc về orchestrator/host.
  - Viết bộ unit test cho Orchestrator (`src/tests/test_orchestrator.py`) và chạy pass toàn bộ 62 test suite student của Shape C.

## 3. Đóng góp cụ thể

- **Triển khai `src/lab8/shapes/orchestrator.py`**:
  - Tích hợp `make_handoff` và `run_readonly_investigators` an toàn.
  - Xử lý đầy đủ luồng nghiệp vụ: `needs_info` khi thiếu `order_id`, `escalated` khi đơn ngoài phạm vi quyền (`outside_principal_scope`), `denied` khi quote = 0 hoặc vi phạm policy, `resolved` khi hoàn tiền thành công.
  - Báo giá bồi thường được trích xuất an toàn từ điều tra viên chỉ đọc (`investigated["tools"]["compute_compensation"]`).
  - Truyền `crash_at` vào `durability.issue_refund` và chuyển tiếp `InjectedCrash` đúng quy định của CP3.
- **Viết test suite mới (`src/tests/test_orchestrator.py`)**:
  - `test_orchestrator_trace_records_sanitized_handoff`: Kiểm tra trace chỉ chứa handoff đã làm sạch, không chứa canary secret hay secret cha.
  - `test_orchestrator_rejects_worker_write_tools`: Xác nhận `make_handoff` ném `HandoffError` khi cố tình cấp `issue_refund` cho worker.
  - `test_orchestrator_escalates_on_unowned_order`: Kiểm tra case C-005 leo thang `escalated` khi truy cập đơn không thuộc quyền sở hữu.
- **Quyết định kỹ thuật**:
  - Truyền báo giá đầy đủ từ `compute_compensation` vào `durability.issue_refund` để host tự động cấn trừ các khoản đã hoàn trước đó (tránh lỗi trừ 2 lần ở T13, T14).

## 4. Bằng chứng

- **Test suite sinh viên (Shape C)**:
  `python -m pytest -q -m student -o addopts= -k "orchestrator"` đạt **62/62 passed**.
- **Unit test riêng của Orchestrator**:
  `python -m pytest -q tests/test_orchestrator.py` đạt **3/3 passed**.
- **Audit Grader**:
  `python -m lab8.check_submission` xác nhận:
  `[ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.

## 5. Công cụ AI đã dùng

- **Công cụ**: Trợ lý AI (Antigravity).
- **Mục đích**: Hỗ trợ đọc hiểu nhanh hợp đồng `handoff.v1`, rà soát ranh giới bảo mật PII/Secret trong trace và sinh khung unit test cho `test_orchestrator.py`.
- **Cách tự kiểm tra**: Trực tiếp chạy test trên terminal local qua `pytest`, kiểm tra trace file JSON sinh ra để đối chiếu `run_id`, `events`, đảm bảo không chứa chuỗi canary cấm nào.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các tiêu chí kỹ thuật và bảo mật của vai trò TV3 (Orchestrator). Toàn bộ 62 test case chạy xanh tuyệt đối.
