# Báo cáo cá nhân — 2A202603605_NguyenHaAnh

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Hà Anh
- MSSV: 2A202603605
- Email: 26ai.anhnh7@vinuni.edu.vn
- GitHub: haanh293

## 2. Phần việc phụ trách

- **Role 1 — Workflow + Team Lead / Integration:**
  - Khởi tạo repo nhóm, thiết lập môi trường chuẩn (`.venv` Python 3.12), điều phối phân chia công việc cho 4 thành viên và giữ cổng host (`python -m pytest -q`) luôn xanh khi tích hợp.
  - Cài đặt hoàn chỉnh **Shape A (`workflow`)** tại `src/lab8/shapes/workflow.py` (cả CP2 và CP3).
  - Xây dựng bộ unit test riêng cho Shape A tại `src/tests/test_team_workflow.py`.
  - Tổng hợp `TEAM.md` và biên soạn mục 1, 2, 3 (phần Shape A) và 6 trong `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- **Thiết kế và cài đặt `src/lab8/shapes/workflow.py`:**
  - Tách biệt rõ ranh giới giữa **code** và **model**: mọi quyết định về quyền truy cập đơn hàng (`lookup_order`), tính toán mức bồi thường (`compute_compensation` dựa trên dòng `orders` và `policies` có `is_current = 1`), và ghi sổ cái (`durability.issue_refund`) đều do code Python quyết định 100%.
  - Chỉ gọi `MockLLM` (`complete(..., purpose="draft")`) đúng 1 lần ở cuối mỗi nhánh để soạn câu chữ phản hồi khách hàng; tuyệt đối không dùng số ngày trễ hay điều khoản do khách viết trong `ticket`.
  - Truyền **quote đầy đủ (full quote)** từ `compute_compensation` vào `durability.issue_refund` để host tự trừ phần tiền đã hoàn của các claim trước trên cùng đơn hàng (đảm bảo đúng T13 và T14, tránh trừ hai lần).
  - Chuyển tiếp `crash_at` vào `durability.issue_refund` và khi gặp `InjectedCrash` thì ghi nhận sự kiện crash vào file trace (`trace.write()`) rồi để exception lan truyền tự nhiên, phục vụ kiểm thử độ bền vững (T12 và crash suite).
  - Chỉ ghi các trường đã qua allowlist vào `Trace` (không ghi `ticket`, `parent_secret`, SĐT, địa chỉ, tên hàng hay ghi chú nội bộ) và luôn kết thúc bằng `lab8.shapes.common.finish()`.
- **Viết unit test tại `src/tests/test_team_workflow.py`:**
  - `test_workflow_ignores_ticket_delay_across_all_seeds`: Kiểm chứng `workflow` giữ nguyên kết quả `denied` (`proposal_amount = 0`) trên `C-002` qua cả 5 seed (`11, 22, 33, 44, 55`), không bị đánh lừa bởi câu chữ "trễ 5 ngày" trong ticket như `swarm` ở seed 55.
  - `test_workflow_early_returns_and_unknown_claim_keep_clean_trace`: Kiểm chứng các nhánh trả về sớm (`C-999` unknown claim $\rightarrow$ `failed`, `C-004` thiếu `order_id` $\rightarrow$ `needs_info`) vẫn sinh file trace hợp lệ theo Trace contract v1 và không rò rỉ `CANARY_SECRET`.
  - `test_workflow_passes_full_quote_for_per_order_cap`: Kiểm chứng hành vi truyền full quote trên `C-013` (`denied`, `proposal_amount = 35000`, có audit `policy_denied`) và `C-014` (`resolved`, `proposal_amount = 150000`, `refund_effects` ghi nhận phần chênh `120000`).

## 4. Bằng chứng

- Code cài đặt: `src/lab8/shapes/workflow.py`
- File test: `src/tests/test_team_workflow.py`
- Kết quả chạy kiểm thử:
  - `python -m lab8.smoke` $\rightarrow$ `lab8.smoke pass`
  - `python -m pytest -q -m student -o addopts= -k workflow` $\rightarrow$ `62 passed` (đạt 100% ma trận public T01–T14 trên cả 5 seed, bao gồm T11 retry và T12 crash recovery).
  - `python -m pytest -q` $\rightarrow$ `57 passed` (54 test cổng host + 3 test mới trong `test_team_workflow.py`).
- Commit chính: `8915a3b` (`feat(workflow): implement Shape A deterministic workflow and unit tests`)

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (Gemini) trong IDE.
- **Mục đích sử dụng:**
  - Đọc hiểu nhanh cấu trúc repo, đối chiếu luật nghiệp vụ (`docs/business_rules.md`) và hợp đồng đầu ra/trace (`docs/contracts.md`).
  - Lên phương án chia 4 role cho nhóm để làm việc song song không xung đột Git.
  - Hỗ trợ rà soát các nhánh trạng thái của `workflow.py` và viết các ca kiểm thử biên trong `src/tests/test_team_workflow.py`.
- **Cách tự kiểm tra kết quả:**
  - Tự đọc lại từng dòng trong `src/lab8/shapes/workflow.py` đối chiếu với docstring và `swarm_reference.py` để chắc chắn không có logic tính tiền nào phụ thuộc vào `MockLLM` và không có dữ liệu thô (`claims`, `orders`) nào được đưa vào `trace.add()`.
  - Chạy trực tiếp `python -m pytest -q -m student -o addopts= -k workflow` và `python -m pytest -q` trong môi trường ảo `.venv` để xác nhận toàn bộ 62 test student của `workflow` và 57 test cổng host đều pass.

## 6. Tự đánh giá

- Hoàn thành đầy đủ trách nhiệm của Role 1 (cài đặt Shape A đạt 62/62 test student, viết 3 unit test mới, thiết lập cấu trúc phối hợp nhóm trong `TEAM.md` và `group_report.md`).
- Nắm vững nguyên lý thiết kế hệ thống agent an toàn: dùng kiến trúc ít tự chủ nhất khi bài toán có luật nghiệp vụ xác định, đặt việc tính tiền/kiểm quyền/idempotency vào tầng code/transaction của host, và coi trace là một ranh giới bảo mật.
