# Báo cáo cá nhân — 2A202603418_TranThanhTung

## 1. Thông tin thành viên

- Họ tên: Trần Thanh Tùng
- MSSV: 2A202603418
- Email: tranthanhtung306thd@gmail.com
- GitHub: tungtran306

## 2. Phần việc phụ trách

- **Checkpoint 2 (CP2):** Cài đặt và hiện thực hóa ba kiến trúc cốt lõi của bài toán xử lý claim hoàn phí vận chuyển LogiX-VN:
  - Shape A (`workflow`): Quy trình tuần tự tất định bằng code Python, tính toán đền bù chính xác, không phụ thuộc LLM vào logic tiền.
  - Shape B (`single`): Single ReAct agent có giới hạn tối đa 8 bước, chỉ gọi read tools (`lookup_order`, `compute_compensation`), host là bên duy nhất ghi ledger.
  - Shape C (`orchestrator`): Mô hình Orchestrator kết hợp các investigator chỉ đọc qua sanitized handoff.
- **Checkpoint 3 (CP3):** Kiểm thử và đảm bảo tính bền vững (durability), cơ chế ghi tiền an toàn không ghi trùng lặp (idempotency với khóa `refund:{claim_id}`), xử lý ngắt và phục hồi sau sập (`InjectedCrash` propagation), và ranh giới bảo mật handoff khử canaries/PII.
- **Kiểm thử mở rộng:** Thiết kế và bổ sung bộ test resilience/idempotency/crash recovery độc lập (`src/tests/test_cp3_resilience.py`).

## 3. Đóng góp cụ thể

- **Commits chính:**
  - `9cc25fe` — `feat(shapes): implement workflow, single, and orchestrator shapes for CP2`: Thay thế stub ban đầu, hiện thực hóa luồng xử lý hoàn tiền an toàn, truyền quote đầy đủ vào host để host xử lý trần bồi thường theo đơn.
  - `e0806e1` — `test(cp3): add resilience, idempotency, and handoff safety tests for student shapes`: Viết 7 unit tests kiểm tra idempotent replay, crash-recovery, và handoff sanitizer.
- **Quyết định kỹ thuật đưa ra:**
  - Tiền bồi thường được tính hoàn toàn bằng code (`compute_compensation`), MockLLM chỉ đóng vai trò hỗ trợ đọc hiểu / soạn thảo chữ.
  - Shape truyền quote đầy đủ vào `durability.issue_refund`, tuyệt đối không tự trừ phần tiền đã hoàn trước đó để tránh trừ 2 lần tại host.
  - Đảm bảo `InjectedCrash` không bị bắt nuốt (swallowed) mà được re-raise sau khi lưu trace, giúp hệ thống kiểm thử bắt đúng điểm sập.
  - Khử toàn bộ `parent_secret` và canaries qua cơ chế allowlist trong `make_handoff` thay vì dựa vào LLM tóm tắt.
- **Test đã thêm:**
  - Thêm file mới `src/tests/test_cp3_resilience.py` với 7 tests:
    - `test_cp3_idempotent_replay_preserves_single_ledger_row` (chạy trên 3 shapes: workflow, single, orchestrator)
    - `test_cp3_crash_recovery_does_not_duplicate_refund` (chạy trên 3 shapes: workflow, single, orchestrator)
    - `test_cp3_handoff_strictly_readonly` (kiểm tra make_handoff loại bỏ write tool và facts nhạy cảm)

## 4. Bằng chứng

- **Commits trên GitHub:**
  - Commit CP2: [9cc25fe](https://github.com/dungpham108/K5-L3A-DAY08-Apollo-FromWorkflowsToAgents/commit/9cc25fe)
  - Commit CP3: [e0806e1](https://github.com/dungpham108/K5-L3A-DAY08-Apollo-FromWorkflowsToAgents/commit/e0806e1)
- **Kết quả kiểm thử:**
  - `python -m pytest -q tests/test_cp3_resilience.py` $\rightarrow$ 7 passed in 0.27s.
  - `python -m pytest -q -m student -o addopts=` $\rightarrow$ 248/248 passed (từ 186 failed ban đầu lên 248 passed).
  - `python -m pytest -q` $\rightarrow$ 61/61 passed (cổng host luôn xanh).
  - `python -m lab8.check_submission` mục `== shapes ==` đạt 100% OK cho cả 3 shapes trên 12/12 claims public ở seed 11.

## 5. Công cụ AI đã dùng

- **Công cụ:** Gemini (Antigravity AI Assistant).
- **Mục đích:** Hỗ trợ rà soát contract v1 của đề bài, phân tích luồng điều hướng của MockLLM và cấu trúc cơ sở dữ liệu SQLite, gợi ý khung triển khai ReAct loop và cấu trúc các test cases cho CP3.
- **Phương pháp tự kiểm tra:**
  - Chạy `python -m pytest -q` để bảo đảm cổng host không bị ảnh hưởng;
  - Chạy toàn bộ ma trận kiểm thử học viên (`pytest -q -m student -o addopts=`) để xác nhận cả 14 tình huống nghiệp vụ T01–T14;
  - Kiểm tra tính idempotent và crash safety qua script mẫu `python -m lab8.demo.buggy_workflow` và `tests/test_crash_suite.py`.

## 6. Tự đánh giá

- Hoàn thành đầy đủ và vượt tiến độ các mốc CP1, CP2, CP3.
- Code tuân thủ nghiêm ngặt chuẩn hợp đồng, không vi phạm các điều kiện must-pass (không lộ secret, không bypass approval, không duplicate ledger row khi crash).
- Mức độ hoàn thành: Hoàn thành xuất sắc (10/10).
