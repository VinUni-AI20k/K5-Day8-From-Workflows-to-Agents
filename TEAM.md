# Team

## Thông tin nhóm

- Tên nhóm: GiCungDuoc
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-GiCungDuoc-FromWorkflowsToAgents`
- URL repo, nhánh nộp, commit chốt: https://github.com/pqhuy454/K5-L3B-DAY08-GiCungDuoc-FromWorkflowsToAgents | nhánh `main` | commit `<cập nhật ở CP5>`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Quốc Huy | 2A202603897 | huymix2k4@gmail.com | pqhuy454 | Lead & QA Integration |
|   2 | Trịnh Gia Huy | 2A202603924 | trgyahuy1710@gmail.com | TrGiaHuy1710-valid | Durability, Eval & Benchmark Lead |
|   3 | Trần Tùng Lâm | 2A202603893 | lamtt262004@gmail.com | lamtt262004 | Shape A Workflow Lead |
|   4 | Đặng Đức Minh | 2A202603886 | ddminh1102@gmail.com | DMinh1102 | Shape B Single ReAct |
|   5 | Nguyễn Thành Tâm | 2A202603933 | ngthanhtamtb@gmail.com | ngthanhtamtb | Shape C & Security Lead |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.
- Nhóm 5 người: xem phân công chi tiết tại LAB8_REQUIREMENTS_AND_PLAN.md.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Phạm Quốc Huy | Lead & QA Integration | `<cập nhật sau khi commit>` | `src/tests/test_student_integration.py` |
| Trịnh Gia Huy | Durability, Eval & Benchmark Lead | `<chờ commit>` | `chờ` |
| Trần Tùng Lâm | Shape A Workflow Lead | `<chờ commit>` | `chờ` |
| Đặng Đức Minh | Shape B Single ReAct | `<chờ commit>` | `chờ` |
| Nguyễn Thành Tâm | Shape C & Security Lead | `<chờ commit>` | `chờ` |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603886_DangDucMinh

### Phần việc phụ trách

- Chịu trách nhiệm toàn quyền Shape B — Single Agent ReAct (`src/lab8/shapes/single.py`).
- Xây dựng vòng lặp ReAct (`run_react`) với giới hạn 8 bước (`max_steps=8`), chạy dưới quyền worker chỉ đọc (`worker=True`).
- Thiết kế hàm `decide(observation)` tuần tự, miễn nhiễm với prompt injection và phớt lờ số ngày trễ sai lệch trong ticket.
- Quản lý ranh giới Code/Host: chuyển quote đầy đủ vào `durability.issue_refund`, truyền `crash_at` và flush trace đúng chuẩn Trace contract v1.
- Viết 5 unit tests độc lập tại `src/tests/test_student_single.py`.

### Đóng góp cụ thể

- Triển khai hoàn chỉnh `src/lab8/shapes/single.py`, vượt qua 62/62 student matrix tests.
- Viết bộ test `src/tests/test_student_single.py` kiểm tra prompt injection, step cap, write-tool blocking và budget tracking.
- Tuân thủ nghiêm ngặt 3 điều kiện Must-Pass (không bypass approval, không rò rỉ secret/PII, an toàn crash).

### Bằng chứng

- File mã nguồn: `src/lab8/shapes/single.py`, `src/tests/test_student_single.py`.
- Báo cáo cá nhân: `report/team/2A202603886_DangDucMinh.md`.
- Kết quả test: 62/62 student test matrix Shape B pass, 59/59 host test pass, `check_submission` xác nhận `shape single: format đúng, 12/12 claim public pass ở seed 11`.
