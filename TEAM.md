# Team

## Thông tin nhóm

- Tên nhóm: 4 Thằng Sinh Viên
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: 

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hoàng Anh | 2A202603385 |       |        |         |
|   2 | Võ Huy Hoàng | 2A202603397 | 26ai.hoangvh4@vinuni.edu.vn | [ferr2764](https://github.com/ferr2764) | D — Test/Host, Durability & Benchmark Runner |
|   3 | Nguyễn Tuấn Hiếu | 2A202603374 |       |        |         |
|   4 | Phạm Hữu Đức | 2A202603380 |       |        |         |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Hoàng Anh | B — Single agent ReAct, ADR | 4b462c5 | src/tests/test_single_safety.py — kiểm thử ReAct budget, crash recovery và prompt injection |
| Võ Huy Hoàng | D — Test/Host, durability, đánh giá | d70fc4a | src/tests/test_durability_shapes.py — test_resume_other_crash_windows_keeps_one_refund (6 ca) |
| Nguyễn Tuấn Hiếu | | | |
| Phạm Hữu Đức | | | |

## Cá nhân

### Nguyễn Hoàng Anh — 2A202603385

- Phụ trách CP2: lập trình Shape B (Single Agent ReAct); CP3 & CP4: xử lý crash/idempotency, rà soát budget/tokens và trace an toàn; CP5: viết quyết định kiến trúc decision_adr.md.
- Đóng góp: hoàn thiện `src/lab8/shapes/single.py`, bổ sung bộ test `src/tests/test_single_safety.py` (7 tests), viết `report/team/decision_adr.md`.
- Bằng chứng: Single student matrix 62/62 pass, Single safety 7/7 pass, crash suite 20/20, benchmark run ID `R-single-C-001-s11`.
- Commit chứa test: `4b462c5`.
- Báo cáo cá nhân: [2A202603385_NguyenHoangAnh.md](report/team/2A202603385_NguyenHoangAnh.md).

### Võ Huy Hoàng — 2A202603397

- Phụ trách CP2: kiểm thử các shape; CP3: kiểm chứng idempotency và crash/resume; CP4: crash suite, approval, handoff, secret và trace.
- Bổ sung sáu ca kiểm thử trên workflow, single và orchestrator tại `before_effect` và `after_checkpoint`, kiểm tra không ghi refund hoặc audit hoàn tiền trùng sau resume/retry.
- Bằng chứng CP3: T11 đạt 4/4 và T12 đạt 4/4 trên bốn shape.
- Bằng chứng CP4: [crash.json](src/reports/crash.json) đạt 20/20; test approval 11 passed, public matrix 248 passed, handoff/secret/trace/workflow safety 18 passed và durability bổ sung 6 passed.
- Commit chứa test: `d70fc4a`. File crash CP4 chưa có commit trong lịch sử tại thời điểm cập nhật.
- Báo cáo cá nhân: [2A202603397_VoHuyHoang.md](report/team/2A202603397_VoHuyHoang.md).
- Việc tiếp theo CP5: chạy benchmark bốn shape với năm seed, cung cấp số liệu cho báo cáo/ADR và chạy `lab8.check_submission`.

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
