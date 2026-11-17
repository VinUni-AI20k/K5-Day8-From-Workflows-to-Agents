# Research card

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 — Evaluation confounders |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Zhang et al. (2026), “Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems,” EMNLP 2026, research paper: https://aclanthology.org/2026.emnlp-main.798/ |
| CLAIM | Một kết luận gốc của nguồn | Tác giả cảnh báo kết quả hiệu quả MAS có thể phụ thuộc setup; prompt và topology khởi điểm khác nhau làm khó quy kết cải thiện cho thay đổi cấu trúc. Một số cải thiện được báo cáo còn phụ thuộc đường tool hoặc baseline đã đơn giản. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết luận paper dựa trên các thiết lập và phương pháp đánh giá được nghiên cứu; không dự đoán trực tiếp kết quả trên claim tổng hợp LogiX-VN hoặc MockLLM. |
| HYPOTHESIS | Nếu đổi shape A→B, metric X sẽ đổi thế nào | So workflow với orchestrator trên cùng input: pass rate giữ gần nhau; orchestrator tăng cost/success do thêm bước model và investigator. Chọn workflow nếu pass không giảm. |
| METHOD | Biến giữ cố định / biến duy nhất thay đổi | Dùng chung MockLLM, public corpus, seeds `11,22,33,44,55`, tool APIs, bảng giá và evaluator. Biến được so sánh là shape/topology; đo pass rate, pass^5, seed variance, cost/success và steps. Số call là kết quả của topology. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo | Confounder: prompt/đường gọi trong mỗi shape khác nhau; corpus nhỏ có thể che khuất lỗi hiếm. Báo pass rate, pass^5, variance, cost/success; đối chiếu T02/seed 55 và kiểm approval/trace. |

## Kết quả ablation

- Lệnh đã chạy: `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11`, `R-orchestrator-C-001-s11`; `src/reports/benchmark.json`.
- Kết quả so với hypothesis: đúng trên public. Workflow và orchestrator đều đạt pass rate 1.000, pass^5 1.000, variance 0; cost/success lần lượt 27.86 và 56.29 VND mô phỏng. Workflow thấp hơn khoảng 50.5% cost/success. Đây là so sánh shape trên benchmark public, không phải bằng chứng đủ để khẳng định quan hệ nhân quả ngoài setup này.
- Giới hạn: 14 claim × 5 seed; MockLLM không phải model sản xuất, latency là `unavailable`; chưa có nhãn hidden/grader chính thức.
