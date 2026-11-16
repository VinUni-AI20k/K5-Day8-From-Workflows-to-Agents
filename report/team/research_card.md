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
| CÂU | R1 / R2 / R3 / R4 | R3 · Architecture choices |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Bogavelli và cộng sự (2026), [AgentArch](https://aclanthology.org/2026.aacl-long.44.pdf), AACL–IJCNLP. Bằng chứng: benchmark thực nghiệm. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Không có kiến trúc tối ưu chung; hiệu quả single/multi-agent phụ thuộc model và tác vụ. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | 18 cấu hình, 6 LLM, 2 workflow × 60 mẫu, temperature = 0, 8 lần thử/cấu hình. Paper không đo cost hay latency. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Đổi B (`single`) → D (`swarm`): cost/success tăng, latency tăng, success rate giảm. Chưa dự đoán độ lớn. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ MockLLM, bộ tool, corpus/world public, giá, evaluator, `as_of=2026-11-15`; 14 claim × 5 seed `11,22,33,44,55`, SQLite mới/trial. Đổi shape `single` → `swarm`. Hai implementation còn khác prompt/luồng tool và lỗi có chủ đích nên chưa cô lập riêng topology. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Swarm có thể tin số ngày trễ trong ticket thay vì order. Đo pass rate, pass^5, seed variance và cost/success (tổng cost, kể cả fail, chia số trial pass). Latency: `unavailable`. |

## Kết quả ablation

Dùng [benchmark có sẵn](../../src/reports/benchmark.json);

```powershell
python -m lab8.benchmark --shapes single,swarm --cases data/public_claims.jsonl --world data/public_world_state.json --seeds 11,22,33,44,55 --out reports/research_r3_single_swarm.json
```

| Metric | Single | Swarm |
| --- | ---: | ---: |
| Trial pass | 70/70 | 69/70 |
| Pass rate | 100% | 98,57% |
| Pass^5 | 100% | 92,86% |
| Seed variance | 0 | 0,00081633 |
| Cost/success mô phỏng (VND) | 35,42 | 49,57 |
| Latency | unavailable | unavailable |

**Kết luận:** cost/success tăng **39,93%**, success giảm **1,43 điểm phần trăm**, phù hợp hai vế giả thuyết; latency chưa kiểm định được.

**Failure:** `R-swarm-C-002-s55` fail (`resolved != denied`), còn `R-single-C-002-s55` pass. Swarm có lỗi cố ý tin ticket ở seed 55 nên chưa thể quy chênh lệch cho riêng topology.

**Giới hạn:** chỉ 14 claim public; MockLLM và chi phí mô phỏng. Không suy latency từ steps, không suy rộng sang model thật hoặc mọi hệ swarm.
