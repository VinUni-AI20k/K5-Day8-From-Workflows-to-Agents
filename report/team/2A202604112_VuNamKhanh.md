# Báo cáo cá nhân — 2A202604112_VuNamKhanh

## 1. Thông tin thành viên

- Họ tên: Vũ Nam Khánh
- MSSV: 2A202604112
- Email: khanhvnm03@gmail.com
- GitHub: khanhvnm

## 2. Phần việc phụ trách

- Shape B `single`: `src/lab8/shapes/single.py`.
- Triển khai agent đơn theo flow nghiệp vụ chung của lab.
- Kiểm tra shape bằng ma trận student, retry/idempotency, crash/resume và cổng host.

## 3. Đóng góp cụ thể

**Shape `single`** — agent chạy ReAct, nhưng code và host vẫn giữ toàn quyền với
tiền và side effect:

1. Mở store và tạo `Budget`/trace theo `make_run_id`.
2. Dùng `run_react` với `max_steps=8`.
3. Agent bắt đầu bằng `get_claim_view`; không ghi ticket vào trace hoặc prompt.
4. Claim không tồn tại → `failed`; thiếu `order_id` → `needs_info`.
5. Dùng `lookup_order` để kiểm tra order và principal. Order không tồn tại hoặc
   ngoài phạm vi principal → `escalated`.
6. Dùng `compute_compensation` để tính quote từ order row và policy hiện hành.
   Quote bằng 0 → `denied`.
7. Quote dương được truyền nguyên vẹn vào
   `durability.issue_refund`; agent không được gọi tool ghi.
8. Host refusal → `denied`, amount conflict → `failed`, refund thành công →
   `resolved`.
9. Dùng `finish()` để lấy `refund_effects`, `committed_audit_count` từ ledger và
   ghi trace cho mọi nhánh return.
10. Truyền `crash_at` xuống host; khi `InjectedCrash` xảy ra, ghi trace rồi
    raise tiếp để kiểm tra crash/resume.

**Quyết định kỹ thuật:**

- **Ranh giới agent/host:** ReAct chỉ điều phối các tool đọc. Agent không được
  gọi `issue_refund`; approval, cap theo order, idempotency và transaction đều
  do host kiểm tra.
- **Tiền do code quyết:** proposal lấy từ `compute_compensation`, không lấy từ
  ticket hoặc nội dung trả về của MockLLM. Single Agent truyền full quote để host
  tự trừ các refund trước đó.
- **Trace an toàn:** trace chỉ ghi tool action, status, proposal amount, reason,
  kết quả refund và crash marker; không ghi ticket, `parent_secret`, raw header,
  số điện thoại, địa chỉ, tên hàng hoặc internal note.
- **Retry/crash:** sử dụng cùng idempotency key và transaction của
  `durability.issue_refund`, nên retry không tạo thêm ledger row.

## 4. Bằng chứng

Các lệnh được chạy bằng Python 3.13 trong `src\.venv`:

- `python -m pytest -q -m student -o addopts= -k "not orchestrator and not workflow and not swarm"`
  → `62 passed` cho Single Agent.
- `python -m pytest -q -m "not student"` → `76 passed` (cổng host xanh).
- 62 test Single Agent bao phủ các public claim theo seed, retry T11 và crash
  resume T12.
- Full student matrix chỉ còn các test của orchestrator fail vì shape C chưa
  triển khai.

**Commit chính:** [`13f5978`](https://github.com/phungtr/K5-L3B-DAY08-Dota-FromWorkflowsToAgents/commit/13f5978)
— `feat(single): implement run_claim and _run functions with decision logic`.
Commit này chứa phần triển khai Single Agent trong
`src/lab8/shapes/single.py`.

## 5. Công cụ AI đã dùng

- **Copilot SDK trong VS Code:** đọc contract, đối chiếu flow chung và rà lại ranh giới tool đọc/host.
- **Cách tự kiểm tra:**
  - Đối chiếu từng nhánh return với `docs/business_rules.md` và
    `docs/contracts.md`.
  - Đọc `runtime.py`, `tools.py`, `durability.py` để xác nhận agent không có
    quyền ghi refund.
  - Chạy 62 test Single Agent, test retry/crash và cổng host.
  - Kiểm tra diff để bảo đảm chỉ thay đổi shape B và tài liệu đóng góp.
- Không bịa số liệu benchmark hoặc run ID; commit hash ở trên được lấy từ Git sau
  khi commit phần Single Agent.

## 6. Tự đánh giá

Phần hoàn thành tốt là giữ được cùng flow và quy tắc return với Workflow A trong
khi thay đổi cách thu thập dữ liệu sang ReAct. Single Agent không tin ticket text,
không tự tính net refund và không có quyền ghi trực tiếp vào ledger.

Điểm còn thiếu là chưa có commit hash cuối cùng và chưa chạy benchmark đầy đủ bốn
shape vì orchestrator vẫn đang được triển khai. Bước tiếp theo là commit phần B,
phối hợp merge shape C, sau đó chạy benchmark, crash suite và cập nhật báo cáo
định lượng.
