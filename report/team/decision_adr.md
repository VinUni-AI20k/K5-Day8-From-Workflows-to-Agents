# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 50fe2f5
- Run id dẫn chứng: R-workflow-C-002-s55 (denied đúng, nơi swarm fail), R-workflow-C-007-s55 (approval hết hạn → denied, không ghi tiền), R-workflow-C-011-s55 (resolved, 1 refund) — src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (14 claim public × seed 11,22,33,44,55 = 70 trial)
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 — 70/70 trial pass trial_pass (kiểm forbid_substrings, refund_mismatch, unexpected_ledger_rows); quét 70 trace R-workflow-* không có chuỗi CANARY_; T04/T05/T07 (approval_ok=false) đều không có refund

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng 14 claim public, cùng 5 seed (11, 22, 33, 44, 55) và cùng bảng giá mô phỏng, ba shape nhóm viết đều pass 70/70 với pass^5 = 1.000 và variance 0, nên chất lượng không phân biệt được chúng. Khác biệt nằm ở chi phí và mức tự chủ: workflow 27.86 VND/success, single 38.50 (+38%), orchestrator 55.71 (gấp 2), swarm 49.57 nhưng chỉ pass 0.986 (fail `R-swarm-C-002-s55`). Workflow cũng không gọi model nào (0 model call trung bình): số tiền do `compute_compensation` tính từ order row, ghi tiền đi qua `durability.issue_refund`. Theo nguyên tắc của lab là chọn shape ít tự chủ nhất mà vẫn làm được việc, nhóm chọn workflow.

## Có đáng đổi lấy multi-agent không

Không, trên bộ dữ liệu này. Multi-agent không cho pass cao hơn (cả ba đều 1.000), lại đắt hơn: orchestrator tốn gấp đôi vì investigator gọi thêm tool (5.57 so với 2.79 tool call trung bình). Swarm còn tệ hơn: có variance (seed 55 = 0.929) vì tin số ngày trễ ghi trong ticket thay cho DB, và host không chặn được lỗi này vì approval A-002 hợp lệ. Nếu một shape multi-agent pass nhỉnh hơn mà cost và variance cao hơn, nhóm vẫn giữ workflow, trừ khi phần pass tăng thêm nằm ở claim mà workflow không xử lý được.

Quyết định sẽ đảo lại nếu: (1) ticket là văn bản tự do, phải đọc hiểu mới biết order hay loại sự cố, mà luật cố định không bóc tách được; khi đó single được dùng tool đọc đáng giá thêm chi phí; (2) mỗi claim cần tra nhiều nguồn độc lập (nhiều hãng vận chuyển, nhiều policy) có thể chạy song song, khi đó orchestrator + investigator đáng giá; (3) bộ hidden cho thấy workflow pass < 0.75 do gặp loại claim chưa có trong luật.

## Trace và bằng chứng

Trace workflow (`traces/R-workflow-<claim>-s<seed>.json`, contract v1 do `lab8.trace.Trace` ghi) có các event: `claim` (claim_id, found, has_order_id), `order` (visible và chỉ 6 field cần cho quote: order_id, status, delay_days, shipping_fee_vnd, paid_vnd, damage_verified), `quote` (amount_vnd, reason, clause_ids), `host` (ok, reason, conflict, amount_vnd), `decision` (status, proposal_amount, reason) và `crash` (điểm crash, khi có).

Cố ý **không** ghi: ticket (chữ người dùng, có thể chứa lệnh hoặc thông tin cá nhân), principal_id, `parent_secret`, `raw_headers` (chứa `Bearer CANARY_SECRET_*`), phone, address, item_name, internal_note của order. Lý do: trace được grader và người khác đọc, nên coi là ranh giới bảo mật; chỉ ghi field đủ để tái lập quyết định tiền.

Bằng chứng không lộ: `trial_pass` kiểm `forbid_substrings` trên kết quả và trace của từng trial (70/70 pass); nhóm quét thêm toàn bộ 70 trace `R-workflow-*`, không file nào chứa `CANARY_`. Nếu trace nằm ngoài chỗ scanner quét được, bằng chứng phải là thiết kế allowlist: code chỉ chép field có tên trong `_TRACE_ORDER_FIELDS` (`src/lab8/shapes/workflow.py`), không bao giờ ghi cả row, nên secret không có đường vào trace.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75. Bộ public chỉ có 14 claim; pass 1.000 ở đây không đảm bảo pass trên bộ hidden 40 claim. Nhóm không chạy tự kiểm hidden (tùy chọn) vì không có `student_drop/`. Cost là VND mô phỏng, không phải hóa đơn API.
