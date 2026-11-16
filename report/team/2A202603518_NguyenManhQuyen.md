# Báo cáo cá nhân — 2A202603518_NguyenManhQuyen

## 1. Thông tin thành viên

- Họ tên: Nguyễn Mạnh Quyền
- MSSV: 2A202603518
- Email: quyenbiak19@gmail.com
- GitHub: https://github.com/manhquyenkma


## 2. Phần việc phụ trách

- **Shape C:** Orchestrator + Handoff (CP2, CP3)
- Cài đặt kiến trúc Orchestrator và điều phối các worker investigators ở chế độ read-only.
- Xây dựng giao thức Handoff an toàn (sanitized context, allowlist tools, ngăn rò rỉ secret/PII).
- Đảm bảo tính toàn vẹn dữ liệu, idempotency và khả năng chịu lỗi (crash safety, 20/20) cho Shape C.
- Viết bộ unit test độc lập cho Shape C (`src/tests/test_orchestrator.py`).

## 3. Đóng góp cụ thể

- **Cài đặt `src/lab8/shapes/orchestrator.py`:**
  - Bước 1-2: Đọc thông tin claim qua view an toàn (chỉ lấy field được phép, không `SELECT *`), chuyển trạng thái `needs_info` khi thiếu `order_id`.
  - Bước 3-4: Đóng gói gói tin chuyển giao an toàn bằng `lab8.handoff.make_handoff` với allowlist công cụ đọc (`lookup_order`, `lookup_policy`, `compute_compensation`). Không chuyển `parent_secret`, `raw_headers` hay PII vào `facts`. Chạy qua `run_readonly_investigators`.
  - Bước 5: Chuyển trạng thái `escalated` khi đơn hàng không thuộc quyền sở hữu của principal hoặc không tìm thấy đơn.
  - Bước 6-7: Tính toán bồi thường hoàn toàn bằng code (`compute_compensation`), MockLLM chỉ dùng để soạn thảo phản hồi, không quyết định số tiền. Quote $\le 0$ chuyển trạng thái `denied`, không gọi `issue_refund`.
  - Bước 8-10: Quote $> 0$ gọi `durability.issue_refund` với full quote để host tự động kiểm tra trần đơn hàng và approval. Chuyển tiếp tham số `crash_at` và không bắt `InjectedCrash` để đảm bảo crash test thực thi chuẩn xác.
  - Tích hợp Trace contract v1 cho mọi nhánh kết quả, trace sanitized handoff thay vì raw parent context.
- **Thêm bộ kiểm thử `src/tests/test_orchestrator.py`:**
  - Viết 18 test cases bao phủ toàn diện:
    - 12 claims public traps (C-001..C-010, C-013, C-014).
    - Kiểm thử tính bền vững với lỗi prompt hallucination tại T02 seed 55 (Orchestrator không bị ảnh hưởng như Swarm).
    - Kiểm thử bảo mật ranh giới: kiểm tra trace và handoff không rò rỉ `CANARY_SECRET_*`, `parent_secret`, `raw_headers`.
    - Kiểm thử các nhánh biên: missing `order_id` (`needs_info`), `outside_principal_scope` (`escalated`), unknown claim (`failed`).
    - Kiểm thử lan truyền `InjectedCrash` và phục hồi idempotent (chạy lại cùng claim không tạo thêm refund).

## 4. Bằng chứng

- **Test Suite Shape C:**
  - `python -m pytest tests/test_orchestrator.py`: **18/18 passed**
  - `python -m pytest -q -m student -o addopts= -k orchestrator`: **62/62 passed**
- **Test Bảo mật Handoff & Host:**
  - `python -m pytest tests/test_handoff_secret.py tests/test_trace_contract.py tests/test_authorization.py`: **12/12 passed**
  - Cổng host `python -m pytest -q`: **72/72 passed**
- **Crash Safety:**
  - `python -m lab8.crash_test --count 20 --out reports/crash.json`: **20/20 safe**
- **Check submission:**
  - `python -m lab8.check_submission`: `[ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`

## 5. Công cụ AI đã dùng

- **Antigravity Assistant (AI Pair Programmer):**
  - Hỗ trợ rà soát ranh giới bảo mật Handoff theo tài liệu `docs/contracts.md` và `docs/business_rules.md`.
  - Hỗ trợ sinh khung test case cho `test_orchestrator.py`.
- **Tự kiểm tra:**
  - Tự chạy toàn bộ test suite cục bộ bằng `pytest`, rà soát các canaries để chắc chắn không có secret nào rò rỉ ra trace hay stdout.

## 6. Tự đánh giá

- Hoàn thành nhiệm vụ C (Orchestrator + Handoff):
  - Đáp ứng toàn bộ 3 điều kiện must-pass: không approval bypass, không lộ secret, crash safety 20/20.
  - Vượt qua 100% các bài test liên quan đến Shape C và Handoff.

