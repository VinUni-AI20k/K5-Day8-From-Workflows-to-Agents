# Báo cáo cá nhân — 2A202603661_TranVietThinh

## 1. Thông tin thành viên

- Họ tên: Trần Việt Thịnh
- MSSV: 2A202603661
- Email: thinhkesat@gmail.com
- GitHub: ThinhTran-codee

## 2. Phần việc phụ trách

- **Vai trò:** Ledger/Policy/Crash + Evaluation.
- **Nhiệm vụ:**
  - Viết test kiểm thử các ràng buộc bảo vệ của Host (Policy gate, Approval validity, Order cap, Idempotency).
  - Chạy và đánh giá crash test suite (`reports/crash.json`), bảo đảm đạt chỉ tiêu 20/20.
  - Chạy benchmark đo đạc độ ổn định, chi phí, pass rate 4 kiến trúc qua 5 seed (`reports/benchmark.json`).
  - Viết mục 4 (Kết quả), mục 7 (Hạn chế) trong `group_report.md` và cung cấp số liệu thực nghiệm cho `decision_adr.md`.

## 3. Đóng góp cụ thể

- **Test đã thêm:** Xây dựng file `src/tests/test_thinh_ledger_policy.py` kiểm tra chặt chẽ các luật host và durability:
  1. `test_expired_approval_is_rejected_by_host`: Đảm bảo approval hết hạn (`expires_at < today`) bị từ chối với lý do `approval_expired` và ghi audit `policy_denied`.
  2. `test_missing_approval_record_is_rejected_by_host`: Đảm bảo claim trỏ vào approval không tồn tại bị chặn với lý do `missing_approval`.
  3. `test_non_positive_amount_is_rejected_by_host`: Kiểm tra authorization chặn các đề xuất số tiền <= 0 (`non_positive_amount`).
  4. `test_cap_at_paid_amount_minus_already_refunded`: Kiểm tra việc tính trần theo số tiền thực tế khách đã trả trừ đi phần đã hoàn (`paid_vnd - already_refunded`).
  5. `test_idempotent_replay_does_not_duplicate_audits_or_ledger`: Kiểm tra việc gọi lại nhiều lần cùng một số tiền chỉ tạo đúng 1 dòng ledger và 1 audit event `refund_committed`.
- Duy trì cổng host `python -m pytest -q` luôn xanh (59/59 passed).

## 4. Bằng chứng

- File test: `src/tests/test_thinh_ledger_policy.py` (5 passed).
- Test suite host: `python -m pytest -q` -> 59 passed.
- Nhánh làm việc: `feat/ledger-tests`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant.
- **Mục đích sử dụng:** Phân tích quy tắc trong `src/lab8/policy.py` và `src/lab8/durability.py` để phát hiện các edge case chưa có test bao phủ.
- **Kiểm chứng:** Tự chạy kiểm thử độc lập trong môi trường ảo `.venv` bằng pytest, kiểm tra các câu lệnh SQL và logic assertion trước khi xác nhận.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các yêu cầu cho thành viên ở mốc CP1 và CP2.
- Chuẩn bị sẵn bộ kiểm thử an toàn cho nhóm trước khi tích hợp các shape.
