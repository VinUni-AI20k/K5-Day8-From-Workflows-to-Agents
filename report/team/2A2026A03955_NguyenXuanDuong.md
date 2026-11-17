# Báo cáo cá nhân — 2A2026A03955_NguyenXuanDuong

## 1. Thông tin thành viên

- Họ tên: Nguyễn Xuân Dương
- MSSV: 2A2026A03955
- Email: -
- GitHub: -

## 2. Phần việc phụ trách

Phụ trách phần Shape C — orchestrator + handoff và kiểm tra trace/host contract. Cụ thể:

- Implement `run_claim` trong `src/lab8/shapes/orchestrator.py`
- Xây dựng handoff theo allowlist: chỉ truyền dữ liệu đã được sanitize
- Gọi `run_readonly_investigators` để lấy dữ liệu từ order/policy
- Tính quote từ kết quả investigator và truyền đầy đủ quote vào `durability.issue_refund`
- Đảm bảo `crash_at` được forward đúng, không bắt `InjectedCrash`
- Kiểm tra trace JSON được ghi đúng `run_id` và không lộ secret

## 3. Đóng góp cụ thể

- Commit chính: đã làm trực tiếp trên repo làm bài, không có commit riêng bên ngoài trong session hiện tại.
- Test đã sửa/kiểm tra: chạy các suite pytest liên quan đến orchestrator và suite host mặc định.
- Quyết định kỹ thuật:
  - Dùng `make_handoff` với `allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]`
  - Không đồng thời truyền raw claim row hoặc dữ liệu nhạy cảm vào trace
  - Trả về `RunResult` bằng `finish(...)` để đảm bảo `trace_path`, `refund_effects`, `committed_audit_count` khớp ledger

## 4. Bằng chứng

- Chạy test orchestrator: `cd src; python -m pytest -q -m student -o addopts= -k orchestrator`
- Kết quả: `62 passed, 240 deselected`
- Chạy suite host: `cd src; python -m pytest -q`
- Kết quả: `54 passed, 248 deselected`

## 5. Công cụ AI đã dùng

- Đã sử dụng Copilot/AI assistant để đọc hướng dẫn README, đọc file code cấu trúc và đề xuất patch cho phần orchestrator.
- Sau khi generate code, tôi tự kiểm tra bằng pytest và đối chiếu với điều kiện contract của `RunResult` và trace.
- Việc tự kiểm tra đã được thực hiện bằng các lệnh trên, không chỉ dựa vào nhận định bằng lời nói.

## 6. Tự đánh giá

Mình tự đánh giá phần làm việc của mình ở mức đạt yêu cầu. Đã hoàn thành đúng phần người 3 theo hướng dẫn, đảm bảo orchestrator hoạt động, hệ thống host contract được giữ và không làm rò rỉ secret trong trace. Các test host và test student cho phần orchestrator đều đã pass.
