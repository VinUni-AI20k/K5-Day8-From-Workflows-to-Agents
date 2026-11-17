# Báo cáo cá nhân — 2A202603953_DinhLeThinh

## 1. Thông tin thành viên

- Họ tên: Đinh Lê Thịnh
- MSSV: 2A202603953
- Email: dinhlethinh137@gmail.com
- GitHub: ThinkLee04

## 2. Phần việc phụ trách

- **Task 2 — Single agent:** Hoàn thiện `src/lab8/shapes/single.py` theo vòng lặp ReAct giới hạn tối đa 8 bước; chỉ cho model chọn công cụ đọc dữ liệu có cấu trúc, phần tính tiền và gọi host ghi hoàn tiền do code thực hiện sau vòng lặp.

## 3. Đóng góp cụ thể

- Commit `b2ed187`: cài đặt `src/lab8/shapes/single.py` dùng `run_react` (`max_steps=8`), chỉ gọi công cụ đọc (`lookup_order`, `compute_compensation`), ghi nhận chi phí model theo từng bước vào `Budget`, chỉ ghi các field đã lọc an toàn vào trace (không copy `ticket` hay `parent_secret`), và truyền quote đầy đủ vào host.
- Tạo bộ test hồi quy riêng `src/tests/test_single_agent.py` kiểm chứng ở `C-002` seed `55` không bị lừa bởi số ngày trong ticket, chỉ gọi công cụ đọc và trace sạch secret/ticket.

## 4. Bằng chứng

- Commit `b2ed187` (PR #3 từ nhánh `thinh` vào `main`).
- Test: `src/tests/test_single_agent.py` và ma trận `pytest -q -m student -o addopts= -k "single]"` (`62 passed`).
- Trong `src/reports/benchmark.json`, `single` đạt `pass_rate = 1.000` (70/70), `pass^5 = 1.000`, `seed_variance = 0.000000`, `cost_per_success_vnd = 29.13`.

## 5. Công cụ AI đã dùng

- Sử dụng trợ lý AI để kiểm tra cách hoạt động của vòng lặp `run_react` trong `src/lab8/runtime.py` và thiết kế test kiểm tra tool dispatch.
- Đã chạy trực tiếp `pytest` cho `test_single_agent.py` và ma trận student để xác nhận mọi ca test đều pass.

## 6. Tự đánh giá

- Hoàn thành tốt phần Shape B với ranh giới bảo mật rõ ràng giữa công cụ đọc trong agent và thao tác ghi tiền ở host; cần lưu ý thêm việc bật `worker=True` và lưu trace khi crash đã được bổ sung hoàn thiện khi tích hợp.

