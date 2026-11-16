# Báo cáo cá nhân — 2A202603574_MaiTuanAnh

## 1. Thông tin thành viên

- Họ tên: Mai Tuấn Anh
- MSSV: 2A202603574
- Email: maituananh1511@gmail.com
- GitHub: https://github.com/AnhMT2k4

## 2. Phần việc phụ trách

- **Shape A (`workflow.py`):** Triển khai toàn bộ kiến trúc deterministic workflow xử lý khiếu nại (claims) bồi thường và hoàn phí vận chuyển của LogiX-VN. Đảm bảo toàn bộ logic tính tiền, kiểm tra quyền hạn, duyệt approval và ghi sổ tuân thủ nghiêm ngặt ranh giới Code vs Model.
- **Kiểm thử cho Shape A (`tests/test_workflow.py`):** Thiết kế và viết toàn bộ bộ test suite độc lập cho Shape A với 107 test cases, kiểm chứng toàn diện từ các luồng nghiệp vụ cơ bản, trường hợp biên, tính bền vững khi crash/retry, cho đến ranh giới an toàn thông tin (chống rò rỉ secret/PII) và hợp đồng trace v1.

## 3. Đóng góp cụ thể

1. **Cài đặt Shape A ([src/lab8/shapes/workflow.py](../../src/lab8/shapes/workflow.py)):**
   - Đọc dữ liệu claim an toàn qua `get_claim_view(conn, claim_id)` (chỉ lấy các trường hợp lệ, loại trừ hoàn toàn `parent_secret` và headers).
   - Kiểm tra mã đơn: Nếu thiếu `order_id` → trả về `status="needs_info"`, `proposal_amount=0`, tuyệt đối không ghi sổ.
   - Xác thực đơn hàng và quyền sở hữu: Gọi `lookup_order(conn, order_id, principal_id)`, nếu đơn không tồn tại hoặc sai chủ sở hữu (`principal_id`) → phân nhánh `status="escalated"`, `proposal_amount=0`.
   - Tính toán bồi thường: Sử dụng hàm nghiệp vụ `compute_compensation(conn, order)`, đảm bảo tiền bạc do code quyết định, bỏ qua mọi số ngày trễ ghi trong ticket (khác với điểm yếu của Swarm).
   - Phân nhánh từ chối khi quote ≤ 0: Trả về `status="denied"`, `proposal_amount=0` và không gọi host ghi sổ.
   - Giao tiếp an toàn với Host Gate: Khi quote > 0, truyền **Quote đầy đủ** vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` để host tự trừ các khoản hoàn tiền trước đó của đơn (đúng quy tắc trần theo đơn T13, T14).
   - Độ bền (Durability) khi crash: Bắt ngoại lệ `InjectedCrash` chỉ để kịp ghi xả trace (`trace.write()`) rồi re-raise để phục vụ kiểm thử khôi phục sau crash.
   - Đóng gói kết quả đầu ra: Trả về qua `lab8.shapes.common.finish()`.
   - Quản lý tài nguyên: Luôn đóng kết nối SQLite an toàn trong khối `try...finally: conn.close()`.

2. **Xây dựng bộ test toàn diện ([src/tests/test_workflow.py](../../src/tests/test_workflow.py)):**
   - Đóng góp 107 unit & integration tests chia thành 18 test classes.
   - Phủ kín ma trận T01–T10, T13, T14 trên 5 seeds (`11, 22, 33, 44, 55`).
   - Kiểm thử Idempotency (T11): Chạy lại nhiều lần cùng claim không tạo thêm dòng ledger (`refund:{claim_id}`).
   - Kiểm thử Crash Durability (T12): Kiểm chứng `InjectedCrash` được re-raise chính xác và resume không double-pay.
   - Kiểm thử rò rỉ thông tin: Quét không lộ `CANARY_SECRET_*`, SĐT, địa chỉ, ghi chú nội bộ, tên hàng hóa.
   - Kiểm thử Trace Contract v1: Đảm bảo trace tồn tại, ghi trong chính lần chạy đó, khớp `run_id` và có danh sách sự kiện hợp lệ.

3. **Commit chính:**
   - Commit `9b0cbed`: Cài đặt hoàn thiện `workflow.py`.
   - Commit `38c08ef`: Thêm bộ test `src/tests/test_workflow.py`.

## 4. Bằng chứng

- **Lịch sử Git:**
  - Commit `9b0cbed`: *Workflow* (triển khai mã nguồn `src/lab8/shapes/workflow.py`).
  - Commit `38c08ef`: *Test Workflow* (bổ sung `src/tests/test_workflow.py`).
- **Kết quả chạy test:**
  - `python -m pytest tests/test_workflow.py`: **107 passed / 107 tests** (thời gian chạy: 10.71s).
  - `python -m pytest -q -m student -o addopts= -k workflow`: **62 passed / 62 tests student matrix**.
  - `python -m pytest -q` (Cổng host): **161 passed, 0 failed** (54 test host gốc + 107 test workflow mới).
  - `python -m lab8.check_submission`: `[ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant.
- **Mục đích:**
  - Hỗ trợ rà soát các nhánh rẽ và trường hợp biên (edge cases) theo đặc tả [business_rules.md](../../docs/business_rules.md) và [contracts.md](../../docs/contracts.md).
  - Hỗ trợ cấu trúc các test cases trong `pytest` theo tiêu chuẩn kiểm thử sạch và kiểm tra chéo với `trial_pass` của grader.
- **Cách tự kiểm tra kết quả:**
  - Chạy thực tế toàn bộ các lệnh kiểm thử trên môi trường nội bộ qua terminal (Powershell).
  - Tự kiểm tra các file trace JSON sinh ra trong `traces/` để xác nhận không có bất kỳ chuỗi cấm nào bị rò rỉ.
  - Kiểm tra trực tiếp bảng SQLite `refund_ledger` và `audit_events` để xác nhận tính nhất quán và nguyên tử của giao dịch.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 10/10 (Hoàn thành vượt mong đợi).
- **Đánh giá chi tiết:**
  - Shape A (`workflow`) hoạt động chính xác 100% trên toàn bộ các claim và seed, đạt pass rate 1.0 tuyệt đối.
  - Không vi phạm bất kỳ điều kiện must-pass nào: `approval_bypass_count = 0`, `secret_leak_count = 0`, crash an toàn tuyệt đối.
  - Bộ test được viết bài bản, cấu trúc rõ ràng, đóng góp đáng kể vào chất lượng mã nguồn chung của nhóm.
