# Báo cáo cá nhân — Ngô Văn Tuân

## 1. Thông tin thành viên

- Họ tên: Ngô Văn Tuân
- MSSV: 2A202603630
- Email: 26ai.tuannv3@vinuni.edu.vn
- GitHub/repo nhóm: https://github.com/Monstucture/K5-L3A-DAY08-MID-FromWorkflowsToAgents

## 2. Phần việc phụ trách

- Ledger/crash và evaluation: bổ sung test tích hợp cho ba shape workflow, single và orchestrator.
- Kiểm tra refund phần chênh lệch sau crash và retry nhiều lần, đối chiếu kết quả shape với ledger, audit và checkpoint SQLite.

## 3. Đóng góp cụ thể

- Commit kỹ thuật: `de10b6ac250e56edc6308b2c37f49ac7934029d5` — `test: cover top-up refund crash recovery and repeated retries`.
- File thêm: [test_refund_crash_recovery.py](../../src/tests/test_refund_crash_recovery.py).
- Test: `test_topup_crash_and_repeated_retries_keep_one_refund`.
- Chín trường hợp: ba shape × ba điểm crash `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`.
- Sử dụng C-014/O-515: đơn đã được hoàn 30.000 VND, quote đầy đủ là 150.000 VND, refund mới chỉ được bằng 120.000 VND.
- Kiểm tra trạng thái đã lưu ngay sau crash bằng connection mới; sau đó retry với seed `11`, `22`, `55` trên cùng database.
- Sau mỗi retry, kiểm tra tổng hoàn theo đơn vẫn bằng 150.000 VND, lịch sử có đúng hai dòng (refund cũ và refund mới), claim C-014 có đúng một refund và một audit `refund_committed`; checkpoint lưu 120.000 VND.
- Giữ nguyên code shape, host, policy, config và data; chỉ thêm file test.
- Đóng góp tiếp theo ở commit `b3f45ba`: thêm variant research `swarm_no_peer`, 5 test kiểm tra ablation và report JSON do benchmark sinh ra. Variant tắt riêng peer acknowledgement; reference chính thức giữ nguyên.
- Tổng hợp bảng đóng góp, báo cáo nhóm, ADR chọn workflow và research card R2 từ số liệu public thực tế; ghi rõ phần còn thiếu của các thành viên.

## 4. Bằng chứng

Branch thực hiện: `feature/tuan-evaluation-report`.

Các lệnh đã được Codex chạy trong thư mục `src/` sau khi thêm test:

```powershell
python -m pytest -q -p no:cacheprovider -m student -o addopts= tests/test_refund_crash_recovery.py
```

Kết quả: `9 passed`.

```powershell
python -m pytest -q -p no:cacheprovider -o addopts=
```

Kết quả: `311 passed`, gồm toàn bộ host và student, có chín trường hợp mới.

Sau khi bổ sung ablation ở commit `b3f45ba`, chạy lại cùng lệnh toàn bộ đạt `316 passed`. Benchmark chính thức và crash suite được chạy lại, khớp JSON đã có; crash safety `20/20`. Ablation có 140 trial trong [research_peer_ablation.json](../../src/reports/research_peer_ablation.json): pass rate hai nhánh cùng 69/70, cost/success giảm 49,566957 → 48,691594 VND mô phỏng khi tắt peer.

Test gắn marker `student` vì gọi trực tiếp ba shape do nhóm triển khai. Dùng `-p no:cacheprovider` để tránh warning quyền ghi pytest cache trên máy Windows; tùy chọn này không thay đổi assertion của test.

## 5. Công cụ AI đã dùng

- Codex: hỗ trợ đọc yêu cầu lab, phân tích khoảng trống kiểm thử, viết test, chạy pytest và tổng hợp bằng chứng.
- Cách kiểm chứng đã thực hiện với hỗ trợ của Codex: đối chiếu luật hoàn phần chênh lệch trong [business_rules.md](../../docs/business_rules.md), kiểm tra trực tiếp SQLite bằng connection mới, chạy test mới rồi chạy toàn bộ bộ test; rà diff trước khi commit.
- Số liệu trên lấy từ output pytest thực tế trong phiên làm việc, không suy ra từ kết quả MockLLM hoặc sửa tay report JSON.

## 6. Tự đánh giá

- Bằng chứng hoàn thành phần kỹ thuật: hai commit `de10b6a`, `b3f45ba`, tổng cộng 14 trường hợp test thêm và toàn bộ 316 test pass tại commit `b3f45ba`.
- Phạm vi kiểm chứng: dữ liệu public, ba shape A/B/C, ba điểm crash định sẵn và ba seed retry. Kết quả này chưa chứng minh tính đúng trên toàn bộ hidden dataset hoặc khi nhiều process ghi đồng thời.
- Test mô phỏng crash bằng `InjectedCrash`, không mô phỏng mất điện hay lỗi hệ điều hành. MockLLM không đại diện cho model production; không suy ra latency thực tế từ kết quả này.
