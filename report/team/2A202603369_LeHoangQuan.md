# Báo cáo cá nhân — Lê Hoàng Quân

## 1. Thông tin thành viên

- Họ tên: Lê Hoàng Quân
- MSSV: 2A202603369
- Lớp: L3A
- GitHub: `lehoangquanvcb`

## 2. Phần việc phụ trách

Triển khai Shape A — Deterministic Workflow cho quy trình xử lý yêu cầu hoàn tiền của LogiX-VN theo [Issue #2](https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents/issues/2).

## 3. Đóng góp cụ thể

- Triển khai `run_claim` trong `src/lab8/shapes/workflow.py`. Workflow đọc claim qua `get_claim_view`, trả `needs_info` khi thiếu mã đơn và trả `escalated` khi đơn không tìm thấy hoặc nằm ngoài quyền truy cập.
- Dùng `compute_compensation` để tính số tiền đề xuất từ dữ liệu đơn hàng và chính sách hiện hành. Các bước xử lý theo quy tắc Python cố định. Số ngày trễ ghi trong ticket không ảnh hưởng đến quyết định.
- Chuyển toàn bộ số tiền đề xuất cho `issue_refund` để host kiểm tra phê duyệt, áp trần hoàn tiền theo đơn và xử lý yêu cầu chạy lại. Tham số `crash_at` được chuyển tiếp để kiểm thử khôi phục sau sự cố.
- Dùng `finish()` để ghi trace cho mọi nhánh trả kết quả, gồm cả các nhánh trả sớm. Trace ghi trạng thái, số tiền đề xuất và mã lý do.
- Thêm test cho mã claim không tồn tại. Test xác nhận trạng thái `failed`, lý do `unknown_claim`, số tiền đề xuất bằng 0, số dòng ledger giữ nguyên và `run_id` trong trace khớp với kết quả.

## 4. Bằng chứng

- Commit kỹ thuật [`4e5c355` — Implement deterministic workflow and test unknown claim](https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents/commit/4e5c355).
- Test bổ sung `src/tests/test_workflow.py::test_workflow_unknown_claim_returns_failed_without_refund`.
- Ma trận public riêng cho Workflow ghi nhận `62 passed, 240 deselected in 5.90s`.
- Bộ pytest mặc định ghi nhận `54 passed, 248 deselected in 6.10s`.

## 5. Công cụ AI đã dùng

Tôi dùng ChatGPT để được hướng dẫn triển khai `run_claim` theo hợp đồng của repo và xây dựng test cho mã claim không tồn tại. Tôi kiểm tra lại trên máy bằng pytest, gồm ma trận public của Workflow và bộ test mặc định.

## 6. Tự đánh giá

Qua ca T14, tôi hiểu rõ hơn sự khác nhau giữa số tiền workflow đề xuất và số tiền host thực ghi vào ledger. Workflow gửi đủ 150.000 đồng. Host tính phần chênh so với 30.000 đồng đã hoàn trước đó và ghi thêm 120.000 đồng. Việc xử lý phần chênh ở host giúp các kiến trúc áp dụng cùng một quy tắc khi một đơn có nhiều claim. Kết quả tôi ghi nhận là từ bộ public. Kết quả hidden do grader của giảng viên xác định.
