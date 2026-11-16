# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash:
- Run id dẫn chứng: R-workflow-C-001-s11; đối chứng lỗi R-swarm-C-002-s55; src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0 (70 public trial, 14 claim × 5 seed)
- Cost per success (mô phỏng, VND): 27.857142857142858
- Crash safety: 20/20 (src/reports/crash.json); A/B/C còn có 9 test crash/retry trên refund phần chênh lệch
- Secret leak / approval bypass: Không phát hiện vi phạm trong 70/70 public trial đã pass của workflow theo evaluator; chưa có bộ đếm hidden chính thức, không coi đây là số liệu hidden

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Chọn workflow vì đạt 70/70 trial, pass^5 = 1 và variance = 0 trên cùng 14 claim × 5 seed. Single và orchestrator cũng đạt 70/70 nhưng cost/success lần lượt 46.398571 và 47.23 VND mô phỏng, cao hơn workflow 27.857143. Swarm đạt 69/70, cost/success 49.566957. Task hiện có luật tuần tự, dữ liệu order có cấu trúc; workflow đáp ứng với mức tự chủ thấp nhất, không cần lời gọi model.

## Có đáng đổi lấy multi-agent không

Trong public benchmark này, multi-agent chưa đem lại thêm trial pass. Giữ workflow; chỉ xem xét đổi khi tập đánh giá độc lập có task cần tra cứu thích ứng hoặc đọc ngôn ngữ mơ hồ và shape khác cải thiện đủ, vẫn bảo đảm approval, secret và crash với cost chấp nhận được. Kết quả A/B/C/D là so sánh implementation hiện tại, chưa cô lập tác động topology.

Ablation tắt peer acknowledgement của swarm giữ nguyên pass rate nhưng giảm cost/success 1.766020%. Điều này chỉ cho thấy lời gọi peer có output không được sử dụng trong reference hiện tại không cần cho kết quả, không chứng minh mọi hình thức phối hợp agent đều thừa.

## Trace và bằng chứng

Workflow ghi `claim_lookup`, `order_lookup`, `quote`, `refund_outcome` và `decision`; các nhánh sớm vẫn gọi `finish()` để ghi trace. C ghi handoff allowlist với facts rỗng và tool chỉ đọc. Không ghi `parent_secret`, raw header, phone, địa chỉ, tên hàng hoặc internal note. Trace nằm trong `src/traces/`, run id khớp kết quả; scanner đọc trace và các file cùng prefix. Không dùng log ngoài vùng scanner làm bằng chứng an toàn, không commit trace/database.

Lệnh tái lập (chạy trong `src/`, tại commit kỹ thuật nêu trên):

```powershell
python -m pytest -q -p no:cacheprovider -o addopts=
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
```

Kết quả đã kiểm chứng: 316 test pass; benchmark và crash JSON chạy lại khớp nội dung đã lưu. Hash trên là commit kỹ thuật có code, test và evidence; các commit sau bổ sung tài liệu. Branch hiện tại cần được review/merge trước khi nộp chính thức.

## Giới hạn

MockLLM không phải model production; latency là `unavailable`, giá mô phỏng. Public pass 1.0 không chứng minh hidden ≥ 0.75; chưa có `student_drop/` hoặc kết quả hidden chính thức. Steps là số event trace, không phải thời gian thực thi. Không sửa JSON cho đủ ngưỡng.
