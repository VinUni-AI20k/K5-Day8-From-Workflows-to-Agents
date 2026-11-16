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

### Shape C — Orchestrator và investigator chỉ đọc

Orchestrator đọc claim bằng `get_claim_view`. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`, không giao việc cho investigator và không ghi refund. Các nhánh trả kết quả đều dùng `finish()` để ghi trace và lấy bằng chứng ledger từ host.

Handoff được tạo bằng `make_handoff`, với `facts` rỗng và ba tool được phép: `lookup_order`, `lookup_policy`, `compute_compensation`. Không chuyển ticket, parent context, secret hoặc raw headers vào handoff. Investigator chạy qua `run_readonly_investigators` và chỉ được gọi tool đọc. Quyền sở hữu đơn được kiểm qua `lookup_order`; đơn không tìm thấy hoặc ngoài phạm vi principal trả `escalated`.

Số tiền lấy từ `compute_compensation` trên dữ kiện đơn và policy hiện hành, không lấy từ lời kể trong ticket. Quote bằng 0 trả `denied`. Quote dương được truyền đầy đủ vào `durability.issue_refund`; host kiểm approval, trần theo đơn và idempotency. Orchestrator không tự trừ tiền đã hoàn. Host từ chối trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`. Tham số `crash_at` được chuyển cho host và `InjectedCrash` được phép truyền ra ngoài; kết nối luôn đóng trong `finally`.

MockLLM chỉ soạn phản hồi từ status và proposal đã được code quyết định. Trace gồm `handoff`, `investigator`, `quote`, `decision` tùy nhánh; event investigator chỉ ghi visibility, reason và số policy. Không dump claim, order hoặc toàn bộ kết quả investigator.

Phần mô tả workflow và single: chờ thành viên phụ trách bổ sung.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

Khi kiểm tra phần orchestrator trên máy hiện tại, `python -m lab8.smoke` báo: `Python 3.10.0 quá cũ. Cần Python 3.11+`. Các lệnh pytest vẫn chạy được: test student riêng orchestrator đạt 62 passed; test mặc định gồm test host và ba ca kiểm thử bảo mật mới đạt 57 passed. Đây là kết quả trên Python 3.10, chưa thay thế xác nhận môi trường yêu cầu. Cần chạy lại smoke và test trên Python 3.11–3.13 trước khi nộp.

Test mới tại `src/tests/test_orchestrator_security.py` kiểm tra ticket chứa chỉ dẫn giả và canary không làm thay đổi quote hoặc xuất hiện trong handoff, trace, kết quả và stdout/stderr. Hai ca còn lại kiểm tra claim không tồn tại và thiếu mã đơn không được giao cho investigator nhưng vẫn có trace hợp lệ. Các test mới dùng thư mục tạm để tách artifact giữa các lần chạy.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
