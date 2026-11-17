# Decision record — Problem Solver

- Shape chọn: workflow
- Commit hash: bd5a602 (commit chứa code đã benchmark; snapshot SHA-256 khớp hidden_summary.json)
- Run id dẫn chứng: R-workflow-C-H03-s11; src/reports/hidden_summary.json; public R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.0000 / 1.0000 / 1.0000–1.0000 / 0.000000 (hidden local, 200 trial)
- Cost per success (mô phỏng, VND): 29.00 (hidden local); 27.86 (public)
- Crash safety: 20/20 host; 30/30 hidden; 12/12 public bổ sung
- Secret leak / approval bypass: 0 / 0; PII leak 0 trên 1000 trial hidden recount và 750 trial public/đối kháng

## Vì sao shape này

Workflow có mức tự chủ thấp nhất, đạt 70/70 trial public, không gọi model và có chi phí thấp nhất trong phép đo. Single và orchestrator cũng đúng trên corpus này nhưng tốn thêm chi phí. Dữ liệu đơn và luật hoàn tiền có cấu trúc; thêm model chưa tạo thêm độ đúng quan sát được.

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 27.86 | 4.43/5 |
| single | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.46 | 7.21/8 |
| orchestrator | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 47.29 | 6.29/7 |
| swarm | 69/70 | 0.9857 | 0.9286 | 0.9286–1.0000 | 0.000816 | 49.57 | 2.80/3 |

## Có đáng đổi lấy multi-agent không

Chưa có bằng chứng để đổi ở task hiện tại. B3 sửa lỗi swarm nhưng vẫn đắt hơn workflow. Đo lại nếu task có chứng từ mơ hồ, điều tra độc lập có thể chạy song song hoặc tool ngoài. Phải giữ cùng corpus, seed, evaluator và budget; gate local hidden ≥ 0.75 và ≥ 0.80 đã đạt; điểm chính thức chờ giảng viên.

## Trace và bằng chứng

Trace ghi get_claim_view đã lọc, lookup_order đã kiểm chủ sở hữu, quote, quyết định và host_outcome. Single thêm observation/react_think; orchestrator thêm plan/handoff/investigator/aggregate. Không ghi ticket thô, parent_secret, header, điện thoại, địa chỉ, internal_note hoặc item_name. finish đọc ledger thật và ghi trace mới ở mọi nhánh return. InjectedCrash được truyền ra harness; trace hoàn chỉnh được sinh ở lần resume.

## Giới hạn

MockLLM, dữ liệu giả và lỗi swarm có chủ đích. Latency: unavailable. Steps là số event, không phải wall-clock latency. A–D khác cả adapter/prompt nên không cô lập riêng topology; ablation B3 chỉ thêm verifier vào cùng swarm. Đã chấm local trên 40 claim × 5 seed bằng nhãn riêng của pack được cung cấp; không suy ra điểm hidden từ public. Kết quả chính thức chờ giảng viên xác nhận.

## Kiểm chứng hidden

Kết quả chấm local trên pack được cung cấp, dùng CLI benchmark và metric nguyên bản với `--labels hidden_labels.json`; bỏ qua `expected` mồi trong claim. Điểm chính thức do giảng viên xác nhận.

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.00 | 4.53/5 |
| single | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 30.68 | 7.42/8 |
| orchestrator | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 49.41 | 6.47/7 |
| swarm | 194/200 | 0.9700 | 0.8500 | 0.8500–1.0000 | 0.003600 | 52.49 | 2.93/3 |
| swarm_verified | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 60.46 | 3.88/4 |

Safety recount 1000 trial: secret/PII leak, approval bypass, execution error và lỗi trace đều 0. Crash hidden 30/30; host 20/20. Không cần sửa logic workflow, single, orchestrator hoặc verifier: cả bốn đạt 200/200 trên lần chạy đầu. Giữ nguyên swarm tham chiếu, gồm lỗi cố ý seed 55. Chỉ bổ sung công cụ đo và tài liệu; không đọc nhãn trong shape, không hardcode claim id và không sửa thước đo.

[Phương pháp, giới hạn và lệnh tái lập](hidden_validation.md). Bằng chứng: `src/reports/hidden_summary.json`; run ví dụ `R-workflow-C-H03-s11`.
