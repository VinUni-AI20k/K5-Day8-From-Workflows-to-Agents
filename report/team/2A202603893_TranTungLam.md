# Báo cáo cá nhân — MSSV_HoTen

## 1. Thông tin thành viên

- Họ tên: Trần Tùng Lâm
- MSSV: 2A202603893
- Email: lamtt22004@gmail.com
- GitHub: lamtt262004

## 2. Phần việc phụ trách

Shape A (workflow tất định): `src/lab8/shapes/workflow.py`, bộ test `src/tests/test_student_workflow.py` và mục "Shape A: Workflow" trong phần 3 của `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- Viết lại stub `run_claim` thành 5 bước cố định: `get_claim_view` → kiểm `order_id` → `lookup_order` → `compute_compensation` → `durability.issue_refund`.
- Truyền quote đầy đủ vào host thay vì tự trừ phần đã hoàn. Cách này giúp T13 và T14 đúng mà không phải xử lý trần theo đơn ở phía shape.
- Chuyển `crash_at` cho host. Khi gặp `InjectedCrash`, shape ghi trace rồi ném lại lỗi; các exception khác trả về `failed` để `run_claim` không ném lỗi ra ngoài.
- Trace chỉ ghi field đã qua allowlist, không ghi ticket. Lý do: ticket là dữ liệu do người dùng nhập, có thể chứa thông tin không được phép xuất hiện trong log.
- Viết 87 test cho workflow: so nhãn 12 claim × 5 seed, các ca biên T01–T10, T13, T14, retry T11, crash ở 3 điểm, claim không tồn tại, trace contract trên các nhánh, và số model call / tool call.

Commit:

## 4. Bằng chứng

- `pytest -q -m student -o addopts= -k workflow`: 62 passed.
- `pytest -q tests/test_student_workflow.py`: 87 passed.
- `pytest -q`: 141 passed.
- `python -m lab8.crash_test --count 20`: `crash_safety 20/20`.
- Benchmark `workflow` trên 14 claim × seed 11, 22, 33, 44, 55: pass rate 1.000, pass^5 1.000, variance 0, cost/success 28.87 VND.
- Trace mẫu: `R-workflow-C-014-s11` (proposal 150000, ledger 120000).

## 5. Công cụ AI đã dùng

Dùng Claude Code để đọc repo, gợi ý code cho `workflow.py` và viết bản nháp test. Cách tự kiểm tra:

- Đối chiếu từng nhánh với bảng output trong `docs/contracts.md` và `docs/business_rules.md`.
- Chạy lại bộ student test, cổng host và crash suite.
- Đọc trace của C-005 và C-010 để chắc chắn không có SĐT, địa chỉ hay `CANARY_*`.

## 6. Tự đánh giá

