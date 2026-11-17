# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape A — `workflow` (`src/lab8/shapes/workflow.py`)

...

### Shape B — `single` (`src/lab8/shapes/single.py`)

...

### Shape C — `orchestrator` (`src/lab8/shapes/orchestrator.py`)

- **Luồng thực thi:**
  1. Đọc thông tin claim qua `get_claim_view(conn, claim_id)` (chỉ lấy `claim_id`, `principal_id`, `order_id`, `ticket`). Nếu không tìm thấy claim → ghi event `error` và trả `status="failed"` (`error_reason="unknown_claim"`); nếu thiếu `order_id` → gọi `complete(..., purpose="draft")` và trả `status="needs_info"` (`error_reason="missing_order_id"`).
  2. Gọi `complete(budget, seed=seed, purpose="plan", prompt=claim_view["ticket"])` cho bước lập kế hoạch, sau đó dựng gói giao việc bằng `lab8.handoff.make_handoff(...)` và chạy `run_readonly_investigators(conn, budget, handoff, principal_id=...)`.
  3. Kiểm tra `order_view.get("visible")` từ kết quả `lookup_order`: nếu không hợp lệ hoặc ngoài `principal_id` → trả `status="escalated"`.
  4. Lấy báo giá từ kết quả `compute_compensation` (tính từ dữ liệu có cấu trúc `order_view["order"]` và policy hiện hành, bỏ qua số ngày trễ tự khai trong `ticket`), gọi `complete(..., purpose="draft", prompt=f"proposal={proposal}")`.
  5. Nếu `proposal <= 0` → trả `status="denied"` (không gọi `issue_refund`). Nếu `proposal > 0` → gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` với **quote đầy đủ**; nếu gặp `InjectedCrash` thì ghi event `crash`, gọi `trace.write()` rồi re-raise để giữ đúng hành vi kiểm thử crash; nếu host từ chối hoặc có `conflict` → trả `denied`/`failed`, thành công → trả `resolved`. Mọi nhánh return đều đi qua `common.finish(...)`.
- **Ranh giới Code / Model & Orchestrator / Investigator:**
  - Investigator chỉ được cấp 4 read-only tools (`lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`), hoàn toàn không có quyền gọi write tool (`issue_refund`, `append_audit`).
  - `MockLLM` (`complete`) chỉ được dùng để mô phỏng chi phí lập kế hoạch (`plan`) và soạn phản hồi (`draft`); mọi quyết định về tiền (`compute_compensation`), quyền sở hữu đơn (`principal_id`), approval, idempotency và trần hoàn tiền theo đơn do code và host (`durability.issue_refund`) quyết định. Orchestrator luôn truyền **quote đầy đủ** để host tự trừ các khoản đã hoàn trước đó trên cùng đơn.
- **Sanitize Handoff & Bảo vệ Trace (`Trace contract v1`):**
  - `make_handoff` và `sanitize` trong `src/lab8/handoff.py` lọc cứng theo allowlist `ALLOWED_FIELDS` và `FACT_KEYS`, truyền `facts={}` (không đưa claim row thô vào `facts`), loại bỏ field ngoài danh sách và ném `HandoffError` nếu phát hiện `CANARY_SECRET_`, `parent_secret`, `raw_headers` hoặc write tool.
  - Trace được ghi mới theo `run_id = make_run_id("orchestrator", claim_id, seed)` ở mọi nhánh kết thúc, gồm các event đã sanitize: `handoff`, `investigator` (`order_view` chỉ gồm 7 trường `ORDER_FIELDS`, `lookup_refund_history`, và `policy_count`), `quote`, và `decision`/`error`/`crash`. Cố ý **không** đọc hoặc ghi vào trace các trường nhạy cảm: `parent_secret`, `raw_headers_json`, SĐT (`phone`), địa chỉ (`address`), tên mặt hàng (`item`) và ghi chú nội bộ (`internal_note`).
- **Kiểm thử bổ sung:** Đã thêm `test_orchestrator_sanitizes_handoff_and_protects_trace` và `test_orchestrator_passes_full_quote_and_survives_crash` trong `src/tests/test_handoff_secret.py` (kiểm tra allowlist handoff, chặn rò rỉ secret/PII, tin order row thay vì ticket ở seed 55, truyền quote đầy đủ ở `C-014`, và phục hồi đúng 1 dòng ledger sau `InjectedCrash` ở `C-012`).

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
