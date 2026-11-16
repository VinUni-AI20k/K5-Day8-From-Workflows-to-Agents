# Bàn giao Nguyễn Quốc Hưng — 2A202603553 — nhánh hung

Repo nhóm: [congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents). Nhánh của Nguyễn Quốc Hưng: [hung](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/tree/hung).

Phần code đã hoàn thành và kiểm tra trên nguồn tại commit `034c6c421c198dae67a9211d15e2587d5a378972`. Commit kỹ thuật của Nguyễn Quốc Hưng: [`2ce84ee86e7f71d83d5bb86ba83b1c22e544b952`](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/2ce84ee86e7f71d83d5bb86ba83b1c22e544b952). Báo cáo dẫn hash này; commit tiếp theo bổ sung báo cáo.

## File đưa lên nhánh hung

Giữ đúng đường dẫn tính từ gốc repo nhóm:

- `src/lab8/shapes/orchestrator.py` — Shape C hoàn chỉnh.
- `src/tests/test_team_orchestrator.py` — 19 test riêng.
- `src/tests/audit_team_security.py` — công cụ rà secret/PII, trace và stdout trên cả ba shape.
- `src/tests/research_orchestrator_r3.py` — biến thể thí nghiệm R3, chỉ thay cách phân chia tool đọc cho investigator.
- `src/tests/check_member3_after_merge.ps1` — chạy hai kiểm tra sau merge trên Windows.
- `src/reports/orchestrator_benchmark.json`, `orchestrator_r3_ablation.json`, `orchestrator_security.json` — bằng chứng sinh từ lệnh chạy thực tế.
- `src/reports/crash.json` — crash suite host do công cụ chính thức sinh, đạt `20/20`.
- `src/reports/member3_security_before_merge.json` — audit trạng thái starter trước merge; Shape C sạch, A/B chưa triển khai nên toàn bộ audit báo BLOCKED.
- `report/team/2A202603553_NguyenQuocHung.md` — báo cáo cá nhân đã điền tên, MSSV, tài khoản GitHub, repo và nhánh.

Các file dùng chung `TEAM.md`, `report/team/group_report.md`, `report/team/research_card.md` đã có phần của người 3. Khi đưa vào repo nhóm đã có nội dung đồng đội, **ghép dòng đóng góp/mục Shape C/phần R3 vào bản hiện có**, giữ nguyên phần của người khác. Không ghi đè cả file bằng template của bản bàn giao.

Giải nén gói ZIP và đưa các file vào đúng đường dẫn trên nhánh `hung`; không upload nguyên file ZIP vào repo. Nếu dùng Git, làm trong checkout repo nhóm trên máy của bạn và chuyển sang nhánh bằng `git switch hung` trước khi chép file. Nếu dùng trang GitHub, chọn nhánh `hung` trước khi upload.

Không đưa `.venv`, `.qa`, `__pycache__`, `.pytest_cache`, `traces`, `*.sqlite` lên repo. Gói ZIP đã loại các file này và không chứa code A/B hay file host/config/data của starter.

## Kết quả đã chạy

| Kiểm tra | Kết quả |
| --- | --- |
| Smoke | `lab8.smoke pass` |
| Student matrix Shape C | `62 passed` |
| Test riêng | `19 passed` |
| Bộ test mặc định | `73 passed` |
| Benchmark riêng C, public 14 claim × 5 seed | `70/70`, pass^5 `1.0`, variance `0.0` |
| Audit riêng C | 70 trace hợp lệ; 0 secret/PII/raw-row finding |
| R3: 1 investigator so với 2 investigator | Cả hai `70/70`; cost/success tăng từ khoảng `49.00` lên `58.29` VND mô phỏng |

Public pass không phải điểm hidden. Không có API key hay model thật. Latency là `unavailable`.

## Chạy lại

Tất cả các lệnh Python dưới đây chạy trong `src/` của repo nhóm, sau khi cài requirements và kích hoạt môi trường Python 3.11–3.13:

```text
python -m pytest -q -m student -o addopts= -k orchestrator
python -m pytest -q tests/test_team_orchestrator.py
python -m pytest -q
python -m tests.audit_team_security --shapes orchestrator --out reports/orchestrator_security.json
```

Nếu máy Windows báo lỗi quyền truy cập temp của pytest, có thể đặt biến sau trong PowerShell, tạo thư mục rồi chạy lại. Đây là cách đã dùng trên máy thực thi:

```powershell
$env:PYTEST_DEBUG_TEMPROOT = Join-Path (Get-Location) '.qa\pytest-temp'
New-Item -ItemType Directory -Force -Path $env:PYTEST_DEBUG_TEMPROOT | Out-Null
```

## Sau khi merge code của cả ba người

Người 1 tạo benchmark cuối đủ bốn shape và crash report. Cả nhóm điền ADR từ số liệu cuối và commit thật. Sau đó người 3 chạy:

```text
python -m tests.audit_team_security --shapes workflow,single,orchestrator --out reports/team_security.json
python -m lab8.check_submission
```

Hoặc trên Windows, chạy một lệnh trong `src/`:

```powershell
powershell -ExecutionPolicy Bypass -File tests/check_member3_after_merge.ps1
```

Script chỉ thành công khi audit không còn stub/lỗi/rò rỉ và `check_submission` ra `0 FAIL`. Trên bản starter hiện tại, hai shape A/B, báo cáo benchmark/crash chung và ADR cuối còn thiếu nên chưa thể có `0 FAIL`. Không sửa checker hoặc điền số giả để vượt bước này.

Đề yêu cầu phiếu nghiên cứu chính chọn **một** câu R1–R4. Phần R3 đã điền đầy đủ và có ablation thật; cả nhóm thống nhất dùng R3 hoặc ghép thành tài liệu phụ khi chọn câu khác.

Hash kỹ thuật thật đã được ghi vào `TEAM.md` và báo cáo cá nhân. Khi chốt bài nhóm, mỗi thành viên tự nộp link repo lên LMS.
