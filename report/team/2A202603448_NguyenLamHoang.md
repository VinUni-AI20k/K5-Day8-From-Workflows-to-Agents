# Báo cáo cá nhân — Nguyễn Lâm Hoàng

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lâm Hoàng
- MSSV: 2A202603448
- Email: 26ai.hoangnl@vinuni.edu.vn
- GitHub: https://github.com/hoangnguyenai

## 2. Phần việc phụ trách

Triển khai shape A tại `src/lab8/shapes/workflow.py` và kiểm thử tích hợp workflow với các thành phần host có sẵn: đọc dữ liệu theo principal, tính compensation, approval, ledger, checkpoint, trace và output contract.

## 3. Đóng góp cụ thể

Commit code, test và benchmark: `2fbe693` — `Implement deterministic workflow and host integration regressions`.

Workflow thực hiện các bước Python cố định: `get_claim_view` → kiểm tra mã đơn → `lookup_order` theo principal → `compute_compensation` → `issue_refund` khi quote dương → `finish`. Claim không tồn tại trả `failed`; thiếu mã đơn trả `needs_info`; đơn không tìm thấy hoặc ngoài phạm vi principal trả `escalated`; quote bằng 0 trả `denied`. Host từ chối approval trả `denied`, conflict số tiền trả `failed`, host chấp nhận trả `resolved`.

Tiền được tính từ order và policy hiện hành, không lấy từ câu chữ trong ticket. Workflow không gọi model, nên có thể đo hành vi xác định và chi phí tool mà không thêm chi phí model. Mọi thao tác đọc nghiệp vụ và yêu cầu ghi refund đều được cộng vào `Budget`.

Quote đầy đủ được truyền vào host. Host kiểm approval của đúng claim, áp trần theo đơn và trừ phần đã hoàn trong transaction. Với C-014, proposal là 150.000 VND và effect là 120.000 VND; workflow không trừ trước 30.000 VND. Với C-013, quote 35.000 VND vẫn được chuyển tới host để ghi audit từ chối khi đơn đã được hoàn đủ.

Tham số `crash_at` được chuyển nguyên vẹn cho `issue_refund`; `InjectedCrash` được truyền ra ngoài. Kết nối SQLite luôn đóng trong `finally`. Ledger và audit của host bảo đảm retry/resume không tạo refund trùng.

Các nhánh kết thúc dùng `common.finish()` để lấy effect và audit từ database, tạo `RunResult` và ghi trace trong lần chạy hiện tại. Trace chỉ ghi trạng thái tìm claim, kết quả kiểm quyền đọc đơn, quote, yêu cầu refund, kết quả host và quyết định cuối. Không ghi ticket, principal, claim/order thô, header, secret, số điện thoại, địa chỉ, tên hàng hay ghi chú nội bộ. Trace được lưu trước khi gọi host để vẫn có bằng chứng nếu xảy ra crash.

Bổ sung `src/tests/test_workflow_integration.py` gồm 28 ca: injection trong ticket, trần theo đơn, approval không tồn tại và approval sai claim, conflict sau commit, thay thế trace cũ cho claim không tồn tại và 20 tổ hợp crash/seed qua cả ba vị trí `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`. Mỗi ca crash đều kiểm tra resume rồi retry vẫn chỉ có một effect và một audit committed. Các test tích hợp thuộc cổng pytest mặc định để kiểm tra lại khi ghép các shape của nhóm.

## 4. Bằng chứng

Môi trường kiểm chứng: Windows AMD64, Python 3.14.3, pytest 8.4.2. Phạm vi phiên bản yêu cầu của đề là Python 3.11–3.13; các kết quả dưới đây được đo trên môi trường nêu trên.

Các lệnh chạy trong `src/`, dùng Python của virtualenv:

```powershell
.\.venv\Scripts\python.exe -m lab8.smoke
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -k workflow -p no:cacheprovider
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/workflow_benchmark.json
```

| Kiểm chứng | Kết quả |
| --- | --- |
| Smoke | `lab8.smoke pass` |
| Cổng host và test tích hợp | 82 passed, 248 deselected |
| Ma trận student của workflow | 62 passed, 268 deselected |
| Test tích hợp bổ sung | 28 passed, gồm 20 ca crash/resume |

Benchmark được công cụ sinh tại [src/reports/workflow_benchmark.json](../../src/reports/workflow_benchmark.json), trên 14 claim public và seed `11,22,33,44,55`, database mới cho mỗi trial:

| Metric | Giá trị |
| --- | --- |
| Trial pass | 70/70 |
| Pass rate / pass^5 | 1.0 / 1.0 |
| Seed min–max / variance | 1.0–1.0 / 0.0 |
| Cost/success mô phỏng | 34,285714 VND |
| Mean / p95 steps | 5,071429 / 6 |
| Mean model calls | 0 |
| Mean tool calls | 3,428571 |

Run id dẫn chứng: `R-workflow-C-001-s11` (refund hợp lệ), `R-workflow-C-002-s55` (không tin số ngày trong ticket), `R-workflow-C-013-s11` (đã hoàn đủ), `R-workflow-C-014-s11` (chỉ ghi phần chênh). JSON benchmark được sinh bằng lệnh, không chỉnh tay.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc tài liệu, triển khai workflow, bổ sung test tích hợp và chạy các lệnh kiểm chứng ở mục 4. Bằng chứng kiểm tra gồm đối chiếu với contract, luật nghiệp vụ, ma trận public, truy vấn effect/audit trong test và benchmark do công cụ của lab tạo. Thông tin này ghi nhận kiểm chứng tự động; không thay cho việc thành viên tự chạy lại và giải thích code khi được hỏi.

## 6. Tự đánh giá

Workflow thể hiện mức tự chủ thấp: code quyết định luồng và số tiền, host quyết định quyền ghi. Kết quả public cho thấy hành vi ổn định trên năm seed và các test crash/resume bảo toàn một refund. Kết quả này có phạm vi dữ liệu public và các test tích hợp đã nêu; không suy ra điểm hidden hay quyết định kiến trúc chung của nhóm. Chi phí là mô phỏng, latency là `unavailable`; lab không sử dụng model sản xuất.
