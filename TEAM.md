# Team

## Thông tin nhóm

- Tên nhóm: Mien Nui
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-MienNui-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt: https://github.com/hoangnguyenai/K5-L3A-DAY08-MienNui-FromWorkflowsToAgents

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Lâm Hoàng | 2A202603448 | 26ai.hoangnl@vinuni.edu.vn | [hoangnguyenai](https://github.com/hoangnguyenai) | Workflow + integration |
|   2 | Nguyễn Tiến Khoa| 2A202603460 | nkhoa151004@gmail.com| llkhoa| single|
|   3 | Nguyễn Tuấn Quang | 2A202603392 | quangbg04@gmail.com | quangbg004 | Orchestrator + Handoff |
|   4 | Phan Hải Đăng | 2A202603409 | 26ai.dangph5@vinuni.edu.vn | [dangph12](https://github.com/dangph12) | ledger + evaluation |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Nguyễn Lâm Hoàng | Workflow + integration; bonus B3 | `2fbe693` | `src/tests/test_workflow_integration.py` (28 ca), `src/tests/test_shapes_integration.py` (17 ca), `src/tests/test_bonus_swarm_verified.py` (101 ca) |
| Nguyễn Tuấn Quang | Orchestrator + Handoff | `8939976` | `src/tests/test_orchestrator_handoff.py` (1 ca tích hợp) |
| Nguyễn Tiến Khoa | Single| fe3f57d| `src/tests/test_single_agent.py` (11 ca mới) |
## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603448_NguyenLamHoang

### Phần việc phụ trách

- Shape workflow và tích hợp với host: contract, approval, ledger, trace và crash/resume.

### Đóng góp cụ thể

- Triển khai workflow, tích hợp ba shape với host, bổ sung 45 ca kiểm thử và chạy benchmark bốn shape trên 14 claim × 5 seed.

### Bằng chứng

- [Báo cáo cá nhân](report/team/2A202603448_NguyenLamHoang.md).
- [Benchmark bốn shape](src/reports/benchmark.json), [crash suite](src/reports/crash.json).

## 2A202603392_NguyenTuanQuang

### Phần việc phụ trách

- Shape C (`orchestrator`) và handoff cho investigator chỉ đọc.

### Đóng góp cụ thể

- Triển khai `handoff.v1` với `lookup_order` giới hạn theo chủ sở hữu đơn. Orchestrator tính đề xuất từ dữ liệu đơn và policy hiện hành rồi chuyển toàn bộ số tiền đề xuất cho host.
- Bổ sung test tích hợp kiểm payload gửi cho investigator và kiểm rò rỉ dữ liệu trong trace, kết quả, stdout và stderr.

### Bằng chứng

- Commit `8939976` và [test handoff](src/tests/test_orchestrator_handoff.py).
- [Báo cáo cá nhân](report/team/2A202603392_NguyenTuanQuang.md).
