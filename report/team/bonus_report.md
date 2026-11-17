# Bonus report: B3

Nhóm: Problem Solver. Chủ đề: verifier bằng code trước khi ghi tiền.

## CLAIM và BOUNDARY

[Google Research, 2026](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) cho thấy phối hợp và cơ chế kiểm chứng ảnh hưởng lan truyền lỗi. Nguồn khảo sát 180 cấu hình với model/benchmark riêng; bài này chỉ kiểm một can thiệp trên MockLLM, không nhận tái lập định lượng của nguồn.

## Hypothesis và thiết kế thí nghiệm

Thêm verifier bằng code sẽ tăng pass rate và pass⁵ của swarm, giảm lỗi tin ticket, đồng thời tăng cost/success. Giữ MockLLM, registry tool, corpus, seed, bảng giá và evaluator; biến duy nhất là bật/tắt verifier. Chi phí các lượt đọc và quote thêm được tính vào budget.

Lệnh tái lập trong src/: `python -m bonus.reproduce`.

## Thực hiện và phép đo

`src/bonus/swarm_verified.py` giữ luồng swarm, thêm fresh lookup_order và đối chiếu delay_days/status/damage_verified trong `verifier.py`. Nếu khác, tính lại quote tối đa một lần; chạy trước cả nhánh quote = 0 để sửa trường hợp ticket nói thiếu ngày. Không sửa host, policy, metric, config hay public data. 16 claim đối kháng có nhãn viết tay trong bonus/cases.jsonl, không lấy quote làm oracle.

Public:

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 27.86 | 4.43/5 |
| swarm | 69/70 | 0.9857 | 0.9286 | 0.9286–1.0000 | 0.000816 | 49.57 | 2.80/3 |
| swarm_verified | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 57.57 | 3.67/4 |

Đối kháng:

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 80/80 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 30.00 | 4.50/5 |
| swarm | 74/80 | 0.9250 | 0.6250 | 0.6250–1.0000 | 0.022500 | 58.40 | 3.19/4 |
| swarm_verified | 80/80 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 65.90 | 4.38/6 |

## Safety và minh họa

Safety recount: 750 trial trên 5 shape và hai corpus, 0 secret leak, 0 PII leak, 0 approval bypass, 0 execution error. Crash bổ sung 12/12. Public verifier can thiệp 1 lần; đối kháng 15 lần; không có trial sửa quá một vòng. Nguồn: `src/reports/bonus_safety.json`.

Trace `R-swarm_verified-C-002-s55`: swarm tin ticket trễ 5 ngày, trong khi order là 2 ngày. Verifier đưa quote từ 20.000 về 0, không ghi ledger. Xem `src/reports/bonus_trace_example.json`.

## Tái lập, kết luận và giới hạn

Chạy `python -m bonus.reproduce` trong src/. So sánh cùng claim/seed/giá/evaluator. Verifier khôi phục độ đúng quan sát được của workflow nhưng tốn nhiều chi phí hơn. Phần swarm chưa chứng minh thêm giá trị khi dữ liệu có cấu trúc đủ quyết định. Đổi kết luận khi có điều tra mở hoặc dữ liệu không cấu trúc và đo lại trên model thật. MockLLM, lỗi cố ý, latency unavailable; workflow đạt pass rate hidden local 1.00, qua ngưỡng 0.80; việc cho điểm bonus do giảng viên xác nhận.

## B3 trên hidden

Kết quả chấm local trên pack được cung cấp, dùng CLI benchmark và metric nguyên bản với `--labels hidden_labels.json`; bỏ qua `expected` mồi trong claim. Điểm chính thức do giảng viên xác nhận.

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.00 | 4.53/5 |
| swarm | 194/200 | 0.9700 | 0.8500 | 0.8500–1.0000 | 0.003600 | 52.49 | 2.93/3 |
| swarm_verified | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 60.46 | 3.88/4 |

Verifier can thiệp 6 lần, tối đa một vòng/trial; leak/bypass/error đều 0 trên 1000 trial recount. Crash hidden 30/30. Shape chọn workflow đạt điều kiện ngưỡng 0.80 quan sát được. [Báo cáo kiểm chứng](hidden_validation.md).
