# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 1f4bca2
- Run id dẫn chứng: R-workflow-C-001-s11 (70 trial workflow trong src/reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 28.87 (2021.00 VND / 70 trial pass)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

## Vì sao shape này

Trên cùng tập 14 claim public × 5 seed (`11, 22, 33, 44, 55`, tổng 70 trial mỗi shape, bảng giá mô phỏng cố định trong `src/reports/benchmark.json`), `workflow` đạt `pass_rate = 1.000` (70/70), `pass^5 = 1.000`, `seed_variance = 0.000000`, đồng thời có `cost_per_success_vnd` thấp nhất (`28.87` VND) và số bước trung bình ít nhất (`2.79` steps, p95 `3` steps). Quy trình xử lý claim hoàn phí của LogiX-VN đã được chuẩn hóa rõ theo trạng thái đơn, điều kiện trễ/hư hỏng và cổng kiểm duyệt của host, nên chọn kiến trúc ít tự chủ nhất (`workflow`) vừa loại bỏ hoàn toàn rủi ro dao động giữa các seed, vừa tiết kiệm chi phí nhất mà vẫn xử lý trọn vẹn mọi bẫy nghiệp vụ.

## Có đáng đổi lấy multi-agent không

Không đáng đổi trong bài toán này. So với `workflow`, `single` có cùng `pass_rate = 1.000` nhưng tốn `6.21` bước trung bình (`29.13` VND/success); `orchestrator` đạt `1.000` nhưng chi phí mô phỏng tăng gần gấp đôi (`57.04` VND/success, `5.57` tool call trung bình); còn `swarm` vừa đắt hơn (`49.57` VND/success) vừa rớt ở seed `55` (`pass_rate = 0.986`, `pass^5 = 0.929`, `seed_variance = 0.000816`) do tin số ngày ghi trong ticket ở T02. Quyết định chỉ nên đảo sang `single` hoặc `orchestrator` khi yêu cầu mở rộng sang quy trình tra cứu động nhiều nguồn dữ liệu chưa cố định trước thứ tự công cụ, khiến luồng Python tuần tự không còn bao phủ hết nhánh điều kiện hợp lệ với ngưỡng `pass_rate >= 0.75`.

## Trace và bằng chứng

Trace của `workflow` chỉ ghi các sự kiện có cấu trúc đã lọc: `lookup_order` (chỉ gồm các field vận hành an toàn của đơn hàng, bỏ SĐT, địa chỉ, tên hàng, ghi chú nội bộ), `quote` (số tiền và mã điều khoản), `decision` (trạng thái và lý do chuẩn hóa), và `crash` (tên điểm crash khi có `InjectedCrash`, được lưu ra đĩa trước khi ném lỗi). Nhóm cố ý không ghi toàn bộ dòng claim, `parent_secret`, `raw_headers` và nội dung `ticket` tự do vào trace hay stdout để tránh lộ thông tin cá nhân hoặc chuỗi canary. Mọi file nhật ký đều ghi đúng định dạng `trace.v1` tại `traces/<run_id>.json` và đóng gói qua hàm tổng hợp chuẩn của hệ thống; nếu đặt trace ngoài phạm vi quét tự động của scanner, hệ thống phải thất bại đóng (`fail-closed`: báo thiếu/lỗi trace thay vì tự suy đoán là an toàn).

## Giới hạn

MockLLM là bộ sinh văn bản giả lập cố định theo seed, không phải mô hình ngôn ngữ thực tế ngoài sản xuất; giá token là chi phí mô phỏng theo `config/pricing.yaml` và độ trễ `latency` để là `unavailable`. Số liệu `1.000` hiện đo trên 14 claim public đã biết nhãn; hiệu quả thực chất trên dữ liệu chưa thấy nhãn phụ thuộc kết quả chấm 40 claim × 5 seed trên bộ hidden của giảng viên và nhóm tuyệt đối không sửa tay file JSON trong `src/reports/`.
