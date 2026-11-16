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
| CÂU | R1 / R2 / R3 / R4 | R2 — Failure taxonomy |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri và cộng sự, Why Do Multi-Agent LLM Systems Fail?, NeurIPS 2025; nghiên cứu thực nghiệm/taxonomy MAST; [nguồn chính thức](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html). |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | MAST phân loại 14 failure mode thành ba nhóm: system design issues, inter-agent misalignment, task verification. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn nghiên cứu trace từ các framework MAS trên coding/math/general agent; không đo task refund của lab. Nhóm chỉ dùng taxonomy làm khung diễn giải, không chuyển tỷ lệ lỗi từ paper sang MockLLM. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Tắt peer acknowledgement (output không được dùng) sẽ giữ pass rate 69/70, pass^5 13/14 và lỗi C-002/seed 55; giảm một model call mỗi trial và cost/success khoảng 0,5–2 VND. Đây là kỳ vọng từ đọc code, không phải hypothesis preregistered. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | So swarm với swarm_no_peer bằng cùng runner, MockLLM, tool/host, prompt của các call còn lại, 14 public claim, seed 11/22/33/44/55, as_of 2026-11-15, giá và evaluator; SQLite mới mỗi trial. Chỉ bật/tắt call purpose=peer. Đổi shape/run id chỉ để tách trace, không đổi quyết định. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Đo pass rate, pass^5, variance, cost/success và mean model calls; đối chiếu C-002/seed 55. Nhóm suy luận lỗi tin ticket thay vì order là task verification; đây không phải nhãn do tác giả MAST gán. |

## Kết quả ablation

- Lệnh đã chạy trong `src/`:

```powershell
python -m lab8.benchmark --shapes swarm,swarm_no_peer --extra-shape swarm_no_peer=bonus.swarm_no_peer:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_peer_ablation.json
```

- Commit kỹ thuật: `b3f45ba`; code [swarm_no_peer.py](../../src/bonus/swarm_no_peer.py), 5 test tại [test_swarm_peer_ablation.py](../../src/tests/test_swarm_peer_ablation.py).
- Run id / file report: `R-swarm-C-002-s55`, `R-swarm_no_peer-C-002-s55`; [research_peer_ablation.json](../../src/reports/research_peer_ablation.json). File chứa 140 trial, 70 mỗi nhánh.

| Metric | Swarm có peer | Swarm tắt peer |
| --- | ---: | ---: |
| Trial pass | 69/70 | 69/70 |
| Pass rate | 0,985714 | 0,985714 |
| Pass^5 | 0,928571 | 0,928571 |
| Seed min–max | 0,928571–1,000000 | 0,928571–1,000000 |
| Variance | 0,000816327 | 0,000816327 |
| Cost/success (VND mô phỏng) | 49,566957 | 48,691594 |
| Mean model calls | 3 | 2 |
| Mean tool calls | 4,657143 | 4,657143 |

- Kết quả phù hợp kỳ vọng: cost/success giảm 0,875362 VND, tương đương 1,766020%; pass/status và tool calls khớp ở cả 70 cặp trial. Cả hai vẫn fail C-002/seed 55. Tắt acknowledgement không sửa lỗi chọn nguồn dữ liệu.
- Giới hạn: MockLLM không phải model production, latency là `unavailable`. Output peer trong reference vốn không được sử dụng; không suy rộng kết quả sang peer có đóng góp nội dung hoặc topology khác. Wrapper dùng scoped patch, chỉ chạy tuần tự; năm test kiểm tra quyết định/trace và khôi phục reference sau cả ba điểm crash. Không có kết luận hidden hay cải thiện production; chưa thực hiện ablation bật verification guard.
- Phạm vi nộp: ablation bắt buộc cho research card; code đặt trong `src/bonus/` theo cơ chế `--extra-shape`, chưa yêu cầu chấm bonus.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
