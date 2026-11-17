# Team

## Thông tin nhóm

- Tên nhóm: 404
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-404-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: `https://github.com/DoLyHoangNam/K5-L3B-DAY08-404-FromWorkflowsToAgents`, nhánh `main`, commit chốt: `<TODO CP5>`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Đỗ Lý Hoàng Nam | 2A202603777 | dolyhoangnam13072005@gmail.com | DoLyHoangNam | Nhóm trưởng & Kiểm soát chất lượng QA (`main` / `qa-testing`) |
|   2 | Hoàng Thế Phong | 2A202603832 | phonghoangthe112@gmail.com | Hphong2305 | Chuyên viên Báo cáo & Dữ liệu (`docs-report`) |
|   3 | Nguyễn Văn Hậu | 2A202603932 | nguyenhau230303@gmail.com | common-maker | Developer 2 — Kiến trúc Single Agent, Shape B (`shape-single`) |
|   4 | Đoàn Công Hải | 2A202603739 | haidoan200426@gmail.com | rawser246 | Developer 1 — Kiến trúc Workflow, Shape A (`shape-workflow`) |
|   5 | Lê Ngọc Khánh | 2A202603804 | lekhanh2k5@gmail.com | lekhanh2k5 | Developer 3 — Kiến trúc Orchestrator, Shape C (`shape-orchestrator`) |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đỗ Lý Hoàng Nam | Nhóm trưởng & QA (`main` / `qa-testing`) | `<TODO sau khi commit>` | `src/tests/test_qa_must_pass.py` |
| Hoàng Thế Phong | Báo cáo & Dữ liệu (`docs-report`) | `<TODO>` | `<TODO>` |
| Nguyễn Văn Hậu | Dev 2 — Shape B `single` (`shape-single`) | `<TODO>` | `<TODO>` |
| Đoàn Công Hải | Dev 1 — Shape A `workflow` (`shape-workflow`) | `<TODO>` | `<TODO>` |
| Lê Ngọc Khánh | Dev 3 — Shape C `orchestrator` (`shape-orchestrator`) | `<TODO>` | `<TODO>` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/team/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`. (Copy từ `report/team/MSSV_HoTen.md` và giữ nguyên file mẫu.)

## 2A202603777_DoLyHoangNam

### Phần việc phụ trách

- Nhóm trưởng & Kiểm soát chất lượng (nhánh `main` / `qa-testing`): quản lý tiến độ, duyệt/merge PR vào `main`; chạy `pytest -q`, test must-pass/hidden self-check, chạy `crash_test` (CP4) & `benchmark` (CP5); chốt `TEAM.md` và viết test QA trong `src/tests/`.

### Đóng góp cụ thể

- Thiết lập môi trường, phân công 5 thành viên trong `TEAM.md`, viết bộ test QA must-pass/crash `src/tests/test_qa_must_pass.py`, quản lý merge PR và chạy benchmark/crash suite.

### Bằng chứng

- Test: `src/tests/test_qa_must_pass.py`
- Báo cáo cá nhân: `report/team/2A202603777_DoLyHoangNam.md`
- Commit / Report: `<TODO sau khi commit & chạy CP4/CP5>`

## 2A202603832_HoangThePhong

### Phần việc phụ trách

- Chuyên viên Báo cáo & Dữ liệu (nhánh `docs-report`): tổng hợp số liệu từ `src/reports/benchmark.json` và `crash.json`, hoàn thiện `report/team/decision_adr.md`, `report/team/research_card.md`, `report/team/group_report.md`, và thêm/sửa test trong `src/tests/`.

### Đóng góp cụ thể

- `<TODO>`

### Bằng chứng

- `<TODO>`

## 2A202603932_NguyenVanHau

### Phần việc phụ trách

- Developer 2 — Kiến trúc Single Agent, Shape B (nhánh `shape-single`): hiện thực `src/lab8/shapes/single.py` (vòng ReAct tối đa 8 bước, dùng tool đọc, gọi `durability.issue_refund` với `crash_at`, CP2 & CP3) và bổ sung test cho `single` trong `src/tests/`.

### Đóng góp cụ thể

- `<TODO>`

### Bằng chứng

- `<TODO>`

## 2A202603739_DoanCongHai

### Phần việc phụ trách

- Developer 1 — Kiến trúc Workflow, Shape A (nhánh `shape-workflow`): hiện thực `src/lab8/shapes/workflow.py` (các bước Python tĩnh, `compute_compensation`, gọi `durability.issue_refund` với `crash_at`, CP2 & CP3) và bổ sung test cho `workflow` trong `src/tests/`.

### Đóng góp cụ thể

- `<TODO>`

### Bằng chứng

- `<TODO>`

## 2A202603804_LeNgocKhanh

### Phần việc phụ trách

- Developer 3 — Kiến trúc Orchestrator, Shape C (nhánh `shape-orchestrator`): hiện thực `src/lab8/shapes/orchestrator.py` (tạo `handoff.v1` allowlist qua `make_handoff`, chạy `run_readonly_investigators`, trace sạch không lộ secret, gọi `durability.issue_refund` với `crash_at`, CP2 & CP3) và bổ sung test cho `orchestrator` trong `src/tests/`.

### Đóng góp cụ thể

- `<TODO>`

### Bằng chứng

- `<TODO>`
