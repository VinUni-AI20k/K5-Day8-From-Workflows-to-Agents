# Báo cáo cá nhân — 2A202603998_TranDuyManh

## 1. Thông tin thành viên

- Họ tên: Trần Duy Mạnh
- MSSV: 2A202603998
- Email: duymanhtran2004mkc2@gmail.com
- GitHub: TDM414

## 2. Phần việc phụ trách

- **Task 4 — Ledger safety + đánh giá:** Kiểm thử idempotency, approval, giới hạn hoàn tiền theo đơn và crash safety (T11, T12, crash suite 20/20); rà soát tích hợp 3 kiến trúc theo tiêu chuẩn nộp bài; chạy công cụ sinh `src/reports/crash.json` và `src/reports/benchmark.json`; tổng hợp `TEAM.md`, `decision_adr.md`, `research_card.md` và `group_report.md`. Không chỉnh sửa `durability.py`, `policy.py`, `metrics.py`, `config/`, `data/`.

## 3. Đóng góp cụ thể

- Commit `1f4bca2`: bổ sung bộ test kiểm chuẩn nộp bài `src/tests/test_submission_standards.py` và tách gọn `src/tests/test_workflow.py`, `src/tests/test_orchestrator.py`; gia cố việc lưu trace khi crash ở `workflow.py` và `single.py`, bật cờ khóa worker cho `single.py`, bổ sung tính ngân sách model cho `orchestrator.py` và `workflow.py`.
- Chạy công cụ tạo bằng chứng `src/reports/crash.json` (`20/20`) và `src/reports/benchmark.json` (4 kiến trúc × 14 claim × 5 seed).
- Hoàn thiện hồ sơ quyết định kiến trúc (`workflow`), phiếu nghiên cứu R3 và báo cáo tổng hợp nhóm.

## 4. Bằng chứng

- Commit `1f4bca2` trên nhánh `main` của repo `TDM414/K5-L3B-DAY08-NhomDMTG-FromWorkflowsToAgents`.
- File kiểm thử: `src/tests/test_submission_standards.py`.
- File bằng chứng: `src/reports/crash.json` (`crash_safety: "20/20"`), `src/reports/benchmark.json` (`workflow` đạt `pass_rate = 1.0`, `cost_per_success_vnd = 28.87`), `python -m lab8.check_submission` đạt `0 FAIL`.

## 5. Công cụ AI đã dùng

- Sử dụng trợ lý AI trong IDE để đọc cấu trúc repo, rà soát lỗi xử lý trace khi crash ở 3 shape, sinh khung bộ test chuẩn nộp bài độc lập từ `SUBMISSION.md` và kiểm tra tính nhất quán số liệu báo cáo.
- Mọi kết quả đều được tự kiểm chứng lại bằng cách chạy thực tế `pytest`, `lab8.crash_test`, `lab8.benchmark` và `lab8.check_submission` trên dữ liệu thật của lab.

## 6. Tự đánh giá

- Hoàn thành đầy đủ phạm vi Task 4 và vai trò tổng hợp tích hợp nhóm: toàn bộ bộ test host, student matrix, bộ test chuẩn nộp bài, crash suite `20/20` và `check_submission` đều đạt xanh, không sửa bất kỳ file thước đo hay cấu hình bị cấm nào.

