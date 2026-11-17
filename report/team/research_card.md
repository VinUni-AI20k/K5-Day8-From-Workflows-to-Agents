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
| CÂU | R1 / R2 / R3 / R4 | R3 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | AgentArch, AACL 2026 (tài liệu tham khảo buổi lý thuyết AI20K slide 68–69; bằng chứng thực nghiệm so sánh kiến trúc agent trong điều kiện kiểm soát biến). |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Trong cùng điều kiện model, bộ công cụ và dữ liệu, thay đổi topology điều phối làm thay đổi rõ rệt chi phí, số bước thực thi và độ ổn định; kiến trúc phức tạp hơn không mặc nhiên thắng kiến trúc đơn giản ở bài toán tuần tự có quy tắc rõ. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Áp dụng trong môi trường mô phỏng MockLLM, bảng giá cố định `config/pricing.yaml`, tập claim có cấu trúc dữ liệu dạng bảng và cổng duyệt của host; chưa đại diện cho độ trễ hay hành vi LLM thực ngoài môi trường sản xuất. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi giữ cố định dữ liệu, seed, model giả lập và công cụ, đổi từ `workflow` sang `single`, `orchestrator` hoặc `swarm` sẽ làm `mean_steps` và `cost_per_success_vnd` tăng từ khoảng ~29 VND lên ~50–57 VND, trong khi `pass_rate` không tăng vượt quá `1.000` (thậm chí giảm nếu nhánh agent tin dữ liệu ticket chưa kiểm chứng). |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: MockLLM, read tools + cổng host, 5 seed `11,22,33,44,55`, corpus `data/public_claims.jsonl` (14 claim), bảng giá `config/pricing.yaml`, `lab8.metrics` và DB cô lập mỗi trial. Biến duy nhất thay đổi: `shape` (`workflow`, `single`, `orchestrator`, `swarm`). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: dao động giữa các seed hoặc tin nhầm thông tin ticket ở kiến trúc tự chủ cao; đo bằng `pass_rate`, `pass_5`, `seed_variance`, `cost_per_success_vnd`, `mean_steps` và đếm lỗi theo `reasons` trong `src/reports/benchmark.json`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json` (ví dụ đối chiếu `R-workflow-C-002-s55` đạt `ok` so với `R-swarm-C-002-s55` lỗi `status resolved != denied`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng với giả thuyết — `workflow` đạt `pass_rate = 1.000`, `pass_5 = 1.000`, `seed_variance = 0.000000`, `cost_per_success_vnd = 28.87`, `mean_steps = 2.79`; `single` đạt `1.000` / `29.13` VND / `6.21` steps; `orchestrator` đạt `1.000` / `57.04` VND / `3.71` steps; `swarm` giảm còn `pass_rate = 0.986` (`69/70`), `pass_5 = 0.929`, `seed_variance = 0.000816`, `cost_per_success_vnd = 49.57` VND vì fail 1 trial ở seed `55`.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
