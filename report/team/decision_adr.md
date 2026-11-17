# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: b2a9970
- Run id dẫn chứng: R-workflow-C-001-s11 … R-workflow-C-014-s55 (70 trial trong src/reports/benchmark.json); ví dụ R-workflow-C-002-s55 (claim swarm fail, workflow `denied` đúng), R-workflow-C-014-s11 (trần theo đơn, ledger 120.000)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0 (14 claim public × seed 11,22,33,44,55, src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.87 (single 39.35, orchestrator 48.51, swarm 49.57)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (70/70 trial pass, gồm quét `forbid_substrings` trong trace và các claim approval hỏng / hết hạn C-007; không có dòng ledger nào khi thiếu approval hợp lệ)

## Vì sao shape này

Trên cùng corpus (14 claim public), cùng 5 seed (11, 22, 33, 44, 55), cùng bảng giá và cùng evaluator, cả ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000, variance 0, nên độ đúng không phân biệt được chúng. Khác biệt chỉ còn ở chi phí và độ phức tạp: workflow tốn 28.87 VND/success với 1 lần gọi model mỗi claim, rẻ hơn single 27% (39.35, 4.64 lần gọi model) và rẻ hơn orchestrator 40% (48.51). Swarm vừa đắt nhất (49.57) vừa là shape duy nhất không ổn định (0.986, pass^5 0.929, fail C-002 ở seed 55). Đây là quy trình tuần tự với luật rõ ràng: số tiền, approval, trần theo đơn đều do code và host quyết, nên phần tự chủ thêm của B/C/D không mua thêm được claim nào. Theo nguyên tắc chọn kiến trúc **ít tự chủ nhất vẫn làm được việc**, nhóm chọn workflow. Workflow cũng ít bề mặt tấn công nhất: không có vòng lặp model nào chọn tool, nên ticket chứa injection ("ignore policy", số ngày nói dối, clause cũ) không có đường nào ảnh hưởng tới quyết định.

## Có đáng đổi lấy multi-agent không

Không, với dữ liệu hiện có. Trên bộ public, multi-agent (orchestrator, swarm) không pass nhỉnh hơn mà còn tốn hơn 68–72% chi phí; swarm còn thêm variance theo seed. Kể cả nếu một shape multi-agent pass nhỉnh hơn vài điểm phần trăm, nhóm vẫn giữ workflow nếu phần nhỉnh đó đến kèm variance cao hơn, vì với thao tác ghi tiền, một trial sai là một lần hoàn tiền sai. Quyết định sẽ đảo lại nếu: (1) bộ hidden cho thấy workflow fail một nhóm claim mà B/C pass, ví dụ ticket mơ hồ cần model hiểu ngôn ngữ để quyết định hỏi thêm hay leo thang (việc model làm trong bound); (2) task cần tra cứu song song nhiều nguồn độc lập, nơi investigator chạy song song giảm được độ trễ; hoặc (3) chênh lệch chi phí mô phỏng không còn ý nghĩa so với lợi ích về độ đúng. Hai điều đầu không xuất hiện trên bộ public.

## Trace và bằng chứng

Trace của workflow (`lab8.trace.Trace`, file `traces/<run_id>.json`) được ghi ở mọi nhánh return, kể cả `needs_info`, `escalated` và khi crash. Event ghi: `tool` (tên tool, `found`/`visible`, `reason`, `order_id`), `quote` (kết quả `compute_compensation`: số tiền, lý do, clause), `host` (`ok`, `reason`, `conflict` từ `issue_refund`), `crash` (điểm crash) và `decision` (status, `proposal_amount`, lý do). Cố ý **không** ghi: ticket (là dữ liệu người dùng, có thể chứa PII hoặc câu injection), claim row (có `parent_secret`, `raw_headers_json`), order row đầy đủ (có SĐT, địa chỉ, `internal_note`, tên hàng). Shape chỉ đọc qua các view allowlist `get_claim_view` và `lookup_order`, nên những field đó không bao giờ vào bộ nhớ của trace. Shape không ghi file nào khác ngoài trace và không in ra stdout, nên mọi thứ shape ghi đều nằm trong chỗ scanner của grader quét được (`trace_path` và các file `<run_id>*`). Nếu có log nằm ngoài chỗ đó, đội security không chứng minh được nó sạch; vì vậy nhóm không tạo log nào như thế. Bằng chứng: 70/70 trial workflow pass `trial_pass` (gồm `check_trace` và quét `forbid_substrings`), và `src/tests/test_single_shape.py` quét thêm `CANARY_SECRET_`, `CANARY_INTERNAL_`, header, SĐT, địa chỉ trên cả 14 claim cho shape B dùng cùng cách ghi trace.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75. Chi phí là VND mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API. Bộ public chỉ có 14 claim và ba shape đều đạt 1.000, nên kết luận chọn workflow dựa trên chi phí và độ đơn giản, chưa dựa trên khác biệt về độ đúng; bộ hidden (40 claim × 5 seed) sẽ là phép thử thật. Chưa chạy tự kiểm trên `student_drop/` (giảng viên phát lúc demo).
