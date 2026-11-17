# Team

## Thông tin nhóm

- Tên nhóm: NhomTuesday
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-NhomTuesday-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/NgChiVinh/K5-L3B-DAY08-NhomTuesday-FromWorkflowsToAgents, nhánh `main`, commit chốt: (điền khi nộp)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Ngô Chí Vĩnh | 2A202603724 | | NgChiVinh | Nhóm trưởng: Integration + Shape A workflow |
|   2 | | | | | Shape B single agent |
|   3 | | | | | Shape C orchestrator + handoff |
|   4 | | | | | Durability / policy / crash (QA cả 3 shape) |
|   5 | | | | | Eval + report (benchmark, ADR, research card) |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Ngô Chí Vĩnh | Integration + Shape A workflow | `e7e6d98` CP2/CP3: implement shape A workflow and its tests | `src/tests/test_workflow_shape.py` (18 test: ticket injection, needs_info, unknown claim, model không đổi được tiền, trace sạch) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603724_NgoChiVinh

### Phần việc phụ trách

- Nhóm trưởng: tạo repo nhóm, chia vai, review và merge PR, giữ `python -m pytest -q` xanh, chạy `check_submission` trước khi nộp.
- Shape A `workflow` (`src/lab8/shapes/workflow.py`).

### Đóng góp cụ thể

- Viết workflow: `get_claim_view` → `lookup_order` → `compute_compensation` → `durability.issue_refund` (quote đầy đủ, truyền `crash_at`, không bắt `InjectedCrash`). MockLLM chỉ soạn câu trả lời.
- Trace chỉ ghi view đã qua allowlist; không ghi ticket, `principal_id`, claim/order row thô.
- Viết `src/tests/test_workflow_shape.py` (18 test).

### Bằng chứng

- Commit `e7e6d98` trên nhánh `p1-workflow`.
- `python -m pytest -q -m student -o addopts= -k workflow`: 62 passed.
- `python -m lab8.check_submission`: `[ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11`.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
