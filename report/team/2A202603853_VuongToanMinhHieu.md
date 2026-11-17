# Báo cáo cá nhân — 2A202603853_VuongToanMinhHieu

## 1. Thông tin thành viên

- Họ tên: Vương Toàn Minh Hiếu
- MSSV: 2A202603853
- Email: hieutrung142005@gmail.com | 26ai.hieuvtm@vinuni.edu.vn
- GitHub: [@HieuVuong145](https://github.com/HieuVuong145)

## 2. Phần việc phụ trách

Xây dựng và triển khai **Shape B (Single ReAct Agent)** cho Checkpoint 2 và Checkpoint 3 trong [`src/lab8/shapes/single.py`](../../src/lab8/shapes/single.py).

- **CP2:** Triển khai vòng lặp ReAct Agent với `max_steps=8` thông qua runtime `lab8.runtime.run_react`. Xử lý hàm `decide` tương tác với các read tools (`lookup_order`, `compute_compensation`) và phân loại các trạng thái kết thúc nghiệp vụ (`needs_info`, `escalated`, `denied`, `resolved`).
- **CP3:** Đảm bảo tính durability, chống idempotency, xử lý chuyển tiếp crash (`crash_at`) tới `durability.issue_refund` mà không nuốt ngoại lệ `InjectedCrash`, và ghi nhận Trace an toàn.
- **Unit Tests:** Xây dựng test [`src/tests/test_shape_single.py`](../../src/tests/test_shape_single.py) để kiểm tra các kịch bản của Shape B (resolved, denied, missing order_id, escalated, crash forwarding).

## 3. Đóng góp cụ thể

- **Xây dựng kiến trúc ReAct Agent độc lập** trong `src/lab8/shapes/single.py`, tuân thủ đúng chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.
- **Thiết lập ranh giới Code vs Model:**
  - Hàm `decide` của Agent chỉ được phép chọn các công cụ chỉ đọc (`lookup_order`, `compute_compensation`).
  - Tuyệt đối không cho phép Model gọi tool ghi hay tự ý đưa ra số tiền bồi thường. Toàn bộ tiền bồi thường do code Python tính toán thông qua `compute_compensation`.
  - Host là bên duy nhất thực hiện việc kiểm duyệt điều kiện và ghi dữ liệu hoàn tiền vào SQLite ledger.
- **Chống Prompt Injection / Hallucination:** Agent không tin vào câu chữ của khách hàng trong ticket (ví dụ khách nói *"trễ 9 ngày"*), mà luôn dựa trên sự thật khách quan từ bảng đơn hàng trong cơ sở dữ liệu (`order["delay_days"]`), giúp Shape B không bị mắc lỗi dao động (seed variance) như Swarm ở seed 55.
- **Tuân thủ trần bồi thường theo đơn (Order Cap - T13, T14):** Luôn truyền **quote đầy đủ** vào `durability.issue_refund` để Host tự động đối trừ các khoản bồi thường đã nhận trước đó của đơn hàng, không tự ý trừ trước.
- **Xử lý Crash & Idempotency (CP3):**
  - Truyền tham số `crash_at` trực tiếp vào `durability.issue_refund`.
  - Khi gặp `InjectedCrash`, ghi nhận sự kiện crash vào Trace và re-raise ngoại lệ để hệ thống kiểm thử bắt được. Lần chạy lại (resume) sau đó nhờ có ledger idempotency key `refund:{claim_id}` nên chỉ sinh đúng 1 dòng refund duy nhất (vượt qua T11 và T12).
- **Trace an toàn (Trace Contract v1):** Ghi nhận đầy đủ tiến trình ReAct qua `Trace` với `run_id` khớp với `RunResult`. Chỉ ghi các trường thuộc allowlist (`get_claim_view`, `lookup_order`), tuyệt đối không ghi dữ liệu nhạy cảm (`parent_secret`, số điện thoại, địa chỉ, internal note).
- **Xây dựng bộ test riêng:** Thêm file [`src/tests/test_shape_single.py`](../../src/tests/test_shape_single.py) gồm 5 bài test bao quát các trường hợp biên của Shape B (hợp lệ, quote=0, thiếu order_id, order không thuộc sở hữu, và chuyển tiếp crash).
- **Commit kỹ thuật chính:** Commit `b872bb2` (`shape-b: implement single react agent`) trên nhánh `main`.

## 4. Bằng chứng

- **Bộ unit test riêng của Shape B:**
  ```bash
  python -m pytest -q tests/test_shape_single.py
  ```
**5/5 passed** trong 0.07s.
- **Kết quả chạy ma trận test học viên cho Shape B:**
  ```bash
  python -m pytest -q -m student -o addopts= -k "single and not orchestrator and not workflow and not swarm"
  ```
**62/62 passed**, bao gồm:
  - 60 test cases trên 12 claims public (C-001 đến C-010, C-013, C-014) qua 5 seeds (11, 22, 33, 44, 55).
  - Test T11: `test_t11_retry_keeps_one_refund[single]` (Idempotency khi chạy lại).
  - Test T12: `test_t12_crash_before_checkpoint_does_not_double_pay[single]` (Crash recovery an toàn).
- **Kiểm tra tính hợp lệ bài nộp qua `check_submission`:**
  ```bash
  python -m lab8.check_submission
  ```
  `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.
- **Trace kiểm duyệt an toàn:** Không xuất hiện bất kỳ cảnh báo rò rỉ nào (`secret_leak_count = 0`, `pii_leak_count = 0`).

## 5. Công cụ AI đã dùng

- **Công cụ:** Google DeepMind / Antigravity AI Assistant.
- **Mục đích sử dụng:**
  - Hỗ trợ giải thích và bám sát các ràng buộc nghiệp vụ trong `docs/business_rules.md` và `docs/contracts.md`.
  - Hỗ trợ phân tích cấu trúc runtime `run_react` và thiết kế hàm `decide` sao cho vừa tối ưu số bước (không vượt quá 8 bước) vừa giữ vững ranh giới an toàn của Host.
- **Phương pháp tự kiểm tra (Verification):**
  - Không tin tưởng kết quả sinh tự động nếu chưa qua kiểm chứng bằng test.
  - Tự tay chạy kiểm thử trên môi trường ảo Python nội bộ (`pytest`), kiểm tra từng mã lỗi trả về của từng claim public, và chạy script kiểm định `check_submission`.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** Hoàn thành đầy đủ yêu cầu Shape B, pass 62/62 test student.
- **Ranh giới trách nhiệm:** Hoàn thành lõi `src/lab8/shapes/single.py`; kịch bản test.
- **Điểm tự đánh giá đề xuất:** Đạt điểm cao cho Shape B.
