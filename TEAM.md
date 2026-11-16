# Team

## Thông tin nhóm

- Tên nhóm:Random
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Random-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |    Đỗ Văn Ngọc    |2A202603391      |       |        | Single agent        |
|   2 |        |      |       |        |         |
|   3 | DoanNhatAnh | 2A202603408 | nhatanhdoan1@gmail.com | [nhatanh2901](https://github.com/nhatanh2901) | Orchestrator, handoff và bảo mật trace |
|   4 | Nguyễn Trần Anh Khôi | 2A202603422 | khoinguyentran1111@gmail.com | khoinguyentran1111 | Ledger + evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| DoanNhatAnh (2A202603408) | Orchestrator + handoff + bảo mật | [158d999](https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/158d999) | `src/tests/test_orchestrator_security.py`: kiểm tra ticket injection, handoff chỉ đọc, trace không lộ dữ liệu và hai nhánh trả về sớm |
| Nguyễn Trần Anh Khôi (2A202603422) | Ledger + evaluation | [ff49706](https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/ff49706) | `src/tests/test_ledger_shapes.py`: crash ở cả 3 điểm rồi resume, retry, approval thiếu/thu hồi/mượn claim khác, trần theo đơn, bất biến ledger và quét secret/PII trên cả corpus (10 test × 4 shape) |

## Cá nhân

Báo cáo của DoanNhatAnh: [2A202603408_DoanNhatAnh.md](report/team/2A202603408_DoanNhatAnh.md).

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
