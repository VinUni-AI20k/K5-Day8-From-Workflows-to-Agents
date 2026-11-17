# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Chưa cung cấp | Chưa cung cấp | Chưa cung cấp | Chưa cung cấp | Workflow, tích hợp và báo cáo nhóm |
|   2 |        |      |       |        |         |
|   4 | Trương Anh Đức | 2A202604096 | Chưa cung cấp | TADIZB | Kiểm thử tích hợp, benchmark và ADR |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Người 1 | Workflow, tích hợp và báo cáo nhóm | Chưa có commit | `src/tests/test_team_workflow.py` (đã thêm; chưa chạy được do thiếu pytest) |
| Người 4 — Trương Anh Đức | Kiểm thử tích hợp, benchmark và ADR | `cb40979`, `d11143b` | `src/tests/test_team_integration.py` (đã thêm, 142 passed) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## Người 1 (chưa cung cấp MSSV_HoTen)

### Phần việc phụ trách

- Workflow cố định: đọc claim/order qua read tools, tính quote bằng dữ kiện order và gọi host với quote đầy đủ.

### Đóng góp cụ thể

- Triển khai `src/lab8/shapes/workflow.py` và thêm test cho ticket/order lệch dữ kiện, cap theo order, trace an toàn, crash/resume.

### Bằng chứng

- `src/tests/test_team_workflow.py` đã thêm; chưa chạy được vì môi trường thiếu `pytest` và cài dependency bị chặn network.
