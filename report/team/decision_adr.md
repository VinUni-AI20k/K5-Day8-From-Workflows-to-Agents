# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: CHƯA COMMIT — thay bằng hash của commit chứa bản sửa single.py và src/reports/
- Run id dẫn chứng: R-workflow-C-002-s55, R-workflow-C-013-s11, R-workflow-C-014-s11 (đối chứng: R-swarm-C-002-s55 fail) — src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (14 claim × 5 seed = 70 trial, bộ public)
- Cost per success (mô phỏng, VND): 28.80 (single 29.29, swarm 49.57, orchestrator 57.12)
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public (ma trận student T01–T14 xanh ở cả 5 seed, gồm các case canary và approval hỏng)

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng corpus public (14 claim), cùng 5 seed `11,22,33,44,55`, cùng MockLLM và `config/pricing.yaml`, ba shape nhóm viết đều đạt pass 1.000, pass^5 1.000, variance 0. Swarm đạt 0.986 / 0.929 vì ở seed 55 nó tin số ngày trễ trong ticket (T02, `R-swarm-C-002-s55` trả `resolved` thay vì `denied`). Khi chất lượng ngang nhau, nhóm chọn shape **ít tự chủ nhất**: workflow có cost/success thấp nhất (28.80 VND; single 29.29, swarm 49.57, orchestrator 57.12), chỉ 1 lần gọi model (soạn chữ), 4.43 step trung bình, và mọi nhánh quyết định là code Python cố định nên đọc lại và audit được. Tiền do `compute_compensation` tính từ order row và policy hiện hành; ticket không bao giờ được dùng để lấy số ngày trễ hay số tiền, nên lỗi kiểu T02 của swarm không xảy ra ở seed nào.

## Có đáng đổi lấy multi-agent không

Không. Trên public, orchestrator không tăng pass (1.000 = 1.000) nhưng cost/success gấp ~2 lần (57.12 so với 28.80) vì thêm lượt plan và tool call của investigator (5.57 so với 2.79 tool call/trial). Swarm vừa đắt hơn vừa có variance khác 0. Task claims là chuỗi tuần tự (claim → order → quote → host), không có nhánh song song để chia cho agent con, nên thêm agent chỉ thêm cost và thêm bề mặt rò rỉ (handoff, trace).

Quyết định sẽ đảo lại nếu: (1) bộ hidden có loại claim mà luật cố định không bao được (ví dụ cần đọc chứng từ phi cấu trúc để xác minh hư hỏng) và một shape có model đạt pass cao hơn workflow một khoảng vượt nhiễu seed; (2) workflow dưới 0.75 trên hidden trong khi single/orchestrator trên 0.75; hoặc (3) cần điều tra song song nhiều nguồn độc lập, khi đó orchestrator mới tận dụng được investigator. Kể cả khi đó, tiền, approval và idempotency vẫn phải ở code/host.

## Trace và bằng chứng

Trace workflow (`src/traces/<run_id>.json`, contract v1 qua `lab8.trace.Trace`) ghi các event: `tool` (get_claim_view: found / has_order_id; lookup_order: visible, reason, order view đã qua allowlist), `quote` (amount_vnd, reason, clause_ids), `issue_refund` (ok, reason, conflict), `crash` (điểm crash; trace được flush trước khi ném lại `InjectedCrash`), `error` (chỉ tên lớp exception) và `decision` (status, proposal_amount, reason). Mọi nhánh return, kể cả `needs_info`, `escalated`, `failed`, đều đi qua `finish()` nên luôn có trace của chính lần chạy.

Cố ý **không** ghi: nội dung ticket (dữ liệu người dùng, có thể chứa injection hoặc secret), claim row thô và `parent_secret`, `principal_id`, order row thô (SĐT, địa chỉ, tên hàng, ghi chú nội bộ), và message của exception (có thể mang dữ liệu đầu vào). Lý do: trace là ranh giới bảo mật mà grader quét, không phải log debug; chỉ ghi những gì cần để audit quyết định.

Nếu trace nằm ngoài chỗ scanner quét được, đội security không thể dựa vào "đã quét không thấy". Bằng chứng phải là cấu trúc: shape chỉ đọc claim qua `get_claim_view` (đã bỏ secret và header) và order qua `lookup_order` (view allowlist), không có đường code nào đưa ticket hay row thô vào `trace.add`; kèm test canary trong ma trận T01–T14 chạy trên mọi seed, và scanner quét cả kết quả trả về lẫn mọi file `<run_id>*`.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75. Mọi số trên chỉ từ bộ public 14 claim; chưa có `student_drop/` nên chưa tự kiểm hidden. Cost là giá mô phỏng trong `config/pricing.yaml`, không phải hóa đơn API. Pass 1.000 trên public không đảm bảo ≥ 0.75 trên 40 claim hidden.
