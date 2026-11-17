# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: d11143b
- Run id dẫn chứng: R-workflow-C-001-s11 … R-workflow-C-014-s55 (70 trial workflow trong `src/reports/benchmark.json`, trường `trials[*].run_id`); đối chứng R-swarm-C-002-s55 (trial fail duy nhất của swarm)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70/70 trial, 14 claim × seed 11,22,33,44,55)
- Cost per success (mô phỏng, VND): 27.86 (tổng 1950.0 VND mô phỏng / 70 trial pass)
- Crash safety: 20/20 (src/reports/crash.json); T11–T12 xanh trên cả workflow, single, orchestrator
- Secret leak / approval bypass: 0 / 0 trên bộ public (forbid_substrings sạch ở 70/70 trial; test tích hợp approval hỏng 5 kiểu không tạo refund). Chỉ số hidden do giảng viên chấm

Lệnh sinh bằng chứng (chạy tại `src/`, commit `d11143b`):

```text
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Biến cố định (`controlled_variables` trong `benchmark.json`): `as_of` 2026-11-15, 14 claim public, seed 11/22/33/44/55, MockLLM, bảng giá mô phỏng (20 VND/1k token vào, 80 VND/1k token ra, 10 VND/tool call), SQLite mới cho mỗi trial, latency `unavailable`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Tổng cost | Mean / p95 steps | Mean model calls | Mean tool calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 1950.00 | 4.29 / 5 | 0.00 | 2.79 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 48.26 | 3378.30 | 7.14 / 8 | 4.64 | 4.50 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.19 | 4003.00 | 5.36 / 6 | 2.00 | 5.57 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 3420.12 | 2.80 / 3 | 3.00 | 4.66 |

## Vì sao shape này

Trên cùng corpus 14 claim, cùng năm seed và cùng bảng giá, ba shape nhóm viết đều đạt 70/70 trial, pass^5 = 1.0 và variance 0; swarm tham chiếu fail một trial (`R-swarm-C-002-s55`, tin số ngày trễ trong ticket) nên pass 0.986, pass^5 0.929. Khi độ đúng bằng nhau, nhóm chọn shape **ít tự chủ nhất**: workflow không gọi model (0 model call), dùng ít tool nhất (2.79/trial) và có cost/success thấp nhất, 27.86 VND mô phỏng, bằng khoảng 58% của single (48.26) và 49% của orchestrator (57.19). Toàn bộ quyết định nghiệp vụ của workflow là code tất định: đọc claim/order qua tool allowlist, tính tiền bằng `compute_compensation` từ dòng order, chuyển quote đầy đủ cho `durability.issue_refund`. Không có vòng lặp nên không có rủi ro `step_cap` (research card cho thấy single giảm còn 14,29% pass khi ngân sách bước bị cắt xuống 2), không có handoff để rò rỉ.

## Có đáng đổi lấy multi-agent không

Không, trên số liệu hiện có. Orchestrator không pass nhiều hơn workflow (cùng 1.000) nhưng đắt hơn 2,05 lần trên mỗi trial pass và tăng bề mặt tấn công (handoff, investigator). Swarm còn thấp hơn về pass rate và là shape duy nhất có variance khác 0. Nhóm giữ workflow kể cả nếu một shape agent nhỉnh hơn vài phần nghìn pass rate mà cost và variance cao hơn, vì ngưỡng hidden là 0.75 và sai một refund tốn hơn nhiều so với vài chục VND mô phỏng.

Quyết định sẽ đảo lại nếu: (1) self-check hoặc kết quả hidden cho thấy workflow fail một nhóm claim mà bước cố định không biểu diễn được (ví dụ cần đọc thêm nguồn tùy theo nội dung, như homoglyph hay principal lẫn) trong khi single/orchestrator xử lý được và vẫn qua ba must-pass; (2) task chuyển sang dạng cần điều tra song song nhiều nguồn độc lập, khi đó orchestrator có thể giảm độ trễ thật (hiện không đo được vì latency `unavailable`); (3) dùng model thật thay MockLLM và phần soạn câu trả lời có giá trị nghiệp vụ đủ lớn để bù cost.

## Trace và bằng chứng

Trace workflow (contract v1, `src/traces/<run_id>.json`, ghi lại trong mỗi lần chạy, kể cả nhánh sớm và nhánh crash) có các event: `tool` `get_claim_view` (chỉ `found`, `claim_id`, `has_order_id`), `tool` `lookup_order` (order view đã qua allowlist `ORDER_FIELDS`: order_id, status, delay_days, shipping_fee_vnd, paid_vnd, damage_verified, carrier), `tool` `compute_compensation` (amount, reason, clause_ids), `host` `issue_refund` (ok, reason), `decision` (status, reason), và `crash` (điểm crash) trước khi để `InjectedCrash` truyền ra ngoài.

Cố ý **không** ghi: `parent_secret`, `raw_headers`, SĐT, địa chỉ, `internal_note`, tên hàng (PII/secret theo contract); `principal_id` (định danh khách, không cần để chấm); **nguyên văn ticket** (dữ liệu người dùng, có thể chứa injection hoặc secret khách tự dán vào). Mục cuối được bổ sung ở commit `d11143b` sau khi test tích hợp `test_sensitive_text_pasted_in_ticket_never_reaches_trace` chứng minh bản trước chép ticket vào trace; số đo benchmark không đổi sau khi sửa.

Bằng chứng không phụ thuộc vào việc scanner tìm thấy file: shape không ghi file nào ngoài trace, không in ra stdout; test tích hợp quét trace + stdout/stderr + `RunResult` của cả ba shape trên 14 claim, so với secret parent, giá trị header và mọi giá trị PII của mọi order trong world. Nếu trace nằm ngoài chỗ scanner quét được, đội security cần chứng minh bằng code chứ không bằng log: chỉ field allowlist mới vào trace (đọc qua `get_claim_view`/`lookup_order`, không `SELECT *`), cộng với test hồi quy chạy được trên mọi claim.

Kiểm tra tích hợp (`src/tests/test_team_integration.py`, 142 test, áp dụng cùng bất biến cho workflow/single/orchestrator và đọc trực tiếp ledger, audit, checkpoint):

- Approval: thiếu, trỏ approval không tồn tại, bị thu hồi, hết hạn, mượn approval của claim khác → `denied`, proposal 35.000, không có dòng ledger, có `policy_denied` đúng lý do; retry vẫn bị chặn; approval thấp hơn quote → ledger bằng approval, proposal giữ quote.
- Retry: chạy 3 lần một ledger/một audit; retry chéo shape trên cùng store vẫn một dòng; xung đột số tiền → `failed`/`amount_conflict`, giữ dòng cũ.
- Crash/resume ở cả ba cửa sổ, crash hai lần liên tiếp, và `crash_at` trên nhánh không ghi.
- Ba shape cho cùng kết quả trên 14 claim ở seed 11 và 55; ticket injection không nâng được số tiền ở cả năm seed.

Kết quả tại commit `d11143b`: `python -m pytest -q` 298 passed; `python -m pytest -q -m student -o addopts=` 248 passed (mỗi shape 62); crash suite 20/20. Chạy lại benchmark ra kết quả giống hệt file đã commit.

## Giới hạn

- MockLLM không phải model sản xuất; workflow không gọi model nên cost của nó chỉ gồm tool call. Cost là mô phỏng, không phải hóa đơn API. Latency để `unavailable`.
- Variance 0 của ba shape nhóm viết phản ánh logic tất định trong setup này, không chứng minh độ ổn định với model thật.
- Benchmark chỉ có 14 claim public (70 trial/shape); 100% trên public không suy ra được pass rate hidden. Chưa có `student_drop/` nên chưa chạy self-check hidden; điểm hidden và `secret_leak_count`/`approval_bypass_count` chính thức do grader giảng viên chấm.
- Benchmark chạy C-011 và C-012 như trial một lần; retry và crash/resume thực sự được kiểm bằng T11–T12 và test tích hợp.
- Không sửa JSON trong `src/reports/` và không sửa thước đo để đạt ngưỡng 0.75.
