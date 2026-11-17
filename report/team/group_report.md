# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Warden
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 50fe2f5

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim`, rồi chọn kiến trúc ít tự chủ nhất mà vẫn đạt yêu cầu, dựa trên số đo. Nhóm hiểu ranh giới quan trọng nhất là **tiền do code quyết**: số tiền do `compute_compensation` / `quote` tính từ order row, ghi tiền chỉ đi qua cửa host `durability.issue_refund` (kiểm approval, trần theo đơn, idempotency `refund:{claim_id}`). Model chỉ đọc và soạn chữ; chữ trong ticket là dữ liệu, không phải lệnh hay nguồn số liệu.

Chia việc theo gợi ý nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation. Mỗi người làm trên nhánh riêng rồi mở PR vào `main`.

Thứ tự: CP1 cài đặt và đọc contract, cả nhóm đọc `swarm_reference.py` làm mẫu. CP2–CP3 ba shape được viết song song, trong lúc đó phần ledger + evaluation chạy những việc không phụ thuộc shape (crash suite, benchmark mốc swarm, test cho host). CP4–CP5: sau khi gộp ba shape thì rà `TODO CP3`, chạy lại crash suite, benchmark 4 shape × 5 seed, điền ADR và research card.

## 3. Giải pháp

Cả ba shape có chung khung: đọc claim qua `get_claim_view` (adapter allowlist, không `SELECT *` nên `parent_secret` và `raw_headers` không bao giờ vào bộ nhớ của shape), thiếu `order_id` thì `needs_info`, order không thấy được thì `escalated`, quote 0 thì `denied` mà không gọi host, quote > 0 thì gọi `issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`. Host từ chối thì `denied` (host tự ghi `policy_denied`), conflict thì `failed`, thành công thì `resolved`. Mọi nhánh return đi qua `lab8.shapes.common.finish()` và có trace contract v1. Khi crash, shape ghi event `crash`, ghi trace rồi `raise` lại `InjectedCrash`, không nuốt crash.

| Shape | Đọc gì | Ai quyết định | Gọi host |
| --- | --- | --- | --- |
| A `workflow` | `get_claim_view` → `lookup_order` | Code cố định từng bước; quote bằng `compute_compensation` từ order row, bỏ qua số trong ticket. Không gọi model | Code của shape |
| B `single` | Vòng ReAct `run_react(max_steps=8)` với tool chỉ đọc: `lookup_order` → `lookup_policy` → `lookup_refund_history` | Model chỉ chọn tool đọc; quote bằng `quote()` từ order row + policy sau vòng lặp | Code sau vòng lặp |
| C `orchestrator` | Investigator chỉ đọc qua `run_readonly_investigators` với 4 tool: `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation` | Investigator trả quote; orchestrator chỉ đọc kết quả có cấu trúc | Orchestrator |

**Handoff (orchestrator):** dựng bằng `lab8.handoff.make_handoff` với `facts={}`, `allowed_tools` chỉ đọc và `principal_scope`; trace ghi `safe_dump(handoff)`, không ghi parent context. Investigator chỉ trả field có cấu trúc (visible, reason, số policy), orchestrator không chép row thô vào trace.

**Trace:** workflow ghi `claim`, `order` (chỉ 6 field cần cho quote), `quote`, `host`, `decision`, `crash`; single ghi `claim`, `react_action`, `react_result`, `quote`, `decision`; orchestrator ghi `handoff`, `investigator`, `quote`, `host_write`. Không shape nào ghi ticket, `parent_secret`, `raw_headers`, phone, address, internal note.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

### 4.1 Crash safety (`src/reports/crash.json`)

`python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`. Gồm: 17 điểm crash của `issue_refund` (5 × `before_effect`, 7 × `after_effect_before_checkpoint`, 5 × `after_checkpoint`), retry khác amount (conflict, giữ số đã commit), retry khi thiếu approval (không ghi), và swarm crash sau effect rồi resume (một refund).

Test bổ sung của nhóm: `src/tests/test_ledger_crash_and_gate.py` (16 test, chạy trong cổng host): crash lặp lại 3 lần tại cùng một điểm, approval hết hạn / revoked / pending / 0 VND, trần theo approval và theo số tiền đã trả, claim lạ, đơn của principal khác, claim không có order.

### 4.2 Mốc đối chứng: swarm (`src/reports/benchmark_swarm.json`)

`python -m lab8.benchmark --shapes swarm --out reports/benchmark_swarm.json` (14 claim public × seed 11,22,33,44,55):

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | --: | --: | --: | --: | --: | --: |
| swarm | 0.986 (69/70) | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.8 / 3.0 |

Trial fail duy nhất: `R-swarm-C-002-s55` (T02), `status resolved != denied`. Ticket ghi "giao trễ 5 ngày", order O-202 trong DB có `delay_days = 2`. Ở seed chia hết cho 5, swarm tin số trong ticket (event `model_override` trong trace), tính lại quote thành 20000 và host **ghi refund thật**, vì approval A-002 hợp lệ. Bài học: cổng host chỉ chặn approval, scope, trần và idempotency; nó không kiểm dữ kiện dùng để tính quote. Vì vậy shape phải lấy `delay_days` từ `lookup_order`, không lấy từ chữ trong ticket.

### 4.3 Bốn shape (`src/reports/benchmark.json`)

`python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` (14 claim public × 5 seed = 70 trial mỗi shape, cùng bảng giá mô phỏng):

| Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Model calls TB | Tool calls TB |
| --- | --: | --: | --: | --: | --: | --: | --: | --: |
| workflow | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0 | 27.86 | 4.43 / 5 | 0 | 2.79 |
| single | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0 | 38.50 | 8.14 / 9 | 3.57 | 3.64 |
| orchestrator | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0 | 55.71 | 3.43 / 4 | 0 | 5.57 |
| swarm | 0.986 (69/70) | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.8 / 3 | 3.0 | 4.66 |

`steps` là số event trong trace (`lab8/trace.py`), không phải số vòng ReAct; single vẫn chạy `run_react` với `max_steps=8`.

Nhận xét: ba shape nhóm viết đều pass 70/70 và không dao động giữa các seed. Trên bộ public, chênh lệch duy nhất giữa chúng là chi phí: workflow rẻ nhất (27.86), single đắt hơn 38%, orchestrator đắt gấp đôi (55.71) vì investigator gọi thêm tool. Swarm là shape duy nhất có variance, do điểm yếu ở mục 4.2.

Crash suite chạy lại sau khi gộp ba shape: vẫn `20/20`. Cổng host `python -m pytest -q`: 83 passed (gồm test của nhóm). Ma trận student `python -m pytest -q -m student -o addopts=`: 267 passed, 0 failed. `python -m lab8.check_submission`: 0 FAIL.

### 4.4 Ablation R2 (`src/reports/ablation_r2.json`)

Swarm cộng một verifier bằng code trước khi ghi (`src/bonus/swarm_verified.py`), mọi thứ khác giữ nguyên:

| Shape | Pass rate | pass^5 | Variance | Cost/success | Tổng cost mô phỏng |
| --- | --: | --: | --: | --: | --: |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 3420.12 |
| swarm_verified | 1.000 | 1.000 | 0 | 49.00 | 3430.10 (+0.29%) |
| workflow | 1.000 | 1.000 | 0 | 27.86 | 1950.00 |

Verifier can thiệp đúng 1/70 trial (`R-swarm_verified-C-002-s55`, event `verifier_override`). Nó sửa được lỗi, nhưng swarm vẫn đắt hơn workflow khoảng 76% cho cùng chất lượng. Chi tiết: `report/team/research_card.md`.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

| Khó khăn | Cách xử lý |
| --- | --- |
| Swarm pay sai `R-swarm-C-002-s55` dù host có cổng approval | So hai trace `s55` và `s11` của C-002, thấy event `model_override` (delay 5 thay cho 2). Kết luận host không kiểm dữ kiện tính quote; nhóm thống nhất mọi shape lấy `delay_days` từ order row. Workflow và single có test riêng cho việc này (`test_workflow_ignores_delay_written_in_ticket`, `test_single_uses_order_row_for_quote`) |
| Phần ledger + evaluation phụ thuộc shape của người khác | Tách việc: crash suite (`lab8.crash_test` chỉ dùng host và swarm) và benchmark mốc swarm chạy ngay từ đầu; T11/T12 và benchmark 4 shape chạy sau khi gộp |
| `steps` của single là 8.14, tưởng vượt giới hạn 8 bước ReAct | Đọc `lab8/trace.py`: `steps` = số event trong trace. Single vẫn chạy `run_react(max_steps=8)`; không phải lỗi |
| Test của nhóm có marker `student` nên `python -m pytest -q` không chạy | Chạy thêm `python -m pytest -q -o addopts= tests/test_workflow_extra.py ...` để xác nhận xanh; test ledger và ablation để không marker nên nằm trong cổng host |
| Xung đột `TEAM.md` khi hai người cùng thêm dòng vào bảng đóng góp | Giữ cả hai dòng khi gộp; mỗi người tự điền phần của mình trên `main` |
| Một commit có tác giả `Your Name` do máy chưa cấu hình git | Ghi rõ hash `8300fcc` trong bảng đóng góp để quy đúng người |
| PowerShell 5.1 không nhận here-string cho `git commit -F -` | Ghi commit message ra file rồi dùng `git commit -F <file>` |

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

- **Cỡ mẫu nhỏ:** 14 claim public × 5 seed. Pass 1.000 ở đây không đảm bảo pass ≥ 0.75 trên bộ hidden 40 claim. Nhóm không chạy tự kiểm hidden (tùy chọn) vì không có `student_drop/`.
- **Single gần như là workflow có thêm model call:** `decide` của single gọi tool theo thứ tự cố định (order → policy → refund history), model call chỉ tốn chi phí. Vì vậy so sánh workflow với single ở đây đo chi phí của model call nhiều hơn là đo giá trị của tự chủ. Hướng cải thiện: để model thật sự chọn tool, rồi đo lại variance.
- **Ablation chỉ bắt được một lỗi:** lỗi của swarm là điểm yếu cài sẵn theo `seed % 5 == 0`; verifier mới được kiểm trên 1 trial fail. Chưa có claim đối kháng tự viết (ticket nói dối hỏng hàng, nhiều con số trong một câu).
- **Cost là VND mô phỏng**, không phải hóa đơn API.
- **Điều kiện làm kết luận đảo lại:** ticket là văn bản tự do cần đọc hiểu mới biết order hay loại sự cố; claim cần tra nhiều nguồn độc lập có thể chạy song song; hoặc bộ hidden cho thấy workflow pass < 0.75 do gặp loại claim chưa có trong luật. Khi đó single hoặc orchestrator có thể đáng giá thêm chi phí.

## 8. Tài liệu tham khảo

- Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657. Dùng cho research card R2.
- Đề bài và tài liệu repo: [README.md](../../README.md), [docs/business_rules.md](../../docs/business_rules.md), [docs/contracts.md](../../docs/contracts.md), [docs/architecture.md](../../docs/architecture.md), [docs/metrics.md](../../docs/metrics.md), [docs/bonus_topics.md](../../docs/bonus_topics.md) (biến thể `--extra-shape`).
- Bằng chứng: `src/reports/benchmark.json`, `src/reports/crash.json`, `src/reports/benchmark_swarm.json`, `src/reports/ablation_r2.json`.
