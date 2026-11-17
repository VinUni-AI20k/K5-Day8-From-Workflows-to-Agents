# src/reports/

## Kết quả hiện tại — đủ bốn shape

Ngày đánh giá: 2026-11-17. Nhánh `thanh-ledger-evaluation`, mốc nguồn shape `4f2060dc4729fa13d235ef41d4ed88480331b4f8` sau merge orchestrator. Test recovery mới và tài liệu cuối đang chưa commit; chưa tuyên bố đã push bản nộp.

| Artifact | Nội dung | Kết quả |
| --- | --- | --- |
| benchmark.json | 4 shape × 14 claim × 5 seed = 280 trial | Workflow/single/orchestrator 70/70 mỗi shape; swarm 69/70 |
| crash.json | Suite chính của lab, chủ yếu host và một scenario swarm | 20/20 |
| research_ablation.json | Workflow bật/tắt draft, 140 trial; giữ report tại 175d770 vì workflow/helper không đổi | Mỗi variant 70/70; tổng tiết kiệm 70.40 VND mô phỏng |
| hidden_selfcheck.json | Tùy chọn nếu có student_drop | Chưa có dữ liệu hidden local, không tạo/bịa kết quả |

Bộ mặc định 195 passed; student 248 passed. Trong đó `tests/test_team_crash_recovery.py` có 24 test cho workflow/single/orchestrator (hai claim × ba crash point và hai scenario approval/shape); `tests/test_research_draft_ablation.py` có 72 test. Student xanh chấp nhận lỗi tham chiếu swarm C-002 seed 55; benchmark vẫn ghi trial đó fail.

ADR chọn `workflow`: cùng pass rate public với single/orchestrator, mức tự chủ thấp nhất và cost/success 28.862857 VND mô phỏng. Không suy ra đạt hidden >= 0.75. Hash ADR là nguồn shape được đánh giá, không phải commit tương lai của báo cáo.

## Lệnh tái tạo

Chạy trong `src/` với Python 3.11.9 của .venv:

```powershell
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m pytest -q -m student -o addopts=
./.venv/Scripts/python.exe -m lab8.crash_test --count 20 --out reports/crash.json
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
./.venv/Scripts/python.exe -m lab8.check_submission
```

Ablation (đã chạy tại giai đoạn 1–2, không chạy lại trong phiên hoàn thiện):

```powershell
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.research_draft_ablation:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

Chạy tuần tự: helper dùng scoped patch module workflow, không hỗ trợ gọi song song cùng process; khôi phục patch kể cả khi exception. Variant có tên/run id riêng. Research helper trong bonus/ không đồng nghĩa đăng ký bonus; không tạo bonus_report.md.

## Lịch sử và provenance

| Mốc | Trạng thái |
| --- | --- |
| 175d770 | Commit đóng góp giai đoạn 1–2 của Thành: baseline khi single/orchestrator còn stub, crash 20/20, ablation, 156 test mặc định |
| db22c3b | Mở rộng single: 164 test mặc định, 186 student không gồm orchestrator |
| 4f2060d | Merge orchestrator, giải quyết TEAM/benchmark bằng giữ đóng góp và chạy lại công cụ; 187 test mặc định, 248 student |
| Phiên hoàn thiện hiện tại, chưa commit | Mở rộng recovery đủ ba shape, 195 test mặc định, 248 student; tạo lại benchmark/crash và hoàn thiện ADR/tài liệu |

Baseline cũ còn trong Git: `git show 175d770:src/reports/benchmark.json`, `git show db22c3b:src/reports/benchmark.json`. Các con số stub trong đó là lịch sử, không phải trạng thái hiện tại. JSON hiện tại do công cụ tạo, không sửa tay hoặc ghép số liệu.

Run id xác định theo shape/claim/seed, không phải batch ID duy nhất. Test/benchmark chạy lại có thể ghi đè trace local cùng tên; khi kiểm trace cần tái tạo đúng lệnh. Commit JSON bằng chứng; không commit traces, SQLite, .venv hoặc student_drop. Chi phí mô phỏng, latency `unavailable`.

## Bàn giao

Phần evaluation/ADR của Thành đã đánh giá đủ ba shape. Sau khi tự review, thành viên commit phần test và tài liệu cuối; nhóm trưởng tích hợp nhánh vào main, chạy lại cổng kiểm tra trên bản nộp. Cập nhật thông tin commit bàn giao nếu có commit mới; giữ rõ hash nguồn benchmark và không bịa hash.

Kiểm tra cuối: `./.venv/Scripts/python.exe -m lab8.check_submission` đạt **0 FAIL, 1 WARN**. WARN duy nhất là thay đổi mới chưa commit; các shape, reports, ADR và research card qua kiểm tra. `git diff --check` không có lỗi whitespace. Không chỉnh checker để bỏ cảnh báo; cần commit thực tế trước bàn giao. Checker không xác nhận đã đạt hidden hoặc việc sử dụng nguồn thay thế đã được coach chấp thuận.

Mỗi thành viên tự xác nhận nội dung báo cáo cá nhân và nộp link repo trên LMS; checker không thay thế việc đọc bài hoặc chứng minh đã đạt hidden.
