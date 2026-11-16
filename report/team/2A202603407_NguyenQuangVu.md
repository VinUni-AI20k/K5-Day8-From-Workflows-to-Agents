# Báo cáo cá nhân — 2A202603407_NguyenQuangVu

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quang Vũ
- MSSV: 2A202603407
- Email: vu.nq@vinuni.edu.vn
- GitHub: nguyenquangvu

## 2. Phần việc phụ trách

- **Nghiên cứu, cài đặt và đánh giá 4 kiến trúc (Shapes):**
  - Cài đặt Shape A (`src/lab8/shapes/workflow.py`): Quy trình tuần tự xác định (Deterministic Workflow).
  - Cài đặt Shape B (`src/lab8/shapes/single.py`): Tác nhân ReAct giới hạn 8 bước (Single Agent ReAct).
  - Cài đặt Shape C (`src/lab8/shapes/orchestrator.py`): Điều phối viên và điều tra viên chỉ đọc qua handoff bảo mật (Orchestrator-Workers).
  - Vận hành và đối chứng với Shape D (`src/lab8/shapes/swarm_reference.py`): Mô hình Swarm baseline.
- **Kiểm thử chất lượng & Đo lường:**
  - Viết bộ unit test `src/tests/test_workflow_custom.py`.
  - Thực thi bộ kiểm thử va đập Crash Safety (20/20 kịch bản).
  - Thực thi đo lường Benchmark 280 trials (4 shapes × 14 claims × 5 seeds).
  - Soạn thảo hồ sơ quyết định kiến trúc (`decision_adr.md`) và phiếu nghiên cứu (`research_card.md`).

## 3. Đóng góp cụ thể

- **Triển khai toàn bộ 3 Shape nhóm cần viết (A, B, C):**
  - *Shape A (Workflow):* Xây dựng pipeline tuần tự hoàn chỉnh: đọc claim view qua allowlist, kiểm tra order_id, tra cứu đơn hàng, tính quote bằng code `compute_compensation`, từ chối quote <= 0, gọi `durability.issue_refund` với full quote và flush trace khi gặp crash.
  - *Shape B (Single Agent):* Xây dựng vòng lặp ReAct `run_react` với hàm `decide()` mô phỏng suy nghĩ qua MockLLM, chỉ gọi các công cụ đọc, miễn nhiễm với prompt injection từ văn bản ticket.
  - *Shape C (Orchestrator):* Thiết lập gói handoff an toàn `make_handoff` (không rò rỉ context cha hay secret), kích hoạt điều tra viên chỉ đọc qua `run_readonly_investigators`, orchestrator trực tiếp giải ngân.
- **Đảm bảo cơ chế Crash Injection & Trace Contract:**
  - Bắt ngoại lệ `InjectedCrash` trong cả ba shape để kịp thời gọi `trace.write()` trước khi re-raise lên host/grader (vượt qua test T12).
  - Tuân thủ nghiêm ngặt Trace Contract v1, cam kết không ghi bất kỳ secret (`CANARY_SECRET_*`) hay PII khách hàng vào trace.
- **Đo lường Benchmark & Đánh giá khoa học:**
  - Chạy `lab8.crash_test` sinh file `src/reports/crash.json` đạt tuyệt đối 20/20.
  - Chạy `lab8.benchmark` sinh file `src/reports/benchmark.json` (280 trials), chứng minh Workflow tối ưu tuyệt đối: Pass rate 1.000, Pass^5 1.000, Variance 0.000000, Chi phí thấp nhất 27.86 VND/success.

## 4. Bằng chứng

- **File code:** `src/lab8/shapes/workflow.py`, `src/lab8/shapes/single.py`, `src/lab8/shapes/orchestrator.py`.
- **File test:** `src/tests/test_workflow_custom.py` (5 tests passed).
- **Kết quả kiểm thử:**
  - Toàn bộ 248/248 bài kiểm thử student matrix đều xanh 100% (`pytest -q -m student -o addopts=`).
  - Crash safety: 20/20 passed (`src/reports/crash.json`).
  - `python -m lab8.check_submission`: 0 FAIL.

## 5. Công cụ AI đã dùng

- **Công cụ:** Google DeepMind Antigravity Agent.
- **Mục đích:** Hỗ trợ phân tích mã nguồn starter, rà soát các nhánh điều kiện biên của hợp đồng Output Contract v1, thiết kế cấu trúc điều hướng cho hàm `decide()` trong ReAct và gói handoff allowlist.
- **Cách tự kiểm tra kết quả:** Trực tiếp thực thi các lệnh kiểm thử tự động của pytest (`python -m pytest`), chạy crash suite và benchmark, kiểm tra trace JSON để đảm bảo 100% không rò rỉ secret hay PII.

## 6. Tự đánh giá

- Hoàn thành toàn diện 100% các yêu cầu của cả 4 kiến trúc và báo cáo.
- Đạt kết quả tối đa ở tất cả các tiêu chí: Pass rate 1.000, Pass^5 1.000, Variance 0.0, Crash safety 20/20.
- Điểm tự đánh giá: 10/10.
