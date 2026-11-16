# Báo cáo cá nhân — Dau Phuc Duc

## 1. Thông tin thành viên

- Họ tên: Dau Phuc Duc
- MSSV: 2A202603580
- Email: teflon125.work@gmail.com
- GitHub: [dpduc313](https://github.com/dpduc313)
- Vai trò: Workflow + tích hợp (bộ ticket A); bonus B4

## 2. Phần việc phụ trách

- Phân tích đề và chia việc cho nhóm: bộ ticket `tickets/` và 18 GitHub issue có nhãn A–D.
- Shape workflow: viết test riêng và rà lại code workflow. Ba shape do nhóm trưởng cài trong commit `3614266`.
- Rà soát bài trên `main` trước khi nộp: các cổng kiểm, khả năng tái lập số liệu, quét lộ dữ liệu trong trace.
- Ablation một biến cho research card (C6) và bonus B4.

## 3. Đóng góp cụ thể

| Commit / PR | Nội dung |
| --- | --- |
| `885d79a` (nhánh `docs/tickets`) | Bộ ticket: README chung (mốc thời gian, cài đặt, quy ước nhánh/PR, shape, trace) và 4 bộ A–D. Từ bộ này tạo issue #2–#19. |
| `2307509` (PR #20, đã merge) | `src/tests/test_team_workflow.py`, 33 test. (a) Claim T02 (`C-002`: ticket ghi trễ 5 ngày, order ghi 2 ngày) ở cả 5 seed, kể cả seed 55, phải ra `denied` với proposal 0. (b) Trace và kết quả của workflow trên 14 claim public (seed 11 và 55) không chứa secret, header thô, nguyên văn ticket, tên khách, SĐT, địa chỉ, ghi chú nội bộ, tên hàng. |
| `7c40c0a` (PR #21) | `src/bonus/swarm_no_override.py`: swarm bỏ đúng khối tin số ngày trong ticket. Kèm `src/reports/bonus_ablation_no_override.json` và bản sửa research card sang ablation chỉ đổi một biến. |

Quyết định kỹ thuật tôi đưa ra:

- Ablation cũ trong research card so workflow với orchestrator, hai shape khác nhau ở nhiều thứ cùng lúc. Tôi thay bằng swarm so với swarm không ghi đè `delay_days`: giữ nguyên topology và số lời gọi model, chỉ đổi một biến.
- Test (a) chọn đúng ca T02 ở seed 55, vì đây là ca swarm fail theo thiết kế. Chạy test đó với swarm thì đỏ đúng một ca, chứng tỏ test bắt được lỗi tin ticket.
- Bonus B4 dùng chính workflow làm baseline rules-only, vì workflow không gọi model lần nào.

## 4. Bằng chứng

Đã kiểm trên `main` @ `d669b6e` và nhánh `feat/dpduc`, Python 3.11.9:

- `python -m pytest -q`: 87 passed (54 test ban đầu + 33 test của tôi).
- `python -m pytest -q -m student -o addopts=`: 248 passed.
- `python -m lab8.check_submission`: 0 FAIL.
- Chạy lại `lab8.benchmark` (4 shape × 14 claim × 5 seed) và `lab8.crash_test --count 20` ra **trùng khớp** `src/reports/benchmark.json` và `src/reports/crash.json` đã commit (C7).
- Quét 280 file trace sinh ra: 0 lần xuất hiện `CANARY_SECRET_`, `parent_secret`, `raw_headers`, nguyên văn ticket, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.
- Ablation (`src/reports/bonus_ablation_no_override.json`):

  | Shape | Pass rate | pass^5 | Cost/success | Model call/claim |
  | --- | --- | --- | --- | --- |
  | swarm | 0.986 | 0.929 | 49.57 | 3.00 |
  | swarm_no_override | 1.000 | 1.000 | 48.72 | 3.00 |

  Trial khác nhau duy nhất: `R-swarm-C-002-s55` so với `R-swarm_no_override-C-002-s55`. Chạy lại lệnh ra file y hệt.

## 5. Công cụ AI đã dùng

**Claude Code** (model Claude Opus 5.5, trong VS Code). Tôi dùng nó vào các việc sau:

- Đọc đề, đối chiếu rubric, rules và submission, ghi lại yêu cầu cứng và chỗ mâu thuẫn. Ví dụ: `check_submission` chỉ nhận tiêu đề bonus B1–B6 trong khi đề có B7.
- Soạn bộ ticket và script tạo GitHub issue từ ticket.
- Viết `test_team_workflow.py` và `bonus/swarm_no_override.py`.
- Rà soát code 3 shape, chạy các lệnh kiểm, chạy lại benchmark và crash để so với file đã nộp.

Cách tôi tự kiểm:

- Mọi lệnh git và gh (commit, push, PR, tạo và đóng issue) do tôi tự chạy, sau khi đọc lệnh.
- Mọi số trong báo cáo này lấy từ file JSON do `lab8.benchmark` và `lab8.crash_test` sinh ra, không chép tay từ màn hình. Số của benchmark và ablation được chạy hai lần và so sánh bằng máy.


## 6. Tự đánh giá

- **Làm được:** phát hiện bảng đóng góp chưa có test nào được thêm (C8) và research card chưa có ablation một biến (C6), rồi bù cả hai bằng bằng chứng chạy lại được. Xác nhận số liệu nộp bài tái lập được. Chia việc cho nhóm thành ticket và issue có tiêu chí "xong khi" kiểm được.
- **Chưa tốt:** Chưa có demo
- **Còn lại:** bonus B4 (`stats.py`, các biến thể ablation, `bonus_report.md`); sửa dòng secret leak / approval bypass trong ADR thành số; trả cột bảng đóng góp về đúng mẫu.
