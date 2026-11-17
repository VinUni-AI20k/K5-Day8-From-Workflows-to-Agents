# Team

## Thông tin nhóm

- Tên nhóm: NhomDMTG
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-NhomDMTG-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/TDM414/K5-L3B-DAY08-NhomDMTG-FromWorkflowsToAgents · nhánh `main` · commit chốt code & report: `1f4bca2`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Trần Duy Mạnh | 2A202603998 | duymanhtran2004mkc2@gmail.com | TDM414 | Task 4 — Ledger safety + đánh giá |
|   2 | Nguyễn Xuân Dương | 2A202603955 | xuanduong20050808@gmail.com | xuanduong2k5 | Task 3 — Orchestrator + handoff |
|   3 | Trần Thị Hồng Gấm | 2A202603967 | tranthihonggam290905@gmail.com | Honggam1109 | Task 1 — Workflow + tích hợp |
|   4 | Đinh Lê Thịnh | 2A202603953 | dinhlethinh137@gmail.com | ThinkLee04 | Task 2 — Single agent |

## Phân công công việc

| Task | Thành viên | Vai trò | Phần việc chính | Đầu ra và tự kiểm |
| --- | --- | --- | --- | --- |
| Task 1 | Trần Thị Hồng Gấm (`2A202603967`) | Workflow + tích hợp | Hoàn thiện `src/lab8/shapes/workflow.py`; điều phối tích hợp ba shape và giữ cổng host xanh. | Test `src/tests/test_workflow.py`; kiểm tra dùng `common.finish()`, giữ nguyên chữ ký `run_claim`, không lấy số ngày từ ticket. |
| Task 2 | Đinh Lê Thịnh (`2A202603953`) | Single agent | Hoàn thiện `src/lab8/shapes/single.py` bằng ReAct, tối đa 8 bước; model chỉ chọn công cụ đọc, code gọi host để ghi refund. | Test `src/tests/test_single_agent.py`; kiểm tra số tiền do code tính và truyền quote đầy đủ cho host. |
| Task 3 | Nguyễn Xuân Dương (`2A202603955`) | Orchestrator + handoff | Hoàn thiện `src/lab8/shapes/orchestrator.py`; investigator chỉ đọc và handoff phải qua `make_handoff`. | Test `src/tests/test_orchestrator.py`; trace chỉ ghi handoff đã sanitize, không đưa secret, dữ liệu thô hay công cụ ghi qua handoff. |
| Task 4 | Trần Duy Mạnh (`2A202603998`) | Ledger safety + đánh giá | Kiểm thử idempotency, approval, giới hạn hoàn theo đơn và crash; chạy benchmark, tổng hợp báo cáo. Không sửa `durability.py`, `policy.py`, metrics, config hoặc dữ liệu. | Kiểm tra T11/T12, crash suite 20/20 (`src/reports/crash.json`), benchmark (`src/reports/benchmark.json`), `src/tests/test_submission_standards.py`, điền ADR, research card, báo cáo nhóm. |

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Trần Duy Mạnh | Ledger safety + đánh giá (Task 4) | `1f4bca2` | `src/tests/test_submission_standards.py` |
| Nguyễn Xuân Dương | Orchestrator + handoff (Task 3) | `9c628ba` | `src/tests/test_orchestrator.py` |
| Trần Thị Hồng Gấm | Workflow + tích hợp (Task 1) | `03ce5b8` | `src/tests/test_workflow.py` |
| Đinh Lê Thịnh | Single agent (Task 2) | `b2ed187` | `src/tests/test_single_agent.py` |

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
