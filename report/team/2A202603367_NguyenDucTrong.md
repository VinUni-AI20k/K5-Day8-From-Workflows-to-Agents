# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên:
- MSSV:
- Email:
- GitHub:

## 2. Phần việc phụ trách

Shape, module hoặc phần báo cáo bạn phụ trách.

Phụ trách **Checkpoint 4 (CP4) – kiểm tra độ an toàn khi crash và các điều kiện bảo vệ refund** trong dự án LogiX-VN, thuộc Lab 8 – From Workflows to Agents.

Các nội dung công việc:
- Chạy crash-safety suite với 20 lần kiểm thử.
- Kiểm tra kết quả các tình huống crash/retry được ghi trong `reports/crash.json`.
- Kiểm tra các báo cáo trong thư mục `reports` để tìm dấu hiệu lộ chuỗi `CANARY_SECRET_`.
- Chạy lại bộ kiểm thử chung và bộ kiểm thử dành cho sinh viên để xác nhận các thay đổi không làm hỏng chức năng hiện có.
- Đối chiếu kết quả với yêu cầu CP4: không thực hiện refund khi thiếu/không hợp lệ approval, không để lộ secret trong trace hoặc kết quả, và không tạo refund trùng khi xảy ra crash/retry.

## 3. Đóng góp cụ thể

Commit chính (hash), test đã thêm hoặc sửa, quyết định kỹ thuật bạn đưa ra.

### 3.1. Kiểm thử crash-safety

Đã thực hiện lệnh:

```powershell
python -m lab8.crash_test --count 20 --out reports/crash.json
```

Kết quả:
- `crash_safety`: **20/20**
- `passed`: **20**
- `count`: **20**
- Các scenario từ `CR-01` đến `CR-20` đều có `passed: true`.
- Các nhóm tình huống trong kết quả bao gồm crash trước/sau effect, crash sau checkpoint, retry khi amount không khớp, retry không có approval và tình huống swarm crash sau effect nhưng trước checkpoint.

### 3.2. Kiểm thử hồi quy

Đã chạy hai bộ lệnh:

```powershell
python -m pytest -q
```

Kết quả: **61 passed, 248 deselected**.

```powershell
python -m pytest -q -m student -o addopts=
```

Kết quả: **248 passed, 61 deselected**.

Hai lệnh đều hoàn tất thành công.

### 3.3. Kiểm tra dấu hiệu lộ secret trong báo cáo

Đã tìm chuỗi `CANARY_SECRET_` trong các file thuộc thư mục `reports` bằng PowerShell:

```powershell
Get-ChildItem .\\reports -Recurse -File |
    Select-String -Pattern 'CANARY_SECRET_'
```

Không có kết quả khớp trong phạm vi thư mục `reports`.

### 3.4. Quyết định và lưu ý kỹ thuật

- Sử dụng crash test report làm bằng chứng định lượng cho yêu cầu chống tạo refund trùng khi tiến trình bị gián đoạn và retry.
- Giữ lại `reports/crash.json` để nhóm có thể kiểm tra lại từng scenario thay vì chỉ ghi nhận kết quả tổng hợp.
- Không tự kết luận rằng toàn bộ yêu cầu bảo mật đã được xác nhận chỉ từ kết quả crash test. Việc tìm chuỗi secret nêu trên mới giới hạn trong thư mục `reports`; cần rà soát thêm toàn bộ trace/stdout và bảo đảm không ghi raw claim row hoặc order row trước khi xác nhận hoàn tất toàn bộ phần kiểm tra bảo mật CP4.


## 4. Bằng chứng

Link commit, tên test, run id hoặc trích đoạn report liên quan.

| Bằng chứng | Kết quả / vị trí |
|---|---|
| Crash-safety report | `reports/crash.json` |
| Crash-safety suite | `crash_safety = 20/20` |
| Toàn bộ pytest | `61 passed, 248 deselected` |
| Student tests | `248 passed, 61 deselected` |
| Quét chuỗi secret trong reports | Không tìm thấy `CANARY_SECRET_` |
| Commit | Bổ sung hash/link commit sau khi push lên GitHub |

## 5. Công cụ AI đã dùng

Công cụ, dùng vào việc gì, và bạn đã tự kiểm tra kết quả thế nào (xem [RULES.md](../../RULES.md)).

- **ChatGPT:** Hỗ trợ phân tích yêu cầu CP4, giải thích các tình huống approval/refund và crash-retry, đề xuất lệnh kiểm thử và cách đọc kết quả.

## 6. Tự đánh giá

Đã hoàn thành phần chạy và xác nhận crash-safety suite với kết quả **20/20**, đồng thời hai bộ pytest đều chạy thành công. Báo cáo `reports/crash.json` đã được tạo và lưu làm bằng chứng cho các tình huống crash/retry.

Phần kiểm tra secret hiện mới thực hiện trên thư mục `reports`, chưa đủ cơ sở để khẳng định toàn bộ trace/stdout không chứa secret hoặc raw claim/order row. Trước khi chốt CP4, cần hoàn tất rà soát phạm vi này, kiểm tra các nhánh approval (bao gồm approval không hợp lệ, approval thuộc claim khác và claim đã refund đủ) và cập nhật hash/link commit thực tế vào báo cáo.
