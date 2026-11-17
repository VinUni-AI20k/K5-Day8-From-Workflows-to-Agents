# src/reports/

Mọi lệnh dưới đây chạy trong thư mục `src/`, nên file JSON được ghi vào `src/reports/`.

Nhóm **commit** các file do công cụ của lab sinh ra. Đây là bằng chứng nộp bài:

| File | Lệnh tạo | Bắt buộc |
| --- | --- | --- |
| `benchmark.json` | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` | Có |
| `crash.json` | `python -m lab8.crash_test --count 20 --out reports/crash.json` | Có |
| `hidden_selfcheck.json` | benchmark trên `student_drop/` (xem `src/README.md`, mục Tự kiểm trên bộ hidden) | Không |
| `bonus_*.json` | script bonus của nhóm | Chỉ khi làm bonus |

Không sửa tay file JSON. Giảng viên chạy lại đúng các lệnh trên trên máy chấm. Số không khớp thì mục Reproducibility mất điểm. `hidden_grade.json` chỉ giảng viên tạo và bị gitignore.

## Bằng chứng giữa kỳ — phần Thành, giai đoạn 1–2

Ngày chạy: 2026-11-17. Nhánh: `thanh-ledger-evaluation`, phát triển từ `main` commit `20b2fba`. Giai đoạn 1–2 đã được lưu tại commit `175d770`; sau đó merge main tại `1f7d89d`. Các số liệu trong đoạn checkpoint này là lịch sử, không thay cho kết quả sau merge ở dưới.

- Baseline cũ tại `175d770`: 4 shape × 14 claim × 5 seed = 280 trial. Khi đó single và orchestrator còn stub. Bản cũ có thể xem bằng `git show 175d770:src/reports/benchmark.json`; `benchmark.json` hiện được tạo lại sau merge single.
- `crash.json`: suite có sẵn đạt 20/20. Suite kiểm host và một kịch bản swarm; độ an toàn workflow được kiểm bổ sung ở `tests/test_team_crash_recovery.py`.
- `research_ablation.json`: 2 variant × 14 claim × 5 seed = 140 trial; phục vụ research card R4, không phải bài bonus.

Lệnh tái tạo ablation trong `src/`:

```powershell
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.research_draft_ablation:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

Chạy tuần tự: helper ablation dùng patch cục bộ trên module workflow, không hỗ trợ chạy song song trong cùng process. Patch được khôi phục kể cả khi crash; variant dùng run id riêng. Hai lời gọi official benchmark có thể ghi lại trace workflow cùng run id, nên không coi trace trong thư mục local là bản lưu bất biến của từng report. JSON là artifact commit; khi cần kiểm trace, chạy lại đúng lệnh.

Các JSON trên được công cụ tạo tự động. ADR và quyết định kiến trúc vẫn chưa chốt. Không suy ra ngưỡng pass hidden từ số liệu public.

Kiểm tra cuối giai đoạn 2: `python -m lab8.check_submission` còn **9 FAIL, 1 WARN**. Hai FAIL thuộc single/orchestrator còn stub; bảy FAIL thuộc ADR chưa chốt; WARN là thay đổi chưa commit. Benchmark, crash report và research card đã qua kiểm tra cấu trúc. Checker chỉ kiểm cột research card đã điền, không xác nhận giá trị khoa học của nguồn hoặc ablation.

Sau khi nhận orchestrator: mở rộng recovery test sang shape đó, chạy toàn bộ student test, tạo lại benchmark/crash report, hoàn thiện ADR với hash/run id thật, cập nhật báo cáo cuối rồi chạy checker về 0 FAIL. Không suy ra trạng thái push/merge phần Thành chỉ từ các commit local.

## Checkpoint hiện tại — sau merge single

Ngày 2026-11-17, sau merge `1f7d89d` trên `thanh-ledger-evaluation`. Code shape dùng để đánh giá là tại mốc merge này; phần cập nhật test/báo cáo đang chưa commit. Commit kỹ thuật giai đoạn trước của Thành là `175d770`.

- `benchmark.json` đã được công cụ tạo lại: 280 trial, workflow và single đều 70/70, swarm 69/70; orchestrator vẫn là stub (0/70). Kết quả baseline cũ nằm trong Git tại `175d770`, không còn là nội dung file hiện tại.
- `crash.json` được tạo lại, vẫn 20/20; suite chính kiểm host/swarm. Test recovery riêng được mở rộng từ 8 lên 16 cho workflow/single, kiểm ba crash point, mở lại kết nối, resume/retry, C-014 và approval.
- Bộ mặc định 164 passed, student không gồm orchestrator 186 passed. Không skip/xfailed orchestrator để tuyên bố cả bộ xanh; checkpoint này chủ động chỉ chạy ba shape đã triển khai.
- Workflow/single cost/success 28.862857 / 29.798571 VND mô phỏng. Bảng và nhận xét tạm thời ở `report/team/decision_adr.md`; bảy trường quyết định cuối vẫn để trống.
- Research card, helper và `research_ablation.json` giữ nguyên kết quả tại `175d770`; workflow/helper không thay đổi sau merge nên không chạy lại ablation trong checkpoint này.

Lệnh đã chạy trong `src/`, dùng Python 3.11.9 của `.venv`:

```powershell
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m pytest -q -m student -o addopts= -k 'not orchestrator'
./.venv/Scripts/python.exe -m lab8.crash_test --count 20 --out reports/crash.json
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Giữ nguyên giới hạn: JSON do công cụ sinh, giá mô phỏng, latency `unavailable`, chưa có kết quả hidden hoặc quyết định kiến trúc cuối. Chờ orchestrator để hoàn tất checklist ở trên.

Kiểm tra cuối checkpoint mới: `./.venv/Scripts/python.exe -m lab8.check_submission` → **8 FAIL, 1 WARN**. Một FAIL là orchestrator còn stub, bảy FAIL là các trường ADR cố ý chưa chốt; WARN là cập nhật chưa commit. `git diff --check` không có lỗi whitespace. Chưa commit/push cập nhật sau merge.
