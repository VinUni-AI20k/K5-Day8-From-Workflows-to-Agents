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
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders; ablation một thành phần trong workflow |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang et al., 2026, [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/), EMNLP; nghiên cứu benchmark có kiểm soát |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lợi ích hiệu suất được báo cáo có thể phụ thuộc prompt và topology khởi đầu; cần kiểm soát setup để quy kết nguyên nhân. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn đánh giá các phương pháp efficiency trên diagnostic benchmark của tác giả với backbone, agent registry và runtime chung; không chứng minh kết quả cho LogiX-VN hoặc mọi MAS. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Bỏ riêng draft model call của workflow sẽ giữ pass rate và pass^5 = 1, variance = 0 trên 14 claim × 5 seed; model calls/trial giảm 1 → 0, cost/success giảm dương nhưng dưới 10%. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ nguyên backend MockLLM cho các call còn lại, world/corpus/nhãn public, seed 11/22/33/44/55, as_of 2026-11-15, tools, host, giá và evaluator. Chỉ thay bật/tắt draft call bằng context patch trong runner; không đổi source shape. Mỗi trial DB mới. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Dự kiến không đổi status/proposal/refund/audit theo trial_pass và các trial ghép cặp; đo pass rate, pass^5, variance, mean model/tool calls, cost/success. Không dùng số event trace làm proxy latency. |

## Kết quả ablation

- Lệnh đã chạy (trong `src/`): `.\.venv\Scripts\python.exe -m tests.evaluation_ablation --out reports/evaluation_ablation.json`.
- Run id / file report: `R-workflow-C-014-s11`; `src/reports/evaluation_ablation.json`, hai nhánh `baseline` và `without_draft` (run id giữ nguyên để ghép cặp, trace được ghi lại mỗi lần chạy).
- Kết quả: ủng hộ hypothesis trong setup này. Cả hai nhánh pass 70/70, pass rate = pass^5 = 1, seed variance = 0; model calls/trial 1 → 0; tool calls/trial đều 2.785714; cost/success 28.77 → 27.857143 VND mô phỏng (giảm ≈ 3.17295%); tổng cost 2013.90 → 1950.00, tiết kiệm 63.90. Mean/p95 trace events vẫn 4.428571/5.
- Diễn giải: draft chỉ soạn lời, nên bỏ call không đổi quyết định tiền. Đây là suy luận từ code và thí nghiệm của nhóm; không phải kết luận về topology của paper. So A/B/C/D chưa đủ cô lập topology vì prompt, số tool và số model call cũng khác.
- Giới hạn: MockLLM không phải model sản xuất, latency `unavailable`; evaluator không chấm lời phản hồi; không đo hidden; trace hai nhánh dùng cùng run id nên report JSON giữ bằng chứng từng trial, không coi trace cuối là hai file độc lập. Không đăng ký bonus.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
