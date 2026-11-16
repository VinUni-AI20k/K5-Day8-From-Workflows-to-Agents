# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: 4 Thằng Sinh Viên
- Thành viên: xem `TEAM.md`
- Repo: [K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents), nhánh `main`.
- Commit mã nguồn dùng cho lần đo CP5: `96ab7201c69c66c532e779e0ef05f9a7ecf2362a`.
- Commit chốt mã nguồn: `96ab720`, trùng `report/team/decision_adr.md` do B cập nhật trong `c21031b`. Tài liệu và bằng chứng CP5 được bổ sung bằng các commit tiếp theo.

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý claim hoàn phí vận chuyển LogiX-VN bằng ba shape tự triển khai: workflow, single agent và orchestrator; sử dụng swarm tham chiếu để đối chứng. Mục tiêu là chọn mức tự chủ phù hợp dựa trên độ đúng, độ ổn định và chi phí mô phỏng.

Phân công theo vai: A phụ trách workflow và tích hợp; B phụ trách single agent và ADR; C phụ trách orchestrator, handoff và nghiên cứu; D phụ trách test/host, durability và benchmark. Trong CP2, nhóm hoàn thiện luồng xử lý và contract kết quả; CP3 kiểm chứng retry, crash/resume và ranh giới handoff.

## 3. Giải pháp

| Shape | Luồng xử lý và ranh giới trách nhiệm |
| --- | --- |
| Workflow | Các bước Python cố định đọc claim/order, tính quote bằng `compute_compensation`, xử lý nhánh nghiệp vụ rồi gọi host. Bản hiện tại không gọi model. |
| Single agent | Vòng ReAct giới hạn 8 bước chọn tool đọc qua `decide`, ghi nhận các lần gọi MockLLM trong budget; sau vòng lặp, code chuyển quote cho host. |
| Orchestrator | Dựng handoff qua `make_handoff`, investigator chạy tool chỉ đọc, nhận quote rồi gọi host. Bản hiện tại không gọi MockLLM. |
| Swarm tham chiếu | Có thêm lời gọi MockLLM; cố ý tin số ngày trễ trong ticket ở seed chia hết cho 5 khi ticket khác order. |

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

### Benchmark public CP5

Số liệu dưới đây đọc từ [benchmark.json](../../src/reports/benchmark.json), được sinh bằng lệnh chuẩn, không sửa JSON bằng tay. A đã tổng hợp kết quả; D đã chạy benchmark tại máy cá nhân, xác nhận đủ 280 trial và phân tích lỗi swarm. File benchmark đã được stage để đưa vào Git trong lần tích hợp này.

Điều kiện cố định: 14 claim C-001…C-014, seed `11,22,33,44,55`, tổng 280 trial; mỗi trial có SQLite mới, cùng evaluator, backend MockLLM, `as_of=2026-11-15`. Giá mô phỏng: tool 10 VND/lần, input/output 20/80 VND mỗi 1000 token; latency là `unavailable`.

| Shape | Pass | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| Workflow | 70/70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0 | 27.86 | 1.64 / 2 |
| Single | 70/70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0 | 29.65 | 2.00 / 2 |
| Orchestrator | 70/70 | 1.000000 | 1.000000 | 1.000000–1.000000 | 0 | 46.43 | 2.79 / 3 |
| Swarm | 69/70 | 0.985714 | 0.928571 | 0.928571–1.000000 | 0.000816327 | 49.57 | 2.80 / 3 |

Run id dẫn chứng: `R-workflow-C-001-s11`, `R-single-C-001-s11`, `R-orchestrator-C-001-s11`, `R-swarm-C-001-s11` đều pass. Trial fail duy nhất là `R-swarm-C-002-s55`, lý do `status resolved != denied`: ticket ghi trễ 5 ngày nhưng order ghi 2 ngày. Đây là điểm yếu có chủ đích của swarm.

Nhóm chọn workflow theo [decision_adr.md](decision_adr.md), đã được B cập nhật trong `c21031b`: cùng độ đúng public với B/C, chi phí mô phỏng thấp nhất và không cần model. Điều kiện đổi kiến trúc ghi trong ADR; C phụ trách [research_card.md](research_card.md) và một ablation. Bảng này chưa cô lập tác động của topology vì số lời gọi model/tool và cách triển khai cũng khác nhau; kết luận về hiệu quả và an toàn vẫn giới hạn ở các ca đã kiểm tra.

Lệnh A đã thực chạy trong `src/`, bằng Python 3.13.14 trên Windows (dùng Python của môi trường `.venv` đã cài):

```powershell
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m pytest -q -o addopts= -p no:cacheprovider --basetemp=.pytest-tmp-cp5-report
python -m lab8.check_submission
```

| Kiểm tra tích hợp CP5 | Kết quả |
| --- | --- |
| Toàn bộ host, student và test bổ sung | 327 passed in 12.70s |
| Crash JSON đã được D commit trong `96ab720` | 20/20 |
| `lab8.check_submission` sau khi tích hợp ADR `c21031b` | 1 FAIL ở research card trống; 1 WARN vì còn file chưa commit |
| Hidden self-check | Chưa chạy: workspace chưa có `student_drop/` |

Tại máy D (Python 3.12.10), lần chạy toàn bộ test trước benchmark đạt **327 passed in 9.89s**. Checker trước khi tích hợp ADR ghi nhận **8 FAIL, 1 WARN** (bảy trường ADR và research card còn trống). Kết quả 1 FAIL tại máy A trong bảng trên được ghi nhận sau khi tích hợp ADR.

Checker tại máy A đọc được benchmark local, crash 20/20, ADR chọn workflow, bảng đóng góp và ba shape đạt 12/12 claim public ở seed 11. Đây chưa phải `0 FAIL`, chưa xác nhận bài nhóm sẵn sàng nộp. C cần hoàn thiện research card; D đã stage benchmark và cần chạy checker lại sau tích hợp. Kết quả public không chứng minh đạt ngưỡng hidden 0.75.

## 5. Khó khăn và cách xử lý

Khi chạy test có fixture `tmp_path`, môi trường Windows báo `PermissionError: [WinError 5] Access is denied` tại `C:\Users\Admin\AppData\Local\Temp\pytest-of-Admin`, khiến các ca lỗi ngay bước setup. Đây là lỗi quyền thư mục tạm, chưa phải lỗi nghiệp vụ của shape.

Một cách xác minh là chỉ định thư mục tạm mới trong workspace bằng `--basetemp` như lệnh ở mục 4, đồng thời tắt cache bằng `-p no:cacheprovider`. Sau đó bộ test tích hợp chạy được và ghi nhận 327 ca pass. Không thay đổi logic test hoặc host để bỏ qua lỗi.

## 6. Tổng hợp đóng góp

| Thành viên | Đóng góp đã có bằng chứng và phân công CP5 |
| --- | --- |
| Nguyễn Tuấn Hiếu — A | Workflow (`28717d8`), test checkpoint/crash (`33d04f3`); tổng hợp báo cáo nhóm và TEAM. |
| Nguyễn Hoàng Anh — B | Single (`c47102a`), test safety/budget (`4b462c5`); ADR chọn workflow (`c21031b`). |
| Phạm Hữu Đức — C | Orchestrator và test (`8966ddd`); phụ trách research card và ablation. |
| Võ Huy Hoàng — D | Durability bổ sung (`d70fc4a`), bằng chứng CP4 và crash 20/20 (`96ab720`); phụ trách benchmark/checker. |

Chi tiết commit, test và báo cáo cá nhân nằm trong [TEAM.md](../../TEAM.md). Phân công CP5 không đồng nghĩa mọi phần việc đã hoàn thành; mỗi thành viên cần tự bổ sung báo cáo cá nhân và nộp link repo trên LMS.

## 7. Hạn chế và hướng cải thiện

MockLLM cố định theo seed không đại diện model sản xuất; cost là mô phỏng, latency `unavailable`. `Steps` là số event trace, không phải số tool call; khác cách ghi trace có thể ảnh hưởng mean/p95. Corpus public nhỏ và swarm có lỗi được cài sẵn, nên chưa chứng minh mọi hệ multi-agent kém hơn workflow. Chưa có điểm hidden: không khẳng định đạt ngưỡng 0.75 hoặc đủ điều kiện bonus. Cần xem xét lại kiến trúc khi tác vụ cần đọc hiểu phi cấu trúc, điều tra độc lập, hoặc khi model/corpus thực cho thấy lợi ích bù chi phí.

## 8. Tài liệu tham khảo

- [Checkpoints](../../CHECKPOINTS.md)
- [Business rules](../../docs/business_rules.md)
- [Contracts](../../docs/contracts.md)
- [Architecture](../../docs/architecture.md)
- [Metrics](../../docs/metrics.md)
