# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: NHOMSH
- Thành viên: Nguyễn Tiến Đạt (2A202603922, L3B), xem `TEAM.md`.
- Commit triển khai: `03f0731`; benchmark public được sinh bằng code ở commit này.

## 2. Mục tiêu và cách tiếp cận

Xử lý claim hoàn phí trên cùng fixture bằng bốn shape, giữ các quyết định về tiền, approval, giới hạn theo đơn và ghi ledger ở host. Hoàn thiện workflow, single, orchestrator; dùng swarm có sẵn làm đối chứng. Thêm kiểm tra claim không tồn tại.

## 3. Giải pháp

- **Workflow:** đọc claim/order qua read tools, gọi `compute_compensation`, rồi chuyển nguyên quote cho `issue_refund`. Không dùng model.
- **Single:** chạy ReAct tối đa 8 bước với read tools; model không có quyền ghi hoặc quyết số tiền. Host kiểm approval và ghi refund sau vòng lặp.
- **Orchestrator:** tạo handoff allowlist; investigator chỉ có `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`. Trace chỉ ghi handoff đã lọc, kết quả tool an toàn và quyết định; không ghi ticket, secret, header, địa chỉ, số điện thoại, ghi chú nội bộ hoặc tên hàng.

Ba shape đều truyền quote đầy đủ để host tự áp dụng approval, idempotency và trần refund theo đơn.

## 4. Kết quả

Public benchmark: 14 claim × 5 seed × 4 shape = 280 trial. Số liệu lấy từ `src/reports/benchmark.json`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 3.43 / 4 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 31.94 | 5.43 / 6 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 56.29 | 5.29 / 6 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Swarm có một trial sai ở T02, seed 55: tin số ngày trên ticket thay vì `delay_days` trong order. Host suite đạt 54 passed; student suite đạt 258 passed; crash suite đạt `20/20`. Bộ hidden và grader chính thức không có trong workspace nên chưa chạy; ngưỡng hidden 0.75 chưa được xác nhận. Chọn `workflow` theo benchmark public vì ba shape nhóm viết đều pass 100%, còn workflow có cost/success thấp nhất.

## 5. Khó khăn và cách xử lý

Windows `python.exe` mặc định bị chặn và thư mục tạm mặc định không truy cập được trong sandbox. Dùng interpreter `src/.venv/Scripts/python.exe` và đặt `TEMP`/`TMP` vào thư mục tạm trong `src/`; smoke, pytest và các công cụ benchmark chạy thành công.

## 6. Tổng hợp đóng góp

Chi tiết ở `TEAM.md` và báo cáo cá nhân `report/team/2A202603922_NguyenTienDat.md`. Codex được dùng hỗ trợ triển khai và soạn báo cáo; các lệnh kiểm tra và kết quả benchmark được ghi ở trên.

## 7. Hạn chế và hướng cải thiện

MockLLM và giá token là mô phỏng, không đại diện model/chi phí API thực; latency không đo được. Public corpus chỉ có 14 claim. Cần đánh giá trên bộ hidden có nhãn của giảng viên trước khi kết luận shape chọn đạt ngưỡng chính thức.

## 8. Tài liệu tham khảo

- `docs/business_rules.md`, `docs/contracts.md`, `docs/metrics.md`.
- Zhang et al. (2026), *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026: https://aclanthology.org/2026.emnlp-main.798/.
