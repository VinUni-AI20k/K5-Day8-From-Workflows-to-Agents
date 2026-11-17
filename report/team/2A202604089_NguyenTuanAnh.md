# Báo cáo cá nhân — 2A202604089_NguyenTuanAnh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tuấn Anh
- MSSV: 2A202604089
- Email: capntryisreal@gmail.com
- GitHub: TuanAnhNg131

## 2. Phần việc phụ trách

- Shape C `orchestrator`: `src/lab8/shapes/orchestrator.py`.
- Ranh giới bàn giao công việc (handoff boundary) và điều phối các tác tử điều tra chỉ đọc (read-only investigators).
- Viết bộ kiểm thử chuyên biệt cho `orchestrator` và `handoff` trong `src/tests/test_orchestrator_shape.py`.

## 3. Đóng góp cụ thể

**Shape `orchestrator`** (`src/lab8/shapes/orchestrator.py`) — tách bạch giữa tác tử điều phối (orchestrator) và các tác tử điều tra chỉ đọc (read-only investigators) qua ranh giới `handoff.v1`:

1. Đọc thông tin yêu cầu qua công cụ danh sách trắng (allowlist) `get_claim_view` (không dùng `SELECT *`, không đọc `parent_secret` hay `raw_headers_json`).
2. Nếu không tìm thấy claim → trả `failed` (`unknown_claim`). Nếu thiếu `order_id` → trả `needs_info` (`missing_order_id`), không lấy mã đơn từ câu chữ trong `ticket`.
3. Tạo gói bàn giao có kiểu (`typed handoff`) bằng `lab8.handoff.make_handoff`:
   - `principal_scope` cố định là `"owner_order_only"`.
   - `allowed_tools` chỉ gồm các công cụ đọc (`lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`).
   - `facts` rỗng (không truyền `parent_secret`, `raw_headers`, hay `ticket` của ngữ cảnh cha sang worker).
   - Ghi nhận gói `handoff` đã làm sạch (sanitized) vào nhật ký `trace`.
4. Chạy `run_readonly_investigators` để worker thu thập thông tin đơn hàng, chính sách hiện hành, lịch sử hoàn tiền của đơn và tính báo giá đền bù (`quote`).
5. Nếu `order_view["visible"] == False` (đơn không tồn tại hoặc không thuộc quyền sở hữu của `principal_id`) → trả `escalated`, không làm lộ thông tin cá nhân (PII).
6. Nhận báo giá `amount_vnd` từ kết quả `compute_compensation` của investigator:
   - Nếu `amount <= 0` → trả `denied`, không gọi `issue_refund`.
   - Nếu `amount > 0` → chỉ có orchestrator (thông qua cổng host `durability.issue_refund`) mới thực hiện lệnh hoàn tiền với **quote đầy đủ** (`amount`) và truyền `crash_at`.
7. Khi xảy ra lỗi mô phỏng `InjectedCrash`: ghi sự kiện `crash` và xả (`write()`) file trace xuống đĩa trước khi `raise` tiếp để đảm bảo tính an toàn khi sập nguồn (crash safety) và giữ đúng hợp đồng `Trace contract v1`.
8. Nếu host từ chối (`not outcome["ok"]`): trả `failed` khi xung đột số tiền (`conflict=True`) hoặc `denied` khi vi phạm chính sách/phê duyệt (host tự ghi `policy_denied`), giữ nguyên `proposal_amount` là quote đầy đủ. Khi thành công → trả `resolved` qua `common.finish()`.

**Quyết định kỹ thuật:**

- **Làm sạch ngữ cảnh qua Allowlist (Code Sanitization), không dùng LLM tóm tắt:** Dùng `make_handoff` và `sanitize` để lọc theo danh sách trắng các trường hợp lệ (`ALLOWED_FIELDS`, `FACT_KEYS`, `READONLY_TOOLS`) và chặn mọi chuỗi chứa `CANARY_SECRET_`, `parent_secret`, `raw_headers`.
- **Phân tách quyền hạn (Least Privilege):** Investigator chỉ có quyền gọi công cụ đọc (`worker=True` trong `runtime.dispatch`), không có quyền gọi `issue_refund`.
- **Truyền quote đầy đủ cho trần theo đơn (Per-order cap):** Dù investigator đọc được `lookup_refund_history`, orchestrator vẫn truyền toàn bộ entitlement quote vào `durability.issue_refund` để host tự trừ phần đã hoàn ở các claim trước trong cùng giao dịch SQLite (`BEGIN IMMEDIATE`), giúp vượt qua cả T13 và T14.

**Test đã thêm:** `src/tests/test_orchestrator_shape.py` (23 test, chạy trong cổng host):

| Test | Kiểm tra |
| --- | --- |
| `test_orchestrator_ticket_injection_cannot_raise_refund` (×5 seed) | Ticket C-002 chứa câu lệnh tiêm nhiễm (prompt injection) đòi hoàn 2.000.000đ và khai khống trễ 30 ngày vẫn bị `denied`, ledger không ghi tiền |
| `test_handoff_rejects_write_tools_and_strips_extra_facts` | `make_handoff` từ chối công cụ ghi (`issue_refund`) với `HandoffError` và tự động loại bỏ `parent_secret`, `raw_headers`, `ticket` khỏi `facts` |
| `test_handoff_sanitize_blocks_canary_secret_in_allowed_fields` | `sanitize` chặn ngay lập tức nếu `CANARY_SECRET_` xuất hiện trong trường hợp lệ |
| `test_orchestrator_traces_sanitized_handoff_and_full_quote_on_partial_refund` | Trên C-014 (T14), orchestrator ghi handoff hợp lệ vào trace, trả `proposal_amount = 150000` (quote đầy đủ) và ledger ghi đúng phần chênh `120000` |
| `test_orchestrator_unknown_claim_and_amount_conflict` | Claim không tồn tại trả `failed` (`unknown_claim`); gọi lại với số tiền khác trả `failed` (`amount_conflict`) và bảo toàn dòng ledger cũ |
| `test_orchestrator_trace_has_no_secret_headers_or_ticket_text` (×14 claim) | Quét toàn bộ trace của 14 claim public đảm bảo không rò rỉ `parent_secret`, `Bearer`, hay nội dung `ticket` |

## 4. Bằng chứng

Chạy trong thư mục `src/` (nhánh `nta`):

- `python -m pytest -q -m student -o addopts= -k orchestrator` → `62 passed` (đủ 12 claim đơn × 5 seed + T11 retry + T12 crash/resume).
- `python -m pytest -q -m student -o addopts=` → `248 passed` (toàn bộ 4 shape × 62 test đều xanh).
- `python -m pytest -q` → `99 passed` (cổng host xanh, bao gồm 23 test mới trong `test_orchestrator_shape.py`).
- `python -m lab8.check_submission` → `[ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.
- Báo cáo cá nhân: [report/team/2A202604089_NguyenTuanAnh.md](2A202604089_NguyenTuanAnh.md).

## 5. Công cụ AI đã dùng

- **Antigravity (Google DeepMind):** hỗ trợ đọc hiểu cấu trúc mã nguồn, đối chiếu hợp đồng đầu ra (`docs/contracts.md`) và luật nghiệp vụ (`docs/business_rules.md`), triển khai `src/lab8/shapes/orchestrator.py`, viết bộ kiểm thử `src/tests/test_orchestrator_shape.py` và rà soát định dạng báo cáo.
- **Cách tự kiểm tra:**
  - Chạy trực tiếp các bài kiểm thử đơn vị (unit tests) và ma trận kiểm thử học viên (`pytest -m student`) trên môi trường ảo `.venv`.
  - Kiểm tra nội dung file trace sinh ra trong `src/traces/R-orchestrator-*.json` để xác nhận đúng cấu trúc `trace.v1` và không chứa dữ liệu nhạy cảm.
  - Kiểm tra logic truyền `crash_at` và xử lý `InjectedCrash` qua bài kiểm thử T12 và `lab8.crash_test`.

## 6. Tự đánh giá

Điểm làm tốt là thiết kế `orchestrator` tuân thủ chặt chẽ nguyên tắc phân tách quyền hạn và làm sạch dữ liệu qua ranh giới `handoff`: investigator hoàn toàn chỉ đọc và nhận gói dữ liệu đã qua allowlist, trong khi quyết định hoàn tiền luôn đi qua cổng kiểm duyệt của host với báo giá đầy đủ. Bộ test bổ sung kiểm tra kỹ cả ranh giới bảo mật của `make_handoff`/`sanitize` lẫn trường hợp hoàn tiền một phần (T14). Điểm cần lưu ý là kiến trúc `orchestrator` tốn nhiều lời gọi công cụ và mô hình hơn `workflow` đơn thuần trong khi độ chính xác trên tác vụ tất định là tương đương; đây là cơ sở thực nghiệm quan trọng để nhóm đưa ra quyết định kiến trúc trong ADR.
