# Báo cáo cá nhân — Nguyễn Lâm Hoàng

## 1. Thông tin thành viên

- Họ tên: Nguyễn Lâm Hoàng
- MSSV: 2A202603448
- Email: 26ai.hoangnl@vinuni.edu.vn
- GitHub: https://github.com/hoangnguyenai

## 2. Phần việc phụ trách

Triển khai shape A tại `src/lab8/shapes/workflow.py` và kiểm thử tích hợp workflow với các thành phần host có sẵn: đọc dữ liệu theo principal, tính compensation, approval, ledger, checkpoint, trace và output contract.

Phụ trách tích hợp ba shape của nhóm, bonus B3 về verifier trước thao tác hoàn tiền và UI demo offline. Bài chính, thí nghiệm B3 và bằng chứng benchmark được trình bày thành các khu vực riêng trong UI.

## 3. Đóng góp cụ thể

| Phần đóng góp | Commit dẫn chứng | Nội dung |
| --- | --- | --- |
| Workflow | `2fbe693` | `Implement deterministic workflow and host integration regressions` |
| Integration | `ede52b8` | `intergration`: tích hợp code nhóm, test ba shape và bằng chứng benchmark/crash |
| Bonus B3 | `27392c9` | `bonus`: verifier, fixture đối kháng, test và báo cáo B3 |
| UI demo | `b374e95` | `add demo ui`: dashboard offline, runner cách ly và test API |

Workflow thực hiện các bước Python cố định: `get_claim_view` → kiểm tra mã đơn → `lookup_order` theo principal → `compute_compensation` → `issue_refund` khi quote dương → `finish`. Claim không tồn tại trả `failed`; thiếu mã đơn trả `needs_info`; đơn không tìm thấy hoặc ngoài phạm vi principal trả `escalated`; quote bằng 0 trả `denied`. Host từ chối approval trả `denied`, conflict số tiền trả `failed`, host chấp nhận trả `resolved`.

Tiền được tính từ order và policy hiện hành, không lấy từ câu chữ trong ticket. Workflow không gọi model, nên có thể đo hành vi xác định và chi phí tool mà không thêm chi phí model. Mọi thao tác đọc nghiệp vụ và yêu cầu ghi refund đều được cộng vào `Budget`.

Quote đầy đủ được truyền vào host. Host kiểm approval của đúng claim, áp trần theo đơn và trừ phần đã hoàn trong transaction. Với C-014, proposal là 150.000 VND và effect là 120.000 VND; workflow không trừ trước 30.000 VND. Với C-013, quote 35.000 VND vẫn được chuyển tới host để ghi audit từ chối khi đơn đã được hoàn đủ.

Tham số `crash_at` được chuyển nguyên vẹn cho `issue_refund`; `InjectedCrash` được truyền ra ngoài. Kết nối SQLite luôn đóng trong `finally`. Ledger và audit của host bảo đảm retry/resume không tạo refund trùng.

Các nhánh kết thúc dùng `common.finish()` để lấy effect và audit từ database, tạo `RunResult` và ghi trace trong lần chạy hiện tại. Trace chỉ ghi trạng thái tìm claim, kết quả kiểm quyền đọc đơn, quote, yêu cầu refund, kết quả host và quyết định cuối. Không ghi ticket, principal, claim/order thô, header, secret, số điện thoại, địa chỉ, tên hàng hay ghi chú nội bộ. Trace được lưu trước khi gọi host để vẫn có bằng chứng nếu xảy ra crash.

Bổ sung `src/tests/test_workflow_integration.py` gồm 28 ca: injection trong ticket, trần theo đơn, approval không tồn tại và approval sai claim, conflict sau commit, thay thế trace cũ cho claim không tồn tại và 20 tổ hợp crash/seed qua cả ba vị trí `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`. Mỗi ca crash đều kiểm tra resume rồi retry vẫn chỉ có một effect và một audit committed. Các test tích hợp thuộc cổng pytest mặc định để kiểm tra lại khi ghép các shape của nhóm.

Tích hợp workflow, single và orchestrator qua các API host chính thức; ba shape không phụ thuộc module bổ sung ngoài tập file mà grader nhận. Single dùng `run_react` giới hạn 8 bước với tool chỉ đọc, tính quote bằng code và chỉ gọi host ghi refund sau khi vòng lặp hoàn tất. Chi phí yêu cầu refund được tính vào Budget theo cùng quy ước ở cả ba shape.

Bổ sung `src/tests/test_shapes_integration.py` gồm 17 ca: chạy từng shape khi không có module ledger bổ sung, đổi shape trên cùng database mà vẫn một refund, crash/resume ở ba vị trí trên cả ba shape, giới hạn ReAct và chặn ghi tiền khi vòng lặp chạm trần. Thông tin thành viên được hợp nhất trong `TEAM.md`, giữ thông tin liên hệ và vai trò của các thành viên.

Triển khai bonus B3 tại `src/bonus/swarm_verified.py`: giữ luồng swarm, thêm verifier đọc lại dữ liệu đơn có kiểm quyền và tính lại quote tối đa một lần trước khi ghi tiền. Bổ sung 12 claim đối kháng với nhãn khai báo theo luật nghiệp vụ, 101 test trong `src/tests/test_bonus_swarm_verified.py` và script tái lập benchmark/safety `src/bonus/evaluate.py`. Kết quả và giới hạn được trình bày trong [báo cáo bonus B3](bonus_report.md).

Xây dựng UI demo tại `src/demo_ui/`, khởi động bằng `demo.cmd` ở gốc repo. UI có ba khu vực: bài chính so sánh bốn kiến trúc, bonus B3 minh họa quote trước/sau verifier, và bằng chứng với biểu đồ cùng JSON gốc. Mỗi yêu cầu demo chạy shape thật trong subprocess với database và trace tạm riêng; retry/resume trong cùng kịch bản dùng chung ledger. UI không ghi đè báo cáo nộp bài và chỉ hiển thị dữ liệu đơn trong phạm vi được phép. Bổ sung 15 test API tại `src/tests/test_demo_ui.py`, chế độ trình chiếu, phát lại trace và dàn ý demo 5 phút trong [DEMO.md](../../DEMO.md).

## 4. Bằng chứng

Môi trường kiểm chứng: Windows AMD64, Python 3.14.3, pytest 8.4.2.

Các lệnh chạy trong `src/`, dùng Python của virtualenv:

```powershell
.\.venv\Scripts\python.exe -m lab8.smoke
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp ".venv/pytest-tmp-$([guid]::NewGuid().ToString('N'))"
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -p no:cacheprovider --basetemp ".venv/pytest-tmp-$([guid]::NewGuid().ToString('N'))"
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
```

| Kiểm chứng | Kết quả |
| --- | --- |
| Smoke | `lab8.smoke pass` |
| Cổng host, tích hợp, bonus và UI | 220 passed, 248 deselected |
| Ma trận student của cả bốn shape | 248 passed, 220 deselected |
| Test cá nhân bổ sung | 161 passed: 28 ca workflow, 17 ca tích hợp ba shape, 101 ca B3, 15 ca API demo |
| Crash suite tham chiếu | 20/20 |

Benchmark được công cụ sinh tại [src/reports/benchmark.json](../../src/reports/benchmark.json), trên 14 claim public và seed `11,22,33,44,55`, database mới cho mỗi trial. Số liệu của workflow:

| Metric | Giá trị |
| --- | --- |
| Trial pass | 70/70 |
| Pass rate / pass^5 | 1.0 / 1.0 |
| Seed min–max / variance | 1.0–1.0 / 0.0 |
| Cost/success mô phỏng | 34,285714 VND |
| Mean / p95 steps | 5,071429 / 6 |
| Mean model calls | 0 |
| Mean tool calls | 3,428571 |

| Shape | Trial pass | Pass rate | Pass^5 | Cost/success mô phỏng (VND) |
| --- | --- | --- | --- | --- |
| workflow | 70/70 | 1,0 | 1,0 | 34,285714 |
| single | 70/70 | 1,0 | 1,0 | 35,422857 |
| orchestrator | 70/70 | 1,0 | 1,0 | 43,571429 |
| swarm | 69/70 | 0,985714 | 0,928571 | 49,566957 |

Trial fail của swarm là C-002 tại seed 55, tương ứng điểm yếu tham chiếu được mô tả trong đề. Ma trận student kiểm tra riêng hành vi fail kỳ vọng này nên vẫn có 248 test pass. Crash suite `reports/crash.json` dùng swarm tham chiếu; crash/resume của ba shape nhóm viết được kiểm tra thêm trong ma trận student và test tích hợp.

Run id dẫn chứng: `R-workflow-C-001-s11` (refund hợp lệ), `R-workflow-C-002-s55` (không tin số ngày trong ticket), `R-workflow-C-013-s11` (đã hoàn đủ), `R-workflow-C-014-s11` (chỉ ghi phần chênh). JSON benchmark được sinh bằng lệnh, không chỉnh tay.

Bằng chứng B3: [bonus_public.json](../../src/reports/bonus_public.json) ghi swarm_verified đạt 70/70 trial, [bonus_adversarial.json](../../src/reports/bonus_adversarial.json) ghi 60/60 trial; [bonus_safety.json](../../src/reports/bonus_safety.json) ghi 10 lần verifier can thiệp và crash bổ sung 15/15 cho biến thể. Trace minh họa `R-swarm_verified-C-002-s55` cho thấy quote 20.000 VND được sửa về 0 trước khi ghi tiền.

Bằng chứng UI: test `test_bonus_demo_shows_real_before_and_after_without_changing_reports`, `test_demo_crash_and_resume_use_same_ledger` và `test_demo_requests_start_with_independent_databases` kiểm kết quả thật, không làm thay đổi benchmark và cách ly từng yêu cầu. Kiểm tra trên trình duyệt xác nhận hiển thị đúng hai hướng sửa quote, bảng crash/resume/retry, số liệu đối kháng 54/60 so với 60/60, chế độ trình chiếu và bố cục màn hình nhỏ.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc tài liệu, triển khai workflow, tích hợp code nhóm, xây dựng bonus B3 và UI demo, bổ sung test và chạy các lệnh kiểm chứng ở mục 4. Bằng chứng kiểm tra gồm đối chiếu với contract, luật nghiệp vụ, ma trận public, truy vấn effect/audit trong test, benchmark do công cụ của lab tạo và kiểm tra UI trên trình duyệt. Thông tin này ghi nhận kiểm chứng tự động; không thay cho việc thành viên tự chạy lại và giải thích code khi được hỏi.

## 6. Tự đánh giá

Workflow thể hiện mức tự chủ thấp: code quyết định luồng và số tiền, host quyết định quyền ghi. Kết quả public cho thấy hành vi ổn định trên năm seed và các test crash/resume bảo toàn một refund. Kết quả này có phạm vi dữ liệu public và các test tích hợp đã nêu; không suy ra điểm hidden hay quyết định kiến trúc chung của nhóm. Chi phí là mô phỏng, latency là `unavailable`; lab không sử dụng model sản xuất.

B3 cho thấy bước kiểm chứng có thể sửa lỗi dữ kiện của swarm nhưng tăng chi phí so với workflow trên các corpus đã đo. UI giúp giải thích ranh giới quote/tiền thực hoàn và minh họa bằng chứng; UI không phải một kiến trúc mới hay bằng chứng về điểm hidden. Điểm bonus phụ thuộc các điều kiện chấm riêng của đề.
