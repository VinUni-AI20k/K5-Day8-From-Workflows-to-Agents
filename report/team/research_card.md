# Research card

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 · Architecture choices |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Bogavelli, Subramani & Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), AACL-IJCNLP 2026 paper / benchmark. Paper evaluates 18 configurations across orchestration, agent style, memory and thinking tools. |
| CLAIM | Một kết luận gốc của nguồn | AgentArch treats architecture as multiple design dimensions and evaluates configurations systematically; its reported results are bounded to its benchmark and tested models. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận | The paper's enterprise workflow tasks, benchmark, tested models and 18 configurations; it does not establish that an orchestrator or multi-agent topology is universally better. |
| HYPOTHESIS | Shape A→B and predicted metric | Workflow→orchestrator, hold other lab settings fixed. Prediction: pass rate remains near 1.00 on this structured corpus while cost/success rises by 20–50% due to investigator tool calls. |
| METHOD | Controls and one changed variable | Same MockLLM, tool set, seeds 11/22/33/44/55, 14 public claims, prices, world and evaluator. Change only the shape implementation (workflow vs orchestrator); compare generated benchmark summaries. This is a bundled architecture comparison, not an isolated causal estimate of topology. |
| FAILURE / METRIC | Predicted error and measurement | Coordination/handoff overhead without accuracy gain. Measure pass rate, pass^5, seed variance, cost/success, mean and p95 steps. Observed: workflow 1.000/1.000, variance 0, 27.86 VND; orchestrator 1.000/1.000, variance 0, 46.43 VND, mean/p95 3.71/4 steps. Hypothesis supported for cost increase; both passed all public trials. |

## Kết quả ablation

- Lệnh đã chạy: `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: Per-trial IDs are recorded in `src/reports/benchmark.json`; example `R-workflow-C-001-s11`. Aggregate report: `src/reports/benchmark.json`.
- Kết quả so với hypothesis: Đúng hướng về cost, không có khác biệt pass rate trong hai shape. Orchestrator cost/success cao hơn workflow 18.57 VND (66.7%); cả hai pass rate 1.000, pass^5 1.000, variance 0.000000. Mức tăng cao hơn dự đoán 20–50%.
- Giới hạn: Đây là so sánh triển khai shape trong fixture nhỏ, các thay đổi trong shape đi cùng nhau; chưa cô lập topology và chưa chạy hidden set. MockLLM không phải model sản xuất, latency `unavailable`.
