# Phiếu nghiên cứu

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 · Lựa chọn kiến trúc |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Bogavelli, Subramani và Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), bài báo AACL-IJCNLP 2026/benchmark. Nghiên cứu đánh giá 18 cấu hình theo chiến lược điều phối, kiểu tác tử, bộ nhớ và công cụ suy nghĩ. |
| CLAIM | Một kết luận gốc của nguồn | AgentArch xem kiến trúc gồm nhiều chiều thiết kế và đánh giá cấu hình một cách có hệ thống; kết quả chỉ áp dụng trong benchmark và các mô hình đã thử nghiệm. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận | Tác vụ quy trình doanh nghiệp, benchmark, mô hình được thử nghiệm và 18 cấu hình của bài báo. Kết quả không chứng minh orchestrator hay nhiều tác tử luôn tốt hơn. |
| HYPOTHESIS | Shape A→B và dự đoán metric | Giữ nguyên topology swarm, chỉ tắt một thành phần: việc tin số ngày trễ ghi trong ticket thay cho `delay_days` của order (khối `REFERENCE_WEAKNESS`). Dự đoán: pass rate tăng từ 0.986 lên 1.000 và pass^5 từ 0.929 lên 1.000, vì lỗi duy nhất của swarm trên bộ public (C-002, seed 55) đến từ thành phần này; số lời gọi model không đổi. Nếu đúng, khoảng cách giữa swarm và workflow là do một quyết định tin dữ liệu, không phải do topology. |
| METHOD | Biến giữ cố định và biến thay đổi | Giữ cố định: MockLLM, bộ công cụ, seed 11/22/33/44/55, 14 claim public, bảng giá, world, evaluator, và topology swarm (peer, parse, handoff, investigator, draft). Biến duy nhất thay đổi: có hay không khối ghi đè `delay_days` bằng số trong ticket. Biến thể `src/bonus/swarm_no_override.py` chép từ `swarm_reference.py`, chỉ bỏ khối đó; chạy cạnh swarm qua `--extra-shape`. |
| FAILURE / METRIC | Lỗi dự đoán và cách đo | Lỗi dự đoán: swarm trả `resolved` cho C-002 ở seed 55 (ticket ghi trễ 5 ngày, order ghi 2 ngày) thay vì `denied`. Đo pass rate, pass^5, pass rate theo seed, phương sai seed, số lời gọi model/tool và chi phí/lần đạt. |

## Kết quả ablation

- Lệnh đã chạy (trong `src/`): `python -m lab8.benchmark --shapes swarm,swarm_no_override --extra-shape swarm_no_override=bonus.swarm_no_override:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_ablation_no_override.json`
- Run id / file report: `src/reports/bonus_ablation_no_override.json`. Trial khác nhau duy nhất: `R-swarm-C-002-s55` (fail, `status resolved != denied`) so với `R-swarm_no_override-C-002-s55` (pass).
- Kết quả so với giả thuyết: **Đúng.** Swarm: pass rate 0.986, pass^5 0.929, seed 55 = 0.929, phương sai 0.000816, 49.57 VND/lần đạt. Swarm không ghi đè: pass rate 1.000, pass^5 1.000, mọi seed = 1.000, phương sai 0, 48.72 VND/lần đạt. Số lời gọi model như nhau (3.00/claim); số tool call 4.66 so với 4.64, chênh do swarm tính lại quote một lần ở trial bị ghi đè. Vậy toàn bộ chênh lệch pass rate giữa swarm và workflow trên bộ public đến từ thành phần này, không phải từ topology. Phần chênh chi phí còn lại (48.72 so với 27.86 VND của workflow) là giá của topology: peer, parse, draft và investigator không mua thêm lượt đạt nào.
- Giới hạn: Chỉ 14 claim public và một trial bất đồng, nên không đủ để kiểm định thống kê. Kết luận dựa trên cơ chế đã biết (`docs/metrics.md`), không dựa trên p-value. Chưa chạy trên bộ hidden. MockLLM không đại diện cho mô hình sản xuất: với model thật, việc đọc ticket có thể cho cả lỗi lẫn lợi ích mà bộ public không đo được. Độ trễ `unavailable`.
