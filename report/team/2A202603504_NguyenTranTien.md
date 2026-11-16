# Báo cáo cá nhân — 2A202603504_NguyenTranTien

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trần Tiến
- MSSV: 2A202603504
- Email: nguyentien2004abc@gmail.com
- GitHub: tiennguyen-ctrl

## 2. Phần việc phụ trách

Shape B `single` (một agent ReAct): file `src/lab8/shapes/single.py`, cùng test nhóm `src/tests/test_team_single.py` và phần Single (ranh giới code/model) trong mục 3 của `group_report.md`.

Ranh giới code và model trong shape này:

- **Model** (`decide`, qua MockLLM) chỉ chọn tool đọc: `lookup_order`, rồi `compute_compensation`. Mỗi bước tính một model call vào `Budget`.
- **Code** quyết mọi thứ có hậu quả: số tiền do `compute_compensation` tính, trạng thái (`needs_info`, `escalated`, `denied`, `resolved`, `failed`), và việc ghi refund. Ghi refund chỉ đi qua `durability.issue_refund`, `runtime.dispatch` từ chối tool ghi.
- Số ngày trễ luôn lấy từ order row, không đọc số trong ticket, nên ticket nói quá hoặc chèn lệnh không đổi được quote.

## 3. Đóng góp cụ thể

Commit chính (hash): _chưa commit, điền hash sau khi commit và push._

Code và test đã viết:

- `src/lab8/shapes/single.py`: thay stub `not_implemented` bằng vòng `run_react(max_steps=8)`.
  - Có claim, có `order_id`, đơn thuộc đúng principal thì mới tính quote. Thiếu `order_id` trả `needs_info`, không thấy đơn hoặc sai principal trả `escalated`, quote bằng 0 trả `denied` và không gọi `issue_refund`.
  - Quote lớn hơn 0 thì gọi `durability.issue_refund` với **quote đầy đủ**. Host tự trừ phần đã hoàn trước đó, shape không trừ thêm.
  - Truyền `crash_at` vào `issue_refund`. `InjectedCrash` chỉ được ghi vào trace rồi ném lại, không bị nuốt.
  - Mọi nhánh return đi qua `finish()` nên `refund_effects` và `committed_audit_count` lấy từ ledger.
  - Trace chỉ ghi field đã qua allowlist (`claim_id`, có `order_id` hay không, order view đã lọc field, quote). Không ghi ticket, claim row hay order row thô.
- `src/tests/test_team_single.py` (19 test):
  - vòng lặp dừng đúng ở 8 bước khi model không bao giờ `final`;
  - `single` không chạm trần 8 bước trên 14 claim public;
  - `decide` chọn `issue_refund` hoặc `append_audit` thì bị `ToolRejected` và ledger không có dòng nào;
  - mọi tool mà `single` gọi đều là tool đọc, refund ở C-001 do host ghi;
  - trace đúng contract và không chứa `CANARY_SECRET`, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.

Quyết định kỹ thuật:

- Không gọi `lookup_refund_history`: host đã tự trừ phần đã hoàn theo đơn (T13, T14), gọi thêm chỉ tốn chi phí mà không đổi kết quả.
- Dùng MockLLM `complete()` cho mỗi bước `decide` và một lần soạn phản hồi `draft`, để chi phí so sánh được với các shape khác.

Giới hạn: chưa có số benchmark và chưa có crash suite 20/20 cho `single`. Hai phần đó do Hoàng chạy ở CP4 và CP5, nên báo cáo này không ghi số nào ngoài các kết quả bên dưới.

## 4. Bằng chứng

Kết quả đã chạy trên máy (Python 3.13.12, Windows) trong thư mục `src/`:

- `python -m lab8.smoke`: `lab8.smoke pass`.
- `python -m pytest -q -m student -o addopts= -rf`: không có dòng `FAILED` nào của `single` (62/62 test student của `single` xanh, gồm T01–T14 trên 5 seed, T11 và T12). Lọc riêng `single` bằng `Select-String "^FAILED.*single\]"` cho kết quả rỗng.
- `python -m pytest -q tests/test_team_single.py`: 19 passed.
- `python -m pytest -q` (cổng host): 73 passed, 248 deselected, không có `failed`.
- Run id của `single` có dạng `R-single-<claim>-s<seed>`, ví dụ `R-single-C-001-s11` (sinh ra khi chạy `test_team_single.py`).

Link commit: _điền sau khi commit và push._

## 5. Công cụ AI đã dùng

- **Claude Code (Claude Sonnet 5.5)** trong VS Code: đọc repo và đề bài, giải thích luật nghiệp vụ và contract, viết bản đầu của `single.py` và `test_team_single.py`, chạy test và đọc kết quả.
- **Cách tự kiểm tra:** chạy lại các lệnh ở mục 4 trên máy mình và đối chiếu với kỳ vọng trong `CHECKPOINTS.md` (62 test student của `single` xanh, cổng host xanh); đối chiếu hành vi từng nhánh với `docs/business_rules.md` và `docs/contracts.md`; không sửa `metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`.
- _Tiến bổ sung: những phần bạn đã tự đọc hiểu và tự giải thích được (vì sao truyền quote đầy đủ, vì sao không bắt `InjectedCrash`, vì sao trace không ghi ticket và claim row)._

## 6. Tự đánh giá

_Phần này Tiến tự viết theo nhận định của mình (đã làm được gì, còn thiếu gì, khó khăn gặp phải). Không điền thay._
