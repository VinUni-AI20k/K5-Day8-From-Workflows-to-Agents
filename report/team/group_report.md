# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: ABCDE
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

**Bài toán.** Xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim`, rồi dựa trên số đo để chọn kiến trúc ít tự chủ nhất mà vẫn làm được việc. Ở mọi shape, nhóm giữ ba ranh giới:

- Số tiền do code tính (`compute_compensation`), không do model.
- Chỉ ghi tiền qua cửa host `durability.issue_refund`, truyền quote đầy đủ để host kiểm approval, trần theo đơn và idempotency.
- Chữ trong ticket là dữ liệu người dùng, không phải lệnh, và không được ghi vào trace.

**Chia việc.** Nhóm 4 người chia theo phần việc, không chia theo checkpoint: mỗi người giữ một phần từ CP2 đến CP5 (chi tiết trong [PHAN_CONG.md](../../PHAN_CONG.md)). Lý do: CP3 và CP4 sửa và kiểm đúng các file của CP2, nên người viết shape sửa lỗi nhanh nhất; chia theo checkpoint thì người giữ checkpoint sau phải chờ người giữ checkpoint trước.

| Người | Phần việc |
| --- | --- |
| Vũ Quang Minh | Workflow (A) + integration |
| Nguyễn Công Quân | Single agent (B) |
| Hồ Anh Dũng | Orchestrator (C) + handoff + kiểm secret trong trace |
| Trần Việt Thịnh | Ledger/policy/crash + đo đạc (benchmark, ADR) |

**Thứ tự.** Ba shape A, B, C được viết song song từ CP2, mỗi người một file, cùng lấy `swarm_reference.py` làm mẫu. Shape D (swarm) có sẵn, dùng để đối chứng cost và variance. CP3 thêm `crash_at` vào từng shape, CP4 chạy crash suite và rà approval/secret, CP5 chạy benchmark 4 shape × 5 seed rồi chọn shape.

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape A — workflow (`src/lab8/shapes/workflow.py`)

**Đọc gì.** `get_claim_view` (claim_id, principal_id, order_id, ticket) và `lookup_order` (chỉ các field allowlist: order_id, status, delay_days, shipping_fee_vnd, paid_vnd, damage_verified, carrier). Không đọc `parent_secret`, raw headers, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ.

**Quyết định gì.** Một chuỗi bước Python cố định, không có vòng lặp và không để model chọn bước:

| Điều kiện | `status` | `proposal_amount` | Gọi host? |
| --- | --- | --- | --- |
| Không tìm thấy claim | `failed` | 0 | Không |
| Thiếu `order_id` (không lấy mã đơn từ ticket) | `needs_info` | 0 | Không |
| Không thấy đơn hoặc principal không sở hữu đơn | `escalated` | 0 | Không |
| Quote = 0 | `denied` | 0 | Không |
| Quote > 0, host từ chối (có audit `policy_denied`) | `denied` | quote đầy đủ | Có |
| Quote > 0, gọi lại với số khác số đã commit | `failed` | quote đầy đủ | Có |
| Quote > 0, host chấp nhận | `resolved` | quote đầy đủ | Có |

**Gọi host ra sao.** Quote lấy từ `compute_compensation` trên dòng order, bỏ qua số ngày trễ ghi trong ticket. Shape gọi `durability.issue_refund(conn, claim_id, quote, crash_at=crash_at)` với **quote đầy đủ**; host tự trừ phần đơn đã được hoàn bởi claim trước (T13, T14). Kết quả trả về qua `lab8.shapes.common.finish()`, nên `refund_effects` và `committed_audit_count` luôn lấy từ ledger.

**Ranh giới code / model.** Có đúng một lời gọi MockLLM (`purpose="draft"`) để soạn câu trả lời cho khách, gọi sau khi đã quyết định xong. Prompt chỉ có status và số tiền. Model không đọc ticket, không chọn số tiền, không ghi ledger.

**Crash (CP3).** `crash_at` được truyền thẳng vào host. Khi host ném `InjectedCrash`, shape ghi event `crash` vào trace rồi `raise` lại, không nuốt exception. Chạy lại cùng claim là an toàn nhờ idempotency key `refund:{claim_id}`: ledger vẫn một dòng, vẫn một audit `refund_committed`.

**Trace.** Các event: `claim` {found, order_id}, `lookup_order` (view đã qua allowlist), `quote` {amount_vnd, reason, clause_ids, parts}, `issue_refund` {ok, reason, conflict}, `crash` {at} khi có crash, `decision` {status, proposal_amount, reason}. Cố ý **không** ghi ticket (dữ liệu người dùng, có thể chứa injection), `principal_id`, claim row và order row thô.

**Tự kiểm.** Ma trận student của workflow `62/62`. `src/tests/test_workflow_team.py` thêm 5 test vào cổng host: crash ở cả ba điểm rồi resume vẫn một refund; trace lúc crash không có `CANARY_SECRET` hay ticket; C-002 bị `denied` ở seed 11 và 55.

### Shape B — single agent

**Đọc gì và chạy agent ra sao.** Shape dùng `run_react(..., max_steps=8, worker=True)` với một `decide()` giữ state điều khiển. Agent lần lượt chọn ba read tool `get_claim_view`, `lookup_order`, `compute_compensation`; `runtime.dispatch` từ chối write tool khi actor là worker. Prompt model chỉ chứa phase và tên tool trước, không chứa ticket hay database row. Số ngày/điều khoản viết trong ticket vì vậy không thể ghi đè nguồn sự thật từ order và policy hiện hành.

**Quyết định và ranh giới code/model.** Mỗi bước `decide()` gọi MockLLM để tính model call/token/cost mô phỏng, nhưng tiền chỉ lấy từ `compute_compensation` trên order allowlist. Agent kết thúc với `failed`, `needs_info`, `escalated`, `denied` hoặc trạng thái nội bộ `ready`. Chỉ code Python bên ngoài vòng ReAct mới gọi `issue_refund`; actor không có write registry. Host tiếp tục kiểm approval, principal, trần theo đơn và idempotency trước khi commit.

**Refund và crash.** Khi quote dương, shape truyền **quote đầy đủ** cùng `crash_at` vào host. Kết quả host từ chối thành `denied` (hoặc `failed` khi conflict), thành công thành `resolved`. `src/tests/test_single_team.py` kiểm retry và cả ba crash point; sau resume vẫn đúng một ledger row, một audit `refund_committed` và idempotency key `refund:{claim_id}`.

**Trace.** Shape ghi `agent_action`, quan sát đã rút gọn (`found`, `has_order_id`, `visible`, quote), `react_stop`, `issue_refund` và `decision`. Cố ý không ghi ticket, principal, claim/order row thô, secret, header hay PII. Ma trận student của Single đạt `62/62`.

**Ablation CP5.** Lát cắt Workflow–Single từ benchmark chính `src/reports/benchmark.json` cho thấy trên 14 claim × 5 seed, hai shape cùng pass rate/pass^5 `1.000`. Single có cost/success mô phỏng `30.70` so với `28.87` VND và mean steps `8.21` so với `4.43`; vòng agent không tăng độ đúng trên flow public tuần tự nhưng tăng overhead. Nhóm chạy lại đúng lát cắt này vào `src/reports/ablation_workflow_single.json` và thu được cùng số liệu. Chi tiết phương pháp và boundary ở `research_card.md`.

### Shape C — orchestrator

...

## 4. Kết quả

### 4.1. An toàn khi gặp sự cố và Crash Safety (`src/reports/crash.json`)

Nhóm đã thực thi kiểm thử toàn diện trên bộ lỗi giả lập 20 điểm (`python -m lab8.crash_test --count 20 --out reports/crash.json`), đạt kết quả tuyệt đối **`crash_safety 20/20`** (100% pass):

- **CR-01 đến CR-05 (`before_effect`):** Crash kích hoạt trước khi ghi nhận tác vụ hoàn tiền. Khi khôi phục, hệ thống hoàn tiền thành công đúng 1 lần, không tạo trạng thái dở dang hay dòng audit rác.
- **CR-06 đến CR-12 (`after_effect_before_checkpoint`):** Crash kích hoạt ngay sau khi ghi ledger nhưng trước khi hoàn tất checkpoint. Khi resume, cơ chế khóa Idempotency `refund:{claim_id}` trong cùng một SQLite transaction nhận diện `idempotent_replay`, bảo đảm không bao giờ thanh toán trùng lặp (không double pay) và giữ đúng 1 sự kiện audit `refund_committed`.
- **CR-13 đến CR-17 (`after_checkpoint`):** Crash sau checkpoint hoàn tiền, hệ thống nhận diện checkpoint hợp lệ và kết thúc an toàn.
- **CR-18 (`amount_conflict_on_retry`):** Khi gọi lại cùng một claim với số tiền khác số tiền đã commit, Host phát hiện xung đột (`conflict=True`), bảo vệ nguyên vẹn số tiền đã ghi nhận ban đầu.
- **CR-19 (`retry_without_approval`):** Khiếu nại thiếu approval hợp lệ bị từ chối nhất quán qua mọi lần gọi lại, ngăn chặn tuyệt đối việc bypass approval.
- **CR-20 (`swarm_after_effect_before_checkpoint`):** Xác thực an toàn crash trên luồng xử lý multi-agent thực tế (Swarm), xác nhận khả năng phục hồi đồng bộ.

### 4.2. Bảng so sánh 4 kiến trúc (kết quả benchmark từ CP5)

Bảng số liệu tổng hợp từ `src/reports/benchmark.json` trên 5 seed (11, 22, 33, 44, 55) qua 14 claims (70 trials mỗi shape):

| Shape | Pass rate | Pass^5 | Seed min-max | Variance | Cost/success (VND) | Mean steps | P95 steps |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A `workflow` | 1.000 | 1.000 | 1.000 – 1.000 | 0.000000 | 28.87 | 4.43 | 5.0 |
| B `single` | 1.000 | 1.000 | 1.000 – 1.000 | 0.000000 | 30.70 | 8.21 | 9.0 |
| C `orchestrator` | 1.000 | 1.000 | 1.000 – 1.000 | 0.000000 | 40.00 | 2.00 | 2.0 |
| D `swarm` | 0.986 | 0.929 | 0.929 – 1.000 | 0.000816 | 49.57 | 2.80 | 3.0 |

**Nhận xét:**
- **Shape A (Workflow):** Đạt chi phí thấp nhất (28.87 VND/thành công) và độ ổn định tuyệt đối (variance = 0), không phụ thuộc vào vòng lặp suy luận của model.
- **Shape B (Single):** Số bước thực thi cao nhất (8.21 bước trung bình) do vòng lặp ReAct phải liên tục thăm dò và gọi tool tuần tự, chi phí cao hơn workflow (30.70 VND).
- **Shape C (Orchestrator):** Số bước ngắn nhất (2.0 bước) nhờ cơ chế dispatch chuyên biệt của orchestrator và investigator, nhưng chi phí cao hơn (40.00 VND) do tải payload handoff.
- **Shape D (Swarm):** Đắt nhất (49.57 VND) và có độ dao động (variance = 0.000816, pass^5 chỉ đạt 0.929 do lỗi ở seed 55 trên claim C-002: status resolved != denied). Nhóm chọn **Workflow** vì là kiến trúc ít tự chủ nhất mà vẫn đạt 100% hiệu năng và an toàn tối đa.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

- **Bộ lọc pytest của Single:** lệnh ngắn `-k single` khớp cả tên hàm `test_public_single_run_cases`, nên vô tình chạy case của bốn shape và hiển thị lỗi từ shape chưa hoàn thành. Nhóm dùng bộ lọc chính xác `-k "single and not workflow and not orchestrator and not swarm"`, xác nhận riêng Shape B đạt `62 passed`.
- **Ranh giới agent/host:** vòng ReAct ban đầu dễ bị hiểu là nơi gọi write tool. Nhóm đặt `worker=True`, chỉ dispatch read tool và chuyển việc ghi refund ra code sau vòng lặp; test crash/retry chứng minh host vẫn giữ exactly-once effect.
- **Python trên máy Windows:** `py` mặc định trỏ tới Python 3.14 trong khi lab hỗ trợ 3.11–3.13. Nhóm tạo `.venv` trực tiếp bằng Python 3.13.5, cài `requirements.txt`, rồi xác minh bằng `lab8.smoke pass` và host gate xanh.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- **Giới hạn của MockLLM:** Hệ thống thử nghiệm sử dụng MockLLM với phản hồi xác định dựa trên seed và tra cứu nội bộ; không phản ánh độ trễ mạng thực tế (`latency` ở trạng thái `unavailable`) hay các hành vi ảo giác (hallucination) ngẫu nhiên, không kiểm soát của các mô hình LLM thương mại lớn.
- **Phạm vi bài toán và tập dữ liệu:** Thử nghiệm tập trung vào quy trình bồi thường chậm trễ đơn hàng với các quy tắc tài chính rõ ràng. Trong môi trường thực tế với khiếu nại phức tạp, bằng chứng hình ảnh hư hỏng đa chiều hoặc nội dung phi cấu trúc, các agent tự chủ cao hơn có thể có thêm đất diễn trong khâu phân loại và phân tích thông tin đầu vào.
- **Điều kiện đảo chiều quyết định (Flipping conditions):**
  - Nếu chi phí tính toán và token giảm về mức không đáng kể, hoặc khi quy tắc nghiệp vụ liên tục thay đổi hàng ngày (không thể viết code cố định kịp thời), kiến trúc Agent có thể được ưu tiên hơn nhờ tính thích ứng linh hoạt.
  - Tuy nhiên, trong các nghiệp vụ tác động trực tiếp đến dòng tiền (Ledger/Financial impact), nguyên tắc "ít tự chủ nhất vẫn làm được việc" kết hợp cơ chế kiểm soát Host nghiêm ngặt luôn là phòng tuyến vững chắc nhất chống gian lận và rò rỉ ngân sách.

## 8. Tài liệu tham khảo

- Yubin Kim et al., [*Towards a Science of Scaling Agent Systems*](https://arxiv.org/abs/2512.08296), 2025/2026 — nguồn cho hypothesis và boundary của ablation Workflow–Single.
- Shunyu Yao et al., [*ReAct: Synergizing Reasoning and Acting in Language Models*](https://arxiv.org/abs/2210.03629), ICLR 2023 — mô hình vòng action/observation dùng để tổ chức Shape B.
- Tài liệu nội bộ của lab: `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md` và `src/README.md`.
