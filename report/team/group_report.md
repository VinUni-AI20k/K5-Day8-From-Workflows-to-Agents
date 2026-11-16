# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: 4AnhEm
- Thành viên: bốn thành viên trong `TEAM.md`; issue GitHub #1 đóng sau khi ghi nhận danh tính.
- Commit chốt: cập nhật sau commit báo cáo cuối.

## 2. Mục tiêu và cách tiếp cận

So sánh workflow, single ReAct, orchestrator và swarm trên cùng claim, seed, world, policy pricing và evaluator. Quy tắc tiền, approval, ownership, giới hạn theo đơn, idempotency và ghi ledger thuộc host code. Model/shape không được tự ghi refund; quote phải được gửi đầy đủ để host áp dụng cap.

## 3. Giải pháp

- **Workflow:** đọc claim view, lookup order theo principal, tính quote bằng structured order và policy hiện hành, rồi gọi host. Không dùng nội dung ticket để tính tiền.
- **Single:** chạy ReAct tối đa 8 bước với tool đọc; model không có tool ghi. Quote lấy từ tool code, sau đó shape gọi host.
- **Orchestrator:** dựng handoff qua allowlist, chỉ cấp tool đọc cho investigator, trace nội dung handoff đã sanitize; orchestrator chuyển quote host xử lý.
- **Swarm:** shape tham chiếu; được dùng làm đối chứng. Ở seed chia hết cho 5 có chủ ý tin số ngày trong ticket và bị lộ ở C-002/s55.

Trace không chứa nguyên văn ticket, principal ID, dữ liệu liên hệ, ghi chú nội bộ, raw headers hoặc canary secret. Handoff chỉ có task, request/claim ID, facts đã allowlist và tên tool đọc.

## 4. Kết quả

Nguồn số liệu: `src/reports/benchmark.json` (14 claim × 5 seed, 70 trial/shape) và `src/reports/crash.json`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 2.86 / 3 |
| Single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 31.54 | 2.79 / 3 |
| Orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 46.43 | 3.71 / 4 |
| Swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Crash suite: 20/20. Host test gate: 54 passed. Student matrix: 248 passed. Submission checker validates shape format and report artifacts; member contribution attribution remains pending in `TEAM.md`. Chọn workflow vì pass tương đương các shape khác nhưng cost thấp nhất trên corpus này. Xem chi tiết và giới hạn trong `decision_adr.md`; ablation topology ở `research_card.md`.

## 5. Khó khăn và cách xử lý

Ba shape ban đầu là stub. Đã triển khai theo contract có sẵn, forward crash injection và để host là nơi duy nhất ghi refund. Kiểm tra bằng host gate, toàn bộ student matrix, benchmark và crash suite. Không ghi log thông tin ticket nguyên văn vào trace.

## 6. Tổng hợp đóng góp

Danh tính bốn thành viên được lấy từ GitHub issue #1; issue không nêu phân công, commit hay test của từng người. Không gán đóng góp khi chưa có bằng chứng. Mỗi thành viên cần cập nhật phần vai trò, commit, test và báo cáo cá nhân trong `TEAM.md` / `report/team/`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; giá là mô phỏng VND, latency không khả dụng. Corpus công khai chỉ có 14 claim và 5 seed; hidden grader/self-check không chạy. So sánh shape là so sánh các triển khai hoàn chỉnh, không cô lập riêng hiệu ứng topology. Nên kiểm tra thêm corpus đại diện và xác nhận kết quả hidden trước khi chốt kết luận rộng hơn.

## 8. Tài liệu tham khảo

- Bogavelli, T., Subramani, H., & Sharma, R. (2026). *AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows*. AACL-IJCNLP 2026. https://aclanthology.org/2026.aacl-long.44/
