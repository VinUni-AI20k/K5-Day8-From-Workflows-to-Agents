# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: GiCungDuoc
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): `<cập nhật ở CP5>`

## 2. Mục tiêu và cách tiếp cận

### Mục tiêu bài toán
Bài lab mô phỏng quy trình xử lý claim hoàn phí vận chuyển và đền bù hàng hỏng của **LogiX-VN** trên bốn kiến trúc (`workflow`, `single`, `orchestrator`, `swarm`) dùng chung chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult` và cùng `MockLLM` cố định theo seed. Mục tiêu của nhóm là:
1. Tuân thủ chặt ranh giới code/model: toàn bộ logic tính tiền (`compute_compensation`), kiểm tra policy hiện hành (`is_current=1`, `effective_date <= 2026-11-15`), chống prompt injection từ nội dung ticket, kiểm tra approval và idempotency/trần hoàn tiền theo đơn do **code và host (`durability.issue_refund`)** quyết định.
2. Đảm bảo tuyệt đối 3 điều kiện must-pass: không refund khi thiếu approval hợp lệ (`approval_bypass_count == 0`), không rò rỉ `CANARY_SECRET_*` hay PII trong trace/stdout (`secret_leak_count == 0`), và an toàn khi crash (`20/20` crash suite).
3. Đo lường khách quan (pass rate, pass^5, seed variance, cost/success) trên cùng corpus và seed để chọn kiến trúc **ít tự chủ nhất mà vẫn hoàn thành tốt nhiệm vụ**.

### Phân công và thứ tự triển khai
Nhóm 5 thành viên chia vai chuyên biệt theo kiến trúc và kiểm thử:
- **Phạm Quốc Huy (Lead & QA Integration):** quản lý Git/CI, giữ cổng host (`pytest -q`) luôn xanh, chuẩn hóa contract `RunResult`/`Trace v1` qua `src/tests/test_student_integration.py` và chạy `check_submission`.
- **Trần Tùng Lâm (Shape A — Workflow Lead):** triển khai `workflow.py` (tuần tự tất định, không dùng `REFERENCE_WEAKNESS`) làm baseline ít tự chủ nhất.
- **Đặng Đức Minh (Shape B — Single ReAct):** triển khai `single.py` (vòng lặp ReAct tối đa 8 bước, chỉ dùng read-tools, chống prompt injection).
- **Nguyễn Thành Tâm (Shape C — Orchestrator & Security Lead):** triển khai `orchestrator.py` (handoff allowlist `handoff.v1`, investigator read-only, kiểm soát zero-leak trace).
- **Trịnh Gia Huy (Durability, Eval & Benchmark Lead):** kiểm thử T11/T12 và `crash_test` 20/20, chạy `benchmark.json`, phân tích số liệu điền `decision_adr.md` và `research_card.md`.

Thứ tự thực hiện bám sát 5 checkpoint: CP1 (cài đặt môi trường, đọc contract, viết test tích hợp giữ cổng host) → CP2–CP3 (hoàn thiện lần lượt 3 shape `workflow`, `single`, `orchestrator` kèm handoff và `crash_at`) → CP4 (chạy crash suite 20/20 và rà soát bảo mật/trace) → CP5 (chạy benchmark 4 shape × 5 seed, hoàn thiện ADR, research card và `check_submission` đạt `0 FAIL`).

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
