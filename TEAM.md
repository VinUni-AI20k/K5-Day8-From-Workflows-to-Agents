# Team

## Thông tin nhóm

- Tên nhóm:Warden
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-Warden-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: https://github.com/DuyDo1007/K5-L3A-DAY08-Warden-FromWorkflowsToAgents

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Lê Xuân Hạ | 2A202603571 |hlee93698@gmail.com       |hlee93698-stack        | Ledger + evaluation |
|   2 | Đỗ Đắc Duy | 2A202603604 |ddduy7890@gmail.com       |[DuyDo1007](https://github.com/DuyDo1007)        | Shape orchestrator + handoff |
|   3 | Vũ Thanh Toàn | 2A202603654 | thanhtoana7hha@gmail.com | Kyo708 | Shape workflow + integration |
|   4 | Chu Thân Nhất | 2A202603649 | | | Shape single |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Vu Thanh Toan (2A202603654) | Shape workflow | `8300fcc3fb7f9bb5bf062e98b588b24809f0a111` | `tests/test_workflow_extra.py`: `test_workflow_ignores_delay_written_in_ticket`, `test_workflow_trace_has_no_secret_or_ticket` |
| Đỗ Đắc Duy (2A202603604) | Shape orchestrator + handoff | `d075c04a321488e3ad2bed762073ef2ad3f53bc2` | `tests/test_orchestrator.py`: `test_orchestrator_handoff_is_read_only_and_trace_is_sanitized` (commit `ad23c61`) |
| Chu Thân Nhất (2A202603649) | Shape single | `bb013891c8919658136be99e2a8b2dc8850d641d` | `tests/test_single_shape.py`: `test_single_uses_order_row_for_quote`, `test_single_early_returns_have_trace`, `test_single_propagates_crash_and_writes_trace` |
| Lê Xuân Hạ (2A202603571) | Ledger + evaluation | `50fe2f5297dced2cd787281fd24dd47dfa62e34c` | `src/tests/test_ledger_crash_and_gate.py` (16 test mới: crash point, cổng approval, trần, scope) |

## Cá nhân


## 2A202603654_VuThanhToan

### Phần việc phụ trách

- Shape A `workflow` (`src/lab8/shapes/workflow.py`) và integration.

### Đóng góp cụ thể

- Viết workflow cố định: đọc claim qua `get_claim_view`, `lookup_order`, quote từ order row bằng `compute_compensation` (bỏ qua số ngày trễ ghi trong ticket), gọi `durability.issue_refund` với quote đầy đủ, ghi trace ở mọi nhánh return.
- CP3: truyền `crash_at` vào host, ghi trace rồi `raise` lại `InjectedCrash`.
- Trace chỉ ghi 6 field order cần cho quote (`_TRACE_ORDER_FIELDS`), không ghi ticket hay principal.
- Thêm `src/tests/test_workflow_extra.py`.

### Bằng chứng

- Commit `8300fcc` (PR #2, nhánh `VuThanhToan-2A202603654`).
- Test: `test_workflow_ignores_delay_written_in_ticket`, `test_workflow_trace_has_no_secret_or_ticket` (chạy bằng `python -m pytest -q -o addopts= tests/test_workflow_extra.py`, xanh).
- Benchmark workflow: pass 1.000, pass^5 1.000, cost/success 27.86 (`src/reports/benchmark.json`). Đây là shape nhóm chọn trong `decision_adr.md`.
- Báo cáo chi tiết: `report/team/2A202603654_VuThanhToan.md` (đã hoàn thành).

## 2A202603649_ChuThanNhat

### Phần việc phụ trách

- Shape B `single` (`src/lab8/shapes/single.py`).

### Đóng góp cụ thể

- Vòng ReAct qua `lab8.runtime.run_react` với `max_steps=8`, chỉ tool đọc; quote từ order row và policy; sau vòng lặp code gọi `issue_refund` với quote đầy đủ.
- Mọi nhánh return đi qua `finish(...)`; ghi trace rồi `raise` lại `InjectedCrash`.
- Thêm `src/tests/test_single_shape.py`.

### Bằng chứng

- Commit `bb01389` (PR #1), `db783d4` (ghi đóng góp).
- Test: `test_single_uses_order_row_for_quote`, `test_single_early_returns_have_trace`, `test_single_propagates_crash_and_writes_trace`.
- Benchmark single: pass 1.000, pass^5 1.000, cost/success 38.50 (`src/reports/benchmark.json`).
- Báo cáo chi tiết: `report/team/2A202603649_ChuThanNhat.md`.

## 2A202603604_DoDacDuy 

### Phần việc phụ trách

- Shape C `orchestrator` + handoff (`src/lab8/shapes/orchestrator.py`).

### Đóng góp cụ thể

- Viết orchestrator và investigator: investigator chỉ có tool đọc, orchestrator gọi `durability.issue_refund`.
- Handoff dựng bằng `lab8.handoff.make_handoff`; trace ghi handoff đã sanitize, không ghi parent context.
- CP3: truyền `crash_at` vào host, ghi trace rồi `raise` lại `InjectedCrash`.
- Thêm `src/tests/test_orchestrator.py`.

### Bằng chứng

- Commit `d075c04` (orchestrator), `ad23c61` (test), PR #1 nhánh `duy`.
- Test: `test_orchestrator_handoff_is_read_only_and_trace_is_sanitized` (xanh).
- Benchmark orchestrator: pass 1.000, pass^5 1.000, cost/success 55.71 (`src/reports/benchmark.json`).
- Báo cáo chi tiết: `report/team/2A202603604_DoDacDuy.md`.

## 2A202603571_LeXuanHa

### Phần việc phụ trách

- Ledger + evaluation: kiểm chứng `durability.issue_refund`, crash suite (CP4), benchmark và phân tích metric (CP5), rà `TODO CP3` ở ba shape.

### Đóng góp cụ thể

- Thêm `src/tests/test_ledger_crash_and_gate.py` (16 test, chạy trong cổng host).
- Chạy crash suite `20/20`, benchmark mốc swarm, phân tích lỗi swarm T02 seed 55.
- Rà `TODO CP3` ở ba shape; benchmark 4 shape × 5 seed (`src/reports/benchmark.json`).
- Điền `decision_adr.md` (shape workflow theo quyết định nhóm) và các mục 1–5, 7, 8 của `group_report.md`.
- Research card R2 + ablation: `src/bonus/swarm_verified.py`, `src/tests/test_ablation_swarm_verified.py` (8 test), `src/reports/ablation_r2.json`.

### Bằng chứng

- `src/reports/crash.json` (20/20), `src/reports/benchmark.json`, `src/reports/benchmark_swarm.json`, run id `R-swarm-C-002-s55`, `R-workflow-C-007-s55`.
- Báo cáo chi tiết: `report/team/2A202603571_LeXuanHa.md`.
- Commit: `50fe2f5` (test + reports), `f721304` (ADR), commit research card tiếp theo trên nhánh `LeXuanHa-2A202603571`.
