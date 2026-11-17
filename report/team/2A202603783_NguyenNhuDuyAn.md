## 2A202603783_NguyenNhuDuyAn

### Phần việc phụ trách

- Shape C `orchestrator` + investigator chỉ đọc: `src/lab8/shapes/orchestrator.py`
- Handoff sanitize qua allowlist bằng `lab8.handoff.make_handoff`
- Test bảo mật handoff/trace: `src/tests/test_shape_orchestrator.py`

### Đóng góp cụ thể

- Cài 3 nhánh quyết định theo `docs/contracts.md`: `needs_info` (thiếu `order_id`), `escalated` (order không thấy/ngoài principal), `denied` (quote ≤ 0 hoặc host từ chối).
- Investigator chỉ nhận `lookup_order`, `lookup_policy`, `compute_compensation`; không có `issue_refund`.
- Truyền **quote đầy đủ** vào `durability.issue_refund` để host tự trừ phần đã hoàn của claim trước (T13, T14).
- CP3: truyền `crash_at` xuyên xuống `issue_refund`, không bắt `InjectedCrash`; flush trace trước khi raise.
- Trace chỉ ghi handoff đã sanitize (`safe_dump`), không ghi claim row/order row thô.

### Bằng chứng

- `pytest -q -m student -o addopts= -k orchestrator` → **62 passed**.
- `pytest -q tests/test_shape_orchestrator.py` → **3 passed** (sanitize field, từ chối write tool, trace không chứa `CANARY_SECRET_*`).
- `pytest -q` (cổng host) → **57 passed**.
- File shape và test nằm trong commit của nhánh nộp bài.
