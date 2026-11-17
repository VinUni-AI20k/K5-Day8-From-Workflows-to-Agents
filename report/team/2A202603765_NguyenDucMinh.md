# Báo cáo cá nhân — Nguyễn Đức Minh — 2A202603765

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Minh
- MSSV: 2A202603765
- Email: 26ai.minhnd5@vinuni.edu.vn
- GitHub: https://github.com/miao1114

## 2. Phần việc phụ trách

Phụ trách Shape A — deterministic workflow tại [`src/lab8/shapes/workflow.py`](../../src/lab8/shapes/workflow.py)

Phạm vi đã thực hiện:

- **CP2, phần workflow:** thay stub `not_implemented` bằng quy trình xử lý claim cố định, trả `RunResult` và trace đúng contract.
- **CP3, phần workflow:** chuyển tiếp `crash_at` cho host, không bắt `InjectedCrash`, sử dụng cơ chế ledger và idempotency có sẵn để hỗ trợ retry và resume.


## 3. Đóng góp cụ thể

Các thay đổi đã thực hiện :

1. **Giữ nguyên chữ ký `run_claim`.** Khởi tạo kết nối SQLite, `Budget` và `Trace` với `make_run_id("workflow", claim_id, seed)`.
2. **Đọc claim qua `get_claim_view`.** Claim không tồn tại trả `failed` với lý do `unknown_claim`; thiếu `order_id` trả `needs_info`. Không lấy mã đơn từ nội dung ticket.
3. **Kiểm tra quyền truy cập đơn qua `lookup_order`.** Đơn không tồn tại hoặc principal không sở hữu đơn trả `escalated`. Chỉ sử dụng dữ liệu đơn đã qua allowlist.
4. **Tính số tiền bằng `compute_compensation`.** Dùng dữ liệu order và policy hiện hành; không dùng số ngày trễ khách ghi trong ticket để thay dữ liệu database. Quote bằng 0 trả `denied` và không gọi ghi refund.
5. **Truyền quote đầy đủ vào `issue_refund`.** Để host kiểm approval, giới hạn theo đơn và phần tiền đã hoàn. Không tự trừ tiền trước khi gọi host. Host từ chối trả `denied`; xung đột số tiền trả `failed`; host chấp nhận trả `resolved`.
6. **Hỗ trợ crash/retry.** Truyền nguyên `crash_at` vào `issue_refund` và để `InjectedCrash` truyền ra ngoài. Không tự ghi ledger hay checkpoint. Luôn đóng kết nối trong `finally`.
7. **Thống nhất kết quả và trace.** Thêm hàm nội bộ `respond()` gọi `finish()` trên mọi nhánh trả kết quả. `finish()` đọc effect và số audit committed từ database thay vì tự gán. Lưu trace trước khi gọi host để có dấu vết khi crash thử nghiệm xảy ra.
8. **Theo dõi chi phí và hạn chế dữ liệu ghi log.** Cộng số lượt gọi tool bằng `Budget`; không gọi MockLLM vì workflow chỉ cần các bước cố định. Không ghi ticket, parent secret, header, số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng vào trace.

Ví dụ kỹ thuật: ở T14, entitlement là 150.000 VND và đơn đã được hoàn 30.000 VND. Workflow vẫn truyền proposal 150.000 VND; host tự trừ phần đã hoàn và chỉ ghi thêm 120.000 VND. Nếu workflow tự trừ trước thì host sẽ trừ lần thứ hai.

- **Commit chính:** `5cbc99e0b10f90aeacb2a54e962b557e94184f6a` — `feat(workflow): implement claim processing and crash recovery`, gồm phần triển khai workflow CP2–CP3 và báo cáo cá nhân. Commit đã được push lên remote; nhánh hiện tại là `Workflow_CP2,3` (đổi tên từ `Workflow_CP1`).
- **Test đã thêm:** bổ sung 3 test trong [`src/tests/test_workflow.py`](../../src/tests/test_workflow.py) với sự hỗ trợ của Codex: claim không tồn tại vẫn ghi trace hợp lệ và không thay đổi ledger; thiếu approval giữ quote đầy đủ nhưng không hoàn tiền, có audit từ chối; quote thay đổi khi retry báo xung đột và giữ nguyên refund cũ. File test được đưa vào commit `test(workflow): cover unknown claims, approval denial and retry conflicts` cùng bản cập nhật báo cáo này.

## 4. Bằng chứng

File triển khai: [`workflow.py`](../../src/lab8/shapes/workflow.py).

Các lệnh dưới đây chạy từ thư mục `src/`. Trong phiên làm việc, chạy chúng bằng `uv run` với Python **3.12.16**, pytest và PyYAML trong môi trường tạm vì lệnh `python` mặc định trên máy không hoạt động và Python 3.12 ban đầu chưa có pytest.

| Kiểm tra | Lệnh Python tương ứng | Kết quả thực tế |
| --- | --- | --- |
| Ma trận student riêng workflow | `python -m pytest -q -m student -o addopts= -k workflow` | **62 passed, 240 deselected** |
| Smoke của starter | `python -m lab8.smoke` | **lab8.smoke pass** |
| Bộ test host mặc định | `python -m pytest -q` | **54 passed, 248 deselected** |
| Định dạng diff | `git diff --check` | Không báo lỗi whitespace |

Sau khi bổ sung 3 test trong `tests/test_workflow.py`, Tôi chạy lại lệnh lọc workflow ở trên và nhận kết quả **65 passed, 240 deselected in 2.81s** (62 test có sẵn và 3 test mới). Các test mới được đánh dấu `student`, dùng database và thư mục trace tạm riêng cho từng test.

Các test workflow đã chạy nằm trong [`test_public_matrix.py`](../../src/tests/test_public_matrix.py):

- `test_public_single_run_cases`: 12 claim × 5 seed (`11, 22, 33, 44, 55`), tổng 60 trường hợp; kiểm tra qua `trial_pass` cả kết quả, ledger và trace.
- `test_t11_retry_keeps_one_refund`: chạy lại cùng claim vẫn chỉ có một refund.
- `test_t12_crash_before_checkpoint_does_not_double_pay`: crash tại `after_effect_before_checkpoint`, sau đó chạy tiếp vẫn chỉ có một refund.

Các con số trên là output kiểm tra trong phiên làm việc, chưa phải benchmark hay kết quả hidden. Chưa chạy riêng crash suite `20/20` để tạo `src/reports/crash.json` trong phần việc này.

## 5. Công cụ AI đã dùng

**Công cụ:** Codex.

**Cách sử dụng:** yêu cầu AI đọc `CHECKPOINTS.md`, luật nghiệp vụ, contract, code host và swarm tham chiếu; hỗ trợ thay hai mục TODO trong workflow; giải thích các nhánh xử lý, quote đầy đủ, approval, trace và crash/retry.

**Kiểm chứng đã thực hiện trong phiên:** Codex chạy ma trận 62 test workflow, smoke, 54 test host và `git diff --check`; kết quả cụ thể ghi ở mục 4. AI không sửa các file thước đo và không sửa tay JSON report.

**Phần tự kiểm tra của thành viên:** tôi đã tự chạy bộ test student riêng cho workflow từ thư mục `src/`. Kết quả terminal trả về:

```text
62 passed, 240 deselected in 2.71s
```

Kết quả xác nhận toàn bộ 62 test workflow công khai đều pass, bao gồm các trường hợp xử lý claim, chạy lại không hoàn trùng (T11) và crash rồi resume (T12). `240 deselected` là các test ngoài phạm vi workflow được bỏ qua, không phải test lỗi. Tôi dùng kết quả chạy test thực tế để kiểm chứng code do AI hỗ trợ, thay vì chỉ dựa vào giải thích của AI. Kết quả này chưa thay thế cho crash suite `20/20`, benchmark hoặc kiểm tra hidden.

## 6. Tự đánh giá

Theo bằng chứng hiện có, phần workflow đạt 62 test student công khai, xử lý được retry và crash/resume trong T11, T12; bộ test host vẫn xanh. Đây là kết quả kiểm chứng cho phạm vi workflow, chưa chứng minh kết quả hidden hoặc hoàn thành toàn bộ bài nhóm.

Các điểm kỹ thuật cần nắm để giải thích bài: tiền do code tính từ order và policy; ticket là dữ liệu người dùng; host là nơi duy nhất ghi refund; phải truyền quote đầy đủ; ledger và idempotency ngăn hoàn trùng; trace chỉ ghi dữ liệu được phép.

Việc còn cần hoàn thiện cho phần đóng góp cá nhân: cập nhật bảng đóng góp trong `TEAM.md`. Commit triển khai workflow đã được tạo và ghi hash ở mục 3; ba test bổ sung được đưa vào commit cùng bản cập nhật báo cáo này. Việc chạy crash suite, benchmark và kiểm tra hidden cần được nhóm thực hiện ở các checkpoint tiếp theo.
