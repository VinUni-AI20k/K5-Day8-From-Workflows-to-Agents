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
| CÂU | R1 / R2 / R3 / R4 | R3 — Architecture choices; phần do người 3 chuẩn bị. Nhóm cần thống nhất câu nghiên cứu chính trước khi nộp. |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Bogavelli, Subramani, Sharma (2026), [AgentArch](https://aclanthology.org/2026.aacl-long.44/), AACL-IJCNLP; bằng chứng thực nghiệm trên benchmark enterprise. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Trong 18 cấu hình AgentArch, hiệu quả kiến trúc phụ thuộc model; nghiên cứu không xác lập một cấu hình tối ưu cho mọi trường hợp. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Phạm vi kết luận là các model, cấu hình và tác vụ enterprise được nghiên cứu. Lab này chỉ dùng MockLLM, 14 claim giả và chi phí mô phỏng; không tái lập điểm của paper hoặc đại diện production. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Tách 1 investigator đọc cả order/policy thành 2 investigator, mỗi bên đọc 1 tool, sẽ giữ pass rate và pass^5 (chênh 0 điểm phần trăm), nhưng tăng 1 tool đọc claim cho mỗi trial cần điều tra, tức 10 VND/trial đó theo bảng giá hiện có. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Cố định MockLLM, nội dung prompt, tool có sẵn, corpus, seed 11/22/33/44/55, as_of, bảng giá, logic quote/host và evaluator. Chỉ thay cách phân chia hai tool đọc cho 1 hoặc 2 investigator; dùng cùng runtime. Mỗi trial có SQLite mới. Mã thí nghiệm ở tests/research_orchestrator_r3.py; không sửa file đo lường. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Rủi ro: thêm investigator làm tăng chi phí mà không tăng độ đúng. Đo pass rate, pass^5, seed variance, cost/success và mean tool/model calls bằng benchmark chính thức; rà secret/PII riêng bằng audit và test injection. |

## Kết quả ablation

- Lệnh đã chạy (trong `src/`; môi trường thực thi dùng `.venv/Scripts/python.exe` làm `python`):

```text
python -m lab8.benchmark --shapes orchestrator,orchestrator_split --extra-shape orchestrator_split=tests.research_orchestrator_r3:run_split_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/orchestrator_r3_ablation.json
```

- Run id / file report: `src/reports/orchestrator_r3_ablation.json`; ví dụ cặp `R-orchestrator-C-001-s11` và `R-orchestrator_split-C-001-s11`.
- Kết quả: phù hợp giả thuyết trong phạm vi public. Cả hai bản pass `70/70`, pass rate/pass^5 đều `1.0`, variance `0.0`. Cost/success tăng từ `49.00142857142857` lên `58.287142857142854` VND mô phỏng, chênh `9.285714285714285` VND/trial trung bình. Có 65/70 trial cần điều tra, mỗi trial thêm đúng 1 lượt đọc claim giá 10 VND; 5 trial thiếu order_id trả sớm nên không thêm lượt đọc. Mean tool calls tăng từ `4.642857142857143` lên `5.571428571428571`; mean model calls giữ `1.9285714285714286`.
- Giới hạn: đây là thí nghiệm phân chia công việc của investigator trong Shape C, thực thi tuần tự, không đo tăng tốc song song. Hai bản dùng cùng prompt và code tính tiền, không phải hai agent tự suy luận độc lập. Mean/p95 trace steps đều `6.0/7.0` vì trace ghi event ở mức tổng hợp, không tương ứng từng tool call. Không suy luận về tốc độ hoặc hidden từ kết quả này. MockLLM không phải model sản xuất; latency là `unavailable`.

## Ghi chú tích hợp của người 3

Người chuẩn bị R3: Nguyễn Quốc Hưng — `2A202603553`; nhánh làm việc `hung`, repo nhóm V3.

Mẫu đề yêu cầu chọn **một** câu R1–R4 cho phiếu chính; R1–R4 không phải bốn mục bắt buộc cho mỗi thành viên. Khi merge, giữ nội dung R3 này nếu nhóm chọn R3, hoặc chuyển nó thành phần tham khảo nếu nhóm quyết định chọn câu khác. Quyết định kiến trúc cuối vẫn cần benchmark đủ 4 shape của nhóm.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
