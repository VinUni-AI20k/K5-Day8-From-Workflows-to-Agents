# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Solo Developer (Nguyễn Khởi Vinh)
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 9b8cc3e

## 2. Mục tiêu và cách tiếp cận

Bài toán Lab 8 yêu cầu cài đặt và đánh giá quy trình xử lý khiếu nại hoàn phí vận chuyển của công ty giả lập LogiX-VN dựa trên 4 hình thái kiến trúc khác nhau:
1. Shape A (`workflow`): Các bước xác định bằng code Python cứng, ranh giới rõ ràng.
2. Shape B (`single`): Một ReAct agent với giới hạn bước tối đa 8 bước, chỉ dùng read tools.
3. Shape C (`orchestrator`): Mô hình bộ điều phối và các điều tra viên chuyên biệt với gói handoff được khử dữ liệu nhạy cảm (sanitize).
4. Shape D (`swarm`): Nhóm các agent ngang hàng giao tiếp với nhau.

Mục tiêu học tập cốt lõi là áp dụng nguyên lý quyền tự chủ tối thiểu (Principle of Least Autonomy): chọn hình thái kiến trúc ít tự chủ nhất nhưng vẫn hoàn thành mục tiêu một cách an toàn, tin cậy và tiết kiệm chi phí nhất.

Thứ tự thực hiện:
- Tìm hiểu các hợp đồng giao tiếp (`contracts.md`) và luật nghiệp vụ hoàn tiền (`business_rules.md`).
- Cài đặt Shape A Workflow → Shape B Single Agent → Shape C Orchestrator.
- Kiểm tra tính bền vững (Idempotency, Crash safety 20/20) và ranh giới an toàn thông tin (chặn rò rỉ PII/secret).
- Chạy benchmark đo lường toàn diện và rút ra kết luận kiến trúc dựa trên số liệu.

## 3. Giải pháp

### Ranh giới Code và Model
- **Code (Host)** nắm toàn quyền kiểm soát logic kinh doanh và an toàn dữ liệu:
  - Tính toán số tiền bồi thường (`compute_compensation` dựa trên chính sách hiện hành và dữ liệu đơn hàng).
  - Kiểm tra điều kiện approval, quyền sở hữu của `principal_id`, và áp trần hoàn tiền tối đa theo đơn hàng (`durability.issue_refund`).
  - Đảm bảo tính Idempotency (`refund:{claim_id}`) và ghi nhật ký kiểm toán duy nhất `refund_committed` trong cùng một transaction SQLite.
- **Model (MockLLM)** chỉ đóng vai trò hỗ trợ đọc, lập kế hoạch hoặc soạn thảo câu từ phản hồi khách hàng; tuyệt đối không để model quyết định số tiền hoàn hay gọi hàm ghi dữ liệu.

### Chi tiết 3 Shape nhóm viết
- **Shape A (Workflow)**: Luồng xử lý tuần tự hoàn toàn tất định. Đọc claim qua `get_claim_view`, kiểm tra `order_id`, tra cứu đơn hàng bằng `lookup_order`, tính bồi thường qua `compute_compensation`, và gửi toàn bộ quote vào host. Nếu quote = 0 thì từ chối ngay mà không ghi ledger; nếu quote > 0 thì chuyển cho host duyệt và ghi nhận.
- **Shape B (Single Agent)**: Xây dựng hàm `decide` vận hành trong vòng lặp ReAct `run_react` (tối đa 8 bước). Agent chỉ được cấp quyền gọi các công cụ đọc. Sau khi kết thúc vòng lặp ReAct, host trích xuất kết quả và thực hiện ghi ledger.
- **Shape C (Orchestrator)**: Khởi tạo gói bàn giao `make_handoff` chỉ chứa các trường thuộc allowlist (`task`, `facts`, `allowed_tools`), tuyệt đối không đính kèm `parent_secret` hay thông tin cá nhân. Gọi `run_readonly_investigators` chạy các điều tra viên chỉ đọc và tổng hợp kết quả tại orchestrator trước khi chuyển sang host duyệt.

### An toàn Trace và Handoff
- Trace chỉ ghi nhận các trường đã lọc sạch: trạng thái đơn, kết quả quote từ host, quyết định cấp cao, và event crash.
- Các trường nhạy cảm như `parent_secret`, số điện thoại, địa chỉ nhận hàng, tên món hàng, ghi chú nội bộ đều được loại bỏ hoàn toàn khỏi trace và stdout.

## 4. Kết quả

### Bảng so sánh 4 Shape trên bộ Public (70 trials/shape = 14 claims × 5 seeds)

| Shape | Pass Rate | Pass^5 | Seed Variance | Min - Max | Cost/Success (VND) | Mean Steps | P95 Steps |
|---|---|---|---|---|---|---|---|
| **workflow** | **1.000** | **1.000** | **0.000000** | **1.000 - 1.000** | **28.79** | **1.86** | **2.0** |
| **single** | 1.000 | 1.000 | 0.000000 | 1.000 - 1.000 | 30.75 | 6.57 | 7.0 |
| **orchestrator** | 1.000 | 1.000 | 0.000000 | 1.000 - 1.000 | 57.05 | 2.79 | 3.0 |
| **swarm** | 0.986 | 0.929 | 0.000816 | 0.929 - 1.000 | 49.57 | 2.80 | 3.0 |

*Ghi chú: Chi phí VND là chi phí mô phỏng theo `config/pricing.yaml`.*

### Đánh giá Độ tin cậy và An toàn
- **Crash Safety**: Đạt `20/20` qua bộ kiểm thử `lab8.crash_test` (bảo đảm an toàn giao dịch ở cả 2 điểm sự cố `before_effect` và `after_effect_before_checkpoint`).
- **Secret Leaks / Approval Bypass**: 0 lượt rò rỉ secret / 0 lượt vi phạm approval.
- **Phân tích Swarm Weakness**: Ở seed 55 tại claim C-002, Swarm tin vào chuỗi ký tự trong ticket thay vì dữ liệu có cấu trúc của order row, dẫn đến việc giải ngân sai và trượt tiêu chí `status resolved != denied`.

## 5. Khó khăn và cách xử lý

1. **Vấn đề môi trường Windows & Python**:
   - Khi cài đặt `PyYAML` trên Windows với Python phiên bản mới, thiếu MSVC Build Tools dẫn tới lỗi biên dịch C extension.
   - *Cách xử lý*: Thiết lập biến môi trường `$env:PYYAML_FORCE_LIBYAML="0"` để ép cài đặt bản Pure Python an toàn, hoàn tất cài đặt các dependency theo yêu cầu mà không làm biến đổi môi trường.
2. **Xử lý Crash Injection**:
   - T12 yêu cầu exception `InjectedCrash` phải được ném ra ngoài hàm `run_claim` để test runner kiểm tra, nhưng trace vẫn phải được lưu trữ để phục vụ kiểm toán.
   - *Cách xử lý*: Sử dụng khối `try...except InjectedCrash`, thực hiện `trace.write()` rồi ngay lập tức `raise` lại exception, đáp ứng hoàn hảo cả 2 điều kiện.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- MockLLM mô phỏng việc sinh token và tính toán chi phí theo bảng giá cố định, chưa phản ánh được độ trễ mạng thực tế (`latency: unavailable`) và độ bất định của các mô hình sinh ngôn ngữ tự nhiên thương mại.
- Khi mở rộng ra hệ thống thật: Cần bổ sung thêm các validator bằng JSON Schema cho các công cụ, tích hợp kiểm soát truy cập dựa trên vai trò (RBAC) nghiêm ngặt hơn, và mở rộng cơ chế caching cho các truy vấn chính sách ít thay đổi.

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. MAST: Multi-Agent System Taxonomy, NeurIPS 2025.
3. Tài liệu đặc tả kỹ thuật và luật nghiệp vụ LogiX-VN (`docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`).
