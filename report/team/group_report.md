# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Random
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 3b97524

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim`, rồi dùng số đo trên cùng claim, cùng seed, cùng bảng giá để chọn kiến trúc ít tự chủ nhất mà vẫn làm được việc. Nhóm thống nhất một ranh giới chung cho cả ba shape tự viết: số tiền do code tính (`compute_compensation` trên order row và policy hiện hành); approval, trần theo đơn và chống ghi trùng do host quyết (`durability.issue_refund`); model chỉ chọn tool đọc hoặc soạn chữ. Chữ trong ticket là dữ liệu người dùng, không phải lệnh.

Chia việc theo gợi ý nhóm 4 người trong `TEAM.md`: workflow + integration (Nguyễn Quang Duy), single agent (Đỗ Văn Ngọc), orchestrator + handoff + bảo mật trace (Đoàn Nhật Anh), ledger + evaluation (Nguyễn Trần Anh Khôi). Mỗi người làm trên một nhánh riêng (`feat/workflow`, `feat/single`, `feat/orchestrator`, `feat/ledger-tests`) rồi gộp vào `main`.

Thứ tự: swarm tham chiếu có sẵn và được dùng làm mẫu contract (`finish()`, trace, cách gọi host). Ba shape A, B, C được viết song song vì chúng chỉ chung phần host, không phụ thuộc lẫn nhau. Sau khi ba shape vào `main`, nhóm chạy ma trận student, test bất biến ledger, crash suite và benchmark bốn shape, rồi mới viết ADR và research card từ file trong `src/reports/`.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape A — Workflow cố định

Workflow là chuỗi bước Python cố định, không có vòng lặp và không để model chọn bước. Shape đọc claim bằng `get_claim_view` (không `SELECT *`), nên `parent_secret` và raw headers không đi vào shape. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info` và không lấy mã đơn từ câu chữ trong ticket. Quyền sở hữu đơn được kiểm qua `lookup_order` với principal của claim; đơn không tìm thấy hoặc ngoài phạm vi trả `escalated`.

Số tiền lấy từ `compute_compensation` trên order row và policy hiện hành, không lấy từ số ngày trễ ghi trong ticket. Quote bằng 0 trả `denied` và không gọi host. Quote dương được truyền đầy đủ vào `durability.issue_refund` cùng `crash_at`; host kiểm approval, trần theo đơn và idempotency. Workflow không tự trừ tiền đã hoàn và không bắt `InjectedCrash`. Host từ chối trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`; `proposal_amount` luôn là quote đầy đủ. Kết nối SQLite đóng trong `finally`.

Mọi nhánh trả kết quả đi qua một hàm `done()` gọi `finish()`, nên nhánh nào cũng có trace và bằng chứng ledger lấy từ host. MockLLM được gọi một lần để soạn phản hồi sau khi host đã trả kết quả, không ảnh hưởng tới status hay số tiền. Trace gồm `claim` (chỉ `claim_id` và cờ `has_order_id`), `lookup_order` (chỉ `visible`, `reason`), `quote`, `host`, `decision`. Không ghi ticket, claim row, order row hay principal.

### Shape B — Single agent (một vòng ReAct)

Single đọc claim bằng `get_claim_view` và xử lý hai nhánh sớm trước khi vào vòng lặp: claim không tồn tại trả `failed`, thiếu `order_id` trả `needs_info`. Sau đó shape gọi MockLLM một lần cho bước quyết định và chạy `run_react` với `max_steps=8`. Hàm `_decide` chỉ chọn tool đọc theo thứ tự có giới hạn: `lookup_order` với principal của claim, rồi `compute_compensation` trên order vừa đọc. Đơn không nhìn thấy được trả `escalated`; chạm trần bước hoặc gặp kết quả tool ngoài dự kiến trả `failed`.

Observation đưa vào vòng lặp chỉ gồm `found`, `claim_id`, `principal_id`, `order_id`; ticket không được đưa vào, nên số ngày trễ hay chỉ dẫn trong ticket không có đường nào tới quyết định. Vòng lặp không có tool ghi. Sau vòng lặp, code của shape lấy quote: bằng 0 thì `denied` và không gọi host; dương thì truyền quote đầy đủ cùng `crash_at` vào `durability.issue_refund`. Khi crash được tiêm, shape ghi trace rồi ném lại `InjectedCrash`. Host từ chối trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`.

Trace gồm `claim_view` (bốn field allowlist ở trên), `react` (lý do dừng và số bước), `quote`, `decision`. Lỗi SQLite được bắt và trả `failed` với lý do `storage_error` để `run_claim` không ném exception.

### Shape C — Orchestrator và investigator chỉ đọc

Orchestrator đọc claim bằng `get_claim_view`. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`, không giao việc cho investigator và không ghi refund. Các nhánh trả kết quả đều dùng `finish()` để ghi trace và lấy bằng chứng ledger từ host.

Handoff được tạo bằng `make_handoff`, với `facts` rỗng và ba tool được phép: `lookup_order`, `lookup_policy`, `compute_compensation`. Không chuyển ticket, parent context, secret hoặc raw headers vào handoff. Investigator chạy qua `run_readonly_investigators` và chỉ được gọi tool đọc. Quyền sở hữu đơn được kiểm qua `lookup_order`; đơn không tìm thấy hoặc ngoài phạm vi principal trả `escalated`.

Số tiền lấy từ `compute_compensation` trên dữ kiện đơn và policy hiện hành, không lấy từ lời kể trong ticket. Quote bằng 0 trả `denied`. Quote dương được truyền đầy đủ vào `durability.issue_refund`; host kiểm approval, trần theo đơn và idempotency. Orchestrator không tự trừ tiền đã hoàn. Host từ chối trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`. Tham số `crash_at` được chuyển cho host và `InjectedCrash` được phép truyền ra ngoài; kết nối luôn đóng trong `finally`.

MockLLM chỉ soạn phản hồi từ status và proposal đã được code quyết định. Trace gồm `handoff`, `investigator`, `quote`, `decision` tùy nhánh; event investigator chỉ ghi visibility, reason và số policy. Không dump claim, order hoặc toàn bộ kết quả investigator.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

Lệnh (chạy trong `src/`): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`. Điều kiện cố định: 14 claim public (C-001…C-014), seed 11/22/33/44/55, MockLLM, `config/pricing.yaml`, as_of 2026-11-15, SQLite mới cho mỗi trial. 70 trial mỗi shape.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND, mô phỏng) | Mean / p95 steps | Mean model calls | Mean tool calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.46 | 4.43 / 5 | 0.64 | 2.79 |
| B single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.47 | 3.79 / 4 | 0.93 | 2.79 |
| C orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.44 | 3.71 / 4 | 1.00 | 4.64 |
| D swarm (tham chiếu) | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 | 4.66 |

Nhận xét:

- Ba shape nhóm viết pass toàn bộ 70 trial, không dao động giữa các seed. Pass rate không phân biệt được chúng; khác biệt nằm ở cost và mức tự chủ.
- Swarm fail đúng một trial, `R-swarm-C-002-s55` (`status resolved != denied`): ở seed 55 swarm tin số ngày trễ trong ticket (5 ngày) thay vì `delay_days` (2 ngày). Đây là điểm yếu cố ý của shape tham chiếu, và là lý do swarm có variance khác 0.
- Orchestrator tốn hơn workflow/single khoảng 67% cost/success vì investigator gọi thêm tool (4.64 so với 2.79 tool call/trial) mà không thêm trial đúng. Ablation chi tiết ở `report/team/research_card.md`.
- Steps là số event trong trace, nên workflow nhiều steps hơn chỉ vì ghi trace chi tiết hơn, không phải vì tốn hơn.

**Crash safety:** `python -m lab8.crash_test --count 20 --out reports/crash.json` cho `crash_safety` = **20/20** (`src/reports/crash.json`).

**Kiểm thử:** cổng host `python -m pytest -q` xanh (106 passed), gồm test riêng của từng thành viên và 40 ca bất biến ledger (`src/tests/test_ledger_shapes.py`, 8 hàm, 10 ca × 4 shape): crash ở cả 3 điểm rồi resume, retry nhiều lần, approval thiếu/thu hồi/mượn claim khác, hai claim cùng đơn, và cả 14 claim chạy trên một DB chung. Ma trận student `python -m pytest -q -m student -o addopts=` đạt 248 passed (62 test T01–T14 cho mỗi shape, swarm có một trial được kiểm là phải fail).

**Tự kiểm hidden (`student_drop/`):** lệnh `python -m lab8.benchmark --shapes workflow,single,orchestrator --cases student_drop/hidden_claims.jsonl --world student_drop/hidden_world_state.json --out reports/hidden_selfcheck.json` (40 claim × 5 seed = 200 trial mỗi shape, `src/reports/hidden_selfcheck.json`). Bộ này không có nhãn nên không ra pass rate.

| Shape | Trial | Lỗi (`error_trials`) | Nghi lộ secret (`leak_suspect_trials`) | resolved / denied / escalated / needs_info | Cost mô phỏng tổng (VND) | Mean steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| workflow | 200 | 0 | 0 | 90 / 95 / 10 / 5 | 5917.5 | 4.53 |
| single | 200 | 0 | 0 | 90 / 95 / 10 / 5 | 5928.7 | 3.90 |
| orchestrator | 200 | 0 | 0 | 90 / 95 / 10 / 5 | 9902.6 | 3.88 |

Cả ba shape chạy hết 200 trial, không lỗi, trace đúng contract và không có trial nghi lộ secret. Đối chiếu từng trial: ba shape cho **cùng status trên cả 200 cặp claim × seed**, và không claim nào đổi status giữa các seed. Điều này cho thấy ba shape nhất quán với nhau, nhưng không chứng minh status đó đúng; pass rate chính thức do giảng viên chấm bằng bộ có nhãn.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

Trong lần kiểm tra ban đầu, máy chạy Python 3.10 nên `python -m lab8.smoke` báo phiên bản quá cũ; đây là vấn đề môi trường, không phải lỗi shape. Sau đó CI của nhóm đã chạy xanh trên Python 3.11 và 3.13 ở cả ba hệ điều hành. Ma trận student đạt 289 passed trên bản tích hợp. Các kết quả cuối cần gắn với commit nộp ở GitHub Actions.

Test mới tại `src/tests/test_orchestrator_security.py` kiểm tra ticket chứa chỉ dẫn giả và canary không làm thay đổi quote hoặc xuất hiện trong handoff, trace, kết quả và stdout/stderr. Hai ca còn lại kiểm tra claim không tồn tại và thiếu mã đơn không được giao cho investigator nhưng vẫn có trace hợp lệ. Các test mới dùng thư mục tạm để tách artifact giữa các lần chạy.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

### Đỗ Văn Ngọc — Single agent

- Phụ trách `src/lab8/shapes/single.py`: vòng ReAct tối đa 8 bước với công cụ chỉ đọc; code kiểm tra claim/order, lấy quote từ dữ liệu đã xác minh và gọi host để hoàn refund.
- Thêm test `src/tests/test_single_agent.py::test_single_uses_order_facts_instead_of_ticket_delay` để kiểm tra agent bỏ qua số ngày trễ trong ticket, không ghi refund sai và trace đúng contract.
- Trạng thái xác minh: ma trận public Single chạy riêng đạt `60 passed, 188 deselected`. Benchmark chung ghi pass rate `1.000` và pass^5 `1.000`. Test riêng cũng được đưa vào cổng mặc định sau khi bỏ marker `@pytest.mark.student`.

### Nguyễn Quang Duy — Workflow + integration

- Phụ trách `src/lab8/shapes/workflow.py` (commit `603e469`): chuỗi bước cố định, tiền do `compute_compensation` tính, host là nơi duy nhất ghi refund.
- Thêm `src/tests/test_workflow_extra.py` (commit `1e53ad2`): 4 hàm, 8 ca, kiểm tra workflow không tin ticket trên cả 5 seed, truyền quote đầy đủ, host từ chối vẫn có audit `policy_denied`, gọi lại vẫn một refund và trace sạch.
- Integration: gộp nhánh `feat/workflow` vào `main` và kiểm tra lại sau khi gộp; chi tiết ở `report/team/2A202603462_NguyenQuangDuy.md`.

### Nguyễn Trần Anh Khôi — Ledger + evaluation

- Viết `src/tests/test_ledger_shapes.py` (commit `ff49706`): 8 hàm test bất biến ledger (40 ca) chạy qua cả 4 shape trong cổng host, dùng swarm làm đối chứng để chứng minh bản thân test đúng.
- Chạy crash suite và benchmark bằng lệnh chính thức, sinh `src/reports/crash.json` và `src/reports/benchmark.json`.
- Điền `report/team/decision_adr.md`, `report/team/research_card.md` (R1, ablation single → orchestrator) và mục 4 của báo cáo này.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

Hạn chế:

- MockLLM cố định theo seed, nên variance 0 của ba shape nhóm viết chỉ cho thấy code ổn định trên 5 seed public. Với model thật, single và orchestrator có thể dao động nhiều hơn workflow vì model tham gia chọn tool.
- Bộ public chỉ có 14 claim. Pass rate 1.000 trên public không đảm bảo kết quả trên bộ hidden (40 claim × 5 seed); số hidden do giảng viên chấm.
- Tự kiểm trên `student_drop/` không có nhãn, nên chỉ chứng minh shape chạy hết 40 claim, trace hợp lệ và không nghi lộ secret, chưa chứng minh status đúng.
- Cost là giá mô phỏng theo `config/pricing.yaml`, không phải hóa đơn API. Steps là số event trong trace nên phụ thuộc cách mỗi shape ghi trace, không so trực tiếp được giữa các shape.
- CI đã xác nhận trên Python 3.11 và 3.13 ở ba hệ điều hành; lần chạy cục bộ cũ trên Python 3.10 chỉ là bằng chứng lịch sử về giới hạn môi trường.
- Workflow chỉ xử lý được các tình huống đã mã hóa thành luật. Loại claim mới cần sửa code, shape không tự thích nghi.

Hướng cải thiện:

- Khi có thay đổi sau lần CI xanh, chạy lại smoke, pytest, crash suite và benchmark trên Python 3.11–3.13 trước khi chốt commit nộp.
- Thêm test cho các nhóm tình huống hidden đã được công bố: homoglyph trong ticket, principal lẫn, policy tương lai.

Điều kiện làm kết luận thay đổi: xem mục "Có đáng đổi lấy multi-agent không" trong `report/team/decision_adr.md`. Tóm tắt: nếu xuất hiện loại claim mà luật cố định không mã hóa được, hoặc có nhiều nguồn dữ liệu độc lập cần tra song song và latency trở thành ràng buộc, nhóm sẽ đo lại trên cùng corpus và cùng seed trước khi đổi shape.

## 8. Tài liệu tham khảo

- Tài liệu của lab trong repo: `README.md`, `CHECKPOINTS.md`, `RUBRIC.md`, `RULES.md`, `SUBMISSION.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md`.
- Shape tham chiếu `src/lab8/shapes/swarm_reference.py` và phần host `src/lab8/durability.py`, `src/lab8/handoff.py`, `src/lab8/runtime.py`.
- Google Research, Google DeepMind, MIT, *Towards a Science of Scaling Agent Systems*, arXiv:2512.08296, https://arxiv.org/abs/2512.08296 (nguồn của research card, câu R1).
- Công cụ AI từng thành viên đã dùng: ghi ở mục 5 trong báo cáo cá nhân `report/team/MSSV_HoTen.md`.
