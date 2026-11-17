# Báo cáo cá nhân — 2A202603909_TranTuanAnh

## 1. Thông tin thành viên

- Họ tên: Trần Tuấn Anh
- MSSV: 2A202603909
- Email: 275679340+Tanh0406@users.noreply.github.com
- GitHub: Tanh0406

## 2. Phần việc phụ trách

- Shape B `single`: `src/lab8/shapes/single.py`, một agent ReAct tối đa 8 bước, cùng chữ ký `run_claim` với ba shape còn lại.
- Test riêng cho shape single: `src/tests/test_single_shape.py`.
- Phần của mình trong `TEAM.md` và báo cáo cá nhân này.

## 3. Đóng góp cụ thể

**Commit chính** (branch `Tanh0406`):

- `94bc560` — feat(single): implement shape B ReAct agent with read-only tools.
- `a82826d` — docs(team): add Tran Tuan Anh (single shape) to TEAM.md, set class L3B.

**Thiết kế shape single:**

| Thành phần | Ai quyết | Cách làm |
| --- | --- | --- |
| Chọn tool kế tiếp | "Model" (`decide()`) | Chỉ chọn tool đọc, theo thứ tự `get_claim_view` → `lookup_order` → `lookup_refund_history` → `compute_compensation` → `final`. Mỗi bước gọi MockLLM một lần để cost so được với các shape khác |
| Số ngày trễ, trạng thái đơn | Code | Lấy từ order row của `lookup_order` (đã allowlist), **không** lấy từ ticket |
| Số tiền | Code | `compute_compensation` |
| Ghi refund | Code của shape, sau vòng lặp | `durability.issue_refund(conn, claim_id, <quote đầy đủ>, crash_at=crash_at)` |
| Approval, trần theo đơn, idempotency | Host | Shape không tự trừ phần đã hoàn |

**Các quyết định kỹ thuật:**

1. **`decide()` có scratchpad riêng.** `run_react` chỉ trả lại kết quả tool gần nhất, nên `decide()` giữ `order_id`, `principal_id` và order view trong một closure để dùng cho bước sau.
2. **Truyền quote đầy đủ vào `issue_refund`.** Host tự trừ phần đơn đã được hoàn. Nếu shape trừ trước thì host trừ thêm lần nữa và T14 sai. `lookup_refund_history` chỉ để ghi vào trace, không dùng để tính tiền.
3. **Quote bằng 0 thì `denied` mà không gọi host.** Khi quote > 0 nhưng host từ chối, shape trả `denied` với `proposal_amount` là quote đầy đủ, và host ghi audit `policy_denied`. Khi số tiền xung đột (`conflict`), shape trả `failed`.
4. **Crash:** khi gặp `InjectedCrash`, shape ghi trace rồi ném lỗi ra tiếp, không nuốt. Với các exception khác, shape trả `failed` (fail closed), vì `run_claim` không được ném exception.
5. **Trace cố ý không ghi** ticket, `principal_id`, claim row thô, `parent_secret`, header. Lý do: ticket có thể chứa dữ liệu người dùng và câu injection; claim row có secret; grader quét trace để tìm secret và PII. Trace chỉ ghi tên tool, `found` và `visible`, order view đã allowlist, quote, kết quả của host và quyết định cuối.

**Test đã thêm** (`src/tests/test_single_shape.py`, 36 test, chạy trong cổng host):

- `test_single_trace_has_no_ticket_secret_or_pii`: chạy 14 claim public, kiểm trace và kết quả không chứa `CANARY_SECRET_`, header, `forbid_substrings` hay nguyên văn ticket.
- `test_single_trace_matches_contract_and_step_cap`: chạy 14 claim, kiểm `run_id` khớp, `events` là list, và số tool call, model call không vượt trần 8 bước.
- `test_single_ignores_ticket_delay_on_every_seed`: chạy T02 ở 5 seed, đều ra `denied`, kể cả seed 55 là chỗ swarm fail.
- `test_single_unknown_claim_fails_closed_with_trace`: claim không tồn tại thì ra `failed` và vẫn có trace hợp lệ.
- `test_single_crash_before_effect_then_resume_pays_once`: điểm crash `before_effect`, cái mà T12 không kiểm.
- `test_single_passes_full_quote_on_partially_refunded_order`: T14, proposal 150.000 và ledger 120.000.

## 4. Bằng chứng

- Commit `94bc560`, `a82826d` trên branch `Tanh0406` của repo nhóm.
- Ma trận student của shape single:
  `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` → `62 passed`.
- Cổng host, gồm cả test mới: `python -m pytest -q` → `90 passed, 248 deselected`.
- Trace mẫu `traces/R-single-C-014-s55.json` (không commit): có 7 event là `tool` ×3, `quote`, `react_stop`, `issue_refund`, `decision`; kết quả `resolved`, `proposal_amount` 150000, ledger 120000.
- Run id theo mẫu `R-single-<claim_id>-s<seed>`. Số liệu benchmark của nhóm nằm trong `src/reports/benchmark.json`, do nhóm chạy ở CP5.

## 5. Công cụ AI đã dùng

- **Claude Code** (trợ lý lập trình trong VS Code). Mình dùng nó để:
  - Đọc toàn bộ repo và tóm tắt yêu cầu đề.
  - Gợi ý code cho `single.py` và viết `test_single_shape.py`.
  - Thao tác git: tạo branch, soạn commit, push.
- **Cách tự kiểm tra kết quả:**
  - Đọc lại từng nhánh của `single.py` và đối chiếu với `docs/business_rules.md` và bảng output contract trong `docs/contracts.md`.
  - Chạy ma trận student của shape single (62/62) và cổng host (90 passed).
  - Mở trace của T14 để kiểm proposal và ledger, và xác nhận trace không chứa ticket hay secret.
  - Quét thư mục `traces/R-single-*` tìm `CANARY` và số điện thoại của T05: không có kết quả nào.
  - Duyệt nội dung commit trước khi push.
- Không dùng AI để bịa số liệu benchmark, run id hay commit. Mọi con số ở trên đều lấy từ lần chạy thật.

## 6. Tự đánh giá

- **Làm được:**
  - Shape single qua đủ 62 test student, cổng host vẫn xanh.
  - Ranh giới code và model rõ ràng: model không quyết số tiền và không ghi refund.
  - Trace không lộ secret hay PII. Có thêm test cho các trường hợp ma trận public chưa phủ.
- **Hạn chế:**
  - `decide()` đi theo kế hoạch cố định, nên single thực chất gần với workflow; mức tự chủ của model chỉ nằm ở việc chọn tool đọc, và không có nhánh hỏi lại khách khi ticket mơ hồ.
  - MockLLM không phải model thật, latency là `unavailable`, nên kết quả chưa phản ánh hành vi của một LLM thật trong vòng ReAct.
  - Chưa tự kiểm shape single trên `student_drop/`, bộ hidden 40 claim.
- **Hướng cải thiện:**
  - Chạy tự kiểm hidden khi được phát `student_drop/`.
  - So cost per success của single với workflow trong benchmark để góp số liệu cho ADR.
  - Thử biến thể `decide()` bỏ bước `lookup_refund_history` để đo xem bước này có đáng phần cost tool không.
