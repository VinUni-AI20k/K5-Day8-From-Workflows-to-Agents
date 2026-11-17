# Báo cáo cá nhân — 2A202603768_NguyenQuangHuy

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quang Huy
- MSSV: 2A202603768
- Email: 26ai.huynq13@vinuni.edu.vn
- GitHub: https://github.com/nguyenquanghuy091204

## 2. Phần việc phụ trách

- **Thực hiện Shape B (`single`)**: Viết agent ReAct trong file `src/lab8/shapes/single.py` đáp ứng tiêu chí CP2 (ReAct bounded, phân định ranh giới code/model) và CP3 (idempotency, xử lý crash).
- **Kiểm thử kỹ thuật**: Xây dựng mới test suite `src/tests/test_single.py` (8 test unit) kiểm tra toàn diện các tình huống biên, trần theo đơn, an toàn secret và phục hồi sau sự cố.

## 3. Đóng góp cụ thể

- **Commit chính**: `cabceb8`
- **Test đã thêm mới**: `src/tests/test_single.py`
- **Các quyết định kỹ thuật chính**:
  1. *Ranh giới Code vs Model (Least Autonomy)*: Thiết lập vòng ReAct (`run_react`) với chặn trần 8 bước (`max_steps=8`) và `worker=True`. Hàm `decide` chỉ được gọi tool đọc (`lookup_order`, `compute_compensation`) và dừng dứt khoát ở bước 3, không bao giờ chạm trần lỗi `step_cap`. Host là bên duy nhất có quyền ghi database.
  2. *Chống ảo giác & Injection*: Tiền bồi thường do code tính (`compute_compensation`), hoàn toàn bỏ qua số ngày trễ ghi trong ticket (vượt qua T02 khai khống và T09 prompt injection).
  3. *Trần hoàn tiền theo đơn (Per-order cap)*: Truyền **quote đầy đủ** vào `durability.issue_refund`, để host tự đối soát và trừ tiền đã hoàn trong transaction (đáp ứng đúng T13, T14).
  4. *Xử lý Crash & Idempotency (CP3)*: Truyền đối số `crash_at` vào `durability.issue_refund`. Bắt ngoại lệ `InjectedCrash` để kịp xả log (`trace.write()`) rồi **re-raise ngoại lệ ra ngoài** cho harness kiểm tra. Khóa `refund:{claim_id}` đảm bảo khi retry (T11) hoặc resume sau crash (T12) chỉ tạo đúng 1 dòng ledger và 1 audit event.
  5. *Trace Contract v1 & An toàn dữ liệu*: Ghi trace bằng `_Trace` tại mọi nhánh return (`finish()`). Loại bỏ toàn bộ `parent_secret`, headers và PII (SĐT, địa chỉ, tên hàng) khỏi trace và console.

## 4. Bằng chứng

- **Test ma trận student của bài lab**:
  - Lệnh: `python -m pytest -q -m student -o addopts= -k single`
  - Kết quả: **`62 passed, 248 deselected in 4.01s`** (đạt 100% trên 5 seed public).
- **Test suite kỹ thuật cá nhân (`test_single.py`)**:
  - Lệnh: `python -m pytest -v tests/test_single.py`
  - Kết quả: **`8 passed in 0.43s`**

## 5. Công cụ AI đã dùng

- **Công cụ**: Antigravity.
- **Mục đích**: 
  - Hỗ trợ thiết kế cấu trúc luồng trạng thái cho hàm `decide` trong `run_react` để phân rã 3 bước logic hợp lý.
  - Tư vấn cơ chế bắt và re-raise `InjectedCrash` đảm bảo trace vẫn được ghi ra đĩa trước khi dừng tiến trình.
- **Cách tự kiểm tra**:
  - Chạy `pytest` trên môi trường ảo `.venv` để đối chiếu kết quả thực tế với nhãn kỳ vọng.
  - Quét thủ công file JSON trong `traces/` để chắc chắn không chứa chuỗi `CANARY_SECRET_*` hay thông tin PII.

## 6. Tự đánh giá

- **Kết quả**: Đạt mục tiêu của CP2 và CP3 đối với Shape B.
- **Chất lượng**: Code clean, không lỗi exception, đáp ứng đầy đủ 3 điều kiện must-pass (không bypass approval, không rò rỉ secret).