# Team

## Thông tin nhóm

- Tên nhóm: Solo Developer (Nguyen Khoi Vinh)
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: main, commit 9b8cc3e

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Khởi Vinh | 20240000 | vinh.nk.2753@gmail.com | vinhnk2753-blip | Core Architecture & Shapes Implementation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Khởi Vinh | Core Architecture & Shapes | 9b8cc3e | tests/test_individual_vinhnk.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 20240000_NguyenKhoiVinh

### Phần việc phụ trách

- Cài đặt 3 shape: workflow, single, orchestrator tuân thủ các quy tắc nghiệp vụ LogiX-VN.
- Đảm bảo ranh giới bảo mật PII/secret và cơ chế crash-safety (20/20).
- Viết test kỹ thuật kiểm thử idempotency và policy rejection.

### Đóng góp cụ thể

- Hoàn thiện code cho `src/lab8/shapes/workflow.py`, `src/lab8/shapes/single.py`, `src/lab8/shapes/orchestrator.py`.
- Thêm test kỹ thuật cá nhân tại `src/tests/test_individual_vinhnk.py`.
- Chạy benchmark 4 shape x 14 claim x 5 seed và crash suite 20 kịch bản.

### Bằng chứng

- `src/tests/test_individual_vinhnk.py` (passed 6/6).
- `src/reports/crash.json` (crash_safety: 20/20).
- `src/reports/benchmark.json`.
