# Báo cáo cá nhân — 2A202603720_HaQuangVinh

## 1. Thông tin thành viên

- Họ tên: Hà Quang Vinh
- MSSV: 2A202603720
- Email: hqvinh2210@gmail.com
- GitHub: hqvinh2210-stack

## 2. Phần việc phụ trách

Orchestrator, handoff, benchmark và HTML. Phạm vi phụ trách theo phân công của nhóm.

## 3. Đóng góp cụ thể

Phạm vi chuẩn bị: Orchestrator, handoff, benchmark và HTML.
Test liên quan trong src/tests/: test_orchestrator_boundary.py; test_submission_portability.py; test_bonus_b3.py.

## 4. Bằng chứng

- Test: `test_orchestrator_boundary.py; test_submission_portability.py; test_bonus_b3.py`; chạy trong src/ bằng `python -m pytest -q -o addopts=`.
- Benchmark: src/reports/benchmark.json; run `R-workflow-C-001-s11`; workflow 70/70 trial public.
- Crash: src/reports/crash.json, 20/20; B3: src/reports/bonus_safety.json.
- Tài liệu: TEAM.md, group_report.md, decision_adr.md, research_card.md và bonus_report.md.

## 5. Công cụ AI đã dùng

Codex hỗ trợ viết code, test, đọc contract, chạy kiểm chứng và tạo bản thảo tài liệu. Kết quả được kiểm bằng smoke, host/student pytest, benchmark, crash, safety recount và kiểm tra HTML.

## 6. Tự đánh giá

Đã kiểm chứng và điều chỉnh toàn bộ code và báo cáo do AI hỗ trợ viết.

## 7. Bằng chứng kiểm chứng hidden

Hidden local: workflow 200/200 trial, pass rate 1.0000, pass⁵ 1.0000, variance 0.000000, 29.00 VND mô phỏng/success. Cả ba shape của nhóm và B3 đều đạt 200/200 trên 40 claim × 5 seed. Kiểm bổ sung: 1000 trial không phát hiện secret/PII leak, approval bypass hoặc execution error; crash hidden 30/30. Đây là kết quả chạy công cụ trên snapshot nguồn hiện tại. Xem [hidden_validation.md](hidden_validation.md) và src/reports/hidden_summary.json.
