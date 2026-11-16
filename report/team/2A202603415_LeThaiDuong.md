# Báo cáo cá nhân — Lê Thái Dương

## 1. Thông tin thành viên

- Họ tên: Lê Thái Dương
- MSSV: 2A202603415
- Email: `[điền email]`
- GitHub: `[điền username hoặc link GitHub]`

## 2. Phần việc phụ trách

- Phụ trách triển khai CP2 cho ba shape `workflow`, `single` và `orchestrator`.
- Hỗ trợ các yêu cầu CP3 về idempotency, crash recovery và handoff an toàn.
- Kiểm tra kết quả bằng test student, test host, test handoff/trace và crash suite.

## 3. Đóng góp cụ thể

- Hoàn thiện luồng workflow: đọc claim/order qua read tool, tính quote bằng code và gọi host để xử lý refund.
- Hoàn thiện single-agent ReAct với giới hạn tối đa 8 bước; model chỉ được dùng cho các bước đọc/ra quyết định, không được ghi refund.
- Hoàn thiện orchestrator và handoff với các tool chỉ đọc; không chuyển secret hoặc dữ liệu ngoài allowlist sang investigator.
- Bảo đảm mỗi shape gọi `finish()` để trả `RunResult` và ghi trace đúng contract.
- Chuyển tiếp `crash_at` tới `durability.issue_refund` và để `InjectedCrash` được propagate để kiểm tra resume/idempotency.
- Commit chính: `[điền commit hash sau khi commit]`.
- Test đã thêm hoặc sửa: `[điền tên test/commit test của cá nhân]`.

## 4. Bằng chứng

- CP2/student matrix: `248 passed`.
- Host test: `54 passed, 248 deselected`.
- T11/T12 retry và crash: `8 passed`.
- Handoff và trace contract: `9 passed`.
- Crash suite: `crash_safety = 20/20` trong `src/reports/crash.json`.
- Run ID benchmark: `[điền sau khi chạy benchmark]`.

## 5. Công cụ AI đã dùng

- Dùng Codex/ChatGPT để đọc contract, gợi ý cấu trúc triển khai và rà soát các nhánh xử lý.
- Tự kiểm tra kết quả bằng cách đọc source/test, chạy pytest, chạy handoff/trace tests và chạy crash suite.
- Không dùng AI để bịa số liệu; các số liệu trong báo cáo lấy từ output test thực tế.

## 6. Tự đánh giá

Đã hoàn thành phần triển khai ba shape cho CP2 và hỗ trợ các yêu cầu CP3. Các shape hiện trả đúng `RunResult`, tôn trọng ranh giới host/model, không ghi secret vào trace và vượt qua các kiểm tra retry/crash đã chạy. Phần còn cần hoàn thiện là cập nhật commit hash, run ID benchmark và thông tin liên hệ trước khi nộp.
