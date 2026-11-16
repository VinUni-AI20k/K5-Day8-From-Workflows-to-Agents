# Báo cáo cá nhân — Trương Văn Thông

## 1. Thông tin thành viên

- Họ tên: Trương Văn Thông
- MSSV: 2A202603560
- Lớp: L3A
- Email: 
- GitHub: 

## 2. Phần việc phụ trách

- Shape C: orchestrator và investigator chỉ đọc, tại [orchestrator.py](../../src/lab8/shapes/orchestrator.py).
- Handoff theo allowlist, trace đúng contract và tách quyền đọc của investigator khỏi quyền yêu cầu ghi refund của orchestrator.
- Kiểm tra retry, crash/resume và trường hợp claim không tồn tại bằng [test_orchestrator.py](../../src/tests/test_orchestrator.py).
- Chạy kiểm tra public và đối chiếu số liệu orchestrator trong báo cáo benchmark do công cụ của lab sinh ra.

## 3. Đóng góp cụ thể

Phần việc dưới đây được triển khai với sự hỗ trợ của Codex; không khai nhận là code viết độc lập không dùng AI.

### Triển khai orchestrator

- Giữ nguyên chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.
- Đọc claim bằng `get_claim_view`; trả `failed` với `unknown_claim` nếu không tìm thấy claim và `needs_info` nếu thiếu `order_id`.
- Dựng handoff bằng `make_handoff`, không đưa nguyên claim, ticket, parent secret hoặc header vào handoff.
- Chỉ cấp cho investigator các tool `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation` và gọi qua `run_readonly_investigators`.
- Trả `escalated` khi order không tồn tại hoặc principal không sở hữu order.
- Lấy quote từ `compute_compensation` dựa trên order có cấu trúc và policy hợp lệ. Không dùng số ngày trong ticket để thay dữ kiện của order; MockLLM không tính tiền.
- Khi quote bằng 0, trả `denied`. Khi quote dương, truyền nguyên quote vào `issue_refund` để host kiểm approval, trần hoàn tiền theo đơn và chống ghi trùng.
- Không tự trừ khoản đã hoàn trước đó. T13 phải bị host từ chối khi đã hoàn đủ; T14 giữ proposal 150.000 VND và host chỉ ghi phần chênh 120.000 VND.
- Ánh xạ kết quả host thành `resolved`, `denied` hoặc `failed` khi có conflict; dựng mọi kết quả trả về bằng `finish()`.
- Truyền `crash_at` vào `issue_refund`, để `InjectedCrash` truyền ra ngoài; đóng connection trong `finally`.
- Ghi các event `claim`, `handoff`, `investigator`, `quote`, `refund_request`, `decision` theo nhánh thực thi. Không ghi nguyên claim/order row, ticket, secret, header hay thông tin cá nhân.
- Ghi nhận chi phí bằng `Budget`; MockLLM chỉ hỗ trợ điều tra và soạn chữ, không có quyền ghi tiền hoặc tạo approval.

### Test bổ sung

| Test | Nội dung kiểm tra |
| --- | --- |
| `test_orchestrator_resumes_each_crash_window[before_effect]` | Chưa có refund trước resume; sau resume đúng một refund, một audit committed và một checkpoint |
| `test_orchestrator_resumes_each_crash_window[after_effect_before_checkpoint]` | Đã ghi refund trước crash; resume không ghi trùng |
| `test_orchestrator_resumes_each_crash_window[after_checkpoint]` | Crash sau checkpoint; resume giữ nguyên một refund |
| `test_orchestrator_unknown_claim_returns_fresh_trace` | Claim không tồn tại trả `failed`, proposal 0, không refund và có trace mới đúng contract |

### Commit kỹ thuật

- Chưa có commit cá nhân cho phần việc này trong lịch sử hiện tại; `orchestrator.py` đang sửa và `test_orchestrator.py` chưa được commit.
- Chưa có link commit cá nhân để dẫn chứng. Cần bổ sung hash thực sau khi commit các thay đổi; không dùng hash của starter làm bằng chứng đóng góp.

## 4. Bằng chứng

### Kết quả kiểm tra

| Kiểm tra | Kết quả đã ghi nhận |
| --- | --- |
| Smoke | `lab8.smoke pass` |
| Test host sau khi thêm test orchestrator | `58 passed, 248 deselected` |
| Ma trận student riêng orchestrator | `62 passed, 244 deselected` |
| Claim `C-001`, seed 11 | `resolved`, proposal 35.000 VND, một refund 35.000 VND và một audit committed |
| Claim `C-012`, crash sau effect trước checkpoint, rồi resume | Crash được kích hoạt; resume `resolved`, một refund 35.000 VND và một audit committed |
| Crash suite chuẩn của host | `20/20`, xem [crash.json](../../src/reports/crash.json) |

Crash suite chuẩn kiểm host và một kịch bản swarm; bằng chứng crash riêng orchestrator là T12 và ba trường hợp trong `test_orchestrator.py`.

Run id dẫn chứng: `R-orchestrator-C-001-s11`, `R-orchestrator-C-012-s11`. Trace được sinh trong `src/traces/`, không đưa vào git theo quy định.

### Số liệu trong file benchmark hiện có

Nguồn: mục `by_shape.orchestrator` của [benchmark.json](../../src/reports/benchmark.json), trên 14 public claim với seed `11,22,33,44,55`, cùng MockLLM và bảng giá mô phỏng.

| Chỉ số | Giá trị |
| --- | --- |
| Trial pass | 70/70 |
| Pass rate | 1,0 |
| Pass^5 | 1,0 |
| Seed min–max | 1,0–1,0 |
| Seed variance | 0,0 |
| Cost/success | 57,27142857142857 VND mô phỏng |
| Mean / p95 steps | 6,0 / 7,0 |
| Latency | `unavailable` |

Đây là số liệu của file benchmark đã sinh trong phiên làm việc, chưa gắn với commit cá nhân. Cần chạy lại benchmark sau mọi thay đổi code hoặc trace trước khi chốt bài nộp. Chưa có kết quả hidden, không suy rộng kết quả public thành kết quả hidden.

### Lệnh tái lập

Chạy trong PowerShell tại thư mục `src/`. Tạo đường dẫn tạm mới mỗi lần chạy test để tránh lỗi quyền truy cập `pytest-of-Thong` trên Windows.

```powershell
$personalTestTemp = Join-Path $PWD.Path (".venv\pytest-personal-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -k orchestrator --basetemp="$personalTestTemp" -p no:cacheprovider
$personalTestTemp = Join-Path $PWD.Path (".venv\pytest-personal-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -m pytest -q --basetemp="$personalTestTemp" -p no:cacheprovider
```

Lệnh sinh bằng chứng benchmark và crash theo README, chạy trong `src/`:

```powershell
.\.venv\Scripts\python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json
```

Tài liệu đối chiếu: [README](../../README.md), [luật nghiệp vụ](../../docs/business_rules.md), [output và trace contract](../../docs/contracts.md), [kiến trúc](../../docs/architecture.md), [metric](../../docs/metrics.md), [quy định dùng AI](../../RULES.md).

## 5. Công cụ AI đã dùng

- Công cụ: Codex trong phiên làm việc này.
- Phạm vi hỗ trợ: đọc README và checkpoint, hướng dẫn thiết lập môi trường, phân tích lỗi pytest, triển khai orchestrator, thêm test crash/claim không tồn tại, chạy các kiểm tra và soạn báo cáo cá nhân từ bằng chứng thực tế.
- Phần kiểm tra đã tự chạy trong quá trình trao đổi: smoke, test host và ma trận student ở trạng thái starter; kết quả đã được gửi lại trong hội thoại. Test host ban đầu đạt `54 passed`; ma trận student starter đúng trạng thái dự kiến.
- Sau triển khai, Codex đã chạy test host, ma trận orchestrator, claim mẫu, crash/resume, crash suite và benchmark. Kết quả của các lần chạy này được ghi riêng ở mục 4; chưa xác nhận thành viên đã tự chạy lại toàn bộ sau triển khai.
- Lỗi thực tế: `PermissionError: [WinError 5]` khi pytest truy cập thư mục tạm `pytest-of-Thong`. Cách xử lý đã thành công: cấp đường dẫn mới bằng `--basetemp` và tắt cache bằng `-p no:cacheprovider`; thành viên đã gửi lại kết quả `54 passed, 248 deselected` sau xử lý.
- Không dùng API key hoặc model thật trong code lab; các lời gọi model đi qua MockLLM có seed. Không sửa tay JSON báo cáo.

## 6. Tự đánh giá

Chưa có nội dung tự đánh giá do Trương Văn Thông cung cấp. Thành viên tự bổ sung mức độ hiểu và phần việc thực sự tự thực hiện, các điểm còn cần luyện tập, cùng giới hạn của việc dùng AI; không tự tạo nhận xét hoặc tự chấm điểm thay thành viên.
