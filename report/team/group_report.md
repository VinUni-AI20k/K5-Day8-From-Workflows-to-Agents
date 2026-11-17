# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: GiCungDuoc
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `<cập nhật ở CP5>`

## 2. Mục tiêu và cách tiếp cận

### Mục tiêu bài toán
Bài lab mô phỏng quy trình xử lý claim hoàn phí vận chuyển và đền bù hàng hỏng của **LogiX-VN** trên bốn kiến trúc (`workflow`, `single`, `orchestrator`, `swarm`) dùng chung chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult` và cùng `MockLLM` cố định theo seed. Mục tiêu của nhóm là:
1. Tuân thủ chặt ranh giới code/model: toàn bộ logic tính tiền (`compute_compensation`), kiểm tra policy hiện hành (`is_current=1`, `effective_date <= 2026-11-15`), chống prompt injection từ nội dung ticket, kiểm tra approval và idempotency/trần hoàn tiền theo đơn do **code và host (`durability.issue_refund`)** quyết định.
2. Đảm bảo tuyệt đối 3 điều kiện must-pass: không refund khi thiếu approval hợp lệ (`approval_bypass_count == 0`), không rò rỉ `CANARY_SECRET_*` hay PII trong trace/stdout (`secret_leak_count == 0`), và an toàn khi crash (`20/20` crash suite).
3. Đo lường khách quan (pass rate, pass^5, seed variance, cost/success) trên cùng corpus và seed để chọn kiến trúc **ít tự chủ nhất mà vẫn hoàn thành tốt nhiệm vụ**.

### Phân công và thứ tự triển khai
Nhóm 5 thành viên chia vai chuyên biệt theo kiến trúc và kiểm thử:
- **Phạm Quốc Huy (Lead & QA Integration):** quản lý Git/CI, giữ cổng host (`pytest -q`) luôn xanh, chuẩn hóa contract `RunResult`/`Trace v1` qua `src/tests/test_student_integration.py` và chạy `check_submission`.
- **Trần Tùng Lâm (Shape A — Workflow Lead):** triển khai `workflow.py` (tuần tự tất định, không dùng `REFERENCE_WEAKNESS`) làm baseline ít tự chủ nhất.
- **Đặng Đức Minh (Shape B — Single ReAct):** triển khai `single.py` (vòng lặp ReAct tối đa 8 bước, chỉ dùng read-tools, chống prompt injection).
- **Nguyễn Thành Tâm (Shape C — Orchestrator & Security Lead):** triển khai `orchestrator.py` (handoff allowlist `handoff.v1`, investigator read-only, kiểm soát zero-leak trace).
- **Trịnh Gia Huy (Durability, Eval & Benchmark Lead):** kiểm thử T11/T12 và `crash_test` 20/20, chạy `benchmark.json`, phân tích số liệu điền `decision_adr.md` và `research_card.md`.

Thứ tự thực hiện bám sát 5 checkpoint: CP1 (cài đặt môi trường, đọc contract, viết test tích hợp giữ cổng host) → CP2–CP3 (hoàn thiện lần lượt 3 shape `workflow`, `single`, `orchestrator` kèm handoff và `crash_at`) → CP4 (chạy crash suite 20/20 và rà soát bảo mật/trace) → CP5 (chạy benchmark 4 shape × 5 seed, hoàn thiện ADR, research card và `check_submission` đạt `0 FAIL`).

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape A: Workflow

File: `src/lab8/shapes/workflow.py`, test: `src/tests/test_student_workflow.py`.

Shape A là chuỗi bước Python cố định, không có vòng lặp và không có nhánh do model chọn. Mỗi claim gọi tối đa 3 tool đọc và tối đa 1 lần ghi qua host.

| Bước | Thao tác | Điều kiện dừng |
| --- | --- | --- |
| 1 | `get_claim_view` | Không có claim → `failed` |
| 2 | Kiểm `order_id` trên claim row | Rỗng → `needs_info`, proposal 0 |
| 3 | `lookup_order(order_id, principal_id)` | Không thấy hoặc sai principal → `escalated`, proposal 0 |
| 4 | `compute_compensation(order)` | Quote = 0 → `denied`, proposal 0 |
| 5 | `durability.issue_refund(conn, claim_id, quote, crash_at=crash_at)` | Host từ chối → `denied`; conflict → `failed`; thành công → `resolved` |

Ranh giới code / model:

- Số tiền chỉ do `compute_compensation` tính từ order row và policy hiện hành. Ticket không được parse, nên số ngày trễ khai sai (T02), clause cũ (T06) hay câu injection (T09) không ảnh hưởng kết quả.
- Shape truyền quote đầy đủ vào host. Host tự trừ phần đã hoàn của đơn: T13 bị từ chối với `order_already_refunded`, T14 có proposal 150000 và ledger ghi 120000.
- MockLLM chỉ được gọi một lần để soạn câu trả lời. Prompt chỉ gồm `status` và `proposal`.
- `crash_at` được chuyển thẳng cho host. Khi có `InjectedCrash`, shape ghi trace rồi ném lại lỗi. Các exception khác được trả về dưới dạng `failed` để `run_claim` không ném lỗi ra ngoài.

Trace ghi ở mọi nhánh return, gồm các event `get_claim_view` (chỉ `claim_id`, `found`, `order_id`), `lookup_order` (7 field allowlist), `compute_compensation`, `issue_refund_request`, `issue_refund_result` và `decision`. Trace không chứa ticket, `parent_secret`, header hay PII của đơn hàng.

Kết quả chạy local trên bộ public:

- `pytest -m student -k workflow`: 62/62 passed.
- `pytest -q` (cổng host và test workflow): 141 passed.
- `lab8.crash_test --count 20`: 20/20.
- Benchmark 14 claim × 5 seed: pass rate 1.000, pass^5 1.000, variance 0, cost/success 28.87 VND (swarm: 0.986 / 0.929 / 0.000816 / 49.57). Steps trung bình là 5.07, cao hơn swarm vì metric này đếm số event trong trace chứ không đếm số lần gọi model.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
