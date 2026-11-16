# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 6d349d3
- Run id dẫn chứng: R-workflow-C-001-s11, R-workflow-C-002-s55, R-workflow-C-014-s11 (src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000 (14 claim public x 5 seed 11,22,33,44,55)
- Cost per success (mô phỏng, VND): 34.29
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (quét trace + T07, T13; hidden do giảng viên chấm)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng corpus public (14 claim), cùng 5 seed `11,22,33,44,55` và cùng bảng giá mô phỏng (`src/reports/benchmark.json`), ba shape nhóm viết đều đạt pass rate 1.000, pass^5 1.000 và variance 0, còn swarm đạt 0.986 / 0.929 (sai C-002 ở seed 55 vì tin số ngày trễ trong ticket). Khi độ đúng ngang nhau, workflow là shape ít tự chủ nhất và rẻ nhất: cost/success 34.29 VND so với 47.94 (single), 49.00 (orchestrator), 49.57 (swarm); 0 model call, trung bình 4.43 step so với 8.07 (single) và 6.00 (orchestrator). Mọi quyết định tiền đều nằm trong code (`compute_compensation` → `durability.issue_refund` với quote đầy đủ), nên không có đường nào để chữ trong ticket đổi số tiền.

## Có đáng đổi lấy multi-agent không

Không, trên dữ liệu hiện có. Single và orchestrator không thắng workflow về pass rate mà tốn thêm khoảng 40% cost và nhiều step hơn; swarm vừa đắt hơn vừa dao động theo seed. Multi-agent chỉ có lý khi nó làm được việc workflow không làm được. Quyết định sẽ đảo lại nếu: (1) bộ hidden có loại claim mà luồng cố định không phân loại được (ticket cần hiểu ngôn ngữ để chọn nhánh, ví dụ nhiều đơn trong một ticket) và single/orchestrator pass cao hơn workflow rõ rệt trên cùng seed; hoặc (2) điều tra cần nhiều nguồn độc lập, tốn thời gian, mà orchestrator chạy song song giảm latency thật (chưa đo được ở lab này). Nếu workflow tụt dưới 0.75 trên hidden thì nhóm đổi sang shape có pass cao nhất mà vẫn qua 3 must-pass.

## Trace và bằng chứng

Trace workflow ghi 5 loại event: `claim` (claim_id, found, has_order_id), `order` (visible và 5 field allowlist: order_id, status, delay_days, shipping_fee_vnd, damage_verified, hoặc reason khi không thấy), `quote` (amount, reason, clause_ids, parts), `issue_refund` (ok, reason, conflict) và `decision` (status, proposal_amount, reason); thêm `crash` khi có `InjectedCrash`. Cố ý **không** ghi: ticket (dữ liệu người dùng, có thể chứa injection), claim row thô (`parent_secret`, raw headers), order row thô (SĐT, địa chỉ, tên hàng, internal note) và dòng ledger thô. Trace chỉ ghi bằng `lab8.trace.Trace` vào `traces/<run_id>.json`, shape không ghi file nào khác và không in ra stdout, nên mọi thứ shape ghi ra đều nằm trong chỗ scanner quét. Bằng chứng: `src/tests/test_team_workflow.py` quét trace và `RunResult` của cả 14 claim public tìm `forbid_substrings`, `CANARY_SECRET`, `CANARY_INTERNAL` và nội dung ticket; quét 282 trace của ba shape nhóm viết không có lần nào trúng.

## Giới hạn

MockLLM không phải model sản xuất: nó cố định theo seed, nên variance 0 của single/orchestrator không chứng minh một LLM thật sẽ ổn định như vậy. Cost là VND mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API. Latency để `unavailable`. Corpus public chỉ có 14 claim; kết luận chưa áp cho bộ hidden 40 claim cho tới khi giảng viên chấm. Không sửa JSON cho đủ 0.75.
