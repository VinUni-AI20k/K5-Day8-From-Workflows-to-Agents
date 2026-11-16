# Báo cáo cá nhân — 2A202603374_NguyenTuanHieu

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tuấn Hiếu.
- MSSV: 2A202603374.
- Email: tuanhieu1162004@gmail.com, theo thông tin author commit.
- GitHub cá nhân: [tuanhieu1162004](https://github.com/tuanhieu1162004), do thành viên cung cấp.
- Nhóm: 4 Thằng Sinh Viên, lớp L3A.
- Repo nhóm: https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents
- Vai trò: A — Workflow & Lead tổng hợp.

## 2. Phần việc phụ trách

- CP1: cài môi trường Python trên Windows, chạy smoke/test nền và đọc luật
  nghiệp vụ, output/trace contract cùng code tham chiếu.
- CP2: hoàn thiện Shape A trong `src/lab8/shapes/workflow.py`, giữ nguyên chữ ký
  `run_claim`, xử lý các nhánh nghiệp vụ và trả kết quả bằng `finish()`.
- CP3: kiểm chứng idempotency, truyền `crash_at` vào host và phục hồi sau crash;
  bổ sung kiểm tra checkpoint và ledger, kể cả khi đã hoàn một phần theo đơn.
- Kiểm tra an toàn thuộc phần A: approval sai claim, ticket chèn lệnh, dữ liệu
  không được đưa vào trace và quote thay đổi khi retry.
- CP5: tổng hợp `report/team/group_report.md`, hoàn thiện phân công/bảng đóng
  góp trong `TEAM.md`, đối chiếu số liệu thực chạy và đồng bộ với ADR của B.

ADR do B phụ trách; research card/ablation do C phụ trách; crash suite chính
thức, commit benchmark và kiểm tra bài nộp sau tích hợp do D phụ trách.

## 3. Đóng góp cụ thể

### Code và quyết định kỹ thuật

Workflow dùng `get_claim_view` để đọc claim, `lookup_order` để kiểm tra quyền
xem đơn và `compute_compensation` để tính quote từ order/policy. Thiếu mã đơn
trả `needs_info`; không thấy hoặc không có quyền xem đơn trả `escalated`;
quote bằng 0 trả `denied` mà không ghi refund. Claim không tồn tại trả `failed`.

Khi quote lớn hơn 0, workflow chuyển toàn bộ quote vào `issue_refund` để host
kiểm approval đúng claim, giới hạn theo đơn và idempotency. Không tự trừ tiền
đã hoàn: với T14, quote 150000 VND và refund lịch sử 30000 VND, host ghi thêm
120000 VND nhưng `proposal_amount` vẫn giữ 150000 VND.

Workflow không gọi model. Các tool đọc được ghi nhận trong `Budget`; trace
chỉ ghi quote và quyết định an toàn, không ghi ticket, raw claim/order,
secret, header, số điện thoại hoặc địa chỉ. Mỗi nhánh trả kết quả dùng
`finish()` để lấy refund/audit từ ledger và ghi trace mới.

Workflow truyền `crash_at` vào host, không bắt `InjectedCrash`; kết nối đóng
trong `finally`. Refund và audit do host ghi cùng transaction với khóa
`refund:{claim_id}`. Checkpoint là dữ liệu phục hồi tiến trình, không thay thế
ledger để xác định đã trả tiền hay chưa.

### Test đã thêm và mở rộng

File [test_workflow_safety.py](../../src/tests/test_workflow_safety.py) có 9 ca:

| Test | Nội dung và số ca |
| --- | --- |
| `test_workflow_unknown_claim_has_valid_trace_and_no_refund` | Claim không tồn tại: failed, trace hợp lệ, không refund (1). |
| `test_workflow_ignores_ticket_injection_and_does_not_log_it` | Ticket đòi bỏ policy và in canary: vẫn theo dữ liệu đơn, không ghi ticket/canary ra artifact hoặc stdout/stderr, seed 11/55 (2). |
| `test_workflow_rejects_approval_borrowed_from_another_claim` | Approval thuộc claim khác: denied, giữ quote đầy đủ, có audit `approval_claim_mismatch` (1). |
| `test_workflow_recovers_each_crash_window_with_one_refund` | Ba điểm crash; kiểm refund/audit/checkpoint trước resume và sau retry qua seed khác (3). |
| `test_workflow_missing_checkpoint_replays_partial_refund_without_double_pay` | Xóa checkpoint sau refund T14, retry seed 22/33/44/55: khôi phục checkpoint, giữ một refund và tổng hoàn đúng trần (1). |
| `test_workflow_changed_quote_on_retry_preserves_committed_amount` | Quote đổi khi retry: failed với `amount_conflict`, không sửa số tiền đã commit (1). |

### Commit chính

| Commit | Đóng góp |
| --- | --- |
| [28717d8](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents/commit/28717d8) | Hoàn thiện workflow và 8 ca safety ban đầu. |
| [33d04f3](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents/commit/33d04f3) | Mở rộng kiểm checkpoint tại ba cửa sổ crash, thêm test mất checkpoint sau partial refund và bằng chứng CP3. |
| [af4358c](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents/commit/af4358c) | Tổng hợp số liệu public vào báo cáo nhóm, hoàn thiện vai trò và đóng góp trong TEAM. |
| [2fa84ff](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents/commit/2fa84ff) | Đồng bộ hai tài liệu của A với ADR workflow mà B đã chốt. |

## 4. Bằng chứng

### Kết quả thực chạy

| Mốc và phạm vi | Kết quả |
| --- | --- |
| CP1, môi trường cá nhân | Python 3.13.14; `lab8.smoke pass`; test nền sau khi chỉ định thư mục tạm đạt 54 passed, 248 deselected. |
| CP2, riêng workflow | 62 passed trong ma trận student. |
| CP3, host và test bổ sung tại mốc thực hiện | 66 passed, 248 deselected. |
| CP3, ma trận student tại mốc thực hiện | 248 passed, 66 deselected. |
| CP5, toàn bộ host/student/test bổ sung trên mã nguồn `96ab720` | 327 passed in 12.70s. |
| Benchmark public phần workflow | 70/70 trial pass; pass rate 1.000000; pass^5 1.000000; seed min–max 1.000000–1.000000; variance 0; cost/success 27.86 VND mô phỏng; mean/p95 steps 1.64/2. |

Số test khác nhau giữa các mốc vì nhóm tiếp tục bổ sung test. Các kết quả
không phải điểm hidden và không được dùng thay kết quả chấm của giảng viên.

Lệnh tái lập sau khi chọn Python trong `.venv`, chạy từ `src/`:

```powershell
python -m lab8.smoke
python -m pytest -q -m student -o addopts= -k workflow --basetemp=.pytest-personal-workflow
python -m pytest -q tests/test_workflow_safety.py --basetemp=.pytest-personal-safety
python -m pytest -q -o addopts= -p no:cacheprovider --basetemp=.pytest-personal-all
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
```

Benchmark đã thực chạy với 14 claim × 5 seed × 4 shape, mỗi trial một SQLite
mới và cùng bảng giá MockLLM. Run dẫn chứng: `R-workflow-C-001-s11` pass.
Nguồn số liệu là JSON do lệnh benchmark sinh tại máy A và
[báo cáo nhóm](group_report.md). Tại mốc tổng hợp của A, JSON chưa được đưa vào
Git; việc kiểm tra/tái chạy và commit file thuộc D. Không sửa JSON bằng tay.

[crash.json](../../src/reports/crash.json) đạt 20/20, do D thực hiện và đưa vào
commit `96ab720`; đây là bằng chứng chung, không nhận là đóng góp cá nhân A.
Bằng chứng checkpoint/crash riêng của A ở [cp3_workflow.md](cp3_workflow.md).
Demo CP3 cho `unsafe refund rows: 2`, minh họa vì sao checkpoint đơn lẻ không
thay được ledger.

Sau tích hợp ADR `c21031b`, lần chạy `lab8.check_submission` tại máy A còn
1 FAIL do research card trống và 1 WARN vì còn file chưa commit. Chưa có
`student_drop/`, chưa chạy hidden self-check. C/D cần hoàn thiện phần được
giao trước khi xác nhận cả nhóm đủ điều kiện nộp.

Lỗi môi trường đã gặp: `py` không được nhận diện nhưng `python` chạy được;
pytest từng báo `PermissionError: [WinError 5]` ở Temp. Dùng Python có sẵn và
`--basetemp` trong workspace khắc phục được, không sửa host/test để bỏ qua lỗi.

## 5. Công cụ AI đã dùng

Sử dụng ChatGPT/Codex trong workspace để đọc đề, giải thích contract,
hướng dẫn từng bước, hỗ trợ hoàn thiện code workflow, tạo/mở rộng test,
chạy kiểm thử và benchmark, đọc kết quả, tổng hợp tài liệu, commit và push.

CP1 được thao tác qua terminal với hướng dẫn và kết quả đã cung cấp trong
cuộc trao đổi. Phần hoàn thiện code, test và các lần kiểm tra tự động sau đó
có Codex trực tiếp thực hiện; báo cáo không mô tả toàn bộ là thao tác thủ công.
Việc kiểm chứng dùng pytest, đối chiếu ledger/audit/checkpoint, kiểm tra
artifact trace và đọc JSON do công cụ chính thức sinh ra; commit được đối
chiếu với lịch sử Git. Không dùng AI để bịa số liệu, hash, run id hoặc điểm.

Code của lab vẫn chạy offline; workflow không gọi model, không dùng API key.
MockLLM chỉ là backend mô phỏng của những shape có gọi model trong benchmark.

## 6. Tự đánh giá

Phần A có code, test và lịch sử commit để đối chiếu: workflow xử lý các nhánh
nghiệp vụ public, qua kiểm tra retry/crash và có bằng chứng tổng hợp CP5.
Đóng góp tập trung vào ranh giới code/host, quote đầy đủ, idempotency và
checkpoint, cùng việc ghi nhận kết quả đúng phạm vi dữ liệu.

Hạn chế: có hỗ trợ AI đáng kể; cần tự chạy lại các lệnh tái lập và tự trình
bày được vì sao quote không trừ trước, vì sao ledger khác checkpoint và vì
sao không ghi raw context vào trace. Không tự chấm điểm hoặc khẳng định đã
thành thạo độc lập chỉ dựa vào test pass. Kết quả MockLLM/public chưa chứng
minh hiệu quả hoặc an toàn trên hidden và môi trường sản xuất.
