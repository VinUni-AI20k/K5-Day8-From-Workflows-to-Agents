# Báo cáo cá nhân — 2A202603904_NguyenManhCuong

## 1. Thông tin thành viên

- Họ tên: Nguyễn Mạnh Cường
- MSSV: 2A202603904
- Email: 26ai.cuongnm4@vinuni.edu.vn
- GitHub: https://github.com/NMCcg

## 2. Phần việc phụ trách

Phụ trách triển khai shape **orchestrator** cho Checkpoint 2 và Checkpoint 3 trong
[`src/lab8/shapes/orchestrator.py`](../../src/lab8/shapes/orchestrator.py).

- CP2: Luồng điều phối Orchestrator & Investigator
- CP3: Handoff an toàn, Idempotency & Crash Forwarding
## 3. Đóng góp cụ thể

- Sử dụng make_handoff(...) để lọc dữ liệu bàn giao theo allowlist
- Orchestrator giữ độc quyền gọi issue_refund(conn, claim_id, proposal, crash_at=crash_at) với mức quote đầy đủ
Commit chính: chưa tạo commit riêng tại thời điểm lập báo cáo.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k orchestrator`:
  **62 passed**.
- `python -m pytest -q`:
  **65 passed, 248 deselected**.


## 5. Công cụ AI đã dùng

Đã dùng Copilot SDK trong VS Code để hỗ trợ đọc contract, đối chiếu các shape
tham chiếu, viết phần triển khai workflow và kiểm tra lỗi. Kết quả được tự
kiểm tra bằng test workflow và toàn bộ test mặc định của repository; không
chấp nhận kết quả chỉ dựa trên gợi ý của AI.

## 6. Tự đánh giá

Hoàn thành phần orchestrator của CP2 và CP3 theo đúng contract chung. Mức độ đóng
góp: hoàn thành triển khai và xác minh bằng test; chưa tạo commit riêng