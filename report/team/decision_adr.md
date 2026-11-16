# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 3b97524
- Run id dẫn chứng: R-workflow-C-001-s11 … R-workflow-C-014-s55 (70 trial workflow trong src/reports/benchmark.json); đối chứng swarm fail duy nhất: R-swarm-C-002-s55
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (workflow, 14 claim × 5 seed, src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.46 (workflow); single 28.47, orchestrator 47.44, swarm 49.57
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (70/70 trial workflow pass; trial_pass quét forbid_substrings trong trace + kết quả và đối chiếu ledger); số hidden do giảng viên chấm

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Bốn shape chạy trên cùng 14 claim public × seed 11, 22, 33, 44, 55, cùng MockLLM, cùng bảng giá và cùng evaluator (`src/reports/benchmark.json`). Ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000 và variance 0, nên pass rate không phân biệt được chúng. Khi chất lượng ngang nhau, nhóm chọn shape **ít tự chủ nhất**: workflow. Mọi quyết định đều là code cố định: đọc claim qua `get_claim_view`, kiểm quyền sở hữu qua `lookup_order`, tính tiền bằng `compute_compensation` từ order row, rồi gọi `durability.issue_refund` với quote đầy đủ. Model chỉ soạn câu trả lời sau khi kết quả đã được quyết định (0.64 model call/trial, thấp nhất trong bốn shape), nên ticket nói dối hay chứa injection không có đường nào ảnh hưởng tới số tiền. Cost/success của workflow (28.46 VND) ngang single (28.47) và thấp hơn orchestrator (47.44) khoảng 40%. Ngoài ma trận public, workflow còn qua 10/10 test bất biến ledger ở `src/tests/test_ledger_shapes.py`: crash ở cả 3 điểm, retry nhiều lần, approval thiếu/thu hồi/mượn claim khác, trần theo đơn, và cả corpus chạy chung một DB.

## Có đáng đổi lấy multi-agent không

Không. Trên bộ public, multi-agent không cải thiện pass rate: orchestrator bằng workflow (1.000), còn swarm thấp hơn (0.986, pass^5 0.929, variance 0.000816 do fail `R-swarm-C-002-s55`), trong khi cost/success cao hơn 67% (orchestrator) và 74% (swarm). Task claims là chuỗi tuần tự (claim → order → quote → host), không có phần đọc độc lập đủ lớn để chia cho nhiều agent. Quyết định sẽ đảo lại nếu: (1) bộ hidden hoặc dữ liệu thật có loại claim mà luật cố định không mã hóa được (ví dụ cần đọc hiểu chứng từ tự do để xác định hỏng hàng), khi đó single hoặc orchestrator có thể pass cao hơn đủ để bù chi phí; (2) có nhiều nguồn dữ liệu độc lập cần tra song song và latency trở thành ràng buộc, lúc đó investigator song song mới có lợi. Cả hai điều kiện đều phải được chứng minh bằng benchmark cùng corpus, cùng seed trước khi đổi.

## Trace và bằng chứng

Trace của nhóm ghi những event nào? Field nào cố ý **không** ghi, và vì sao? Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?

Đối với workflow (shape chọn), trace được ghi bằng `Trace` và `finish()`, có `run_id` khớp kết quả. Các event theo thứ tự: `claim` (chỉ `claim_id` và cờ `has_order_id`), `lookup_order` (chỉ `visible` và `reason`), `quote` (kết quả của `compute_compensation`), `host` (`ok`, `reason` do host trả) và `decision` (`status`, `proposal_amount`, `reason`). Nhánh trả sớm (`failed`, `needs_info`, `escalated`, `denied`) vẫn ghi `decision` và trace. Cố ý không ghi: ticket, `parent_secret`, raw headers, principal, order row (SĐT, địa chỉ, tên hàng, ghi chú nội bộ). Trace là thứ grader quét, nên chỉ ghi field đã qua allowlist. Shape không ghi log phụ và không in ra stdout, nên không có dữ liệu nằm ngoài chỗ scanner quét được. Bằng chứng: 70/70 trial workflow pass trong benchmark (trial_pass quét `forbid_substrings` gồm canary, SĐT, địa chỉ, ghi chú nội bộ), và `test_public_corpus_in_one_store_keeps_ledger_invariants` quét thêm toàn bộ artifact khi chạy cả corpus.

Đối với orchestrator, trace được ghi bằng `Trace` và `finish()`, có `run_id` khớp kết quả. Tùy nhánh, các event gồm `handoff`, `investigator`, `quote`, `decision`. Handoff qua allowlist, không chứa ticket hay parent context; investigator chỉ ghi visibility, reason và số policy. Không ghi secret, headers, principal context, số điện thoại, địa chỉ, tên hàng hoặc ghi chú nội bộ. Shape không tạo log phụ và không in dữ liệu ra stdout. Test `test_ticket_injection_cannot_cross_handoff_or_change_quote` kiểm tra handoff thực tế, các file có tiền tố run id, kết quả và stdout/stderr với ticket được cài canary/PII giả. Đây là bằng chứng cho các ca đã thử, chưa phải kết quả hidden hay bằng chứng an toàn tuyệt đối.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

- MockLLM cố định theo seed, nên variance 0 của ba shape nhóm viết chỉ cho thấy code ổn định trên seed public, không chứng minh model thật cũng ổn định. Với model thật, single và orchestrator có thể dao động nhiều hơn workflow vì model chọn tool.
- Bộ public chỉ có 14 claim; pass 1.000 trên public không đảm bảo hidden (40 claim, có homoglyph, principal lẫn, injection). Pass rate hidden chỉ có sau khi giảng viên chấm.
- Cost là giá mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API.
- Workflow chỉ xử lý được các tình huống đã mã hóa trong luật; loại claim mới cần sửa code chứ không tự thích nghi.
