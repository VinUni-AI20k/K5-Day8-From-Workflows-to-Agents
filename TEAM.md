# Team

## Thông tin nhóm

- Tên nhóm: DatToanAnKhanhQuan
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/datnguyen101004/K5-L3A-DAY08-DatToanAnKhanhQuan-FromWorkflowsToAgents, phamnguyentatdat

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Nguyễn Tất Đạt | datnguyen101004 | datnguyen101004@gmail.com | datnguyen101004 | Integration & Host / Eval |
|   2 | Nguyễn Ngọc Toàn | 2A202603405 |       | jpack1 | Shape B — single agent |
|   3 | Phan Bá An | 2A202603375 |       | anphn3 | Shape C — orchestrator + handoff |
|   4 | Khánh | | | | Orchestrator (Shape C) |
|   5 | Lê Hoàng Quân | 2A202603369|lehoangquanvcb@gmail.com | lehoanquanvcb| Evaluation & Report |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Nguyễn Tất Đạt | integration | 7158031 | tests/test_integration_harness.py |
| Nguyễn Ngọc Toàn (2A202603405, jpack1) | Shape B — single ReAct agent (`src/lab8/shapes/single.py`) | 307a9a4 | `src/tests/test_single_shape.py` (thêm mới) |
| Phan Bá An (2A202603375, anphn3) | Shape C — orchestrator + read-only investigators (`src/lab8/shapes/orchestrator.py`) | 5002904 | `src/tests/test_orchestrator_shape_c.py` (thêm mới, 7 test) |
| Lê Hoàng Quân | Shape A — Deterministic Workflow (Issue #2) | `4e5c355` | `src/tests/test_workflow.py::test_workflow_unknown_claim_returns_failed_without_refund` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-

## datnguyen101004_PhamNguyenTatDat

### Phần việc phụ trách

- Integration: Thiết lập môi trường Python 3.12, kích hoạt venv, kiểm định smoke test, duy trì cổng host pytest luôn xanh, chạy Crash suite (20/20), bổ sung integration test harness và kiểm định checklist submission.

### Đóng góp cụ thể

- Cài đặt virtual environment `.venv` và dependencies (`requirements.txt`).
- Xây dựng bộ test harness `src/tests/test_integration_harness.py` kiểm định môi trường runtime Python 3.11–3.13, SQLite, tính toàn vẹn 14 public claims, cấu hình YAML và crash safety.
- Chạy sinh `src/reports/crash.json` đạt chuẩn must-pass 20/20.

### Bằng chứng

- `tests/test_integration_harness.py` (4 passed)
- `src/reports/crash.json` (`crash_safety: 20/20`)

## 2A202603369_LeHoangQuan

### Phần việc phụ trách

- Shape A — xây dựng luồng xử lý claim tất định cho LogiX-VN theo Issue #2.

### Đóng góp cụ thể

- Triển khai `run_claim` trong `src/lab8/shapes/workflow.py`. Workflow kiểm tra mã đơn và quyền truy cập, tính số tiền đề xuất từ dữ liệu đơn hàng và policy hiện hành, rồi chuyển toàn bộ số tiền đề xuất cho host kiểm tra approval và ghi refund.
- Truyền `crash_at` cho host để kiểm thử khôi phục sau sự cố. Ghi trace cho cả các nhánh trả kết quả sớm.
- Thêm test cho mã claim không tồn tại, kiểm tra trạng thái `failed`, lý do `unknown_claim`, số dòng ledger giữ nguyên và trace có `run_id` khớp với kết quả.

### Bằng chứng

- Commit kỹ thuật `4e5c355` — Implement deterministic workflow and test unknown claim.
- Test thêm mới `src/tests/test_workflow.py::test_workflow_unknown_claim_returns_failed_without_refund`.
- Kết quả đã ghi nhận: 62 test trong ma trận public của Shape A và 54 test trong bộ mặc định đều pass.
