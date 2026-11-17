# Báo cáo cá nhân — Tăng Nguyễn Hải Đăng — 2A202603916

## 1. Thông tin thành viên

- Họ tên: Tăng Nguyễn Hải Đăng
- MSSV: 2A202603916
- Email: haidangg.work@gmail.com
- GitHub: https://github.com/haidangwork1411

## 2. Phần việc phụ trách

Vai trò: **Thành viên 4 — Safety & Testing**

Phạm vi phụ trách:
- **CP1 — Setup & Baseline:** Khởi tạo môi trường ảo Python 3.12 (`src/.venv`), cài đặt dependencies đúng theo repo, chạy smoke test và lấy baseline ban đầu (54 host passed, ma trận student ban đầu 186 failed do 3 shape chưa code, 62 swarm passed).
- **Phát triển Test An toàn Độc lập (Safety Invariant):** Bổ sung **1 test an toàn độc lập** tại ranh giới host/policy (`src/tests/test_safety_approval_invariant.py`) kiểm tra invariant: Khi approval bị rejected, cổng host từ chối và không ghi nhận refund vào ledger.
- **Audit An toàn các Nhánh Thành viên:** Thực hiện audit cô lập bằng `git worktree` tạm ngoài repo cho các nhánh đồng đội (`origin/Workflow_CP2,3`, `origin/feature/orchestrator`, `origin/nguyenquanghuy`) trước khi merge, rà soát secret/PII, hợp đồng `RunResult`, xử lý crash/retry và điều kiện nộp bài.
- **Tích hợp & Kiểm thử Toàn diện Hệ thống:** Sau khi các PR của Workflow, Orchestrator và Single được merge vào `origin/main`, thực hiện đồng bộ tích hợp vào nhánh kiểm thử và chạy kiểm thử hồi quy cho cả 4 shape, cổng host và crash suite 20/20.

## 3. Đóng góp cụ thể

### A. Test trực tiếp viết và đóng góp (1 test)
- **Commit kỹ thuật:** `733745de580667e3bed07506a5532c46d100363b` — `test(safety): add approval invariant enforcement test`.
- **File triển khai:** [`src/tests/test_safety_approval_invariant.py`](../../src/tests/test_safety_approval_invariant.py).
- **Hành vi kiểm thử:**
  - Tạo claim `C-TEST-REJECTED` trỏ vào đơn `O-107` (giao trễ 4 ngày, đủ điều kiện hoàn 35.000 VND phí ship, chính chủ `P-100`).
  - Gán approval `A-TEST-REJECTED` có trạng thái bị từ chối (`status = 'rejected'`).
  - Khi gọi `durability.issue_refund`, test kiểm tra 5 điều kiện:
    1. Cổng host từ chối: `outcome["ok"] is False`, `reason == "approval_rejected"`, `effect is None`.
    2. Không ghi refund: `get_refund(conn, claim_id) is None`.
    3. Số dòng ledger giữ nguyên: `ledger_count_after == ledger_count_before`.
    4. Không ghi nhận audit thành công: `committed_audit_count(conn, claim_id) == 0`.
    5. Ghi nhận đúng audit từ chối chính sách: Sự kiện `policy_denied` với chi tiết lý do `"approval_rejected"`.

### B. Audit Độc lập các Nhánh Đồng đội (qua git worktree tạm)
- **Nhánh `origin/Workflow_CP2,3` (Nguyễn Đức Minh - Shape A):** Chạy trong worktree tạm, xác nhận đạt 62 student test workflow, 54 host test và 3 test riêng của Minh (`src/tests/test_workflow.py`).
- **Nhánh `origin/feature/orchestrator` (Nguyễn Nghiêm Khánh Tiệp - Shape C):** Kiểm tra handoff và 16 test riêng của Tiệp (`src/tests/test_orchestrator_own.py`), xác nhận không leak secret/PII, đạt 62 student test orchestrator và 20/20 crash suite.
- **Nhánh `origin/nguyenquanghuy` (Nguyễn Quang Huy - Shape B):** Audit lần 1 phát hiện thiếu test riêng và tài liệu; sau khi tác giả cập nhật bản `cabceb8`, audit lại xác nhận đạt 62 student test single và 8 test riêng của Huy (`src/tests/test_single.py`).

### C. Tích hợp Hệ thống
- Đồng bộ `origin/main` vào nhánh `feat/dang-safety-testing` (merge commit `07202ef`, clean merge).
- Phần code nghiệp vụ của các shape do các thành viên tương ứng phụ trách; tôi không sửa code nghiệp vụ của các shape.

## 4. Bằng chứng Thực nghiệm

Toàn bộ các lệnh kiểm thử dưới đây được chạy trực tiếp từ thư mục `src/` trên nhánh `feat/dang-safety-testing` với môi trường ảo `.venv` (Python 3.12.3):

| Phân loại kiểm thử | Thành phần / Tác giả | Lệnh thực thi | Kết quả thực tế |
| --- | --- | --- | --- |
| **Smoke test** | Starter | `python -m lab8.smoke` | **lab8.smoke pass** |
| **Test Safety riêng** | **Tăng Nguyễn Hải Đăng trực tiếp viết** | `python -m pytest tests/test_safety_approval_invariant.py -v` | **1 passed in 0.06s** |
| **Toàn bộ cổng host** | 54 starter + 16 Orchestrator + 8 Single + 1 Safety | `python -m pytest -q` | **79 passed, 251 deselected in 2.76s** |
| **Ma trận Student cả 4 shape** | 248 ma trận public + 3 test Workflow | `python -m pytest -q -m student -o addopts=` | **251 passed, 79 deselected in 7.79s** |
| • *Shape A (Workflow)* | Nguyễn Đức Minh triển khai | `python -m pytest -q -m student -o addopts= -k workflow` | **65 passed** (62 ma trận + 3 test riêng) |
| • *Shape B (Single)* | Nguyễn Quang Huy triển khai | `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` | **62 passed** |
| • *Shape C (Orchestrator)* | Nguyễn Nghiêm Khánh Tiệp triển khai | `python -m pytest -q -m student -o addopts= -k orchestrator` | **62 passed** |
| • *Shape D (Swarm)* | Shape tham chiếu starter | `python -m pytest -q -m student -o addopts= -k swarm` | **62 passed** (gồm điểm yếu seed 55) |
| **Crash test suite** | Suite kiểm thử host & crash | `python -m lab8.crash_test --count 20 --out reports/crash.json` | **crash_safety 20/20** |


**Giới hạn xác minh thực tế:**
- Các kết quả trên được kiểm chứng trên bộ fixture public (14 claim T01–T14 × 5 seed).
- Chưa kiểm tra trên bộ hidden (CP5) và chưa chạy benchmark CP5 (đây là nhiệm vụ đánh giá chung của cả nhóm).

## 5. Công cụ AI đã dùng

- **Công cụ:** Google Antigravity.
- **Mục đích sử dụng:**
  - Hỗ trợ tra cứu nhanh cấu trúc schema SQLite (`src/lab8/db.py`) và luồng kiểm tra quyền tại `src/lab8/policy.py`.
  - Gợi ý cấu trúc test biên cho trường hợp approval có trạng thái `rejected`.
- **Phương pháp tự kiểm tra và kiểm chứng:**
  - Đọc trực tiếp `docs/business_rules.md` (mục "Không có approval, approval hết hạn, bị thu hồi...") và `docs/contracts.md`.
  - Chạy test thực tế trên SQLite database qua pytest và viết query SQL kiểm tra trực tiếp bảng `refund_ledger` và `audit_events`.
  - Sử dụng `git worktree` cách ly ngoài repo để kiểm chứng output thực tế của từng nhánh, không dựa vào suy đoán.

## 6. Tự đánh giá

**Phần làm tốt:**
- Bổ sung được test chặn approval rejected ở ranh giới host, xác nhận tính bất biến của cổng duyệt host.
- Quy trình audit độc lập qua worktree giúp phát hiện sớm thiếu sót về deliverable trước khi tích hợp vào nhánh chính.
- Tích hợp 4 shape chạy ổn định, toàn bộ 79 test host và 251 test student đạt kết quả xanh mà không gây xung đột vào code nghiệp vụ.

**Phần còn hạn chế:**
- Chưa chạy benchmark CP5 để có số liệu so sánh chi phí và độ dao động giữa các shape.
- Chưa mở rộng thêm các ca kiểm thử tải đồng thời cao (concurrency race condition) ngoài các ca có sẵn trong host.

**Bài học rút ra:**
- Ranh giới code/model rõ ràng: Các thao tác tiền bạc, phê duyệt và chống ghi trùng phải do code và cơ sở dữ liệu khóa chặt; model chỉ hỗ trợ trích xuất thông tin và soạn thảo.
- Tầm quan trọng của Idempotency và Ledger: Hệ thống cần dựa vào khóa duy nhất (`refund:{claim_id}`) và transaction nguyên tử để chống thanh toán trùng khi gặp crash hoặc retry.
- Trace Contract là ranh giới bảo mật: Cần lọc dữ liệu qua allowlist để ngăn ngừa rò rỉ secret hoặc PII của khách hàng.
