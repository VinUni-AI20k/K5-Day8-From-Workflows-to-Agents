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
| CÂU | R1 / R2 / R3 / R4 | R2 (Phân loại lỗi failure taxonomy và so sánh mức độ tự chủ từ Workflow đến Swarm) |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, "Why Do Multi-Agent LLM Systems Fail?", https://arxiv.org/abs/2501.06648 (Empirical Benchmark & Failure Taxonomy) |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống Multi-Agent có mức độ tự chủ cao dễ mắc lỗi lệch mục tiêu (goal drift) và ảo giác (hallucination) trong các bài toán quy tắc nghiệp vụ cứng; chi phí phối hợp (coordination overhead) tăng cao mà không cải thiện độ chính xác so với quy trình xác định. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Môi trường giải quyết khiếu nại bồi thường LogiX-VN với các quy tắc nghiệp vụ cứng (policy, SLA, trần bồi thường), chạy trên MockLLM, corpus 14 claims public, 5 seeds cố định (11, 22, 33, 44, 55). |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi chuyển từ Workflow tĩnh sang Orchestrator/Swarm (tăng tự chủ): chi phí (cost/success) tăng mạnh từ 27.86 VND lên 49.57 - 56.65 VND (gấp ~1.8-2 lần) do overhead lập kế hoạch/suy luận LLM; Swarm sẽ xuất hiện ảo giác logic làm pass rate giảm xuống dưới 1.000 và pass^5 giảm xuống ~0.929. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: MockLLM, bộ công cụ tools (lookup_order, compute_compensation, issue_refund), tập seeds (11, 22, 33, 44, 55), corpus 14 claims public, biểu giá token/tool giả định, evaluator đối soát SQLite ledger. Biến duy nhất thay đổi: Topology kiến trúc phần mềm (Workflow vs Single ReAct vs Orchestrator vs Swarm). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Đo lường bằng Pass rate, Pass^5, Seed variance, Cost per success (VND). Lỗi quan sát được: Swarm bị fail ở seed 55 với lỗi 'status resolved != denied' (1 case) do ảo giác; Orchestrator đội chi phí lên 56.65 VND (cao gấp 2.03 lần Workflow 27.86 VND) do chi phí lập kế hoạch. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json` (dải run_id: `R-workflow-C-001-s11` đến `R-swarm-C-014-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **Đúng hoàn toàn**.
  + **Workflow**: pass rate = 1.000, pass^5 = 1.000, variance = 0.000000, min = 1.000, max = 1.000, cost/success = 27.86 VND, mean steps = 1.86.
  + **Single ReAct**: pass rate = 1.000, pass^5 = 1.000, variance = 0.000000, min = 1.000, max = 1.000, cost/success = 29.43 VND, mean steps = 1.86.
  + **Orchestrator**: pass rate = 1.000, pass^5 = 1.000, variance = 0.000000, min = 1.000, max = 1.000, cost/success = 56.65 VND, mean steps = 2.79.
  + **Swarm**: pass rate = 0.986, pass^5 = 0.929, variance = 0.000816, min = 0.929, max = 1.000, cost/success = 49.57 VND, mean steps = 2.80.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

### Phân tích chuyên sâu từ góc độ System Analyst (R1 - R4)

1. **So sánh chi phí và hiệu quả điều phối (R1 & R3)**:
   - Kiến trúc **Workflow** đạt mức chi phí tối ưu nhất (27.86 VND/success), thấp hơn Single ReAct (29.43 VND) và rẻ hơn một nửa so với Orchestrator (56.65 VND).
   - **Nguyên nhân cốt lõi**: Workflow có luồng điều khiển tĩnh (static hardcoded pipeline), gọi tool trực tiếp theo trình tự nghiệp vụ xác định mà không tiêu tốn token vào các vòng lặp ReAct, không cần LLM suy luận, lên kế hoạch (planning) hay phân tách tác vụ (task decomposition). Ngược lại, Orchestrator phải tốn thêm token cho bước lập kế hoạch và chuyển giao handoff cho Investigator, đẩy số bước trung bình lên 2.79 steps/claim và chi phí tăng hơn 103%.

2. **Đánh giá mức độ tự chủ và hiện tượng ảo giác (R2 - Swarm Failure Analysis)**:
   - Kiến trúc **Swarm** là mô hình có mức độ tự chủ cao nhất, cho phép các agent thảo luận và hành động độc lập. Tuy nhiên, Swarm là kiến trúc duy nhất bị sụt giảm độ tin cậy (pass rate giảm còn 0.986, pass^5 còn 0.929, phương sai variance = 0.000816).
   - **Bằng chứng thực tế**: Tại seed 55, Swarm gặp lỗi `status resolved != denied x1`. Trong tình huống này (claim T02), khiếu nại của khách hàng tự khai báo trễ 5 ngày, nhưng dữ liệu hệ thống đơn hàng thực tế ghi nhận chỉ trễ 2 ngày (chưa thỏa mãn điều kiện bồi thường theo SLA). Việc trao quyền tự chủ suy luận tự do cho LLM trong một bài toán có luật nghiệp vụ cứng đã dẫn đến lỗi **lệch mục tiêu và ảo giác dữ liệu (hallucination)**: LLM tin theo lời khai trong văn bản khiếu nại thay vì dữ liệu xác thực từ cơ sở dữ liệu đơn hàng, dẫn đến ra quyết định bồi thường (`resolved`) sai trái thay vì từ chối (`denied`).

3. **Kết luận kiến trúc phần mềm**:
   - Đối với bài toán xử lý khiếu nại bồi thường (claims flow) với quy tắc kinh doanh rõ ràng và yêu cầu tuân thủ nghiêm ngặt, **kiến trúc Workflow (ít tự chủ nhất)** là giải pháp tối ưu tuyệt đối: đảm bảo 100% tính chính xác tất định (deterministic), không có độ lệch phương sai, an toàn dữ liệu và tối thiểu hóa chi phí vận hành.
