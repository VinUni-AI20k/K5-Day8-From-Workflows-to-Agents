# Báo cáo cá nhân — 2A202603774_NguyenNgocNinh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Ngọc Ninh
- MSSV: 2A202603774
- Email: sevenminutes2311@gmail.com
- GitHub: sevenminutes2311-creator

## 2. Phần việc phụ trách

- Kiểm thử cổng policy, trần hoàn tiền theo đơn và các trường hợp biên: viết file test `src/tests/test_team_policy_gate.py` chạy trong cổng host (`python -m pytest -q`).
- Đánh giá định lượng 4 kiến trúc (`workflow`, `single`, `orchestrator`, `swarm`) từ dữ liệu `src/reports/benchmark.json` và `src/reports/crash.json`.
- Viết quyết định kiến trúc tại `report/team/decision_adr.md`, phiếu nghiên cứu & ablation tại `report/team/research_card.md` (chủ đề R2 — MAST failure taxonomy), báo cáo tổng hợp nhóm tại `report/team/group_report.md` và cập nhật bảng đóng góp trong `TEAM.md`.

## 3. Đóng góp cụ thể

- Commit `9e8f63a`: thêm bộ kiểm thử `src/tests/test_team_policy_gate.py` (12 test: 4 kịch bản × 3 shape `workflow`, `single`, `orchestrator`):
  - `test_missing_order_id_returns_needs_info_without_ledger_write`: kiểm tra `C-004` (thiếu `order_id`) trả `status = needs_info`, `proposal_amount = 0`, không phát sinh dòng mới trong `refund_ledger` và `committed_audit_count = 0`.
  - `test_order_already_fully_refunded_is_denied_with_policy_audit`: kiểm tra `C-013` (đơn `O-505` đã hoàn đủ `35.000` VND từ claim trước) trả `status = denied`, giữ nguyên `proposal_amount = 35000` (quote đầy đủ truyền vào host), có bản ghi `policy_denied` trong bảng `audit_events` và không tạo dòng mới trong `refund_ledger`.
  - `test_partial_prior_refund_pays_only_remaining_entitlement`: kiểm tra `C-014` (đơn `O-515` đã hoàn `30.000` VND phí ship, nay phát sinh hư hỏng đã xác minh với entitlement `150.000` VND) trả `status = resolved`, `proposal_amount = 150000` và ghi đúng phần chênh `120.000` VND vào `refund_ledger` kèm 1 audit `refund_committed`.
  - `test_expired_approval_and_approval_cap_enforced_by_host`: kiểm tra `C-007` (approval hết hạn → `denied`, `proposal_amount = 35000`, có audit `policy_denied`) và `C-008` (quote `35.000` VND nhưng approval chỉ duyệt `20.000` VND → `resolved`, `proposal_amount = 35000`, ledger ghi `20.000` VND).
- Quyết định kỹ thuật & phân tích kiến trúc:
  - **Chọn `workflow` trong `report/team/decision_adr.md`**: Cả ba shape `workflow`, `single`, `orchestrator` đều đạt `pass_rate = 1.000`, `pass^5 = 1.000`, `seed_variance = 0.0` trên 70 trial public, nhưng `workflow` có chi phí thấp nhất (`28.80` VND/success so với `39.08` VND của `single` và `57.14` VND của `orchestrator`), `mean_steps = 4.36` và ít tự chủ nhất.
  - **Phân tích lỗi MAST R2 trong `report/team/research_card.md`**: Thiết kế ablation giữ cố định MockLLM, bộ công cụ, 5 seed (`11, 22, 33, 44, 55`), 14 claim public và bảng giá, chỉ thay đổi topology. Chỉ ra nguyên nhân `swarm` fail ở `R-swarm-C-002-s55` (`pass_rate = 0.986`, `pass^5 = 0.929`, `seed_variance = 0.000816`) thuộc nhóm lỗi **Task Verification** trong taxonomy MAST (tin số ngày trễ 5 ngày trong ticket thay vì đối chiếu `delay_days = 2` của đơn `O-202` trong DB).
  - **Giải thích ranh giới bảo mật của Trace & Handoff**: Chứng minh vì sao chỉ ghi các trường allowlist (`claim`, `order` view, `quote`, `host`, `decision`, `handoff` đã sanitize) và cố ý loại bỏ `ticket`, `parent_secret`, `raw_headers`, `phone`, `address`, `internal_note`, `item_name`.

## 4. Bằng chứng

- Commit test kỹ thuật: `9e8f63a` (`src/tests/test_team_policy_gate.py`), commit báo cáo: `c8d9515`.
- Chạy cổng host kèm test mới (`python -m pytest -q`): `81 passed, 248 deselected` (tăng từ 69 lên 81 test xanh).
- Kiểm tra định dạng nộp bài (`python -m lab8.check_submission`): `0 FAIL`.
- Run id dẫn chứng:
  - `R-workflow-C-014-s11`: minh họa truyền quote đầy đủ `150.000` VND vào `durability.issue_refund` và host tự trừ `30.000` VND đã hoàn để ghi `120.000` VND.
  - `R-swarm-C-002-s55`: phản ví dụ ở `swarm` khi thiếu kiểm chứng dữ kiện ticket với DB (`status resolved != denied`).
- Các tài liệu hoàn thiện: `report/team/decision_adr.md`, `report/team/research_card.md`, `report/team/group_report.md`, `TEAM.md`.

## 5. Công cụ AI đã dùng

- Gemini (Antigravity): hỗ trợ rà soát yêu cầu trong `RUBRIC.md`, `SUBMISSION.md`, `docs/contracts.md`, viết kiểm thử `src/tests/test_team_policy_gate.py` và cấu trúc hóa các file báo cáo (`decision_adr.md`, `research_card.md`, `group_report.md`).
- Cách tự kiểm tra:
  - Chạy trực tiếp `.\.venv\Scripts\python.exe -m pytest -q` (81 passed) và `.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts=` (248 passed).
  - Đối chiếu từng con số trong `decision_adr.md`, `research_card.md`, `group_report.md` với `src/reports/benchmark.json` và `src/reports/crash.json`, kèm kiểm tra từng `expected` trong `src/data/public_claims.jsonl`.
  - Chạy `.\.venv\Scripts\python.exe -m lab8.check_submission` để xác nhận trình đọc tự động của giảng viên báo `0 FAIL`.

## 6. Tự đánh giá

- Làm tốt: hoàn thành đầy đủ bộ test kiểm chứng cổng policy và trần hoàn tiền theo đơn trên cả 3 shape (`test_team_policy_gate.py`), liên kết chặt chẽ số liệu thực nghiệm từ `benchmark.json` / `crash.json` với lý thuyết MAST (R2) và nguyên tắc chọn kiến trúc ít tự chủ nhất trong ADR.
- Hạn chế: đánh giá hiện tại dựa trên `MockLLM` (`latency = unavailable`) và bộ 14 claim public; nếu chạy trên model thực tế hoặc bộ dữ liệu mở rộng có nhiều nhiễu ngôn ngữ tự nhiên hơn, cần đo thêm chi phí retry và tỷ lệ lỗi định dạng tool call.
