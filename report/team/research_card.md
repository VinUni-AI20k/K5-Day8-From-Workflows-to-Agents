# Phiếu nghiên cứu

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 · Lựa chọn kiến trúc |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Bogavelli, Subramani và Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), bài báo AACL-IJCNLP 2026/benchmark. Nghiên cứu đánh giá 18 cấu hình theo chiến lược điều phối, kiểu tác tử, bộ nhớ và công cụ suy nghĩ. |
| CLAIM | Một kết luận gốc của nguồn | AgentArch xem kiến trúc gồm nhiều chiều thiết kế và đánh giá cấu hình một cách có hệ thống; kết quả chỉ áp dụng trong benchmark và các mô hình đã thử nghiệm. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận | Tác vụ quy trình doanh nghiệp, benchmark, mô hình được thử nghiệm và 18 cấu hình của bài báo. Kết quả không chứng minh orchestrator hay nhiều tác tử luôn tốt hơn. |
| HYPOTHESIS | Shape A→B và dự đoán metric | Workflow→orchestrator, giữ các điều kiện lab khác cố định. Dự đoán: tỷ lệ đạt xấp xỉ 1.00 trên corpus có cấu trúc này, còn chi phí/lần đạt tăng 20–50% do các lượt gọi investigator. |
| METHOD | Biến giữ cố định và biến thay đổi | Cùng MockLLM, bộ công cụ, seed 11/22/33/44/55, 14 claim public, bảng giá, world và evaluator. Thay đổi shape workflow/orchestrator và so sánh báo cáo benchmark. Đây là so sánh hai triển khai kiến trúc hoàn chỉnh, chưa cô lập hiệu ứng nhân quả riêng của topology. |
| FAILURE / METRIC | Lỗi dự đoán và cách đo | Dự đoán overhead điều phối/handoff mà không tăng độ chính xác. Đo pass rate, pass^5, phương sai seed, chi phí/lần đạt, số bước trung bình và p95. Quan sát: workflow 1.000/1.000, phương sai 0, 27.86 VND; orchestrator 1.000/1.000, phương sai 0, 46.43 VND, số bước trung bình/p95 là 3.71/4. Giả thuyết đúng về hướng tăng chi phí; cả hai đạt mọi lượt public. |

## Kết quả ablation

- Lệnh đã chạy: `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: Mã từng lượt nằm trong `src/reports/benchmark.json`; ví dụ `R-workflow-C-001-s11`. Báo cáo tổng hợp: `src/reports/benchmark.json`.
- Kết quả so với giả thuyết: Đúng hướng về chi phí, không có chênh lệch tỷ lệ đạt giữa hai shape. Orchestrator tốn thêm 18.57 VND/lần đạt (66.7%); cả hai có pass rate 1.000, pass^5 1.000 và phương sai 0.000000. Mức tăng cao hơn dự đoán 20–50%.
- Giới hạn: Đây là so sánh các triển khai trên fixture nhỏ; nhiều khác biệt trong shape đi cùng nhau, chưa chạy hidden set. MockLLM không đại diện cho mô hình sản xuất; độ trễ `unavailable`.
