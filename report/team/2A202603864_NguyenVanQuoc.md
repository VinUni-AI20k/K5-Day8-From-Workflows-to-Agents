# Báo cáo cá nhân — Nguyễn Văn Quốc

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Quốc
- MSSV: 2A202603864
- Email:
- GitHub: missher03

## 2. Phần việc phụ trách

Kiểm thử nền tảng/tích hợp, crash safety và xác minh theo T002, T010–T011, T016.

## 3. Đóng góp cụ thể

- `src/reports/crash.json` ghi nhận `passed=20` và `crash_safety=20/20` (commit `42c8cf2` trên nhánh `quoc/task5`).
- Chạy cổng tích hợp **T010** sau khi merge các PR shape (`workflow`, `single`, `orchestrator`): `lab8.smoke` pass, host pytest `165 passed, 248 deselected`, student matrix `248 passed, 165 deselected`, và rà soát `git diff` xác nhận không sửa các file được bảo vệ.
- Bổ sung bộ test tích hợp cá nhân `src/tests/test_integration_safety.py` (9 test case parametrize trên `workflow`, `single`, `orchestrator` kiểm tra crash/resume, chống ticket injection ở seed 55, bảo vệ secret/PII, và truyền full quote ở `C-014`) trên nhánh `quoc/task5` (commit `88b6ba3`, đạt `9 passed in 1.22s`).

## 4. Bằng chứng

- Commit:
  - `42c8cf2 chore(crash): add T011 crash safety report (20/20)` (`src/reports/crash.json`)
  - `88b6ba3 test(integration): add safety tests, personal report, and member 5 name` (trên nhánh `quoc/task5`, gồm `src/tests/test_integration_safety.py`)
- Report: `src/reports/crash.json` (`crash_safety: 20/20`).
- Lệnh đã chạy từ `src/`:
  - `python -m lab8.smoke` → `lab8.smoke pass` (`manifest 1.1 | MockLLM seeded | swarm C-001 refund 35000 | trace clean`)
  - `python -m pytest -q` → `165 passed, 248 deselected`
  - `python -m pytest -q -m student -o addopts=` → `248 passed, 165 deselected`
  - `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`
  - `python -m pytest -q tests/test_integration_safety.py` → `9 passed`

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI (Antigravity / Gemini).
- **Mục đích:** Đọc hiểu tài liệu lab/contract, tổng hợp danh sách công việc theo `tasks.md`, hỗ trợ viết bộ test `src/tests/test_integration_safety.py`, chạy các lệnh kiểm thử/crash suite và hoàn thiện báo cáo cá nhân.
- **Cách tự kiểm tra:** Chạy trực tiếp toàn bộ lệnh trong `.venv` (`lab8.smoke`, `pytest -q`, `pytest -q -m student -o addopts=`, `lab8.crash_test`, `lab8.check_submission`), kiểm tra `src/reports/crash.json` và đối chiếu `git diff` để bảo đảm không sửa các file bị cấm.

## 6. Tự đánh giá

- Đã hoàn thành các nhiệm vụ T002, T010, T011 đúng phạm vi và quy định toàn vẹn của bài lab (`crash_safety 20/20`, không chạm file được bảo vệ).
- Đã bổ sung test tích hợp cá nhân (`src/tests/test_integration_safety.py`) trên nhánh `quoc/task5` và cập nhật đầy đủ bằng chứng, thông tin AI-use; sẵn sàng chạy bước xác minh cuối **T016** theo `quickstart.md` sau khi nhóm chốt T014.
