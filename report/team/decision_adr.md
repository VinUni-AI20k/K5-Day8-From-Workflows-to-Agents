# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 9b8cc3e
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 28.79
- Crash safety: 20/20
- Secret leak / approval bypass: 0 / 0

## Vì sao shape này

Theo nguyên lý quyền tự chủ tối thiểu (Principle of Least Autonomy) được đặt ra trong mục tiêu môn học: hệ thống cần chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành bài toán một cách tin cậy và tối ưu. Trên cùng bộ dữ liệu thực tế (public claims 14 ca x 5 seeds), shape `workflow` đạt độ chính xác hoàn hảo 100% (pass rate 1.000, pass^5 1.000) với độ dao động bằng 0 (variance 0.000000), đồng thời đạt chi phí rẻ nhất (28.79 VND/success) so với `single` (30.75 VND), `orchestrator` (57.05 VND) và `swarm` (49.57 VND, pass rate 0.986). Toàn bộ logic tiền và điều kiện nghiệp vụ được đảm bảo tất định bởi code, loại bỏ hoàn toàn rủi ro prompt injection hay ảo giác số liệu từ LLM.

## Có đáng đổi lấy multi-agent không

Không đáng đổi. Dữ liệu benchmark cho thấy việc tăng mức độ tự chủ sang đa agent (`orchestrator` hoặc `swarm`) không làm tăng tỷ lệ thành công (thậm chí `swarm` bị giảm pass rate xuống 0.986 và pass^5 xuống 0.929 ở seed 55 do tin số ngày trễ người dùng khai trên ticket), trong khi chi phí giả lập tăng từ 1.7 đến 2 lần. Quyết định sẽ chỉ đảo lại nếu bài toán phát sinh các yếu tố phi cấu trúc cao mà workflow cứng không thể bao quát, ví dụ: cần điều tra hình ảnh hư hỏng hàng hóa bằng thị giác máy tính, phân tích tài liệu khiếu nại phức tạp không có schema cố định, hoặc quy trình nghiệp vụ biến động liên tục hàng ngày đòi hỏi agent tự lập kế hoạch động.

## Trace và bằng chứng

Trace của nhóm ghi lại các sự kiện chính bao gồm: `lookup_order` (trạng thái hiển thị và lý do), `quote` (kết quả tính bồi thường chi tiết từ host), `decision` (các nhánh trả lời cần thêm thông tin hoặc từ chối), và `crash` (ghi nhận điểm ngắt trước khi re-raise InjectedCrash). 
Các trường cố ý **không ghi** vào trace bao gồm: `parent_secret`, số điện thoại, địa chỉ khách hàng, tên mặt hàng, ghi chú nội bộ và token nhạy cảm nhằm tuân thủ Trace Contract v1 và nguyên tắc bảo mật thông tin cá nhân (PII). Nếu trace nằm ngoài vùng scanner quét được, đội ngũ an ninh chứng minh hệ thống không rò rỉ secret bằng cách áp dụng cơ chế kiểm thử tĩnh (AST static analysis) kiểm tra các trường truyền vào hàm ghi trace, kết hợp với runtime assertions tại gateway của Tracer để chặn và cảnh báo mọi payload chứa khóa thuộc denylist trước khi ghi ra đĩa.

## Giới hạn

MockLLM không phải model sản xuất (chỉ mô phỏng latency `unavailable` và tính token cố định theo seed). Các con số chi phí là chi phí mô phỏng bằng VND dựa trên cấu hình giá trong repo, không phản ánh hóa đơn API thực tế. Mọi số liệu được lấy nguyên bản từ kết quả chạy benchmark tự động tại `src/reports/benchmark.json`.
