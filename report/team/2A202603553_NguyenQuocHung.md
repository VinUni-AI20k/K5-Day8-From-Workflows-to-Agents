# Báo cáo cá nhân — Nguyễn Quốc Hưng — 2A202603553

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quốc Hưng.
- MSSV: 2A202603553.
- Email: hung90879087@gmail.com.
- GitHub: hung309911.
- Repo nhóm: https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents.
- Nhánh làm việc: `hung`.
- File báo cáo: `report/team/2A202603553_NguyenQuocHung.md`.

## 2. Phần việc phụ trách

- Hoàn thiện `src/lab8/shapes/orchestrator.py`: handoff allowlist, investigator chỉ đọc, quote bằng code, host là cửa ghi refund.
- Thêm test riêng `src/tests/test_team_orchestrator.py`.
- Chuẩn bị công cụ rà trace/stdout/PII `src/tests/audit_team_security.py` để chạy lại sau merge.
- Viết phần Shape C của báo cáo nhóm và phiếu nghiên cứu R3, kèm ablation chạy được.

## 3. Đóng góp cụ thể

Commit kỹ thuật: [`2ce84ee86e7f71d83d5bb86ba83b1c22e544b952`](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/2ce84ee86e7f71d83d5bb86ba83b1c22e544b952), chứa Shape C, các test và bằng chứng benchmark/security. Phần báo cáo được cập nhật trong commit tiếp theo để dẫn đúng hash này.

Handoff dùng `make_handoff`, facts rỗng và chỉ cấp `lookup_order`, `lookup_policy`. Không chuyển ticket hoặc toàn bộ parent context cho investigator. Orchestrator tính quote bằng `compute_compensation`, giữ quote đầy đủ khi gọi `issue_refund`, để host xử lý approval, giới hạn theo đơn và idempotency. Mọi nhánh kết thúc dùng `finish()`. `crash_at` được truyền nguyên vẹn, `InjectedCrash` được phát ra ngoài và connection được đóng trong `finally`.

Các test riêng kiểm việc chặn ticket injection ở 5 seed, không lộ dữ liệu qua handoff/trace/stdout, trace mới trên nhánh trả sớm, approval bị thu hồi/hết hạn, top-up theo quote đầy đủ, retry sau cả 3 cửa sổ crash và xung đột quote sau lần hoàn đầu.

## 4. Bằng chứng thực thi

- Python 3.13.17, Windows AMD64; `lab8.smoke pass`.
- Ma trận student Shape C: `62 passed`.
- Test riêng: `19 passed`.
- Bộ test mặc định sau thay đổi: `73 passed`.
- Crash suite host: `src/reports/crash.json`, `20/20`; các cửa sổ crash của Shape C được kiểm riêng trong test mới.
- Benchmark riêng: `src/reports/orchestrator_benchmark.json`, `70/70` trial public pass, pass^5 `1.0`, variance `0.0`; run id ví dụ `R-orchestrator-C-001-s11`.
- R3: `src/reports/orchestrator_r3_ablation.json`. Tách investigator giữ pass rate/pass^5 nhưng tăng cost/success từ `49.00142857142857` lên `58.287142857142854` VND mô phỏng.
- Audit riêng: `src/reports/orchestrator_security.json`. Shape C có 70 trace hợp lệ, không phát hiện secret/PII/raw-row field. Workflow/single trên main lúc chuẩn bị PR vẫn là stub; cần audit lại cả nhóm sau khi merge đủ các shape.
- Trường hợp máy này: dùng `PYTEST_DEBUG_TEMPROOT` trỏ vào `.qa/pytest-temp` để xử lý quyền truy cập thư mục temp của pytest, không sửa host/test gốc.

## 5. Công cụ AI đã dùng

Codex/ChatGPT được dùng để đọc contract, hỗ trợ triển khai Shape C, viết test và soạn báo cáo. Đầu ra đã được kiểm bằng smoke, pytest, benchmark chính thức và audit; các số liệu trong báo cáo lấy từ lần chạy thực tế. Mã lab chỉ gọi MockLLM có seed, không gọi API model thật hoặc dùng API key.

## 6. Tự đánh giá và việc còn cần tích hợp

Phần Shape C đã đạt các test public và kiểm tra riêng nêu trên. Kết quả public chưa chứng minh ngưỡng hidden. Khi trình bày, cần giải thích ranh giới code/model, full quote, handoff allowlist và cách retry dựa trên ledger.

Sau merge cần chạy audit cả ba shape, `python -m lab8.check_submission` và các kiểm tra chung của nhóm. Nhóm điền ADR bằng benchmark cuối; Nguyễn Quốc Hưng tự nộp link repo lên LMS.
