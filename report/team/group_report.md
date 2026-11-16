# Báo cáo nhóm — Lab 8 LogiX-VN

Số liệu trong báo cáo lấy từ các file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: NhomV3
- Thành viên: Trương Việt Công (2A202603585), Nguyễn Quốc Hưng (2A202603553), Đỗ Minh Hoàng (2A202603554). Chi tiết trong `TEAM.md`.
- Repo: https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents, nhánh nộp `main`
- Commit chốt (trùng `report/team/decision_adr.md`): e99c5f2
- Shape chọn: `workflow`

## 2. Mục tiêu và cách tiếp cận

**Cách nhóm hiểu bài toán.** Một claim hoàn phí vận chuyển phải ra đúng một trong năm trạng thái (`resolved`, `denied`, `needs_info`, `escalated`, `failed`) và ghi ledger đúng số tiền. Phần nguy hiểm không nằm ở việc hiểu câu chữ trong ticket, mà ở chỗ ghi tiền: số tiền, approval và chống ghi trùng phải do code và host quyết, còn model chỉ đọc và soạn chữ. Vì vậy câu hỏi của lab không phải "multi-agent có giỏi hơn không" mà là "kiến trúc ít tự chủ nhất nào vẫn đúng, an toàn khi crash và không lộ secret".

**Nguyên tắc chung cho cả ba shape nhóm viết.**

1. Tiền chỉ do `compute_compensation` tính từ order row và policy hiện hành. Chữ trong ticket (số ngày trễ, mã đơn, "ignore policy") là dữ liệu người dùng, không phải lệnh.
2. `durability.issue_refund` là cửa ghi duy nhất. Shape truyền **quote đầy đủ** và `crash_at`, không tự trừ phần đã hoàn, không bắt `InjectedCrash`.
3. Mọi nhánh return đều qua `finish()` và ghi trace theo allowlist. Không ghi ticket, claim row hay order row thô.

**Chia việc.** Mỗi thành viên sở hữu trọn một shape trên một nhánh riêng, chỉ sửa một file shape và một file test của mình, nên ba nhánh không xung đột khi merge:

| Thành viên | Shape | Nhánh / PR | Việc chung sau merge |
|---|---|---|---|
| Đỗ Minh Hoàng | A `workflow` | `hoang` / PR #3 | Crash suite, benchmark 4 shape, ADR |
| Trương Việt Công | B `single` | `feature/single` / PR #2 | Phần Shape B trong báo cáo |
| Nguyễn Quốc Hưng | C `orchestrator` | `hung` / PR #1 | Audit secret/PII, research card R3 |

**Thứ tự làm.** (1) Cả nhóm cài môi trường, đọc `business_rules.md`, `contracts.md` và `swarm_reference.py` (CP1). (2) Ba shape được viết song song đến khi mỗi shape đạt 62/62 test student (CP2), rồi thêm `crash_at` và handoff sanitize (CP3). (3) Merge vào `main` theo thứ tự C → B → A, chạy lại toàn bộ test, crash suite và audit trên code đã gộp (CP4). (4) Benchmark 4 shape × 5 seed trên cùng corpus, sau đó chọn shape bằng số đo (CP5). Swarm có sẵn, chỉ dùng để đối chứng.

## 3. Giải pháp

Ranh giới code / model chung cho cả ba shape: model (MockLLM) không bao giờ thấy quyền ghi, không chọn số tiền và không gọi `issue_refund`. Host kiểm approval đúng claim, trần theo đơn và idempotency `refund:{claim_id}` trước khi ghi ledger.

| | A `workflow` | B `single` | C `orchestrator` |
|---|---|---|---|
| Ai chọn bước tiếp theo | Code cố định | Vòng ReAct (`run_react`, tối đa 8 bước) | Orchestrator giao việc cho investigator |
| Model call trung bình | 0 | 5.5 | 1.93 |
| Tool model được dùng | Không có | `lookup_order`, `lookup_refund_history`, `lookup_policy` (chỉ đọc) | Investigator: `lookup_order`, `lookup_policy` (chỉ đọc) |
| Ai tính tiền | `compute_compensation` | `compute_compensation` sau vòng lặp | `compute_compensation` ở orchestrator |
| Ai gọi ghi refund | Shape → host | Shape (sau vòng lặp) → host | Orchestrator → host |

### Shape A — Workflow cố định

Người phụ trách: Đỗ Minh Hoàng, MSSV `2A202603554`, nhánh `hoang` (PR #3).

Shape A là luồng Python cố định, không gọi model. Đọc claim bằng `get_claim_view` (không có `parent_secret`); claim không tồn tại trả `failed`, thiếu `order_id` trả `needs_info` và không ghi ledger. `lookup_order` kiểm đơn thuộc principal của claim; không thấy hoặc khác principal trả `escalated`. Quote do `compute_compensation` tính từ order row và policy hiện hành; số ngày trễ hay mã đơn viết trong ticket không được dùng. Quote bằng 0 trả `denied` mà không gọi host.

Quote dương được truyền **nguyên vẹn** cùng `crash_at` vào `durability.issue_refund`. Host kiểm approval đúng claim, trần theo đơn và idempotency; host từ chối thì shape trả `denied` (host đã ghi `policy_denied`), xung đột số tiền trả `failed`, còn lại `resolved`. `InjectedCrash` không bị bắt: shape ghi event `crash` rồi ném lại. Mọi nhánh trả qua `finish()`.

Trace ghi `claim` (found, has_order_id), `order` (5 field allowlist: order_id, status, delay_days, shipping_fee_vnd, damage_verified), `quote`, `issue_refund` (ok, reason, conflict) và `decision`. Không ghi ticket, claim row, order row thô hay dòng ledger. Vì không có model call, Shape A rẻ nhất và không dao động theo seed.

### Shape B — Single agent ReAct

Người phụ trách: Trương Việt Công, MSSV `2A202603585`, nhánh `feature/single` (PR #2).

Shape B đọc claim bằng `get_claim_view`; claim không tồn tại trả `failed`. Model đọc ticket một lần (`purpose="parse"`, có tính cost) nhưng nội dung ticket chỉ là dữ liệu. Thiếu `order_id` trả `needs_info`. Sau đó agent chạy vòng `run_react` với `max_steps=8` và `worker=True`; hàm `decide` chỉ được chọn ba tool đọc theo thứ tự `lookup_order` → `lookup_refund_history` → `lookup_policy`, không có tool ghi nào được đưa vào. Nếu đơn không nhìn thấy, agent dừng sớm và shape trả `escalated`. Chạm trần 8 bước thì trả `failed` (`step_cap`).

Sau vòng lặp, **code** (không phải model) tính quote bằng `compute_compensation` từ order row đã đọc; model chỉ soạn lời đáp với số đã tính. Quote bằng 0 trả `denied`. Quote dương được truyền nguyên vẹn cùng `crash_at` vào `issue_refund`; `lookup_refund_history` chỉ để agent quan sát, shape không tự trừ khoản đã hoàn. `InjectedCrash` được ghi vào trace rồi ném lại.

Trace ghi `action` (tên tool), `observe` (tóm tắt theo allowlist: tầm nhìn và field đơn đã lọc của `lookup_order`, `refund_count`/`refunded_vnd` của lịch sử hoàn, số policy), `react` (lý do dừng, các tool đã quan sát), `quote` và `decision`. Không ghi ticket, principal hay row thô. Shape B có nhiều model call nhất (5.5/trial) nên cost cao hơn A khoảng 40% dù độ đúng như nhau.

### Shape C — Orchestrator và investigator chỉ đọc

Người phụ trách: Nguyễn Quốc Hưng, MSSV `2A202603553`, nhánh `hung` (PR #1).

Shape C đọc claim bằng `get_claim_view`, nhưng không chuyển ticket hay toàn bộ claim view sang investigator. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`. Handoff được dựng bằng `make_handoff`, có `facts={}`, scope `owner_order_only` và chỉ hai tool `lookup_order`, `lookup_policy`. Investigator chạy qua `run_readonly_investigators`, đọc đơn trong phạm vi principal và policy hiện hành. Đơn không nhìn thấy trả `escalated`.

Orchestrator tính quote bằng `compute_compensation` trên order view. Quote bằng 0 trả `denied`. Quote dương được chuyển nguyên vẹn vào `durability.issue_refund`; host kiểm approval đúng claim, giới hạn theo đơn và idempotency. Shape không tự trừ khoản đã hoàn. Vì vậy T14 giữ `proposal_amount=150000` nhưng refund thực tế là `120000`. Khi host từ chối, quote vẫn được giữ và audit `policy_denied` do host ghi. Xung đột số tiền khi retry trả `failed`.

MockLLM chỉ nhận handoff đã lọc để xác nhận kế hoạch và quyết định có cấu trúc để soạn lời đáp; không quyết định số tiền hoặc cấp quyền ghi. Mọi lời gọi model và tool đọc được tính vào `Budget`. `crash_at` được truyền xuống host; shape không bắt `InjectedCrash`, và connection luôn được đóng trong `finally`.

Trace chỉ ghi kết quả tìm claim dạng boolean, handoff đã sanitize, khả năng nhìn thấy đơn, số policy, quote, yêu cầu/kết quả của host và quyết định cuối. Không ghi ticket, principal, claim/order row thô, secret, header, SĐT, địa chỉ, tên hàng hay internal note. Trace được ghi trước khi gọi host để còn bằng chứng nếu crash; mọi nhánh trả kết quả đều qua `finish()` để đồng bộ trace, ledger và audit.

## 4. Kết quả

### Benchmark 4 shape trên bộ public

Nguồn: `src/reports/benchmark.json`, commit `e99c5f2`. 14 claim public × seed `11,22,33,44,55`, 70 trial mỗi shape, SQLite mới mỗi trial, cùng MockLLM, cùng bảng giá mô phỏng (`tool_call_vnd = 10`, 20/80 VND mỗi 1k token vào/ra).

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Mean model calls |
|---|---:|---:|---|---:|---:|---|---:|
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 34.29 | 4.43 / 5 | 0.00 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.94 | 8.07 / 9 | 5.50 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 49.00 | 6.00 / 7 | 1.93 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

Swarm sai đúng 1 trial: C-002 ở seed 55 trả `resolved` thay vì `denied`. Ticket ghi trễ 5 ngày, order row ghi 2 ngày; swarm tin ticket ở seed chia hết cho 5. Ba shape nhóm viết đều lấy số ngày trễ từ order row nên không bị lỗi này.

### Durability, policy và bảo mật

| Kiểm tra | Kết quả | Nguồn |
|---|---|---|
| Crash suite 20 điểm | `crash_safety 20/20` | `src/reports/crash.json` |
| Ma trận student T01–T14, 4 shape | `248 passed` | `python -m pytest -q -m student -o addopts=` |
| Cổng host và test nhóm | `102 passed` (trong đó 48 test nhóm: A 25, B 4, C 19) | `python -m pytest -q` |
| Audit secret/PII/raw row, 3 shape × 14 claim × 5 seed | 210 trial; 0 secret, 0 PII, 0 raw row, 0 trace sai format | `src/reports/team_security.json` |
| Kiểm tra định dạng bài nộp | `0 FAIL` | `python -m lab8.check_submission` |

Công cụ `python -m tests.audit_team_security` (Nguyễn Quốc Hưng viết) bắt stdout/stderr trong bộ nhớ và quét `RunResult`, trace cùng mọi file `<run_id>*` cùng thư mục. Sau khi merge đủ ba shape, công cụ được chạy lại trên code gộp và cho kết quả trên. Kết quả riêng Shape C trước merge vẫn lưu ở `src/reports/orchestrator_benchmark.json` và `src/reports/orchestrator_security.json`; chúng khớp với số của Shape C trong benchmark cuối.

Nhóm chưa chạy tự kiểm trên `student_drop/`. Kết quả hidden 40 claim × 5 seed do giảng viên chấm.

### Quyết định

Ba shape nhóm viết đều đạt độ đúng tối đa trên bộ public, nên nhóm chọn shape ít tự chủ nhất và rẻ nhất: **workflow** (cost/success 34.29 so với 47.94 và 49.00, không có model call, không dao động theo seed). Lý do đầy đủ và điều kiện làm quyết định đảo lại nằm trong `report/team/decision_adr.md`. Phiếu nghiên cứu R3 và ablation tách investigator nằm trong `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

| Vấn đề | Cách xử lý |
|---|---|
| Trên một máy Windows, thư mục temp mặc định của pytest không truy cập được (`PermissionError: WinError 5`) | Đặt `PYTEST_DEBUG_TEMPROOT` trỏ tới `.qa/pytest-temp` trong `src/` rồi chạy lại. Không sửa test hay code host để né lỗi |
| `py -3` trên một máy trỏ tới Python 3.14 bị hỏng (`Unable to create process`), trong khi lab chỉ hỗ trợ 3.11–3.13 | Liệt kê bằng `py -0p` rồi tạo venv bằng `py -3.13 -m venv .venv` |
| Khi viết song song, mỗi shape chỉ kiểm được một mình; chưa chứng minh được an toàn cho cả nhóm cho đến khi merge | Mỗi người chỉ sửa một file shape và một file test nên merge không xung đột. Sau merge chạy lại ma trận 4 shape, crash suite và audit trên code gộp (số liệu ở mục 4) |
| Commit hash phải ghi vào ADR, nhưng ghi hash vào ADR lại tạo thêm commit mới | Theo `SUBMISSION.md`: commit code và `benchmark.json` trước (`e99c5f2`), ghi hash đó vào ADR, rồi commit ADR riêng |
| Grader chỉ lấy 3 file shape, nên helper dùng chung đặt ở file khác sẽ bị bỏ qua | Mỗi shape tự chứa đủ logic; không sửa `common.py` hay các file thước đo |

## 6. Tổng hợp đóng góp

| Thành viên | Phần việc chính | Commit chính | Test riêng |
|---|---|---|---|
| Trương Việt Công | Shape B `single` | `cbc72cc` | `src/tests/test_team_single.py` (4 test) |
| Nguyễn Quốc Hưng | Shape C `orchestrator`, audit secret/PII, R3 | `2ce84ee` | `src/tests/test_team_orchestrator.py` (19 test) |
| Đỗ Minh Hoàng | Shape A `workflow`, crash suite, benchmark, ADR | `9cdc97b`, `e99c5f2`, `a7d2ace` | `src/tests/test_team_workflow.py` (25 test) |

Chi tiết từng người nằm trong bảng đóng góp của `TEAM.md` và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

**Hạn chế của kết quả.**

- **MockLLM không phải model sản xuất.** Nó cố định theo seed, nên variance 0 của single và orchestrator chỉ cho thấy code của nhóm không để model quyết số tiền, chứ không chứng minh một LLM thật sẽ ổn định như vậy. Với model thật, B và C có thể dao động theo lần chạy; A thì không vì không gọi model.
- **Cost là VND mô phỏng** theo `config/pricing.yaml`, không phải hóa đơn API. Latency là `unavailable`, nên lab không đo được lợi ích tốc độ nếu orchestrator chạy investigator song song.
- **Corpus public chỉ có 14 claim.** Cả ba shape đều đạt 1.000 nên benchmark public không phân biệt được chúng về độ đúng; quyết định thực chất dựa trên cost và mức tự chủ. Kết luận chưa áp cho bộ hidden 40 claim cho tới khi giảng viên chấm.
- **Test riêng của Shape B còn mỏng** (4 test) so với A (25) và C (19); phần lớn bằng chứng của B đến từ ma trận student.

**Điều kiện làm kết luận thay đổi.**

- Bộ hidden có loại claim mà luồng cố định không phân loại được (ví dụ ticket nhắc nhiều đơn, hoặc cần hiểu ngôn ngữ để chọn nhánh), trong khi single hoặc orchestrator đạt pass rate cao hơn workflow rõ rệt trên cùng seed.
- Workflow tụt dưới ngưỡng 0.75 trên hidden. Khi đó nhóm đổi sang shape có pass rate cao nhất mà vẫn qua ba must-pass.
- Có model thật và đo được latency, trong đó orchestrator chạy song song giảm thời gian xử lý đáng kể mà cost tăng không nhiều.

**Hướng cải thiện.**

- Chạy tự kiểm `student_drop/` và thêm test cho các nhóm lỗi mà hidden phủ: homoglyph trong mã đơn, principal lẫn, approval mượn của claim khác, cộng dồn sai.
- Bổ sung test riêng cho Shape B: ticket injection ở cả 5 seed, chạm trần 8 bước, crash ở cả ba cửa sổ.
- Chạy lại benchmark với nhiều seed hơn 5 để ước lượng variance của swarm chắc chắn hơn.

## 8. Tài liệu tham khảo

- Contract, luật nghiệp vụ và runtime do đề Lab 8 cung cấp (`docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`).
- Tara Bogavelli, Hari Subramani, Roshnee Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), AACL-IJCNLP. Dùng cho R3; không suy rộng kết quả MockLLM thành hiệu quả của model thật.
