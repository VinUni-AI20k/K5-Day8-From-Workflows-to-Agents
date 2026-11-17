# Team

## Thông tin nhóm

- Tên nhóm: ABC
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-ABC-FromWorkflowsToAgents` (xem [SUBMISSION.md](SUBMISSION.md))
- URL repo, nhánh nộp, commit chốt:
  - https://github.com/tundut/K5-L3B-DAY08-ABC-FromWorkflowsToAgents
  - nhánh: `main`
  - commit chốt: _(điền khi nộp)_

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Huỳnh Văn Cường | 2A202603866 |  | cuong-huynh | Workflow |
|   2 |        |      |       |        | Single agent |
|   3 |        |      |       |        | Orchestrator và handoff |
|   4 |        |      |       |        | Kiểm thử và an toàn |
|   5 |        |      |       |        | Nhóm trưởng, tích hợp và đánh giá |

## Phân công cho 5 thành viên

Số thành viên bên dưới tương ứng với STT trong bảng trên. Họ tên và thông tin cá nhân để trống để nhóm bổ sung.

| Thành viên | Công việc phụ trách | Sản phẩm bàn giao | Test cần tự viết |
| --- | --- | --- | --- |
| 1 | Viết workflow cố định: đọc claim, kiểm quyền truy cập đơn, tính quote bằng code, gọi host và trả kết quả có trace ở mọi nhánh | `src/lab8/shapes/workflow.py`; phần mô tả workflow trong mục 3 báo cáo nhóm | Ticket nói sai số ngày; thiếu `order_id`; đơn không thuộc principal |
| 2 | Viết single agent bằng `run_react`, tối đa 8 bước; model chỉ chọn tool đọc; code tính tiền và gọi host; ghi nhận model call và budget | `src/lab8/shapes/single.py`; phần mô tả ReAct và chi phí trong báo cáo nhóm | Giới hạn 8 bước; không cho model gọi tool ghi; ticket có lệnh “ignore policy” |
| 3 | Viết orchestrator và investigator; tạo handoff bằng `make_handoff`; investigator chỉ đọc; trace chỉ ghi handoff đã sanitize | `src/lab8/shapes/orchestrator.py`; phần mô tả handoff và ranh giới quyền trong báo cáo nhóm | Handoff không chứa secret; investigator không có tool ghi; xử lý thiếu dữ kiện |
| 4 | Kiểm thử cả 3 shape về approval, idempotency, crash/resume, trần hoàn tiền theo đơn và rò secret/PII; phối hợp chủ shape sửa lỗi | Test mới trong `src/tests/`; `src/reports/crash.json` do công cụ sinh; nội dung kiểm thử và khó khăn cho báo cáo nhóm | Approval sai claim; crash rồi resume; gọi lại không ghi trùng; hoàn đúng phần chênh |
| 5 | Quản lý tích hợp và merge; chạy benchmark; chủ trì research card và ablation; tổng hợp ADR, báo cáo và kiểm tra bài nộp | `src/reports/benchmark.json`; `TEAM.md`; `report/team/group_report.md`, `decision_adr.md`, `research_card.md` | Test tham số hóa cả 3 shape để kiểm contract của `RunResult` và trace trên các nhánh return sớm |

### Tiến độ và phối hợp

| Checkpoint | Công việc và điều kiện bàn giao |
| --- | --- |
| CP1 — 13:30–13:45 | Cả nhóm cài môi trường, chạy smoke và test host; đọc luật nghiệp vụ và contract; điền thông tin thành viên |
| CP2 — 13:45–14:30 | Thành viên 1–3 viết song song từng shape; thành viên 4 viết test an toàn; thành viên 5 chuẩn bị khung báo cáo, giả thuyết nghiên cứu và kế hoạch đo |
| CP3 — 14:30–15:15 | Tích hợp lần đầu; hoàn thiện handoff, trace, idempotency và crash; kiểm T11, T12 trên từng shape |
| CP4 — 15:30–16:15 | Thành viên 4 chủ trì kiểm approval, secret và crash; chủ shape sửa lỗi; thành viên 5 kiểm bản tích hợp |
| CP5 — 16:15–17:00 | Chạy benchmark 4 shape × 5 seed; thực hiện ablation; tự kiểm `student_drop/` nếu được phát; chọn kiến trúc dựa trên số liệu |
| Chốt bài — 17:00–17:30 | Hoàn thiện báo cáo và bằng chứng đóng góp; chạy `check_submission`; push; mỗi người tự nộp cùng link repo lên LMS |

Các mốc trên là lịch lab mẫu, không phải deadline nộp bài. Deadline theo `SUBMISSION.md` và thông báo của coach.

- Thành viên 1–3 sở hữu file shape tương ứng, giữ nguyên chữ ký `run_claim` và dùng `finish()` để tạo kết quả, ghi trace ở mọi nhánh.
- Thành viên 4 báo lỗi kèm claim, seed, kết quả mong đợi và thực tế; chủ shape sửa code của mình. Không sửa host để làm test xanh.
- Thành viên 5 quản lý file báo cáo chung và sinh bộ JSON bằng chứng cuối cùng sau khi tích hợp. Mỗi chủ shape cung cấp phần giải pháp của mình.
- Research card và ablation là phần bài chính: thành viên 5 chủ trì chọn một câu R1–R4; thành viên 1–3 hỗ trợ biến thể; thành viên 4 kiểm chỉ thay đổi một biến và giữ cố định model, tools, seed, corpus, giá, evaluator.
- Mỗi người có commit kỹ thuật, ít nhất một test thêm hoặc sửa, và báo cáo cá nhân ghi công cụ AI đã dùng cùng cách tự kiểm tra. Bổ sung bằng chứng thật vào bảng đóng góp sau khi hoàn thành.

### Điều kiện nghiệm thu

- Mỗi shape qua bộ student của mình (đề dự kiến 62 test/shape); test host và toàn bộ ma trận student xanh.
- Tiền do code tính; truyền quote đầy đủ vào `durability.issue_refund`; truyền `crash_at` và không bắt `InjectedCrash`.
- Không refund khi thiếu approval hợp lệ; không lộ secret/PII qua trace, kết quả hoặc stdout; gọi lại và crash/resume không tạo refund trùng.
- `src/reports/crash.json` đạt `20/20`. Crash suite có sẵn kiểm host/swarm; vẫn phải kiểm T12 trên từng shape nhóm viết.
- Benchmark đủ 4 shape, ít nhất 10 claim, seed `11,22,33,44,55`; JSON được công cụ sinh, không sửa tay.
- ADR ghi shape chọn, commit hash, run id và số liệu thật. Shape chọn phải đạt hidden pass rate ≥ 0.75 khi giảng viên chấm; tự kiểm trên `student_drop/` không có nhãn nên không xác nhận được pass rate.
- `python -m lab8.check_submission` ra `0 FAIL`; đủ báo cáo nhóm, ADR, research card và 5 báo cáo cá nhân.
- Không sửa thước đo: `src/lab8/metrics.py`, `durability.py`, `policy.py`, `src/config/*.yaml`, `src/data/*`. Code triển khai bài chính nằm trong 3 file shape; chỉ dùng MockLLM, không gọi model thật.
- Không commit secret, `.env`, `.venv/`, trace, `*.sqlite`, `student_drop/` hoặc `src/eval/instructor/`.
- Ưu tiên hoàn thành bài chính; bonus chỉ triển khai khi còn thời gian và đáp ứng các điều kiện trong rubric.

## Bảng đóng góp

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Huỳnh Văn Cường | Workflow | ce1d813 | `test_workflow_owner.py` (C-002 ticket sai ngày; C-004 thiếu order_id; C-005 ngoài principal) |
| | Single agent | | |
| | Orchestrator và handoff | | |
| | Kiểm thử và an toàn | | |
| | Tích hợp và đánh giá | | |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## 2A202603866_HuynhVanCuong

### Phần việc phụ trách

- Shape A `workflow` (`src/lab8/shapes/workflow.py`): pipeline cố định đọc claim → order → quote → `issue_refund`.

### Đóng góp cụ thể

- Implement `run_claim` (CP2+CP3): tool trực tiếp, full quote, truyền `crash_at`, không bắt `InjectedCrash`.
- Thêm `src/tests/test_workflow_owner.py`.

### Bằng chứng

- Student matrix: `pytest -q -m student -o addopts= -k workflow` → 62 passed.
- Owner tests: `pytest -q -m student -o addopts= -k workflow_owner`.
- Báo cáo cá nhân: `report/team/2A202603866_HuynhVanCuong.md`.
