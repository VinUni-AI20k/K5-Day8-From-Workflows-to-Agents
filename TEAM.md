# Team

## Thông tin nhóm

- Tên nhóm: 4 Thằng Sinh Viên
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents`
- URL repo: https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents
- Nhánh nộp: `main`.
- Commit mã nguồn đã kiểm thử và đo CP5: `96ab7201c69c66c532e779e0ef05f9a7ecf2362a`.
- Commit chốt mã nguồn: `c21031b`, khớp `report/team/decision_adr.md`. Các file mã nguồn được đo không thay đổi so với `96ab720`; tài liệu và bằng chứng CP5 được bổ sung bằng các commit tiếp theo.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Hoàng Anh | 2A202603385 | Chưa khai báo | [hoanganhchimxanh](https://github.com/hoanganhchimxanh) | B — Single Agent; quyết định kiến trúc và ADR |
|   2 | Võ Huy Hoàng | 2A202603397 | 26ai.hoangvh4@vinuni.edu.vn | [ferr2764](https://github.com/ferr2764) | D — Test/Host, Durability & Benchmark Runner |
|   3 | Nguyễn Tuấn Hiếu | 2A202603374 | tuanhieu1162004@gmail.com (Git) | [tuanhieu1162004](https://github.com/tuanhieu1162004) | A — Workflow & Lead tổng hợp; báo cáo nhóm và TEAM |
|   4 | Phạm Hữu Đức | 2A202603380 | phamduc31103@gmail.com | [ducpahm](https://github.com/ducpahm) | C — Orchestrator & Research; handoff, research card và ablation |

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
| Võ Huy Hoàng | D — Test/Host, durability, approval và bằng chứng CP4 | `d70fc4a`, `96ab720`, `791521c` | `src/tests/test_durability_shapes.py::test_resume_other_crash_windows_keeps_one_refund` (6 ca, không có marker student) |
| Nguyễn Tuấn Hiếu | A — Workflow, idempotency, checkpoint và tổng hợp | `28717d8`, `33d04f3` | `src/tests/test_workflow_safety.py::test_workflow_rejects_approval_borrowed_from_another_claim`; `src/tests/test_workflow_safety.py::test_workflow_missing_checkpoint_replays_partial_refund_without_double_pay` (file có 9 ca, không gắn marker student) |
| Phạm Hữu Đức | C — Orchestrator và tool đọc qua handoff | `8966ddd` | `src/tests/test_orchestrator.py`: `test_orchestrator_c001_resolves`, `test_orchestrator_missing_order_needs_info`, `test_orchestrator_unknown_claim_fails` (3 ca) |

Các commit có thật trong lịch sử `main`. Phân công ở trên không được dùng thay bằng chứng hoàn thành; bảng đóng góp chỉ ghi code và test đã có.

## Trạng thái tích hợp CP5

- Lần chạy tích hợp trên commit `96ab720` đạt **327 passed**.
- `src/reports/crash.json` đã được D đưa vào `96ab720`, đạt **20/20**.
- A đã tổng hợp benchmark trong [báo cáo nhóm](report/team/group_report.md). D đã chạy và xác nhận benchmark bốn shape × 14 claim × 5 seed, phân tích trial fail duy nhất của swarm. `src/reports/benchmark.json` đã nằm trong Git từ `bfd4ee7`.
- B đã hoàn thiện `report/team/decision_adr.md`: chọn workflow, commit chốt hiện ghi `c21031b`, run id `R-workflow-C-001-s11`.
- C đã cập nhật `report/team/research_card.md`; phần kiểm tra định dạng tài liệu đã qua checker trong lần kiểm tra mới nhất.
- D đã tự kiểm `student_drop/`: [hidden_selfcheck.json](src/reports/hidden_selfcheck.json) có 600 trial (3 shape × 40 claim × 5 seed), tất cả `reason = unlabeled`, không có lỗi runtime hoặc cảnh báo trace/leak từ bộ tự kiểm. Không có nhãn nên chưa có pass rate hidden chính thức; không commit `student_drop/`.
- A chạy lại lệnh self-check ngày 17/11/2026 trên bản sao giữ nguyên SHA256 của hai file gốc: kết quả khớp JSON đã commit, mỗi shape 200 trial, không có lỗi runtime hoặc cảnh báo trace/leak. Cổng host mặc định đạt **79 passed, 248 deselected**; 9 ca trong `test_workflow_safety.py` không có marker `student` nên chạy trong cổng này.
- Checker chạy lại ngày 17/11/2026 đạt **0 FAIL, 1 WARN**; cảnh báo tại thời điểm kiểm tra do file chưa commit. Đây là kiểm tra định dạng bài nộp, không phải điểm hidden.
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
- CP5: phụ trách research card và ablation; đã hoàn thiện [research_card.md](report/team/research_card.md) với bài đo R2 (MAST NeurIPS 2025).
- Báo cáo cá nhân: [2A202603380_PhamHuuDuc.md](report/team/2A202603380_PhamHuuDuc.md).

### Võ Huy Hoàng — 2A202603397

- Phụ trách CP2: kiểm thử các shape; CP3: kiểm chứng idempotency và crash/resume; CP4: crash suite, approval, handoff, secret và trace.
- Bổ sung sáu ca kiểm thử trên workflow, single và orchestrator tại `before_effect` và `after_checkpoint`, kiểm tra không ghi refund hoặc audit hoàn tiền trùng sau resume/retry.
- Bằng chứng CP3: T11 đạt 4/4 và T12 đạt 4/4 trên bốn shape.
- Bằng chứng CP4: [crash.json](src/reports/crash.json) đạt 20/20; test approval 11 passed, public matrix 248 passed, handoff/secret/trace/workflow safety 18 passed và durability bổ sung 6 passed.
- Commit chứa test: `d70fc4a`. File crash và bằng chứng CP4 được đưa vào `96ab720`.
- Commit `791521c` (Võ Huy Hoàng) bỏ marker `student` để test đóng góp chạy trong cổng host mặc định; chạy riêng đạt 6 passed in 0.37s.
- Báo cáo cá nhân: [2A202603397_VoHuyHoang.md](report/team/2A202603397_VoHuyHoang.md).
- CP5: tạo [benchmark.json](src/reports/benchmark.json) với 4 shape × 14 claim × 5 seed (280 trial); ba shape nhóm viết đạt 70/70 mỗi shape, swarm đạt 69/70. Phân tích trial fail `R-swarm-C-002-s55`, tổng hợp bảng số liệu và đề xuất workflow theo kết quả public.
- Chạy toàn bộ test trước benchmark: 327 passed in 9.89s.
