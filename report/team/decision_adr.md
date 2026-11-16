# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 96ab720
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86 (reports/benchmark.json)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm chọn kiến trúc **Workflow (Shape A)** dựa trên số liệu thực nghiệm đo đạc đồng nhất trên 14 claims × 5 seeds (70 trials) trong `src/reports/benchmark.json`. Workflow đạt điểm tuyệt đối: **Pass rate = 1.000**, **Pass^5 = 1.000**, độ ổn định tuyệt đối với **Seed variance = 0.000000**, chi phí thấp nhất toàn hệ sinh thái (**27.86 VND/success** so với 29.65 VND của Single, 46.43 VND của Orchestrator, và 49.57 VND của Swarm), cùng số bước thực thi tối ưu nhất (**1.64 mean steps**). Bản chất nghiệp vụ khiếu nại cước của LogiX-VN là quy trình xác định (deterministic): đối soát mã đơn, kiểm tra số ngày trễ thực tế từ cơ sở dữ liệu, áp trần bồi thường theo đơn và kiểm tra approval. Vì toàn bộ luật tính tiền và chính sách an toàn đều do Code và Host kiểm soát (`compute_compensation`, `durability.issue_refund`), Shape Workflow là lựa chọn "ít tự chủ nhất mà vẫn hoàn thành xuất sắc công việc", triệt tiêu hoàn toàn rủi ro ảo giác (hallucination), prompt injection từ ticket, và loại bỏ hoàn toàn phương sai không đáng có.

## Có đáng đổi lấy multi-agent không

Dựa trên bằng chứng thực nghiệm, câu trả lời là **hoàn toàn không đáng**. Khi chuyển đổi từ Workflow sang kiến trúc đa tác nhân (Swarm - Shape D), hệ thống không những không cải thiện được pass rate mà còn làm suy giảm độ tin cậy nghiêm trọng:
1. **Pass rate giảm & sinh phương sai:** Pass rate của Swarm giảm xuống **0.986**, Pass^5 chỉ đạt **0.929**, độ dao động seed variance tăng lên **0.000816** (min đạt 0.929 ở seed 55). Nguyên nhân là ở seed 55, Swarm bị lỗi nhận thức (cognitive failure / goal drift) khi tin vào số ngày khách phóng đại trong ticket thay vì đọc dữ liệu thật từ bảng `orders` (thất bại ở ca T02).
2. **Chi phí và độ phức tạp bùng nổ:** Chi phí trên mỗi ca thành công của Swarm tăng gần 78% (**49.57 VND** so với **27.86 VND** của Workflow), số bước thực hiện tăng từ 1.64 lên 2.80 steps do chi phí overhead trao đổi đồng cấp (`peer messaging`) và điều tra trùng lặp.

**Điều kiện làm quyết định đảo chiều:** Nhóm sẽ chỉ cân nhắc chuyển sang Single Agent hoặc Multi-Agent khi và chỉ khi:
- Dữ liệu đầu vào từ khách hàng là văn bản tự do, ngôn ngữ tự nhiên phức tạp hoặc đa phương tiện (ảnh chụp bưu kiện vỡ, video mở hàng) mà regex/rule-based code không thể phân tích được.
- Chính sách bồi thường đòi hỏi suy luận logic tình huống mở, đàm phán linh hoạt ngoài khung quy tắc cứng của database.
- Lợi ích kinh doanh thu được từ việc xử lý các ngoại lệ phức tạp vượt trội hơn hẳn chi phí token phát sinh và rủi ro dao động chất lượng (variance).

## Trace và bằng chứng

- **Các event được ghi nhận trong trace:** Trace của nhóm ghi đúng [Trace contract v1](../../docs/contracts.md#trace-contract-v1), bao gồm các event có cấu trúc: `claim` (`claim_id`, `order_id`), `decision` (`status`, `error_reason`), `quote` (thông tin bồi thường an toàn), và `crash` (khi kích hoạt điểm crash).
- **Các field cố ý KHÔNG ghi:**
  - Tuyệt đối loại bỏ `parent_secret`, `raw_headers` (chứa Authorization token `CANARY_SECRET_*`).
  - Tuyệt đối loại bỏ các thông tin nhận dạng cá nhân (PII): SĐT (`090...`), địa chỉ nhà khách hàng, tên mặt hàng cụ thể, và ghi chú nội bộ (`internal_note`).
  - *Lý do:* Trace là một ranh giới bảo mật (security boundary). Mọi tệp trace đều bị scanner tự động quét. Việc ghi nhật ký thô (raw dump row) sẽ vi phạm must-pass security leak và làm lộ lọt dữ liệu nhạy cảm của khách hàng.
- **Chứng minh hệ thống an toàn nếu trace nằm ngoài phạm vi scanner:**
  - Nhóm áp dụng nguyên lý **Secure-by-Design & Least Privilege**: Toàn bộ dữ liệu đi vào Shape đều qua các view/tool chỉ đọc có projection cố định (`get_claim_view`, `lookup_order`). Database query không bao giờ dùng `SELECT *` từ bảng `claims` mà chỉ chọn đúng các trường cần thiết, do đó `parent_secret` và PII nhạy cảm chưa từng được nạp vào bộ nhớ ngữ cảnh của Shape.
  - Về mặt kiểm toán kỹ thuật: Codebase được bảo vệ bởi Static Analysis (chặn hoàn toàn việc `print` raw payload ra stdout/stderr) và hợp đồng interface cô lập (`safe_dump`), đảm bảo dữ liệu bí mật không thể bị rò rỉ ngay cả khi không có scanner bên ngoài.

## Giới hạn

- Thực nghiệm được tiến hành trên `MockLLM` với seed cố định nhằm đảm bảo tính tái lập (reproducibility) trong phòng lab. MockLLM không mô phỏng hoàn toàn độ trễ mạng thực tế (chỉ số latency ghi nhận là `unavailable`) và chưa phản ánh hết các suy thoái ngữ cảnh phức tạp của các LLM sản xuất thương mại.
- Chi phí token là chi phí mô phỏng dựa trên cấu hình `config/pricing.yaml`, không phải là hóa đơn tài chính thực tế từ các nhà cung cấp dịch vụ cloud.
- Toàn bộ kết luận của nhóm bám sát dữ liệu thu được từ benchmark công khai, không suy diễn vượt quá phạm vi bằng chứng, và bảo đảm tính toàn vẹn không can thiệp thủ công vào các tệp JSON báo cáo.
