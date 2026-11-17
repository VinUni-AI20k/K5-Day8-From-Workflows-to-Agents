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
| CÂU | R1 / R2 / R3 / R4 | R2 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự, "Why Do Multi-Agent LLM Systems Fail?", NeurIPS 2025 (Datasets and Benchmarks), https://arxiv.org/abs/2503.13657. Loại bằng chứng: benchmark/dataset gồm hơn 1600 trace được gán nhãn (MAST-Data) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent LLM xếp được vào 14 kiểu lỗi thuộc 3 nhóm: specification issues, inter-agent misalignment và task verification |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Taxonomy xây từ trace của 7 framework multi-agent, các model GPT-4, Claude 3, Qwen2.5, CodeLlama, task coding, math và general agent. Không phải bài toán hoàn phí LogiX-VN và không phải MockLLM, nên chỉ dùng taxonomy làm khung phân loại, không dùng làm số liệu |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trial fail của swarm (C-002, seed 55: tin số ngày trễ trong ticket thay vì order row) được nhóm xếp gần nhất với nhóm task verification vì không đối chiếu khẳng định trong ticket với nguồn sự thật là order row (cách xếp của nhóm, không phải nhãn của paper). Nếu đổi D (swarm) sang B (single) thì pass rate không thấp hơn swarm, variance giữa các seed bằng 0 và C-002 là denied ở cả 5 seed, vì shape B không đọc ticket khi quyết định |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, tool đọc, 14 claim public, 5 seed (11, 22, 33, 44, 55), bảng giá, evaluator trial_pass, DB SQLite mới cho mỗi trial. Biến duy nhất được thay đổi: shape (swarm so với single) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: tin số ngày trễ trong ticket thay vì order row ở C-002 seed 55 (bypass bằng chữ trong ticket). Đo bằng pass rate, pass^5, variance giữa các seed và cost/success |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes swarm,single --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_r2.json`
- Run id / file report: `src/reports/ablation_r2.json`. Trial fail duy nhất: `R-swarm-C-002-s55` (swarm, status resolved thay vì denied). Cùng claim và seed với shape single: `R-single-C-002-s55` (denied, đúng)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **đúng**. Trên 14 claim × 5 seed (70 trial mỗi shape): swarm pass rate 0,986, pass^5 0,929, variance 0,000816; single pass rate 1,000, pass^5 1,000, variance 0. C-002 là denied ở cả 5 seed với single. Quan sát thêm, chưa phải điều dự đoán trước: cost/success của single là 29,74 VND so với 49,57 của swarm (trung bình 2,79 so với 4,66 tool call mỗi trial)
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Điểm yếu của swarm là cố ý đặt vào (REFERENCE_WEAKNESS), nên kết quả chỉ cho thấy một kiểu lỗi và cách shape B tránh nó, không chứng minh single tốt hơn multi-agent nói chung. Bộ public chỉ có 14 claim. Cột steps của single (4,64) cao hơn swarm (2,80) vì steps đếm số event trong trace và shape single ghi nhiều event hơn, không phải model suy luận nhiều hơn. Cost là chi phí mô phỏng, không phải hóa đơn API.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
