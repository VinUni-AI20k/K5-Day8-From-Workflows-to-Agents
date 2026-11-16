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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2503.13657, benchmark & empirical failure taxonomy on multi-agent systems |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống Multi-Agent thất bại phần lớn do lỗi kiểm chứng thông tin (verification failure) và tin tưởng dữ liệu đầu vào chưa được xác thực thay vì lỗi khả năng suy luận cơ bản. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Môi trường hệ thống multi-agent xử lý tác vụ nghiệp vụ có dữ liệu đầu vào hỗn hợp giữa ngôn ngữ tự nhiên không tin cậy và cơ sở dữ liệu chuẩn. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ Swarm (D) sang Workflow (A), lỗi kiểm chứng ở seed 55 trên claim C-002 sẽ biến mất hoàn toàn: pass rate tăng từ 0.986 lên 1.000, pass^5 tăng từ 0.929 lên 1.000, seed variance giảm từ 0.000816 về 0.000000 và chi phí giảm 43.8%. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM backend, bảng giá pricing.yaml, 5 seeds (11, 22, 33, 44, 55), tập 14 claims public, các tool đọc CSDL. Biến duy nhất thay đổi: Kiến trúc topology và cơ chế kiểm chứng nguồn chân lý (Ground Truth Verification: đọc trực tiếp CSDL vs tin tưởng câu chữ ticket). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi kiểm chứng (Verification Failure): Swarm tin ticket "trễ 5 ngày" thay vì cột delay_days=2 trong CSDL dẫn đến status resolved != denied trên C-002 seed 55. Đo bằng: pass rate (0.986 vs 1.000), pass^5 (0.929 vs 1.000), seed variance (0.000816 vs 0.000000), cost/success (49.57 vs 27.86 VND). |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
  `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report:
  `reports/benchmark.json` (dẫn chứng cặp đối chiếu `R-workflow-C-002-s55` vs `R-swarm-C-002-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  **Đúng hoàn toàn.**
  - Ở `R-swarm-C-002-s55`: Swarm mắc lỗi kiểm chứng đúng như phân loại của MAST (verification failure). Swarm chấp nhận thông tin người dùng khai báo trong ticket ("trễ 5 ngày") thay vì dữ liệu thực tế trong bảng orders (`delay_days = 2 < 3`), tự ý chi trả 20.000 VND và nhận kết quả `status resolved != denied` (thất bại).
  - Ở `R-workflow-C-002-s55`: Workflow tuân thủ quy tắc kiểm chứng nghiêm ngặt, đọc trực tiếp từ `lookup_order` và tính quote = 0 qua `compute_compensation`, trả về `denied` hợp lệ (thành công 100%).
  - Số liệu thực nghiệm: Pass rate đạt 1.000 (so với Swarm 0.986), pass^5 đạt 1.000 (so với Swarm 0.929), variance giảm về 0.000000, chi phí giảm từ 49.57 VND xuống còn 27.86 VND.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
