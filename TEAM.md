# Team

## Thông tin nhóm

- Tên nhóm: Dota
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-Dota-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/phungtr/K5-L3B-DAY08-Dota-FromWorkflowsToAgents · nhánh `main` · commit chốt: _(điền cuối)_

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phùng Quang Trà |2A202604094|traquangphung@gmail.com|phungtr| Nhóm trưởng · workflow (A) + integration |
|   2 | Vũ Nam Khánh |2A202604112|khanhvnm03@gmail.com|khanhvnm| single agent (B) |
|   3 | Nguyễn Tuấn Anh|2A202604089|capntryisreal@gmail.com|TuanAnhNg131| orchestrator (C) + handoff |
|   4 | Phạm Duy Thành |2A202604075|thanhteyv2@gmail.com|thanhtey1234| ledger/crash + evaluation (benchmark, ADR) |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phùng Quang Trà | workflow (A) + integration | `f0fb63f` | `src/tests/test_workflow_shape.py` (22 test) |
| | single agent (B) | | |
| | orchestrator (C) + handoff | | |
| Phạm Duy Thành | ledger/crash + evaluation | Chưa commit — nhánh `thanh-ledger-evaluation`, base `20b2fba` | `src/tests/test_team_crash_recovery.py` (8 test), `src/tests/test_research_draft_ablation.py` (72 test) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Mỗi thành viên điền mục của mình dưới đây (đổi `MSSV_HoTen` thành MSSV và họ tên không dấu).

## Thành viên 1 — 2A202604094_PhungQuangTra

### Phần việc phụ trách

- Shape A `workflow` (`src/lab8/shapes/workflow.py`) + integration

### Đóng góp cụ thể

- Viết shape `workflow` theo 7 bước cố định: đọc claim qua `get_claim_view` → thiếu `order_id` thì `needs_info` → `lookup_order` (không thấy/không sở hữu thì `escalated`) → quote bằng `compute_compensation` → quote 0 thì `denied` → quote > 0 thì gọi `durability.issue_refund` với quote đầy đủ → `resolved` / `denied` / `failed` (conflict).
- Ranh giới code/model: tiền do code tính; MockLLM chỉ được gọi 1 lần để soạn câu trả lời, prompt chỉ có `status` và số tiền, không chứa ticket. Số ngày trễ ghi trong ticket bị bỏ qua.
- Durability: truyền `crash_at` vào `issue_refund`; khi `InjectedCrash` thì ghi trace rồi raise tiếp, không nuốt lỗi.
- Trace: chỉ ghi field đã qua allowlist; không ghi ticket, `parent_secret`, header.
- Thêm 22 test trong `src/tests/test_workflow_shape.py`: ticket chèn lệnh không làm tăng tiền (5 seed), output của model không quyết số tiền, claim không tồn tại trả `failed` có trace hợp lệ, gọi lại với số tiền khác thì `amount_conflict` và giữ dòng cũ, trace của 14 claim public không lộ secret/header/ticket.

### Bằng chứng

- Commit [`f0fb63f`](https://github.com/phungtr/K5-L3B-DAY08-Dota-FromWorkflowsToAgents/commit/f0fb63f) (nhánh `Phungtr-04094`).
- `python -m pytest -q -m student -o addopts= -k workflow` → 62 passed.
- `python -m pytest -q` → 76 passed (cổng host xanh, gồm 22 test mới).
- `python -m lab8.check_submission` → `[ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11`.
- Báo cáo cá nhân: [report/team/2A202604094_PhungQuangTra.md](report/team/2A202604094_PhungQuangTra.md).

**Nhật ký integration**

| Lần | Ngày | Merge vào `main` | Cổng host `pytest -q` | Ma trận student | `check_submission` |
| --- | --- | --- | --- | --- | --- |
| 1 | 2026-11-17 | `Phungtr-04094` → `main`, fast-forward tới `f0fb63f`, không conflict | 76 passed | 124 passed / 124 failed (workflow 62/62, swarm 62/62; 124 fail là của `single`, `orchestrator` chưa merge) | 12 FAIL (2 shape chưa có; chưa có benchmark, crash, ADR, research card) |


## Thành viên 2 — MSSV_HoTen

### Phần việc phụ trách

- Shape B `single` (`src/lab8/shapes/single.py`)

### Đóng góp cụ thể

-

### Bằng chứng

-

## Thành viên 3 — MSSV_HoTen

### Phần việc phụ trách

- Shape C `orchestrator` + handoff (`src/lab8/shapes/orchestrator.py`)

### Đóng góp cụ thể

-

### Bằng chứng

-

## Thành viên 4 — 2A202604075_PhamDuyThanh

### Phần việc phụ trách

- Ledger/crash + evaluation (`reports/crash.json`, `reports/benchmark.json`, ADR, research card)

### Đóng góp cụ thể

- Giai đoạn 1–2 (2026-11-17): bổ sung 8 test crash/retry/approval cho workflow, kiểm đủ ba crash point, mở lại kết nối, resume và retry nhiều lần; C-014 chỉ trả thêm 120.000 đồng.
- Thêm helper ablation `workflow_no_draft` và 72 test về kết quả nghiệp vụ, accounting, trace và khôi phục patch. Helper dùng cho research card bắt buộc, không đăng ký bonus.
- Tạo baseline 280 trial bằng benchmark chính thức, crash report 20/20 và ablation 140 trial; điền research card R4 cùng phần kết quả ban đầu của báo cáo nhóm.
- ADR, benchmark cuối và kiểm thử tích hợp single/orchestrator chờ hai shape được merge. Không sửa code của thành viên khác hoặc thước đo của lab.
- Code và tài liệu giai đoạn này được soạn với trợ lý Codex theo yêu cầu; thành viên cần tự đọc, chạy lại và bổ sung tự đánh giá trước khi nộp.

### Bằng chứng

- Test mới: 80 passed. Toàn bộ test mặc định: 156 passed; student workflow/swarm: 124 passed.
- `src/reports/crash.json`: 20/20. Đây là crash suite host/swarm; test riêng bổ sung bằng chứng workflow.
- `src/reports/research_ablation.json`: mỗi variant 70/70 pass; cost/success 28.862857 → 27.857143 VND mô phỏng.
- Báo cáo cá nhân: [report/team/2A202604075_PhamDuyThanh.md](report/team/2A202604075_PhamDuyThanh.md).
- Commit kỹ thuật: chưa tạo; base `20b2fba` thuộc bản main được kiểm tra, không phải commit đóng góp của Thành. Bổ sung hash thật sau khi commit.
