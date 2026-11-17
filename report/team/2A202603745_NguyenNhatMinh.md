# Báo cáo cá nhân — 2A202603745_NguyenNhatMinh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Nhật Minh
- MSSV: 2A202603745
- Email: nnhatminh2610@gmail.com
- GitHub: NhMinh-2610

## 2. Phần việc phụ trách

Shape C `orchestrator`; handoff chỉ đọc; trace và kiểm tra rò secret/PII;
kiểm crash/idempotency; quyết định kiến trúc trong `decision_adr.md`.

## 3. Đóng góp cụ thể

- Commit triển khai: `a06249f`.
- Hoàn thiện `src/lab8/shapes/orchestrator.py`: đọc claim an toàn, giao tool đọc
  cho investigator, quote từ order view, gọi host với quote đầy đủ và trả qua
  `common.finish()`. Không dùng ticket làm nguồn quyết số tiền.
- Truyền `crash_at`, để crash truyền ra ngoài, đóng connection trong `finally`.
- Bổ sung 15 trường hợp test trong `src/tests/test_team_orchestrator.py`, bao
  gồm secret/PII nằm cả trong ticket, approval thiếu/sai claim, ba điểm crash,
  replay, quote thay đổi gây conflict, trần theo đơn và trace ở nhánh sớm.
- Viết `src/tests/audit_team_security.py` để tái lập audit public cho cả bốn shape.
  Tài liệu allowlist và field cấm: `orchestrator_security.md`.
- Tổng hợp benchmark, crash và audit vào ADR; chọn single theo bằng chứng hiện
  tại và nêu điều kiện đánh giá lại khi workflow được tích hợp.

## 4. Bằng chứng

Các lệnh chạy trong `src/`, sau khi kích hoạt môi trường ảo:

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest -q tests/test_team_orchestrator.py --basetemp=.pytest_cache/tmp-minh` | 15 passed |
| `python -m pytest -q -m student -o addopts= -k orchestrator --basetemp=.pytest_cache/tmp-orchestrator` | 62 passed |
| `python -m pytest -q --basetemp=.pytest_cache/tmp` | 77 passed, 248 deselected |
| `python -m pytest -q -m student -o addopts= -k "not workflow" --basetemp=.pytest_cache/tmp-ready-shapes` | 186 passed, 139 deselected; single, orchestrator và swarm |
| `python -m lab8.crash_test --count 20 --out reports/crash.json` | 20/20; suite host + swarm |
| `python -m tests.audit_team_security --out reports/orchestrator_security.json` | 280 trial; secret/PII/approval bypass/trace errors đều 0; workflow có 70 trial stub |

`src/reports/benchmark.json`: orchestrator 70/70 public, pass rate/pass^5 = 1/1,
seed variance = 0, cost/success = 57.23 VND mô phỏng. Run ID minh họa:
`R-orchestrator-C-001-s11`, `R-orchestrator-C-002-s55`.
Kết quả benchmark và audit được sinh bằng công cụ; không sửa JSON bằng tay.

Trên máy Windows, pytest mặc định gặp lỗi quyền truy cập thư mục temp dùng
chung. `--basetemp=.pytest_cache/tmp` chuyển dữ liệu tạm vào thư mục riêng của
dự án; không sửa host, metric, policy hoặc fixture để vượt test.

## 5. Công cụ AI đã dùng

Codex hỗ trợ triển khai orchestrator, viết test/audit, chạy lệnh kiểm chứng và
tổng hợp số liệu vào báo cáo. Mã chạy lab chỉ dùng MockLLM offline; không gọi
model thật hoặc dùng API key. Bằng chứng kiểm chứng là kết quả pytest và report
do công cụ sinh; không coi nội dung AI sinh ra là bằng chứng đã hiểu hoặc đã
đạt điểm hidden.

## 6. Tự đánh giá

Phần orchestrator đã qua ma trận public và kiểm tra bổ sung về ranh giới bảo mật,
retry và ba cửa sổ crash. Audit chỉ chứng minh phạm vi dữ liệu và output đã quét.
Chưa có bộ hidden hoặc `student_drop/` để kết luận điểm hidden. Workflow còn
stub tại commit benchmark, nên cần đánh giá lại lựa chọn kiến trúc sau tích hợp.
Khả năng giải thích trực tiếp kiến trúc và ranh giới code/model phải được kiểm
tra độc lập với các test tự động.

Tự kiểm bài nộp tại commit triển khai: `lab8.check_submission` xác nhận
orchestrator, single, ADR và các report đúng format. Hai lỗi còn lại là workflow
chưa triển khai và research card chưa điền. Báo cáo nhóm, thông tin/đóng góp của
hai thành viên còn lại và quyết định sau tích hợp cần được nhóm hoàn thiện trước nộp.
