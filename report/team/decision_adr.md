# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 132507f (commit kỹ thuật chứa test và các report; ba shape kế thừa bản đã merge)
- Run id dẫn chứng: R-workflow-C-014-s11; đối chứng lỗi R-swarm-C-002-s55
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0 trên public 14 claim × 5 seed (src/reports/benchmark.json)
- Cost per success (mô phỏng, VND): 28.77 (workflow); single 39.348571; orchestrator 56.647143; swarm 49.566957
- Crash safety: 20/20 (src/reports/crash.json, host + swarm); test tích hợp bổ sung 18 trường hợp crash trên workflow/single/orchestrator với refund cap và top-up
- Secret leak / approval bypass: 0 / 0 trên 280 trial public của bốn shape (src/reports/safety.json); PII leak, invalid trace, unexpected ledger và exception cũng bằng 0; chưa chấm hidden

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Chọn workflow: trên cùng 14 claim và seed `11,22,33,44,55`, cả workflow, single và orchestrator đều pass 70/70, nhưng workflow có cost/success thấp nhất và chỉ dùng model soạn lời. Task có thứ tự rõ: đọc claim, xác minh đơn theo principal, quote bằng code, rồi host kiểm approval và ghi ledger. Với dữ liệu hiện tại, thêm vòng ReAct hoặc investigator chưa cải thiện pass rate. Đây là lựa chọn mức tự chủ thấp nhất đáp ứng task public; ngưỡng hidden phải chờ giảng viên chấm.

## Có đáng đổi lấy multi-agent không

Chưa có bằng chứng nên đổi sang multi-agent: swarm chỉ đúng 69/70, pass^5 = 13/14, variance ≈ 0.000816327 và cost/success cao hơn workflow. Trial `R-swarm-C-002-s55` tin ticket trễ 5 ngày thay vì order trễ 2 ngày nên hoàn 20.000 sai entitlement. Approval vẫn hợp lệ: host bảo vệ approval/cap/idempotency nhưng không tự tính lại entitlement.

Chỉ cân nhắc đổi khi benchmark mới có nhãn độc lập chứng minh thêm agent cải thiện chất lượng trên ticket mơ hồ, cần nhiều nguồn điều tra hoặc có công việc song song, với chi phí chấp nhận được và vẫn qua safety gates. Chênh lệch A/B/C/D hiện có còn gồm prompt, số tool và số model call; không quy toàn bộ chênh lệch cho topology.

Ablation một biến trong `src/reports/evaluation_ablation.json`: bỏ riêng draft call của workflow, giữ các yếu tố còn lại, vẫn 70/70, pass^5 = 1, variance = 0; cost/success 28.77 → 27.857143. Kết quả chỉ cho thấy drafting không tham gia quyết định tiền được evaluator chấm, không đánh giá chất lượng câu trả lời khách.

## Trace và bằng chứng

Workflow ghi claim (`found`, `has_order_id`), order view allowlist, quote, host outcome, decision và mốc crash. Single ghi các tool đọc, quote, react stop và quyết định; orchestrator ghi handoff đã sanitize, kết quả investigator đã allowlist, quote và refund. Không ghi ticket thô, principal context, `parent_secret`, raw headers, SĐT, địa chỉ, internal note hoặc tên hàng.

`finish()` lấy effect/audit từ SQLite rồi ghi trace đúng run id. Runner `python -m tests.evaluate_safety --out reports/safety.json` quét trace, file cùng thư mục có tiền tố run id, `RunResult` và stdout/stderr; so với canary của các claim và PII của toàn world public. File ngoài phạm vi scanner không được coi là bằng chứng an toàn; code shape hiện tại chỉ ghi trace qua tracer. Audit này không thay thế security review hoặc phép chấm hidden.

## Giới hạn

MockLLM không phải model sản xuất; latency `unavailable`, cost mô phỏng, không phải hóa đơn API. `steps` là số event trace nên khác cách ghi trace cũng làm mean/p95 khác nhau; không coi đó là thời gian chạy. Bộ public nhỏ và không đại diện toàn bộ claim thực tế. Chưa có `student_drop/`, chưa công bố pass rate hidden. Không sửa host, config/data hoặc sửa tay JSON.

Tái lập trong `src/`, sau khi activate `.venv`:

```text
python -m pytest -q
python -m pytest -q -m student -o addopts=
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m tests.evaluate_safety --out reports/safety.json
python -m tests.evaluation_ablation --out reports/evaluation_ablation.json
```
