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

Ngày chạy: 2026-11-17. Nhánh: `thanh-ledger-evaluation`, phát triển từ `main` commit `20b2fba`. Đây là mốc nguồn ban đầu, không phải hash commit mới hoặc commit chốt. Code/test bổ sung của Thành chưa commit tại lúc ghi báo cáo.

- `benchmark.json`: baseline 4 shape × 14 claim × 5 seed = 280 trial. Workflow đã có; single và orchestrator còn stub. Hai shape này có pass rate 0 do chưa triển khai, không phải bằng chứng kiến trúc kém hơn. Phải tạo lại sau khi tích hợp đủ code.
- `crash.json`: suite có sẵn đạt 20/20. Suite kiểm host và một kịch bản swarm; độ an toàn workflow được kiểm bổ sung ở `tests/test_team_crash_recovery.py`.
- `research_ablation.json`: 2 variant × 14 claim × 5 seed = 140 trial; phục vụ research card R4, không phải bài bonus.

Lệnh tái tạo ablation trong `src/`:

```powershell
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.research_draft_ablation:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

Chạy tuần tự: helper ablation dùng patch cục bộ trên module workflow, không hỗ trợ chạy song song trong cùng process. Patch được khôi phục kể cả khi crash; variant dùng run id riêng. Hai lời gọi official benchmark có thể ghi lại trace workflow cùng run id, nên không coi trace trong thư mục local là bản lưu bất biến của từng report. JSON là artifact commit; khi cần kiểm trace, chạy lại đúng lệnh.

Các JSON trên được công cụ tạo tự động. ADR và quyết định kiến trúc vẫn chưa chốt. Không suy ra ngưỡng pass hidden từ số liệu public.

Kiểm tra cuối giai đoạn 2: `python -m lab8.check_submission` còn **9 FAIL, 1 WARN**. Hai FAIL thuộc single/orchestrator còn stub; bảy FAIL thuộc ADR chưa chốt; WARN là thay đổi chưa commit. Benchmark, crash report và research card đã qua kiểm tra cấu trúc. Checker chỉ kiểm cột research card đã điền, không xác nhận giá trị khoa học của nguồn hoặc ablation.

Sau khi nhận đủ hai shape: chạy toàn bộ student test, mở rộng test crash tích hợp sang hai shape, tạo lại benchmark/crash report, hoàn thiện ADR với hash/run id thật, cập nhật báo cáo cuối rồi chạy checker về 0 FAIL. Phần Thành hiện chưa commit/push và chưa merge vào main; không cần chờ hai shape để review/commit phần giai đoạn 1–2 này.
