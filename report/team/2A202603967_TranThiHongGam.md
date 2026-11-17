# Báo cáo cá nhân — 2A202603967_TranThiHongGam

## 1. Thông tin thành viên

- Họ tên: Trần Thị Hồng Gấm
- MSSV: 2A202603967
- Email: tranthihonggam290905@gmail.com
- GitHub: Honggam1109

## 2. Phần việc phụ trách

- **Task 1 — Workflow + tích hợp:** Hoàn thiện `src/lab8/shapes/workflow.py` theo luồng tuần tự xác định bằng Python; điều phối tích hợp cả ba kiến trúc với cổng host và giữ bộ test cổng host luôn xanh.

## 3. Đóng góp cụ thể

- Commit `03ce5b8`: cài đặt `src/lab8/shapes/workflow.py` xử lý đầy đủ các nhánh `unknown_claim`, `needs_info`, `escalated`, `denied` (quote = 0 và host từ chối), `resolved`, `failed` (`amount_conflict`), không tin số ngày trong `ticket` và truyền quote đầy đủ vào host.
- Bổ sung các bài test hồi quy cho `workflow` (đã tách gọn sang `src/tests/test_workflow.py`) kiểm tra `C-UNKNOWN`, chống injection từ nội dung `ticket`, chống lộ chuỗi canary và các điểm crash `before_effect`, `after_checkpoint`.

## 4. Bằng chứng

- Commit `03ce5b8` (PR #1 từ nhánh `HG` vào `main`).
- Test: `src/tests/test_workflow.py` và ma trận `pytest -q -m student -o addopts= -k workflow` (`62 passed`).
- Trong `src/reports/benchmark.json`, `workflow` đạt `pass_rate = 1.000` (70/70), `pass^5 = 1.000`, `seed_variance = 0.000000`, chi phí thấp nhất (`28.87` VND/success) và được chọn làm kiến trúc nộp chính thức.

## 5. Công cụ AI đã dùng

- Sử dụng trợ lý AI để tra cứu luật nghiệp vụ trong `docs/business_rules.md`, kiểm tra các nhánh trạng thái của `RunResult` và rà soát test hồi quy cho `workflow`.
- Tự kiểm chứng bằng `pytest` trên bộ host và bộ student cho `workflow` trước khi merge vào nhánh chính.

## 6. Tự đánh giá

- Hoàn thành đầy đủ phần việc được giao, giữ đúng chữ ký hàm và ranh giới bảo mật; kiến trúc `workflow` đạt độ ổn định cao nhất trong benchmark nhóm.

