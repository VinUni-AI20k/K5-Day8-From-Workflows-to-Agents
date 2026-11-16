# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Hồ Quốc Toản
- MSSV:2A202603668
- Email:26ai.toanhq@vinuni.edu.vn
- GitHub:https://github.com/ToyzZone/K5-L3A-DAY08-VinSpace-FromWorkflowsToAgents.git

## 2. Phần việc phụ trách

Shape, module hoặc phần báo cáo bạn phụ trách.
- hoàn thành file workflow.py, và thêm file test_workflow.py
...

## 3. Đóng góp cụ thể

**Commit chính (hash):** [Bổ sung hash commit chứa workflow và test]

**Phần việc thực hiện:**
- Hoàn thiện `src/lab8/shapes/workflow.py`: đọc claim, tra đơn hàng, tính khoản hoàn, gọi host xử lý giao dịch và trả về `RunResult`.
- Thêm `src/tests/test_workflow.py` với 43 trường hợp kiểm thử về luật nghiệp vụ, approval, chống hoàn trùng, bảo mật, xung đột số tiền và 20 tình huống crash/resume.
- Kết quả kiểm tra: 43/43 test mới đạt; bộ test mặc định đạt 97 test, không có lỗi.

**Quyết định kỹ thuật:**
- Dùng quy trình Python cố định, không gọi model vì các bước nghiệp vụ đã có quy tắc rõ ràng.
- Tính khoản hoàn từ dữ liệu đơn hàng và policy chính thức; không tin các chỉ dẫn hoặc số liệu trong ticket.
- Truyền quote đầy đủ vào `durability.issue_refund`, để host kiểm approval, trần hoàn tiền và chống ghi trùng.
- Dùng `finish()` để lấy kết quả từ ledger thực tế; chỉ ghi dữ liệu cần thiết, an toàn vào trace.
- Truyền `crash_at` xuống host và để `InjectedCrash` truyền ra ngoài, giúp kiểm chứng việc chạy lại không tạo refund trùng.
- Dùng database và thư mục tạm cho test, không sửa dữ liệu đề bài.

Phần triển khai và kiểm thử có sự hỗ trợ của ChatGPT/Codex.

...

## 4. Bằng chứng

**Link commit:** [Bổ sung link commit thực tế trên GitHub]

**File triển khai:** `src/lab8/shapes/workflow.py`  
**File kiểm thử:** `src/tests/test_workflow.py`

Các test tiêu biểu:
- `test_public_business_rules_and_result_contract`: kiểm tra luật nghiệp vụ, kết quả, ledger và trace.
- `test_invalid_approval_never_refunds_and_writes_denial`: approval không hợp lệ không tạo refund và có audit từ chối.
- `test_retry_with_different_seeds_still_has_one_refund`: chạy lại với nhiều seed vẫn chỉ một refund.
- `test_crash_resume_keeps_one_refund_and_one_audit`: 20 tình huống crash/resume không gây hoàn trùng.
- `test_untrusted_ticket_cannot_instruct_workflow_or_leak_data`: không làm theo lệnh trong ticket và không lộ dữ liệu nhạy cảm.

**Kết quả chạy thực tế trên Windows, Python 3.11.9:**

```text
Kiểm thử riêng tests/test_workflow.py:
43 passed in 9.29s

Bộ kiểm thử mặc định:
97 passed, 248 deselected in 21.85s
```

248 test bị loại khỏi lần chạy mặc định theo cấu hình marker của đề, không phải test thất bại. Các bằng chứng này chưa bao gồm kết quả bộ hidden hoặc báo cáo crash chính thức.

...

## 5. Công cụ AI đã dùng

**Công cụ:** ChatGPT/Codex.

**Mục đích sử dụng:** Giải thích yêu cầu và luồng xử lý workflow; hỗ trợ viết `workflow.py` kèm chú thích đầu vào, đầu ra; sửa lỗi dán trùng import và hàm; tạo file `tests/test_workflow.py`.

**Cách kiểm chứng:** Các lệnh kiểm thử được Codex chạy trực tiếp trên môi trường Python 3.11.9 của dự án:
- Test riêng workflow mới thêm: **43/43 đạt**.
- Bộ test mặc định: **97 đạt, 248 deselected**, không có lỗi.

Code được đối chiếu với luật nghiệp vụ và contract: truyền quote đầy đủ cho host, không tự ghi ledger, không dùng chỉ dẫn trong ticket để quyết định hoàn tiền và không ghi dữ liệu nhạy cảm vào trace. Kết quả test được lấy từ lần chạy thực tế; chưa có bằng chứng đạt bộ hidden.

Tôi cần tự đọc hiểu và giải thích được các quyết định trong phần code có AI hỗ trợ trước khi nộp bài.

...

## 6. Tự đánh giá

Phần workflow tôi phụ trách đã được triển khai và kiểm chứng bằng 43 test mới; bộ test mặc định đạt 97 test, không có lỗi. Kết quả cho thấy workflow xử lý đúng các tình huống đã kiểm tra về hoàn phí, approval, chống hoàn trùng, bảo mật và phục hồi sau crash.

Qua quá trình làm bài, tôi hiểu rõ hơn vai trò của workflow: tổ chức các bước cố định, dùng dữ liệu chính thức để tính khoản hoàn và để host kiểm soát việc ghi tiền. Tôi cũng nhận thấy kết quả chạy test là bằng chứng cần thiết, nhưng chưa đủ để khẳng định đạt bộ hidden hoặc kết luận workflow tốt hơn các kiến trúc khác.

Tôi còn cần củng cố khả năng tự viết code và giải thích từng nhánh xử lý vì phần triển khai có AI hỗ trợ. Trước khi nộp, tôi sẽ đọc lại code, hoàn thiện bằng chứng commit và phối hợp với nhóm đối chiếu kết quả benchmark để đưa ra quyết định kiến trúc.
