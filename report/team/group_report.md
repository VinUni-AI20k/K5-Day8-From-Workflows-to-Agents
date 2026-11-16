# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Random
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 5fb3b5d

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape C — Orchestrator và investigator chỉ đọc

Orchestrator đọc claim bằng `get_claim_view`. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`, không giao việc cho investigator và không ghi refund. Các nhánh trả kết quả đều dùng `finish()` để ghi trace và lấy bằng chứng ledger từ host.

Handoff được tạo bằng `make_handoff`, với `facts` rỗng và ba tool được phép: `lookup_order`, `lookup_policy`, `compute_compensation`. Không chuyển ticket, parent context, secret hoặc raw headers vào handoff. Investigator chạy qua `run_readonly_investigators` và chỉ được gọi tool đọc. Quyền sở hữu đơn được kiểm qua `lookup_order`; đơn không tìm thấy hoặc ngoài phạm vi principal trả `escalated`.

Số tiền lấy từ `compute_compensation` trên dữ kiện đơn và policy hiện hành, không lấy từ lời kể trong ticket. Quote bằng 0 trả `denied`. Quote dương được truyền đầy đủ vào `durability.issue_refund`; host kiểm approval, trần theo đơn và idempotency. Orchestrator không tự trừ tiền đã hoàn. Host từ chối trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`. Tham số `crash_at` được chuyển cho host và `InjectedCrash` được phép truyền ra ngoài; kết nối luôn đóng trong `finally`.

MockLLM chỉ soạn phản hồi từ status và proposal đã được code quyết định. Trace gồm `handoff`, `investigator`, `quote`, `decision` tùy nhánh; event investigator chỉ ghi visibility, reason và số policy. Không dump claim, order hoặc toàn bộ kết quả investigator.

Phần mô tả workflow và single: chờ thành viên phụ trách bổ sung.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

Lệnh (chạy trong `src/`): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`. Điều kiện cố định: 14 claim public (C-001…C-014), seed 11/22/33/44/55, MockLLM, `config/pricing.yaml`, as_of 2026-11-15, SQLite mới cho mỗi trial. 70 trial mỗi shape.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND, mô phỏng) | Mean / p95 steps | Mean model calls | Mean tool calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.46 | 4.43 / 5 | 0.64 | 2.79 |
| B single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.47 | 3.79 / 4 | 0.93 | 2.79 |
| C orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.44 | 3.71 / 4 | 1.00 | 4.64 |
| D swarm (tham chiếu) | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 | 4.66 |

Nhận xét:

- Ba shape nhóm viết pass toàn bộ 70 trial, không dao động giữa các seed. Pass rate không phân biệt được chúng; khác biệt nằm ở cost và mức tự chủ.
- Swarm fail đúng một trial, `R-swarm-C-002-s55` (`status resolved != denied`): ở seed 55 swarm tin số ngày trễ trong ticket (5 ngày) thay vì `delay_days` (2 ngày). Đây là điểm yếu cố ý của shape tham chiếu, và là lý do swarm có variance khác 0.
- Orchestrator tốn hơn workflow/single khoảng 67% cost/success vì investigator gọi thêm tool (4.64 so với 2.79 tool call/trial) mà không thêm trial đúng. Ablation chi tiết ở `report/team/research_card.md`.
- Steps là số event trong trace, nên workflow nhiều steps hơn chỉ vì ghi trace chi tiết hơn, không phải vì tốn hơn.

**Crash safety:** `python -m lab8.crash_test --count 20 --out reports/crash.json` cho `crash_safety` = **20/20** (`src/reports/crash.json`).

**Kiểm thử:** cổng host `python -m pytest -q` xanh (65 passed); ma trận student `python -m pytest -q -m student -o addopts=` đạt 289 passed, gồm 62 test T01–T14 cho mỗi shape và 40 test bất biến ledger (`src/tests/test_ledger_shapes.py`, 10 test × 4 shape): crash ở cả 3 điểm rồi resume, retry nhiều lần, approval thiếu/thu hồi/mượn claim khác, hai claim cùng đơn, và cả 14 claim chạy trên một DB chung.

**Tự kiểm hidden (`student_drop/`):** chưa có, sẽ bổ sung khi giảng viên phát thư mục.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

Khi kiểm tra phần orchestrator trên máy hiện tại, `python -m lab8.smoke` báo: `Python 3.10.0 quá cũ. Cần Python 3.11+`. Các lệnh pytest vẫn chạy được: test student riêng orchestrator đạt 62 passed; test mặc định gồm test host và ba ca kiểm thử bảo mật mới đạt 57 passed. Đây là kết quả trên Python 3.10, chưa thay thế xác nhận môi trường yêu cầu. Cần chạy lại smoke và test trên Python 3.11–3.13 trước khi nộp.

Test mới tại `src/tests/test_orchestrator_security.py` kiểm tra ticket chứa chỉ dẫn giả và canary không làm thay đổi quote hoặc xuất hiện trong handoff, trace, kết quả và stdout/stderr. Hai ca còn lại kiểm tra claim không tồn tại và thiếu mã đơn không được giao cho investigator nhưng vẫn có trace hợp lệ. Các test mới dùng thư mục tạm để tách artifact giữa các lần chạy.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

### Đỗ Văn Ngọc — Single agent

- Phụ trách `src/lab8/shapes/single.py`: vòng ReAct tối đa 8 bước với công cụ chỉ đọc; code kiểm tra claim/order, lấy quote từ dữ liệu đã xác minh và gọi host để hoàn refund.
- Thêm test `src/tests/test_single_agent.py::test_single_uses_order_facts_instead_of_ticket_delay` để kiểm tra agent bỏ qua số ngày trễ trong ticket, không ghi refund sai và trace đúng contract.
- Trạng thái xác minh: chưa chạy được test vì môi trường chưa có Python khả dụng; cần bổ sung kết quả thực tế trước khi chốt báo cáo.

### Nguyễn Trần Anh Khôi — Ledger + evaluation

- Viết `src/tests/test_ledger_shapes.py` (commit `ff49706`): 10 test bất biến ledger chạy qua cả 4 shape, dùng swarm làm đối chứng để chứng minh bản thân test đúng.
- Chạy crash suite và benchmark bằng lệnh chính thức, sinh `src/reports/crash.json` và `src/reports/benchmark.json`.
- Điền `report/team/decision_adr.md`, `report/team/research_card.md` (R1, ablation single → orchestrator) và mục 4 của báo cáo này.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
