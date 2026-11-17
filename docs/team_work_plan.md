# Kế hoạch phân công nhóm 4 người

## 1. Mục tiêu buổi lab

Hoàn thiện ba shape còn thiếu (`workflow`, `single`, `orchestrator`), giữ
host/ledger an toàn, so sánh cả bốn shape bằng cùng claim và seed, sau đó chọn
kiến trúc dựa trên số liệu. Shape được chọn phải đạt:

- Pass rate hidden tối thiểu `0.75` trên `40 claim x 5 seed`.
- Không refund khi approval không hợp lệ.
- Không lộ `CANARY_SECRET_*` hoặc PII trong trace/kết quả.
- Crash suite đạt `20/20` và retry không tạo refund trùng.

Các quy tắc nguồn: [README.md](../README.md), [RUBRIC.md](../RUBRIC.md),
[CHECKPOINTS.md](../CHECKPOINTS.md), [RULES.md](../RULES.md) và
[SUBMISSION.md](../SUBMISSION.md).

## 2. Nguyên tắc phối hợp

1. Cả nhóm cùng đọc [docs/business_rules.md](business_rules.md),
   [docs/contracts.md](contracts.md), [docs/architecture.md](architecture.md)
   trước khi code.
2. Không sửa `metrics.py`, `durability.py`, `policy.py`, `config/`, `data/`
   hoặc sửa tay JSON trong `src/reports/`.
3. Mọi lệnh chạy từ thư mục `src/`; trước và sau mỗi checkpoint chạy
   `python -m pytest -q`.
4. Mỗi thành viên làm ít nhất một commit kỹ thuật có ít nhất một test thêm/sửa;
   ghi commit và test vào bảng đóng góp trong `TEAM.md`.
5. Không tự trừ phần refund đã nhận trước đó: shape luôn truyền **full quote**
   vào `durability.issue_refund`.
6. Không bắt `InjectedCrash`; phải truyền `crash_at` để test resume kiểm tra
   đúng durability.

## 3. Phân công chi tiết

### Thành viên 1 — Workflow và tích hợp chung

**Phụ trách chính**

- Triển khai `src/lab8/shapes/workflow.py` theo các bước trong docstring.
- Đọc claim bằng view an toàn, kiểm tra `order_id`, ownership/order visibility,
  policy hiện hành và tính quote bằng code.
- Gọi `finish()` ở mọi nhánh, kể cả `needs_info`, `escalated`, `denied` và
  `failed`; tạo trace đúng contract.
- Viết hoặc cập nhật test cho workflow và hỗ trợ tích hợp ba shape.

**Đầu ra kiểm chứng**

- `python -m pytest -q -m student -o addopts= -k workflow` đạt đủ test.
- Workflow không tin số ngày trong ticket, không để model quyết tiền.
- Có test cho T01, T02, T03/T04 và các nhánh thiếu order/không sở hữu.
- Commit có nội dung và ít nhất một test được ghi trong `TEAM.md`.

### Thành viên 2 — Single ReAct agent

**Phụ trách chính**

- Triển khai `src/lab8/shapes/single.py` bằng `run_react`, tối đa 8 bước.
- Chỉ cho model chọn tool đọc; model không được gọi `issue_refund`.
- Sau vòng ReAct, code lấy quote từ order/policy và để host kiểm approval,
  idempotency, cap theo order.
- Đảm bảo budget, trace và `crash_at` được truyền đúng.

**Đầu ra kiểm chứng**

- `python -m pytest -q -m student -o addopts= -k single` đạt đủ test.
- Có test chống tin ticket injection/sai delay và giới hạn 8 bước.
- Có test quote đầy đủ cho T13/T14, approval sai và retry.
- Ghi rõ cost/steps của single trong benchmark, không bịa số liệu.

### Thành viên 3 — Orchestrator và handoff

**Phụ trách chính**

- Triển khai `src/lab8/shapes/orchestrator.py`.
- Dùng `make_handoff()` với allowlist; investigator chỉ được dùng read-only
  tools và không nhận `parent_secret`, header, raw claim/order hoặc tool ghi.
- Lấy quote từ dữ liệu investigator đã sanitize; trace chỉ ghi handoff đã
  sanitize và các event hợp lệ.
- Kiểm tra trace contract v1 và các nhánh return sớm.

**Đầu ra kiểm chứng**

- `python -m pytest -q -m student -o addopts= -k orchestrator` đạt đủ test.
- Có test handoff không chứa secret/PII và investigator không có write tool.
- Có test T11/T12, T13/T14 và approval gắn đúng claim.
- Rà soát trace của cả ba shape trước CP4.

### Thành viên 4 — Host safety, crash, benchmark và báo cáo

**Phụ trách chính**

- Không sửa host bị cấm; thay vào đó kiểm thử cách ba shape gọi host:
  `durability.issue_refund`, approval, idempotency và cap theo order.
- Chạy crash suite, retry/resume và rà secret/PII trong trace/kết quả.
- Chạy benchmark 4 shape x 5 seed, tổng hợp metric và giữ lại `run_id`.
- Điều phối hoàn thiện `TEAM.md`, ADR, research card, group report và báo cáo
  cá nhân; chạy `check_submission` trước khi push.

**Đầu ra kiểm chứng**

- `python -m pytest -q` xanh.
- `python -m lab8.crash_test --count 20 --out reports/crash.json` cho `20/20`.
- Benchmark có đủ `workflow,single,orchestrator,swarm`, seed
  `11,22,33,44,55`, tối thiểu 10 claim.
- `decision_adr.md` có shape chọn, commit hash, run id, metric, crash safety,
  secret leak và approval bypass.
- `python -m lab8.check_submission` ra `0 FAIL`.

## 4. Lịch thực hiện theo checkpoint

| Mốc | Công việc chung | Người dẫn dắt | Tiêu chí hoàn thành |
|---|---|---|---|
| CP1, 13:30 | Cài môi trường, chạy smoke/host tests, đọc business rules và contracts, điền vai trong `TEAM.md` | Thành viên 4 | `smoke pass`; `pytest -q` không có failed |
| CP2, 13:45 | Viết ba shape; thống nhất `RunResult`, `finish()`, full quote và trace | Thành viên 1, 2, 3 | Mỗi shape chạy được; test riêng shape không còn stub |
| CP3, 14:30 | Bổ sung `crash_at`, handoff allowlist, retry/idempotency | Thành viên 3, 4 | T11/T12 xanh; host tests vẫn xanh |
| CP4, 15:30 | Kiểm approval, ownership, order cap, trace leak; chạy crash suite | Thành viên 4 | Không bypass approval, không secret leak, crash `20/20` |
| CP5, 16:15 | Benchmark, tự kiểm hidden nếu có, chọn shape bằng số liệu, hoàn thiện báo cáo | Cả nhóm; thành viên 4 tổng hợp | Benchmark hợp lệ, ADR/research/report đầy đủ, `check_submission` `0 FAIL` |

## 5. Quy trình bàn giao và review

1. Thành viên hoàn thành phần mình phải gửi: file đã sửa, lệnh test, kết quả
   và rủi ro còn lại.
2. Thành viên 1 review luồng `workflow` và contract chung; thành viên 2 review
   giới hạn ReAct/budget; thành viên 3 review handoff/trace; thành viên 4
   review durability, benchmark và tiêu chí nộp.
3. Trước khi merge/push, chạy lần lượt:

   ```text
   python -m pytest -q
   python -m pytest -q -m student -o addopts=
   python -m lab8.crash_test --count 20 --out reports/crash.json
   python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
   python -m lab8.check_submission
   ```

4. Chỉ ghi số liệu thật từ `src/reports/` vào
   [report/team/decision_adr.md](../report/team/decision_adr.md) và
   [report/team/group_report.md](../report/team/group_report.md). Không sửa tay
   các file JSON sinh bởi công cụ.

## 6. Checklist nộp bài

- [ ] `TEAM.md` có đủ 4 thành viên, vai trò, commit và test của từng người.
- [ ] Ba shape hoàn chỉnh, không còn `not_implemented`.
- [ ] `python -m pytest -q` xanh; student matrix không còn lỗi của shape nhóm.
- [ ] Crash `20/20`; không bypass approval; không lộ secret/PII.
- [ ] `reports/benchmark.json` và `reports/crash.json` được sinh bằng CLI.
- [ ] `decision_adr.md`, `research_card.md`, `group_report.md` đã điền.
- [ ] Mỗi thành viên có `report/team/MSSV_HoTen.md`.
- [ ] `python -m lab8.check_submission` ra `0 FAIL`.
- [ ] Không commit `.venv/`, `.env`, `*.sqlite`, `traces/` hoặc dữ liệu hidden.
