# Báo cáo cá nhân — Trịnh Quốc Đạt

## 1. Thông tin thành viên

- Họ tên: Trịnh Quốc Đạt
- MSSV: 2A202603581
- Email:
- GitHub: [Trinh-Quoc-Dat](https://github.com/Trinh-Quoc-Dat)

## 2. Phần việc phụ trách

- Shape A `workflow`: triển khai quy trình xử lý claim cố định bằng Python trong `src/lab8/shapes/workflow.py`.

## 3. Đóng góp cụ thể

- Commit chính: `a4ebc01` — `Implement deterministic workflow shape`.
- Thêm test `test_unknown_claim_fails_without_refund_and_writes_trace` trong `src/tests/test_workflow_contribution.py`.
- Workflow đọc claim qua allowlist, tra cứu đơn theo principal, tính quote bằng `compute_compensation`, rồi chuyển quote đầy đủ cho `durability.issue_refund` để host kiểm tra và ghi refund.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k workflow`: 62 passed.
- `python -m pytest -q`: 54 passed, 248 deselected.
- `python -m pytest -q tests/test_workflow_contribution.py`: 1 passed.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- Branch làm việc: `TrinhQuocDat-2A202603581`.

## 5. Công cụ AI đã dùng

- Dùng ChatGPT/Codex để hiểu yêu cầu workflow, rà các contract và hướng dẫn triển khai/test.
- Tự kiểm tra bằng các lệnh pytest và crash suite nêu ở mục 4; kết quả hiển thị trên terminal.

## 6. Tự đánh giá

Đã triển khai và tự kiểm tra shape workflow trên bộ test công khai, bao gồm retry, crash, và ca claim không tồn tại. Cần xác nhận việc tích hợp branch vào nhánh nộp chung và cập nhật bằng chứng sau khi nhóm hoàn tất benchmark, báo cáo và kiểm tra nộp bài.
