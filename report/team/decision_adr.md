# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 073b783
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0-1.0 / 0.0
- Cost per success (mô phỏng, VND): 28.87
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

## Vì sao shape này

Trên cùng tập corpus public (14 claims) và 5 seed kiểm soát (11, 22, 33, 44, 55), Workflow đạt độ chính xác hoàn hảo (pass rate 1.000, pass^5 1.000, variance 0.000000) với chi phí thấp nhất trong cả 4 hình thái kiến trúc (28.87 VND/thành công, so với 30.70 VND ở Single, 40.00 VND ở Orchestrator và 49.57 VND ở Swarm). Workflow là kiến trúc ít tự chủ nhất nhưng đáp ứng 100% yêu cầu nghiệp vụ bồi thường claim, thực thi chuỗi logic xác định bằng mã nguồn Python cố định, loại bỏ rủi ro vòng lặp vô tận hay trượt ngữ cảnh của LLM.

## Có đáng đổi lấy multi-agent không

Không đáng đổi. Kiến trúc multi-agent (Swarm) không làm tăng pass rate mà ngược lại còn làm phát sinh lỗi phân loại ở seed 55 (claim C-002: giải quyết thay vì từ chối), khiến pass^5 giảm xuống 0.929 và variance tăng lên 0.000816, trong khi chi phí tăng hơn 71% (từ 28.87 lên 49.57 VND). 
Điều kiện đảo chiều quyết định: Chỉ cân nhắc chuyển sang Orchestrator hoặc Multi-agent khi nghiệp vụ xuất hiện các khiếu nại phi cấu trúc phức tạp đòi hỏi nhiều kỹ năng điều tra phân nhánh song song (ví dụ: giám định hình ảnh, xác minh thực địa đa nguồn, đối thoại đàm phán linh hoạt với khách hàng) mà các bước code tuần tự không thể bao quát hết.

## Trace và bằng chứng

Trace của Workflow (`traces/R-workflow-*.json`) chỉ ghi nhận các sự kiện chuẩn xác: `claim` (thông tin định danh), `lookup_order` (thông tin đơn hàng đã lọc qua allowlist), `quote` (công thức tính tiền), `issue_refund` (kết quả giao dịch từ host), `crash` (khi gặp sự cố giả lập) và `decision`. 
Các trường nhạy cảm tuyệt đối **không** được ghi vào trace bao gồm: `ticket` (tránh rủi ro Prompt Injection), `principal_id`, `parent_secret`, thông tin liên hệ khách hàng (SĐT, địa chỉ) và order row thô. Toàn bộ trace đều được rà soát sạch 100% canary secret và PII (`secret_leak_count` = 0).

## Giới hạn

MockLLM là môi trường mô phỏng với phản hồi định sẵn dựa trên seed; không phải mô hình sản xuất và thông số `latency` ở trạng thái `unavailable`. Chi phí tính theo đơn vị VND mô phỏng quy định trong lab. Toàn bộ số liệu được trích xuất tự động từ `src/reports/benchmark.json` và `src/reports/crash.json`, cam kết không chỉnh sửa thủ công.
