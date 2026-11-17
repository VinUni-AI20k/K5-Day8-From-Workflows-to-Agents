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
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), arXiv:2503.13657, bản v3 (10/2025), https://arxiv.org/abs/2503.13657. Loại bằng chứng: phân tích trace có chú thích của chuyên gia (grounded theory), kiểm lại trên benchmark |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent LLM phần lớn đến từ thiết kế hệ thống, lệch phối hợp giữa các agent và khâu kiểm chứng, không chỉ do giới hạn của model. MAST gom 14 failure mode vào 3 nhóm: FC1 System Design Issues, FC2 Inter-Agent Misalignment, FC3 Task Verification |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Taxonomy dựng từ 150 trace của 5 framework MAS (HyperAgent, AppWorld, AG2, ChatDev, MetaGPT) trên task lập trình và toán, model họ GPT-4 / Claude; kiểm lại trên OpenManus, Magentic-One, MMLU, GAIA. Không có task hoàn tiền có host gate. Lab dùng MockLLM tất định, nên chỉ mượn cách phân loại, không mượn tỉ lệ lỗi |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trial fail của swarm ở seed 55 thuộc FC3, cụ thể FM-3.2 *No or incomplete verification*: con số trong ticket không được đối chiếu với dòng order trước khi tính tiền (kèm FM-1.1 *Disobey task specification*, vì luật nói ticket là dữ liệu). Bật lỗi kiểm chứng (seed 55) thay vì tắt (seed 11) sẽ làm pass rate của swarm giảm đúng ở các claim có số ngày trong ticket khác DB; trên public chỉ có C-002, tức giảm 1/14 ≈ 0.071. Cost/success gần như không đổi |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool, corpus `data/public_claims.jsonl` (14 claim), giá `config/pricing.yaml`, evaluator `lab8.metrics.trial_pass`, shape `swarm`, SQLite mới mỗi trial. Biến duy nhất được thay đổi: seed 11 → 55. Trong `swarm_reference.py`, seed chỉ quyết định một việc là có tin số ngày trong ticket hay không (`seed % 5 == 0`), nên đổi seed ở đây tương đương tắt/bật bước kiểm chứng |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: C-002 (ticket ghi "trễ 5 ngày", order ghi 2 ngày) bị trả `resolved` 20.000 thay vì `denied` 0. Đo bằng pass rate theo seed (`seed_pass_rates`), lý do fail (`reasons`), event `model_override` trong trace, và tổng cost mô phỏng của mỗi seed |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes swarm --cases data/public_claims.jsonl --seeds 11,55 --out reports/ablation_r2_swarm_seed.json`
- Run id / file report: `src/reports/ablation_r2_swarm_seed.json`; trial fail duy nhất `R-swarm-C-002-s55` (trace có event `model_override` với `delay_days: 5`, rồi quote `SHIP-LATE-03` = 20.000). Đối chiếu thêm `src/reports/benchmark.json` (5 seed): swarm chỉ fail ở seed 55.
- Kết quả so với hypothesis: **đúng**. Seed 11: 14/14 pass (1.000). Seed 55: 13/14 pass (0.929), giảm đúng 0.071; fail duy nhất là C-002 với lý do `status resolved != denied`. Tổng cost mô phỏng 682.02 → 692.04 VND (+10 VND, đúng bằng một tool call tính lại quote). Lỗi xếp vào FC3 / FM-3.2 vì agent có sẵn dòng order đúng (2 ngày) nhưng không kiểm số ngày trong ticket với nó. Đối chứng: ba shape của nhóm (A/B/C) luôn lấy `delay_days` từ order, nên pass 1.000 ở cả 5 seed trong `benchmark.json`.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi ở đây được cài sẵn và tất định theo seed, nên chỉ cho thấy taxonomy phân loại được lỗi này, không ước lượng được tần suất FC3 với model thật. Bộ public chỉ có một claim kích hoạt lỗi (n = 1).

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
