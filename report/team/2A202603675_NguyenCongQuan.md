# Báo cáo cá nhân — 2A202603675_NguyenCongQuan

## 1. Thông tin thành viên

- Họ tên: Nguyễn Công Quân
- MSSV: 2A202603675
- Email: nguyencongquancn06@gmail.com
- GitHub: [nguyencongquana2](https://github.com/nguyencongquana2)

## 2. Phần việc phụ trách

- Shape B — Single Agent tại `src/lab8/shapes/single.py`.
- Test retry/crash của Single Agent tại `src/tests/test_single_team.py`.
- Ablation Workflow–Single và `report/team/research_card.md`.
- Đóng góp mô tả Shape B, khó khăn và tài liệu tham khảo trong báo cáo nhóm.

## 3. Đóng góp cụ thể

- Commit `3dbdd8a`: hiện thực Single Agent bằng `run_react`, tối đa 8 bước và chỉ cấp read tool cho actor.
- Commit `66944d5`: thêm test idempotent retry và crash/resume tại `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`.
- Giữ ranh giới code/model: MockLLM chỉ mô phỏng quyết định/soạn phản hồi; quote do `compute_compensation` tính; chỉ code sau vòng ReAct mới gọi `issue_refund` với quote đầy đủ.
- Trace chỉ ghi control state và kết quả allowlist, không ghi ticket, claim/order row thô, secret hoặc PII.
- Phân tích lát cắt Workflow–Single từ benchmark chính của nhóm và chạy tái lập 140 trial, giữ nguyên model/tool/seed/corpus/pricing/evaluator, chỉ đổi shape.

## 4. Bằng chứng

- Commit CP2: `3dbdd8a feat: implement single-agent claim shape`.
- Commit CP3: `66944d5 test: verify single-agent crash recovery`.
- Test riêng Single: `62 passed`; cổng host sau khi merge: `68 passed`; toàn ma trận student: `248 passed`.
- Test đã thêm: `test_single_retry_keeps_one_refund` và `test_single_crash_then_resume_keeps_one_refund` (ba crash point).
- Bằng chứng chính: `src/reports/benchmark.json`; báo cáo tái lập: `src/reports/ablation_workflow_single.json`; run dẫn chứng `R-single-C-001-s11`.
- Kết quả: Single và Workflow cùng pass rate/pass^5 `1.000`; Single tăng cost/success mô phỏng 6.34% và mean steps 85.48%.

## 5. Công cụ AI đã dùng

- Dùng OpenAI Codex để giải thích contract, hỗ trợ triển khai vòng ReAct, gợi ý test crash/idempotency và soạn khung báo cáo.
- Tôi tự kiểm tra bằng cách đọc `docs/business_rules.md`, `docs/contracts.md`, đối chiếu code với `runtime.py`/`durability.py`, chạy test riêng Single, host gate, toàn bộ student matrix và benchmark có kiểm soát.
- Không dùng AI để tạo số liệu: mọi con số trong báo cáo lấy từ pytest hoặc file JSON do `lab8.benchmark` sinh ra.

## 6. Tự đánh giá

- Hoàn thành đúng phần Single Agent CP2–CP3, có commit kỹ thuật và test riêng.
- Có thể giải thích ranh giới code/model, lý do truyền quote đầy đủ, idempotency key `refund:{claim_id}` và vì sao ticket không phải lệnh.
- Hạn chế: benchmark/ablation dùng MockLLM và public corpus nhỏ; kết quả chính thức vẫn phụ thuộc bộ hidden của giảng viên, còn hidden self-check chỉ chạy được khi nhóm nhận `student_drop/`.
