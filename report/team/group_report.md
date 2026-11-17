# Báo cáo nhóm — Lab 8 LogiX-VN

Bản hiện tại tổng hợp phần Single agent đã triển khai. Các phần kiến trúc còn lại, benchmark và quyết định cuối sẽ được bổ sung sau khi nhóm tích hợp. Báo cáo hoàn chỉnh tối đa 5 trang ngoài phụ lục.

## 1. Thông tin nhóm

- Tên nhóm: ABC
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): _(điền khi nộp)_

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý yêu cầu hoàn phí của LogiX-VN theo bốn kiến trúc workflow, single agent, orchestrator và swarm tham chiếu. Các shape dùng chung dữ liệu, MockLLM, policy và host. Quote được tính từ order có cấu trúc cùng policy hiện hành. Host kiểm approval, trần hoàn tiền theo đơn và chống ghi trùng.

Phân công dự kiến cho 5 thành viên gồm workflow, single agent, orchestrator, safety và tích hợp, benchmark và tổng hợp báo cáo. Người phụ trách từng shape triển khai và kiểm thử riêng. Phần safety được kiểm tra theo từng shape hoàn thành, còn benchmark cuối chạy trên bản đã tích hợp.

## 3. Giải pháp

### Shape B — Single agent

`single.py` mở connection SQLite, khởi tạo `Budget` và `Trace`, rồi đọc claim bằng `get_claim_view`. Claim không tồn tại trả `failed`, thiếu mã đơn trả `needs_info`. Các nhánh còn lại chạy `run_react` với giới hạn 8 bước và `worker=True`.

Trong vòng đọc, callback `decide` dùng kết quả gần nhất để chọn `lookup_order`, sau đó chọn `compute_compensation`. Đơn ngoài phạm vi principal trả `escalated`. Quote được tính bằng code từ order và policy hiện hành. Nội dung “ignore policy”, số ngày do khách khai và điều khoản cũ trong ticket được xử lý như dữ liệu đầu vào không đáng tin cậy.

Sau vòng ReAct, quote bằng 0 trả `denied`. Với quote dương, code gọi `durability.issue_refund` và truyền quote đầy đủ cùng `crash_at`. Host kiểm approval, trần theo đơn và idempotency. Kết quả thành công trả `resolved`, bị từ chối trả `denied`, conflict trả `failed`. Ví dụ T14 có quote 150.000 VND và khoản hoàn trước 30.000 VND, host chỉ ghi thêm 120.000 VND.

Mọi kết quả trả qua `finish` để đồng bộ effect, audit count và trace. Khi crash, shape lưu sự kiện rồi ném lại `InjectedCrash`, cho phép kiểm tra resume trên cùng database.

### Budget và trace của Single

Mỗi lần gọi `decide` sử dụng `mock_llm.complete`, tự ghi nhận model call, token và chi phí trong `Budget`. Runtime cộng chi phí các tool được dispatch, còn lần đọc claim được cộng trực tiếp. Luồng có order hợp lệ thường có 3 lượt gọi MockLLM và 3 lần gọi tool. Lệnh host sau vòng lặp được hạch toán theo cách của swarm tham chiếu.

Trace ghi các sự kiện `tool`, `model`, `action`, `order_scope`, `quote`, `host`, `decision` và `crash`. Mỗi sự kiện sử dụng payload chọn lọc. Ticket, nguyên claim row, secret, header và thông tin cá nhân của order được loại khỏi nội dung ghi log.

### Shape A — workflow

Pipeline cố định trong code, không ReAct/handoff. Đọc claim bằng `get_claim_view`; thiếu `order_id` → `needs_info`; `lookup_order` không visible → `escalated` (không đưa PII vào trace). Quote lấy từ order qua `compute_compensation` — bỏ qua số ngày trong ticket. Quote 0 → `denied` (không gọi host). Quote > 0 → `issue_refund` với **full quote** và `crash_at`; host tự kiểm approval và trần theo đơn. Model không chọn số tiền và không commit refund. Trace (`lab8.trace.Trace`) ghi mọi nhánh return.

### Shape B — single

...

### Shape C — orchestrator

...

## 4. Kết quả

### Kiểm thử hiện có

| Phạm vi | Kết quả đã chạy |
| --- | --- |
| Test bổ sung trong `tests/test_single.py` | 13 passed |
| Ma trận student riêng shape Single | 62 passed, 186 deselected |
| Bộ host mặc định, gồm test bổ sung | 67 passed, 248 deselected |
| Crash suite của host và swarm tham chiếu | 20/20, xem `src/reports/crash.json` |

Các test bổ sung kiểm tra đầu vào, quyền sở hữu, ticket đối kháng, quote đầy đủ, giới hạn 8 bước, chặn tool ghi, cả ba điểm crash/resume và conflict số tiền. Ma trận student kiểm tra Single trên các seed public `11,22,33,44,55`, gồm retry T11 và crash T12.

Các lệnh tái lập phần Single, chạy từ `src`, sử dụng môi trường Python 3.12.2 trên Windows.

```powershell
.\.venv\Scripts\python.exe -m pytest -q tests/test_single.py
.\.venv\Scripts\python.exe -m pytest -q tests/test_public_matrix.py -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"
.\.venv\Scripts\python.exe -m pytest -q
```

Run id minh họa là `R-single-C-014-s11`. Test T14 xác nhận quote 150.000 VND, effect 120.000 VND và một audit committed. Trace nằm trong thư mục cục bộ `src/traces/` đã được gitignore.

### Benchmark và lựa chọn kiến trúc

Chờ chạy benchmark đủ 4 shape trên cùng corpus và seed. Bảng cuối cần lấy pass rate, pass^5, seed min–max, variance, cost/success và mean/p95 steps từ `src/reports/benchmark.json`. Kiểm tra hidden và ablation chờ bổ sung theo tiến độ nhóm.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Khi cài dependency, sandbox chặn kết nối tải package với lỗi `WinError 10013`. Lệnh `python -m pip install -r requirements.txt` được chạy lại với quyền truy cập mạng phù hợp và cài thành công. Smoke test pass, `pip check` báo `No broken requirements found`.

Lệnh lọc `pytest -k single` chọn thêm test của shape khác vì tên test chung có chuỗi `single_run`. Biểu thức `single and not workflow and not orchestrator and not swarm` giới hạn đúng 62 test student của Single. Các lỗi từ shape còn là stub được xác định qua tham số shape trong tên test.

## 6. Tổng hợp đóng góp

Đào Văn Hiệp (2A202603813) phụ trách triển khai `src/lab8/shapes/single.py`, bổ sung `src/tests/test_single.py` và nội dung ReAct, budget, kiểm thử trong báo cáo này. Báo cáo cá nhân nằm tại `report/team/2A202603813_DaoVanHiep.md`. Commit code và test là `1b1469ce65b345666314cee04f4528b497e8ebc8`, trên nhánh `hiep-sigle-agent`.

Nhóm cần bổ sung danh tính, commit và test của từng người vào bảng đóng góp trong `TEAM.md`. Các phần đóng góp workflow, orchestrator, safety và benchmark chờ người phụ trách xác nhận.

## 7. Hạn chế và hướng cải thiện

MockLLM cung cấp hành vi mô phỏng cố định theo seed. Chi phí được tính bằng VND mô phỏng theo config, latency là `unavailable`. Hiện chưa có benchmark tích hợp hoặc kết quả hidden để chốt lựa chọn kiến trúc.

Ở Single hiện tại, callback Python chọn tool theo observation, còn chuỗi trả về của MockLLM chưa được phân tích thành action. Yêu cầu model lựa chọn tool mới được mô phỏng qua callback và lượt gọi model. Nhóm cần đối chiếu giới hạn này với yêu cầu kiến trúc khi hoàn thiện bài, đồng thời đánh giá lại nếu thay đổi cơ chế chọn action.

## 8. Tài liệu tham khảo

- Quy tắc nghiệp vụ và nguồn dữ liệu chuẩn được mô tả trong [business_rules.md](../../docs/business_rules.md).
- Output contract và trace contract được mô tả trong [contracts.md](../../docs/contracts.md).
- Ranh giới giữa các shape và host được mô tả trong [architecture.md](../../docs/architecture.md).
- Công thức benchmark được mô tả trong [metrics.md](../../docs/metrics.md).
- Quy định AI, bảo mật và đóng góp được mô tả trong [RULES.md](../../RULES.md).
