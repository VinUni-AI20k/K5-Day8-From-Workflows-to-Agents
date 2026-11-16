# Báo cáo cá nhân

- Họ và tên: Nguyễn Đức Đạt
- MSSV: 2A202603544
- Email: nguyenducdat298@gmail.com
- GitHub: nguyenducdat298
- Vai trò trong nhóm: Viết báo cáo & Đánh giá thực nghiệm (Eval & Reporting Specialist)

---

## 1. Phần việc phụ trách

- Phụ trách nghiên cứu, đánh giá thực nghiệm và viết toàn bộ hệ thống báo cáo của nhóm:
  - Báo cáo nhóm tổng thể (`report/team/group_report.md`).
  - Tài liệu quyết định kiến trúc (`report/team/decision_adr.md`).
  - Phiếu nghiên cứu khoa học (`report/team/research_card.md`).
  - Báo cáo cá nhân (`report/team/2A202603544_NguyenDucDat.md`).
- Tham gia chạy thử nghiệm, thu thập và đối chiếu các số đo thực nghiệm từ kết quả benchmark (pass rate, pass^5, seed variance, cost per success).

---

## 2. Đóng góp cụ thể: Viết báo cáo

- **Soạn thảo Báo cáo nhóm (`report/team/group_report.md`):**
  - Hoàn thiện đầy đủ 8 mục theo chuẩn Rubric: Mục tiêu và cách tiếp cận, Phân tích giải pháp 3 shapes, Ranh giới bảo mật (Code vs. Model), Bảng kết quả đối sánh 4 shapes x 5 seeds, Khó khăn và cách xử lý, Tổng hợp đóng góp, Hạn chế và Hướng cải thiện.
- **Soạn thảo Tài liệu Quyết định Kiến trúc (`report/team/decision_adr.md`):**
  - Đưa ra quyết định lựa chọn Shape A (`workflow`) dựa trên cơ sở khoa học và bằng chứng số liệu từ `reports/benchmark.json`.
  - Luận giải chi tiết lý do không đánh đổi lấy Multi-Agent trong bài toán này và xác định rõ 3 điều kiện kinh doanh thực tế sẽ làm đảo ngược quyết định kiến trúc.
- **Soạn thảo Phiếu Nghiên cứu Khoa học (`report/team/research_card.md`):**
  - Lựa chọn và giải quyết bài toán R2 (Failure Taxonomy) dựa trên bài báo NeurIPS 2025 (*Why Do Multi-Agent LLM Systems Fail?*).
  - Phân tích thực nghiệm nguyên nhân thất bại của Swarm ở seed 55 trên claim `C-002` là do lỗi kiểm chứng (Verification Failure) và đối chứng với khả năng kiểm chứng tất định của Workflow.
- **Hoàn thiện `TEAM.md`:** Cập nhật thông tin thành viên, phân vai và bảng đóng góp đúng chuẩn định dạng để `check_submission` chấm tự động.

---

## 3. Bằng chứng

- **Host Gate Test:** `54 passed, 248 deselected` (`python -m pytest -q`).
- **Student Matrix Test:** `248 passed, 0 failed` (`python -m pytest -q -m student -o addopts=`).
- **Crash Safety Test:** `20/20` (`python -m lab8.crash_test --count 20 --out reports/crash.json`).
- **Benchmark Suite:** Hoàn thành 4 shape x 14 claims x 5 seeds = 280 trials (`reports/benchmark.json`).
- **Submission Check:** `python -m lab8.check_submission` đạt chuẩn định dạng hoàn toàn (`0 FAIL, 0 WARN`).
