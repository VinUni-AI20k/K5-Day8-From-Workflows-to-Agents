# Team

## Thông tin nhóm

- Tên nhóm: HVM
- Lớp: L3B theo tên repo hiện tại, chờ coach xác nhận mã lớp dùng khi nộp.
- Repo nhóm: [K5-L3B-DAY08-HVM-FromWorkflowsToAgents](https://github.com/NhMinh-2610/K5-L3B-DAY08-HVM-FromWorkflowsToAgents)
- Nhánh nộp: `main`
- Commit chốt: chờ tích hợp đủ ba shape.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Thế Hùng | 2A202603778 |  26ai.hungpt5@vinuni.edu.vn | `thehung1406` | `workflow`, tích hợp và nộp bài |
|   2 | Phạm Đức Vinh | 2A202603849 | 26ai.vinhpd@vinuni.edu.vn | `vindpd203` | `single`, báo cáo nhóm và research card |
|   3 | Nguyễn Nhật Minh | 2A202603745 | nnhatminh2610@gmail.com | `NhMinh-2610` | `orchestrator`, handoff, trace, audit bảo mật và ADR |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Hùng | `workflow`, tích hợp | `3b87b6e` | `test_workflow_rejects_approval_for_another_claim`, `test_workflow_retry_keeps_one_refund_and_audit` |
| Vinh | `single`, research card R2, báo cáo nhóm | `8ba0422`, `9aa1dd9`, `85c0a35`, `2c2c7c2` | `src/tests/test_team_single.py` (`test_single_quotes_from_order_row_not_ticket`, `test_single_does_not_echo_stored_approval_status`, so sánh swarm seed 55, giới hạn 8 bước) |
| Minh | `orchestrator`, bảo mật và ADR | `a06249f` | `src/tests/test_team_orchestrator.py` (secret/PII, approval, 3 điểm crash, retry, conflict và quote đầy đủ) |

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
