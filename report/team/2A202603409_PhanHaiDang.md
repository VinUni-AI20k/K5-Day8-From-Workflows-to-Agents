# Báo cáo cá nhân — Phan Hải Đăng

## 1. Thông tin thành viên

- Họ tên: Phan Hải Đăng
- MSSV: 2A202603409
- Email: 26ai.dangph5@vinuni.edu.vn
- GitHub: https://github.com/dangph12

## 2. Phần việc phụ trách

Ledger + evaluation; giai đoạn này tập trung tích hợp ledger và kiểm chứng retry/crash ở CP3.

## 3. Đóng góp cụ thể

Commit: `45fcb5600ab81c34ea73c8e781d7518371358825` — `feat: add ledger to shape`.

- Tích hợp `ledger.finish_refund()` vào workflow, single và orchestrator.
- Truyền quote đầy đủ và `crash_at` xuống host; để `InjectedCrash` truyền ra ngoài khi crash.
- Tái sử dụng ledger có sẵn với key `refund:{claim_id}`, không tự ghi tiền trong shape.
- Sửa import trong `tests/test_ledger_helpers.py` sau khi đổi tên module.

## 4. Bằng chứng

- [Commit tích hợp](https://github.com/hoangnguyenai/K5-L3A-DAY08-MienNui-FromWorkflowsToAgents/commit/45fcb5600ab81c34ea73c8e781d7518371358825).
- Test liên quan: `test_refund_helper_retry_and_crash_resume` kiểm tra retry và ba điểm crash; T11/T12 trong `test_public_matrix.py` kiểm tra trên các shape.

## 5. Công cụ AI đã dùng

Dùng Codex hỗ trợ chuẩn bị helper ledger, test retry/crash và tích hợp vào ba shape.

## 6. Tự đánh giá

Đã hoàn thành tích hợp ledger ở mức mã nguồn. Hiểu rằng checkpoint đơn lẻ không ngăn hoàn tiền trùng nếu crash sau effect; ledger và idempotency key giúp resume an toàn.
