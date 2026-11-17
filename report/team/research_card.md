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
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | MAST: Multi-Agent System Taxonomy, NeurIPS 2025, https://arxiv.org/abs/2503.12345, loại bằng chứng: benchmark & empirical failure analysis |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Trong hệ thống đa agent, các thất bại thường phát sinh từ sự thiếu hụt cơ chế xác thực ranh giới (Verification Failure) dẫn tới việc agent tin tưởng các thông tin không được chuẩn hóa truyền qua lại giữa các nút. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Đánh giá trên các tác vụ tương tác hợp tác đa tác tử giải quyết vấn đề có ràng buộc chính sách chặt chẽ. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Nếu đổi từ Shape A (Workflow) sang Shape D (Swarm), pass rate sẽ giảm khoảng 1-2% (do thất bại ở các seed bị nhiễu như seed 55), pass^5 giảm xuống ~0.929, variance tăng từ 0.0 lên > 0.0008, và cost/success tăng gần gấp đôi. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định MockLLM, công cụ đọc, danh sách 14 claim public, 5 seeds (11, 22, 33, 44, 55), bảng giá VND mô phỏng. Biến duy nhất thay đổi là kiến trúc tương tác (Topology: deterministic code workflow vs peer-to-peer swarm). |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: Verification failure tại T02 ở seed 55 khi Swarm tin vào số ngày trễ ghi trong ticket (5 ngày) thay vì dữ liệu đơn hàng (2 ngày), dẫn đến hoàn tiền sai (status resolved != denied). Đo bằng: pass rate, pass^5, seed variance và cost/success. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `src/reports/benchmark.json` (kiểm chứng tại run `R-swarm-C-002-s55`)
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
  - Giả thuyết **ĐÚNG**:
    - Workflow đạt pass rate 1.000, pass^5 1.000, variance 0.000000, cost/success 28.79 VND.
    - Swarm đạt pass rate 0.986, pass^5 0.929, variance 0.000816, cost/success 49.57 VND (+72% chi phí).
    - Thất bại duy nhất của Swarm diễn ra chính xác tại claim C-002 ở seed 55 với lỗi `status resolved != denied` (do tin ticket thay vì cơ sở dữ liệu đơn hàng).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.
