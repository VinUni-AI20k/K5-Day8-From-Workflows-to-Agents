# Báo cáo cá nhân — 2A202603382_ChuVanHiep

## 1. Thông tin thành viên

- Họ tên: Chử Văn Hiệp
- MSSV: 2A202603382
- Email: 26ai.hiepcv@vinuni.edu.vn
- GitHub: hiepchuvanpc

## 2. Phần việc phụ trách

- **Vai trò:** `orchestrator + handoff` (Kiến trúc Shape C & Cơ chế chuyển giao an toàn).
- **Phạm vi trách nhiệm chính:**
  - Viết logic cho Shape C tại file `src/lab8/shapes/orchestrator.py` tuân thủ output contract `RunResult` và trace contract v1.
  - Phụ trách cơ chế bảo mật chuyển giao dữ liệu (`handoff`): thiết lập allowlist, đảm bảo cách ly tuyệt đối giữa Orchestrator và Investigator, ngăn chặn rò rỉ bí mật (`CANARY_SECRET_*`) và PII.
  - Xử lý cơ chế an toàn khi gặp sự cố (Durability & Crash resilience) tại CP3 cho Orchestrator.
  - Viết bổ sung unit test kiểm thử ranh giới bảo mật của handoff trong `src/tests/test_handoff_secret.py`.

## 3. Đóng góp cụ thể

1. **Shape C (`src/lab8/shapes/orchestrator.py`):**
   - Thiết lập quy trình phân cấp: Orchestrator đóng vai trò lập kế hoạch, điều phối các `read-only investigators` thực thi việc tra cứu dữ liệu (`lookup_order`, `lookup_policy`, `compute_compensation`).
   - Loại bỏ hoàn toàn điểm yếu cố ý của Swarm (`REFERENCE_WEAKNESS`): Orchestrator luôn lấy dữ liệu sự thật từ database, không bao giờ tin cậy số ngày trễ ghi trong ticket người dùng, giúp loại bỏ dao động vô lý (variance).
   - Đảm bảo nguyên tắc trần theo đơn: Truyền quote đầy đủ vào `durability.issue_refund` để Host tự động trừ phần đã hoàn trước đó, không tự trừ trước ở tầng agent.

2. **Handoff & Bảo mật thông tin:**
   - Sử dụng `make_handoff`: chỉ cấp quyền cho 3 công cụ đọc, tuyệt đối không cấp quyền cho write tool (`issue_refund`).
   - Đảm bảo ranh giới dữ liệu sạch: Chỉ chuyển giao các trường trong `FACT_KEYS`, loại bỏ hoàn toàn `parent_secret`, headers, context thô trước khi chuyển giao cho worker.
   - Ghi nhận handoff vào trace bằng `safe_dump(handoff)` đã qua sanitization để vượt qua scanner bảo mật của grader.

3. **Durability & Crash Safety (CP3):**
   - Chuyển tiếp tham số `crash_at` vào `durability.issue_refund`.
   - Bắt ngoại lệ `InjectedCrash` chỉ để kịp thời ghi và flush trace ra đĩa, sau đó re-raise ngoại lệ ra ngoài để hệ thống crash test ghi nhận, đáp ứng tiêu chuẩn an toàn idempotency và crash resilience.

4. **Unit Test:**
   - Bổ sung hàm kiểm thử `test_orchestrator_handoff_blocks_write_tools_and_unauthorized_facts` trong `src/tests/test_handoff_secret.py` nhằm xác thực việc từ chối các write tools và tự động loại bỏ các facts nằm ngoài allowlist.

## 4. Bằng chứng

- **Commit hash:** `a204a46`.
- **Test đã thêm:** `test_orchestrator_handoff_blocks_write_tools_and_unauthorized_facts` trong file `src/tests/test_handoff_secret.py`.
- **Kết quả kiểm thử thực tế (chạy trong thư mục `src/`):**
  - Lệnh: `python -m pytest -q -m student -o addopts= -k orchestrator`
  - Kết quả: **62 passed**
  - Lệnh: `python -m pytest -q tests/test_handoff_secret.py` Pass toàn bộ các test kiểm tra rò rỉ secret và phân quyền handoff.
  - Bộ chỉ số an toàn cá nhân phụ trách: `secret_leak_count = 0`, `approval_bypass_count = 0`.

## 5. Công cụ AI đã dùng

- **Công cụ:** ChatGPT.
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích luồng dữ liệu giữa Orchestrator và `run_readonly_investigators`.
  - Đối soát các yêu cầu bắt buộc của hợp đồng `RunResult` và `Trace contract v1`.
  - Hỗ trợ phát hiện lỗi import sai path module (`from src.lab8...` thành import chuẩn `from lab8...`).
  - Gợi ý cấu trúc viết unit test cho handoff allowlist.
- **Cách tự kiểm tra kết quả:**
  - Đọc tài liệu nghiệp vụ `docs/business_rules.md` và hợp đồng `docs/contracts.md` đối chiếu từng nhánh rẽ (denied, needs_info, escalated, resolved, failed).
  - Trực tiếp chạy test trên máy cá nhân thông qua `pytest` ở nhiều mức seed (`11, 22, 33, 44, 55`).
  - Kiểm tra các file trace JSON được sinh ra trong thư mục `traces/` xem có bị lọt `CANARY_SECRET_*`, số điện thoại, địa chỉ hay thông tin PII nào không.

## 6. Tự đánh giá

- Cá nhân: Hoàn thành vai trò `orchestrator + handoff`.
- Nhóm: Phối hợp cùng bạn phụ trách `ledger + evaluation` và `workflow` để đối chiếu số liệu benchmark giữa Shape A và Shape C, làm rõ sự đánh đổi giữa chi phí/độ phức tạp của Orchestrator so với tính tất định của Workflow trong việc hoàn thiện `decision_adr.md`.