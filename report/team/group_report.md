# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: NhomV3
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm hiểu bài toán thế nào, chia việc ra sao, thứ tự làm bốn shape.

...

## 3. Giải pháp

Mô tả ba shape nhóm viết (workflow, single, orchestrator): mỗi shape đọc gì, quyết định gì, gọi host ra sao. Chỉ rõ ranh giới code / model (tham khảo [docs/architecture.md](../../docs/architecture.md)), cách handoff được sanitize và trace ghi những event nào.

### Shape B — Single agent dùng ReAct
Trương Việt Công (MSSV 2A202603585) phụ trách Shape B trên nhánh feature/single.

Shape B đọc claim trước khi chạy vòng ReAct, giới hạn tối đa 8 bước. Callback decide dùng kế hoạch đọc cố định theo thứ tự lookup_order, lookup_refund_history, lookup_policy. Các lượt gọi MockLLM được tính vào Budget. Claim không tồn tại trả failed, thiếu mã đơn trả needs_info, còn đơn ngoài phạm vi truy cập hoặc không tìm thấy trả escalated.

Sau vòng lặp, compute_compensation tính mức bồi thường từ dữ liệu đơn và chính sách hiện hành. Ở C-002, ticket khai trễ 5 ngày nhưng dữ liệu đơn ghi 2 ngày nên Shape B từ chối hoàn tiền ở cả 5 seed. Khi quote dương, shape chuyển nguyên số tiền đề xuất vào issue_refund. Host kiểm approval, áp trần theo đơn và dùng ledger để tránh hoàn trùng khi retry. Ví dụ, ở C-014, quote là 150.000 VND, đơn đã được hoàn 30.000 VND nên host chỉ ghi thêm 120.000 VND.

Trace ghi tên tool, tóm tắt quan sát, quote và quyết định cuối. Dữ liệu đơn trong trace lấy từ các trường cho phép của lookup_order. Mọi nhánh trả kết quả đi qua finish(). Shape truyền crash_at xuống host và ghi trace trước khi ném lại InjectedCrash để bên gọi tiếp tục xử lý.

### Shape C — Orchestrator và investigator chỉ đọc

Người phụ trách: Nguyễn Quốc Hưng, MSSV `2A202603553`, nhánh `hung` trong repo `congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents`.

Shape C đọc claim bằng `get_claim_view`, nhưng không chuyển ticket hay toàn bộ claim view sang investigator. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`. Handoff được dựng bằng `make_handoff`, có `facts={}`, scope `owner_order_only` và chỉ hai tool `lookup_order`, `lookup_policy`. Investigator chạy qua `run_readonly_investigators`, đọc đơn trong phạm vi principal và policy hiện hành. Đơn không nhìn thấy trả `escalated`.

Orchestrator tính quote bằng `compute_compensation` trên order view. Quote bằng 0 trả `denied`. Quote dương được chuyển nguyên vẹn vào `durability.issue_refund`; host kiểm approval đúng claim, giới hạn theo đơn và idempotency. Shape không tự trừ khoản đã hoàn. Vì vậy T14 giữ `proposal_amount=150000` nhưng refund thực tế là `120000`. Khi host từ chối, quote vẫn được giữ và audit `policy_denied` do host ghi. Xung đột số tiền khi retry trả `failed`.

MockLLM chỉ nhận handoff đã lọc để xác nhận kế hoạch và quyết định có cấu trúc để soạn lời đáp; không quyết định số tiền hoặc cấp quyền ghi. Mọi lời gọi model và tool đọc được tính vào `Budget`. `crash_at` được truyền xuống host; shape không bắt `InjectedCrash`, và connection luôn được đóng trong `finally`.

Trace chỉ ghi kết quả tìm claim dạng boolean, handoff đã sanitize, khả năng nhìn thấy đơn, số policy, quote, yêu cầu/kết quả của host và quyết định cuối. Không ghi ticket, principal, claim/order row thô, secret, header, SĐT, địa chỉ, tên hàng hay internal note. Trace được ghi trước khi gọi host để còn bằng chứng nếu crash; mọi nhánh trả kết quả đều qua `finish()` để đồng bộ trace, ledger và audit.

## 4. Kết quả

Bảng so sánh 4 shape trên bộ public (từ `src/reports/benchmark.json`): pass rate, pass^5, seed min–max, variance, cost/success, mean/p95 steps. Kèm crash safety (`src/reports/crash.json`) và, nếu có, kết quả tự kiểm trên `student_drop/`.

### Kết quả Shape B
Theo [benchmark.json](../../src/reports/benchmark.json), Shape B đạt 70/70 trial public trên 14 claim và 5 seed 11,22,33,44,55. Pass rate và pass^5 đều đạt 100%, tỷ lệ pass theo seed dao động 100%–100%, phương sai bằng 0. Chi phí mô phỏng là 47,94 VND/lần thành công. Mean/p95 theo số sự kiện trace lần lượt là 8,07/9. Một run đối chiếu là R-single-C-001-s11.

Ma trận student lọc riêng Shape B đạt 62 test pass, gồm kịch bản retry T11 và crash/resume T12. Bốn test riêng của nhóm trong tests/test_team_single.py đều pass. Sau merge, kiểm tra approval ở seed 11 trên cả Workflow, Single và Orchestrator đạt 15/15 lượt. Approval bị thu hồi, hết hạn, thuộc claim khác và đơn đã hoàn đủ đều bị từ chối với audit policy_denied. Ca C-014 giữ tổng tiền hoàn ở mức 150.000 VND trên cả ba shape. Kết quả hidden đang chờ bộ dữ liệu student_drop/.

### Kết quả riêng Shape C trước khi merge

Bằng chứng: `src/reports/orchestrator_benchmark.json`, chạy 14 claim public × 5 seed `11,22,33,44,55`, tổng 70 trial. Shape C đạt pass rate `1.0`, pass^5 `1.0`, seed min–max `1.0–1.0`, variance `0.0`, cost/success mô phỏng `49.00142857142857 VND`, mean/p95 steps `6.0/7.0`. Run id ví dụ: `R-orchestrator-C-001-s11`. Đây là kết quả public, không phải điểm hidden hay bảng so sánh cuối của cả nhóm.

Ma trận student riêng Shape C đạt `62 passed`; 19 test mới trong `tests/test_team_orchestrator.py` đều pass. Bộ test mặc định đạt `73 passed`. Các test mới phủ ticket injection chứa secret/PII, allowlist của handoff, các nhánh trả sớm, approval hỏng, full quote khi top-up, ba cửa sổ crash và xung đột số tiền khi retry. Có test cố ý tạo leak qua stdout/file phụ để kiểm audit phát hiện được mà không chép secret vào report, và test đối chiếu outcome/budget của hai biến thể R3.

Công cụ `python -m tests.audit_team_security` bắt stdout/stderr trong bộ nhớ và quét cả kết quả, trace cùng các file phụ có tên theo run id. Bản trước merge ghi nhận 70 trial Shape C có trace hợp lệ, không phát hiện secret/PII hoặc field của raw row. Workflow và single trong main vẫn là stub, nên chưa thể kết luận an toàn cho hai bản triển khai của đồng đội. Cần chạy lại công cụ trên cả ba shape sau merge. Crash suite host đã sinh `src/reports/crash.json`, đạt `20/20`; điều này được báo riêng với test crash/resume của Shape C.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Lỗi gặp phải (kèm lệnh, output hoặc ảnh chụp) và cách nhóm xử lý.

Phần người 3: môi trường Windows có thư mục temp mặc định của pytest không truy cập được (`PermissionError: WinError 5`). Đã dùng `PYTEST_DEBUG_TEMPROOT` trỏ tới thư mục `.qa/pytest-temp` trong `src/`, rồi chạy lại các bộ test. Không sửa test hoặc mã host để né lỗi.

Đã đối chiếu bản bàn giao với nhánh `hung` của repo nhóm V3 ở commit `034c6c421c198dae67a9211d15e2587d5a378972`: nguồn của nhánh khớp starter đã dùng để kiểm thử. Code Shape A/B trên nhánh này vẫn là stub; commit nộp cuối và `student_drop/` chưa có trong bản bàn giao. Quyết định kiến trúc cuối, điểm hidden và kiểm tra `0 FAIL` cần hoàn tất sau khi merge code của cả nhóm.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`. Nêu thêm giới hạn của nhóm và điều kiện làm kết luận thay đổi.

...

## 8. Tài liệu tham khảo

- Contract, luật nghiệp vụ và runtime do đề Lab 8 cung cấp.
- Tara Bogavelli, Hari Subramani, Roshnee Sharma (2026), [AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows](https://aclanthology.org/2026.aacl-long.44/), AACL-IJCNLP. Dùng cho R3; không suy rộng kết quả MockLLM thành hiệu quả của model thật.
