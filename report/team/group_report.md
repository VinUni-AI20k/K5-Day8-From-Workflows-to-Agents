# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Soopi
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY8-Soopi-FromWorkflowsToAgents`
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 7e8fc66

## 2. Mục tiêu và cách tiếp cận

### 2.1. Mục tiêu bài toán
Bài toán đặt ra cho nhóm là xây dựng và đánh giá hệ thống xử lý khiếu nại bồi hoàn phí vận chuyển / hàng hỏng tự động cho công ty giả lập LogiX-VN. Mục tiêu trọng tâm không phải là xây dựng một hệ thống AI phức tạp nhất, mà là **tìm kiếm kiến trúc ít tự chủ nhất (least autonomous architecture) mà vẫn hoàn thành công việc một cách chính xác, an toàn, ổn định và tiết kiệm chi phí nhất**.

### 2.2. Cách tiếp cận và Phân kỳ thực hiện
Nhóm thực hiện theo 5 checkpoint tuần tự:
1. **CP1 (Khởi tạo):** Thiết lập môi trường ảo Python 3.12, chạy smoke test và xác thực cổng an toàn của Host.
2. **CP2 (Hiện thực 3 Shapes):** Viết mã nguồn cho Shape A (`workflow.py`), Shape B (`single.py`), và Shape C (`orchestrator.py`).
3. **CP3 (Độ bền bỉ & Khử khuẩn Handoff):** Đảm bảo cơ chế Idempotency chống chi trả 2 lần, xử lý bắt và ném ngoại lệ `InjectedCrash`, và cách ly bí mật qua Handoff.
4. **CP4 (Kiểm định Must-Pass):** Thực thi bộ kiểm thử sập nguồn 20/20 và rà soát rò rỉ dữ liệu nhạy cảm.
5. **CP5 (Đo lường & Quyết định):** Chạy thực nghiệm benchmark 4 shape x 5 seed, tổng hợp số liệu và viết báo cáo phân tích kiến trúc.

## 3. Giải pháp

### 3.1. Ranh giới Phân định Quyền hạn (Code vs. Model Boundary)
Nhóm áp dụng triệt để nguyên tắc **Model chỉ được đọc và đề xuất, Code là đối tượng duy nhất ra quyết định và ghi sổ**:
- **Tính toán tiền tệ:** Hoàn toàn do hàm logic tất định `compute_compensation` tính toán dựa trên các điều khoản chính sách có hiệu lực. Mô hình LLM tuyệt đối không được tự ý quyết định hay chỉnh sửa số tiền bồi thường.
- **Quyền ghi CSDL:** Tất cả các thao tác bồi hoàn đều phải đi qua cổng chốt chặn duy nhất của Host là `durability.issue_refund`. Các Agent không được cấp công cụ ghi dữ liệu (`WRITE_TOOLS`).

### 3.2. Chi tiết ba Shape được triển khai
- **Shape A — Deterministic Workflow (`workflow.py`):**
  - Chạy tuần tự theo một luồng cố định không có vòng lặp suy luận.
  - Sử dụng các adapter an toàn: `get_claim_view` $\rightarrow$ `lookup_order` $\rightarrow$ `compute_compensation` $\rightarrow$ `issue_refund`.
  - Không tốn chi phí gọi LLM, thời gian phản hồi nhanh nhất.
- **Shape B — Single ReAct Agent (`single.py`):**
  - Triển khai thông qua vòng lặp ReAct (`run_react`) với chặn trần tối đa 8 bước (`max_steps=8`).
  - Hàm `decide` của Agent suy nghĩ qua từng bước để chọn tool đọc thích hợp dựa trên thông tin quan sát được, sau đó kết luận bằng trạng thái `final`.
  - Host bên ngoài vòng lặp ReAct tiếp nhận đề xuất và thực thi lệnh ghi tiền.
- **Shape C — Orchestrator + Read-only Investigators (`orchestrator.py`):**
  - Áp dụng mô hình điều phối phân cấp. Orchestrator tạo tài liệu giao việc `make_handoff` được làm sạch (sanitized).
  - Các Sub-agents (`run_readonly_investigators`) được cách ly hoàn toàn, chỉ được cấp danh sách công cụ đọc trong `allowed_tools`.
  - Orchestrator nhận kết quả điều tra, phán quyết tính hợp lệ và gọi `issue_refund`.

### 3.3. Ranh giới Bảo mật và Trace Contract v1
- **Khử khuẩn Handoff:** Chỉ cho phép các trường thuộc `ALLOWED_FIELDS` và `FACT_KEYS`. Tuyệt đối không chuyển `parent_secret`, token `Authorization`, hoặc thông tin cá nhân khách hàng sang Sub-agents.
- **Trace Contract:** Ghi nhận đầy đủ các sự kiện nghiệp vụ (`lookup_order`, `quote`, `decision`, `crash`) dưới định dạng JSON với `run_id` nhất quán. Bộ quét an toàn không tìm thấy bất kỳ dấu hiệu rò rỉ nào của `CANARY_SECRET_*`, số điện thoại, hay địa chỉ nhà.

## 4. Kết quả thực nghiệm

### 4.1. Bảng số liệu Benchmark 4 Shape x 5 Seed (trích xuất từ `src/reports/benchmark.json`)

| Shape | Pass Rate | Pass^5 | Seed Variance | Min Seed | Max Seed | Cost / Success (VND) | Mean Steps | Mean Model Calls | Mean Tool Calls |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`workflow`** | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **27.86** | **2.14** | **0.0** | 2.79 |
| **`single`** | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **30.53** | **5.00** | **4.79** | 2.79 |
| **`orchestrator`** | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **47.36** | **3.07** | **2.00** | 4.79 |
| **`swarm`** | 0.986 | 0.929 | 0.000816 | 0.929 | 1.000 | 49.57 | 2.80 | 3.64 | 4.57 |

### 4.2. Kiểm thử Chịu lỗi Crash Suite (`src/reports/crash.json`)
- Đạt kết quả tuyệt đối: **`crash_safety = 20/20`**.
- Không có bất kỳ tình huống nào phát sinh việc ghi đúp dòng tiền trong bảng `refund_ledger` khi xảy ra sự cố sập nguồn giữa chừng.

### 4.3. Quyết định Kiến trúc (ADR)
Nhóm chính thức lựa chọn **Shape A — `workflow`** làm kiến trúc tối ưu nhất để nộp bài và triển khai thực tế. Chi tiết lập luận và phân tích điều kiện đảo ngược kiến trúc được trình bày tại [`report/team/decision_adr.md`](decision_adr.md).

## 5. Khó khăn và cách xử lý

1. **Bẫy trần hoàn tiền theo đơn hàng (Per-order Cap - T13, T14):**
   - *Vấn đề:* Ban đầu có thể nhầm lẫn rằng cần tự trừ khoản tiền đã hoàn trước đó rồi mới gửi sang Host.
   - *Cách xử lý:* Phải truyền Quote đầy đủ vào `issue_refund`, Host sẽ là đơn vị duy nhất tự động tính toán phần khấu trừ để tránh bị trừ lặp 2 lần.
2. **Nguy cơ nuốt mất ngoại lệ Crash (`InjectedCrash` - T12):**
   - *Vấn đề:* Khối xử lý ngoại lệ chung có thể vô tình triệt tiêu tín hiệu sập nguồn.
   - *Cách xử lý:* Tách riêng khối `except InjectedCrash:`, gọi `trace.write()` kịp thời xả nhật ký xuống đĩa rồi re-raise ngoại lệ ra ngoài.
3. **Bẫy tự từ chối khi Quote > 0 (`missing_policy_denied`):**
   - *Vấn đề:* Tự return `denied` ở code ứng dụng mà không gọi Host sẽ làm thiếu bản ghi kiểm toán `policy_denied`.
   - *Cách xử lý:* Khi Quote > 0, bắt buộc chuyển qua `issue_refund` để Host thẩm định và ghi audit log chuẩn.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của thành viên được ghi nhận tại [`TEAM.md`](../../TEAM.md) và báo cáo cá nhân [`report/team/2A202603544_NguyenDucDat.md`](2A202603544_NguyenDucDat.md).

## 7. Hạn chế và hướng cải thiện

- **Môi trường giả lập:** Nghiên cứu được thực hiện trên `MockLLM` với hạt giống cố định (seeded), chưa phản ánh đầy đủ độ trễ mạng thực tế (`latency: unavailable`) và sự biến động văn phong tự nhiên của LLM thương mại.
- **Hướng cải thiện:** Trong môi trường sản xuất, có thể mở rộng mô hình Workflow kết hợp một lớp LLM chuyên biệt chỉ để trích xuất thực thể (Named Entity Recognition) đối với các ticket có cấu trúc tự do phức tạp, trước khi chuyển giao dữ liệu sạch vào luồng xử lý tất định.

## 8. Tài liệu tham khảo

1. Google Research (2026), *Towards a Science of Scaling Agent Systems*.
2. MAST Team (NeurIPS 2025), *Why Do Multi-Agent LLM Systems Fail?*, arXiv:2503.13657.
3. Anthropic (2024), *Building Effective Agents*, Research Report.
4. Martin Fowler (2023), *Patterns for Resilient and Durable Distributed Workflows*.
