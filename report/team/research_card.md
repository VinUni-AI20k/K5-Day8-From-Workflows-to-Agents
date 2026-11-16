# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối mini research ở buổi lý thuyết. Ablation dưới đây so shape A và C trên cùng claims, seed, tool, giá và evaluator; chỉ đổi shape.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 — Architecture choices |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Bogavelli, Subramani & Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), AACL-IJCNLP 2026 long paper, benchmark thực nghiệm |
| CLAIM | Một kết luận gốc của nguồn | Kết quả của 18 cấu hình trên nhiều LLM và hai bài toán enterprise cho thấy kiến trúc tốt nhất phụ thuộc model/task; không có một cấu hình tối ưu cho mọi trường hợp. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn đo 18 cấu hình trên LLM hiện đại và hai use case enterprise. Lab này chỉ có 14 claim synthetic, MockLLM xác định theo seed và một flow hoàn phí; kết quả lab không tái lập quy mô hay model của paper. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Workflow → orchestrator trên cùng bộ public sẽ giữ pass rate gần 1.0, nhưng tăng cost/success ít nhất 50% do thêm planning/handoff/investigator; seed variance vẫn gần 0 vì MockLLM xác định. |
| METHOD | Biến giữ cố định và biến duy nhất được thay đổi | Giữ nguyên 14 claim, seed 11/22/33/44/55, MockLLM, tool, policy, giá, SQLite isolation và evaluator. Chỉ thay shape workflow ↔ orchestrator. Lệnh benchmark công khai chạy đủ bốn shape trong cùng điều kiện. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó | Nguy cơ ticket đánh lừa quyết định hoặc kiến trúc làm tăng lỗi handoff. Đo pass rate, pass^5, seed min–max, variance, cost/success và số reason fail trong benchmark; trace/security được kiểm bởi contract và test riêng. |

## Kết quả ablation

- Lệnh đã chạy: `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11`; `reports/benchmark.json` (benchmark gồm 280 run)
- Kết quả so với hypothesis: được ủng hộ trên bộ public. Workflow và orchestrator đều đạt pass rate/pass^5 1.000; cost/success lần lượt 27.86 và 61.51 VND mô phỏng (+120.7% cho orchestrator); variance đều 0.000000. Kết quả cho thấy trong flow synthetic này, orchestrator không cải thiện pass rate đủ để bù cost.
- Giới hạn: đây là so sánh shape, không cô lập riêng tác động của investigator khỏi các bước khác của kiến trúc. MockLLM không phải model sản xuất, latency là `unavailable`, và 14 claim public không đại diện mọi claim.
