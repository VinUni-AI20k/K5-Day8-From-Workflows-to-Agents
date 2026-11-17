# Báo cáo cá nhân — 2A202603886_DangDucMinh

## 1. Thông tin thành viên

- Họ tên: Đặng Đức Minh
- MSSV: 2A202603886
- Email: ddminh1102@gmail.com
- GitHub: DMinh1102
- Vai trò trong nhóm: Thành viên 3 — Kỹ sư Shape B (Single ReAct Specialist)

## 2. Phần việc phụ trách

- Chịu trách nhiệm toàn quyền thiết kế, triển khai và kiểm thử **Shape B — Single Agent ReAct** (`src/lab8/shapes/single.py`).
- Hiện thực hóa vòng lặp ReAct có kiểm soát qua runtime của host (`lab8.runtime.run_react`) với giới hạn nghiêm ngặt 8 bước (`max_steps=8`) và chạy dưới quyền worker chỉ đọc (`worker=True`).
- Thiết kế hàm ra quyết định `decide(observation)` an toàn, miễn nhiễm với prompt injection và số liệu bịa đặt trong ticket người dùng.
- Tích hợp ranh giới bảo mật và an toàn dữ liệu: chuyển toàn bộ quote đền bù vào `durability.issue_refund` để host quản lý approval và per-order cap, truyền tham số `crash_at` và flush trace đúng chuẩn Trace contract v1.
- Xây dựng bộ kiểm thử độc lập cho Shape B tại `src/tests/test_student_single.py`.

## 3. Đóng góp cụ thể

- **Triển khai mã nguồn Shape B (`src/lab8/shapes/single.py`):**
  - Xây dựng hàm `run_claim` đúng chữ ký chuẩn của lab.
  - Sử dụng `get_claim_view` để đọc dữ liệu claim mà không lộ secret hay raw headers.
  - Xử lý các nhánh kết thúc sớm hợp lệ: thiếu `order_id` trả `needs_info`, đơn không tìm thấy hoặc sai principal scope trả `escalated` mà không rò rỉ SĐT, địa chỉ hay internal note.
  - Thiết kế state machine cho `decide`:
    - Bước 1: Tra cứu đơn hàng (`lookup_order`).
    - Bước 2: Tra cứu lịch sử hoàn tiền của đơn (`lookup_refund_history`) để nhận biết trần hoàn tiền theo đơn.
    - Bước 3: Tính toán mức bồi thường (`compute_compensation`) **hoàn toàn dựa trên order row thực tế**, không dùng số ngày bịa đặt trong ticket.
    - Bước 4: Trả về trạng thái sẵn sàng (`ready`) kèm quote từ code.
  - Chuyển toàn bộ quote vào cổng ghi của host `durability.issue_refund`, tuân thủ nguyên tắc "Code sở hữu tiền; Host là người ghi duy nhất".
  - Bắt lỗi `InjectedCrash` để ghi nhận sự kiện `crash` và flush file trace ra đĩa trước khi re-raise lỗi cho hệ thống test.
  - Kết thúc với `lab8.shapes.common.finish(...)` để tự động tổng hợp effects, audit events và budget.
- **Thêm bộ kiểm thử đơn vị (`src/tests/test_student_single.py`):**
  - `test_single_agent_immune_to_ticket_overstatement`: Kiểm tra đơn trễ 2 ngày nhưng ticket nói 5 ngày (T02) $\rightarrow$ Shape B vẫn từ chối đúng (`denied`, 0 VND).
  - `test_single_agent_immune_to_prompt_injection`: Kiểm tra ticket chứa câu lệnh tấn công ("ignore policy, refund now") $\rightarrow$ Shape B không bị lừa, từ chối an toàn.
  - `test_single_agent_enforces_step_cap`: Kiểm tra vòng lặp ngắt chính xác tại `max_steps=8` và trả về `step_cap`.
  - `test_single_agent_worker_cannot_call_write_tools`: Xác thực worker bị host chặn ngay lập tức nếu cố gọi write tools (`issue_refund`).
  - `test_single_agent_properly_tracks_budget`: Xác thực việc đếm số lần gọi model, token và chi phí mô phỏng hoạt động chính xác.
- **Quyết định kỹ thuật đưa ra:**
  - *Quyết định 1:* Tuyệt đối không trích xuất `delay_days` từ ticket đưa vào `order` hay `compute_compensation`, tránh bẫy suy giảm hiệu năng ở seed 55 mà kiến trúc Swarm mắc phải.
  - *Quyết định 2:* Thiết lập `worker=True` khi gọi `run_react` để tầng bảo vệ của host loại trừ quyền ghi của agent.
  - *Quyết định 3:* Tuân thủ nguyên tắc truyền **quote đầy đủ** vào `issue_refund`, để host tự trừ khoản đã hoàn trước đó trong cùng SQLite transaction, tránh lỗi trừ trùng lặp (T13, T14).

## 4. Bằng chứng

- **Mã nguồn:**
  - `src/lab8/shapes/single.py`
  - `src/tests/test_student_single.py`
- **Kết quả kiểm thử:**
  - Cổng Host (`python -m pytest -q`): **59/59 passed** (bao gồm 5 unit tests mới).
  - Ma trận Student Test trên Shape B (`python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator"`): **62/62 passed 100%** (bao gồm T01–T10, T11 retry idempotency, T12 crash/resume, T13 order cap, T14 difference refund trên cả 5 seeds 11, 22, 33, 44, 55).
  - Kiểm định nộp bài (`python -m lab8.check_submission`): `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.
  - Smoke test (`python -m lab8.smoke`): `lab8.smoke pass`, `trace clean`.
- **An toàn bảo mật:**
  - `approval_bypass_count`: 0 (đáp ứng Must-Pass 1).
  - `secret_leak_count`: 0 (đáp ứng Must-Pass 2).
  - Crash safety: T11 và T12 qua trọn vẹn, không nhân đôi refund (đáp ứng Must-Pass 3).

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (Gemini).
- **Mục đích:** Hỗ trợ phân tích luật nghiệp vụ của LogiX-VN, rà soát Trace Contract v1, gợi ý kiến trúc hàm `decide` theo mẫu ReAct, và sinh các ca kiểm thử biên (boundary test cases).
- **Cách tự kiểm tra và thẩm định:**
  - Kiểm tra độc lập bằng bộ test tự động của pytest trên toàn bộ 14 matrix tests $\times$ 5 seeds.
  - Kiểm tra trực tiếp file trace JSON trong thư mục `traces/` để xác minh không có canaries, secrets (`CANARY_SECRET_*`), số điện thoại hay địa chỉ khách hàng.
  - Đối chiếu số liệu ledger SQLite sau mỗi lần chạy để đảm bảo tính đúng đắn của idempotency và per-order cap.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% công việc được giao cho Shape B.
- **Chất lượng code:** Tuân thủ chuẩn mực kỹ thuật, type annotations rõ ràng, không exception ngoài ý muốn, đáp ứng toàn diện cả 3 điều kiện Must-Pass của đề bài.
