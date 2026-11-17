# Team

## Thông tin nhóm

- Tên nhóm: Apollo
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Apollo-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/dungpham108/K5-L3A-DAY08-Apollo-FromWorkflowsToAgents / nhánh: thanhtung

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Trần Thanh Tùng | 2A202603418 | 26ai.tungtt@vinuni.edu.vn | tungtran306 | Shape B (Single ReAct) & Policy/Approval |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Trần Thanh Tùng | Shape B (Single ReAct) & Policy/Approval | 734df62 | src/tests/test_SV02_tungtran306_single_policy.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603418_TranThanhTung

### Phần việc phụ trách

- Cài đặt và hiện thực hóa Shape B (Single ReAct Agent).
- Viết unit tests kiểm thử cho Shape B và kiểm duyệt Policy/Approval.
- Tham gia phân tích nghiên cứu & đối chứng thực nghiệm (Research Card).

### Đóng góp cụ thể

- Commit `9cc25fe`: Hoàn thành 3 shapes, pass toàn bộ 248 test student.
- Commit `734df62`: Thêm bộ unit test `src/tests/test_SV02_tungtran306_single_policy.py` (7 tests).

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603418_TranThanhTung.md`
- 7/7 unit tests passed trong `python -m pytest -q tests/test_SV02_tungtran306_single_policy.py`
