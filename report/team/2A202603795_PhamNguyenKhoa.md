# Báo cáo cá nhân — 2A202603795_PhamNguyenKhoa

## 1. Thông tin thành viên

- Họ tên: Phạm Nguyên Khoa
- MSSV: 2A202603795
- Email:
- GitHub: Neronmen

## 2. Phần việc phụ trách

- Integration: tạo repo nhóm, cài môi trường, giữ cổng host (`python -m pytest -q`) xanh suốt buổi.
- Viết ba shape: A `workflow` (`src/lab8/shapes/workflow.py`), B `single` (`src/lab8/shapes/single.py`), C `orchestrator` (`src/lab8/shapes/orchestrator.py`).
- Durability: truyền `crash_at` vào `durability.issue_refund`, không nuốt `InjectedCrash`; chạy crash suite.
- Chạy benchmark 4 shape × 14 claim × 5 seed và commit `src/reports/benchmark.json`, `src/reports/crash.json`.

## 3. Đóng góp cụ thể

- Commit `75ae9e4`: cài đặt ba shape cùng file test `src/tests/test_team_shapes_safety.py`.
- Commit `19cd820`: thêm `src/reports/benchmark.json` và `src/reports/crash.json`, cả hai do `lab8.benchmark` và `lab8.crash_test` sinh ra, không sửa tay.
- Quyết định kỹ thuật:
  - **Tiền do code tính.** Cả ba shape lấy quote từ `compute_compensation` trên view order (`lookup_order`), không đọc số ngày trễ trong ticket. MockLLM chỉ dùng để soạn câu trả lời (`draft`), lập kế hoạch (`plan`) hoặc mô phỏng bước chọn tool (`decide`). Text model trả về không được dùng để quyết định.
  - **Truyền quote đầy đủ** vào `issue_refund`. Host tự trừ phần đã hoàn của đơn (T13, T14). Quote > 0 thì luôn gọi host, để khi host từ chối sẽ có audit `policy_denied`.
  - **Single (ReAct):** observation đưa vào vòng lặp chỉ gồm `claim_id`, `order_id`, `principal_id`, không có ticket. Nhờ vậy chữ trong ticket (kể cả prompt injection) không điều khiển được việc chọn tool. Kế hoạch đọc cố định: `lookup_order` → `lookup_refund_history` → `compute_compensation` → `final`. Tối đa 8 bước. Sau vòng lặp, code mới gọi host.
  - **Orchestrator:** handoff dựng bằng `make_handoff` với `facts={}` và 4 tool chỉ đọc. Investigator tự đọc lại order theo principal. Trace ghi handoff đã sanitize, không ghi parent context. Shape này không có khối `REFERENCE_WEAKNESS`.
  - **Trace:** chỉ ghi `claim_id`/`has_order_id`, view order đã qua allowlist, quote, kết quả từ host và quyết định. Cố ý không ghi ticket, `parent_secret`, raw headers, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.
- Test đã thêm (`src/tests/test_team_shapes_safety.py`, 15 test, chạy trong cổng host):
  - `test_crash_then_resume_pays_exactly_once`: 3 điểm crash × 3 shape. Crash phải xảy ra; resume rồi gọi lại vẫn chỉ một dòng ledger 35.000 và một audit `refund_committed`.
  - `test_ticket_delay_is_ignored_on_seed_55`: T02 ở seed 55 (ticket ghi 5 ngày, order ghi 2 ngày). Ba shape đều phải `denied`, không có refund.
  - `test_trace_and_result_have_no_secret_or_pii`: chạy mọi claim public, quét trace và kết quả để chắc không có `CANARY_SECRET_*`, SĐT, địa chỉ, ghi chú nội bộ, tên hàng.

## 4. Bằng chứng

- `python -m pytest -q`: `69 passed, 248 deselected` (cổng host 54 test + 15 test nhóm).
- `python -m pytest -q -m student -o addopts=`: `248 passed`, tức 4 shape × 62 test T01–T14.
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- `src/reports/benchmark.json` (bộ public, seed 11, 22, 33, 44, 55, chi phí mô phỏng):

| Shape | Pass rate | Pass^5 | Variance | Cost/success (VND) | Mean steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| workflow | 1.000 | 1.000 | 0.000000 | 28.80 | 4.36 |
| single | 1.000 | 1.000 | 0.000000 | 39.08 | 7.86 |
| orchestrator | 1.000 | 1.000 | 0.000000 | 57.14 | 4.36 |
| swarm | 0.986 | 0.929 | 0.000816 | 49.57 | 2.80 |

- Run id ví dụ: `R-workflow-C-014-s11` (T14: quote 150.000, ledger 120.000 sau khi host trừ 30.000 đã hoàn).

## 5. Công cụ AI đã dùng

- Claude Code (Claude): dùng để đọc repo, giải thích contract và luật nghiệp vụ, gợi ý code cho ba shape và test.
- Cách tự kiểm tra:
  - chạy ma trận student (248 passed), cổng host và crash suite;
  - đọc trace sinh ra (ví dụ `traces/R-workflow-C-014-s11.json`) để chắc chỉ có field allowlist;
  - đối chiếu từng nhánh `status`/`proposal_amount` với bảng trong `docs/contracts.md`.
- Số liệu benchmark lấy từ `src/reports/benchmark.json` do công cụ sinh ra, không do AI viết.

## 6. Tự đánh giá

- Làm tốt: ba shape qua đủ T01–T14 trên 5 seed, trace sạch, crash/resume không trả tiền hai lần.
- Hạn chế: chưa tự kiểm trên `student_drop/` (bộ hidden), vì cần giảng viên phát. Benchmark chạy bằng MockLLM nên `single` và `orchestrator` đạt 1.0 nhờ `decide` được viết cố định. Với model thật, hai shape này sẽ có variance.
