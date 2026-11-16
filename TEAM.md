# Team

## Thông tin nhóm

- Tên nhóm: ABCDE
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-ABCDE-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/Minh8246/K5-L3A-DAY08-ABCDE-FromWorkflowsToAgents, `main`, commit chốt điền ở CP5

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Vũ Quang Minh| 2A202603657|vuquangminh897@gmail.com|Minh8246| Nhóm trưởng: Workflow (A) + Integration |
|   2 |Nguyễn Công Quân|2A202603675|nguyencongquancn06@gmail.com|nguyencongquana2| Single agent (B) + Research card |
|   3 |Hồ Anh Dũng|2A202603613|hoanhdungsongcau@gmail.com|ITCSIU21172| Orchestrator (C) + Handoff + Trace security |
|   4 |Trần Việt Thịnh|2A202603661|thinhkesat@gmail.com  |  ThinhTran-codee      | Ledger/Policy/Crash + Evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Vũ Quang Minh | Workflow + Integration | `7fe18d7` (CP2 workflow), `2cc5ff8` (CP3 crash_at + test) | `src/tests/test_workflow_team.py` (5 test: crash/resume 3 điểm, trace sạch khi crash, không tin delay trong ticket) |
| Nguyễn Công Quân | Single agent + Research card | `3dbdd8a` (CP2 single), `66944d5` (CP3 crash/retry test) | `src/tests/test_single_team.py` (4 test: retry và crash/resume tại 3 điểm, bảo đảm một refund/audit) |
| Hồ Anh Dũng | Orchestrator + Handoff + Trace security | | |
| Trần Việt Thịnh | Ledger/Policy/Crash + Evaluation | `a13c033` (test policy/durability, báo cáo cá nhân) | `src/tests/test_thinh_ledger_policy.py` (5 test: approval expired, missing approval, non-positive amount, order cap, idempotent replay) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
