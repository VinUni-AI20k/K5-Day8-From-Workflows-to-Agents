# Báo cáo cá nhân — Mai Lê Bá Vương

## 1. Thông tin thành viên

- Họ tên: Mai Lê Bá Vương
- MSSV: 2A202603872
- Email: 26ai.vuongmlb@vinuni.edu.vn
- GitHub: bavuong2005

## 2. Phần việc phụ trách

Phụ trách shape swarm tham chiếu: đọc luồng xử lý, kiểm chứng baseline public, phân tích lỗi T02 theo seed và bổ sung test cho cổng approval. Khi ba shape do nhóm triển khai hoàn thành, tham gia tổng hợp benchmark bốn shape và quyết định kiến trúc.

## 3. Đóng góp cụ thể

- Đối chiếu `src/lab8/shapes/swarm_reference.py` với luật nghiệp vụ, contract và nhãn public. Swarm đọc claim, tạo handoff chỉ gồm field cho phép, dùng investigator có tool đọc để lấy order/policy và quote, rồi gọi host `issue_refund` để kiểm approval và ghi ledger.
- Phân tích T02: order `O-202` ghi `delay_days=2`, nên quote đúng là 0 và kết quả đúng là `denied`. Seed 11 giữ dữ liệu order; seed 55 dùng số 5 ngày trong ticket, ghi `model_override`, quote 20.000 VND và trả `resolved`. Đây là lỗi tin dữ liệu ticket thay cho order, không phải lỗi của cổng approval.
- Thêm `src/tests/test_swarm_approval_seed55.py`: kiểm ở seed yếu 55, claim C-007 có approval hết hạn vẫn bị host từ chối, không có refund và có audit `policy_denied`. Test pass; commit kỹ thuật `9f7faa6`.

## 4. Bằng chứng

- `src/reports/swarm_baseline.json`: 69/70 trial pass; pass rate 0,985714; pass^5 13/14 = 0,928571; seed variance 0,0008163; cost/success mô phỏng 49,57 VND; mean/p95 steps 2,8/3. Seed 11, 22, 33, 44 đều pass 14/14; seed 55 pass 13/14.
- Trial `R-swarm-C-002-s11`: `denied`, quote 0, pass. Trace có handoff, investigator thấy order trễ 2 ngày và quote `no_entitlement`.
- Trial `R-swarm-C-002-s55`: `resolved`, fail với lý do `status resolved != denied`. Trace có `model_override.delay_days=5` và quote 20.000 VND.
- Lệnh kiểm test cá nhân (chạy trong `src/`): `python -m pytest -q tests/test_swarm_approval_seed55.py`. Kết quả: `1 passed in 0.07s`.
- Commit kỹ thuật: `9f7faa6` — `test: verify swarm approval gate at weak seed`.

## 5. Công cụ AI đã dùng

Dùng ChatGPT/Codex để đối chiếu tài liệu, trace và benchmark, hỗ trợ soạn test và báo cáo. Tự kiểm bằng dữ liệu order, nhãn T02 trong `public_claims.jsonl`, trace hai seed, số liệu do `lab8.benchmark` sinh ra và kết quả chạy test mới.

## 6. Tự đánh giá

Đã xác định được nguyên nhân và phạm vi lỗi seed 55 của swarm, lưu baseline public và có test mới chạy xanh. Còn phải tổng hợp so sánh bốn shape sau khi nhóm hoàn thành ba shape còn lại. MockLLM và giá mô phỏng không đại diện cho model hay chi phí sản xuất; latency không được đo.
