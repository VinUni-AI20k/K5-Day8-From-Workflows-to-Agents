# Decision record

- Shape chọn: workflow
- Commit hash: 7d7506e
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1,0000 / 1,0000 / 1,0000–1,0000 / 0,000000 (public, 70/70 lượt)
- Cost per success (mô phỏng, VND): 34,29 (public)
- Crash safety: 20/20 ở crash suite của host và swarm. Workflow đạt T11 và T12 trong ma trận public.
- Secret leak / approval bypass: Không phát hiện vi phạm trong các ca public được kiểm. Hidden chạy local đạt 200/200 theo nhãn. Bộ đếm chính thức do grader của giảng viên xác nhận.

Số liệu public lấy từ [benchmark.json](../../src/reports/benchmark.json) và [crash.json](../../src/reports/crash.json).

## Vì sao shape này

Nhóm chọn `workflow` vì xét hoàn phí dựa vào dữ kiện có cấu trúc và policy hiện hành. Trên cùng 14 claim public và năm seed `11,22,33,44,55`, `workflow`, `single` và `orchestrator` đều đạt 70/70. `workflow` dùng luồng Python cố định và có chi phí thấp nhất ở mức 34,29 VND mỗi lượt đạt, so với 35,42 của `single`, 43,57 của `orchestrator` và 49,57 của `swarm`. `swarm` đạt 69/70 và có phương sai theo seed là 0,000816.

Kiểm tra hidden local trên 40 claim × 5 seed bằng `lab8.benchmark --labels` cho kết quả `workflow`, `single` và `orchestrator` đều đạt 200/200, còn `swarm` đạt 194/200. Chi phí mô phỏng của `workflow` trên lần kiểm tra này là 35,25 VND mỗi lượt đạt.

## Có đáng đổi lấy multi-agent không

Nhóm giữ `workflow` với tập claim đã đo. Nhóm sẽ cân nhắc kiến trúc khác nếu thử nghiệm lặp lại cho thấy nó xử lý đúng thêm các claim mà workflow bỏ sót, đáp ứng các cổng an toàn và mức tăng tỷ lệ thành công đáng với chi phí cùng độ dao động tăng thêm.

## Trace và bằng chứng

Trace workflow ghi `claim_lookup`, `order_lookup`, `quote`, `refund_request`, `refund_outcome` và `decision` tùy nhánh. Các event chứa trạng thái đọc, khoản đề xuất và kết quả host. Ticket, hàng dữ liệu thô, header, secret và PII nằm ngoài payload để tránh sao chép dữ liệu nhạy cảm vào log.

`common.finish()` trả đường dẫn trace mới của trial với `run_id` khớp kết quả. Khi thử crash, workflow ghi trace trước khi gọi host. Bằng chứng bảo mật phải nằm trong trace hoặc file cùng thư mục có tiền tố `run_id` để scanner đọc được. Với log ngoài phạm vi đó, cần thu thập và quét log cùng stdout, stderr trước khi kết luận.

## Giới hạn

Chi phí dùng bảng giá mô phỏng. Lab chạy với MockLLM và latency là `unavailable`. Kết quả hidden local đối chiếu với nhãn qua benchmark. Grader riêng của giảng viên xác nhận điểm và các cổng chính thức.
