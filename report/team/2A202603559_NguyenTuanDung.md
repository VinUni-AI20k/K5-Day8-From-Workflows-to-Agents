# Báo cáo cá nhân — 2A202603559_NguyenTuanDung

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tuấn Dũng
- MSSV: 2A202603559
- Email: 26ai.dungnt13@vinuni.edu.vn
- GitHub: https://github.com/Ntd1411

## 2. Phần việc phụ trách

Tôi phụ trách Shape B — Single Agent, gồm vòng lặp ReAct, giới hạn quyền gọi tool, xử lý kết quả quote và chuyển yêu cầu hoàn tiền qua host. Ngoài ra, tôi tham gia kiểm tra các điều kiện bắt buộc về approval, secret leakage, crash safety và chạy benchmark public ở CP4–CP5.

## 3. Đóng góp cụ thể

- Commit chính: `49a0003` — `implement bounded single ReAct agent`.
- Triển khai `src/lab8/shapes/single.py` với `run_react(max_steps=8, worker=True)`. Agent chỉ chọn các read tool; `issue_refund` không nằm trong tool registry của agent.
- Dùng `get_claim_view` và dữ liệu order có cấu trúc làm nguồn sự thật. Nội dung ticket không được dùng để sửa `delay_days`, `damage_verified` hoặc chọn policy.
- Gọi `compute_compensation` để tính quote. MockLLM chỉ tham gia bước quyết định và được ghi nhận vào `Budget`, không quyết định số tiền.
- Truyền quote đầy đủ vào `durability.issue_refund`; host chịu trách nhiệm approval, trần theo đơn, idempotency và ghi ledger.
- Truyền `crash_at`, ghi trace khi xảy ra `InjectedCrash` rồi ném exception lại để crash/resume hoạt động đúng.
- Thêm `src/tests/test_single_agent_student.py`, kiểm tra Single Agent tin dữ liệu order thay vì câu “trễ 5 ngày” trong ticket của `C-002`.

## 4. Bằng chứng

- Commit: `49a0003`.
- Test: `test_single_agent_trusts_order_over_ticket` trong `src/tests/test_single_agent_student.py`.
- Run id minh họa: `R-single-C-002-s55`; kết quả đúng là `denied`, `proposal_amount=0` dù ticket nói giao trễ 5 ngày.
- Public benchmark: 70/70 trial thành công, pass rate `1.000`, pass^5 `1.000`, seed variance `0`, seed min–max `1.000–1.000`.
- Chi phí mô phỏng của Single Agent: `29.19 VND/success`; mean/p95 steps: `2.50/3`.
- Full student matrix: `248 passed`; host test: `60 passed`.
- Crash safety: `20/20` trong `src/reports/crash.json`.
- Benchmark: `src/reports/benchmark.json`.

## 5. Công cụ AI đã dùng

Tôi sử dụng OpenAI Codex để giải thích cấu trúc dự án, phân tích contract, hỗ trợ triển khai Single Agent, rà soát trace và chuẩn bị báo cáo. Tôi tự kiểm tra kết quả bằng `pytest`, public student matrix, crash suite và `lab8.check_submission`. Tôi cũng đối chiếu trực tiếp `docs/business_rules.md`, `docs/contracts.md` và code host để bảo đảm AI không tự quyết định tiền hoặc bỏ qua approval.

## 6. Tự đánh giá

Phần Single Agent đã hoàn thành đúng contract và ổn định trên năm seed public. Tôi hiểu rõ ranh giới giữa agent và host: agent chỉ đọc và đề xuất, còn code xác định quote và host kiểm soát side effect. Điểm cần cải thiện là tiếp tục kiểm chứng trên bộ hidden khi giảng viên cung cấp `student_drop/`; kết quả hiện tại dùng MockLLM nên chưa đại diện cho độ trễ hoặc hành vi của model sản xuất.
