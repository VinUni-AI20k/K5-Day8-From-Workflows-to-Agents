# Báo cáo cá nhân — 2A202603405_NguyenNgocToan

## 1. Thông tin thành viên

- Họ tên: Nguyễn Ngọc Toàn
- MSSV: 2A202603405
- Email: ngoctoan140604@gmail.com
- GitHub: jpack1

## 2. Phần việc phụ trách

Shape B — single ReAct agent (`src/lab8/shapes/single.py`), theo issue #3.

## 3. Đóng góp cụ thể

- **Commit chính:** `307a9a4` — `feat(single): implement Shape B bounded ReAct agent` (nhánh `NguyenNgocToan`, PR #7).
- **Test thêm mới:** `src/tests/test_single_shape.py`
  - `test_single_ignores_ticket_delay_on_swarm_weak_seed`: C-002 seed 55 (ticket ghi trễ 5 ngày, order ghi 2) vẫn ra `denied`, không có refund.
  - `test_model_cannot_dispatch_issue_refund`: dispatcher từ chối `issue_refund`; vòng lặp dừng ở `step_cap` sau 8 bước.
- **Quyết định kỹ thuật:**
  - Dùng `lab8.runtime.run_react(max_steps=8)`. `decide` chỉ chọn tool đọc theo thứ tự `get_claim_view` → `lookup_order` → `compute_compensation`, rồi trả `final`. Mỗi bước gọi MockLLM một lần và ghi vào `Budget` để chi phí so sánh được với các shape khác.
  - Ticket là dữ liệu không tin cậy: chỉ đưa vào prompt trong thẻ `<untrusted_ticket>`, không dùng số ngày trễ hay điều khoản ghi trong ticket. Dữ kiện lấy từ `lookup_order`, số tiền lấy từ `compute_compensation` (chỉ policy hiện hành).
  - Model không ghi ledger. Sau vòng lặp, code của shape gọi `durability.issue_refund` với **quote đầy đủ**, để host tự trừ phần đã hoàn của đơn (T13, T14).
  - Truyền `crash_at` vào `issue_refund`, không bắt `InjectedCrash` (chỉ ghi trace rồi ném lại) để lần chạy lại replay idempotent (T12).
  - Trace chỉ ghi bước ReAct, quote và quyết định; không ghi ticket, secret hay PII.
  - Ánh xạ trạng thái: không có claim → `failed`; thiếu order → `needs_info`; order không thấy được → `escalated`; quote 0 → `denied`; host từ chối → `denied` (xung đột số tiền → `failed`); ghi thành công → `resolved`.

## 4. Bằng chứng

- Commit: `307a9a4`, `0baf8c7` (TEAM.md). PR: https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents/pull/7
- Ma trận student của shape single:
  `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` → `62 passed` (T01–T14, gồm T11 retry và T12 crash).
- Cổng host: `python -m pytest -q` → xanh.
- Run id ví dụ: `R-single-C-001-s11` (`python -m lab8.run --shape single --claim-id C-001 --seed 11 --db data/run.sqlite` → `resolved`).
- Benchmark public (14 claim × seed 11,22,33,44,55), chạy `python -m lab8.benchmark --shapes single,swarm ...`:

  | shape | pass | pass^5 | variance | cost/success |
  |---|---|---|---|---|
  | single | 1.000 | 1.000 | 0.000000 | 37.16 |
  | swarm | 0.986 | 0.929 | 0.000816 | 49.57 |

  Lỗi duy nhất của swarm là C-002 seed 55 (`resolved != denied`), đúng điểm yếu cố ý của bản tham chiếu. Chi phí là VND mô phỏng, không phải hoá đơn API.
- Chưa chạy bộ hidden 40 claim (chưa có `student_drop/`).

## 5. Công cụ AI đã dùng

- **Claude Code (Claude Opus):** đọc issue #3 và code host, gợi ý cài đặt `single.py`, viết `test_single_shape.py`, chạy test/benchmark, soạn mô tả PR và bản nháp báo cáo này.
- **Cách tự kiểm tra:**
  - Chạy lại ma trận student cho shape single (62 passed) và cổng host `pytest -q` (xanh).
  - Lọc test đúng shape: lệnh `-k single` gốc trong issue còn khớp tên `test_public_single_run_cases` của các shape khác, nên phải loại workflow/orchestrator/swarm mới thấy đúng kết quả của single.
  - Kiểm tra trace `R-single-*.json` không chứa `CANARY`.
  - Đối chiếu số benchmark với output lệnh chạy thật, không tự điền.

## 6. Tự đánh giá

Qua phần việc Shape B, tôi hiểu rõ hơn cách xây dựng một ReAct agent có giới hạn và cách chia trách nhiệm giữa agent với host. Agent chỉ chọn các bước đọc dữ liệu và đề xuất kết quả; host kiểm tra quote rồi mới ghi hoàn tiền. Cách tách này giúp tôi xử lý an toàn hơn các trường hợp ticket chứa thông tin sai, yêu cầu bỏ qua policy hoặc vòng lặp cần dừng.

Tôi đã kiểm tra các tình huống quan trọng bằng test, gồm seed mà swarm tin vào số ngày trễ trong ticket, việc agent không được gọi công cụ ghi, giới hạn 8 bước và các trường hợp retry/crash trong ma trận student. Benchmark public cho kết quả single pass 1.000 trên tập đã chạy. Tuy vậy, tôi chưa chạy bộ hidden 40 claim, nên kết quả hiện tại chưa cho biết đầy đủ hiệu năng trên tập đánh giá đó. Khi có bộ dữ liệu này, tôi cần chạy lại và xem xét các trường hợp thất bại để đánh giá phần cài đặt toàn diện hơn.
