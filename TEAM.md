# Team

## Thông tin nhóm

- Tên nhóm: 4 Thằng Sinh Viên
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents`
- URL repo: https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents
- Nhánh nộp: `main`.
- Commit mã nguồn đã kiểm thử và đo CP5: `96ab7201c69c66c532e779e0ef05f9a7ecf2362a`.
- Commit chốt mã nguồn: `96ab720`, khớp `report/team/decision_adr.md` do B cập nhật trong `c21031b`. Tài liệu và bằng chứng CP5 được bổ sung bằng các commit tiếp theo.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hoàng Anh | 2A202603385 | Chưa khai báo | [hoanganhchimxanh](https://github.com/hoanganhchimxanh) | B — Single Agent; quyết định kiến trúc và ADR |
|   2 | Võ Huy Hoàng | 2A202603397 | 26ai.hoangvh4@vinuni.edu.vn | [ferr2764](https://github.com/ferr2764) | D — Test/Host, Durability & Benchmark Runner |
|   3 | Nguyễn Tuấn Hiếu | 2A202603374 | tuanhieu1162004@gmail.com (Git) | Chưa khai báo | A — Workflow & Lead tổng hợp; báo cáo nhóm và TEAM |
|   4 | Phạm Hữu Đức | 2A202603380 | phamduc31103@gmail.com (Git) | Chưa khai báo | C — Orchestrator & Research; handoff, research card và ablation |

Email ghi `(Git)` lấy từ author commit; trường chưa có bằng chứng được đánh dấu `Chưa khai báo` để chính thành viên xác nhận, không suy đoán tài khoản.

## Phân công CP3–CP5

| Người | Sở hữu kỹ thuật CP3–CP4 | Sở hữu tài liệu và báo cáo CP5 |
| --- | --- | --- |
| A — Nguyễn Tuấn Hiếu | Shape A: retry/crash, checkpoint, approval/policy edge cases | `report/team/group_report.md`, `TEAM.md` |
| B — Nguyễn Hoàng Anh | Shape B: retry/crash, giới hạn bước, budget/token | `report/team/decision_adr.md`: lựa chọn kiến trúc bằng số liệu |
| C — Phạm Hữu Đức | Shape C: handoff allowlist, tool chỉ đọc, trace/PII | `report/team/research_card.md`: nguồn, hypothesis và một ablation |
| D — Võ Huy Hoàng | Crash suite 20/20, T11/T12 và durability trên ba shape | `src/reports/benchmark.json`, kiểm tra bằng `lab8.check_submission` |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Hoàng Anh | B — Single, safety, budget/token và ADR | `c47102a`, `4b462c5`, `c21031b` | `src/tests/test_single_safety.py`: unknown claim, budget/token, injection và ba cửa sổ crash (7 ca) |
| Võ Huy Hoàng | D — Test/Host, durability, approval và bằng chứng CP4 | `d70fc4a`, `96ab720` | `src/tests/test_durability_shapes.py::test_resume_other_crash_windows_keeps_one_refund` (6 ca) |
| Nguyễn Tuấn Hiếu | A — Workflow, idempotency, checkpoint và tổng hợp | `28717d8`, `33d04f3` | `src/tests/test_workflow_safety.py`: approval sai claim, injection, ba cửa sổ crash, mất checkpoint và amount conflict (9 ca) |
| Phạm Hữu Đức | C — Orchestrator và tool đọc qua handoff | `8966ddd` | `src/tests/test_orchestrator.py`: `test_orchestrator_c001_resolves`, `test_orchestrator_missing_order_needs_info`, `test_orchestrator_unknown_claim_fails` (3 ca) |

Các commit có thật trong lịch sử `main`. Phân công ở trên không được dùng thay bằng chứng hoàn thành; bảng đóng góp chỉ ghi code và test đã có.

## Trạng thái tích hợp CP5

- Lần chạy tích hợp trên commit `96ab720` đạt **327 passed**.
- `src/reports/crash.json` đã được D đưa vào `96ab720`, đạt **20/20**.
- A đã tổng hợp benchmark bốn shape × 14 claim × 5 seed trong [báo cáo nhóm](report/team/group_report.md), từ lệnh chuẩn thực chạy tại máy A. File JSON local chưa nằm trong lịch sử Git ở phần việc A; D kiểm tra/tái chạy và commit `src/reports/benchmark.json`.
- B đã hoàn thiện `report/team/decision_adr.md` trong `c21031b`: chọn workflow, commit mã nguồn `96ab720`, run id `R-workflow-C-001-s11`.
- C cần hoàn thiện `report/team/research_card.md`, gồm một ablation thực chạy và giới hạn kết luận.
- Sau khi tích hợp ADR `c21031b`, lần chạy `lab8.check_submission` tại máy A đọc được benchmark local, crash và ADR; còn **1 FAIL** do research card trống và **1 WARN** vì file chưa commit. D cần chạy lại sau tích hợp để đạt **0 FAIL**.
- Workspace máy A chưa có `student_drop/`; chưa ghi nhận hidden self-check hoặc điểm hidden.
- Mỗi thành viên xác nhận thông tin cá nhân, bổ sung báo cáo riêng và tự nộp cùng link repo trên LMS. Trạng thái này chưa xác nhận bài nhóm đã sẵn sàng nộp.

## Cá nhân

### Nguyễn Tuấn Hiếu — 2A202603374

- CP2: hoàn thiện workflow, chỉ dùng code tính tiền; mọi ghi refund qua host.
- CP3: kiểm chứng ba cửa sổ crash; mất checkpoint vẫn nhận ra refund trong ledger, không hoàn trùng hoặc tạo audit committed lần hai.
- Test: `src/tests/test_workflow_safety.py`; chi tiết [cp3_workflow.md](report/team/cp3_workflow.md).
- CP5: tổng hợp `group_report.md`, phân công và bảng đóng góp trong `TEAM.md` bằng commit/test/số liệu thực tế.
- Báo cáo cá nhân: [2A202603374_NguyenTuanHieu.md](report/team/2A202603374_NguyenTuanHieu.md).

### Nguyễn Hoàng Anh — 2A202603385

- CP2: hoàn thiện single agent với vòng ReAct giới hạn 8 bước.
- CP3: bổ sung test secret/injection, budget/token và crash/resume của single.
- CP5: đã cập nhật ADR trong `c21031b`, chọn workflow và chốt commit mã nguồn `96ab720` với số liệu public.
- Báo cáo cá nhân cần tạo riêng: `report/team/2A202603385_NguyenHoangAnh.md`.

### Phạm Hữu Đức — 2A202603380

- CP2: hoàn thiện orchestrator và ba test cho resolved, needs_info, unknown claim.
- Handoff qua `make_handoff`, investigator chỉ có tool đọc; orchestrator chuyển quote đầy đủ cho host.
- CP5: phụ trách research card và ablation; chưa ghi nhận file hoàn thiện ở snapshot đo.
- Báo cáo cá nhân cần tạo riêng: `report/team/2A202603380_PhamHuuDuc.md`.

### Võ Huy Hoàng — 2A202603397

- Phụ trách CP2: kiểm thử các shape; CP3: kiểm chứng idempotency và crash/resume; CP4: crash suite, approval, handoff, secret và trace.
- Bổ sung sáu ca kiểm thử trên workflow, single và orchestrator tại `before_effect` và `after_checkpoint`, kiểm tra không ghi refund hoặc audit hoàn tiền trùng sau resume/retry.
- Bằng chứng CP3: T11 đạt 4/4 và T12 đạt 4/4 trên bốn shape.
- Bằng chứng CP4: [crash.json](src/reports/crash.json) đạt 20/20; test approval 11 passed, public matrix 248 passed, handoff/secret/trace/workflow safety 18 passed và durability bổ sung 6 passed.
- Commit chứa test: `d70fc4a`. File crash và bằng chứng CP4 được đưa vào `96ab720`.
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
