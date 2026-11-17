# Báo cáo cá nhân — 2A202603784_PhamLeChuan

## 1. Thông tin thành viên

- Họ tên: Phạm Lê Chuẩn
- MSSV: 2A202603784
- Email: lechuanpham@gmail.com
- GitHub: 22520160

## 2. Phần việc phụ trách

- Phụ trách shape `workflow` và tích hợp shape này với host/runtime chung của dự án.
- Kiểm tra luồng từ đọc claim, tra cứu order, tính quote theo dữ liệu order đến gửi quote đầy đủ cho host xử lý refund.
- Phối hợp bảo đảm kết quả trả về theo `RunResult` và trace được ghi theo contract.

## 3. Đóng góp cụ thể

- Với `workflow`, dùng các bước Python xác định để đọc claim và order, sau đó gọi `compute_compensation`; không dùng nội dung ticket làm căn cứ tính tiền.
- Tích hợp bước ghi refund qua `durability.issue_refund`, chuyển nguyên quote để host kiểm tra approval, giới hạn hoàn theo order và idempotency.
- Giữ các nhánh kết quả như `needs_info`, `escalated`, `denied` và `resolved` đi qua hàm hoàn tất chung để tạo kết quả và trace.
- Bổ sung test integration riêng cho workflow; thay đổi hiện chưa commit.

## 4. Bằng chứng

- Mã workflow: `src/lab8/shapes/workflow.py`.
- Tích hợp kết quả và trace: `src/lab8/shapes/common.py` và `src/lab8/trace.py`.
- Host ghi refund: `src/lab8/durability.py`.
- Test riêng: `python -m pytest -q tests/test_workflow_integration.py` — 3 passed (14 claim public, retry, crash/resume).
- Ma trận workflow: `python -m pytest -q -m student -o addopts= -k workflow` — 62 passed.
- Smoke: `python -m lab8.smoke` — pass. Chưa chạy `lab8.check_submission` hoặc benchmark/crash report tổng thể.
- Commit và run ID cá nhân: chưa điền; cần đối chiếu commit/run thực tế trước khi nộp.

## 5. Công cụ AI đã dùng

- Dùng OpenAI Codex để đọc yêu cầu, rà soát đường đi của workflow qua host và hỗ trợ soạn báo cáo theo thông tin có trong repository.
- Đối chiếu nội dung báo cáo với mã nguồn và kết quả test đã chạy; commit hash vẫn cần cập nhật sau khi commit.

## 6. Tự đánh giá

- Đã xác định rõ ranh giới giữa workflow và host: workflow đọc dữ liệu, tạo quote từ order; host kiểm soát quyền refund và ghi ledger.
- Cần cập nhật commit hash sau khi commit; thông tin test cá nhân đã được ghi ở mục bằng chứng.
