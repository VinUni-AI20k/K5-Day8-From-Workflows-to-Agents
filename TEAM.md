# Team

## Thông tin nhóm

- Tên nhóm: NhomV3
- Lớp: L3A
- Repo nhóm: `congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents ; nhánh nộp chung và commit chốt do nhóm xác nhận sau merge.
- Nhánh làm việc của Nguyễn Quốc Hưng: `hung`.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Trương Việt Công | 2A202603585 | vietcongtruong07@gmail.com | congcoderht | Single agent; nhánh feature/single |
|   2 | Nguyễn Quốc Hưng | 2A202603553 | hung90879087@gmail.com | hung309911 | Shape C; handoff/trace; rà secret/PII; R3; nhánh hung |
|   3 | Đỗ Minh Hoàng | 2A202603554 | hoangcoihd6@gmail.com | worryveem | Phần việc còn lại theo phân công nhóm |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |
| Nguyễn Quốc Hưng — 2A202603553 | Orchestrator, handoff/trace, audit secret/PII và R3 | [2ce84ee](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/2ce84ee86e7f71d83d5bb86ba83b1c22e544b952) | src/tests/test_team_orchestrator.py — 19 test pass; ví dụ test_injected_ticket_cannot_override_order_or_leak_pii |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Báo cáo Nguyễn Quốc Hưng: [2A202603553_NguyenQuocHung.md](report/team/2A202603553_NguyenQuocHung.md).

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
