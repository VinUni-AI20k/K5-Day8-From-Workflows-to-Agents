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

## Bằng chứng bonus B3 của nhóm

Chạy `python -m bonus.reproduce` để tái lập smoke, toàn bộ pytest, benchmark, crash và evidence. Các file bonus do công cụ sinh:

- `bonus_public.json`: workflow/swarm/swarm_verified trên 14 claim × 5 seed.
- `bonus_adversarial.json`: cùng ba shape trên 16 claim có nhãn viết tay × 5 seed.
- `bonus_safety.json`: recount 750 trial trên hai corpus và năm shape; crash bổ sung 12/12.
- `bonus_trace_example.json`: trace và ledger thật của C-002 / seed 55 / swarm_verified.

Hai benchmark dùng CLI `lab8.benchmark --extra-shape`; hai file evidence cuối dùng `python -m bonus.evidence`. Lệnh đầy đủ và phân tích ở [bonus report](../../report/team/bonus_report.md). Đã có kết quả kiểm chứng local hidden trong hidden_summary.json.

## Bằng chứng hidden local

- `hidden_grade.json`: do lab8.benchmark với --labels tạo; log local đầy đủ, được gitignore.
- `hidden_selfcheck.json`: do lab8.benchmark trên student_drop không nhãn tạo; chỉ có status/trace/cost, không có pass rate.
- `hidden_summary.json`: do bonus.hidden_evidence tạo; metric, safety recount, 30 kịch bản crash hidden, source/pack SHA-256; không chứa ticket, labels hoặc PII.

Tái lập trong src/: `python -m bonus.hidden_evidence --pack D:/AIThucChien/DAY08/instructor/instructor`. Giữ pack bên ngoài repo. Tổng hợp này là kiểm chứng local bằng evaluator nguyên bản; giảng viên xác nhận điểm chính thức.
