# Báo cáo cá nhân — Tăng Nguyễn Hải Đăng — 2A202603916

## 1. Thông tin thành viên

- Họ tên: Tăng Nguyễn Hải Đăng
- MSSV: 2A202603916
- Email: damedang1411@gmail.com
- GitHub: https://github.com/haidangwork1411

## 2. Phần việc phụ trách

Vai trò: **Thành viên 4 — Safety & Testing**

Phạm vi phụ trách:
- **CP1 — Setup & Baseline:** Khởi tạo môi trường ảo Python 3.12 (`src/.venv`), cài đặt dependencies đúng chuẩn repo, chạy smoke test và ghi nhận baseline kiểm thử ban đầu (54 host passed, ma trận student 186 failed do 3 shape chưa code, 62 swarm passed).
- **Phát triển Test An toàn Độc lập (Safety Invariant):** Thiết kế và viết đúng **1 test an toàn độc lập** tại ranh giới host/policy (`src/tests/test_safety_approval_invariant.py`) nhằm kiểm tra bất biến an toàn bắt buộc: Khi không có approval hợp lệ (cụ thể là approval bị rejected), cổng host phải chặn dứt khoát và tuyệt đối không ghi nhận refund vào ledger.
- **Audit An toàn các Nhánh Thành viên:** Thực hiện audit cô lập bằng `git worktree` tạm ngoài repo cho các nhánh đồng đội (`origin/Workflow_CP2,3`, `origin/feature/orchestrator`, `origin/nguyenquanghuy`) trước khi merge, rà soát ranh giới bảo mật, rò rỉ secret/PII, hợp đồng `RunResult`, cơ chế crash/retry và điều kiện nộp bài.
- **Tích hợp & Kiểm thử Toàn diện Hệ thống:** Sau khi các PR của Workflow, Orchestrator và Single được merge vào `origin/main`, thực hiện đồng bộ tích hợp vào nhánh kiểm thử và chạy kiểm thử hồi quy toàn diện trên cả 4 shape, cổng host và crash suite 20/20.

## 3. Đóng góp cụ thể

### A. Test do tôi trực tiếp viết và đóng góp (1 test)
- **Commit kỹ thuật:** `733745de580667e3bed07506a5532c46d100363b` — `test(safety): add approval invariant enforcement test`.
- **File triển khai:** [`src/tests/test_safety_approval_invariant.py`](../../src/tests/test_safety_approval_invariant.py).
- **Hành vi kiểm thử:**
  - Khởi tạo claim `C-TEST-REJECTED` trỏ vào đơn hàng `O-107` (giao trễ 4 ngày, đủ điều kiện hoàn 35.000 VND phí ship, chính chủ `P-100`).
  - Gắn kèm approval `A-TEST-REJECTED` nhưng có trạng thái bị từ chối (`status = 'rejected'`).
  - Khi gọi lệnh thực thi hoàn tiền `durability.issue_refund`, xác minh 5 bất biến bắt buộc:
    1. Cổng host từ chối: `outcome["ok"] is False`, `reason == "approval_rejected"`, `effect is None`.
    2. Ledger không bị ô nhiễm: `get_refund(conn, claim_id) is None`.
    3. Tổng số dòng trong bảng `refund_ledger` không thay đổi trước và sau khi gọi (`ledger_count_after == ledger_count_before`).
    4. Không có sự kiện ghi tiền: `committed_audit_count(conn, claim_id) == 0`.
    5. Ghi nhận đúng audit từ chối chính sách: Sự kiện `policy_denied` với chi tiết lý do `"approval_rejected"`.

### B. Công việc Audit Độc lập các Nhánh Đồng đội (qua git worktree)
- **Nhánh `origin/Workflow_CP2,3` (Nguyễn Đức Minh - Shape A):** Đã audit mã nguồn và test trong worktree độc lập; xác nhận vượt qua 62/62 student test workflow, 54/54 host test và 3 test riêng của Minh (`src/tests/test_workflow.py`).
- **Nhánh `origin/feature/orchestrator` (Nguyễn Nghiêm Khánh Tiệp - Shape C):** Đã audit handoff allowlist và 16 test riêng của Tiệp (`src/tests/test_orchestrator_own.py`), xác nhận không leak secret/PII và đạt 62/62 student test orchestrator cùng 20/20 crash test suite.
- **Nhánh `origin/nguyenquanghuy` (Nguyễn Quang Huy - Shape B):** Đã audit bản đầu phát hiện thiếu test riêng/docs; sau khi Huy push bản mới (`cabceb8`), đã re-audit xác nhận đạt 62/62 student test single và 8 test riêng của Huy (`src/tests/test_single.py`).

### C. Tích hợp Hệ thống
- Tích hợp sạch sẽ `origin/main` vào nhánh `feat/dang-safety-testing` (merge commit `07202ef`, không có conflict).
- Toàn bộ code nghiệp vụ các shape (A, B, C) do các thành viên tương ứng phụ trách; tôi không sửa code nghiệp vụ hay thay đổi logic của các shape.

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
| **Crash test suite** | Suite kiểm thử host & crash | `python -m lab8.crash_test --count 20 --out /tmp/crash_test.json` | **crash_safety 20/20** |

**Giới hạn xác minh thực tế:**
- Các kết quả trên được kiểm chứng đầy đủ trên bộ fixture public (14 claim T01–T14 × 5 seed).
- Tôi không tự ý suy diễn hay khẳng định pass rate trên bộ dữ liệu ẩn (hidden test suite), và không tự chạy benchmark CP5 vì đây là nhiệm vụ đánh giá chung của cả nhóm.

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI (Google Antigravity / Gemini).
- **Mục đích sử dụng:**
  - Hỗ trợ tra cứu cấu trúc schema SQLite trong `src/lab8/db.py` và cơ chế phân quyền trong `src/lab8/policy.py`.
  - Gợi ý kịch bản test biên cho trường hợp approval có trạng thái `rejected` nhằm bao quát ranh giới an toàn host gate.
- **Phương pháp tự kiểm tra và kiểm chứng (Verification Method):**
  - Đọc trực tiếp và đối chiếu yêu cầu trong `docs/business_rules.md` (mục "Không có approval, approval hết hạn, bị thu hồi...") và `docs/contracts.md`.
  - Chạy thực thi độc lập qua pytest trên cơ sở dữ liệu SQLite trong sandbox; viết truy vấn SQL trực tiếp để xác nhận dòng ledger không được sinh ra và event `policy_denied` được ghi nhận chính xác.
  - Sử dụng `git worktree` cách ly ngoài repo để kiểm chứng output thực tế của từng nhánh, không dựa vào thông báo miệng hay suy đoán.

## 6. Tự đánh giá

**Phần làm tốt:**
- Thiết kế test an toàn thực chất, chứng minh được tính bất biến của cổng duyệt host (chống hoàn tiền trái phép khi approval bị rejected).
- Đảm bảo quy trình audit nghiêm ngặt qua worktree độc lập, phát hiện sớm các thiếu sót về deliverable của đồng đội trước khi tích hợp vào nhánh chính.
- Thực hiện kiểm thử tích hợp toàn diện trên toàn bộ 4 shape, đảm bảo 79 test host và 251 test student đạt 100% xanh mà không làm phát sinh bất kỳ xung đột hay sửa đổi sai lệch nào vào code nghiệp vụ.

**Phần còn hạn chế:**
- Chưa mở rộng thêm các kịch bản kiểm thử tải đồng thời cao (concurrency race condition) ở mức sâu hơn ngoài các ca kiểm tra sẵn có trong host.
- Cần phối hợp cùng nhóm ở CP5 để quan sát các chỉ số benchmark thực tế (chi phí mô phỏng, độ lệch chuẩn giữa các seed) nhằm đưa ra kết luận kiến trúc toàn diện.

**Bài học rút ra:**
- "Fail-closed" là nguyên tắc sống còn: Mọi quyết định xuất tiền phải do code và cơ sở dữ liệu khóa chặt; các mô hình ngôn ngữ chỉ đóng vai trò phân tích thông tin đầu vào.
- Trách nhiệm của Safety & Testing là bảo vệ ranh giới hệ thống: Kiểm thử không chỉ là xác nhận tính năng chạy được (happy path), mà quan trọng hơn là chứng minh hệ thống từ chối an toàn khi gặp dữ liệu sai, approval hỏng hoặc sự cố crash bất ngờ.
