# Kiểm chứng hidden — Problem Solver

## Phạm vi và cách chấm

Kết quả chấm local trên pack được cung cấp, dùng CLI benchmark và metric nguyên bản với `--labels hidden_labels.json`; bỏ qua `expected` mồi trong claim. Điểm chính thức do giảng viên xác nhận.

Pack giữ ngoài repo tại `D:/AIThucChien/DAY08/instructor/instructor`. Có 40 claim, seed 11/22/33/44/55, năm shape; SQLite mới cho mỗi trial. Không commit pack, labels, dữ liệu cá nhân hoặc trace. Summary chỉ giữ metric, mã trial, số đếm và checksum.

## Kết quả

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.00 | 4.53/5 |
| single | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 30.68 | 7.42/8 |
| orchestrator | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 49.41 | 6.47/7 |
| swarm | 194/200 | 0.9700 | 0.8500 | 0.8500–1.0000 | 0.003600 | 52.49 | 2.93/3 |
| swarm_verified | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 60.46 | 3.88/4 |

Hidden local: workflow 200/200 trial, pass rate 1.0000, pass⁵ 1.0000, variance 0.000000, 29.00 VND mô phỏng/success.

## Safety và durability

Recount độc lập 1000 trial: secret leak 0, PII leak 0, approval bypass 0, execution error 0, trace contract failure 0. Scanner kiểm artifact lẫn stdout, mọi secret và các field phone/address/internal_note/item_name trong world.

Crash hidden 30/30: năm shape × hai trường hợp (refund thường và hoàn phần chênh theo đơn) × ba điểm crash, seed 55. Mỗi lần crash phải thực sự xảy ra, resume/replay khớp nhãn riêng, chỉ có một effect và một committed audit. Host crash suite độc lập vẫn 20/20.

Verifier đọc kiểm chứng 185 lần, sửa 6 lần, số trial sửa quá một vòng 0.

## Phân tích và quyết định

Không cần sửa logic workflow, single, orchestrator hoặc verifier: cả bốn đạt 200/200 trên lần chạy đầu. Giữ nguyên swarm tham chiếu, gồm lỗi cố ý seed 55. Chỉ bổ sung công cụ đo và tài liệu; không đọc nhãn trong shape, không hardcode claim id và không sửa thước đo.

Swarm có 6 trial fail, tất cả seed 55; pass rate 0.97 và pass⁵ 0.85. Verifier đưa kết quả về 1.00/1.00, đổi lại chi phí 60.46 so với 29.00 VND/success của workflow (2.08 lần). Quyết định giữ workflow.

Gate local cho shape chọn: pass rate ≥ 0.75 đạt; điều kiện pass rate ≥ 0.80 cho B3 đạt; leak/bypass bằng 0; crash host 20/20 và kiểm bổ sung hidden 30/30. Điều này xác nhận điều kiện kỹ thuật quan sát được, không tự quy đổi thành điểm rubric hay điểm bonus.

## Tái lập

Chạy trong `src/`, sau khi cài requirements:

```powershell
python -m bonus.hidden_evidence --pack D:/AIThucChien/DAY08/instructor/instructor
python -m pytest -q -o addopts=
python -m lab8.crash_test --count 20 --out reports/crash.json
```

Tại gốc repo:

```text
python scripts/update_hidden_report.py
python -m presentation.build
```

`bonus.hidden_evidence` gọi `lab8.benchmark --labels` cho bản chấm và benchmark không nhãn cho student_drop, rồi recount safety/crash. `hidden_grade.json` là log chấm local đầy đủ, được gitignore. `hidden_selfcheck.json` không có pass rate vì không dùng nhãn. `hidden_summary.json` là bằng chứng tổng hợp có thể đi cùng báo cáo, chứa SHA-256 của nguồn, pack và bản chấm; không thay thế nhãn hoặc grader.

## Giới hạn

MockLLM, dữ liệu synthetic, latency unavailable. Bộ hidden nay đã được cung cấp nên kết quả là kiểm chứng trên pack này, không chứng minh tổng quát trên dữ liệu chưa từng thấy khác. Đã chạy 351 test hồi quy xanh. Code đã kiểm chứng nằm trong commit `bd5a602`; SHA-256 của các file nguồn khớp bằng chứng hidden. Các cập nhật hồ sơ sau rà soát cần được commit trước khi nộp.
