# Báo cáo cá nhân — Nguyễn Võ Thái Bảo

## 1. Thông tin thành viên

- Họ tên: Nguyễn Võ Thái Bảo
- MSSV: 2A202603638
- Email: baonguyenvothai@gmail.com
- GitHub: https://github.com/baonvt

## 2. Phần việc phụ trách

- Triển khai Shape A — workflow xác định.
- Thêm test cho workflow.
- Chạy benchmark public và crash suite, lưu report do công cụ sinh.

## 3. Đóng góp cụ thể

- Hoàn thiện `src/lab8/shapes/workflow.py`: đọc claim qua tool allowlist, kiểm tra quyền sở hữu order, tính quote từ dữ liệu order/policy có cấu trúc và giao quote đầy đủ cho `durability.issue_refund`.
- Không dùng ticket để quyết định số ngày trễ hoặc số tiền; truyền `crash_at` tới host và để crash exception truyền ra.
- Thêm `src/tests/test_workflow_shape.py` cho ticket khai sai ngày trễ, quote đầy đủ khi order đã có refund trước, và trace hợp lệ ở nhánh thiếu order.
- Chạy benchmark bốn shape và crash suite; lưu `src/reports/benchmark.json`, `src/reports/crash.json`.

## 4. Bằng chứng

- Commit kỹ thuật: `cb1cb3f`.
- Test thêm: `src/tests/test_workflow_shape.py`; workflow student slice đạt 62/62.
- Benchmark: run tiêu biểu `R-workflow-C-001-s11`; workflow đạt 70/70 trial, pass rate `1.000`, pass^5 `1.000`, seed variance `0.000000`, cost/success `27.86` VND mô phỏng và mean steps `3.50`.
- Crash suite: `20/20` trong `src/reports/crash.json`.
- Cổng host toàn nhóm: `63 passed`; student matrix: `248 passed`.

## 5. Công cụ AI đã dùng

Đã dùng Codex để đọc hướng dẫn/contract, hỗ trợ triển khai và rà soát test. Tự kiểm bằng cách chạy pytest, đối chiếu kết quả với luật trong `docs/business_rules.md` và `docs/contracts.md`, rồi sinh benchmark/crash report bằng CLI của lab. Không sửa tay JSON report.

## 6. Tự đánh giá

Workflow đạt toàn bộ trial public với chi phí mô phỏng thấp nhất trong bốn shape. Cách làm giữ việc tính tiền và ghi ledger ở code/host, giúp flow dễ kiểm tra và tránh tin vào nội dung ticket. Kết quả hiện chỉ phản ánh 14 claim public và MockLLM; cần dựa thêm vào hidden grade trước khi kết luận về dữ liệu ngoài bộ public.
