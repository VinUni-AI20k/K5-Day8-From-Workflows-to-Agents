# Báo cáo cá nhân — 2A202604075_PhamDuyThanh

## 1. Thông tin thành viên

- Họ tên: Phạm Duy Thành
- MSSV: 2A202604075
- Email: thanhteyv2@gmail.com
- GitHub: thanhtey1234
- Nhánh: `thanh-ledger-evaluation`.
- Mốc nguồn đánh giá đủ bốn shape: `4f2060dc4729fa13d235ef41d4ed88480331b4f8`. Phần test/tài liệu hoàn thiện mới chưa commit.

## 2. Phần việc phụ trách

Ledger/crash và evaluation: bổ sung test phục hồi và approval, chạy benchmark/crash suite, thực hiện ablation, hoàn thiện ADR/research card và phần đánh giá trong báo cáo nhóm sau khi các thành viên merge code. Không sửa host, policy, metrics, config/data hoặc triển khai thay shape của người khác.

## 3. Đóng góp cụ thể

- `175d770`: giai đoạn 1–2, tám test recovery workflow, helper workflow_no_draft, 72 test ablation, baseline/crash/ablation và tài liệu.
- `db22c3b`: mở rộng recovery sang single thành 16 test; cập nhật baseline và phân tích tạm thời.
- `4f2060d`: commit merge main, giải quyết TEAM/benchmark sau khi orchestrator được tích hợp; không khai code orchestrator là đóng góp cá nhân.
- Phiên hoàn thiện hiện tại: mở rộng recovery thành **24 test** cho workflow/single/orchestrator, tạo lại benchmark/crash, chốt ADR chọn workflow và cập nhật báo cáo theo đủ bốn shape. Phần này chưa có hash commit mới.

Recovery test kiểm hai claim × ba crash point cho mỗi shape, trạng thái ledger/audit/checkpoint ngay sau crash, rồi mở lại kết nối, resume và retry ba lần. C-014 chỉ ghi thêm 120000 từ full quote 150000, tổng theo order 150000. Hai scenario approval/shape từ chối khi thiếu approval hoặc approval sai claim, dù retry nhiều lần.

Helper ablation dùng lại nguyên workflow, chỉ bỏ draft và đổi tên variant để tách trace. Scoped patch khôi phục kể cả khi crash; chỉ hỗ trợ chạy tuần tự cùng process. Đây là nghiên cứu bắt buộc, không đăng ký bonus.

## 4. Bằng chứng và khả năng tái tạo

Kết quả hiện tại, ngày 2026-11-17, Python 3.11.9:

- Bộ mặc định **195 passed**, student **248 passed**; không skip shape chưa triển khai.
- Crash suite **20/20**, cộng 24 test recovery/approval riêng cho ba shape. Không nhầm suite host/swarm với bằng chứng recovery riêng từng shape.
- Benchmark 280 trial: workflow/single/orchestrator đều **70/70**, swarm **69/70**. Pass^5 của ba shape nhóm viết = 1; swarm = 0.928571. Lỗi tham chiếu swarm ở C-002 seed 55 vẫn được benchmark tính fail.
- Workflow cost/success **28.862857**, single **29.798571**, orchestrator **57.258571**, swarm **49.566957** VND mô phỏng. ADR chọn workflow với mức tự chủ thấp nhất đáp ứng public; không khai đạt hidden.
- Ablation đã hoàn thành tại `175d770`: 70/70 mỗi variant, cost/success 28.862857 → 27.857143; tổng giảm 70.40 VND (3.48%). Workflow/helper không đổi sau merge nên không chạy lại report ablation trong phiên cuối.
- Run id ví dụ: `R-workflow-C-001-s11`, `R-orchestrator-C-014-s55`, `R-workflow_no_draft-C-001-s11`.
- Report JSON do công cụ sinh; trace/database local không commit.
- Kiểm tra cuối: `check_submission` đạt **0 FAIL, 1 WARN**, WARN do phần hoàn thiện chưa commit; `git diff --check` không có lỗi whitespace. ADR dùng hash nguồn có thật, chưa tạo hoặc khai hash mới.

Lệnh checkpoint cuối, chạy trong `src/`:

```powershell
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m pytest -q -m student -o addopts=
./.venv/Scripts/python.exe -m lab8.crash_test --count 20 --out reports/crash.json
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
./.venv/Scripts/python.exe -m lab8.check_submission
```

Lệnh ablation và các mốc trước nằm trong `src/reports/README.md`. Hash source trong ADR là `4f2060d`; thay đổi test mới chưa commit không thay code shape đã đánh giá. Chưa khai phần cuối đã được push/merge vào main.

| Checkpoint lịch sử | Commit | Test mặc định | Student đã kiểm |
| --- | --- | --- | --- |
| Workflow + nghiên cứu | 175d770 | 156 pass | workflow/swarm 124 pass |
| Mở rộng single | db22c3b | 164 pass | trừ orchestrator 186 pass |
| Merge orchestrator | 4f2060d | 187 pass | đủ bốn shape 248 pass |
| Hoàn thiện recovery đủ ba shape | Chưa commit | 195 pass | đủ bốn shape 248 pass |

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc repo, lập kế hoạch, viết test/helper, chạy lệnh, phân tích và soạn tài liệu. Firecrawl đã hỗ trợ xác minh nguồn research card. Bằng chứng kỹ thuật ở trên là kết quả thực thi bằng công cụ trong phiên Codex, không phải khẳng định thành viên đã tự chạy thủ công.

Thành viên cần tự đọc diff và chạy lại lệnh trước khi nộp; tự giải thích ledger khác checkpoint, full quote khác số tiền thực trả, ranh giới approval/handoff/trace và giới hạn của ablation. Không bịa commit, số liệu hoặc trải nghiệm tự kiểm tra cá nhân.

## 6. Tự đánh giá

Về sản phẩm, phần phụ trách đã có test tích hợp đủ ba shape, bằng chứng benchmark/crash tái tạo được, ADR và research card. Việc bổ sung từng shape sau merge giúp phát hiện khoảng trống giữa suite host và an toàn tại điểm tích hợp.

Về giới hạn, chưa có hidden có nhãn; chưa đánh giá chất lượng phản hồi khách hàng hoặc model sản xuất. Chi phí chỉ mô phỏng, latency `unavailable`; ablation chỉ tắt draft, không chứng minh lợi ích topology.

Nhận xét này đánh giá sản phẩm và giới hạn kỹ thuật. Mức độ hiểu bài và phần tự kiểm tra thủ công cần chính thành viên xác nhận trước khi nộp; không ghi thay trải nghiệm học tập cá nhân.
