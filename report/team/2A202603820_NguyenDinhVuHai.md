# Báo cáo cá nhân — <MSSV>_NguyenDinhVuHai

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đình Vũ Hải
- MSSV: 2A202603820
- Email: nguyendinhvuhai1234@gmail.com
- GitHub: HaiVuuu

## 2. Phần việc phụ trách

- **Shape A — `workflow`:** Hiện thực hàm `run_claim` trong `src/lab8/shapes/workflow.py` hoàn thành các checkpoint CP2, CP3 và CP4.
- **Unit & Integration Tests:** Viết bộ kiểm thử `src/tests/test_team_workflow.py` kiểm tra tính bất biến trước dữ liệu nhiễu trong ticket, khả năng phục hồi idempotent sau crash và tuân thủ Trace Contract v1.
- **Đo lường & So sánh:** Chạy benchmark so sánh `workflow` với `swarm` (70 trials) để báo cáo cho Lead.

## 3. Đóng góp cụ thể

- **Commit chính:** `submit` (nhánh `nguyendinhvuhai`).
- **Code & Test đã thêm/sửa:**
  - `src/lab8/shapes/workflow.py`: Xây dựng pipeline xác định (deterministic) đọc claim qua `get_claim_view`, kiểm tra thiếu `order_id` (`needs_info`), tra cứu đơn qua `lookup_order` có kiểm soát phạm vi principal (`escalated` nếu không hợp lệ), tính tiền hoàn bằng `compute_compensation`, gọi `durability.issue_refund` với toàn bộ quote cùng tham số `crash_at` (không nuốt `InjectedCrash`), và ghi trace trên mọi nhánh thoát thông qua `lab8.shapes.common.finish()`.
  - `src/tests/test_team_workflow.py`: Bổ sung các test case kiểm tra: (1) ticket ghi "trễ 9 ngày" nhưng đơn thực tế trễ 2 ngày phải trả `denied`; (2) crash tại `after_effect_before_checkpoint` và chạy lại trên cùng SQLite chỉ tạo đúng 1 dòng `refund_ledger` và 1 audit `refund_committed`; (3) trace file khớp `run_id` và sạch secret/PII trên nhiều kịch bản (`C-001`, `C-005`, `C-010`).
- **Quyết định kỹ thuật — Ranh giới Code / Model và các trường Trace cố ý không ghi:**
  - **Ranh giới Code / Model:** Toàn bộ luồng điều khiển, kiểm tra quyền sở hữu dữ liệu, tính toán số tiền hoàn và ghi nhận giao dịch được khóa cứng bằng code Python xác định thông qua các hàm host (`get_claim_view`, `lookup_order`, `compute_compensation`, `durability.issue_refund`). Nội dung văn bản tự do trong `ticket` không bao giờ được phân tích để lấy `order_id`, số ngày trễ hay điều khoản áp dụng; mọi căn cứ tính tiền chỉ lấy từ bản ghi `orders` và `policies` hiện hành trong SQLite. Mô hình ngôn ngữ (`MockLLM`) được loại bỏ hoàn toàn khỏi đường dẫn quyết định và ghi sổ (`model_calls = 0`), triệt tiêu rủi ro prompt injection, ảo giác số liệu và sai lệch giữa các seed.
  - **Các trường Trace cố ý không ghi:** Để tuân thủ Trace Contract v1 và ranh giới bảo mật, `workflow` tuyệt đối không dump bản ghi thô từ bảng `claims` hoặc `orders` ra trace hay `stdout`. Cụ thể, các trường nhạy cảm sau được cố ý loại bỏ hoàn toàn: `parent_secret`, `raw_headers` (chứa token `Bearer CANARY_SECRET_*`), nội dung `ticket` thô, cùng toàn bộ thông tin định danh và nội bộ trên đơn hàng gồm số điện thoại (`phone`), địa chỉ giao hàng (`address`), tên sản phẩm (`item_name`) và ghi chú vận hành (`internal_note`). Trace chỉ lưu metadata tối thiểu đã qua allowlist (`claim_id`, `order_id`, trạng thái `visible`, các trường nghiệp vụ từ `lookup_order`, kết quả `quote` và trạng thái `issue_refund`).

## 4. Bằng chứng

- **Commit & Nhánh:** Nhánh `nguyendinhvuhai`, commit `submit` (kèm PR gửi Lead).
- **Kết quả Pytest:**
  - `python -m pytest -q -m student -o addopts= -k workflow` → **62 passed**, 245 deselected (4.69s).
  - `python -m pytest -q` → **59 passed**, 248 deselected (8.73s), bao gồm toàn bộ test trong `src/tests/test_team_workflow.py`.
- **Kết quả Benchmark (`workflow` vs `swarm` trên 14 claims × 5 seeds = 70 trials):**
  - `workflow`: **pass rate = 1.000** (70/70), **pass^5 = 1.000**, `seed_variance = 0.000000`, **cost/success = 27.86 VND**, `mean_steps = 3.79`, `mean_model_calls = 0.0` (ví dụ run ID: `R-workflow-C-001-s11`, `R-workflow-C-002-s55`, `R-workflow-C-014-s11`).
  - `swarm`: `pass rate = 0.986` (69/70), `pass^5 = 0.929`, `seed_variance = 0.000816`, `cost/success = 49.57 VND` (lỗi trên `R-swarm-C-002-s55`: `status resolved != denied` do tin vào số ngày trễ ghi trong ticket ở seed chia hết cho 5).

## 5. Công cụ AI đã dùng

- **Công cụ:** Gemini.
- **Mục đích sử dụng:** Hỗ trợ rà soát hợp đồng dữ liệu (`contracts.md`, `business_rules.md`), đối chiếu chữ ký hàm host (`tools.py`, `durability.py`, `common.py`), phác thảo cấu trúc cho `src/lab8/shapes/workflow.py` và các ca kiểm thử trong `src/tests/test_team_workflow.py`.
- **Tự kiểm tra kết quả:** Tự đọc lại từng dòng diff để đảm bảo không thay đổi signature `run_claim`, không copy `REFERENCE_WEAKNESS`, truyền nguyên quote vào `issue_refund` và không bắt `InjectedCrash`. Chạy trực tiếp `pytest` (62/62 student tests, 59/59 default & team tests) và `python -m lab8.benchmark` trên môi trường local để xác minh toàn bộ số liệu trước khi commit.

## 6. Tự đánh giá

- Hoàn thành đầy đủ 100% checklist của Shape A (`workflow`) từ CP1 đến CP4, đạt `pass_rate = 1.000` và `pass^5 = 1.000` với chi phí mỗi lần thành công thấp hơn ~43.8% so với `swarm`.
- Mức độ hoàn thành cá nhân: **10/10**.