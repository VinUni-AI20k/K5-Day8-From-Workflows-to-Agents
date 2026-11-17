# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: Nhóm 145
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim` và cùng contract kết quả. Mục tiêu là chọn kiến trúc ít tự chủ nhất nhưng vẫn xử lý đúng nghiệp vụ, giữ an toàn hoàn tiền và có chi phí hợp lý. Ticket là dữ liệu đầu vào; số ngày trễ và số tiền phải căn cứ vào order cùng policy hiện hành, không làm theo chỉ dẫn hay số tiền khách tự ghi trong ticket.

Theo phân công trong `TEAM.md`, Vũ Quang Thanh phụ trách workflow, Vương Toàn Minh Hiếu phụ trách single và Nguyễn Mạnh Cường phụ trách orchestrator. Vũ Thành phụ trách phiếu nghiên cứu (`research_card.md`) và quyết định kiến trúc (`decision_adr.md`). Nguyễn Đình Trường phụ trách benchmark và tổng hợp báo cáo nhóm.

Cách tiếp cận lấy swarm có sẵn làm đối chứng, workflow làm đường cơ sở với các bước cố định, rồi so sánh với single có vòng ReAct và orchestrator có investigator chỉ đọc. Các phần triển khai độc lập dùng chung host thay vì tự viết cơ chế ghi tiền. Sau phần nghiệp vụ là kiểm tra retry/crash, bảo mật handoff và benchmark trên cùng claim, seed, policy và bảng giá. Tiêu chí so sánh gồm pass rate, pass^5, độ dao động theo seed, chi phí trên mỗi trial thành công và số event trace.

## 3. Giải pháp

**Workflow:** `get_claim_view` đọc các trường claim được phép; thiếu `order_id` trả `needs_info`. `lookup_order` kiểm tra phạm vi principal; order không thấy được trả `escalated`. `compute_compensation` tính quote từ order và policy, bỏ qua số ngày khách khai trong ticket. Quote bằng 0 trả `denied`; quote dương được truyền nguyên số tiền tới `issue_refund`. Host từ chối thì trả `denied`, xung đột số tiền trả `failed`, thành công trả `resolved`. Shape này không gọi model. Trace ghi `claim` chỉ gồm các ID, `lookup_order`, `quote`, `decision`; claim không tồn tại ghi `error`, crash ghi `crash` rồi ném lại ngoại lệ.

**Single:** shape dùng `run_react(..., max_steps=8)` với observation ban đầu từ `get_claim_view`. Hàm `decide` hiện được viết bằng Python theo trạng thái: đọc order → tính compensation → kết thúc; MockLLM được gọi với purpose `decide` hoặc `draft`, nhưng văn bản model trả về không được phân tích để chọn tool hay quyết định số tiền. Vì vậy đây là vòng ReAct có hướng đi được code quy định, chưa phải agent tự lập kế hoạch linh hoạt. Runtime chỉ dispatch tool đọc và chặn tool ghi. Sau vòng lặp, code gọi `issue_refund` với full quote; chạm trần bước trả `failed`. Trace ghi `react_thought`, `react_observation`, `quote`, `decision`, cùng `error` hoặc `crash` khi có.

**Orchestrator:** đọc claim qua `get_claim_view`, kiểm tra order thuộc principal, rồi tạo handoff cho nhiệm vụ `check_applicable_policy`. Bản hiện tại đọc order trực tiếp bằng SQL có điều kiện principal và chỉ đưa các trường nghiệp vụ cần thiết vào facts. Investigator chạy các tool `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation` qua `run_readonly_investigators`. Orchestrator lấy quote trả về và là bên gọi `issue_refund`; investigator không được ghi tiền. Shape này hiện không gọi MockLLM; việc điều phối là code cố định. Trace ghi `claim_view`, `handoff`, `investigator`, `quote`, `refund_call`; nhánh thiếu order ghi `decision`.

**Ranh giới code/model và bảo mật:** cả ba shape dùng code để tính tiền, kiểm quyền và ghi refund. `make_handoff` tạo contract `handoff.v1`, lọc facts theo allowlist gồm delay, xác minh hư hỏng, carrier, trạng thái order, phí vận chuyển và số tiền đã thanh toán; `sanitize` lọc trường ngoài contract, từ chối secret/header còn sót và tool ghi. Không dùng tóm tắt LLM để thay thế lọc dữ liệu. Các read tool trả order theo allowlist, không trả điện thoại, địa chỉ, tên hàng hay ghi chú nội bộ. Orchestrator hiện ghi cả claim view có ticket vào trace; đây là phần cần tiếp tục rà soát nếu ticket có dữ liệu nhạy cảm ngoài bộ public.

`durability.issue_refund` là cửa ghi chung: host xác minh approval thuộc đúng claim, kiểm trần theo order và tự trừ khoản claim trước đã nhận. Shape giữ `proposal_amount` bằng full quote, không tự trừ trước. Ledger và audit `refund_committed` được ghi trong cùng transaction, có khóa chống trùng theo claim; retry căn cứ vào ledger. Cả ba shape truyền `crash_at`; workflow và single ghi trace rồi ném lại `InjectedCrash`, orchestrator để ngoại lệ lan truyền. Mọi nhánh trả `RunResult` đều dùng `finish` để đối chiếu ledger/audit và ghi JSON trace với `run_id`, `events`.

## 4. Kết quả

Số liệu dưới đây lấy từ [`src/reports/benchmark.json`](../../src/reports/benchmark.json) đang có trong repository, không phải kết quả chạy lại khi viết báo cáo. Mỗi shape có 14 claim × 5 seed (`11, 22, 33, 44, 55`) = 70 trial, tổng cộng 280 trial. Các biến kiểm soát gồm `as_of=2026-11-15`, MockLLM, bảng giá mô phỏng chung và một SQLite mới cho mỗi trial.

| Shape | Trial pass | Pass rate | Pass^5 | Seed min–max | Seed variance | Cost/success (VND mô phỏng) | Mean / p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |
| Workflow | 70/70 | 100% | 100% | 100%–100% | 0 | 27,8571 | 3,7857 / 4 |
| Single | 70/70 | 100% | 100% | 100%–100% | 0 | 29,5343 | 4,5714 / 5 |
| Orchestrator | 70/70 | 100% | 100% | 100%–100% | 0 | 52,8571 | 4,2857 / 5 |
| Swarm | 69/70 | 98,5714% | 92,8571% | 92,8571%–100% | 0,00081633 | 49,5670 | 2,8000 / 3 |

Pass^5 là tỷ lệ claim pass cả năm seed; variance tính trên tỷ lệ pass theo seed ở thang 0–1. Steps là số event trace, không phải thời gian chạy hay số vòng suy luận. Chi phí là mô phỏng, không phải hóa đơn API; latency của cả bốn shape là `unavailable`.

Workflow, single và orchestrator đạt cùng độ đúng trên bộ public. Workflow có cost/success thấp nhất; single cao hơn khoảng 6,02%, orchestrator cao hơn khoảng 89,74%. Swarm có ít event trace hơn nhưng chi phí cao hơn workflow và có một trial sai: `C-002`, seed `55` (`R-swarm-C-002-s55`), trả `resolved` thay vì `denied`. Đây là điểm yếu đối chứng đã nêu trong đề: swarm tin số ngày trễ trong ticket thay vì order ở seed chia hết cho 5. Workflow dùng dữ liệu order nên tránh được lỗi này. Kết quả public ủng hộ workflow làm lựa chọn cơ sở; chưa đủ để suy ra hiệu quả trên dữ liệu thực tế hoặc model sản xuất.

Về độ bền, [`src/reports/crash.json`](../../src/reports/crash.json) ghi nhận **20/20 kịch bản pass**: 5 trước effect, 7 sau effect trước checkpoint, 5 sau checkpoint, 1 xung đột số tiền khi retry, 1 retry thiếu approval và 1 crash-resume qua swarm. Đối chiếu `lab8/crash_test.py`, 19 kịch bản đầu kiểm tra trực tiếp host, kịch bản cuối kiểm tra swarm; kết quả này chứng minh bộ crash suite hiện có đạt yêu cầu, chưa phải bằng chứng 20/20 riêng cho từng shape sinh viên. Cơ chế chung bảo đảm retry không tạo refund và audit committed thứ hai; retry xung đột hoặc không đủ quyền được kiểm tra riêng.

Chưa có artifact kết quả tự kiểm `student_drop/` trong các báo cáo đã đọc, nên chưa kết luận pass rate hidden hay đạt ngưỡng 0,75 trên 200 hidden trial. Các số liệu trên phản ánh artifact hiện có; cần tái sinh benchmark và crash report nếu mã nguồn thay đổi trước khi chốt nộp.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- **Thiếu thư viện trong môi trường Python:** khi chạy test bằng Python mặc định, lệnh `python -m pytest` báo `No module named pytest`; test dùng `unittest` cũng chưa chạy được vì `No module named 'yaml'`. Cách xử lý là dùng đúng môi trường ảo của dự án và cài thư viện bằng `python -m pip install -r requirements.txt` trong `src/` trước khi chạy lại.
- **Phân biệt dữ liệu ticket và dữ liệu order:** ticket có thể ghi số ngày trễ khác thực tế. Nhóm dùng order và policy hiện hành để tính compensation. Bằng chứng đối chứng trong `src/reports/benchmark.json` là swarm sai ở `C-002`, seed `55`, trong khi workflow xử lý đúng.
- **Tránh hoàn tiền trùng khi retry hoặc crash:** các shape truyền full quote và `crash_at` cho host, không tự ghi ledger hay tự trừ tiền đã hoàn. Host kiểm approval và dùng ledger cùng audit trong một transaction; kết quả bộ crash suite được lưu tại `src/reports/crash.json` là 20/20.
- **Giữ an toàn dữ liệu khi handoff và ghi trace:** nhóm dùng claim/order view được giới hạn trường và handoff theo allowlist, không chuyển toàn bộ bản ghi cho investigator. Trace vẫn cần được rà soát khi bổ sung dữ liệu mới, đặc biệt với nội dung ticket.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

- MockLLM là mô phỏng, chưa phản ánh đầy đủ khả năng và lỗi của model sản xuất. Chi phí trong báo cáo là chi phí mô phỏng; latency là `unavailable`, nên chưa thể kết luận kiến trúc nào chạy nhanh hơn trong thực tế.
- Bộ public chỉ có 14 claim với 5 seed, chưa bao quát mọi tình huống nghiệp vụ. Nhóm cần đánh giá thêm trên bộ hidden và bổ sung trường hợp ticket mơ hồ, dữ liệu thiếu, retry và dữ liệu nhạy cảm.
- Single và orchestrator hiện có luồng xử lý chủ yếu do code quy định. Nhóm cần thử các nhiệm vụ cần lựa chọn tool hoặc phối hợp linh hoạt hơn để đánh giá rõ lợi ích của agent.
- Hướng cải thiện là bổ sung kiểm tra crash-resume riêng cho từng shape, rà soát dữ liệu ghi vào trace và chạy lại benchmark sau mỗi thay đổi quan trọng. Workflow đang phù hợp với kết quả public; lựa chọn có thể thay đổi nếu single hoặc orchestrator xử lý tốt hơn các claim phức tạp với mức chi phí và độ ổn định chấp nhận được.

## 8. Tài liệu tham khảo
- Google Research 2026, *Towards a Science of Scaling Agent Systems* 
- MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?*
- AgentArch, AACL 2026
- EMNLP 2026, *Rethinking Evaluation of MAS Efficiency*
