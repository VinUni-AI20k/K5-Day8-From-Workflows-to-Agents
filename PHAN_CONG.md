# Phân công Lab 8 LogiX-VN: Hùng, Vinh, Minh

Mọi lệnh chạy trong `src/` với Python 3.11–3.13. Mỗi người làm trên nhánh riêng, viết test trong file riêng để merge không đụng nhau. Không sửa các file thước đo: `metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`. Grader chỉ lấy từ repo nhóm ba file shape và `src/bonus/`.

## Vai trò tổng quát

| Người | Vai | Nhánh | File code | File test riêng | Báo cáo phụ trách |
| --- | --- | --- | --- | --- | --- |
| **Hùng** | Shape A `workflow`, tích hợp, nhóm trưởng | `feat/workflow` | [`workflow.py`](src/lab8/shapes/workflow.py) | `src/tests/test_team_workflow.py` | [`TEAM.md`](TEAM.md), file JSON trong `src/reports/`, nộp bài |
| **Vinh** | Shape B `single`, đo đạc và báo cáo | `feat/single` | [`single.py`](src/lab8/shapes/single.py) | `src/tests/test_team_single.py` | [`group_report.md`](report/team/group_report.md), [`research_card.md`](report/team/research_card.md) |
| **Minh** | Shape C `orchestrator`, bảo mật và quyết định kiến trúc | `feat/orchestrator` | [`orchestrator.py`](src/lab8/shapes/orchestrator.py) | `src/tests/test_team_orchestrator.py` | [`decision_adr.md`](report/team/decision_adr.md) |

Lý do chia như vậy:

- Workflow đơn giản nhất nên Hùng xong sớm và còn thời gian merge, chạy benchmark và crash suite.
- Single liên quan trực tiếp tới câu hỏi "model tin ticket hay tin dữ liệu đơn", nên Vinh là người hợp nhất để làm ablation trong research card.
- Orchestrator có handoff và allowlist, nên Minh nắm sâu nhất phần secret và trace, tiện rà must-pass và viết ADR.

Quy tắc chung cho cả ba shape:

- Giữ chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None)`.
- Trả kết quả bằng `common.finish()` ở **mọi** nhánh return, kể cả `needs_info`, `escalated` và `denied`.
- Tiền do `compute_compensation` tính. MockLLM chỉ đọc hoặc soạn chữ.
- Truyền **quote đầy đủ** vào `durability.issue_refund`, không tự trừ phần đã hoàn trước đó (T13, T14).
- Truyền `crash_at` vào `issue_refund` và không bắt `InjectedCrash`.

---

## CP1 — Cài đặt, đọc contract, chia vai (13:30–13:45)

| Người | Việc | Xong khi |
| --- | --- | --- |
| **Hùng** | Tạo repo nhóm, hỏi coach dùng `L3A` hay `L3B` cho tên repo, mời Vinh và Minh, tạo ba nhánh. Điền phần thông tin nhóm và bảng thành viên trong `TEAM.md`. Đọc [`business_rules.md`](docs/business_rules.md) mục refund và approval. | Repo đã push, ba người clone được, `TEAM.md` có đủ 3 dòng thành viên. |
| **Vinh** | Đọc [`swarm_reference.py`](src/lab8/shapes/swarm_reference.py), `runtime.py` (`run_react`, `Budget`) và `mock_llm.py`. Ghi lại cách swarm gọi `finish()` và `issue_refund` để cả nhóm dùng làm mẫu. Đọc [`metrics.md`](docs/metrics.md). | Gửi nhóm ghi chú ngắn: các `status` của `RunResult`, cách dùng `Trace` và `finish()`. |
| **Minh** | Đọc [`contracts.md`](docs/contracts.md) (Trace contract v1), `handoff.py` (`make_handoff`, allowlist) và `tests/test_handoff_secret.py`. Liệt kê field nào được và không được vào handoff hay trace. | Gửi nhóm danh sách field cấm: `CANARY_SECRET_*`, số điện thoại, địa chỉ, item, internal note, claim row thô. |

Cả ba tự kiểm trên máy mình:

- `python -m lab8.smoke` in ra `lab8.smoke pass`.
- `python -m pytest -q` không có dòng `failed`.
- `python -m pytest -q -m student -o addopts=` ra `186 failed, 62 passed`.

---

## CP2 — Viết ba shape (13:45–14:30)

Ba người làm song song. Mục tiêu chung: shape không còn `not_implemented`, và `python -m pytest -q -m student -o addopts= -k <shape>` ra **62 passed**.

### Hùng: `workflow.py`

1. Mở store, đọc claim bằng `get_claim_view`, không dùng `SELECT *`.
2. Không có `order_id` thì trả `needs_info`, không ghi ledger.
3. Gọi `lookup_order`. Không thấy đơn thì trả `escalated`, không chép phone, address, item hay internal note vào kết quả.
4. Tính quote bằng `compute_compensation` từ order row. Bỏ qua số ngày trễ ghi trong ticket.
5. Quote bằng 0 thì trả `denied` và không gọi `issue_refund`.
6. Quote lớn hơn 0 thì gọi `issue_refund(conn, claim_id, <quote đầy đủ>)`, rồi map kết quả:
   - auth fail hoặc đơn đã hoàn đủ: `denied`, host tự ghi `policy_denied`;
   - amount conflict: `failed`;
   - thành công: `resolved`.
7. Ghi trace bằng `lab8.trace.Trace` ở mọi nhánh.

**Test thêm** trong `test_team_workflow.py`: approval thuộc claim khác thì bị từ chối, có audit `policy_denied` và ledger vẫn trống.

### Vinh: `single.py`

1. Dùng `run_react` với `max_steps=8`. Registry của `decide` chỉ có tool đọc: `get_claim_view`, `lookup_order`, `lookup_refund_history`. Không có `issue_refund`.
2. Ghi mọi model call vào `Budget` để cost so được với các shape khác.
3. Sau vòng lặp, **code** lấy order row, tính quote bằng `compute_compensation`, rồi gọi `issue_refund` với quote đầy đủ. Model không chọn số tiền.
4. Hết 8 bước mà chưa đủ dữ kiện thì trả `escalated` qua `finish()`.
5. Map `needs_info`, `escalated`, `denied` và `failed` giống workflow.

**Test thêm** trong `test_team_single.py`: ticket khai trễ nhiều ngày hơn dữ liệu đơn. Số tiền hoàn phải bằng quote tính từ order row, không theo ticket.

### Minh: `orchestrator.py`

1. Orchestrator đọc claim bằng `get_claim_view`, rồi dựng handoff bằng `make_handoff`. `facts` chỉ chứa field trong allowlist, `tools` chỉ gồm tool đọc như `lookup_order` và `lookup_refund_history`.
2. Chạy `run_readonly_investigators`. Investigator không có write registry.
3. Orchestrator lấy order view từ investigator, tính quote bằng `compute_compensation` và gọi `issue_refund` với quote đầy đủ.
4. Trace ghi handoff **đã sanitize**, không ghi parent context. Không dùng LLM tóm tắt để thay cho redaction.
5. Map status giống workflow.

**Test thêm** trong `test_team_orchestrator.py`: claim chứa `CANARY_SECRET_*` thì handoff, file trace và `RunResult` đều không chứa chuỗi đó.

**Bàn giao CP2:** mỗi người commit lên nhánh của mình. Hùng merge `feat/workflow` vào `main` trước, rồi tới `single` và `orchestrator`. Sau mỗi lần merge, chạy lại `python -m pytest -q`.

---

## CP3 — Crash, idempotency, handoff (14:30–15:15)

| Người | Việc | Xong khi |
| --- | --- | --- |
| **Hùng** | Xử lý `TODO CP3` trong `workflow.py`: truyền `crash_at`, không `try/except` quanh `issue_refund`. Chạy `python -m lab8.demo.buggy_workflow` để thấy vì sao checkpoint không thay được ledger. Thêm test: gọi `run_claim` hai lần cùng claim thì ledger chỉ có 1 dòng. | T11 và T12 của workflow xanh. |
| **Vinh** | Xử lý `TODO CP3` trong `single.py`. Kiểm tra trace vẫn được ghi khi `run_react` dừng ở bước 8. Thêm test: crash ở `crash_at` rồi resume thì có đúng 1 refund và 1 audit `refund_committed`. | T11 và T12 của single xanh. |
| **Minh** | Xử lý `TODO CP3` trong `orchestrator.py`. Kiểm tra lại handoff: chỉ có field allowlist và tool đọc. Rà file trace trong `src/traces/` của cả ba shape bằng cách tìm `CANARY_SECRET`, số điện thoại và địa chỉ. | T11 và T12 của orchestrator xanh, không trace nào chứa secret hay PII. |

Tự kiểm: `python -m pytest -q` vẫn xanh, và `python -m pytest -q -m student -o addopts=` không còn fail T11 hay T12 ở ba shape.

---

## Nghỉ 15:15–15:30

Trước 15:30, nếu nhóm muốn làm bonus thì Hùng đăng ký topic với giảng viên. Xem [`bonus_topics.md`](docs/bonus_topics.md). Bonus chỉ được tính khi pass rate hidden ≥ 0,80.

---

## CP4 — Must-pass: crash, approval, secret (15:30–16:15)

| Người | Việc | Sản phẩm |
| --- | --- | --- |
| **Hùng** | Chạy `python -m lab8.crash_test --count 20 --out reports/crash.json`. Nếu dưới `20/20`, đọc lỗi rồi báo người viết shape liên quan. | `src/reports/crash.json` với `crash_safety = 20/20`, đã commit. |
| **Vinh** | Rà nhánh approval của cả ba shape: approval hỏng, approval của claim khác, đơn đã hoàn đủ, policy cũ hoặc policy tương lai. Đối chiếu với T01–T14 trong `test_public_matrix.py`. Bắt đầu ghi số liệu thô cho báo cáo nhóm. | Bảng ghi chú "nhánh nào, shape nào, kết quả gì" để đưa vào báo cáo. |
| **Minh** | Rà must-pass về secret: chạy toàn bộ claim public, tìm `CANARY_SECRET_` trong `src/traces/`, các file `<run_id>*` và stdout. Kiểm grader không fail-closed với `missing_trace`, `stale_trace`, `invalid_trace` hay `trace_run_id_mismatch`. | Kết quả `0` lần lộ secret, kèm lệnh đã dùng, để ghi vào ADR. |

---

## CP5 — Benchmark, hidden, ADR, báo cáo (16:15–17:30)

| Người | Việc | Sản phẩm |
| --- | --- | --- |
| **Hùng** | Chạy `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`. Commit file JSON do công cụ sinh, không sửa tay. Gửi `run_id` cho Vinh và Minh. Điền bảng đóng góp trong `TEAM.md`: mỗi người một dòng, ghi commit và test. | `src/reports/benchmark.json` và `TEAM.md` hoàn chỉnh. |
| **Vinh** | Chọn câu **R2** trong research card: trial nào của swarm fail ở seed 55 và thuộc nhóm lỗi nào. Làm ablation với swarm: bật rồi tắt khả năng dùng số ngày trễ từ ticket. Giữ nguyên model, tool, corpus, seed, bảng giá và bộ chấm. Ghi lệnh, `run_id` và số đo. Viết `group_report.md`, tối đa 5 trang, dùng số từ `benchmark.json`. | `research_card.md` không còn ô "Nhóm điền" trống, và `group_report.md`. |
| **Minh** | Sau 16:15, tự kiểm trên `student_drop/` theo [`src/README.md`](src/README.md#tự-kiểm-trên-bộ-hidden-cp5). Chọn shape **ít tự chủ nhất** vẫn đạt pass rate ≥ 0,75 và qua đủ 3 must-pass, nhiều khả năng là `workflow`. Điền `decision_adr.md`: dòng `- Shape chọn:`, pass rate, pass^5, variance, cost/success, `run_id`, giới hạn của MockLLM. Giữ nguyên các dòng nhãn. | `decision_adr.md` đã điền, có thêm `reports/hidden_selfcheck.json` nếu chạy. |

**Mỗi người** copy mẫu [`MSSV_HoTen.md`](report/team/MSSV_HoTen.md) thành file của mình, ví dụ `2024xxxx_NguyenVanHung.md`, rồi ghi phần việc, commit và test đã viết.

---

## Trước khi nộp

Hùng làm theo đúng thứ tự trong [`SUBMISSION.md`](SUBMISSION.md):

1. `python -m pytest -q` xanh.
2. Commit, rồi chạy `git rev-parse --short HEAD` và gửi hash cho Minh.
3. Minh ghi hash vào ADR, rồi commit.
4. `python -m lab8.check_submission` ra `0 FAIL`, rồi push.

Cả ba kiểm tra cùng nhau:

- Bảng đóng góp đủ 3 dòng, có 3 file báo cáo cá nhân.
- Không commit `traces/`, `*.sqlite`, `student_drop/`, `.venv/` hay `.env`.
- **Mỗi người** tự nộp link repo trên LMS bằng tài khoản cá nhân. Ai không nộp thì không có điểm.

## Nếu bị trễ

Ưu tiên theo thứ tự:

1. Ba must-pass trên shape chọn.
2. Shape chọn qua 62 test.
3. `benchmark.json` và ADR.
4. Hai shape còn lại.
5. Báo cáo và research card.

Ai xong trước thì hỗ trợ shape đang đỏ. Thường là Hùng hỗ trợ Vinh, vì `single` có vòng ReAct dễ vướng hơn.
