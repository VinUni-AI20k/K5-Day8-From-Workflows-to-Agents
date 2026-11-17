# Ranh giới bảo mật của orchestrator

## Handoff

Handoff được tạo bằng `lab8.handoff.make_handoff`, contract `handoff.v1`.
Các field cấp cao được phép: `contract_version`, `request_id`, `claim_id`,
`principal_scope`, `task`, `facts`, `allowed_tools`, `max_output_tokens`.
Allowlist của `facts` gồm `delay_days`, `damage_verified`, `carrier`,
`order_status`, `shipping_fee_vnd`, `paid_vnd`. Triển khai hiện tại gửi `facts={}`;
investigator tự đọc lại dữ liệu qua tool có kiểm principal.

Orchestrator chỉ giao `lookup_order`, `lookup_policy`, `lookup_refund_history`.
Investigator không được gọi `issue_refund` hoặc `append_audit`.
Orchestrator gọi `compute_compensation` từ order view và chuyển quote đầy đủ cho
host. Approval, cap theo đơn và idempotency được kiểm trong host.

## Dữ liệu không được chuyển hoặc ghi log

- Không chuyển `parent_secret`, raw header, lịch sử hội thoại hay claim row thô.
- Không đưa ticket vào prompt, handoff hoặc trace: ticket có thể chứa dữ liệu
  nhạy cảm và câu lệnh giả mạo.
- Không ghi số điện thoại, địa chỉ, tên hàng, ghi chú nội bộ vào trace, kết quả
  hoặc stdout/stderr. Trace cũng không ghi carrier và order ID tự do.
- Tóm tắt bằng model không thay thế allowlist.

## Trace và crash

Trace có các event `claim`, `handoff`, `investigator`, `quote`, `refund_request`,
`refund_outcome`, `decision`, tùy nhánh. Chỉ ghi trạng thái, số đếm, số tiền,
lý do do code tạo và handoff đã sanitize. Mỗi kết quả bình thường đi qua
`common.finish()` để ghi trace mới, đọc effect/audit thật từ ledger và tổng hợp
Budget. Trace được flush trước khi gọi host để điểm crash vẫn có bằng chứng an toàn.
`crash_at` được truyền nguyên vẹn; `InjectedCrash` không bị bắt trong shape.
Connection đóng trong `finally`, cả khi crash.

## Lệnh tái lập

Chạy trong `src/`, sau khi kích hoạt môi trường ảo:

```text
python -m pytest -q tests/test_team_orchestrator.py --basetemp=.pytest_cache/tmp-minh
python -m pytest -q -m student -o addopts= -k orchestrator --basetemp=.pytest_cache/tmp-orchestrator
python -m tests.audit_team_security --out reports/orchestrator_security.json
```

Audit chạy 14 claim public × 5 seed trên cả bốn shape; quét `RunResult`, trace,
file cùng thư mục có tiền tố run ID và stdout/stderr. Tập chuỗi cấm lấy từ toàn
bộ secret và field PII của fixture public. Report chỉ ghi số đếm, không ghi giá
trị nhạy cảm. Kiểm approval đối chiếu dòng ledger với approval và principal gốc.

Audit bảo mật không thay cho kiểm tra nghiệp vụ: shape stub có thể không lộ dữ
liệu vì chưa làm việc; report ghi riêng `not_implemented_trials` và `public_passed`.
Đây là bằng chứng public, không phải điểm hidden chính thức.

## Kết quả tại commit triển khai a06249f

- Test nhóm: 15 passed; ma trận orchestrator: 62 passed.
- Cổng host và test nhóm hiện có: 77 passed, 248 deselected.
- Audit 4 shape × 14 claim × 5 seed: 280 trial; 0 secret leak, 0 PII leak,
  0 approval bypass, 0 trace contract failures, 0 unexpected ledger trial.
- Orchestrator pass 70/70 trial public; workflow còn 70 trial stub. Single pass
  70/70; swarm pass 69/70 (điểm yếu T02/seed 55).
- Suite host + swarm: 20/20; ba cửa sổ crash riêng của orchestrator qua test nhóm.
- Không có `student_drop/`; chưa có bằng chứng hidden chính thức.
