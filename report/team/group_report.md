# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

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
