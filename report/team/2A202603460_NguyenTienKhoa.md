# Báo cáo cá nhân — Nguyễn Tiến Khoa

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tiến Khoa
- MSSV: 2A202603460
- Email: nkhoa151004@gmail.com
- GitHub: llkhoa

## 2. Phần việc phụ trách

- Triển khai toàn bộ 3 kiến trúc (Shape A `workflow`, Shape B `single`, Shape C `orchestrator`).
- Xây dựng vòng lặp ReAct có kiểm soát (bounded ReAct loop) cho Shape B với giới hạn 8 bước và các công cụ đọc.
- Đảm bảo ranh giới bảo mật và sanitize dữ liệu cho Shape C (Orchestrator và read-only Investigator).
- Kiểm tra tính chịu lỗi và idempotency khi crash hệ thống (Crash test 20/20).
- Thực hiện đo đạc benchmark trên 4 kiến trúc với 5 seed độc lập và viết báo cáo phân tích.

## 3. Đóng góp cụ thể

- **Shape A (Workflow)**: Cài đặt luồng quyết định tuần tự, không để model tự ý can thiệp vào tính tiền hay duyệt hoàn tiền; quote đầy đủ do `compute_compensation` tính toán và ủy thác việc ghi sổ qua `durability.issue_refund`.
- **Shape B (Single Agent)**: Hiện thực hóa ReAct Agent sử dụng `lab8.runtime.run_react` với hàm `decide` tương tác với MockLLM, lưu trữ ngữ cảnh quan sát và chỉ được phép gọi read tools (`get_claim_view`, `lookup_order`, `compute_compensation`).
- **Shape C (Orchestrator)**: Khởi tạo handoff an toàn với `lab8.handoff.make_handoff`, lọc bỏ hoàn toàn các trường bí mật như `parent_secret` và thông tin PII khách hàng, giao nhiệm vụ điều tra cho investigator chỉ đọc.
- **Idempotency & Crash Handling**: Đảm bảo tất cả các shape chuyển giao `crash_at` xuống tầng host SQLite an toàn, không bắt `InjectedCrash` để pass bài kiểm tra crash.

## 4. Bằng chứng

- **Test suite**: Vượt qua 62/62 test student cho mỗi shape (tổng cộng 248/248 test student pass 100%).
- **Cổng host**: 54/54 test pytest mặc định pass.
- **Crash test suite**: Đạt kết quả an toàn tuyệt đối 20/20 (`src/reports/crash.json`).
- **Benchmark report**: `src/reports/benchmark.json` ghi nhận pass rate 1.000 cho workflow, single, orchestrator và 0.986 cho swarm.

## 5. Công cụ AI đã dùng

- Dùng AI Agent để hỗ trợ rà soát cú pháp, đối chiếu các schema và hợp đồng dữ liệu trong `contracts.md` và `business_rules.md`.
- Tự kiểm tra độc lập bằng cách chạy trực tiếp các lệnh kiểm thử của hệ thống: `python -m lab8.smoke`, `python -m pytest -q`, `python -m lab8.crash_test`, `python -m lab8.benchmark` và `python -m lab8.check_submission`.

## 6. Tự đánh giá

- Hoàn thành đầy đủ các yêu cầu từ CP1 đến CP5 của bài thực hành.
- Hiểu rõ ranh giới giữa code kiểm soát logic/bảo mật và model AI trong các kiến trúc agent.
- Đạt điểm tối đa ở các tiêu chí must-pass (không lộ secret, không bypass approval, an toàn khi crash).
