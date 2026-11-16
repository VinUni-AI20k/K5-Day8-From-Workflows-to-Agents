# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: Chưa chốt; cần commit mã nguồn và test rồi điền hash thật trước khi nộp.
- Run id dẫn chứng: R-workflow-C-001-s11; R-workflow-C-002-s55; R-workflow-C-014-s55 (src/reports/workflow_baseline.json).
- Pass rate / pass^5 / seed min-max / variance: 1.0 / 1.0 / 1.0–1.0 / 0.0 trên public 14 claim × 5 seed.
- Cost per success (mô phỏng, VND): 27.857142857142858 (src/reports/workflow_baseline.json).
- Crash safety: 20/20 cho suite host/swarm (src/reports/crash.json); workflow được kiểm riêng ở cả 3 điểm crash trong tests/test_workflow.py và T12 của ma trận student.
- Secret leak / approval bypass: Các trial workflow public đều pass kiểm tra trace, chuỗi cấm và ledger; test approval sai/thiếu/hết hạn đều không ghi refund. Chưa có số đếm chính thức từ hidden grader.

**Trạng thái: bản nháp của người phụ trách workflow.** Mới so workflow với swarm trên cùng corpus và seed. Single và orchestrator chưa được triển khai; nhóm phải chạy benchmark đủ 4 shape, cập nhật bằng chứng và thống nhất lại lựa chọn trước khi nộp. `workflow_baseline.json` không thay thế `benchmark.json` bắt buộc.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Tạm chọn workflow làm baseline vì bài toán hiện tại có luật rõ ràng và tiền phải do code quyết định. Trên cùng 14 claim public, seed `11,22,33,44,55`, workflow đúng 70/70 trial, pass^5 = 1.0 và variance = 0. Swarm đúng 69/70 trial, pass^5 = 0.9285714285714286, variance = 0.0008163265306122443 và cost/success = 49.56695652173913 VND mô phỏng, so với 27.857142857142858 của workflow. Sai lệch của swarm nằm ở C-002 seed 55: tin số ngày trong ticket thay vì order. Đây là bằng chứng public cho baseline, chưa phải kết luận workflow thắng cả bốn kiến trúc hay qua hidden.

## Có đáng đổi lấy multi-agent không

Với dữ liệu đã đo, swarm chưa đem lại lợi ích về độ đúng để bù chi phí mô phỏng cao hơn. Chỉ đổi lựa chọn khi benchmark đầy đủ cho thấy single/orchestrator có lợi ích đo được, hoặc yêu cầu thực tế có phần xử lý thông tin mơ hồ hay công việc độc lập mà workflow hiện tại không đáp ứng. Giữ cố định corpus, seed, model, tool, giá và evaluator khi so sánh. Chưa suy ra lợi ích về latency vì MockLLM không đo latency.

## Trace và bằng chứng

Workflow ghi các event `claim` (chỉ claim_id và found), `lookup_order` (view đã lọc field), `quote`, `refund` (ok, reason, conflict) và `decision`. Mọi nhánh trả kết quả dùng `finish()` để ghi JSON mới có run_id đúng và lấy effect/audit từ ledger. Không ghi ticket, principal_id, parent_secret, header, SĐT, địa chỉ, ghi chú nội bộ hoặc tên hàng; không in ra stdout. Không tạo debug dump ngoài trace. File trace ở `traces/<run_id>.json`, thuộc phạm vi scanner. Test `test_untrusted_ticket_is_never_copied_to_trace_or_stdout` chèn chuỗi nhạy cảm vào ticket và kiểm tra cả artifact lẫn stdout/stderr.

## Giới hạn

MockLLM không phải model sản xuất. Workflow hiện tại không gọi model; chi phí được tính từ các read tool qua `dispatch`, theo cùng cách tính tool của host/swarm. Latency là `unavailable`; số event trace phụ thuộc mức ghi log nên không đại diện trực tiếp cho thời gian xử lý. Public chỉ có 14 claim, không chứng minh đạt ngưỡng hidden 0.75. Suite crash 20/20 chủ yếu kiểm host và swarm; bằng chứng crash workflow là test riêng và T12. Chưa có benchmark đủ bốn shape hoặc commit chốt. Các file JSON report được sinh bằng công cụ, không chỉnh tay.
