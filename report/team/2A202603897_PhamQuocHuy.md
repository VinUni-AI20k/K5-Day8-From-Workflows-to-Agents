# Báo cáo cá nhân — 2A202603897_PhamQuocHuy

## 1. Thông tin thành viên

- Họ tên: Phạm Quốc Huy
- MSSV: 2A202603897
- Email: huymix2k4@gmail.com
- GitHub: pqhuy454

## 2. Phần việc phụ trách

- **Vai trò:** Thành viên 1 — Trưởng nhóm, Tích hợp & Kiểm thử Hệ thống (Team Lead & QA Integration).
- **Phạm vi công việc:**
  - Thiết lập và kiểm soát môi trường, giữ cổng host (`python -m pytest -q`) xanh 100% xuyên suốt các commit.
  - Quản lý Git, phân nhánh tính năng cho nhóm và tổng hợp quy chuẩn vào `PROJECT_GUIDELINE.md`.
  - Viết bộ test tích hợp đa shape tại `src/tests/test_student_integration.py` kiểm tra Output Contract (`RunResult`), Trace Contract v1 và an toàn rò rỉ secret.
  - Quản lý `TEAM.md`, chạy `python -m lab8.check_submission` và viết Phần 1–2 của `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- **Chuẩn hóa tài liệu & môi trường (CP1):**
  - Tổng hợp toàn bộ yêu cầu, luật nghiệp vụ, contract và tiêu chí chấm điểm vào `PROJECT_GUIDELINE.md`.
  - Khôi phục file mẫu `report/team/MSSV_HoTen.md` và cài đặt môi trường `.venv` (Python 3.13.15), xác nhận `lab8.smoke` và cổng host hoạt động ổn định.
- **Đóng góp kỹ thuật & Test (`src/tests/test_student_integration.py`):**
  - Thiết kế và triển khai 12 test cases (parametrize trên cả 4 shape: `workflow`, `single`, `orchestrator`, `swarm`) kiểm tra:
    - Không ném uncaught exception khi xử lý claim hợp lệ (`C-001`) và claim không tồn tại (`C-999-NONEXISTENT`).
    - Trả về đúng `RunResult`, khớp `claim_id`, `shape`, `seed`, `run_id = make_run_id(...)`, `status` hợp lệ và `proposal_amount` kiểu `int`.
    - File trace đáp ứng Trace Contract v1 (`check_trace(...) == (True, "ok")`) và không chứa `CANARY_SECRET_`.
- **Commit chính:** `<sẽ cập nhật commit hash sau khi commit lên nhánh main>`

## 4. Bằng chứng

- File test đã thêm: `src/tests/test_student_integration.py`
- Kết quả chạy test tích hợp (`python -m pytest -q tests/test_student_integration.py`): **12 passed in 0.42s**.
- Kết quả cổng host sau khi thêm test (`python -m pytest -q`): **66 passed, 248 deselected in 2.73s** (tăng từ 54 lên 66 passed).
- Kết quả smoke test (`python -m lab8.smoke`): `lab8.smoke pass` (`manifest 1.1 | MockLLM seeded | swarm C-001 refund 35000 | trace clean`).

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI trong IDE (Antigravity / Gemini).
- **Mục đích sử dụng:** Hỗ trợ đọc hiểu toàn bộ tài liệu quy định của lab để tổng hợp và tóm tắt quá trình cần làm, thiết kế các test case bất biến theo Output Contract và Trace Contract v1 cho `test_student_integration.py`.
- **Cách tự kiểm tra kết quả:**
  - Chạy trực tiếp `python -m lab8.smoke` và `python -m pytest -q` trong môi trường `.venv` để xác nhận toàn bộ 66 test cổng host đều pass.
  - Đối chiếu trực tiếp từng trường kiểm tra trong `test_student_integration.py` với `src/lab8/schemas.py`, `src/tests/test_trace_contract.py` và `docs/contracts.md`.

## 6. Tự đánh giá

- Hoàn thành đúng và đầy đủ các hạng mục kỹ thuật và kiểm thử tích hợp của Thành viên 1 ở giai đoạn khởi tạo và CP1.
- Bộ test `test_student_integration.py` giúp đảm bảo mọi shape mới khi được các thành viên khác triển khai ở CP2–CP4 đều tuân thủ chuẩn `RunResult` và `Trace contract v1` mà không làm gãy cổng host.
- Việc cần làm tiếp ở các checkpoint sau: cập nhật `TEAM.md` khi có đủ thông tin 4 thành viên, hoàn thiện Phần 1–2 trong `report/team/group_report.md`, điền commit hash vào báo cáo này sau khi commit, và chạy `python -m lab8.check_submission` cho tới khi đạt `0 FAIL`.
