# Báo cáo cá nhân — Haidoan2426

> Đổi tên file thành `MSSV_HoTen.md` trước khi nộp và thay các trường còn để trống.

## 1. Thông tin thành viên

- Họ tên: Hai Doan
- MSSV: 2A202603739
- Email: 26ai.haidc@vinuni.edu.vn
- GitHub: rawser246

## 2. Phần việc phụ trách

- Phụ trách Shape A — `workflow` trong `src/lab8/shapes/workflow.py`.
- Xây dựng quy trình xử lý claim hoàn phí theo các bước cố định: đọc claim, kiểm tra order, tính compensation bằng code, gọi host durability và tạo kết quả/trace.
- Đảm bảo shape không tự quyết số tiền hoàn, không ghi trực tiếp vào database và hỗ trợ `crash_at`/idempotency theo contract.

## 3. Đóng góp cụ thể

- Hoàn thiện hàm `run_claim` và luồng xử lý workflow.
- Bổ sung `src/tests/test_workflow.py` với 7 test tập trung cho các nhánh không hoàn tiền, refund thành công, approval, crash/retry và trace bảo mật.
- Xử lý các nhánh `unknown_claim`, `missing_order_id`, order không hiển thị, quote bằng 0, refund bị từ chối/xung đột và refund thành công.
- Tính quote từ dữ liệu order bằng `compute_compensation`, truyền proposal đầy đủ cho `issue_refund`.
- Ghi trace cho các đường chạy, bao gồm cả trường hợp crash; giữ nguyên ranh giới bảo mật bằng các view/tool được phép.
- Commit chính: `bc5b2c3` — `Hoan thanh shape A`.

## 4. Bằng chứng

- File triển khai: `src/lab8/shapes/workflow.py`.
- Commit: `bc5b2c3`.
- Contract tham chiếu: `docs/contracts.md`, `docs/business_rules.md`.
- Có thể kiểm tra bằng cổng host: `cd src; python -m pytest -q`.
- Kiểm thử phần cá nhân: `cd src; python -m pytest -q tests/test_workflow.py` → `7 passed`.

## 5. Công cụ AI đã dùng

- Dùng trợ lý AI để đọc yêu cầu, rà soát contract và hỗ trợ kiểm tra các nhánh xử lý.
- Tự kiểm tra kết quả bằng cách đọc lại diff, đối chiếu với docstring/contract, chạy test và kiểm tra trace không chứa secret hoặc dữ liệu ngoài allowlist.

## 6. Tự đánh giá

Đã hoàn thành phần workflow theo đúng ranh giới host: code quyết định quy tắc nghiệp vụ và host mới được phép ghi refund. Đã bổ sung test riêng cho các đường chạy quan trọng. Phần cần hoàn thiện trước khi nộp là cập nhật dòng đóng góp tương ứng trong `TEAM.md`.
