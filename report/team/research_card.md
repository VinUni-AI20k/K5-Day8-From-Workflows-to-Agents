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
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders; cô lập chi phí bước draft trong workflow. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Kapoor và cộng sự, *AI Agents That Matter*, arXiv:2407.01502v1, 2024, mục 2 và 6. [Bản gốc](https://arxiv.org/html/2407.01502v1). Loại bằng chứng: nghiên cứu thực nghiệm về benchmark agent. Đây là nguồn thay thế đã kiểm tra, không phải paper EMNLP 2026 nêu ở bảng gợi ý. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Đánh giá agent cần xem đồng thời độ chính xác và chi phí; so sánh thiếu kiểm soát chi phí có thể gây hiểu sai về lợi ích của thiết kế phức tạp. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Nguồn nghiên cứu các benchmark như HumanEval với LLM thật. Lab này dùng MockLLM, dữ liệu LogiX-VN giả và giá mô phỏng; không chuyển số liệu của paper sang lab hoặc suy ra latency thực tế. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Trước khi chạy: tắt duy nhất bước draft sẽ giữ nguyên quyết định, ledger, pass rate và pass^5; giảm 1 model call/trial và khoảng 1 VND mô phỏng/trial. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Workflow gốc so với workflow_no_draft, giữ nguyên tools, policy, evaluator, 14 claim public, seed 11/22/33/44/55 và pricing. Mỗi trial có SQLite mới. Backend khi bật vẫn là MockLLM; biến duy nhất là có thực hiện lời gọi draft hay không. Helper dùng scoped patch, không sửa workflow; định danh variant/trace riêng chỉ để tách artifact. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Rủi ro: vô tình đổi hành vi nghiệp vụ hoặc làm mất accounting khi bỏ model call. Đo pass rate, pass^5, seed variance, cost/success, mean model/tool calls; 70 cặp test đối chiếu status, quote, ledger, audit, trace events và tool calls bằng evaluator thật. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn, trong `src/`):

```powershell
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.research_draft_ablation:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

- Run id / file report: `src/reports/research_ablation.json`; ví dụ cặp `R-workflow-C-001-s11` và `R-workflow_no_draft-C-001-s11`.
- Kết quả: hypothesis được hỗ trợ trên public, 70/70 trial pass cho mỗi variant, pass rate và pass^5 đều 1.0, seed variance đều 0.

| Metric | Workflow (draft bật) | Workflow_no_draft |
| --- | ---: | ---: |
| Cost/success (VND mô phỏng) | 28.862857 | 27.857143 |
| Tổng cost của 70 trial | 2020.40 | 1950.00 |
| Mean model calls | 1 | 0 |
| Mean tool calls | 2.785714 | 2.785714 |
| Mean / p95 trace steps | 4.428571 / 5 | 4.428571 / 5 |

Giảm tổng cộng 70.40 VND mô phỏng (khoảng 3.48%). `steps` là số event trong trace, không phải `Budget.steps`; vì workflow không trace lời gọi draft riêng nên steps không giảm. Thí nghiệm không đổi topology: nó cho thấy một thành phần phụ có thể đổi cost mà không đổi kết quả nghiệp vụ.

- Giới hạn: workflow hiện gọi nhưng không đưa nội dung draft vào `RunResult`; thí nghiệm không đo chất lượng câu trả lời khách hàng. MockLLM không phải model sản xuất, latency là `unavailable`. Không kết luận multi-agent luôn đắt hơn hoặc workflow luôn tốt hơn. Chưa có kết quả hidden hay quyết định kiến trúc cuối.
- Nguồn: đã đọc bản gốc liên kết ở trên ngày 2026-11-17. Chưa xác minh được paper có đúng tên *Rethinking Evaluation of MAS Efficiency* trong mẫu; không gán kết luận cho nguồn đó. Cần nhóm/coach xác nhận nếu bắt buộc dùng đúng paper trong slide.
- Helper nằm trong `src/bonus/` vì đây là vùng mở rộng của lab; thí nghiệm phục vụ research card bắt buộc, không đăng ký topic bonus hoặc tạo `bonus_report.md`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
