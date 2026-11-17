# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hữu Thịnh | 2A202603726 | nht702812@gmail.com | huuthinh812 | Workflow (Core Developer), Shape A |
|   2 |        |      |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Hữu Thịnh (2A202603726) | Workflow (Core Developer), Shape A | `1484656` feat(workflow): implement shape A deterministic workflow + crash report; `057ee06` test(workflow): add shape A boundary tests | Thêm `src/tests/test_workflow_boundary.py` (31 test: ticket là dữ liệu, chỉ gọi host khi quote > 0 với quote đầy đủ, trace không lộ ticket/secret/PII). Chạy pass 62 student test workflow |

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

## 2A202603726_NguyenHuuThinh

### Phần việc phụ trách

- Người 1, Workflow (Core Developer): Shape A `src/lab8/shapes/workflow.py`. Quy trình xử lý claim tuần tự, nối policy, tracking, compensation và approval qua cổng host `durability.issue_refund`.

### Đóng góp cụ thể

- Commit `1484656`: implement workflow (`src/lab8/shapes/workflow.py`). File `src/reports/crash.json` đã gỡ khỏi branch này và giao cho Người 4.
- Commit `057ee06`: thêm `src/tests/test_workflow_boundary.py` (31 test boundary cho workflow).
- Báo cáo kiến trúc Workflow (`report/team/workflow_architecture.md`) và báo cáo cá nhân (`report/team/2A202603726_NguyenHuuThinh.md`).

### Bằng chứng

- Student test workflow 62/62, test boundary 31/31, cổng host 85 passed, `crash_safety 20/20`, 0 trace lộ secret.
- Benchmark public workflow: pass 1.000, pass^5 1.000, var 0, cost/success 27.86 VND mô phỏng (swarm: 0.986, 0.929, 49.57).
