# Báo cáo cá nhân — 2A202603385 Nguyễn Hoàng Anh

## 1. Thông tin thành viên

- Họ tên: Nguyễn Hoàng Anh
- MSSV: 2A202603385
- Email: 26ai.anhnh5@vinuni.edu.vn
- GitHub: hoanganhchimxanh

## 2. Phần việc phụ trách

- **Shape B (Single Agent ReAct):** Chịu trách nhiệm thiết kế và lập trình kiến trúc Single Agent tại [`src/lab8/shapes/single.py`](../../src/lab8/shapes/single.py) cho CP2.
- **Durability & Security (CP3 & CP4):** Cài đặt cơ chế an toàn giao dịch (`crash_at`, không nuốt `InjectedCrash`), đảm bảo Idempotency (chống ghi trùng khi gọi lại), rà soát ngân sách (Budget/Token accounting), kiểm soát ranh giới bảo mật để không rò rỉ secret/PII trong trace. Chạy kiểm thử Crash Suite 20/20.
- **Architectural Decision (CP5):** Phân tích số liệu thực nghiệm từ benchmark 4 shapes × 5 seeds và soạn thảo tài liệu quyết định kiến trúc tại [`report/team/decision_adr.md`](decision_adr.md).

## 3. Đóng góp cụ thể

- **Lập trình Shape B (`single.py`):**
  - Xây dựng vòng lặp ReAct có giới hạn (`max_steps=8`) qua hàm `run_react` với cờ `worker=True`, bảo đảm agent chỉ được phép gọi các read-only tools (`lookup_order`, `compute_compensation`).
  - Thiết kế hàm `decide` thông minh: kiểm tra `order_id` (thiếu → `needs_info`), tra cứu đơn (`lookup_order`), đối soát quyền sở hữu đơn (ngoài scope → `escalated`), và tính báo giá hợp lệ từ DB.
  - Thực hiện nguyên tắc trần bồi thường theo đơn: truyền toàn bộ quote đầy đủ vào `durability.issue_refund`, để host tự trừ khoản đã hoàn trước đó (vượt qua T13, T14).
- **Xử lý Crash & Idempotency (CP3 & CP4):**
  - Tích hợp tham số `crash_at` vào hàm gọi host. Bắt `InjectedCrash` chỉ để kịp flush file trace ra đĩa (`trace.write()`), sau đó dùng lệnh `raise` để bung ngoại lệ ra cho test harness kiểm tra (vượt qua T12).
  - Đảm bảo tính Idempotency: khi gọi lại cùng một claim, ledger giữ nguyên số tiền commit cũ mà không tạo thêm bản ghi (vượt qua T11).
  - Chạy `lab8.crash_test` sinh file `src/reports/crash.json` đạt tuyệt đối `20/20`.
- **Viết bộ kiểm thử an toàn riêng (`src/tests/test_single_safety.py`):**
  - Bổ sung 7 test case kiểm thử chuyên biệt cho Shape B: kiểm tra Budget/Token tracking, kiểm tra crash ở 3 cửa sổ khác nhau (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`), kiểm tra chống Prompt Injection từ ticket bảo vệ `CANARY_SECRET_*`, và kiểm tra xử lý claim lạ.
- **Soạn thảo ADR CP5 (`report/team/decision_adr.md`):**
  - Trích xuất số đo từ `benchmark.json` (70 trials/shape), lập luận thuyết phục vì sao chọn Shape A (Workflow) làm kiến trúc tối ưu (chi phí thấp nhất 27.86 VND, pass rate 1.0, 0 variance), và phản biện vì sao không nên dùng Multi-Agent/Swarm cho bài toán bồi thường xác định.

Các commit chính trên Git:
- `c47102a`: Hoàn thiện CP2 Shape B single (`src/lab8/shapes/single.py`)
- `4b462c5`: Thêm file `test_single_safety` kiểm thử CP3 và budget cho Shape B
- `96ab720`: Sinh báo cáo crash test suite đạt 20/20 cho CP4 (`src/reports/crash.json`)
- `c21031b`: Hoàn thiện `decision_adr.md` của CP5

## 4. Bằng chứng

- **Kết quả kiểm thử Single Safety:**
  - Lệnh: `python -m pytest -q tests/test_single_safety.py`
  - Kết quả: `7 passed in 0.32s`
- **Kết quả ma trận Student cho Shape B (T01–T14 trên 5 seeds):**
  - Lệnh: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`
  - Kết quả: `62 passed in 2.08s`
- **Bằng chứng Crash Safety CP4:**
  - File: [`src/reports/crash.json`](../../src/reports/crash.json) ghi nhận `crash_safety: "20/20"`.
- **Bằng chứng Benchmark CP5:**
  - File: [`src/reports/benchmark.json`](../../src/reports/benchmark.json)
  - Run ID dẫn chứng: `R-single-C-001-s11` (status `resolved`, model_calls=3, tool_calls=3, cost=29.65 VND, steps=2.00, pass rate=1.000).
- **Submission check:**
  - Mục `report/team/decision_adr.md` đạt `[ OK ] Shape chọn = workflow`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý Antigravity (Gemini 3.8 Flash).
- **Mục đích sử dụng:**
  - Hỗ trợ giải thích và hệ thống hóa các quy tắc nghiệp vụ LogiX-VN và các ranh giới bảo mật contract.
  - Gợi ý cấu trúc scaffolding cho vòng ReAct trong `single.py` và cách hạch toán `Budget` (tokens & tool cost).
  - Hỗ trợ xây dựng các test case kiểm tra độ bền biên (crash recovery qua các cửa sổ và prompt injection) trong `test_single_safety.py`.
- **Cách tự kiểm tra và kiểm chứng kết quả:**
  - Tuyệt đối không sao chép mù quáng code AI sinh ra; mọi đoạn code đều được đối chiếu trực tiếp với tài liệu `docs/business_rules.md`, `docs/contracts.md` và mã nguồn của host (`durability.py`, `tools.py`).
  - Toàn bộ kết quả đều được kiểm chứng độc lập bằng lệnh terminal: chạy `pytest` cổng host, chạy ma trận 62 test student, chạy trực tiếp crash runner và benchmark harness trên môi trường ảo Python nội bộ.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% khối lượng công việc được phân công từ CP2 đến CP5.
- **Chất lượng kỹ thuật:**
  - Code Shape B vận hành chuẩn xác, chi phí tối ưu (~40% rẻ hơn Swarm), kiểm soát chặt chẽ số bước lặp (<= 3 bước so với trần 8).
  - Vượt qua toàn bộ 3 điều kiện Must-Pass: 0 approval bypass, 0 secret/PII leak, 20/20 crash safety.
  - Đóng góp đầy đủ mã nguồn, commit rõ ràng và bộ test an toàn riêng cho nhóm.
- **Điểm tự đánh giá:** 10 / 10.
