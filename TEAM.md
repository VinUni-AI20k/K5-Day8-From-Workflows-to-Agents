# Team

## Thông tin nhóm

- Tên nhóm: NhomV3
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-NhomV3-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents
- Nhánh nộp: main
- Commit chốt: e99c5f2 (trùng `report/team/decision_adr.md`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Trương Việt Công|2A202603585|vietcongtruong07@gmail.com|congcoderht|         |
|   2 |Nguyễn Quốc Hưng|2A202603553|hung90879087@gmail.com|hung309911|         |
|   3 |Đỗ Minh Hoàng|2A202603554|hoangcoihd6@gmail.com|worryveem|Workflow (Shape A), crash suite, benchmark, ADR|

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |
| Nguyễn Quốc Hưng — 2A202603553 | Orchestrator, handoff/trace, audit secret/PII và R3 | [2ce84ee](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/2ce84ee86e7f71d83d5bb86ba83b1c22e544b952) | src/tests/test_team_orchestrator.py — 19 test pass; ví dụ test_injected_ticket_cannot_override_order_or_leak_pii |
| Đỗ Minh Hoàng — 2A202603554 | Workflow (Shape A), crash suite, benchmark, ADR | [9cdc97b](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/9cdc97b) | src/tests/test_team_workflow.py — 25 test pass; ví dụ test_full_quote_is_passed_and_host_pays_only_the_difference |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Báo cáo Nguyễn Quốc Hưng: [2A202603553_NguyenQuocHung.md](report/team/2A202603553_NguyenQuocHung.md).

Báo cáo Đỗ Minh Hoàng: [2A202603554_DoMinhHoang.md](report/team/2A202603554_DoMinhHoang.md).

Sao chép mục dưới đây cho từng thành viên.

## Nguyễn Quốc Hưng — 2A202603553

### Phần việc phụ trách

- Shape C, handoff allowlist, trace và công cụ rà secret/PII; nhánh `hung`.
- Phần Shape C trong báo cáo nhóm, nghiên cứu R3 và báo cáo cá nhân.

### Đóng góp cụ thể

- Triển khai `src/lab8/shapes/orchestrator.py`; thêm 19 test riêng trong `src/tests/test_team_orchestrator.py`.
- Viết `audit_team_security.py`, thí nghiệm `research_orchestrator_r3.py` và script kiểm sau merge.

### Bằng chứng

- Student matrix Shape C: `62 passed`; test riêng: `19 passed`; bộ test mặc định: `73 passed`.
- `src/reports/orchestrator_benchmark.json`: 70/70 trial public pass.
- `src/reports/orchestrator_security.json` và `src/reports/orchestrator_r3_ablation.json`.
- Báo cáo cá nhân: `report/team/2A202603553_NguyenQuocHung.md`. Commit kỹ thuật: `2ce84ee86e7f71d83d5bb86ba83b1c22e544b952` trên nhánh `hung`.

## Đỗ Minh Hoàng — 2A202603554

### Phần việc phụ trách

- Shape A `workflow`; nhánh `hoang` (PR #3).
- Crash suite, benchmark 4 shape × 5 seed và `decision_adr.md` sau khi merge đủ ba shape.

### Đóng góp cụ thể

- Triển khai `src/lab8/shapes/workflow.py`; thêm 25 test riêng trong `src/tests/test_team_workflow.py`.
- Sinh `src/reports/benchmark.json`, chạy lại `src/reports/crash.json`, điền ADR chọn `workflow`.

### Bằng chứng

- Student matrix Shape A: `62 passed`; test riêng: `25 passed`; sau merge: ma trận 4 shape `248 passed`, bộ test mặc định `102 passed`.
- `src/reports/benchmark.json`: workflow pass rate/pass^5 `1.0`, cost/success `34.29` VND mô phỏng; `src/reports/crash.json`: `20/20`.
- Báo cáo cá nhân: `report/team/2A202603554_DoMinhHoang.md`. Commit: `9cdc97b` (code), `e99c5f2` (benchmark), `a7d2ace` (ADR).
