# Phân công nhóm ABCDE — Lab 8

Thông tin thành viên và bảng đóng góp nằm ở [TEAM.md](TEAM.md). File này chỉ ghi ai làm gì, khi nào.

## Nguyên tắc

- **Chia theo phần việc, không chia theo checkpoint.** Mỗi người giữ một phần từ CP2 đến CP5. Checkpoint là mốc để cả nhóm kiểm tiến độ.
- Ai viết shape nào thì tự sửa shape đó khi fail T11, T12 hay crash suite.
- Mỗi người phải có **ít nhất 1 commit có nội dung + ít nhất 1 test** (mục C8 trong [RUBRIC.md](RUBRIC.md)).

## Vai

| Người | Phụ trách | Ghi chú |
| --- | --- | --- |
| **Vũ Quang Minh** (nhóm trưởng) | Workflow (A) + integration | Workflow gần giống `swarm_reference.py` bỏ khối `REFERENCE_WEAKNESS`. Xong sớm thì hỗ trợ Quân |
| **Nguyễn Công Quân** | Single agent (B) | Shape khó nhất: tự viết `decide()` cho `run_react`, tối đa 8 bước, chỉ tool đọc |
| **Hồ Anh Dũng** | Orchestrator (C) + handoff + kiểm secret trong trace | Swarm đã có mẫu `make_handoff` và `run_readonly_investigators` |
| **Trần Việt Thịnh** | Ledger/policy/crash + đo đạc (benchmark, ADR) | Viết test kiểm bài cả nhóm, chạy crash suite và benchmark |

## Theo checkpoint

Mọi lệnh chạy trong `src/`.

| Mốc | Minh | Quân | Dũng | Thịnh |
| --- | --- | --- | --- | --- |
| **CP2** 13:45 | Viết `workflow.py`, push sớm để nhóm xem làm mẫu | Viết `single.py` | Viết `orchestrator.py` | Viết test approval hỏng, approval của claim khác, đơn đã hoàn đủ; chạy trên cả 3 shape |
| *Tự kiểm CP2* | `-k workflow` ra 62 passed | `-k single` ra 62 passed | `-k orchestrator` ra 62 passed | `python -m pytest -q` vẫn xanh |
| **CP3** 14:30 | Thêm `crash_at` vào workflow; review và merge PR | Thêm `crash_at` vào single | Thêm `crash_at`; trace chỉ ghi handoff đã sanitize | Chạy crash/resume trên 3 shape, báo lỗi cho từng người |
| **CP4** 15:30 | Hỗ trợ Quân nếu single chưa xong | Sửa single nếu còn fail; bắt đầu research card | Quét `traces/` tìm `CANARY_SECRET_*` và PII | `python -m lab8.crash_test --count 20 --out reports/crash.json` đạt **20/20** |
| **CP5** 16:15 | Tổng hợp group report, chốt commit hash, `python -m lab8.check_submission` ra 0 FAIL | Ablation + `research_card.md` | `decision_adr.md` mục "Trace và bằng chứng" | Benchmark 4 shape × 5 seed, tự kiểm hidden, điền số liệu `decision_adr.md` |

Lệnh tự kiểm một shape (mỗi lệnh chọn đúng 62 test):

- Workflow: `python -m pytest -q -m student -o addopts= -k workflow`
- Orchestrator: `python -m pytest -q -m student -o addopts= -k orchestrator`
- Single: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`. **Không dùng `-k single`**: tên hàm `test_public_single_run_cases` có chữ "single" nên lệnh đó chọn 242 test của cả 4 shape.

## Báo cáo

| Phần | Người viết |
| --- | --- |
| `report/team/group_report.md` mục 1, 2, 6 và tổng hợp | Minh |
| `group_report.md` mục 3 (Giải pháp) | Mỗi người viết phần shape/vai của mình |
| `group_report.md` mục 4 (Kết quả), 7 (Hạn chế) | Thịnh |
| `group_report.md` mục 5 (Khó khăn), 8 (Tài liệu tham khảo) | Dũng, Quân |
| `report/team/decision_adr.md` | Thịnh (số liệu), Dũng (trace), Minh (commit hash) |
| `report/team/research_card.md` | Quân |
| `report/team/<MSSV>_<HoTen>.md` | Mỗi người tự viết, copy từ `MSSV_HoTen.md` |
| Cột Commit + Test trong bảng đóng góp `TEAM.md` | Mỗi người tự điền dòng của mình |

## Quy ước Git

- Mỗi người một nhánh: `feat/workflow`, `feat/single`, `feat/orchestrator`, `feat/ledger-tests`. Xong thì mở PR vào `main`; Minh merge khi `python -m pytest -q` còn xanh.
- Mỗi người chỉ sửa file shape của mình. **Không tạo file helper dùng chung** cho các shape: grader hidden chỉ lấy 3 file shape và `src/bonus/`, file khác bị bỏ qua nên shape sẽ lỗi import.
- Không sửa `src/lab8/metrics.py`, `durability.py`, `policy.py`, `src/config/`, `src/data/`. Không sửa tay JSON trong `src/reports/`.
- Không commit `traces/`, `*.sqlite`, `student_drop/`, `.venv/`.

## Lưu ý khi viết test

Test gọi shape sẽ đỏ khi shape còn là stub, và kéo `python -m pytest -q` đỏ theo. Viết test **sau khi** shape đã 62 passed, hoặc tạm gắn `@pytest.mark.student` rồi bỏ marker khi shape xong.
