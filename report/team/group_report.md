# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: BanGiua
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

**Hiểu bài toán.** Cùng một quy trình xử lý claim hoàn phí vận chuyển được cài theo bốn kiến trúc với mức tự chủ tăng dần: A `workflow` (bước cố định), B `single` (một agent ReAct), C `orchestrator` (orchestrator + investigator chỉ đọc), D `swarm` (có sẵn, dùng đối chứng). Mục tiêu không phải tìm kiến trúc "thông minh" nhất, mà là kiến trúc **ít tự chủ nhất vẫn làm đúng việc**, chọn bằng số đo trên cùng corpus, cùng seed, cùng bảng giá.

Ba nguyên tắc nhóm thống nhất trước khi viết code (từ `docs/business_rules.md` và `docs/contracts.md`):

1. **Tiền do code quyết.** Số tiền luôn lấy từ `compute_compensation`; MockLLM chỉ soạn câu chữ, không chọn số tiền, không gọi ghi refund.
2. **Ticket là dữ liệu người dùng.** Số ngày trễ, mã đơn, clause hay câu "ignore policy" trong ticket không bao giờ được dùng để quyết định; nguồn sự thật là dòng order và policy hiện hành.
3. **Host là cửa ghi duy nhất.** Shape truyền **quote đầy đủ** vào `durability.issue_refund`; host kiểm approval, trần theo đơn, idempotency rồi mới ghi ledger.

**Thứ tự làm.**

- CP1: cài môi trường, chạy smoke và cổng host, đọc contract và `swarm_reference.py`. Baseline student: 186 failed / 62 passed (đúng như CHECKPOINTS).
- CP2: viết A trước (đơn giản nhất, làm chuẩn để so), rồi B và C dùng lại cùng chuỗi kiểm tra: claim → order → quote → host.
- CP3–CP4: truyền `crash_at`, không nuốt `InjectedCrash`; thêm test riêng cho ba điều kiện must-pass trên shape B; chạy crash suite.
- CP5: chạy benchmark 4 shape × 5 seed trên bộ public.

## 3. Giải pháp

Cả ba shape giữ nguyên chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`, trả kết quả qua `lab8.shapes.common.finish()` (tự đọc `refund_effects` và `committed_audit_count` từ ledger), và đi qua cùng một cây quyết định:

| Bước | Điều kiện | Kết quả |
| --- | --- | --- |
| Đọc claim qua `get_claim_view` (không `SELECT *`) | Không tồn tại | `failed` / `unknown_claim` |
| | Thiếu `order_id` | `needs_info`, không ghi ledger |
| `lookup_order` (chỉ field allowlist) | Không thấy đơn / không đúng principal | `escalated`, không trả SĐT, địa chỉ, ghi chú, tên hàng |
| `compute_compensation` trên dòng order | Quote = 0 | `denied`, **không** gọi `issue_refund` |
| `durability.issue_refund(conn, claim_id, quote, crash_at=...)` | Host từ chối | `denied` (host ghi `policy_denied`), `proposal_amount` = quote |
| | Số tiền khác số đã commit | `failed` / `amount_conflict` |
| | Host chấp nhận / replay | `resolved` |

**A — `workflow`.** Các bước trên viết cứng bằng Python. Model chỉ được gọi một lần để soạn câu trả lời sau khi status và số tiền đã cố định. Đây là shape ít tự chủ nhất.

**B — `single`.** Dùng `lab8.runtime.run_react` với `max_steps=8`. Hàm `decide` đọc kết quả tool trước, rồi chọn bước tiếp: `lookup_order` → `lookup_refund_history` → `compute_compensation` → kết thúc. Agent chỉ được chọn trong ba tool đọc này; nếu model đòi tool ghi, runtime ném `ToolRejected` và shape trả `failed`. Câu trả lời cuối của model chỉ là "quote đã sẵn sàng"; số tiền đưa vào host là kết quả `compute_compensation` mà code lưu lại, không phải số model viết. Vượt 8 bước → `failed` / `step_cap`.

**C — `orchestrator`.** Orchestrator đọc claim, kiểm `needs_info`, rồi dựng handoff bằng `lab8.handoff.make_handoff` với `facts={}` và `allowed_tools=["lookup_order", "lookup_refund_history"]`. Investigator chạy qua `run_readonly_investigators` (registry chỉ đọc, `worker=True`). Orchestrator tự tính quote từ order view của investigator rồi gọi host. Handoff không có ticket, `parent_secret` hay header; `sanitize()` còn từ chối nếu chuỗi `CANARY_SECRET_` lọt vào.

**Ranh giới code / model.**

| Việc | A | B | C |
| --- | --- | --- | --- |
| Chọn bước đọc tiếp theo | Code | Model (chỉ tool đọc, ≤ 8 bước) | Orchestrator lập kế hoạch, investigator đọc |
| Tính số tiền | `compute_compensation` | `compute_compensation` (code giữ kết quả) | `compute_compensation` do orchestrator gọi |
| Ghi refund | Host | Host, sau vòng ReAct | Host, do orchestrator gọi |
| Soạn câu chữ | MockLLM | MockLLM | MockLLM |

**Trace.** Dùng `lab8.trace.Trace`, ghi ở mọi nhánh return (kể cả `needs_info`, `escalated`) và cả khi crash (ghi event `crash` rồi `raise` lại). Event ghi: `tool` / `act` / `observe` (chỉ tên tool, `visible`, `reason`), `handoff` (bản đã sanitize), `investigator` (chỉ `visible`, `refund_count`, `refunded_vnd`), `quote`, `host` (`ok`, `reason`, `conflict`), `decision`. Cố ý **không** ghi: ticket, claim row, order row, `parent_secret`, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.

## 4. Kết quả

Benchmark chính thức `src/reports/benchmark.json`: 14 claim public × seed `11,22,33,44,55` = 70 trial mỗi shape, MockLLM, giá mô phỏng, SQLite mới cho mỗi trial.

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Model calls TB |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A workflow | 1.000 | 1.000 | 1.000–1.000 | 0 | **28.87** | 4.43 / 5 | 1.00 |
| B single | 1.000 | 1.000 | 1.000–1.000 | 0 | 39.35 | 7.93 / 9 | 4.64 |
| C orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0 | 48.51 | 4.36 / 5 | 2.93 |
| D swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

- **Crash safety:** `src/reports/crash.json` → **20/20**.
- **Ma trận student:** 248/248 passed (62 test × 4 shape; swarm có một miss dự kiến ở C-002 seed 55, test khẳng định miss đó).
- **Cổng host:** `python -m pytest -q` xanh, gồm 34 test thêm cho shape B (`src/tests/test_single_shape.py`): approval mượn / thu hồi / hết hạn / thiếu / bằng 0, quét secret và PII trên cả 14 claim, crash ở 3 điểm, ticket không ghi đè dòng order.
- **Swarm fail ở đâu:** duy nhất C-002 seed 55. Ticket ghi "trễ 5 ngày", dòng order ghi 2 ngày; ở seed chia hết cho 5 swarm tin số trong ticket nên trả `resolved` 20.000 thay vì `denied`. Ba shape của nhóm luôn lấy `delay_days` từ order nên không bị.
- **Nhận xét:** trên bộ public, cả ba shape của nhóm đều đúng tuyệt đối và không dao động theo seed, nên khác biệt chỉ còn ở chi phí: so với A, B tốn hơn ~36% và C tốn hơn ~68% mà không pass thêm claim nào. Tự kiểm trên `student_drop/` sẽ làm khi giảng viên phát bộ test lúc demo.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Merge conflict làm hỏng `single.py`.** Khi merge `main` vào nhánh `khoa/shapeB` (commit `86a21fe`), conflict được giải bằng cách giữ dòng của cả hai phía, khiến `single.py` lỗi cú pháp (`SyntaxError: unmatched ')'` dòng 152). Vì `lab8/shapes/__init__.py` import cả bốn shape, lỗi này làm **mọi** shape và cả cổng host không import được (`7 errors`). Phát hiện khi chạy benchmark; xử lý bằng `git checkout caebbbe -- src/lab8/shapes/single.py` (khôi phục bản sạch) rồi chạy lại cổng host, ma trận student, smoke, crash và benchmark. Bài học: chạy `python -m pytest -q` trước mỗi lần merge.
- **Lọc test theo shape bị khớp nhầm.** `pytest -k single` khớp cả tên test `test_public_single_run_cases` nên ra 242 thay vì 62; dùng `-k "single and not workflow and not orchestrator and not swarm"` để đếm đúng 62 test của shape B.
- **Phiên bản Python.** Máy dùng Python 3.14 (README yêu cầu 3.11–3.13); mọi lệnh vẫn chạy đúng, nhưng nên kiểm lại trên 3.12/3.13 cho khớp máy chấm.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- MockLLM không phải model sản xuất; latency là `unavailable`; chi phí là VND mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API.
- Bộ public chỉ có 14 claim, và ba shape đều đạt 1.0, nên benchmark public không phân biệt được độ đúng giữa A/B/C — chỉ phân biệt chi phí. Bộ hidden (ticket nói dối, injection, homoglyph, principal lẫn…) mới là phép thử thật.
- `decide` của shape B là chính sách cố định, nên variance theo seed bằng 0 là do thiết kế, không phải vì "agent ổn định". Với một LLM thật, đường đi của agent sẽ thay đổi theo seed và variance của B/C có thể tăng.
- **Điều kiện làm kết luận đổi:** nếu ticket thật cần hiểu ngôn ngữ mơ hồ để quyết định hỏi thêm hay leo thang (việc model làm trong bound), hoặc cần tra song song nhiều nguồn, thì B hoặc C có thể đáng thêm chi phí. Với quy trình tuần tự, luật rõ ràng như ở đây, thêm tự chủ chỉ thêm chi phí.

## 8. Tài liệu tham khảo

- `README.md`, `CHECKPOINTS.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md` trong repo lab.
- `src/lab8/shapes/swarm_reference.py` (shape D tham chiếu).
