# Báo cáo cá nhân — Nguyễn Trung Hải

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trung Hải
- MSSV: 2A202603728
- Email: trunghaicva@gmail.com
- Nhánh GitHub: `NguyenTrungHai`

## 2. Phần việc phụ trách

Phần được giao là kiến trúc B, `single`, trong `src/lab8/shapes/single.py`. Shape sử dụng vòng ReAct tối đa 8 bước để lấy thông tin claim, tra đơn theo quyền của người yêu cầu và tính khoản đề xuất từ dữ liệu đơn hàng và chính sách.

## 3. Mã nguồn và đóng góp

Mã triển khai hiện có đến từ commit `91b00e4` của repo nguồn. Hàm Python `decide` chọn công cụ dựa trên kết quả bước trước. `MockLLM` ghi nhận mức sử dụng model, còn lệnh gọi ghi hoàn tiền nằm ngoài vòng lặp. Shape chuyển toàn bộ khoản đề xuất cho `issue_refund` để host kiểm tra phê duyệt và trần theo đơn.

Phần chuẩn bị trên nhánh `NguyenTrungHai` bổ sung test `test_single_step_cap_stops_before_refund`. Test xác nhận shape yêu cầu giới hạn 8 bước và mô phỏng việc hết lượt trước khi có đề xuất. Shape phải trả về `failed` với lý do `step_cap` và dừng trước khi gọi ghi hoàn tiền.

## 4. Bằng chứng

Chạy từ thư mục `src`:

```powershell
python -m pytest -q -m student -o addopts= -k 'single and not workflow and not orchestrator and not swarm'
python -m pytest -q tests/test_single_agent.py
```

Kết quả tự kiểm trên môi trường lab08: 62/62 test public và 1/1 test giới hạn bước đạt. Ca T11 kiểm chạy lại claim và ca T12 kiểm phục hồi sau crash. Benchmark public chạy riêng cho `single` đạt 70/70 lượt, pass⁵ 100% và chi phí mô phỏng 35,95 VND mỗi lượt đúng (ví dụ run ID R-single-C-001-s11). `workflow` đạt cùng tỷ lệ đúng ở mức 34,29 VND. Số liệu dùng MockLLM và 14 claim public.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc mã, thêm test giới hạn bước, chạy ma trận public cho `single` và soạn báo cáo. Ma trận public đạt 62/62 test và test mới đạt 1/1.

## 6. Tự đánh giá

Thành viên bổ sung phần tự đánh giá dựa trên công việc đã trực tiếp thực hiện.
