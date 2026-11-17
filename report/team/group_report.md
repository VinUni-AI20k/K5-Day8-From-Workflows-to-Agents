# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Dota
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): chưa chốt; phần dưới là checkpoint giai đoạn 1–2, nhánh `thanh-ledger-evaluation` từ main `20b2fba`.

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

...

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

**Baseline 2026-11-17, chưa phải kết quả cuối:** 14 claim × 5 seed × 4 shape = 280 trial. Single và orchestrator vẫn là stub, phải chạy lại sau khi tích hợp, không coi pass rate 0 của stub là bằng chứng về chất lượng kiến trúc.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1.000000 | 1.000000 | 1–1 | 0 | 28.862857 | 4.428571 / 5 |
| single — chưa triển khai | 0 | 0 | 0–0 | 0 | null | 1 / 1 |
| orchestrator — chưa triển khai | 0 | 0 | 0–0 | 0 | null | 1 / 1 |
| swarm | 0.985714 | 0.928571 | 0.928571–1 | 0.000816327 | 49.566957 | 2.8 / 3 |

Swarm fail một trial C-002, seed 55 (`R-swarm-C-002-s55`): lấy ngày trễ từ ticket thay vì order. Đây là điểm yếu đối chứng có chủ đích; test student của swarm chấp nhận lỗi này, nhưng benchmark vẫn tính là fail. Không so trực tiếp steps thấp hơn thành hiệu quả cao hơn vì steps ở đây là số event trace.

Crash suite `src/reports/crash.json` đạt **20/20**. Suite có sẵn đo host và một kịch bản swarm; test riêng của Thành bổ sung workflow ở cả ba điểm crash, mở lại kết nối, resume/retry nhiều lần, C-014 và approval. Bộ mặc định hiện **156 passed**; student workflow/swarm **124 passed**. Chưa xác nhận single/orchestrator.

Research ablation từ `src/reports/research_ablation.json`: bật/tắt draft workflow, mỗi variant 70/70 pass; cost/success 28.862857 → 27.857143 VND mô phỏng, tổng giảm 70.40 VND (3.48%). Xem research card để biết biến kiểm soát, nguồn và giới hạn. Chưa có kết quả hidden.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

Ghi nhận môi trường của Thành: `.venv` trước đây dùng Python 3.15; `python -m lab8.smoke` báo thiếu PyYAML, `python -m pytest -q` báo `No module named pytest`. Khi cài requirements, PyYAML phải build và báo `Microsoft Visual C++ 14.0 or greater is required`. Đã tạo lại môi trường bằng Python 3.11.9 có sẵn và cài requirements; smoke pass. Sau cập nhật workflow và bổ sung test giai đoạn này, bộ mặc định đạt 156 passed. Đây là lỗi môi trường, không thay host hoặc dependency constraints để né lỗi.

Tên paper R4 trong mẫu chưa được xác minh; research card ghi rõ nguồn thay thế đã đọc là *AI Agents That Matter* (2024), không gán nội dung cho paper EMNLP 2026 chưa xác minh.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

...
