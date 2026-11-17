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
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems, EMNLP 2026. Bài nghiên cứu/benchmark có kiểm soát: https://aclanthology.org/2026.emnlp-main.798/ |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | So sánh hiệu quả MAS có thể bị nhiễu bởi prompt/topology khởi đầu khác nhau; paper dùng backbone/runtime dùng chung và biến thiên có kiểm soát để tăng khả năng quy kết kết quả. Không suy rộng kết luận paper thành mọi MAS. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Paper đánh giá các phương pháp tái cấu trúc MAS trong benchmark của tác giả. Lab này dùng MockLLM và 14 claim public tổng hợp, nên chỉ cung cấp bằng chứng cho bộ claim/seed/config của lab. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Giả thuyết cho phép so sánh này: khi giữ corpus, seed, giá và evaluator cố định, workflow sẽ giữ pass rate tương đương các shape sinh viên nhưng có cost/success thấp hơn. Giả thuyết được ghi sau khi benchmark đã chạy, không phải đăng ký trước. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Lệnh benchmark bên dưới giữ MockLLM, tool registry, 14 public claim, seeds 11/22/33/44/55, giá mô phỏng, SQLite mới mỗi trial và evaluator; yếu tố so sánh là shape workflow/single/orchestrator/swarm. Shape chứa nhiều khác biệt triển khai, nên đây không phải ablation chỉ tách riêng một topology nội bộ. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Failure dự kiến: swarm tin delay trong ticket ở seed 55; đo bằng pass rate/pass^5, variance, cost/success và lý do fail. Kết quả public có 1/70 lỗi swarm, còn mỗi shape sinh viên 0/70. Hidden leak/bypass chưa có số liệu. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` (người dùng xác nhận chạy trong `.venv` từ `src/`; chưa lưu output `python --version`/console)
- Run id / file report: `R-workflow-C-001-s11` (trial đại diện; ID riêng của trial), `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Trên public set, hypothesis được ủng hộ về cost: workflow 28.87 VND/success so với orchestrator 46.43 và single 54.65; ba shape đều 70/70 pass, swarm 69/70. Chưa kết luận được về hidden/generalization. Người dùng xác nhận đã chạy lại trong `.venv`; JSON hiện có cùng các controlled variables và số liệu.
- Giới hạn: MockLLM không phải model sản xuất; latency là `unavailable`; 14 claim public; giả thuyết ghi sau lần chạy, so sánh shape không cô lập topology nội bộ; phiên bản Python và output console của lần chạy lại chưa được lưu trong phiên này.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
