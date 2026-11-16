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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research, Google DeepMind, MIT, *Towards a Science of Scaling Agent Systems*, arXiv:2512.08296 (https://arxiv.org/abs/2512.08296), kèm blog Google Research 01/2026. Loại bằng chứng: benchmark có kiểm soát (single agent so với 4 kiến trúc multi-agent, nhiều họ LLM, 6 benchmark agentic) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lợi ích của multi-agent phụ thuộc vào việc task có chia song song được không: phối hợp nhiều agent giúp ở task song song hóa được, và làm giảm hiệu năng ở task tuần tự (slide 15, 33: giảm 39–70% ở các biến thể multi-agent trên task tuần tự). Thêm agent không tự động tốt hơn |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Đo trên các LLM thật (nhiều họ model) và 6 benchmark agentic của paper, không phải task hoàn tiền có host kiểm approval. Kết luận về tương quan giữa cấu trúc task và kiến trúc; không nói gì về hệ thống mà số tiền do code tính và cổng host chặn mọi ghi sai, như LogiX |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Claims flow là chuỗi tuần tự (claim → order → quote → host). Đổi single → orchestrator (thêm investigator + handoff) sẽ **không tăng** pass rate (giữ 1.000 trên public) và làm cost/success **tăng ≥ 50%** do thêm tool call của investigator |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, bộ tool manifest v1.1, seed 11/22/33/44/55, 14 claim public, `config/pricing.yaml`, evaluator `trial_pass`, SQLite mới cho mỗi trial, cùng host `durability.issue_refund`. Biến duy nhất thay đổi: topology, single (một vòng ReAct) → orchestrator (orchestrator + investigator chỉ đọc qua handoff allowlist) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: chi phí phối hợp (thêm tool call, thêm model call) mà không thêm trial đúng, đo bằng cost/success và mean tool calls. Kèm pass rate, pass^5, seed variance để chắc chất lượng không đổi, và safety (leak/bypass) qua trial_pass |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` (ablation đọc hai dòng `single` và `orchestrator` của cùng lần chạy, nên mọi biến khác đều chung)
- Run id / file report: `src/reports/benchmark.json`, trial `R-single-C-001-s11` … `R-single-C-014-s55` và `R-orchestrator-C-001-s11` … `R-orchestrator-C-014-s55` (70 trial mỗi shape)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** Pass rate 1.000 → 1.000, pass^5 1.000 → 1.000, variance 0 → 0 (không cải thiện chất lượng). Cost/success 28.47 → 47.44 VND (**+66.6%**), mean tool calls 2.79 → 4.64 (+66.7%), mean model calls 0.93 → 1.00, mean steps 3.79 → 3.71, p95 steps 4 → 4. Khác với paper, pass rate không *giảm* khi thêm agent: host chặn mọi ghi sai và MockLLM cố định theo seed, nên chi phí phối hợp chỉ hiện ra ở cost, không hiện ra ở độ chính xác.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Corpus chỉ 14 claim public; không đo được critical path nên không kiểm được phần "song song giúp nhanh hơn" của claim. Với model thật, investigator có thể chọn sai tool, nên pass rate có thể giảm như paper mô tả; điều đó cần đo lại.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
