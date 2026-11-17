# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn:
- Commit hash:
- Run id dẫn chứng:
- Pass rate / pass^5 / seed min-max / variance:
- Cost per success (mô phỏng, VND):
- Crash safety:
- Secret leak / approval bypass:

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Viết 1 đoạn. So cùng corpus và cùng seed, không so với một lần chạy lẻ.

## Có đáng đổi lấy multi-agent không

Nếu pass nhỉnh hơn mà cost và variance cao hơn, nhóm giữ hay đổi? Điều kiện nào làm quyết định đảo lại?

## Trace và bằng chứng

Trace của nhóm ghi những event nào? Field nào cố ý **không** ghi, và vì sao? Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.

## Phân tích tạm thời — sau khi tích hợp single

Checkpoint 2026-11-17 trên `thanh-ledger-evaluation`, sau merge `1f7d89d`. Các shape được benchmark là code tại mốc này; phần mở rộng test/tài liệu sau merge chưa commit. Chưa chốt shape hoặc điền bảy trường quyết định ở đầu file vì orchestrator vẫn là stub.

Nguồn số liệu: `src/reports/benchmark.json`, công cụ sinh 4 shape × 14 claim × seed 11/22/33/44/55 = 280 trial. SQLite mới mỗi trial; cùng MockLLM, pricing và evaluator. Bảng dưới chỉ so sánh ba shape đã triển khai; orchestrator 0/70 do stub, chưa đủ điều kiện đánh giá.

| Shape | Pass rate / pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean model/tool calls | Mean/p95 trace steps |
| --- | --- | --- | ---: | ---: | --- | --- |
| workflow | 1 / 1 | 1–1 | 0 | 28.862857 | 1 / 2.785714 | 4.428571 / 5 |
| single | 1 / 1 | 1–1 | 0 | 29.798571 | 3.785714 / 2.785714 | 4.428571 / 5 |
| swarm | 0.985714 / 0.928571 | 0.928571–1 | 0.000816327 | 49.566957 | 3 / 4.657143 | 2.8 / 3 |

Workflow và single cùng 70/70 trial pass; single dùng nhiều model calls hơn, cost/success cao hơn 0.935714 VND mô phỏng. Trên public hiện tại chưa thấy lợi ích về pass rate của vòng ReAct. Đây là nhận xét về hai triển khai cụ thể, không phải kết luận nhân quả chỉ do topology: prompt, cách gọi model và cách trace khác nhau.

Swarm đạt 69/70; fail ở `R-swarm-C-002-s55` do ưu tiên ngày trễ trong ticket. Cost/success tính cả chi phí trial fail. Trace steps là số event, không đại diện trực tiếp cho model calls, latency hoặc hiệu suất giữa các kiến trúc.

Run id minh họa để tái tạo: `R-workflow-C-001-s11`, `R-single-C-001-s11`, `R-swarm-C-002-s55`. Chúng là định danh xác định theo shape/claim/seed; trace local có thể được ghi lại bởi lần chạy sau, nên không phải ID duy nhất cho cả một batch benchmark. Lệnh tái tạo nằm trong `src/reports/README.md`.

Workflow trace ghi các bước đọc claim/order, quote, host outcome và quyết định; single trace ghi agent action/decision, host outcome và crash nếu có. Không ghi ticket, secret, headers hoặc order row thô. Các trial workflow/single đều qua evaluator kiểm trạng thái, ledger, audit và trace; điều này không chứng minh an toàn với mọi dữ liệu chưa thấy. Crash suite host/swarm đạt 20/20; 16 test recovery/approval bổ sung cho workflow/single đều pass. Chưa có bằng chứng tương ứng cho orchestrator.

Điều kiện chốt: nhận orchestrator, mở rộng test recovery sang shape đó, chạy đầy đủ student matrix và benchmark cùng corpus/seed; so lại chất lượng, cost và variance trước khi chọn mức tự chủ thấp nhất đáp ứng yêu cầu. Chỉ kết luận ngưỡng hidden khi có kết quả chấm có nhãn. Chưa có lý do quyết định cuối hoặc commit chốt bài tại checkpoint này.
