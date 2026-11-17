# Báo cáo nhóm — Problem Solver / LogiX-VN

## 1. Thông tin nhóm

- Nhóm demo - Problem Solver; lớp L3A. Thành viên và phân công: [TEAM.md](../../TEAM.md).

## 2. Mục tiêu và cách tiếp cận

Giải cùng bài toán hoàn phí vận chuyển bằng workflow, single ReAct và orchestrator, dùng swarm tham chiếu để so sánh. Chọn kiến trúc ít tự chủ nhất vẫn đáp ứng nghiệp vụ. Thứ tự triển khai: workflow làm baseline → single → orchestrator → kiểm bảo mật/crash → benchmark → ablation B3.

## 3. Giải pháp

- Workflow: get_claim_view → kiểm order_id → lookup_order theo principal → compute_compensation → issue_refund. Không gọi model.
- Single: run_react tối đa 8 lượt. MockLLM mô phỏng think và được tính budget mỗi lượt; adapter Python chọn tool đọc theo observation, không lấy text model để quyết định tiền. Sau loop shape mới gọi host.
- Orchestrator: MockLLM plan → make_handoff allowlist → investigator chỉ đọc → aggregate → host ghi. Investigator chạy tuần tự; không được cấp write tool. Helper ClaimRun nằm ngay trong workflow.py để ba file shape có thể chạy trên host nguyên bản.
- Chính sách: chỉ dùng policy current đã effective; max(ship, damage), không cộng. Truyền quote đầy đủ; host trừ lịch sử theo đơn và cap approval/paid. Thiếu mã đơn → needs_info; ngoài principal → escalated; quote 0 → denied; quote dương bị host chặn vẫn giữ proposal và audit policy_denied.
- Durability: refund:claim_id dedupe; effect và refund_committed cùng transaction. Truyền crash_at và để InjectedCrash đi ra harness. Kết quả và trace lấy qua finish, không tự khai số ledger.
- Trace/handoff: không gửi parent context, không ghi ticket thô, secret, header, phone, address, item_name hay internal_note. Handoff chỉ có field cho phép và tool đọc. Chi tiết: [kiến trúc](../../docs/architecture.md), [sáu luồng ngang](../../docs/flow_details.md).

## 4. Kết quả

Public 14 claim × 5 seed × 4 shape; nguồn `src/reports/benchmark.json`:

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 27.86 | 4.43/5 |
| single | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.46 | 7.21/8 |
| orchestrator | 70/70 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 47.29 | 6.29/7 |
| swarm | 69/70 | 0.9857 | 0.9286 | 0.9286–1.0000 | 0.000816 | 49.57 | 2.80/3 |

Smoke pass. Cổng host: 103 passed, 248 deselected; ma trận student: 248 passed, 103 deselected. Tổng 351 test gồm test nhóm bổ sung. Crash suite 20/20; recount bổ sung 12/12. Test portability chép đúng ba shape vào host gốc, kiểm seed 55, delta refund và crash/resume. Safety bổ sung: 750 trial, leak/bypass/error đều 0. B3, research và số đo ablation: [research card](research_card.md), [bonus report](bonus_report.md).

Chọn workflow: cùng mức đúng public với chi phí thấp nhất (27.86 VND mô phỏng/success), không cần model. Đã chấm local trên 40 claim × 5 seed bằng nhãn riêng của pack được cung cấp; không suy ra điểm hidden từ public. Kết quả chính thức chờ giảng viên xác nhận.

## Kiểm chứng hidden

Kết quả chấm local trên pack được cung cấp, dùng CLI benchmark và metric nguyên bản với `--labels hidden_labels.json`; bỏ qua `expected` mồi trong claim. Điểm chính thức do giảng viên xác nhận.

| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 29.00 | 4.53/5 |
| single | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 30.68 | 7.42/8 |
| orchestrator | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 49.41 | 6.47/7 |
| swarm | 194/200 | 0.9700 | 0.8500 | 0.8500–1.0000 | 0.003600 | 52.49 | 2.93/3 |
| swarm_verified | 200/200 | 1.0000 | 1.0000 | 1.0000–1.0000 | 0.000000 | 60.46 | 3.88/4 |

Safety recount 1000 trial: secret/PII leak, approval bypass, execution error và lỗi trace đều 0. Crash hidden 30/30; host 20/20. Không cần sửa logic workflow, single, orchestrator hoặc verifier: cả bốn đạt 200/200 trên lần chạy đầu. Giữ nguyên swarm tham chiếu, gồm lỗi cố ý seed 55. Chỉ bổ sung công cụ đo và tài liệu; không đọc nhãn trong shape, không hardcode claim id và không sửa thước đo.

[Phương pháp, giới hạn và lệnh tái lập](hidden_validation.md). Bằng chứng: `src/reports/hidden_summary.json`; run ví dụ `R-workflow-C-H03-s11`.

## 5. Khó khăn và cách xử lý

Môi trường Python ban đầu thiếu PyYAML/pytest. Tạo src/.venv và cài src/requirements.txt; smoke và hai suite sau cài đều xanh. Grader chỉ lấy ba shape cùng bonus/, nên helper được đặt trong workflow.py và được kiểm bằng host nguyên bản. HTML dùng dữ liệu nhúng local; sáu SVG đọc ngang, có vừa chiều cao, zoom, cuộn trái/phải và mở rộng để thuyết trình.

## 6. Tổng hợp đóng góp

Quốc Anh: tech lead/workflow/tích hợp/B3; Bình: BA/acceptance/báo cáo; Hưng: single/QA/crash; Vinh: orchestrator/handoff/benchmark/HTML. Chi tiết trong TEAM.md và bốn báo cáo cá nhân.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency unavailable. A–D có khác adapter/prompt, chưa cô lập topology. Steps phụ thuộc instrumentation. B3 cô lập thêm verifier nhưng lỗi swarm là cố ý; dữ liệu đối kháng do nhóm thiết kế không thay hidden. Kết quả local hidden đã được kiểm chứng; giảng viên xác nhận điểm và người học nộp LMS; không tuyên bố sẵn điểm số. Đo lại nếu phải đọc chứng từ mơ hồ hoặc có điều tra song song.

## 8. Tài liệu tham khảo

- README.md, RULES.md, RUBRIC.md, docs/business_rules.md, docs/contracts.md và docs/metrics.md của đề bài.
- [Google Research — Towards a science of scaling agent systems, 28/01/2026](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/).
- [Hướng dẫn chạy và thuyết trình](../../docs/presentation_guide.md).
