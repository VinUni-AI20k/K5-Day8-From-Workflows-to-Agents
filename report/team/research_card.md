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
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy: trial fail của swarm ở seed 55 thuộc nhóm MAST nào, và sửa đúng nhóm đó thì metric đổi ra sao? |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657 (slide 35, 45). Loại bằng chứng: nghiên cứu thực nghiệm, gán nhãn tay trace của các hệ multi-agent mã nguồn mở |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent LLM chia được thành 14 failure mode trong 3 nhóm: system design (specification), inter-agent misalignment, task verification; taxonomy xây bằng human annotation với độ đồng thuận κ = 0,88 |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Trace của các framework MAS mã nguồn mở với LLM thật, chủ yếu task lập trình và giải toán/hỏi đáp; nhãn do người gán. Không phải task ghi tiền có host chặn, không phải MockLLM có lỗi cài sẵn theo seed như LogiX |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Lỗi `R-swarm-C-002-s55` là inter-agent misalignment (peer bỏ qua dữ kiện `delay_days = 2` của investigator, tin số 5 trong ticket, FM "ignored other agent's input") rồi lọt qua vì thiếu task verification (FM "no or incomplete verification"). Bật một verifier bằng code trước khi ghi: pass rate swarm 0.986 → 1.000, seed 55 từ 0.929 → 1.000, variance về 0, cost/success đổi dưới 2% |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool chỉ đọc, handoff, peer/parse/draft call, seed 11,22,33,44,55, 14 claim public, bảng giá mô phỏng, evaluator `lab8.benchmark` + `trial_pass`. Biến duy nhất được thay đổi: bật bước verifier bằng code (`src/bonus/swarm_verified.py`) đối chiếu `delay_days`, `status`, `damage_verified` với order row trước `issue_refund`, lệch thì quote lại 1 lần và ghi `verifier_override` |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: refund cho claim không đủ điều kiện vì tin chữ trong ticket (host không chặn được vì approval hợp lệ). Đo bằng pass rate, pass^5, seed variance, cost/success, số event `verifier_override`, và leak (quét `CANARY_` trong trace) |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes swarm,swarm_verified,workflow --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r2.json`
- Run id / file report: `src/reports/ablation_r2.json`; `R-swarm-C-002-s55` (swarm, `resolved`, refund 20000, sai) so với `R-swarm_verified-C-002-s55` (`denied`, event `model_override` rồi `verifier_override` với `delay_days` 2, quote lại 0)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng.** swarm → swarm_verified: pass rate 0.986 → 1.000 (69/70 → 70/70), pass^5 0.929 → 1.000, seed min 0.929 → 1.000, variance 0.000816 → 0. Verifier can thiệp đúng 1/70 trial. Tổng cost mô phỏng 3420.12 → 3430.10 VND (+0.29%); cost/success 49.57 → 49.00 (giảm vì thêm 1 trial thành công). 0 trace chứa `CANARY_`. Workflow trên cùng điều kiện: 1.000 / 1.000 / 0 với cost/success 27.86, nghĩa là verifier đưa swarm về bằng workflow về chất lượng nhưng vẫn đắt hơn khoảng 76%. Test: `src/tests/test_ablation_swarm_verified.py` (8 passed)
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm là điểm yếu cài sẵn (`seed % 5 == 0`), nên chỉ có 1 trial fail để phân loại; nhóm gán nhãn MAST bằng tay cho trial này, không chạy tagger và không tính κ. 14 claim public là cỡ mẫu nhỏ; kết quả không chứng minh verifier đủ cho các loại lỗi khác (ví dụ ticket nói dối hỏng hàng nhưng DB cũng sai).

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
