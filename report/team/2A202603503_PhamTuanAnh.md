# Báo cáo cá nhân — 2A202603503_PhamTuanAnh

## 1. Thông tin thành viên

- Họ tên: Phạm Tuấn Anh
- MSSV: 2A202603503
- Email: 26ai.anhpt9@vinuni.edu.vn
- GitHub: phamtuananhhatay

## 2. Phần việc phụ trách

- Phụ trách toàn diện **Shape B — Single Agent (ReAct)** tại `src/lab8/shapes/single.py`.
- Thiết kế vòng lặp ReAct có giới hạn tối đa 8 bước (`max_steps=8`), phân tách rõ ràng quyền đọc của Model và quyền ghi của Host.
- Đảm bảo tính toàn vẹn dữ liệu, idempotency (khóa `refund:{claim_id}`) và cơ chế phục hồi an toàn sau crash (`InjectedCrash`).
- Thiết kế và triển khai bộ unit test chuyên biệt cho shape single tại `src/tests/test_single_student.py`.

## 3. Đóng góp cụ thể

- **Triển khai Shape B (`src/lab8/shapes/single.py`):**
  - Xây dựng vòng lặp ReAct thông qua `lab8.runtime.run_react` với hàm callback `decide(seen)`.
  - Phân luồng công cụ đọc an toàn: `lookup_order` $\rightarrow$ kiểm tra quyền sở hữu đơn hàng (`principal_id`) $\rightarrow$ gọi `compute_compensation`.
  - Khắc phục điểm yếu của Swarm: Luôn trích xuất `delay_days` từ dòng `order` trong DB, kiên quyết bỏ qua số ngày trễ do khách hàng khai man hoặc prompt injection trong `ticket` (giải quyết triệt để case C-002 ở seed 55).
  - Xử lý trần bồi thường theo đơn (Per-order cap): Luôn truyền **quote đầy đủ** vào `durability.issue_refund` để Host tự động trừ các khoản đã bồi thường trước đó (T13, T14).
  - Đảm bảo Crash Safety: Chuyển tiếp tham số `crash_at` và re-raise `InjectedCrash` để harness kiểm tra crash-resume (T12).
- **Bộ Unit Test (`src/tests/test_single_student.py`):**
  - Viết 8 test case kiểm thử: luồng ReAct hoàn phí thành công (C-001), khả năng chống prompt injection trên cả 5 seeds (C-002), tính an toàn bí mật của Trace Contract v1 và các nhánh trả về sớm (`needs_info`, `escalated`).

## 4. Bằng chứng

- **Mã commit kỹ thuật:**
  - `5b65ad8`: `feat(shapes): implement single ReAct agent claim processing workflow`
  - `0ca10b7`: `test(single): add unit tests for single ReAct agent claim handling and trace safety`
- **Kết quả kiểm thử:**
  - Ma trận Student test: `62 passed` / 62 test cho shape `single` trên cả 5 seeds (`11, 22, 33, 44, 55`).
  - Unit test mới: `8 passed in 0.62s` (`src/tests/test_single_student.py`).
  - Cổng host `pytest -q`: `62 passed` (bao gồm các test mới).
- **Trace & Run ID minh chứng:**
  - `R-single-C-001-s11` (status: `resolved`, proposal: 35000, 0 leak).

## 5. Công cụ AI đã dùng

- **Công cụ:** Google Deepmind Antigravity Assistant.
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích cấu trúc contracts và cơ chế tương tác giữa `run_react`, `dispatch` và `issue_refund`.
  - Gợi ý cấu trúc code chuẩn và sinh các kịch bản kiểm thử biên cho unit test.
- **Cách tự kiểm tra và thẩm định kết quả:**
  - Kiểm tra độc lập mã nguồn theo đúng `docs/contracts.md` và `docs/business_rules.md`.
  - Chạy toàn bộ test suites (`pytest -m student -k single`, `pytest tests/test_single_student.py`).
  - Kiểm tra thực tế file trace JSON sinh ra để chắc chắn không chứa `CANARY_SECRET_*` và thông tin cá nhân (PII).

## 6. Tự đánh giá

- Mức độ hoàn thành: **100%**.
- Hoàn thành đúng hạn, đúng kiến trúc quy định, bảo đảm 100% các điều kiện Must-Pass và vượt qua toàn bộ ma trận test case.
