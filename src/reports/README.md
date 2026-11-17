# src/reports/

Mọi lệnh dưới đây chạy trong thư mục `src/`, nên file JSON được ghi vào `src/reports/`.

Nhóm **commit** các file do công cụ của lab sinh ra. Đây là bằng chứng nộp bài:

| File | Lệnh tạo | Bắt buộc |
| --- | --- | --- |
| `benchmark.json` | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` | Có |
| `crash.json` | `python -m lab8.crash_test --count 20 --out reports/crash.json` | Có |
| `safety.json` | `python -m tests.evaluate_safety --out reports/safety.json` | Bằng chứng nhóm bổ sung: ledger, trace, secret/PII và stdout/stderr trên public có nhãn |
| `evaluation_ablation.json` | `python -m tests.evaluation_ablation --out reports/evaluation_ablation.json` | Ablation CP5 của nhóm: bật/tắt riêng draft call của workflow |
| `hidden_selfcheck.json` | benchmark trên `student_drop/` (xem `src/README.md`, mục Tự kiểm trên bộ hidden) | Không |
| `bonus_*.json` | script bonus của nhóm | Chỉ khi làm bonus |

Không sửa tay file JSON. Giảng viên chạy lại đúng các lệnh trên trên máy chấm. Số không khớp thì mục Reproducibility mất điểm. `hidden_grade.json` chỉ giảng viên tạo và bị gitignore.

Trên máy Windows của Chu, tạo venv bằng Python 3.12 rồi dùng `.\.venv\Scripts\python.exe` thay cho `python` trong các lệnh trên (Python hệ thống mặc định là 3.15). Hai runner bổ sung chỉ dùng thư viện chuẩn và harness của lab, không thay đổi host hoặc shape.

Safety runner dùng nhãn public để kiểm approval bypass, không phải grader hidden. Ablation lưu hai báo cáo theo cùng `(claim_id, seed, run_id)`; trace bị ghi lại bởi lần chạy sau, vì vậy dùng các nhánh JSON để so sánh số liệu. Chất lượng lời phản hồi và latency không được chấm.
