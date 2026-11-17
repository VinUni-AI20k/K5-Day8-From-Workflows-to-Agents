# Báo cáo cá nhân — 2A202603837_NguyenDinhTruong
## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Trường
- MSSV: 2A202603837
- Email: 26ai.truongnd@vinuni.edu.vn
- GitHub: ngdinhtruong28

## 2. Phần việc phụ trách

Tôi phụ trách phần đánh giá và tổng hợp báo cáo nhóm, cùng với việc chạy các kiểm tra hệ thống để đảm bảo 3 shape workflow, single và orchestrator đều hoạt động đúng, đồng thời cập nhật các bằng chứng benchmark và crash test cho báo cáo cuối cùng.

Cụ thể:
- viết và rà soát báo cáo nhóm, phần tóm tắt quyết định kiến trúc
- chạy benchmark 4 shape trên cùng claim và cùng seed để so sánh pass rate, variance, cost/success
- chạy crash suite để kiểm tra crash-safe và idempotency
- chạy test cho cả 3 shape để xác nhận không còn lỗi logic chính
- phối hợp với các thành viên khác để thống nhất output cuối cùng trước khi nộp

## 3. Đóng góp cụ thể

- Tổng hợp các kết quả chạy từ các lệnh sau:
  - `python -m pytest -q -m student -o addopts= -k workflow`
  - `python -m pytest -q -m student -o addopts= -k single`
  - `python -m pytest -q -m student -o addopts= -k orchestrator`
  - `python -m pytest -q`
  - `python -m lab8.crash_test --count 20 --out reports/crash.json`
  - `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Kiểm tra lại các chỉ số quan trọng của bài: pass rate, pass^5, variance, cost/success để đưa ra nhận định về kiến trúc nào là ít tự chủ nhất nhưng vẫn hoàn thành nhiệm vụ.
- Tạo/điều chỉnh các phần dựng báo cáo: tóm tắt quá trình làm việc, cam kết về bảo mật trace, idempotency, crash-safe và sự ổn định của các shape.
- Đảm bảo báo cáo cá nhân phản ánh đúng phần việc và bằng chứng thực tế đã chạy, không ghi các kết quả giả tưởng.

## 4. Bằng chứng

Bằng chứng cho phần công việc của tôi gồm các lệnh kiểm tra và file output được sinh ra trong quá trình làm việc:

- `src/reports/crash.json`: file output của crash suite
- `src/reports/benchmark.json`: file output của benchmark 4 shape
- kết quả chạy pytest của 3 shape và toàn bộ hệ thống:
  - `python -m pytest -q -m student -o addopts= -k workflow`
  - `python -m pytest -q -m student -o addopts= -k single`
  - `python -m pytest -q -m student -o addopts= -k orchestrator`
  - `python -m pytest -q`

Các file này là bằng chứng phục vụ cho việc viết báo cáo nhóm và chuẩn bị submission cuối cùng.

## 5. Công cụ AI đã dùng

- Công cụ hỗ trợ: Copilot / GitHub Copilot trong quá trình đọc code, rà soát lỗi, kiểm tra logic handoff, trace, và test cases.
- Mục đích sử dụng:
  - gợi ý cách tổ chức code và test theo chuẩn của lab
  - rà soát các nhánh lỗi trong workflow / single / orchestrator
  - hỗ trợ viết báo cáo ngắn gọn, rõ ràng và đúng cấu trúc yêu cầu
- Tôi đã tự kiểm tra lại mọi đề xuất bằng cách chạy pytest, crash suite và benchmark để đảm bảo kết quả phù hợp với repo và yêu cầu thực tế của bài.

## 6. Tự đánh giá

Mức đánh giá: Tốt.
Lý do:
- Đã đóng góp vào phần tổng hợp kết quả chạy và báo cáo nhóm, một phần khá quan trọng vì bài này đánh giá không chỉ ở mã mà còn ở việc lựa chọn kiến trúc dựa trên dữ liệu thực tế.
- Đảm bảo luôn kiểm tra lại bằng chứng chạy thực tế trước khi ghi vào báo cáo.
- Nhận thức rõ rằng trong lab này, thành công phụ thuộc vào cả chất lượng code lẫn độ tin cậy của dữ liệu benchmark và crash test.

