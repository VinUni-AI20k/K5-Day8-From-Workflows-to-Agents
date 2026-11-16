# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 · Scaling |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research 2026, *Towards a Science of Scaling Agent Systems* (thư viện tham khảo slide 68–69); loại bằng chứng: benchmark có kiểm soát trên nhiều task và topology |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lợi ích của việc thêm agent phụ thuộc cấu trúc task: task song song hóa được có thể hưởng lợi, còn task tuần tự chặt thì multi-agent thường tăng chi phí phối hợp và có thể kém single agent |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Gắn với các LLM thật, bộ task và topology mà paper đo; không áp trực tiếp cho MockLLM tất định, corpus 14 claim và bảng giá mô phỏng của lab |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Task claims tuần tự (claim → order → quote → host). Thêm tầng orchestrator + investigator (workflow → orchestrator) sẽ không tăng pass rate (giữ 1.000) nhưng tăng cost/success khoảng 1.5–2.5× do thêm lượt plan và tool call của investigator |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định MockLLM, tool manifest v1.1, seed 11,22,33,44,55, `data/public_claims.jsonl`, `config/pricing.yaml`, evaluator của `lab8.benchmark`, SQLite mới mỗi trial, host `issue_refund` và `compute_compensation`. Biến duy nhất thay đổi: có/không tầng investigator read-only (workflow vs orchestrator) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: chi phí phối hợp tăng mà chất lượng không tăng, thêm bề mặt rò secret qua handoff. Đo bằng cost/success và tool call/trial; pass rate, pass^5, variance để kiểm không có cải thiện; leak qua test canary |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,orchestrator --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r1_investigator.json`
- Run id / file report: `src/reports/ablation_r1_investigator.json`; ví dụ `R-workflow-C-001-s11` so với `R-orchestrator-C-001-s11`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Pass rate 1.000 = 1.000, pass^5 1.000 = 1.000, variance 0 = 0. Cost/success 28.80 → 57.12 VND (×1.98, trong khoảng dự đoán); tool call/trial 2.79 → 5.57; model call/trial 1.00 → 1.93
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Corpus public chỉ 14 claim và cả hai shape chạm trần 1.000, nên ablation không phân biệt được chất lượng, chỉ kết luận về chi phí. Không suy rộng ra model thật hay task song song.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
