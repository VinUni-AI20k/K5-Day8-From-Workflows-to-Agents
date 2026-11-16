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

### A — Workflow

Workflow thực hiện các bước cố định bằng Python: đọc claim qua `get_claim_view`, kiểm tra quyền xem đơn bằng `lookup_order`, rồi dùng `compute_compensation` để tính quote từ dữ liệu order và policy. Nếu quote dương, workflow chuyển toàn bộ quote cho `durability.issue_refund`; host chịu trách nhiệm kiểm tra approval, áp dụng trần theo đơn, idempotency và ghi ledger. Workflow không dùng model để quyết định số tiền. Trace ghi trạng thái tra cứu, quote đã lọc và quyết định; không ghi dữ liệu nhạy cảm của claim hoặc order.

### B — Single agent

Single Agent sử dụng vòng ReAct có giới hạn tối đa 8 bước. Mỗi lần quyết định được tính vào `Budget`; agent chỉ được gọi read tool vì `run_react` chạy với `worker=True`. Luồng chính là đọc claim qua `get_claim_view`, dùng `lookup_order` để kiểm tra quyền sở hữu và lấy dữ liệu có cấu trúc, sau đó gọi `compute_compensation`. Agent không lấy số ngày trễ hoặc trạng thái hư hỏng từ ticket, nên tránh được trường hợp người dùng nói quá hoặc chèn chỉ dẫn như “ignore policy”.

Sau vòng ReAct, code của shape lấy quote và gọi `durability.issue_refund` với toàn bộ entitlement. Host tiếp tục kiểm tra approval, trần hoàn tiền theo đơn và idempotency trước khi ghi ledger. Shape truyền `crash_at`; nếu xảy ra `InjectedCrash`, trace được ghi rồi exception được ném lại để lần resume không tạo refund thứ hai. Trace chỉ ghi `agent_stop`, quote đã lọc và kết quả cổng refund; không ghi raw claim, ticket, header, số điện thoại, địa chỉ hoặc internal note.

Trên public benchmark, Single Agent đạt 70/70 trial: pass rate `1.000`, pass^5 `1.000`, seed variance `0`, cost/success mô phỏng `29.19 VND`, mean/p95 steps `2.50/3`.

### C — Orchestrator

[Nhóm bổ sung mô tả orchestrator, investigator và handoff đã sanitize sau khi tích hợp và kiểm chứng.]

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

Crash suite đã chạy: `crash_safety 20/20` (`src/reports/crash.json`). Benchmark 4 shape và các số liệu so sánh đang chờ nhóm chạy; không điền số liệu trước khi có report do công cụ sinh ra.

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
