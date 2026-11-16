# Báo cáo cá nhân — Nguyễn Tuấn Quang

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tuấn Quang
- MSSV: 2A202603392
- Nhóm: MienNui, lớp L3A
- Vai trò: Orchestrator + Handoff
- Tài khoản tác giả trong Git: `quangbg004`
- Email trong commit: `quangbg04@gmail.com`

## 2. Phần việc phụ trách

Triển khai shape C để điều phối việc tra cứu đơn hàng, tính khoản hoàn phí từ dữ liệu nghiệp vụ và chuyển đề xuất đến host. Phần handoff xác định dữ liệu và quyền truy cập mà investigator nhận được. [Mã nguồn orchestrator](../../src/lab8/shapes/orchestrator.py)

## 3. Đóng góp cụ thể

Commit `8939976` (`orchestrator + handoff`) triển khai shape và bổ sung một test tích hợp cho ranh giới handoff.

- **Điều phối và phân quyền.** Orchestrator đọc claim qua `get_claim_view`. Claim không tồn tại trả `failed`, thiếu mã đơn trả `needs_info`. Với claim có mã đơn, `make_handoff` tạo `handoff.v1` với `facts` rỗng, phạm vi `owner_order_only` và đúng một công cụ là `lookup_order`. Runtime dùng principal của claim khi tra cứu. Đơn không tìm thấy hoặc ngoài phạm vi trả `escalated`.
- **Tính và ghi tiền.** `compute_compensation` tính từ dữ liệu đơn và policy hiện hành. Nếu đề xuất bằng 0, shape trả `denied`. Nếu đề xuất dương, shape chuyển toàn bộ số tiền cho `issue_refund` để host kiểm approval đúng claim và trừ khoản đã hoàn. Ví dụ, C-014 đề xuất 150.000 VND và host ghi 120.000 VND sau khi trừ 30.000 VND đã hoàn. Host từ chối trả `denied`, xung đột số tiền trả `failed`, host chấp nhận trả `resolved`.
- **Trace và phục hồi.** `common.finish()` ghi trace và lấy effect cùng số audit từ ledger ở mọi nhánh trả kết quả. Trace ghi handoff đã lọc, khả năng truy cập đơn, số tiền đề xuất, lượt yêu cầu hoàn phí và trạng thái cuối. Ticket, claim/order thô, header, secret và thông tin cá nhân được loại khỏi trace. Khi có `crash_at`, shape ghi trace trước khi gọi host và để `InjectedCrash` truyền ra ngoài. Ledger của host bảo đảm chạy lại trên cùng DB chỉ có một refund và một audit `refund_committed`.

## 4. Bằng chứng

Các lệnh kiểm chứng chạy trong `src/` trên Windows với Python 3.12.6.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -k orchestrator -p no:cacheprovider
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out "$env:TEMP/lab8-orchestrator-benchmark.json"
```

| Kiểm chứng | Kết quả |
| --- | --- |
| Bộ pytest mặc định trên repo đã tích hợp | 83 passed |
| Ma trận public riêng của orchestrator | 62 passed, gồm T11 retry và T12 crash/resume |
| Benchmark public trên 14 claim × 5 seed | 70/70 trial đạt, pass rate và pass^5 đều bằng 1,00 |
| Pass rate theo seed và phương sai | Min–max 1,00–1,00, phương sai 0,00 |
| Chi phí mô phỏng cho mỗi trial thành công | 43,57 VND, trung bình 0 lần gọi MockLLM |
| Kiểm qua CLI tại ba điểm crash | `before_effect`, `after_effect_before_checkpoint` và `after_checkpoint` đều phục hồi. Mỗi ca giữ một refund 35.000 VND và một audit sau resume và retry. |

Test `test_orchestrator_delegates_through_sanitized_readonly_handoff` kiểm payload thực tế nhận bởi investigator, đối chiếu với trace và quét chuỗi cấm trong trace, kết quả, stdout và stderr. [Test tích hợp](../../src/tests/test_orchestrator_handoff.py)

Run ID dẫn chứng từ benchmark gồm `R-orchestrator-C-002-s55` cho trường hợp số ngày trong ticket khác dữ liệu đơn, `R-orchestrator-C-010-s55` cho ca kiểm ranh giới secret, và `R-orchestrator-C-014-s11` cho ca chỉ hoàn phần chênh lệch.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc contract, triển khai shape, bổ sung test handoff và soạn báo cáo. Các kết quả trong mục 4 lấy từ lệnh kiểm thử và benchmark Codex đã chạy. Khi trình bày phần này, có thể đối chiếu lại kết quả T11/T12 và số tiền của C-014 bằng các lệnh trên. [Quy định sử dụng AI](../../RULES.md)

## 6. Tự đánh giá

Phần điều phối hiện dùng một investigator và một truy vấn nghiệp vụ được cấp quyền qua handoff. Cách triển khai này thể hiện được ranh giới giữa quyền đọc của investigator và quyền ghi của host. Kết quả trên năm seed cho thấy hành vi ổn định với bộ public. Bộ hidden của giảng viên chưa được chạy, chi phí là giá mô phỏng và latency để `unavailable`.
