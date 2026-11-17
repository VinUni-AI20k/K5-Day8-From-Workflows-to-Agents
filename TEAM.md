# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-NhomChokeVy-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Lê Chuẩn | 2A202603784 | lechuanpham@gmail.com | 22520160 | workflow + integration |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Lê Chuẩn | workflow + integration | Chưa commit (working tree) | `src/tests/test_workflow_integration.py` (3 passed); student workflow matrix (62 passed) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603784_PhamLeChuan

### Phần việc phụ trách

- Phụ trách shape `workflow` và tích hợp với host: đọc claim/order qua tool, tính quote theo order, gọi `durability.issue_refund` bằng quote đầy đủ, và trả kết quả/trace theo contract chung.

### Đóng góp cụ thể

- Triển khai workflow xác định: đọc claim và order qua tool, lấy quote từ dữ liệu order, chuyển nguyên quote cho host ghi refund, và hoàn tất các nhánh status bằng helper dùng chung.

### Bằng chứng

- Mã: `src/lab8/shapes/workflow.py`; test riêng `src/tests/test_workflow_integration.py`: 3 passed; `python -m pytest -q -m student -o addopts= -k workflow`: 62 passed; `python -m lab8.smoke`: pass.
