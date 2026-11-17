# Báo cáo cá nhân — 2A202603955_NguyenXuanDuong

## 1. Thông tin thành viên

- Họ tên: Nguyễn Xuân Dương
- MSSV: 2A202603955
- Email: xuanduong20050808@gmail.com
- GitHub: xuanduong2k5

## 2. Phần việc phụ trách

Phụ trách phần Shape C — orchestrator + handoff và kiểm tra trace/host contract. Cụ thể:

- Cài đặt `run_claim` trong `src/lab8/shapes/orchestrator.py`.
- Xây dựng handoff theo allowlist: chỉ truyền dữ liệu đã được sanitize.
- Gọi nhánh điều tra chỉ đọc để lấy dữ liệu từ order/policy.
- Tính quote từ kết quả investigator và truyền đầy đủ quote vào cổng ghi hoàn tiền của host.
- Đảm bảo `crash_at` được chuyển tiếp đúng, lưu trace khi gặp `InjectedCrash` và không nuốt lỗi.
- Kiểm tra trace JSON được ghi đúng `run_id` và không lộ secret.

## 3. Đóng góp cụ thể

- Commit `9c628ba`: hoàn thiện `src/lab8/shapes/orchestrator.py` dùng `make_handoff` với `allowed_tools=["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]`, không đưa raw claim row hoặc `ticket` vào trace, trả về `RunResult` qua `common.finish(...)`.
- Phối hợp kiểm thử qua `src/tests/test_orchestrator.py` (kiểm tra allowlist handoff, ngân sách model và bảo mật trace).

## 4. Bằng chứng

- Commit `9c628ba` (PR #2 từ nhánh `duong` vào `main`).
- Test: `src/tests/test_orchestrator.py` và ma trận `pytest -q -m student -o addopts= -k orchestrator` (`62 passed`).
- Suite host mặc định `pytest -q` xanh toàn bộ.

## 5. Công cụ AI đã dùng

- Đã sử dụng trợ lý AI để đọc hướng dẫn README, đọc cấu trúc code và kiểm tra bản nháp cho `orchestrator.py`.
- Sau khi hoàn thiện code, đã tự kiểm chứng bằng `pytest` và đối chiếu trực tiếp với `docs/contracts.md` cùng `docs/business_rules.md`.

## 6. Tự đánh giá

- Hoàn thành đúng phần Task 3 theo phân công, đảm bảo ranh giới handoff chỉ đọc, không rò rỉ secret trong trace và xử lý an toàn khi crash.

