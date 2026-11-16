# Team

## Thông tin nhóm

- Tên nhóm: Soopi
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Soopi-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Mai Tuấn Anh | 2A202603574 | maituananh1511@gmail.com | https://github.com/AnhMT2k4 | Workflow + Integration |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Mai Tuấn Anh | workflow | 38c08ef | tests/test_workflow.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603574_MaiTuanAnh

### Phần việc phụ trách

- Triển khai Shape A (`workflow.py`).
- Xây dựng bộ test toàn diện cho Shape A (`tests/test_workflow.py`).

### Đóng góp cụ thể

- Hoàn thiện mã nguồn `src/lab8/shapes/workflow.py` tuân thủ ranh giới Code vs Model và xử lý an toàn crash/retry.
- Thêm 107 test cases trong `src/tests/test_workflow.py`.

### Bằng chứng

- Commit `9b0cbed` (Workflow) và `38c08ef` (Test Workflow).
- File báo cáo cá nhân: `report/team/2A202603574_MaiTuanAnh.md`.
