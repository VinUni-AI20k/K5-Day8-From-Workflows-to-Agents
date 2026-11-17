# Báo cáo cá nhân — 2A202603746_NguyenVanHieu

## 1. Thông tin thành viên

- Họ tên: Nguyễn Văn Hiếu
- MSSV: 2A202603746
- Email: 26ai.hieunv3@vinuni.edu.vn
- GitHub: lunaHieu

## 2. Phần việc phụ trách

- **Kiến trúc đảm nhiệm:** Shape B — Single ReAct Agent (`src/lab8/shapes/single.py`).
- **Nhiệm vụ chính:**
  - Triển khai vòng lặp ReAct bằng `lab8.runtime.run_react` với trần tối đa 8 bước (`max_steps=8`).
  - Thiết lập ranh giới an toàn tuyệt đối: Model chỉ được gọi các công cụ đọc (`get_claim_view`, `lookup_order`, `compute_compensation`); lệnh ghi tiền `durability.issue_refund` do Code Python thực thi sau khi kết thúc ReAct.
  - Chống prompt injection từ ticket người dùng (không bóc tách số ngày trong ticket, lấy trực tiếp từ database).
  - Tuân thủ hợp đồng trần theo đơn (T13, T14): truyền quote đầy đủ để Host tự trừ tiền đã hoàn.
  - Đảm bảo độ bền khi crash: truyền `crash_at` và không bắt ngoại lệ `InjectedCrash`.
  - Xây dựng bộ test kiểm chứng độc lập cho Single Shape (`src/tests/test_single_agent.py`).

## 3. Đóng góp cụ thể

- **Code lõi (`src/lab8/shapes/single.py`):**
  - Xây dựng hàm `_make_decide` điều phối 4 bước ReAct chuẩn: `get_claim_view` $\rightarrow$ `lookup_order` $\rightarrow$ `compute_compensation` $\rightarrow$ `final` (hoàn thành trong 4 bước, nằm an toàn trong giới hạn 8 bước).
  - Xử lý các nhánh thoát sớm đúng hợp đồng: `unknown_claim` (`failed`), `missing_order_id` (`needs_info`), đơn không tìm thấy / không sở hữu (`escalated`), quote $\le 0$ (`denied`).
  - Tách bạch vai trò: Khi ReAct trả về `ready_to_refund`, code Python đứng ngoài gọi `durability.issue_refund(conn, claim_id, proposal_amount, crash_at=crash_at)`.
  - Luôn truyền `proposal_amount` là quote đầy đủ (full quote), để Host ghi nhận audit `policy_denied` khi quote > 0 bị từ chối.
  - Sử dụng `finish()` để ghi trace chuẩn và trả về `RunResult` đồng nhất.
- **Bộ kiểm thử kỹ thuật (`src/tests/test_single_agent.py`):**
  - Viết 6 test case kiểm tra:
    1. `test_single_agent_ignores_ticket_prompt_injection`: Khắc phục lỗi của Swarm ở seed 55 trên claim C-002.
    2. `test_single_agent_react_step_cap`: Khống chế số bước model/tool $\le 8$.
    3. `test_single_agent_full_quote_on_t13_and_t14`: Bảo toàn proposal quote đầy đủ trên T13 và T14.
    4. `test_single_agent_expired_approval_denied`: Chặn approval hết hạn (C-007) và ghi audit `policy_denied`.
    5. `test_single_agent_mismatched_approval_rejected`: Chặn approval cấp cho claim khác (`approval_claim_mismatch`).
    6. `test_single_agent_retry_and_crash_durability`: Lan truyền `InjectedCrash` và kiểm tra idempotent replay.

## 4. Bằng chứng

- **Commit kỹ thuật chính:** `451c154` (`feat(single): implement Shape B Single ReAct agent and unit test suite`).
- **Kết quả chạy test matrix student cho Shape Single:**
  - Lệnh: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`
  - Kết quả: **62 passed**, 246 deselected in 1.64s.
- **Kết quả chạy bộ test cá nhân:**
  - Lệnh: `python -m pytest -q tests/test_single_agent.py`
  - Kết quả: **6 passed** in 0.24s.
- **Kết quả cổng Host an toàn:**
  - Lệnh: `python -m pytest -q`
  - Kết quả: **60 passed** in 2.29s (không làm vỡ test của host).
- **Kết quả crash test suite:**
  - Lệnh: `python -m lab8.crash_test --count 20 --out reports/crash.json`
  - Kết quả: `crash_safety 20/20` (đạt trọn vẹn Must-pass số 3).
- **Rà soát rò rỉ bảo mật (Trace Contract v1):**
  - Đã quét 63 file trace sinh ra bởi `single`: **0 secret leak** (`CANARY_SECRET_*`), **0 PII leak** (đạt Must-pass số 2).

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity AI Assistant.
- **Mục đích sử dụng:**
  - Hỗ trợ giải thích và rà soát các hợp đồng dữ liệu (`docs/contracts.md`, `docs/business_rules.md`).
  - Đề xuất cấu trúc bộ test unit độc lập trong `tests/test_single_agent.py`.
- **Cách tự kiểm chứng kết quả:**
  - Tự chạy toàn bộ các lệnh pytest trong môi trường ảo `src/.venv` trên máy cục bộ.
  - Tự kiểm tra các file trace JSON sinh ra trong `traces/` để xác thực không có rò rỉ secret hoặc PII.
  - Chạy `check_submission` để đối chiếu định dạng bài nộp.

## 6. Tự đánh giá

- Hoàn thành đầy đủ 100% các tiêu chí kỹ thuật và quy định bàn giao cho vai trò Thành viên 2 (Single ReAct Agent).
- Mã nguồn sạch sẽ, tuân thủ nghiêm ngặt ranh giới an toàn Code / Model và các điều kiện Must-pass của đề bài.
