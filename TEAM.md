# Team

## Thông tin nhóm

- Tên nhóm: hihihaha
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-hihihaha-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
  - URL repo: https://github.com/VinUni-AI20k/K5-L3A-DAY08-hihihaha-FromWorkflowsToAgents
  - Nhánh nộp: nguyenquangvu-2A202603407
  - Commit chốt: e665c23

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Quang Vũ | 2A202603407 | vu.nq@vinuni.edu.vn | nguyenquangvu | Triển khai 4 Shapes, Benchmark & Báo cáo |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.
- Nhóm 3 người: workflow; agent systems (single + orchestrator); durability, benchmark & report.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Quang Vũ | Triển khai 4 Shapes, Benchmark & Báo cáo | e665c23 | tests/test_workflow_custom.py |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/2A202603407_NguyenQuangVu.md`.

## 2A202603407_NguyenQuangVu

### Phần việc phụ trách

- Cài đặt và tích hợp toàn bộ các kiến trúc: Shape A (Workflow), Shape B (Single Agent), Shape C (Orchestrator).
- Thực thi bộ kiểm thử crash safety 20/20 và benchmark 4 shapes × 5 seeds.
- Viết bộ unit test `tests/test_workflow_custom.py` và hoàn thiện hồ sơ báo cáo.

### Đóng góp cụ thể

- Hoàn thiện Shape A với logic tính quote cố định, tích hợp cổng duyệt host `durability.issue_refund`.
- Hoàn thiện Shape B với vòng lặp ReAct `run_react` giới hạn 8 bước, chỉ dùng read tools.
- Hoàn thiện Shape C với cơ chế handoff allowlist, điều tra viên chỉ đọc.
- Chạy sinh `src/reports/crash.json` (20/20) và `src/reports/benchmark.json` (280 trials).
- Viết hồ sơ quyết định kiến trúc (`decision_adr.md`) và phiếu nghiên cứu (`research_card.md`).

### Bằng chứng

- File test: `tests/test_workflow_custom.py` (5 tests passed).
- Báo cáo chi tiết: `report/team/2A202603407_NguyenQuangVu.md`.
