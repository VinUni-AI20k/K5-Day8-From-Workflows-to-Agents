# Báo cáo cá nhân - Nguyễn Trường Duy

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trường Duy
- MSSV: 2A202603589
- Email: ntduy279@gmail.com
- GitHub: https://github.com/Dizo279

## 2. Phần việc phụ trách

Phụ trách Shape B - single ReAct agent:

- Hoàn thiện `src/lab8/shapes/single.py` theo contract `run_claim`.
- Bảo đảm agent chỉ dùng read-only tools; quote tiền do `compute_compensation` tính và host là nơi duy nhất gọi `issue_refund`.
- Truyền `crash_at` xuống durability để kiểm tra retry/idempotency.
- Thêm test contract tập trung cho single trong `src/tests/test_single_shape.py`.
- Cập nhật ADR/research card và ghi nhận số liệu benchmark cho quyết định kiến trúc.

## 3. Đóng góp cụ thể

Commit chính: `67a3a24` - `feat: update single ReAct shape implementation and add focused contract tests`.

Các đóng góp kỹ thuật:

- Xây dựng vòng ReAct giới hạn 8 bước, lần lượt đọc claim, order, policy, refund history rồi gọi `compute_compensation`.
- Không đưa ticket/raw claim/order vào prompt hoặc trace; trace chỉ ghi các summary đã allowlist.
- Không để model tự chọn số tiền hoặc gọi tool ghi tiền; truyền full quote cho host để host kiểm tra approval, idempotency và cap theo order.
- Xử lý các kết quả `resolved`, `denied`, `needs_info`, `escalated` và `failed` bằng `lab8.shapes.common.finish()`.
- Test ba nhóm rủi ro chính: không tin ticket thay cho order (`C-002`, seed 55), truyền full quote để host áp cap (`C-014`) và crash/retry không tạo refund kép (`C-012`).

## 4. Bằng chứng

- Commit: `67a3a24e5df0766f7b4169da318c030637efb865`.
- Test: `src/tests/test_single_shape.py`.
- Benchmark: `src/reports/benchmark.json`, các run single có dạng `R-single-C-001-s11`.
- Single đạt `70/70` trial hợp lệ trên 14 claim x 5 seed; `pass_rate = 1.000`, `pass^5 = 1.000`, seed min-max `1.000-1.000`, variance `0.000000`.
- Chi phí mô phỏng: `47.852857 VND/success` (xấp xỉ `47.85`), trung bình `8.5` bước, `5.5` model calls và `4.5` tool calls mỗi trial.
- Crash suite chung: `20/20` trong `src/reports/crash.json`; test single riêng chứng minh crash sau effect trước checkpoint retry vẫn chỉ có một dòng ledger.
- Run tiêu biểu: `R-single-C-002-s55` bị deny đúng vì quote dựa trên order là 0, không tin số ngày trong ticket; `R-single-C-014-s11` có proposal `150000` nhưng effect thực tế `120000` do host áp cap theo order.

## 5. Công cụ AI đã dùng

Đã dùng Codex/AI để đọc cấu trúc repo, rà contract, gợi ý các trường hợp test và hỗ trợ diễn giải số liệu. AI không được dùng để sinh hoặc sửa benchmark, run id, commit hash hay kết quả đánh giá.

Tự kiểm tra bằng cách đối chiếu code với `docs/contracts.md`, `docs/business_rules.md`, đọc diff của commit, kiểm tra test source và đối chiếu số liệu trong `src/reports/benchmark.json`/`crash.json`. Các quyết định về quote, approval, cap, idempotency và dữ liệu trace đều được kiểm chứng từ code host và test contract.

## 6. Tự đánh giá

Phần single đạt mục tiêu public benchmark và giữ đúng ranh giới tin cậy: model điều phối các bước đọc, còn code/host quyết định tiền và ghi ledger. Điểm mạnh là flow xác định, dễ kiểm thử, không phụ thuộc ticket text và an toàn khi retry/crash.

Hạn chế là single tốn chi phí mô phỏng cao hơn workflow (`47.85` so với `27.86` VND/success) vì có thêm model calls, trong khi bộ public chưa cho thấy lợi ích pass-rate. Benchmark dùng MockLLM và 14 claim synthetic nên chưa đủ để kết luận cho production; hidden benchmark và latency thực tế cần được đánh giá thêm.
