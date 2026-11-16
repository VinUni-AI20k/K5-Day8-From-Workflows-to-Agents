# Báo cáo cá nhân — 2A202603397_VoHuyHoang

## 1. Thông tin thành viên

- Họ tên: Võ Huy Hoàng
- MSSV: 2A202603397
- Email: 26ai.hoangvh4@vinuni.edu.vn
- GitHub: https://github.com/ferr2764

## 2. Phần việc phụ trách

CP2: Test các shape đã viết

Vai trò D — Test/Host, phụ trách kiểm thử workflow, single và orchestrator; bổ sung test. Kiểm thử crash/resume bổ sung phục vụ CP3–CP4.

## 3. Đóng góp cụ thể

- Bổ sung `src/tests/test_durability_shapes.py`, test `test_resume_other_crash_windows_keeps_one_refund`.
- Tham số hóa ba shape và hai điểm crash `before_effect`, `after_checkpoint`, tạo thành 6 ca kiểm thử. Đây là hai cửa sổ crash bổ sung cho T12 có sẵn (`after_effect_before_checkpoint`).
- Kiểm tra `InjectedCrash` thực sự xảy ra, cùng trạng thái ledger, audit và checkpoint ngay sau crash.
- Resume rồi retry trên cùng database; kiểm tra kết quả qua `trial_pass`, đúng một refund, một audit `refund_committed` và có checkpoint sau phục hồi.
- Sử dụng fixture `public_db` và marker `student`; không sửa host, policy, metric hoặc dữ liệu chuẩn.
- Commit chính: chưa tạo; bổ sung hash sau khi commit.

## 4. Bằng chứng

File test: [test_durability_shapes.py](../../src/tests/test_durability_shapes.py).

Lệnh chạy từ thư mục `src/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_durability_shapes.py -p no:cacheprovider
```

Kết quả xác minh: **6 passed in 0.27s**. 
![Test Durability](test_durability.png)

Kết quả này chỉ xác nhận sáu ca test bổ sung, không thay thế toàn bộ bộ student, crash suite 20/20 hoặc benchmark.

## 5. Công cụ AI đã dùng

Sử dụng Codex để đọc hướng dẫn lab và test có sẵn, phân tích lỗi pytest, bổ sung test crash/resume và soạn báo cáo. Codex chạy test mới và ghi nhận sáu ca pass.

Cần tự đọc lại assertion, chạy lại lệnh trên bằng môi trường cá nhân và bổ sung kết quả tự xác minh trước khi nộp. Không dùng AI để sửa file thước đo hoặc sửa tay report JSON.

## 6. Tự đánh giá

Đã có test bổ sung cho hai cửa sổ crash trên ba shape, kiểm tra dữ liệu cả trước và sau phục hồi. Cần nắm rõ vì sao checkpoint không thay thế ledger và retry không được tạo thêm refund hoặc audit hoàn tiền.

Việc tiếp theo: tự xác minh test, ghi commit đóng góp, chạy crash suite 20/20, benchmark bốn shape với năm seed và `lab8.check_submission`. Các bước này chưa được ghi nhận là hoàn thành trong báo cáo hiện tại.
