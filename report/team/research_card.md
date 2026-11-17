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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | https://arxiv.org/pdf/2503.13657 |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Các lỗi của hệ thống Multi-Agent LLM không chỉ xuất phát từ model nền mà còn liên quan đến thiết kế hệ thống, sự phối hợp giữa các agent và quá trình kiểm chứng kết quả |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nghiên cứu phân tích 1.642 execution traces từ 7 framework MAS, sử dụng các task và setup được mô tả trong paper. Kết quả không mặc nhiên đại diện cho mọi hệ thống Multi-Agent |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Khi đổi thiết kế hệ thống từ Swarm (Shape D) sang Workflow (Shape A), hệ thống sẽ loại bỏ lỗi kiểm chứng ở Swarm: pass rate tăng từ ~0.986 lên 1.000, seed variance giảm từ ~0.000816 về 0.000000 và tiết kiệm chi phí hơn|
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định: MockLLM, bộ 14 public claims, 5 seeds (11, 22, 33, 44, 55), pricing.yaml, SQLite isolation, evaluator. Biến duy nhất thay đổi: Kiến trúc topology (Swarm multi-agent chuyển sang Workflow deterministic kiểm chứng bằng code) |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi cần khắc phục: Lỗi kiểm chứng (Verification Failure) tại C-002 seed 55 (Swarm ra resolved thay vì denied do tin ticket khách). Cách đo hiệu quả khắc phục: Nâng pass rate lên 1.000, Pass^5 lên 1.000 và giảm cost/success xuống < 49.57|

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
- Run id / file report: reports/benchmark.json (Run ID trial fail của Swarm: R-swarm-C-002-s55, đối chiếu Workflow: R-workflow-C-002-s55)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng. Kết quả thực nghiệm xác nhận: Khi chuyển từ Swarm sang Workflow, toàn bộ lỗi kiểm chứng (Verification Failure) được loại bỏ hoàn toàn: pass rate tăng từ 0.986 lên 1.000 (100%), pass^5 tăng từ 0.929 lên 1.000, triệt tiêu hoàn toàn phương sai giữa các seed (seed variance giảm từ 0.000816 về 0.000000), đồng thời tối ưu chi phí cost/success từ 49.57 VND xuống còn 27.86 VND. Claim C-002 tại seed 55 ở Workflow đã trả về đúng trạng thái denied nhờ code kiểm tra trực tiếp DB thay vì nghe theo ticket khách hàng khai khống.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
