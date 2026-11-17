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
| CÂU | R1 / R2 / R3 / R4 | R2 · Failure taxonomy: trial fail của swarm ở seed 55 thuộc nhóm lỗi nào trong MAST? |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Cemri et al., *Why Do Multi-Agent LLM Systems Fail?* (MAST), NeurIPS 2025, https://arxiv.org/abs/2503.13657. Loại bằng chứng: phân tích và gán nhãn trace thật của nhiều framework multi-agent, có đo độ đồng thuận giữa người gán nhãn. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Lỗi của hệ multi-agent gom được vào 3 nhóm: (1) đặc tả và thiết kế hệ thống, (2) lệch nhau giữa các agent, (3) kiểm chứng và kết thúc task. Lỗi không chỉ đến từ model yếu: một phần lớn đến từ thiết kế hệ thống, ví dụ thiếu bước kiểm chứng. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Trace của các framework MAS dùng LLM thật (GPT, Claude, …) trên task lập trình, toán và hỏi đáp. Paper không đo task hoàn tiền, không dùng MockLLM, và tỉ lệ giữa các nhóm lỗi phụ thuộc framework và task. Lab chỉ mượn **bảng phân loại**, không mượn tỉ lệ. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trial fail C-002 seed 55 thuộc nhóm (3) **kiểm chứng**: swarm nhận số ngày trễ khai trong ticket (5) mà không đối chiếu với order row (2), nên trả 20000 thay vì từ chối. Nếu tắt riêng kênh "dùng số ngày trễ từ ticket", lỗi phải biến mất: pass rate tăng từ 69/70 (0,986) lên 70/70 (1,000), pass rate ở seed 55 từ 13/14 lên 14/14, seed variance về 0, cost/success giảm nhẹ (dưới 2 %). Dự đoán này dựa trên việc đọc `REFERENCE_WEAKNESS` trong code trước khi chạy. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM (vẫn gọi `parse` nên số model call không đổi), tool, handoff, host, `data/public_claims.jsonl` (14 claim), seed `11,22,33,44,55`, `config/pricing.yaml`, evaluator `trial_pass`, chạy trong cùng một lệnh benchmark. Biến duy nhất được thay đổi: swarm có được dùng số ngày trễ đọc từ ticket hay không. Biến thể `swarm_no_ticket_delay` (`src/research/r2_swarm_no_ticket_delay.py`) bọc nguyên swarm tham chiếu, chỉ thay `parse_delay_days` bằng hàm trả `None`. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: trả tiền sai do tin dữ liệu người dùng mà không kiểm chứng. Host **không** chặn được lỗi này vì approval và idempotency đều hợp lệ, chỉ có dữ kiện là sai. Đo bằng: pass rate, pass^5, pass rate theo seed, seed variance, cost/success, và lý do fail `status resolved != denied`. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn, trong `src/`): `python -m lab8.benchmark --shapes swarm,swarm_no_ticket_delay --extra-shape swarm_no_ticket_delay=research.r2_swarm_no_ticket_delay:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/r2_ablation.json`
- Run id / file report: `src/reports/r2_ablation.json`, chạy trên commit `81a4d15` kèm file biến thể chưa commit. Trial fail duy nhất: `R-swarm-C-002-s55` (claim C-002, seed 55, 6 tool call, 3 model call). Biến thể dùng lại hàm `make_run_id("swarm", …)` của swarm nên trial tương ứng cũng có run id `R-swarm-C-002-s55`. Trong file JSON, phân biệt hai trial bằng cột `shape`.
- Kết quả so với hypothesis: **đúng**.

  | Metric | swarm | swarm_no_ticket_delay |
  | --- | ---: | ---: |
  | Pass rate | 0,986 (69/70) | 1,000 (70/70) |
  | pass^5 | 0,929 (13/14 claim) | 1,000 (14/14) |
  | Pass rate seed 55 | 0,929 | 1,000 |
  | Seed variance | 0,000816 | 0 |
  | Tổng cost mô phỏng | 3420,12 VND | 3410,10 VND |
  | Cost/success | 49,57 VND | 48,72 VND |
  | Model call trung bình | 3,0 | 3,0 |

  Toàn bộ chênh lệch nằm ở một trial C-002 seed 55. Swarm ghi `model_override` với `delay_days = 5`, gọi thêm một lần `compute_compensation` (vì vậy tổng cost chênh khoảng 10 VND, đúng bằng một tool call), rồi trả 20000 khi đáng ra phải từ chối. Theo MAST, lỗi này thuộc nhóm (3) **kiểm chứng**: dữ kiện chưa được đối chiếu với nguồn có cấu trúc trước khi dùng để tính tiền. Có thể đọc thêm theo nhóm (2): kết quả `lookup_order` của investigator bị ghi đè bởi một peer đọc ticket. Tuy vậy, sửa bằng cách đối chiếu, tức là kiểm chứng, là đủ để hết lỗi. Shape `single` của nhóm luôn tính quote từ order row và qua cả 5 seed của C-002 (`src/tests/test_team_single.py`).
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Lỗi của swarm được cài sẵn theo quy tắc `seed % 5 == 0`, nên ablation chỉ chứng minh **cơ chế** gây lỗi, không ước lượng được tần suất lỗi của LLM thật. Mẫu nhỏ (70 trial, chỉ 1 trial khác nhau), nên không kiểm định thống kê. Kết quả chỉ trên bộ public, chưa chạy trên `student_drop/`. Cost là cost mô phỏng theo `pricing.yaml`, không phải hóa đơn API.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
