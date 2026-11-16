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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Kim et al., *Towards a Science of Scaling Agent Systems*, 2025/2026, [arXiv:2512.08296](https://arxiv.org/abs/2512.08296), bằng chứng benchmark có kiểm soát trên 180 cấu hình agent. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Trong setup của paper, kiến trúc nhiều agent giúp tác vụ song song nhưng làm hiệu năng tác vụ suy luận tuần tự giảm 39–70%; coordination overhead và mật độ tool là hai yếu tố quan trọng. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Paper dùng bốn benchmark Finance-Agent, BrowseComp-Plus, PlanCraft và Workbench; ba họ LLM GPT/Gemini/Claude; công cụ và token budget được chuẩn hóa. Kết luận không trực tiếp bao phủ MockLLM, dữ liệu claim LogiX-VN hoặc thao tác ghi tiền có host gate. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi đổi A `workflow` → B `single` trên flow claim chủ yếu tuần tự, pass rate và pass^5 giữ nguyên 1.0, còn cost/success tăng 5–15% và mean steps tăng ít nhất 50% do vòng ReAct/model decision. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Dùng benchmark chính của nhóm, giữ cố định MockLLM, tool/host, 14 claim public, seed `11,22,33,44,55`, `as_of=2026-11-15`, pricing, evaluator và fresh SQLite mỗi trial. Ablation lấy lát cắt A/B, biến duy nhất là shape `workflow` hay `single` (2 × 14 × 5 = 140 trial); chạy lại riêng để kiểm tra khả năng tái lập. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Failure dự kiến: thêm vòng agent không tăng số trial đúng nhưng tăng overhead. Đo pass rate, pass^5, seed variance/min-max, cost/success, mean/p95 steps và model calls; đồng thời yêu cầu leak/bypass bằng 0 qua host gate. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): benchmark chính `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`; tái lập lát cắt A/B `python -m lab8.benchmark --shapes workflow,single --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/ablation_workflow_single.json`.
- Run id / file report: bằng chứng chính `src/reports/benchmark.json`, tái lập `src/reports/ablation_workflow_single.json`; run dẫn chứng `R-workflow-C-001-s11` và `R-single-C-001-s11`.
- Kết quả so với hypothesis: **đúng trên bộ public và khớp ở cả hai report**. Workflow và Single đều có pass rate = pass^5 = `1.000`, variance `0`, min-max `1.000–1.000`. Single có cost/success `30.70` so với workflow `28.87` VND mô phỏng (**+6.34%**), mean steps `8.21` so với `4.43` (**+85.48%**), p95 steps `9` so với `5`. Kết quả này củng cố quyết định ADR chọn Workflow là shape ít tự chủ nhất vẫn đạt độ đúng tương đương.
- Giới hạn: chỉ 14 claim public và 5 seed; MockLLM xác định không phải model sản xuất, latency là `unavailable`; kết quả không chứng minh Single luôn kém hơn trên task phi tuần tự hoặc dữ liệu hidden.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
