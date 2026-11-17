# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: NHOMSH
- Thành viên: Nguyễn Tiến Đạt (2A202603922, Lớp L3B), xem [`TEAM.md`](../../TEAM.md).
- Commit chốt (trùng [`report/team/decision_adr.md`](decision_adr.md)): `0f3c523`

## 2. Mục tiêu và cách tiếp cận

Bài toán yêu cầu xử lý khiếu nại hoàn phí vận chuyển và đền bù hư hỏng hàng hóa của LogiX-VN qua bốn kiến trúc (`workflow`, `single`, `orchestrator`, `swarm`) dưới cùng chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.

Cách tiếp cận của nhóm bám sát nguyên tắc phân tách trách nhiệm giữa **Code/Host** và **Model**:
- **Code và Host nắm quyền quyết định tài chính và an toàn:** lọc quyền sở hữu đơn (`principal_id`), đối chiếu chính sách hiện hành (`is_current = 1`, `effective_date <= 2026-11-15`), tính toán mức bồi hoàn qua `compute_compensation`, kiểm tra chữ ký phê duyệt (`approval_id` phải thuộc đúng `claim_id`), áp trần hoàn tiền theo đơn (per-order cap) và đảm bảo idempotency (`refund:{claim_id}`) trong cùng một giao dịch SQLite.
- **Chữ trong ticket là dữ liệu không tin cậy (untrusted user input):** không lấy mã đơn, số ngày trễ hay mệnh lệnh bỏ qua chính sách từ nội dung văn bản của khách hàng.
- **Thứ tự thực hiện:** hoàn thiện `workflow` làm chuẩn cơ sở (baseline), xây dựng vòng lặp ReAct giới hạn bước cho `single`, thiết lập cơ chế `make_handoff` và worker chỉ đọc cho `orchestrator`, sau đó kiểm thử độ bền crash và đo đạc định lượng trên cả bốn kiến trúc.

## 3. Giải pháp

- **Shape A (`workflow`):** Thực thi tuần tự cố định trong Python, không gọi model. Shape đọc claim qua `get_claim_view` (chỉ trích xuất `found`, `claim_id`, `order_id`), kiểm tra `order_id` (thiếu thì trả `needs_info`), tra cứu đơn qua `lookup_order` (không thấy hoặc khác chủ sở hữu thì trả `escalated`), tính quote bằng `compute_compensation`. Nếu `quote <= 0` thì trả `denied` mà không gọi host; nếu `quote > 0` thì truyền **nguyên quote đầy đủ** vào `durability.issue_refund`.
- **Shape B (`single`):** Chạy một vòng lặp ReAct qua `run_react(..., max_steps=8)`. Hàm `decide` gọi `MockLLM` ở mỗi bước và chỉ được phép chọn trong các công cụ đọc (`get_claim_view`, `lookup_order`, `compute_compensation`), tuyệt đối không có quyền gọi công cụ ghi. Sau khi vòng lặp trả về trạng thái `quoted`, phần code bên ngoài mới gọi `durability.issue_refund`.
- **Shape C (`orchestrator`):** Sau khi kiểm tra sơ bộ claim, orchestrator đóng gói dữ kiện qua `make_handoff` (`contract_version = "handoff.v1"`, `principal_scope = "owner_order_only"`, chỉ cấp quyền 4 công cụ đọc `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`). Hàm `sanitize` loại bỏ mọi trường ngoài allowlist và chặn cứng các dấu hiệu nhạy cảm (`CANARY_SECRET_*`, `parent_secret`, `raw_headers`, write tools). Worker chạy qua `run_readonly_investigators` với cờ `worker=True`; sau đó orchestrator nhận kết quả và gọi `durability.issue_refund`.
- **Truyền quote đầy đủ & Xử lý Crash:** Cả ba shape đều truyền nguyên `proposal = quote["amount_vnd"]` vào `issue_refund(conn, claim_id, proposal, crash_at=crash_at)` để host tự trừ số tiền đơn hàng đã được hoàn ở các claim trước (đáp ứng T13, T14). Khi gặp `InjectedCrash`, shape ghi sự kiện `crash` ra file trace rồi để ngoại lệ nổi lên đúng yêu cầu kiểm thử T12. Mọi đường trả về đều đi qua `lab8.shapes.common.finish()` để đồng bộ trạng thái với `refund_ledger`.

## 4. Kết quả

Kết quả benchmark trên bộ public (14 claim × 5 seed × 4 shape = 280 trial), trích xuất từ [`src/reports/benchmark.json`](../../src/reports/benchmark.json):

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Mean model / tool calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `workflow` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 3.43 / 4 | 0.00 / 2.79 |
| `single` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 31.94 | 5.43 / 6 | 3.79 / 2.79 |
| `orchestrator` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 56.29 | 5.29 / 6 | 1.00 / 5.57 |
| `swarm` | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 / 4.66 |

- **Phân tích lỗi của `swarm`:** Ở claim `C-002` (T02) với `seed = 55` (`seed % 5 == 0`), `swarm` mắc lỗi `REFERENCE_WEAKNESS`: tin vào con số "trễ 5 ngày" trong câu chữ ticket thay vì `delay_days = 2` trong dòng dữ liệu `orders`, dẫn tới bồi hoàn sai 20.000 VND khi lẽ ra phải `denied`.
- **Kiểm thử an toàn & độ bền:**
  - Cổng host (`python -m pytest -q`): **54 passed**.
  - Bộ test student (`python -m pytest -q -m student -o addopts=`): **264 passed** (bao gồm toàn bộ ma trận T01–T14 và 16 test bổ sung kiểm tra claim lạ, lỗi nội bộ, lỗi mở DB, xung đột số tiền khi gọi lại và chống rò rỉ secret/PII).
  - Crash suite (`src/reports/crash.json`): **`20/20`** (`crash_safety = "20/20"`).
- **Quyết định kiến trúc:** Chọn **`workflow`** vì đạt độ chính xác tuyệt đối trên bộ public (`pass_rate = 1.000`, `pass^5 = 1.000`, `variance = 0`) với chi phí thấp nhất (`27.86 VND`). Chi tiết lập luận ghi tại [`report/team/decision_adr.md`](decision_adr.md) và [`report/team/research_card.md`](research_card.md).

## 5. Khó khăn và cách xử lý

- **Sự cố alias `python.exe` trên Windows:** Lệnh `python` mặc định bị Windows App Execution Alias chặn trong môi trường chạy. Nhóm xử lý bằng cách tạo môi trường ảo `.venv` trực tiếp từ bộ cài Python 3.13 (`C:\Users\Legion\AppData\Local\Programs\Python\Python313\python.exe -m venv .venv`) và gọi qua `.venv\Scripts\python.exe`.
- **Bảo toàn hợp đồng Trace khi xảy ra lỗi bất ngờ hoặc Crash:** Nếu DB không mở được hoặc công cụ đọc gặp lỗi nội bộ, việc ném thẳng exception sẽ làm trial bị chấm `exception:...` hoặc `missing_trace`. Nhóm bổ sung cơ chế xử lý an toàn trong cả ba shape: luôn khởi tạo và flush `Trace` hợp lệ trước khi trả về `RunResult(status="failed", error_reason="internal_error")`, đồng thời không ghi chuỗi message của exception nội bộ vào trace để tránh vô tình làm lộ dữ liệu nhạy cảm.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp được kê khai trong [`TEAM.md`](../../TEAM.md) và báo cáo cá nhân [`report/team/2A202603922_NguyenTienDat.md`](2A202603922_NguyenTienDat.md).

## 7. Hạn chế và hướng cải thiện

- `MockLLM` và bảng giá trong `config/pricing.yaml` chỉ là mô phỏng tất định theo seed, không đo được độ trễ thực tế (`latency: unavailable`) hay hiện tượng suy giảm chất lượng prompt trên model thật.
- Bộ dữ liệu public chỉ gồm 14 kịch bản chuẩn hóa; cần chạy thêm trên bộ chấm ẩn (40 claim × 5 seed) của giảng viên để kiểm chứng toàn diện khả năng tổng quát hóa.

## 8. Tài liệu tham khảo

- Tài liệu nội bộ repo: [`docs/business_rules.md`](../../docs/business_rules.md), [`docs/contracts.md`](../../docs/contracts.md), [`docs/architecture.md`](../../docs/architecture.md), [`docs/metrics.md`](../../docs/metrics.md).
- Zhang et al. (2026), *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026: https://aclanthology.org/2026.emnlp-main.798/.
