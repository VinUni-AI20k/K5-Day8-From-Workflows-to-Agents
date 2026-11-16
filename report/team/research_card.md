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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST, NeurIPS 2025, https://arxiv.org/abs/2503.13657, benchmark & empirical failure taxonomy on Multi-Agent Systems |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Hệ thống đa tác tử (MAS) thường gặp lỗi kiểm chứng (Verification Failure) khi các tác tử tin cậy thông tin chưa được xác thực từ ngữ cảnh hội thoại hoặc người dùng thay vì đối soát với nguồn dữ liệu sự thật (ground-truth). |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Giới hạn trong môi trường kiểm tra quy tắc nghiệp vụ hoàn tiền (claims handling), tập dữ liệu public claims và mô hình đối soát chính sách. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu chuyển từ Swarm (Shape D) sang Orchestrator với Read-only Investigators (Shape C), lỗi Verification Failure ở seed 55 sẽ bị triệt tiêu hoàn toàn: pass rate tăng từ 0.986 lên 1.000, seed variance giảm từ 0.000816 về 0.0, và cost/success giảm từ 49.57 VND xuống 46.43 VND (~6.3%). |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Biến giữ cố định: MockLLM, định nghĩa tools, 5 seed (11, 22, 33, 44, 55), 14 claims public, bảng giá và evaluator trial_pass. Biến duy nhất được thay đổi: Topology điều phối (Swarm tự do peer-to-peer vs Orchestrator phân quyền điều tra viên chỉ đọc). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: 'status resolved != denied' tại claim C-002 seed 55. Đo lường qua pass rate, pass^5, seed variance và cost/success (VND). |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  - **Đúng hoàn toàn.**
  - **Swarm (Shape D):** Pass rate đạt `0.986` (69/70), pass^5 đạt `0.929`, seed variance là `0.000816`, chi phí mô phỏng `49.57 VND/success`. Xuất hiện đúng 1 lỗi Verification Failure tại C-002 seed 55 (`status resolved != denied x1`) do Swarm tin vào chuỗi text khiếu nại thay vì dữ liệu hệ thống.
  - **Orchestrator (Shape C):** Pass rate đạt tuyệt đối `1.000` (70/70), pass^5 đạt `1.000`, seed variance triệt tiêu hoàn toàn về `0.000000`, chi phí mô phỏng giảm còn `46.43 VND/success`. Ranh giới phân quyền rõ ràng ngăn chặn hoàn toàn việc dữ liệu chưa kiểm chứng tác động lên quyết định hoàn tiền.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
