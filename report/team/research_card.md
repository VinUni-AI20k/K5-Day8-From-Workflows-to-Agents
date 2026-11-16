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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Google Research, 2026, [Towards a science of scaling agent systems: When and why agent systems work](https://www.research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/), controlled benchmark trên 180 cấu hình agent. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hiệu quả của multi-agent phụ thuộc cấu trúc tác vụ: phối hợp giúp tác vụ song song hóa được, nhưng trong các tác vụ suy luận tuần tự được nghiên cứu, các biến thể multi-agent làm giảm hiệu năng 39–70% do chi phí phối hợp và phân mảnh quá trình xử lý. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn đánh giá năm kiến trúc trên bốn benchmark và ba họ model với tool/token budget được chuẩn hóa. Kết luận không trực tiếp bao phủ LogiX-VN synthetic, MockLLM hoặc mọi hệ thống production. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Đổi từ workflow tuần tự sang orchestrator có investigator sẽ không tăng pass rate trên claim LogiX-VN, nhưng làm cost/success tăng ít nhất 50% do thêm bước điều phối và tool call. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định MockLLM, tool manifest, 14 claim, world state, seed `11,22,33,44,55`, pricing và evaluator. Biến thay đổi là topology: workflow cố định → orchestrator trung tâm với investigator read-only. Mỗi trial dùng SQLite mới. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Rủi ro dự kiến là investigator không tăng độ đúng nhưng tạo coordination overhead. Đo pass rate, pass^5, seed variance/min–max, cost/success, mean/p95 steps; đồng thời yêu cầu leak và approval bypass đều bằng 0. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `.venv/bin/python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11`, `R-orchestrator-C-001-s11`; `src/reports/benchmark.json`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng trên bộ public. Hai shape cùng đạt pass rate/pass^5 `1.000/1.000` và variance `0`, nhưng cost/success tăng từ `27.86` lên `46.43 VND`, tương đương khoảng `66.7%`; mean steps tăng từ `3.79` lên `4.36`. Leak và approval bypass đều bằng 0.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Đây là ablation trong lab synthetic; khác biệt giữa hai implementation được xem như một thay đổi topology và chưa chứng minh quan hệ nhân quả ngoài thiết lập này.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
