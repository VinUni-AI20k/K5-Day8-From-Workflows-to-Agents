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

...

### 3.3 Shape C — Orchestrator

Code: `src/lab8/shapes/orchestrator.py`. Test riêng: `src/tests/test_orchestrator_own.py`.

**Luồng xử lý.** Orchestrator đọc claim row, rồi chia việc thành hai vai:

1. Claim không tồn tại thì `failed`. Thiếu `order_id` thì `needs_info` (không lấy mã đơn từ chữ trong ticket).
2. Orchestrator dựng handoff bằng `lab8.handoff.make_handoff` với `facts` rỗng và bốn tool chỉ đọc theo thứ tự `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`. `lookup_order` đứng trước vì `compute_compensation` cần dữ liệu đơn.
3. Investigator chạy qua `run_readonly_investigators`. Investigator không có tool ghi và không thấy claim row.
4. Đơn không thấy hoặc sai chủ thì `escalated`. Quote bằng 0 thì `denied` và không gọi host.
5. Quote lớn hơn 0 thì **orchestrator** (không phải investigator) gọi `durability.issue_refund` với quote đầy đủ và `crash_at`. Host tự trừ phần đã hoàn trên cùng đơn, nên shape không tự trừ (T13, T14).
6. Kết quả host được ánh xạ: ghi được thì `resolved`; từ chối thì `denied`; xung đột số tiền thì `failed`. `proposal_amount` luôn là quote đầy đủ.

**Ranh giới code và model.** Số tiền do `compute_compensation` tính từ dòng order trong database. Ngày trễ trong ticket không được dùng, nên shape không có điểm yếu "tin ticket" như swarm tham chiếu. MockLLM chỉ được gọi hai lần mỗi claim (`plan`, `draft`) để soạn chữ, không quyết định tiền, approval hay ghi ledger.

**Handoff và trace.** Handoff đi qua allowlist trong code (`ALLOWED_FIELDS`, `FACT_KEYS`), không dùng tóm tắt bằng LLM làm bước lọc. Trace chỉ ghi handoff đã sanitize, kết quả `lookup_order`, số policy, quote và quyết định (event `handoff`, `investigator`, `quote`, `decision`, `error`, `crash`). Không ghi claim row, ticket hay parent context. Mọi nhánh return đều đi qua `finish()` nên luôn có trace hợp lệ.

**Crash.** `crash_at` được truyền vào `issue_refund`. `InjectedCrash` chỉ ghi trace rồi `raise` lại, không bị bắt.

**Kiểm chứng (chạy ngày 2026-11-17).**

- `pytest -q -m student -o addopts= -k orchestrator`: 62 passed (gồm T11 gọi lại cùng claim, T12 crash rồi resume).
- `pytest -q` (cổng host): xanh.
- `test_orchestrator_own.py` (16 test): trace và kết quả của 14 claim public không có `CANARY_SECRET_` hay thông tin cá nhân; handoff không có `parent_secret`, `raw_headers` hay tool ghi; crash vẫn ném `InjectedCrash`.
- Số benchmark (pass rate, pass^5, cost/success) của shape này: điền sau CP5 từ `src/reports/benchmark.json`.

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
