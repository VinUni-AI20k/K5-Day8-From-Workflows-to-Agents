# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 7272047
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000 - 1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng tập kiểm thử công khai (14 claim x 5 seed = 70 trial), `workflow` đạt kết quả vượt trội và toàn diện nhất:
1. **Độ chính xác và tính ổn định tuyệt đối:** Đạt `pass_rate = 1.000`, `pass^5 = 1.000`, và phương sai `seed_variance = 0.000000`. Ngược lại, kiến trúc `swarm` bị trượt ở seed 55 trên claim `C-002` do dính lỗi tin tưởng số ngày trễ ghi trong ticket người dùng thay vì kiểm tra cơ sở dữ liệu (`pass_rate = 0.986`, `pass^5 = 0.929`).
2. **Chi phí vận hành tối ưu nhất:** `workflow` đạt chi phí mô phỏng chỉ **27.86 VND / thành công** với số bước thực thi trung bình thấp nhất (2.14 bước), rẻ hơn `single` (30.53 VND, 5.0 bước), `orchestrator` (47.36 VND, 3.07 bước) và `swarm` (49.57 VND, 2.80 bước).
3. **An toàn và bất biến:** Do không sử dụng mô hình LLM để rẽ nhánh hay tính toán tiền bạc, `workflow` hoàn toàn miễn nhiễm với ảo giác (hallucination) và tấn công prompt injection từ câu chữ trong ticket, đồng thời vượt qua bài kiểm tra chịu lỗi sập nguồn đạt 20/20 (`crash_safety`).

## Có đáng đổi lấy multi-agent không

**Không đáng.** Với bài toán xử lý khiếu nại hoàn tiền LogiX-VN, việc nâng cấp lên Single-Agent, Orchestrator hay Swarm không mang lại bất kỳ sự gia tăng nào về tỷ lệ thành công (tất cả các shape do nhóm xây dựng đều đạt 1.000 pass rate), nhưng lại làm tăng đáng kể chi phí mô phỏng (tăng từ 10% đến hơn 70%) và tiềm ẩn rủi ro lệch mục tiêu hoặc rò rỉ dữ liệu khi giao tiếp giữa các agent.

**Điều kiện nào làm quyết định kiến trúc đảo lại (khi nào nên đổi sang Multi-agent)?**
Quyết định kiến trúc sẽ đảo ngược sang Orchestrator / Multi-agent khi bài toán xuất hiện các yếu tố sau:
1. **Nhiệm vụ đa miền và chuyên biệt hóa cao:** Khi việc xử lý khiếu nại yêu cầu tích hợp các nguồn dữ liệu phi cấu trúc phức tạp (như phân tích hình ảnh hàng hóa bị vỡ, giám định hóa đơn scan OCR tiếng nước ngoài, hoặc tra cứu các điều ước vận tải quốc tế) mà các luật if-else bằng code không thể bao quát hết.
2. **Yêu cầu xử lý phân tán song song (Parallel latency reduction):** Khi cần truy vấn đồng thời nhiều đơn vị đối tác vận chuyển thứ ba (3PL) độc lập có độ trễ mạng lớn, mô hình Orchestrator phân chia tác vụ song song cho các Sub-agents sẽ tối ưu thời gian phản hồi (latency) tốt hơn luồng tuần tự.
3. **Phân tách ranh giới ủy quyền bảo mật (Security Privilege Separation):** Khi quy trình yêu cầu các cấp độ truy cập khác nhau (ví dụ: Agent chăm sóc khách hàng bên ngoài không được nhìn thấy CSDL tài chính và token ngân hàng nội bộ).

## Trace và bằng chứng

- **Các event được ghi trong Trace:**
  - `lookup_order`: Lưu thông tin đơn hàng đã lọc sạch qua allowlist (`ORDER_FIELDS`).
  - `quote`: Lưu chi tiết báo giá và lý do tính toán của `compute_compensation`.
  - `decision`: Lưu các quyết định rẽ nhánh (`needs_info`, `escalated`, `denied`).
  - `crash`: Ghi nhận điểm sập nguồn giả lập khi kích hoạt bài test chịu lỗi.
- **Các field cố ý KHÔNG ghi và lý do:**
  - Tuyệt đối không ghi `parent_secret`, `raw_headers` (chứa Authorization Bearer token), số điện thoại khách hàng (`phone`), địa chỉ nhà (`shipping_address`), ghi chú nội bộ (`internal_note`), hay tên hàng hóa (`item_name`).
  - Lý do: Trace là một phần của ranh giới bảo mật (security boundary). Grader quét regex tự động toàn bộ file trace; nếu phát hiện PII hoặc secret, hệ thống sẽ bị đánh rớt theo điều kiện Must-Pass.
- **Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?**
  - Đội security chứng minh thông qua **kiểm toán tĩnh mã nguồn (Static Code Analysis)** và **phân tích dòng dữ liệu (Taint Analysis)**:
    1. Xác minh rằng mã nguồn chỉ sử dụng các hàm đọc được bao bọc an toàn (`get_claim_view`, `lookup_order`), không hề tồn tại câu lệnh `SELECT *` đọc toàn bộ bảng dữ liệu.
    2. Xác minh các biến chứa secret không bao giờ được truyền làm tham số vào bất kỳ hàm I/O nào (không truyền vào logger, trace, stdout, print, hay API bên ngoài).

## Giới hạn

- Thử nghiệm được thực hiện trên môi trường giả lập `MockLLM` có seed, không phải mô hình ngôn ngữ lớn chạy trên môi trường production thực tế.
- Độ trễ (latency) được quy ước là `unavailable` do không đo thời gian mạng và suy luận LLM thực.
- Toàn bộ chi phí được tính toán mô phỏng theo bảng giá tại `config/pricing.yaml` (VND), không phải hóa đơn API thanh toán thực tế.
- Các số liệu đã được kiểm chứng tự động bằng script `lab8.benchmark` và `lab8.crash_test`, không qua chỉnh sửa thủ công.
