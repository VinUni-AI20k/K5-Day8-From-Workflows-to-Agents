# Team

## Thông tin nhóm

- Tên nhóm: NhomV3
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-NhomV3-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo: https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents
- Nhánh nộp: main
- Commit chốt: 

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |Trương Việt Công|2A202603585|vietcongtruong07@gmail.com|congcoderht|Single agent (Shape B), approval audit, hidden self-check, R2|
|   2 |Nguyễn Quốc Hưng|2A202603553|hung90879087@gmail.com|hung309911|         |
|   3 |Đỗ Minh Hoàng|2A202603554|hoangcoihd6@gmail.com|worryveem|         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| | | | |
| Nguyễn Quốc Hưng — 2A202603553 | Orchestrator, handoff/trace, audit secret/PII và R3 | [2ce84ee](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/2ce84ee86e7f71d83d5bb86ba83b1c22e544b952) | src/tests/test_team_orchestrator.py — 19 test pass; ví dụ test_injected_ticket_cannot_override_order_or_leak_pii |
| Trương Việt Công — 2A202603585 | Single agent (Shape B), rà approval must-pass #1, hidden self-check và R2 | [cbc72cc](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/cbc72cc40c1c9a8a2f23b82f69bd42fef937430b) | src/tests/test_team_single.py — 4 test pass; ví dụ test_single_ignores_ticket_delay_c002 |

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


## Trương Việt Công — 2A202603585

### Phần việc phụ trách

- Shape B (single ReAct agent); nhánh `feature/single`.
- Rà must-pass #1 (approval) trên cả 3 shape; tự kiểm bộ hidden `student_drop/`.
- Phần Shape B trong báo cáo nhóm, nghiên cứu R2 và báo cáo cá nhân.

### Đóng góp cụ thể

- Triển khai `src/lab8/shapes/single.py`: vòng `run_react` tối đa 8 bước, `worker=True` nên model chỉ gọi được tool đọc (`lookup_order`, `lookup_refund_history`, `lookup_policy`).
- Sau vòng lặp, code tính tiền bằng `compute_compensation` từ order row (không tin số trong ticket), truyền quote đầy đủ và `crash_at` vào `durability.issue_refund`, không nuốt `InjectedCrash`.
- Trace ghi ở mọi nhánh return, chỉ field allowlist; không ghi ticket, principal hay row thô.
- Thêm 4 test trong `src/tests/test_team_single.py`: không trả theo ticket (C-002, 5 seed), retry giữ 1 dòng ledger, trace không lộ secret/ticket, giới hạn bước.

### Bằng chứng

- Student matrix Shape B: `62 passed` (gồm T11, T12); test riêng: `4 passed`; cổng host `python -m pytest -q` xanh.
- Commit kỹ thuật: `cbc72cc40c1c9a8a2f23b82f69bd42fef937430b` trên nhánh `feature/single`, merge vào `main` qua PR #2.
- Báo cáo cá nhân: `report/team/2A202603585_TruongVietCong.md`.

