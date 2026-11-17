# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Chưa được cung cấp; cần điền trước khi nộp.
- Thành viên: xem `TEAM.md`; phân công có sáu vai trò nhưng Đào Đức Duy (2A202603900) được ghi cho cả vai trò trưởng nhóm/Thành viên 1 và benchmark/report/Thành viên 6, nên hiện có năm người khác nhau trong danh sách. Có năm báo cáo cá nhân theo năm MSSV duy nhất.
- Commit chốt: mã nguồn được benchmark ở `f176005`; cần chạy lại benchmark và cập nhật hash sau khi chốt/commit report theo `SUBMISSION.md`.
- Lưu ý: thư mục workspace có tên lớp `L3B`, trong khi `SUBMISSION.md` hiện quy định repo nộp `L3A`; nhóm cần xác minh đúng lớp/tên repo, không tự đổi theo suy đoán.

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai ba shape A/B/C để xử lý cùng contract và so sánh với shape swarm reference D.
Theo bảng phân công, Hùng phụ trách workflow, Nhân phụ trách single-agent, Hưng phụ trách
orchestrator; vai trò tích hợp, kiểm thử và benchmark/report được giao cho các thành viên còn
lại. Nền tảng/contract được chốt trước khi ba shape làm song song; benchmark chạy sau khi tích
hợp. Tên/MSSV chính thức và đóng góp được xác minh của các thành viên còn lại cần điền từ
TEAM.md/nhóm.

## 3. Giải pháp

Workflow đọc claim/order/policy qua tool, code tính quote rồi gọi host. Single-agent dùng vòng
ReAct có giới hạn 8 bước và tool chỉ đọc; model không quyết định số tiền hay ghi refund. Shape
orchestrator tạo handoff theo allowlist, investigator chỉ đọc, còn orchestrator gọi host. Cả ba
truyền full quote để host áp approval/cap và giữ quyền ghi ledger. Workflow trace chỉ ghi ID,
view order đã allowlist, quote, verdict và quyết định; không ghi ticket, approval hay effect row.
Trace của các shape phải tuân thủ [docs/contracts.md](../../docs/contracts.md).

## 4. Kết quả

Benchmark do `lab8.benchmark` sinh, 14 claim × 5 seed = 70 trial mỗi shape:

| Shape | Pass | Pass^5 | Seed min–max | Variance | Cost/success mô phỏng (VND) | Mean/p95 steps |
|---|---:|---:|---:|---:|---:|---:|
| workflow | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 28.87 | 4.43 / 5 |
| single | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 54.65 | 10.64 / 12 |
| orchestrator | 1.000 (70/70) | 1.000 | 1.000–1.000 | 0.000000 | 46.43 | 2.79 / 3 |
| swarm | 0.986 (69/70) | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Crash report hiện có `20/20`. Swarm có một trial lỗi `status resolved != denied` ở seed 55. Hidden self-check/hidden grade chưa có. Giá là mô phỏng, không phải API bill; latency unavailable. Người dùng xác nhận đã chạy lại benchmark bằng `.venv`; output/version chính xác chưa được lưu trong phiên này.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Interpreter của agent không có `python` trên PATH; benchmark ban đầu được chạy bằng `python3`.
Người dùng sau đó xác nhận đã chạy lại trong `.venv`, theo dải Python được tài liệu hỗ trợ.
Output console và phiên bản cụ thể chưa được lưu trong workspace. Hidden report chưa được cung
cấp.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp, commits, tests và report evidence được liệt kê trong `TEAM.md` và các báo cáo
cá nhân. Git history xác nhận test mới trong commit workflow `a81d469` và orchestrator `d4e1899`;
commit single-agent `303976a`, T003 `deac9b2` và crash report `42c8cf2` không chứa test mới. Do đó
chưa đủ bằng chứng để xác nhận mọi thành viên có test riêng trong lịch sử branch. Các thành viên
cần bổ sung hoặc xác nhận bằng chứng trước khi nộp; không gán nhầm test hay commit.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency `unavailable`; bộ public chỉ có 14 claim; chi phí VND
là mô phỏng. Kết quả công khai không thay thế hidden grade trên 40 claim × 5 seed và không chứng
minh workflow sẽ đạt ngưỡng hidden 0.75/must-pass. Kết luận đổi nếu hidden cho thấy workflow
không đạt cổng, hoặc benchmark tái lập trên Python được hỗ trợ cho kết quả khác.

## 8. Tài liệu tham khảo

1. ACL Anthology, “Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems,”
   EMNLP 2026: https://aclanthology.org/2026.emnlp-main.798/.
2. `README.md`, `RUBRIC.md`, `docs/contracts.md`, `docs/business_rules.md`,
   `src/reports/README.md`.
