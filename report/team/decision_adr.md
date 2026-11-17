# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow 
- Commit hash: abdd828
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000    1.000   1.000-1.000  0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0/0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm quyết định chọn kiến trúc **Workflow (Shape A)** vì đây là kiến trúc ít tự chủ nhất nhưng đạt hiệu năng cao nhất với chi phí tối ưu nhất. Khi đánh giá trên cùng tập dữ liệu (14 public claims) và cùng 5 seed (11, 22, 33, 44, 55 — tổng cộng 70 trials), Workflow đạt tỷ lệ thành công 100% (pass rate = 1.000, pass^5 = 1.000) với seed variance = 0.000000, về chi phí thì chi phí mô phỏng của Workflow rẻ nhất trong cả 4 shape với 27.86 VND/success(so với 29.53 VND của Single Agent, 49.57 VND của Swarm và 52.86 VND của Orchestrator). Nhờ việc cố định logic kiểm tra ngày trễ, thẩm định chính sách và tính toán hoàn tiền hoàn toàn bằng code logic Python đọc trực tiếp từ database, Workflow loại bỏ triệt để rủi ro ảo giác hoặc bị đánh lừa bởi văn bản khiếu nại của khách hàng, đảm bảo tính an toàn và tính đảm bảo hành vi cao nhất cho môi trường thực tế

## Có đáng đổi lấy multi-agent không

Nhóm quyết định giữ và không đổi sang multi agent, trong thực tế và xử lý giao dịch hoàn tiền, tính ổn định và nhất quán quan trọng hơn một mức tăng pass rate nhỉnh hơn. Một hệ thống có phương sai cao (variance > 0) đồng nghĩa với việc cùng một hồ sơ khiếu nại nhưng chạy ở các thời điểm khác nhau có thể cho ra kết quả khác nhau, gây rủi ro thất thoát tiền bạc trong khi chi phí vận hành lại bị tăng lên, vậy nên việc đánh đổi sự ổn định và ngân sách để lấy một mức tự chủ không cần thiết là không nên

- Quyết định đảo lại chỉ khi bài toán thỏa mãn 3 điều kiện:
1. **Dữ liệu phi cấu trúc và ngữ cảnh mở:** Khi khiếu nại của khách hàng không thể chuẩn hóa thành các trường dữ liệu cố định trong DB mà đòi hỏi đọc hiểu ngôn ngữ tự nhiên phức tạp, phân tích bằng chứng hình ảnh (ảnh hàng vỡ) hoặc đối soát hợp đồng ngoại lệ
2. **Cần sự phối hợp và phản biện đa bên:** Khi một quyết định đòi hỏi nhiều góc nhìn chuyên biệt độc lập (ví dụ: Agent kho vận xác minh tình trạng vận chuyển, Agent tài chính kiểm tra ngân sách, Agent chăm sóc khách hàng đánh giá độ thân thiết) cùng thương lượng để đưa ra mức bồi thường linh hoạt
3. **Giá trị nghiệp vụ vượt xa chi phí LLM:** Khi mỗi case xử lý có giá trị kinh tế lớn, lúc đó mức tăng thêm vài phần trăm tỷ lệ thành công sẽ vượt trội hoàn toàn so với chi phí token và công sức kiểm soát của hệ thống Multi-Agent

## Trace và bằng chứng
Trace của nhóm được ghi nhận theo đúng Trace Contract v1, bao gồm các event:
- `claim`: Ghi nhận thông tin ban đầu đã qua allowlist (`claim_id`, `principal_id`, `order_id`)
- `lookup_order`: Trạng thái hiển thị và thông tin đơn hàng an toàn (`visible`, `reason`, `order`)
- `quote`: Kết quả định giá bồi thường do code tính (`amount_vnd`, `reason`, `parts`, `clause_ids`)
- `decision`: Quyết định cuối cùng ở mọi nhánh trả về, kể cả return sớm (`status`, `proposal_amount`, `reason`)
- `crash` & `error`: Điểm sập nguồn giả lập (`at: crash_at`) hoặc lỗi không tìm thấy claim

Các field cố ý không ghi vào trace:
1. **Secret và auth:** `parent_secret` và `raw_headers_json` (chứa `Authorization: Bearer CANARY_SECRET_*`). *Lý do:* Đây là thông tin nhạy cảm bảo mật, việc ghi vào log sẽ gây rò rỉ thông tin xác thực, tạo lỗ hổng cho kẻ tấn công mạo danh quyền hệ thống
2. **Thông tin định danh cá nhân (PII):** `phone` (SĐT khách), `address` (địa chỉ nhà), `item_name` (tên sản phẩm), và `internal_note` (chứa `CANARY_INTERNAL_*`). *Lý do:* Tuân thủ nguyên tắc tối thiểu hóa dữ liệu, việc tính tiền bồi thường chỉ cần các trường số liệu (`delay_days`, `shipping_fee_vnd`, `damage_verified`), không được phép đưa PII của khách hàng vào log điều hành
3. **Dữ liệu thô:** Cố ý không bao giờ gọi `SELECT *` hoặc dump nguyên dòng thô của bảng `claims` hay `orders`

Nếu trace nằm ngoài phạm vi scanner quét được, đội security chứng minh hệ thống không lộ secret bằng:
1. **Kiểm soát từ nguồn bằng Allowlist:** Phân tích mã nguồn tĩnh (Static Code Analysis) chứng minh lớp truy xuất dữ liệu (`lookup_order`, `get_claim_view`) chỉ chọn lọc đúng các trường trong bộ lọc cứng `ORDER_FIELDS`. Các trường bí mật và PII không bao giờ được nạp vào biến của Shape, do đó Shape không thể leak thứ mà nó không có
2. **Kiểm thử hộp đen bằng Canary:** Chạy thử nghiệm với dữ liệu giả lập chứa các chuỗi nhận diện độc nhất (`CANARY_SECRET_*`), sau đó quét toàn bộ bộ nhớ (memory dump), network egress và stdout/stderr của tiến trình để chứng minh các chuỗi này không bao giờ rời khỏi phạm vi bảo vệ của Host

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
