# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Bài toán: xử lý claim hoàn phí vận chuyển của LogiX-VN theo bốn kiến trúc có cùng chữ ký `run_claim`, rồi chọn kiến trúc ít tự chủ nhất mà vẫn đạt yêu cầu. Nhóm coi ba thứ là bất biến ở mọi shape: tiền do `compute_compensation` tính từ order row và policy hiện hành; chỉ host (`durability.issue_refund`) được ghi ledger, kiểm approval, trần theo đơn và idempotency `refund:{claim_id}`; chữ trong ticket là dữ liệu người dùng, không phải lệnh hay nguồn số liệu.

Thứ tự làm: đọc contract và `swarm_reference.py` (CP1) → workflow trước làm baseline tất định → single (ReAct, tool đọc) và orchestrator (handoff + investigator read-only) song song → nối `crash_at` vào host ở cả ba shape (CP3) → crash suite, benchmark, ADR (CP4–CP5).

## 3. Giải pháp

| Shape | Đọc gì | Ai quyết định | Gọi host |
| --- | --- | --- | --- |
| A `workflow` | `get_claim_view` → `lookup_order` (theo principal của claim) → `compute_compensation` | Code Python cố định. MockLLM chỉ soạn chữ trả lời (1 lần) | Quote > 0: `issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=...)` |
| B `single` | Vòng `run_react` tối đa 8 bước; `decide` chỉ chọn tool đọc theo thứ tự claim → order → quote | `decide` dừng bằng `final`; vượt step cap → `failed` | Sau vòng lặp, code của shape gọi `issue_refund` với quote đầy đủ và `crash_at` |
| C `orchestrator` | Orchestrator đọc claim view; dựng handoff bằng `make_handoff` với `facts={}` và allowlist 4 tool đọc; `run_readonly_investigators` tra order, policy, quote, refund history | Orchestrator (code) quyết từ kết quả investigator; model chỉ plan và draft | Orchestrator gọi `issue_refund` với quote đầy đủ và `crash_at` |

Ranh giới code / model: không shape nào để MockLLM chọn số tiền, approval hay gọi ghi. Cả ba đều truyền **quote đầy đủ** cho host (host tự trừ phần đơn đã được hoàn, T13/T14), không bắt `InjectedCrash`, và flush trace an toàn trước khi gọi host để run crash vẫn để lại trace.

Handoff (orchestrator): không mang ticket, parent context hay secret; `facts` rỗng, investigator tự tra bằng tool đọc trong allowlist. Trace ghi handoff đã qua `safe_dump`.

Trace (contract v1, `lab8.trace.Trace`): ghi kết quả tool đã lọc (found, visible, reason, order view allowlist), quote (amount, reason, clause_ids), kết quả host (ok, reason, conflict) và `decision`. Không ghi ticket, claim/order row thô, `principal_id`, SĐT, địa chỉ, tên hàng, ghi chú nội bộ. Mọi nhánh return đi qua `finish()`.

## 4. Kết quả

Bộ public, 14 claim × 5 seed (`11,22,33,44,55`), MockLLM, giá mô phỏng — nguồn `src/reports/benchmark.json`:

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean / p95 steps | Model call/trial |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.80 | 4.43 / 5 | 1.00 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 29.29 | 7.86 / 9 | 3.79 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.12 | 4.29 / 5 | 1.93 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 |

- Swarm fail đúng 1 trial: `R-swarm-C-002-s55` (T02, tin "trễ 5 ngày" trong ticket thay vì `delay_days` = 2), trả `resolved` thay vì `denied`.
- Crash safety: `20/20` (`src/reports/crash.json`).
- Ma trận student: 248 passed (4 shape × 62); cổng host `python -m pytest -q`: 66 passed.
- Chưa có `student_drop/` nên chưa tự kiểm hidden.

Quyết định kiến trúc: **workflow** — xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation (R1: thêm investigator làm cost/success ×1.98, pass không đổi): xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **T12 của `single` fail:** `python -m pytest -q -m student -o addopts=` ra `1 failed, 247 passed` với thông báo `crash did not fire: pass crash_at to durability.issue_refund and do not catch InjectedCrash`. Nguyên nhân: `single.run_claim` bỏ `crash_at` (`del crash_at`). Sửa: truyền `crash_at` xuống `_run` và vào `issue_refund`, ghi `host_call` rồi flush trace trước khi gọi host. Sau sửa: 248 passed.
- **Trace khi crash:** run bị crash không đi qua `finish()`, nên nếu không flush trước thì không có artifact. Cả ba shape ghi trace đã sanitize trước khi gọi host.
- **Dễ trừ tiền hai lần ở T13/T14:** đọc `lookup_refund_history` rồi tự trừ sẽ làm host trừ lần nữa. Nhóm giữ quy tắc: luôn truyền quote đầy đủ.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Corpus public chỉ 14 claim và cả ba shape nhóm viết đều chạm trần 1.000, nên benchmark public không phân biệt được chất lượng giữa chúng — quyết định dựa trên cost, số bước và độ tự chủ. Kết luận sẽ thay đổi nếu hidden có loại claim mà luật cố định không bao được, hoặc nếu workflow dưới 0.75 trên hidden. Hướng cải thiện: chạy tự kiểm trên `student_drop/` khi có, thêm test cho homoglyph và principal lẫn ở workflow.

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`, `docs/architecture.md` của repo lab.
- Google Research 2026, *Towards a Science of Scaling Agent Systems* (R1, thư viện tham khảo slide 68–69).
