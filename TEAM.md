# Team

## Thông tin nhóm

- Tên nhóm: Nhom2AE
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/Neronmen/K5-L3B-DAY08-Nhom2AE-FromWorkflowsToAgents, nhánh `main` / `2A202603774_NguyenNgocNinh`, commit chốt: `c8d9515` (ghi trong `report/team/decision_adr.md`)

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Nguyên Khoa | 2A202603795 | pnkvlog1508@gmail.com | Neronmen | Integration + 3 shape (workflow, single, orchestrator) + crash/benchmark |
|   2 | Nguyễn Ngọc Ninh | 2A202603774 | sevenminutes2311@gmail.com | sevenminutes2311-creator | Evaluation + test policy gate + ADR + research card + báo cáo nhóm |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Nguyên Khoa | Integration, 3 shape, crash, benchmark | `75ae9e4`, `19cd820` | `src/tests/test_team_shapes_safety.py` (15 test: crash 3 điểm × 3 shape, ticket nói dối seed 55, quét secret/PII trong trace) |
| Nguyễn Ngọc Ninh | Evaluation, policy gate test, ADR, research card, báo cáo nhóm | `9e8f63a`, `c8d9515` | `src/tests/test_team_policy_gate.py` (12 test: C-004 thiếu order_id, C-013 đơn đã hoàn đủ + audit policy_denied, C-014 hoàn phần chênh 120k, C-007/C-008 cổng approval × 3 shape) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603795_PhamNguyenKhoa

### Phần việc phụ trách

- Integration, ba shape `workflow` / `single` / `orchestrator`, crash suite, benchmark.

### Đóng góp cụ thể

- Cài ba shape theo contract (`finish()`, quote đầy đủ, `crash_at` truyền vào host).
- Thêm `src/tests/test_team_shapes_safety.py` (15 test).
- Sinh `src/reports/benchmark.json` và `src/reports/crash.json`.

### Bằng chứng

- Commit `75ae9e4`, `19cd820`; báo cáo chi tiết: `report/team/2A202603795_PhamNguyenKhoa.md`.

## 2A202603774_NguyenNgocNinh

### Phần việc phụ trách

- Kiểm thử cổng policy & trần hoàn tiền theo đơn, đánh giá kết quả benchmark/crash, viết ADR (`decision_adr.md`), phiếu nghiên cứu (`research_card.md`) và báo cáo nhóm (`group_report.md`).

### Đóng góp cụ thể

- Thêm `src/tests/test_team_policy_gate.py` (12 test cho 3 shape `workflow`, `single`, `orchestrator` trên các ca `C-004`, `C-013`, `C-014`, `C-007`, `C-008`).
- Phân tích số liệu từ `src/reports/benchmark.json` và `src/reports/crash.json`, hoàn thiện `report/team/decision_adr.md`, `report/team/research_card.md` (R2 — MAST failure taxonomy) và `report/team/group_report.md`.

### Bằng chứng

- Commit `9e8f63a`; báo cáo chi tiết: `report/team/2A202603774_NguyenNgocNinh.md`.
