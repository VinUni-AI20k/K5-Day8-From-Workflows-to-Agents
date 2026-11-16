# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: 4 Thằng Sinh Viên
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý claim hoàn phí vận chuyển LogiX-VN bằng ba shape tự triển khai: workflow, single agent và orchestrator; sử dụng swarm tham chiếu để đối chứng. Mục tiêu là chọn mức tự chủ phù hợp dựa trên độ đúng, độ ổn định và chi phí mô phỏng.

Phân công theo vai: A phụ trách workflow và tích hợp; B phụ trách single agent và ADR; C phụ trách orchestrator, handoff và nghiên cứu; D phụ trách test/host, durability và benchmark. Trong CP2, nhóm hoàn thiện luồng xử lý và contract kết quả; CP3 kiểm chứng retry, crash/resume và ranh giới handoff.

## 3. Giải pháp

| Shape | Luồng xử lý và ranh giới trách nhiệm |
| --- | --- |
| Workflow | Code đọc claim và order, tính quote bằng `compute_compensation`, xử lý các nhánh nghiệp vụ rồi gọi host. |
| Single agent | Vòng ReAct giới hạn 8 bước chọn tool đọc; sau vòng lặp, code chuyển quote cho host để ghi refund. |
| Orchestrator | Dựng handoff qua `make_handoff`, giao investigator chạy tool chỉ đọc, nhận kết quả tính quote rồi gọi host. |

Mọi shape giữ chữ ký `run_claim` và trả kết quả qua `finish()`. Số tiền do code tính, approval và giới hạn theo đơn do host kiểm tra. Shape truyền quote đầy đủ để host xử lý phần đã hoàn trước đó, tránh trừ hai lần.

Handoff dùng allowlist, không chuyển parent secret hoặc header thô. Trace ghi các sự kiện xử lý như quyết định, quote và handoff đã sanitize; có trace ở các nhánh trả sớm. Các test contract và bảo mật hiện có đều pass.

Refund dùng khóa idempotency `refund:{claim_id}`. Ledger và audit `refund_committed` được ghi cùng transaction; checkpoint ghi bước đã hoàn tất. Khi crash sau refund nhưng trước checkpoint, lần resume nhận ra hiệu ứng đã tồn tại và không ghi refund lần hai. Cả ba shape truyền `crash_at` vào host và để exception crash truyền ra ngoài.

## 4. Kết quả

### Kiểm chứng CP2–CP3

| Hạng mục | Kết quả |
| --- | --- |
| Toàn bộ host và student hiện có | 327 passed in 8.93s |
| T11 — retry cùng claim | 4 passed, 323 deselected in 0.25s |
| T12 — crash sau refund, trước checkpoint rồi resume | 4 passed, 323 deselected in 0.22s |
| Test bổ sung hai cửa sổ crash trên ba shape | 6 passed in 0.27s |

T11/T12 đều pass với workflow, single, orchestrator và swarm. Sáu test bổ sung kiểm tra `before_effect` và `after_checkpoint` trên ba shape nhóm viết, xác nhận trạng thái dữ liệu tại thời điểm crash và chỉ một refund, một audit sau resume/retry.

Lệnh kiểm tra tích hợp chạy trong `src/`:

```powershell
$testTemp = Join-Path $PWD ('.pytest-review-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -q -o addopts= -p no:cacheprovider --basetemp="$testTemp"
```

Chi tiết lệnh T11/T12 và ảnh test bổ sung nằm trong [báo cáo Võ Huy Hoàng](2A202603397_VoHuyHoang.md). Demo `python -m lab8.demo.buggy_workflow` cho `unsafe refund rows: 2`, minh họa checkpoint đơn lẻ không chống được ghi trùng.

### Kiểm chứng CP4

| Hạng mục | Kết quả |
| --- | --- |
| Crash suite chính thức | 20/20 |
| Approval và giới hạn theo đơn | 11 passed in 0.30s |
| Public matrix | 248 passed in 7.61s |
| Handoff, secret, trace contract và workflow safety | 18 passed in 0.46s |
| Chạy lại durability bổ sung | 6 passed in 0.25s |

Crash safety lấy từ [src/reports/crash.json](../../src/reports/crash.json): cả 20 scenario đều pass. File được tạo bằng `python -m lab8.crash_test --count 20 --out reports/crash.json`, không sửa tay. Các kết quả pytest được ghi nhận từ terminal; lệnh đầy đủ nằm trong [báo cáo Võ Huy Hoàng](2A202603397_VoHuyHoang.md).

Đã rà các điểm ghi trace/log trên ba shape: quyết định, mã claim/order, quote, điểm crash và handoff đã sanitize; investigator ghi order view từ tool đọc có allowlist. Không thấy ghi trực tiếp claim/order row thô tại các điểm đã rà. Các test approval và bảo mật đã chạy đều pass; kết quả này giới hạn trong các tình huống được kiểm tra.

### Kết quả cần bổ sung ở CP5

Chưa có bằng chứng benchmark trong báo cáo để kết luận pass rate, pass^5, seed min–max, variance, cost/success hoặc mean/p95 steps. Kết quả pytest không thay thế benchmark hoặc đánh giá hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Khi chạy test có fixture `tmp_path`, môi trường Windows báo `PermissionError: [WinError 5] Access is denied` tại `C:\Users\Admin\AppData\Local\Temp\pytest-of-Admin`, khiến các ca lỗi ngay bước setup. Đây là lỗi quyền thư mục tạm, chưa phải lỗi nghiệp vụ của shape.

Một cách xác minh là chỉ định thư mục tạm mới trong workspace bằng `--basetemp` như lệnh ở mục 4, đồng thời tắt cache bằng `-p no:cacheprovider`. Sau đó bộ test tích hợp chạy được và ghi nhận 327 ca pass. Không thay đổi logic test hoặc host để bỏ qua lỗi.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`, chi phí là mô phỏng. Bộ test hiện có xanh chỉ xác nhận các tình huống được kiểm tra, chưa chứng minh hiệu quả trên hidden hoặc môi trường thực tế. Nhóm sẽ bổ sung benchmark cùng claim, seed và bảng giá trước khi chốt kiến trúc; kết luận cần xem xét lại khi corpus, model hoặc yêu cầu nghiệp vụ thay đổi.

## 8. Tài liệu tham khảo

- [Checkpoints](../../CHECKPOINTS.md)
- [Business rules](../../docs/business_rules.md)
- [Contracts](../../docs/contracts.md)
- [Architecture](../../docs/architecture.md)
- [Metrics](../../docs/metrics.md)
