# Team

## Thông tin nhóm

- Tên nhóm: Apollo
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Apollo-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/dungpham108/K5-L3A-DAY08-Apollo-FromWorkflowsToAgents / nhánh: thanhtung

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Trần Thanh Tùng | 2A202603418 | tranthanhtung306thd@gmail.com | tungtran306 | CP2 Shapes & CP3 Durability |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Trần Thanh Tùng | CP2 Shapes & CP3 Durability | e0806e1 | src/tests/test_cp3_resilience.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603418_TranThanhTung

### Phần việc phụ trách

- Triển khai Shape A (workflow), Shape B (single), Shape C (orchestrator) ở CP2.
- Đảm bảo tính Idempotency, Crash recovery và Handoff an toàn ở CP3.
- Viết test mở rộng `src/tests/test_cp3_resilience.py`.

### Đóng góp cụ thể

- Commit `9cc25fe`: Hoàn thành 3 shapes, pass toàn bộ 248 test student.
- Commit `e0806e1`: Thêm 7 tests kiểm tra resilience & idempotency.

### Bằng chứng

- File báo cáo cá nhân: `report/team/2A202603418_TranThanhTung.md`
- 302/302 tests passed trên toàn bộ hệ thống test.
