# Báo cáo cá nhân — 2A202603397_VoHuyHoang

## 1. Thông tin thành viên

- Họ tên: Võ Huy Hoàng
- MSSV: 2A202603397
- Email: 26ai.hoangvh4@vinuni.edu.vn
- GitHub: https://github.com/ferr2764

## 2. Phần việc phụ trách

CP2: Kiểm thử các shape đã viết. CP3: Kiểm chứng idempotency và crash/resume.

CP4: Chạy crash suite, kiểm tra approval, giới hạn hoàn tiền theo đơn, handoff, trace và secret.

Vai trò D — Test/Host, phụ trách kiểm thử workflow, single và orchestrator; bổ sung test. Kiểm thử crash/resume bổ sung phục vụ CP3–CP4.

## 3. Đóng góp cụ thể

- Bổ sung `src/tests/test_durability_shapes.py`, test `test_resume_other_crash_windows_keeps_one_refund`.
- Tham số hóa ba shape và hai điểm crash `before_effect`, `after_checkpoint`, tạo thành 6 ca kiểm thử. Đây là hai cửa sổ crash bổ sung cho T12 có sẵn (`after_effect_before_checkpoint`).
- Kiểm tra `InjectedCrash` thực sự xảy ra, cùng trạng thái ledger, audit và checkpoint ngay sau crash.
- Resume rồi retry trên cùng database; kiểm tra kết quả qua `trial_pass`, đúng một refund, một audit `refund_committed` và có checkpoint sau phục hồi.
- Sử dụng fixture `public_db` và marker `student`; không sửa host, policy, metric hoặc dữ liệu chuẩn.
- CP3: trực tiếp chạy T11 và T12 trên workflow, single, orchestrator và swarm; cả hai nhóm kiểm thử đều đạt 4/4 ca.
- CP4: chạy crash suite đạt 20/20, tạo `src/reports/crash.json`; chạy các nhóm test approval, public matrix, bảo mật và durability bổ sung đều pass.
- Commit chứa file test bổ sung: `d70fc4a` — `Final CP2`.

## 4. Bằng chứng

File test: [test_durability_shapes.py](../../src/tests/test_durability_shapes.py).

Lệnh chạy từ thư mục `src/`:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_durability_shapes.py -p no:cacheprovider
```

Kết quả xác minh: **6 passed in 0.27s**. 
![Test Durability](test_durability.png)

Kết quả này chỉ xác nhận sáu ca test bổ sung, không thay thế toàn bộ bộ student, crash suite 20/20 hoặc benchmark.

### CP3 — T11: Retry không tạo refund trùng

Chạy trong `src/`, bằng môi trường `.venv` với Python 3.12.10 và pytest 8.4.2:

```powershell
.\.venv\Scripts\python.exe -m pytest -vv -m student -o addopts= -k t11 -p no:cacheprovider
```

Kết quả terminal: **4 passed, 323 deselected in 0.25s**.

### CP3 — T12: Crash trước checkpoint rồi resume

```powershell
.\.venv\Scripts\python.exe -m pytest -vv -m student -o addopts= -k t12 -p no:cacheprovider
```

Kết quả terminal: **4 passed, 323 deselected in 0.22s**.

| Shape | T11 — Retry cùng claim | T12 — Crash/resume |
| --- | --- | --- |
| workflow | PASSED | PASSED |
| single | PASSED | PASSED |
| orchestrator | PASSED | PASSED |
| swarm | PASSED | PASSED |

T11 xác nhận gọi lại cùng claim trên cùng database không tạo thêm refund. T12 xác nhận crash tại `after_effect_before_checkpoint` thực sự xảy ra và sau resume vẫn chỉ có một refund, với kết quả được đối chiếu bằng `trial_pass`. Không có ca fail hoặc error trong hai lần chạy này. Đây là bằng chứng cho T11/T12, chưa thay thế kết quả toàn bộ host, crash suite 20/20 hoặc benchmark.

### Kiểm tra tích hợp CP2–CP3

Lần kiểm tra toàn bộ host và student ghi nhận **327 passed in 8.93s**. Khi xác minh, dùng thư mục tạm riêng cho `--basetemp` để tránh lỗi quyền truy cập Temp mặc định; không thay đổi cấu hình pytest của repo.

```powershell
$testTemp = Join-Path $PWD ('.pytest-review-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q -o addopts= -p no:cacheprovider --basetemp="$testTemp"
```

Lệnh này bỏ bộ lọc mặc định để chạy cả host và student. Kết quả xác nhận bộ test hiện có đều xanh, chưa kết luận pass rate hidden hoặc số liệu benchmark.

### CP4 — Crash safety, approval và bảo mật

Các lệnh dưới đây chạy trong `src/`; kết quả ghi nhận từ terminal:

| Kiểm tra | Kết quả |
| --- | --- |
| Crash suite chính thức | crash_safety 20/20 |
| Approval và giới hạn hoàn tiền theo đơn | 11 passed in 0.30s |
| Public matrix bốn shape | 248 passed in 7.61s |
| Handoff, secret, trace contract và workflow safety | 18 passed in 0.46s |
| Durability bổ sung ba shape | 6 passed in 0.25s |

```powershell
.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
.\.venv\Scripts\python.exe -m pytest -q tests/test_authorization.py tests/test_order_cap_and_approval_binding.py -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_public_matrix.py -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q tests/test_handoff_secret.py tests/test_trace_contract.py tests/test_workflow_safety.py -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_durability_shapes.py -p no:cacheprovider
```

Bằng chứng crash: [crash.json](../../src/reports/crash.json), với `count = 20`, `passed = 20`, mọi scenario đều có `passed = true`.

Rà các điểm ghi log/trace bằng:

```powershell
Select-String -Path lab8/shapes/workflow.py,lab8/shapes/single.py,lab8/shapes/orchestrator.py -Pattern 'print\(|trace\.add|logging|parent_secret|raw_headers'
```

Các điểm trace ghi quyết định, mã claim/order, quote, điểm crash và handoff đã sanitize. Trace investigator dùng order view từ tool đọc có allowlist. Trong kết quả tìm kiếm, `parent_secret` chỉ xuất hiện ở lời nhắc trong docstring orchestrator; không thấy lệnh in trực tiếp claim/order row thô tại các điểm đã rà. Các test bảo mật nêu trên pass; kết luận giới hạn trong code và tình huống được kiểm tra, chưa thay thế đánh giá hidden.

## 6. Tự đánh giá

Đã có test bổ sung cho hai cửa sổ crash trên ba shape, kiểm tra dữ liệu cả trước và sau phục hồi. Cần nắm rõ vì sao checkpoint không thay thế ledger và retry không được tạo thêm refund hoặc audit hoàn tiền.

Đã có bằng chứng CP2–CP4: sáu test bổ sung, T11/T12, kiểm tra tích hợp, crash suite 20/20 và các nhóm test approval/bảo mật đều pass. Việc tiếp theo: cập nhật bảng đóng góp trong `TEAM.md`, commit bằng chứng CP4, benchmark bốn shape với năm seed và `lab8.check_submission`. Các bước tiếp theo chưa được ghi nhận là hoàn thành trong báo cáo hiện tại.
