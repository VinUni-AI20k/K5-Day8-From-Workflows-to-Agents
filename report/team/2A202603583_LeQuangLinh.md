# Báo cáo cá nhân — Le Quang Linh

## 1. Thông tin thành viên

- Họ tên: Le Quang Linh
- MSSV: 2A202603583
- Email: linhlqhe181396@fpt.edu.vn
- GitHub: [linhlqhe181396](https://github.com/linhlqhe181396)
- Vai trò: Phụ trách Shape B (single-agent ReAct), kiểm thử hồi quy và báo cáo phần việc cá nhân

## 2. Phần việc phụ trách

Phụ trách Shape B (single-agent ReAct): kiểm tra vòng ReAct có giới hạn, bảo đảm model chỉ dùng công cụ đọc và code lấy quote rồi gọi host để xử lý refund. Bổ sung kiểm thử hồi quy cho T02 ở seed 55, giới hạn số model call và tính khớp run_id của trace.

## 3. Đóng góp cụ thể

Thêm `src/tests/test_team_single.py` với hai kiểm thử: T02 phải bị từ chối ở seed 55 dù ticket khai trễ 5 ngày; và lần chạy Single phải nằm trong giới hạn 8 model call, có trace JSON với `run_id` khớp kết quả. Phần Single dùng `run_react` với tối đa 8 bước; số tiền được tính bằng tool trong code và thao tác ghi refund đi qua host.

## 4. Bằng chứng

- `python -m pytest -q tests/test_team_single.py`: 2 passed.
- `python -m pytest -q -m student -o addopts= -k single`: 242 passed, 93 deselected.
- `python -m pytest -q`: 89 passed, 248 deselected.
- Ví dụ trace được kiểm tra: `R-single-C-001-s11`.

## 5. Công cụ AI đã dùng

GitHub Copilot trong VS Code hỗ trợ rà soát và viết kiểm thử. Tôi đối chiếu hành vi với contract của lab, rồi chạy kiểm thử hồi quy, ma trận student và cổng test mặc định. Tôi kiểm tra rằng model chỉ dùng công cụ đọc, quote được tính từ dữ liệu có cấu trúc, host là nơi duy nhất ghi refund, và trace có `run_id` khớp.

## 6. Tự đánh giá

Hoàn thành phần kiểm thử và bằng chứng cho Shape B: T02 không được hoàn tiền chỉ dựa trên số ngày khách ghi trong ticket; vòng ReAct nằm trong giới hạn; trace đáp ứng kiểm tra `run_id`. Kết quả xác nhận trên bộ public, không đại diện cho hiệu năng của model sản xuất.
