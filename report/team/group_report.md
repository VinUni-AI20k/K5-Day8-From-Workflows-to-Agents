# Báo cáo nhóm — Lab 8 LogiX-VN

Số liệu dưới đây lấy từ các file sinh bởi công cụ trong `src/reports/`.

## 1. Thông tin nhóm

- Tên nhóm: NhomBDH (chi tiết trong `TEAM.md`).
- Thành viên: xem `TEAM.md`.
- Commit chốt: `ebd88eb` (hoàn thiện đầy đủ cả 3 shape: workflow, single, orchestrator).

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng claims flow trên workflow, single ReAct và orchestrator, rồi so với swarm tham chiếu. Quy tắc về quyền sở hữu đơn, policy hiện hành, approval, số tiền và idempotency luôn do code/host quyết; text trong ticket không được dùng làm nguồn sự thật cho số ngày trễ. Ba shape dùng chung public corpus, seeds `11,22,33,44,55`, MockLLM, giá mô phỏng và evaluator.

## 3. Giải pháp

- **Workflow:** đọc claim qua tool allowlist, xác minh order theo principal, tính quote bằng `compute_compensation`, rồi chuyển quote đầy đủ cho `durability.issue_refund`. Không dùng model để chọn tiền.
- **Single:** chạy `run_react` với giới hạn 8 bước. Agent chỉ gọi tool đọc; code lấy quote từ order/policy có cấu trúc. Sau vòng lặp, host kiểm approval, trần theo order và idempotency rồi mới ghi.
- **Orchestrator:** tạo `handoff.v1` với investigator chỉ có tool đọc. Trace ghi handoff đã sanitize và kết quả đã giới hạn field; quote do code tính, còn host duy nhất được ghi refund. `crash_at` truyền thẳng vào `issue_refund`.

Cả ba shape đều truyền quote đầy đủ để host tự trừ refund trước đó trên cùng order. Trace không chứa ticket, parent secret, raw headers, số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng.

## 4. Kết quả

Benchmark có 14 claim × 5 seed = 70 trial mỗi shape. Các số dưới đây được tính từ `src/reports/benchmark.json`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 3.50 / 4 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 47.85 | 8.50 / 9 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 61.51 | 4.86 / 5 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Swarm có một trial sai ở `C-002`, seed 55: nó tin ngày trễ trong ticket thay vì `delay_days` của order. Workflow, single và orchestrator đều pass toàn bộ 70 trial. Bộ test kiểm tra approval/trace không ghi nhận bypass hoặc secret leak trên public suite. Crash report đạt `20/20`. Official hidden grade chưa có; workspace không chứa `student_drop/` hay grader riêng của giảng viên.

ADR chọn workflow: trên public corpus, pass ngang hai shape phức tạp hơn, cost thấp nhất và không có seed variance. Xem `decision_adr.md` và `research_card.md` để biết lập luận và ablation.

## 5. Khó khăn và cách xử lý

Các cổng chạy thành công: `python -m pytest -q` → 63 passed; `python -m pytest -q -m student -o addopts=` → 248 passed; benchmark 4 shape × 14 claim × 5 seed; crash suite → 20/20. Review chéo phát hiện orchestrator bắt rồi ném lại `InjectedCrash`; đã bỏ phần bắt để crash truyền thẳng theo contract CP3. Không có lỗi kỹ thuật còn mở.

## 6. Tổng hợp đóng góp

Phần thành viên và bảng đóng góp được giữ cho lượt cập nhật tiếp theo theo yêu cầu. Khi điền, mỗi thành viên cần khai commit có nội dung và ít nhất một test đã thêm hoặc sửa trong `TEAM.md`, đồng thời tạo báo cáo cá nhân từ file mẫu.

## 7. Hạn chế và hướng cải thiện

MockLLM chỉ cho hành vi/cost mô phỏng, không phải model sản xuất; latency là `unavailable`. Public corpus có 14 claim nên không đại diện các claim thật hoặc hidden pack. Cần chạy official hidden grade trước khi kết luận về mức pass ngoài public set. Nếu investigator cải thiện độ chính xác trên claim mơ hồ hoặc yêu cầu trust boundary tách biệt, trade-off chi phí có thể đáng xem lại.

## 8. Tài liệu tham khảo

- Bogavelli, Subramani & Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), AACL-IJCNLP 2026.
- `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md` trong repo bài lab.
