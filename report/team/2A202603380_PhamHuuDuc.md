# Báo cáo cá nhân — 2A202603380_PhamHuuDuc

## 1. Thông tin thành viên

- Họ tên: Phạm Hữu Đức
- MSSV: 2A202603380
- Email: phamduc31103@gmail.com
- GitHub: [ducpahm](https://github.com/ducpahm)
- Vai trò: Người C — Shape C (Orchestrator) & Nghiên cứu (Research)

## 2. Phần việc phụ trách

- **CP2:** Cài đặt toàn bộ Shape C trong `src/lab8/shapes/orchestrator.py` theo mô hình Orchestrator + Read-only Investigators.
- **CP3:** Hoàn thiện ranh giới Handoff với `lab8.handoff.make_handoff` (chỉ cho phép các tool đọc trong allowlist, không chuyển giao secret/headers); tích hợp tham số `crash_at` vào lệnh hoàn tiền và xử lý ngoại lệ `InjectedCrash` để kịp ghi nhận trace trước khi ném lại lỗi.
- **CP4:** Rà soát và quét sạch trace, ngăn chặn rò rỉ `CANARY_SECRET_*`, đảm bảo đáp ứng 3 điều kiện must-pass của đề bài; phối hợp kiểm tra `reports/crash.json` đạt 20/20.
- **CP5:** Chịu trách nhiệm thực hiện bài nghiên cứu thực nghiệm (ablation) và hoàn thiện phiếu nghiên cứu `report/team/research_card.md`.

## 3. Đóng góp cụ thể

- **Cài đặt `src/lab8/shapes/orchestrator.py`:**
  - Tổ chức hàm `run_claim` đảm bảo đóng kết nối SQLite an toàn qua khối `try ... finally`.
  - Tách bạch vai trò: Orchestrator quản lý ngân sách và điều phối; các investigator chỉ có quyền đọc (`lookup_order`, `lookup_policy`, `compute_compensation`).
  - Đảm bảo tính toán bồi thường hoàn toàn dựa trên dữ liệu thật của đơn hàng, không dựa dẫm vào MockLLM để tránh biến sai lệch như Swarm.
  - Tuân thủ Trace contract v1, ghi nhận đầy đủ sự kiện trên mọi nhánh kết thúc (kể cả `needs_info`, `escalated`, `denied`).
- **Bổ sung bộ kiểm thử riêng `src/tests/test_orchestrator.py`:**
  - `test_orchestrator_c001_resolves`: Kiểm thử quy trình hoàn tiền thành công cho đơn trễ hạn.
  - `test_orchestrator_missing_order_needs_info`: Kiểm thử claim thiếu mã đơn hàng trả về `needs_info`.
  - `test_orchestrator_unknown_claim_fails`: Kiểm thử claim không tồn tại trả về `failed`.
- **Commit chính:** `8966ddd` — `feat(cp2): implement Shape C orchestrator and add unit tests`.

## 4. Bằng chứng

- **Kết quả kiểm thử Shape C:**
  - `python -m pytest -q -m student -o addopts= -k orchestrator`: **62/62 test cases passed** (100%).
  - `python -m pytest -q tests/test_orchestrator.py`: **3/3 test cases passed**.
  - `python -m pytest -q tests/test_handoff_secret.py tests/test_trace_contract.py`: **9/9 test cases passed** (không rò rỉ secret, trace chuẩn contract).
- **Trạng thái kiểm tra toàn diện:**
  - `python -m lab8.check_submission`: Báo `[ OK ] shape orchestrator: format đúng, 12/12 claim public pass ở seed 11`.
  - `reports/crash.json`: Đạt độ an toàn **20/20**.

## 5. Công cụ AI đã dùng

- **Công cụ:** Antigravity (Google DeepMind Agentic Assistant).
- **Mục đích sử dụng:**
  - Hỗ trợ phân tích luồng điều phối Orchestrator - Investigators và đối chiếu các điểm yếu của Swarm Reference.
  - Hướng dẫn thiết lập ranh giới bảo mật Handoff và cấu trúc bọc Trace khi crash.
  - Hỗ trợ viết các kịch bản kiểm thử biên trong `src/tests/test_orchestrator.py`.
- **Cách tự kiểm tra và thẩm định kết quả:**
  - Chạy thực tế bằng công cụ chính thức của bài lab: `pytest`, `lab8.smoke`, `lab8.crash_test`, và `lab8.check_submission` trên môi trường Python 3.13 cục bộ.
  - Đọc trực tiếp file trace JSON sinh ra trong `src/traces/` để xác nhận không chứa chuỗi `CANARY_SECRET_*` và thông tin cá nhân khách hàng.

## 6. Tự đánh giá

- Hoàn thành đầy đủ và vượt tiến độ các mốc CP2, CP3, CP4 đối với Shape C.
- Kiến trúc code rõ ràng, phân định quyền hạn chặt chẽ theo nguyên tắc đặc quyền tối thiểu (least privilege).
- Đóng góp đầy đủ mã nguồn, unit test và báo cáo cá nhân đúng quy định của ban tổ chức.
