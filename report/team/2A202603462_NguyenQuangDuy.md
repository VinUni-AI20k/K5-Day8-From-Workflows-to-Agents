# Báo cáo cá nhân — NguyenQuangDuy

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quang Duy
- MSSV: 2A202603462
- Email: nduy120505@gmail.com
- GitHub: nduy120505
- Vai trò: Workflow (shape A) và integration.

## 2. Phần việc phụ trách

- Triển khai shape A tại `src/lab8/shapes/workflow.py`: chuỗi bước Python cố định, không có vòng lặp, model không tham gia quyết định.
- Giữ ranh giới code / model / host trong shape: code đọc dữ liệu và tính tiền, host kiểm approval và ghi ledger, MockLLM chỉ soạn câu trả lời.
- Thêm test riêng cho workflow tại `src/tests/test_workflow_extra.py`.
- Integration: gộp nhánh `feat/workflow` vào `main` và kiểm tra lại sau khi gộp (cổng host, ma trận student, `check_submission`). Benchmark và crash suite do thành viên phụ trách evaluation chạy.

## 3. Đóng góp cụ thể

Luồng xử lý của workflow:

- Đọc claim qua `get_claim_view` thay vì `SELECT *`, nên `parent_secret` và `raw_headers` không đi vào shape. Claim không tồn tại trả `failed`.
- Thiếu `order_id` trả `needs_info`, không ghi ledger và không lấy mã đơn từ câu chữ trong ticket.
- Tra đơn bằng `lookup_order` với principal của claim. Đơn không tồn tại hoặc không thuộc principal trả `escalated`.
- Tính tiền bằng `compute_compensation` trên order row và policy hiện hành. Không dùng số ngày trễ ghi trong ticket, nên T02 (ticket ghi 5 ngày, đơn ghi 2 ngày) bị từ chối trên mọi seed.
- Quote bằng 0 trả `denied` và không gọi `issue_refund`.
- Quote dương được truyền **đầy đủ** vào `durability.issue_refund`. Host kiểm approval, trừ phần đơn đã được hoàn trước đó và chống ghi trùng. Shape không tự trừ, vì nếu trừ trước thì host trừ thêm lần nữa và T14 sai.
- Host từ chối trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`. Trong cả ba trường hợp `proposal_amount` vẫn là quote đầy đủ.
- Truyền `crash_at` vào host và không bắt `InjectedCrash`; kết nối SQLite luôn được đóng trong `finally`.
- Mọi nhánh trả kết quả đi qua một hàm `done()` gọi `finish()`, nên nhánh nào cũng có trace và `refund_effects` luôn lấy từ ledger.
- Trace chỉ ghi các event `claim`, `lookup_order`, `quote`, `host`, `decision`. Cố ý không ghi ticket, claim row, order row, principal, SĐT, địa chỉ, tên hàng và ghi chú nội bộ.
- MockLLM được gọi một lần với `purpose="draft"` sau khi host đã trả kết quả; đầu ra của nó không ảnh hưởng tới status hay số tiền.

Test đã thêm (`src/tests/test_workflow_extra.py`, 4 hàm, 8 ca):

- `test_workflow_ignores_delay_written_in_ticket`: T02 trên 5 seed `11,22,33,44,55` đều `denied`, proposal 0, không có dòng ledger.
- `test_workflow_passes_full_quote_and_host_pays_difference`: T14 có proposal 150.000 và ledger 120.000.
- `test_workflow_host_denial_keeps_quote_and_writes_audit`: T07 có proposal 35.000, không có dòng ledger, có đúng một audit `policy_denied`.
- `test_workflow_retry_keeps_one_refund_and_clean_trace`: chạy C-011 hai lần vẫn một dòng ledger 35.000; trace khớp `run_id`, không chứa secret hay nội dung ticket.

Commit:

- [603e469](https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/603e469) — triển khai `workflow.py`.
- [1e53ad2](https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/1e53ad2) — thêm `test_workflow_extra.py`; đã push lên nhánh `feat/workflow`.
- [b05673d](https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/b05673d) — báo cáo cá nhân.

Nhánh `feat/workflow` đã được gộp vào `main`.

## 4. Bằng chứng

Kết quả kiểm tra lại sau khi gộp, trên bản sao của `main` tại commit `051be2c`. Các lệnh do trợ lý Claude chạy (Python 3.13, Linux), không phải trên máy của tôi:

| Lệnh | Kết quả quan sát |
| --- | --- |
| `python -m pytest -q` | 65 passed, 289 deselected |
| `python -m pytest -q -m student -o addopts=` | 289 passed, 65 deselected |
| `python -m pytest -q -m student -o addopts= -k workflow` | 62 passed cho ma trận T01–T14 của workflow |
| `python -m pytest -q tests/test_workflow_extra.py` | 8 passed |
| `python -m lab8.check_submission` | 0 FAIL (1 WARN vì bản sao không có git) |
| `python -m lab8.benchmark ...` (lệnh chính thức, ghi ra file tạm) | Số của cả 4 shape khớp `src/reports/benchmark.json` đã commit |

Số liệu của workflow trong `src/reports/benchmark.json`: pass rate 1.000, pass^5 1.000, variance 0, cost/success 28.46 VND (mô phỏng) trên 14 claim × 5 seed. `src/reports/crash.json` ghi `crash_safety` = 20/20. Hai file này do thành viên phụ trách evaluation sinh ra bằng lệnh chính thức.

Trên máy của tôi, bộ student đã được chạy cho workflow và sinh trace tại `src/traces/R-workflow-*.json`. Ví dụ `R-workflow-C-005-s11` chỉ có ba event `claim`, `lookup_order`, `decision` với lý do `outside_principal_scope`, không có dữ liệu của đơn.

Chưa có kết quả hidden; pass rate hidden do giảng viên chấm.

## 5. Công cụ AI đã dùng

Sử dụng Claude vào các việc sau:

- Đọc yêu cầu lab, giải thích luật nghiệp vụ, contract và từng nhánh của `workflow.py`.
- Soạn bản đầu của `workflow.py` và viết `src/tests/test_workflow_extra.py`.
- Kiểm tra trạng thái repo, chạy lại test và benchmark trên bản sao (bảng ở mục 4).
- Soạn bản nháp báo cáo này, dòng của tôi trong `TEAM.md` và đoạn mô tả workflow trong báo cáo nhóm.

Code lab chỉ dùng MockLLM có sẵn, không gọi model thật và không dùng API key.

Cách tự kiểm tra: đọc lại từng nhánh của `workflow.py` cùng phần giải thích để nắm ranh giới code / model / host và lý do truyền quote đầy đủ; chạy bộ student cho workflow trên máy mình; mở trace để kiểm tra không có secret hay thông tin cá nhân. Các con số trong bảng ở mục 4 do Claude chạy và báo lại; tôi cần chạy lại trên máy mình và đối chiếu trước khi nộp.

## 6. Tự đánh giá

Shape workflow đáp ứng các ca public đã chạy, gồm cả gọi lại cùng claim (T11) và crash rồi resume (T12). Trên bộ public, workflow ngang pass rate với single và orchestrator và có cost/success thấp nhất, nên được nhóm chọn trong ADR. Bằng chứng hiện giới hạn ở dữ liệu public; chưa có cơ sở kết luận về bộ hidden. MockLLM không đại diện model sản xuất; latency là `unavailable`.
