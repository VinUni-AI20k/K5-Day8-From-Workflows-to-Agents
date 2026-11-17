# Team

## Thông tin nhóm

- Tên nhóm:
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 |        |      |       |        |         |
|   2 | Đào Văn Hiệp | 2A202603813 | 26ai.hiepdv3@vinuni.edu.vn | [daohiep2903](https://github.com/daohiep2903) | Single agent, kiểm thử và mô tả ReAct, budget |

Gợi ý chia vai:

- Nhóm 6 người: integration; workflow; single agent; orchestrator; ledger/policy/crash; eval/report.
- Nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Đào Văn Hiệp — 2A202603813 | Triển khai `single.py` bằng `run_react` tối đa 8 bước, giới hạn tool đọc, tích hợp host hoàn tiền, budget và trace. Bổ sung mô tả Single trong báo cáo nhóm. | [1b1469c](https://github.com/tundut/K5-L3B-DAY08-ABC-FromWorkflowsToAgents/commit/1b1469ce65b345666314cee04f4528b497e8ebc8) | `src/tests/test_single.py` — 13 test pass, gồm đầu vào, ticket đối kháng, giới hạn bước, chặn tool ghi, quote đầy đủ, crash/resume và conflict. Ma trận public riêng Single đạt 62/62. |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603813_DaoVanHiep

### Phần việc phụ trách

- Shape B, Single agent trong `src/lab8/shapes/single.py`.
- Test bổ sung trong `src/tests/test_single.py` và nội dung ReAct, budget trong báo cáo nhóm.

### Đóng góp cụ thể

- Xử lý claim, vòng ReAct giới hạn 8 bước, gọi tool đọc và tính quote bằng code.
- Tích hợp `durability.issue_refund`, truyền quote đầy đủ và `crash_at`, xử lý approval, retry và conflict.
- Ghi model call, token, chi phí mô phỏng và trace chọn lọc.
- Bổ sung test cho cả ba điểm crash/resume và các tình huống an toàn của Single.

### Bằng chứng

- Báo cáo cá nhân tại [2A202603813_DaoVanHiep.md](report/team/2A202603813_DaoVanHiep.md).
- Kết quả đã chạy gồm 13 test bổ sung pass, 62 test student riêng Single pass và bộ host đạt 67 passed.
- Run id minh họa `R-single-C-014-s11`, quote 150.000 VND và refund 120.000 VND.
- Commit code và test `1b1469ce65b345666314cee04f4528b497e8ebc8`, nhánh `hiep-sigle-agent`.
