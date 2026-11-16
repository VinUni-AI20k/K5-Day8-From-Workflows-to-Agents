# Báo cáo cá nhân — datnguyen101004_PhamNguyenTatDat

## 1. Thông tin thành viên

- Họ tên: Phạm Nguyễn Tất Đạt
- MSSV: datnguyen101004
- Email: datnguyen101004@gmail.com
- GitHub: datnguyen101004

## 2. Phần việc phụ trách

- **Integration & Tooling (CP1):** Thiết lập môi trường phát triển ảo, kích hoạt dependencies, kiểm tra smoke test và cổng host pytest, chạy Crash suite đạt 20/20, bổ sung bộ test kiểm định môi trường và quy chuẩn bài nộp (`check_submission`).
- **Bonus Topic (B2):** Nghiên cứu mở rộng gắn nhãn lỗi Multi-Agent theo phân loại MAST (NeurIPS 2025).

## 3. Đóng góp cụ thể

- Thiết lập Python 3.12 virtual environment (`.venv`) và cài đặt `requirements.txt`.
- Chạy xác nhận `python -m lab8.smoke` và đảm bảo cổng host `python -m pytest -q` đạt 58/58 test xanh (100% pass).
- Viết mới bộ test tích hợp `src/tests/test_integration_harness.py` gồm 4 bài kiểm tra:
  - `test_environment_and_runtime_compliance`: kiểm định Python 3.11–3.13 và SQLite runtime.
  - `test_fixtures_integrity`: kiểm định tính toàn vẹn của 14 public claims (`C-001` đến `C-014`) và world state.
  - `test_config_manifests_validity`: kiểm định cú pháp các file YAML cấu hình trong `config/`.
  - `test_crash_report_safety_status`: kiểm định trạng thái must-pass của crash safety.
- Chạy sinh `src/reports/crash.json` đạt tuyệt đối `crash_safety: 20/20`.

## 4. Bằng chứng

- Bộ test: `src/tests/test_integration_harness.py` (4 passed)
- Cổng host: `python -m pytest -q` (58 passed)
- Báo cáo crash an toàn: `src/reports/crash.json` (`crash_safety: 20/20`)
- Smoke test: `python -m lab8.smoke pass`

## 5. Công cụ AI đã dùng

- Dùng trợ lý AI hỗ trợ rà soát yêu cầu từ toàn bộ tài liệu Markdown của lab, phân tích quy chuẩn chấm điểm Rubric, tự động hóa việc tạo bộ test harness và thiết lập khung tài liệu nhóm. Đã kiểm tra lại kết quả chạy thực tế qua pytest và smoke test trên máy cục bộ.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các tiêu chí của giai đoạn CP1 và vai trò Integration, tạo nền tảng ổn định và an toàn cho toàn đội bắt tay vào triển khai các shape A, B, C.
