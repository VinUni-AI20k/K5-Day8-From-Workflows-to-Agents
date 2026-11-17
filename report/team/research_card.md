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
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy (MAST) |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., 2025, "Why Do Multi-Agent LLM Systems Fail?" (MAST - Multi-Agent System Failure Taxonomy), NeurIPS 2025, https://arxiv.org/abs/2503.13657, loại bằng chứng: empirical failure taxonomy và benchmark trên các hệ multi-agent LLM |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Thất bại của hệ thống multi-agent phân bố vào ba cụm chính trong taxonomy MAST gồm System Design Issues, Inter-Agent Misalignment và Task Verification, trong đó việc thiếu bước kiểm chứng độc lập dữ kiện đầu vào với nguồn dữ liệu chuẩn trước khi kết thúc tác vụ dẫn đến quyết định sai dù từng bước gọi agent không báo lỗi kỹ thuật |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận gốc dựa trên phân tích trace của các hệ multi-agent mở; trong khuôn khổ Lab 8 LogiX-VN, thực nghiệm giới hạn trên 14 claim public (T01–T14) nhân 5 seed (11, 22, 33, 44, 55) = 70 trial mỗi shape, sử dụng MockLLM tất định theo seed và SQLite cô lập từng trial |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi đổi topology từ D (swarm tham chiếu có thể lấy số ngày trễ từ chữ trong ticket ở seed chia hết cho 5 mà không đối chiếu bắt buộc với dòng order) sang A (workflow tuần tự ép buộc kiểm chứng qua lookup_order và compute_compensation trên dữ liệu DB), lỗi Task Verification ở C-002 seed 55 sẽ bị triệt tiêu hoàn toàn: pass rate tăng từ ~0.986 lên 1.000, pass^5 tăng từ ~0.929 lên 1.000, seed variance giảm từ ~0.000816 về 0.0 và cost/success giảm khoảng 42% (từ ~49.57 xuống ~28.80 VND) |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: model backend (MockLLM), bộ tool đọc/ghi (lookup_order, compute_compensation, durability.issue_refund), 5 seed (11, 22, 33, 44, 55), corpus (data/public_claims.jsonl gồm 14 claim), bảng giá mô phỏng (config/pricing.yaml), as_of (2026-11-15) và evaluator (lab8.metrics.trial_pass với fresh_sqlite_per_trial). Biến duy nhất được thay đổi: kiến trúc/topology xử lý claim (workflow, single, orchestrator so với swarm) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến là Task Verification failure ở trial R-swarm-C-002-s55: ticket khai "Đơn giao trễ 5 ngày" nhưng bảng orders ghi O-202 có delay_days = 2 (nhỏ hơn ngưỡng 3 ngày của SHIP-LATE-03); swarm tin dữ kiện trong ticket ở seed 55 nên trả status resolved với refund 20.000 VND thay vì denied 0 VND. Cách đo: pass_rate, pass_5, seed_variance, cost_per_success_vnd, secret_leak_count và approval_bypass_count trong src/reports/benchmark.json |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-swarm-C-002-s55` (trial fail duy nhất của `swarm`), đối chứng trực tiếp với `R-workflow-C-002-s55`, `R-single-C-002-s55`, `R-orchestrator-C-002-s55` (đều pass với `status = denied`, `proposal_amount = 0`) và `R-workflow-C-014-s11`; file bằng chứng: `src/reports/benchmark.json` và `src/reports/crash.json`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng với hypothesis.** Theo `src/reports/benchmark.json` (70 trial/shape), `swarm` đạt `pass_rate = 0.986` (`69/70`), `pass^5 = 0.929` (`13/14`), `seed_min = 0.929`, `seed_max = 1.000`, `seed_variance = 0.000816`, `cost_per_success_vnd = 49.57` VND, `mean_steps = 2.80` do thất bại ở đúng 1 trial `R-swarm-C-002-s55` (`status resolved != denied`, hoàn sai `20.000` VND vì lỗi Task Verification — không đối chiếu số ngày trễ trong ticket với `delay_days = 2` của đơn `O-202` trong DB). Khi đổi sang topology `workflow` (cũng như `single` và `orchestrator` có khóa nguồn sự thật vào `lookup_order`), cả 3 shape đạt `pass_rate = 1.000` (`70/70`), `pass^5 = 1.000` (`14/14`), `seed_variance = 0.0`, trong đó `workflow` có chi phí thấp nhất `cost_per_success_vnd = 28.80` VND (rẻ hơn `swarm` **41.9%**), `mean_steps = 4.36` và `crash_safety = 20/20`.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi ở seed 55 của `swarm` là `REFERENCE_WEAKNESS` được thiết kế có chủ đích để tái hiện nhóm lỗi Task Verification / Inter-Agent trust trong MAST; nếu chạy trên model sản xuất, cả `single` và `orchestrator` cũng có thể phát sinh variance ở bước chọn tool nếu không cưỡng chế kiểm chứng bằng code.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
