# CP3 — Shape A: Workflow

## Phạm vi

Kiểm chứng idempotency, ledger và crash/resume của workflow. Không thay đổi
single, orchestrator, swarm hoặc các file host/thước đo. Handoff của orchestrator
thuộc phần Shape C.

## Cơ chế hiện có

`src/lab8/shapes/workflow.py` đã truyền `crash_at` vào `issue_refund` trong
commit `28717d8`. Workflow không bắt `InjectedCrash`; `finally` chỉ đóng kết nối.
Vì vậy CP3 không cần sửa thêm logic ghi tiền.

Host dùng khóa `refund:{claim_id}`. Refund và audit `refund_committed` được ghi
trong cùng transaction SQLite. Khi resume, host đọc ledger để nhận ra refund
đã commit và dựng lại checkpoint; checkpoint không phải nguồn xác định đã trả
tiền hay chưa. Shape luôn truyền quote đầy đủ để host áp trần theo đơn.

## Kiểm chứng bổ sung

Trong `src/tests/test_workflow_safety.py`:

- `test_workflow_recovers_each_crash_window_with_one_refund`: kiểm tra cả
  `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`.
  Trước resume, đối chiếu sự tồn tại của refund, audit và checkpoint theo đúng
  cửa sổ crash. Sau resume và retry với seed khác, kiểm tra một refund,
  một audit và checkpoint khớp ledger; khóa là `refund:C-012`.
- `test_workflow_missing_checkpoint_replays_partial_refund_without_double_pay`:
  C-014 có quote 150000 VND, đã được hoàn 30000 VND bởi claim trước, nên refund
  mới là 120000 VND. Sau khi xóa riêng checkpoint, chạy lại ở seed
  22, 33, 44, 55 vẫn giữ một refund và một audit cho C-014, khôi phục checkpoint,
  tổng hoàn của đơn O-515 vẫn là 150000 VND.

Trace của workflow chỉ ghi quyết định và quote, không ghi ticket hoặc raw
claim/order. Việc tóm tắt dữ liệu bằng model không thay thế allowlist/redaction.

## Lệnh và kết quả thực chạy

Chạy trong `src/`, bằng Python 3.13.14 trên Windows:

```powershell
python -m pytest -q --basetemp=.pytest-tmp-cp3-host
python -m pytest -q -m student -o addopts= --basetemp=.pytest-tmp-cp3-student
python -m lab8.demo.buggy_workflow
```

| Kiểm tra | Kết quả |
| --- | --- |
| Cổng host và test bổ sung | 66 passed, 248 deselected |
| Ma trận student public của bốn shape | 248 passed, 66 deselected |
| Demo checkpoint không thay được ledger | `unsafe refund rows: 2 (the host ledger must stay at 1)` |

Ma trận student bao gồm T11 (retry) và T12 (crash/resume) của bốn shape.
Demo tạo hai dòng trong bảng cố ý không an toàn; đây là phản ví dụ, không phải
lỗi của workflow đã triển khai.

Các kết quả trên thuộc bộ public; không phải kết quả chấm hidden. File này là
bằng chứng bổ sung cho phần A, không thay báo cáo cá nhân hoặc báo cáo nhóm.
