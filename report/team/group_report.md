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

### Workflow deterministic

Workflow do Nguyễn Minh Quân triển khai xử lý claim theo chuỗi bước cố định: đọc claim bằng `get_claim_view`, kiểm tra `order_id`, tra cứu order theo phạm vi principal bằng `lookup_order`, tính full entitlement bằng `compute_compensation`, rồi chuyển full quote cho `issue_refund`. Shape không dùng MockLLM để quyết định nghiệp vụ hoặc số tiền; `model_calls` bằng 0 trong lần chạy kiểm chứng.

Các nhánh kết quả tuân theo contract chung: claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`; order không hiển thị trả `escalated`; quote bằng 0 trả `denied` mà không ghi ledger; host từ chối approval trả `denied`; amount conflict trả `failed`; refund hợp lệ trả `resolved`. `proposal_amount` luôn giữ full quote khi quote lớn hơn 0, còn host chịu trách nhiệm áp approval, giới hạn theo order và idempotency.

Trace chỉ ghi các trường đã allowlist gồm số tiền quote, reason, clause ID, refund request và quyết định cuối. Workflow không ghi ticket, claim row, order row, secret hoặc PII. Public matrix của workflow đạt 62/62; retry C-001 và crash/resume C-012 đều giữ đúng một refund và một audit `refund_committed`.

Phần mô tả `single` và `orchestrator` sẽ được các thành viên phụ trách hai shape bổ sung.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

- Trên Windows, pytest ban đầu báo `PermissionError: [WinError 5]` tại thư mục `%TEMP%\\pytest-of-minhq`, khiến 62 case workflow lỗi ở bước setup trước khi code được chạy. Nhóm chuyển `basetemp` vào repository bằng `--basetemp .pytest-tmp\\workflow` và thêm `.pytest-tmp/` vào `.gitignore`. Sau đó ma trận workflow chạy thành công với 62 passed.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
