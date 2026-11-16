# Báo cáo cá nhân — 2A202603672_NguyenVanVinh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Vinh
- MSSV: 2A202603672
- Email: 26ai.vinhnv@vinuni.edu.vn
- GitHub: https://github.com/VINH1811

## 2. Phần việc phụ trách

Tôi phụ trách **Role 2: Single agent (ReAct)**, tức shape B `single`:

- Code: `src/lab8/shapes/single.py`. Hàm `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult` giữ nguyên chữ ký.
- Test: `src/tests/test_single_shape.py`. Đây là test riêng của shape `single` và chạy trong cổng host.

## 3. Đóng góp cụ thể

**Commit chính:** `cc29c4d`

**Thiết kế shape `single`:**

1. Đọc claim qua `get_claim_view`, không dùng `SELECT *`. Claim không tồn tại thì trả `failed` với `proposal_amount = 0`.
2. Vòng ReAct dùng `lab8.runtime.run_react` với `max_steps = 8`. Hàm `decide` chỉ được chọn tool **đọc** (`lookup_order`, `lookup_refund_history`) hoặc trả `final`:
   - Thiếu `order_id` thì trả `needs_info`. Tôi không lấy mã đơn từ chữ trong ticket.
   - Đơn không thấy hoặc không thuộc principal thì trả `escalated`, và không trả phone, địa chỉ, tên hàng hay ghi chú nội bộ.
   - Đủ dữ kiện thì trả `propose`.
3. `run_react` thay toàn bộ observation sau mỗi tool, nên các kết quả tool cũ sẽ mất. Vì vậy tôi giữ dữ kiện lấy từ DB trong dict `state` do **code** quản lý, không để model "nhớ".
4. Sau vòng lặp, **code** tính tiền bằng `compute_compensation` từ order row. Tôi bỏ qua số ngày trễ, clause cũ và các câu kiểu "ignore policy" trong ticket.
   - Quote bằng 0 thì trả `denied` và không gọi `issue_refund`.
   - Quote lớn hơn 0 thì gọi `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)`.
5. Kết quả từ host được ánh xạ như sau:
   - `ok` thành `resolved`.
   - `conflict` thành `failed`.
   - Các trường hợp còn lại thành `denied`, với `proposal_amount` vẫn là quote đầy đủ. Host đã tự ghi audit `policy_denied`.
6. `InjectedCrash` không bị nuốt: shape ghi trace rồi `raise` lại.
7. Mỗi bước ReAct gọi MockLLM một lần, và gọi thêm một lần để soạn trả lời, nên cost và token được tính vào `Budget` để so sánh được với các shape khác. Model không quyết số tiền và không gọi tool ghi.

**Quyết định kỹ thuật và lý do:**

- **Truyền quote đầy đủ, không tự trừ phần đã hoàn.** Host đã tự trừ số đã hoàn của cùng đơn. Nếu shape trừ trước thì sẽ thành trừ hai lần và T14 fail (đúng phải là ledger 120.000, quote 150.000). Tôi chỉ dùng `lookup_refund_history` như tool đọc tham khảo.
- **Không bắt `InjectedCrash`.** T12 kiểm crash có thật sự xảy ra. Idempotency key `refund:{claim_id}` của host đảm bảo resume vẫn chỉ ra một refund và một audit `refund_committed`.
- **Trace cố ý không ghi** ticket, claim row, order row, `parent_secret` và header. Trace chỉ ghi các event `claim` (`has_order_id`), `act` (tên tool), `react_stop`, `quote` (amount, reason, clause_ids), `host` (ok, reason), `decision` và `crash`. Lý do: trace là ranh giới bảo mật mà grader quét, và claim row có `parent_secret`, order row có SĐT và địa chỉ.

**Test đã thêm** (`src/tests/test_single_shape.py`, 33 test):

- `test_single_ignores_delay_written_in_ticket` (5 seed): C-002, ticket ghi "trễ 5 ngày" còn order ghi 2 ngày, phải ra `denied`, `proposal_amount = 0` và ledger trống ở **cả 5 seed**, kể cả seed 55 (chỗ swarm fail).
- `test_single_trace_has_no_secret_or_ticket_text` (14 claim): trace không chứa `CANARY_SECRET_`, `Bearer`, `parent_secret` hay nội dung ticket.
- `test_single_react_uses_only_read_tools_within_step_cap` (14 claim): theo dõi `runtime.dispatch`. Mọi tool mà vòng ReAct gọi phải thuộc `READONLY_TOOLS`, không quá 8 lần gọi tool, và `model_calls ≤ 9`.

## 4. Bằng chứng

Các lệnh dưới đây chạy trong `src/`:

| Lệnh | Kết quả |
| --- | --- |
| `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` | `62 passed` (T01–T14, gồm T11 retry và T12 crash) |
| `python -m pytest -q tests/test_single_shape.py` | `33 passed` |
| `python -m pytest -q` (cổng host) | `87 passed`, không có `failed` |
| `python -m lab8.run --shape single --claim-id C-001 --seed 11 --db data/run.sqlite` | `status = resolved`, `proposal_amount = 35000`, một refund `refund:C-001`, `committed_audit_count = 1`, trace `traces/R-single-C-001-s11.json` |

**Lưu ý khi chạy lệnh:** lệnh `-k single` ghi trong CHECKPOINTS cũng khớp tên test `single_run_cases` của mọi shape. Vì vậy tôi dùng biểu thức `-k` ở bảng trên để chỉ chạy test của shape `single`.

Số liệu benchmark của `single` (pass rate, pass^5, variance, cost/success, run id) lấy từ `src/reports/benchmark.json` sau khi nhóm chạy benchmark 4 shape × 5 seed, và được ghi trong `report/team/decision_adr.md`.

## 5. Công cụ AI đã dùng

Dùng trợ lý AI để giải thích khái niệm, gợi ý code, viết test và đọc trace. Kết quả được tự kiểm bằng cách chạy ma trận student, test riêng và cổng host (mục 4).

## 6. Tự đánh giá

- Shape `single` chạy đúng contract trên bộ public: 62/62 test student xanh, cổng host xanh.
- Ranh giới được giữ đúng: model chỉ chọn tool đọc; tiền do code tính; host là nơi duy nhất ghi ledger; truyền `crash_at` và không nuốt crash.
- Trace không lộ secret trên 14 claim public. Hidden set có thêm các ca như homoglyph và principal lẫn, nên sẽ cần kiểm lại bằng `student_drop/` ở CP5.
- Giới hạn: `decide` hiện là một máy trạng thái cố định, dùng MockLLM chỉ để đếm cost. Vì vậy shape `single` ổn định giữa các seed nhưng tốn nhiều lời gọi model hơn `workflow` mà không thêm năng lực. Đây là dữ kiện để nhóm cân nhắc khi chọn shape trong ADR.
