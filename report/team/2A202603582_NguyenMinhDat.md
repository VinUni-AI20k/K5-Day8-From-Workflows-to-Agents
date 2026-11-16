# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Minh Đạt
- MSSV: 2A202603582
- Email: nguyenminhdat6401@gmail.com
- GitHub: https://github.com/nguyenminhdat6401

## 2. Phần việc phụ trách


Triển khai và kiểm thử single agent tại
src/lab8/shapes/single.py.


...

## 3. Đóng góp cụ thể


- Giữ nguyên chữ ký run_claim và trả kết quả theo RunResult.
- Sử dụng run_react với giới hạn max_steps=8.
- Điều phối lookup_order và compute_compensation từ observation.
- Gọi MockLLM và ghi nhận usage qua Budget.
- Để host ghi refund sau vòng lặp; agent chỉ dùng tool đọc.
- Truyền quote đầy đủ và crash_at vào issue_refund.
- Dùng common.finish để tạo kết quả và trace.
- Kiểm tra trường hợp claim không tồn tại trên single
  trong tests/test_student_unknown_claim.py.

Commit chính: eef682d

...

## 4. Bằng chứng

- Code: src/lab8/shapes/single.py.
- Test bổ sung: src/tests/test_student_unknown_claim.py,
  trường hợp tham số single.
- Bộ test riêng single: 62 passed.
- Bộ test tích hợp repo update: 305 passed.
- Report: src/reports/benchmark.json.
- Run ID dẫn chứng: R-single-C-001-s11.

Kết quả benchmark single trên 14 claim public và 5 seed:
- Pass rate: 1.000.
- Pass^5: 1.000.
- Seed variance: 0.000000.
- Cost/success: 29.16 VND mô phỏng.
- Mean/p95 steps: 4.57 / 5.

Các kiểm tra được chạy từ thư mục src.

...

## 5. Công cụ AI đã dùng

Công cụ, dùng vào việc gì, và bạn đã tự kiểm tra kết quả thế nào (xem [RULES.md](../../RULES.md)).
Sử dụng ChatGPT/Codex để giải thích yêu cầu, gợi ý code
single và test, hướng dẫn xử lý lỗi môi trường.

Kiểm chứng kết quả bằng test riêng single, bộ test tích hợp
và benchmark. Đối chiếu trạng thái, proposal_amount,
refund và audit thông qua bộ kiểm thử của repo.

...

## 6. Tự đánh giá

Single đạt các kiểm tra public đã chạy, bao gồm retry
và crash. Quyền ghi refund được tách khỏi vòng ReAct;
tiền do code tính từ order và policy hiện hành.

Trong triển khai này, action được chọn bằng logic Python.
MockLLM được gọi để ghi nhận usage nhưng chuỗi trả về
không quyết định action. Vì vậy chưa thể dùng kết quả
để kết luận về khả năng tự chủ của model thực.

Chưa có kết quả hidden. Chi phí là mô phỏng;
latency là unavailable.

...
