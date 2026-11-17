# Research card — Problem Solver

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 — Scaling; mở rộng kiểm chứng vào luồng tuần tự |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Google Research, 28/01/2026, [Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/); blog báo cáo nghiên cứu, 180 cấu hình |
| CLAIM | Một kết luận gốc của nguồn | Lợi ích phối hợp phụ thuộc task; nguồn cũng ghi nhận bộ điều phối tập trung tạo điểm kiểm chứng giúp hạn chế lỗi lan truyền. Bài lab kiểm riêng việc thêm verifier bằng code. |
| BOUNDARY | Model / dataset / setup | Nguồn dùng nhiều model và benchmark riêng; LogiX chỉ có MockLLM và luật có cấu trúc, không tái lập hệ số của paper. |
| HYPOTHESIS | Một biến và dự đoán | Thêm verifier code trước ghi tiền sẽ sửa lỗi tin ticket của swarm, tăng pass rate và cost/success; không làm swarm rẻ hơn workflow. |
| METHOD | Biến giữ cố định / thay đổi | Giữ MockLLM, seed 11/22/33/44/55, tools, corpus, giá và evaluator; bật/tắt verifier là biến ablation. Workflow là baseline tham chiếu. |
| FAILURE / METRIC | Lỗi và cách đo | Sai delay/status/damage; đo pass, pass⁵, seed variance, cost/success, interventions, secret/PII leak và approval bypass. |

## Kết quả ablation

Lệnh chạy trong `src/`:

```text
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_public.json
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_adversarial.json
python -m bonus.evidence
```

- Run id minh họa: R-swarm_verified-C-002-s55; file `src/reports/bonus_trace_example.json`.
- Public: 69/70 → 70/70; can thiệp 1 lần.
- Đối kháng: 74/80 → 80/80; can thiệp 15 lần.
- Kết quả ủng hộ hypothesis trong corpus này; chưa chứng minh lợi ích trên task mở hoặc model thật. MockLLM không phải model sản xuất; latency: unavailable.

## Đối chiếu hypothesis trên hidden

Hidden local: workflow 200/200 trial, pass rate 1.0000, pass⁵ 1.0000, variance 0.000000, 29.00 VND mô phỏng/success. Swarm đạt 194/200 (pass⁵ 0.85); swarm_verified 200/200 (pass⁵ 1.00), chi phí 60.46 VND/success. Verifier sửa 6 trial. Hypothesis được ủng hộ trên pack này: độ đúng tăng cùng chi phí, chưa tạo lợi thế so với workflow.

Biến ablation vẫn chỉ là bật/tắt verifier. Lệnh: `python -m bonus.hidden_evidence --pack D:/AIThucChien/DAY08/instructor/instructor` trong src/. Nguồn: hidden_summary.json; [phương pháp và giới hạn](hidden_validation.md).
