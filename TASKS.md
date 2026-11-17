# Phân công nhóm — Lab 8 LogiX-VN

Đề bài: [README.md](README.md). Lịch checkpoint: [CHECKPOINTS.md](CHECKPOINTS.md). Cách chấm: [RUBRIC.md](RUBRIC.md). Cách nộp: [SUBMISSION.md](SUBMISSION.md). Luật: [RULES.md](RULES.md).

## Nguyên tắc chung (cả nhóm đọc trước)

1. **Làm song song, không chờ nhau.** Việc của 4 thành viên chỉ đụng tới shape của chính mình hoặc phần có sẵn trong starter (host, swarm). Không ai phải chờ code của người khác mới bắt đầu, viết test hay chạy test được. Chỉ phần tích hợp cuối buổi của Lead (benchmark 4 shape, ADR, báo cáo nhóm) chạy sau khi các PR đã merge.
2. **Mỗi file chỉ có một chủ.** Chỉ sửa file trong cột "File sở hữu" của mình. Không ai sửa file shape của người khác.
3. **Test của mỗi người chỉ chạy trên phần của người đó.** Test shape chỉ gọi shape của mình (`SHAPES["workflow"]`, ...), không parametrize sang shape khác. Nhờ vậy test của bạn xanh hay đỏ không phụ thuộc người khác.
4. **Không ai sửa file thước đo:** `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*`, `src/data/*`, `src/grader_audit/*`. Không sửa tay JSON trong `src/reports/`.
5. **Mỗi người làm trên nhánh riêng** (tên nhánh = GitHub username), mở PR vào `main`, Lead review và merge. Không push thẳng `main`, không force-push.
6. **Mỗi người phải có:** ít nhất một commit kỹ thuật có nội dung, ít nhất một **file test riêng** trong `src/tests/` (rubric C8), và một báo cáo cá nhân `report/team/<MSSV>_<HoTenKhongDau>.md` (copy từ `report/team/MSSV_HoTen.md`, **không sửa file mẫu**).
7. Trước khi mở PR, chạy trong `src/`: `python -m pytest -q` phải xanh (không có dòng `failed`).
8. File chung (`TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`) chỉ Lead sửa. Thành viên gửi thông tin (MSSV, email, commit hash, tên test, số liệu, đoạn mô tả phần mình) cho Lead qua chat hoặc comment PR.

## Tổng quan

| Người | GitHub | Vai | File sở hữu | Phụ thuộc ai |
| --- | --- | --- | --- | --- |
| doanxuanduybao (Lead) | doanxuanduybao | Việc chung: repo, review/merge, tích hợp, benchmark 4 shape, ADR, báo cáo nhóm, nộp bài | `TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`, `src/reports/benchmark.json`, `src/reports/hidden_selfcheck.json`, `src/tests/test_team_integration.py` | Phần tích hợp cuối buổi chạy sau khi merge |
| Nguyen Dinh Vu Hai | HaiVuuu | Shape A workflow, end-to-end | `src/lab8/shapes/workflow.py`, `src/tests/test_team_workflow.py` | Không |
| HungVT01 | hungvueducation-hash | Shape B single agent, end-to-end | `src/lab8/shapes/single.py`, `src/tests/test_team_single.py` | Không |
| Nguyen Dinh Minh | minhh25 | Shape C orchestrator + handoff, end-to-end | `src/lab8/shapes/orchestrator.py`, `src/tests/test_team_orchestrator.py` | Không |
| QDat18 | QDat18 | Safety của host + crash suite + research card/ablation | `src/tests/test_team_host_safety.py`, `src/reports/crash.json`, `report/team/research_card.md`, `src/bonus/` (biến thể cho ablation) | Không |

"End-to-end" nghĩa là chủ shape tự làm đủ CP2, CP3, CP4 cho shape mình: logic, idempotency, crash, approval, secret, trace. Không chờ ai rà hộ.

`crash.json` không phụ thuộc shape của nhóm: `python -m lab8.crash_test` chỉ kiểm host và swarm có sẵn (xem `src/lab8/crash_test.py`), nên QDat sinh được ngay từ đầu buổi.

## Thứ tự làm

| Mốc | Hai, Hưng, Minh (song song) | QDat (song song) | Lead |
| --- | --- | --- | --- |
| CP1 (13:30) | Cài môi trường, đọc docs, gửi thông tin cho Lead | Cài môi trường, đọc docs, gửi thông tin cho Lead | Setup repo, mời thành viên, điền `TEAM.md` |
| CP2 (13:45) | Viết shape của mình, qua 62 test student của shape đó | Viết test host safety, sinh `crash.json` | Review/merge PR đến trước |
| CP3 (14:30) | `crash_at`, T11, T12 xanh trên shape mình | Chọn câu R1–R4, viết biến thể ablation trong `src/bonus/` | Review/merge |
| CP4 (15:30) | Rà approval, secret, PII, trace trên shape mình; viết test riêng | Chạy ablation, điền research card | Review/merge |
| CP5 (16:15) | Gửi Lead đoạn mô tả shape + số tự đo | Gửi Lead số crash + kết quả ablation | Tích hợp: benchmark 4 shape, hidden selfcheck, chọn shape, ADR, báo cáo |
| Trước deadline | Báo cáo cá nhân, nộp LMS | Báo cáo cá nhân, nộp LMS | `check_submission` `0 FAIL`, push, nhắc nộp LMS |

---

## doanxuanduybao — Lead (việc chung + tích hợp)

**Đọc:** [README.md](README.md), [CHECKPOINTS.md](CHECKPOINTS.md), [RUBRIC.md](RUBRIC.md), [SUBMISSION.md](SUBMISSION.md), [RULES.md](RULES.md), [docs/metrics.md](docs/metrics.md), [docs/architecture.md](docs/architecture.md), [src/reports/README.md](src/reports/README.md), [src/README.md](src/README.md#tự-kiểm-trên-bộ-hidden-cp5), [report/team/README.md](report/team/README.md), [report/team/decision_adr.md](report/team/decision_adr.md), [report/team/group_report.md](report/team/group_report.md).

**Checklist**

- [ ] CP1: cài môi trường, `python -m lab8.smoke` pass, `python -m pytest -q` ra `52 passed`.
- [ ] CP1: repo đặt tên theo mẫu `K5-L3A-DAY08-TenNhom-FromWorkflowsToAgents` ([SUBMISSION.md](SUBMISSION.md#tạo-repo-nhóm)); mời 4 thành viên làm collaborator; mời giảng viên vào repo (hoặc để public).
- [ ] CP1: điền "Thông tin nhóm" và "Thành viên" trong `TEAM.md`.
- [ ] Suốt buổi: theo dõi tiến độ theo checkpoint, gỡ chỗ bị chặn, nhắc ai trễ.
- [ ] CP2–CP4: review và merge PR theo thứ tự đến. Trước khi merge: `python -m pytest -q` xanh; PR shape thì thêm `python -m pytest -q -m student -o addopts= -k <shape>` ra 62 passed.
- [ ] Tích hợp (sau khi 3 shape đã merge): viết `src/tests/test_team_integration.py` chạy cả 3 shape trên cùng claim `C-001` seed 11, kiểm cùng `status` và cùng số tiền refund; chạy `python -m pytest -q -m student -o addopts=` không còn fail ở 3 shape nhóm.
- [ ] Tích hợp: chạy benchmark trên `main` mới nhất và commit `src/reports/benchmark.json`:
  `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- [ ] Tích hợp (khi giảng viên phát `student_drop/`): tự kiểm hidden theo [src/README.md](src/README.md#tự-kiểm-trên-bộ-hidden-cp5), commit `src/reports/hidden_selfcheck.json`.
- [ ] Tổ chức cả nhóm chọn shape theo số đo (tiêu chí ở [docs/metrics.md](docs/metrics.md#quyết-định-kiến-trúc)).
- [ ] Điền `report/team/decision_adr.md`: giữ nguyên các dòng nhãn; commit trước, lấy `git rev-parse --short HEAD` và run id ghi vào ADR, rồi commit tiếp ([SUBMISSION.md](SUBMISSION.md#thứ-tự-nộp)).
- [ ] Viết `report/team/group_report.md` (≤ 5 trang): mục 3 từ đoạn mô tả của Hai, Hưng, Minh; mục 4 từ `benchmark.json`, `crash.json`, research card; mục 5 gom khó khăn cả nhóm.
- [ ] Điền "Bảng đóng góp" trong `TEAM.md` (mỗi người một dòng: commit + file test), giữ nguyên tiêu đề và cột.
- [ ] Chạy `python -m lab8.check_submission` ra `0 FAIL`, đi hết checklist nộp ở cuối file, rồi push.
- [ ] Nhắc cả nhóm nộp link repo trên LMS. Viết báo cáo cá nhân.

**Deliver:** `TEAM.md`, `report/team/group_report.md`, `report/team/decision_adr.md`, `src/reports/benchmark.json`, `src/reports/hidden_selfcheck.json` (nếu có `student_drop/`), `src/tests/test_team_integration.py`, `main` sạch với `check_submission` `0 FAIL`, báo cáo cá nhân.

---

## Nguyen Dinh Vu Hai (HaiVuuu) — Shape A: workflow

**Đọc:** docstring đầu file [src/lab8/shapes/workflow.py](src/lab8/shapes/workflow.py), [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), [docs/architecture.md](docs/architecture.md), [RULES.md](RULES.md#secret-và-api-key), `src/lab8/shapes/swarm_reference.py` (tham khảo cấu trúc, **không copy khối `REFERENCE_WEAKNESS`**), `src/lab8/tools.py`, `src/lab8/durability.py`, `src/lab8/trace.py`, `src/lab8/shapes/common.py`, `src/tests/test_trace_contract.py`, [src/README.md](src/README.md#đọc-khi-bắt-đầu-viết-shape-cp2).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2` theo 8 bước trong docstring: đọc claim bằng `get_claim_view`; thiếu `order_id` → `needs_info`; không thấy đơn → `escalated`; quote bằng `compute_compensation` từ order row (bỏ qua số trong ticket); quote 0 → `denied`; quote > 0 → `durability.issue_refund` với **quote đầy đủ**.
- [ ] Trả kết quả bằng `lab8.shapes.common.finish()`; ghi trace ở **mọi** nhánh return (dùng `lab8.trace.Trace`).
- [ ] CP3: ở `TODO CP3`, truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] CP4: rà trace và stdout của workflow: không có phone, địa chỉ, tên hàng, internal note, `parent_secret`, `CANARY_SECRET_*`, claim row/order row thô ([docs/contracts.md](docs/contracts.md#trace-contract-v1)).
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k workflow` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_workflow.py`, **chỉ gọi workflow**, ít nhất 3 test: ticket ghi "trễ 9 ngày" nhưng order ghi 2 ngày → `denied`; crash `after_effect_before_checkpoint` rồi chạy lại cùng DB → 1 dòng ledger, 1 audit `refund_committed`; trace có `run_id` khớp và không chứa `CANARY_SECRET_`.
- [ ] Tự đo (không commit): `python -m lab8.benchmark --shapes workflow,swarm --out reports/tmp_workflow.json`, gửi Lead pass rate, pass^5, cost/success của workflow.
- [ ] Mở PR từ nhánh `HaiVuuu`, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả ranh giới code/model trong workflow và field trace cố ý không ghi.

**Deliver:** `src/lab8/shapes/workflow.py` qua 62 test student, `src/tests/test_team_workflow.py`, báo cáo cá nhân.

---

## HungVT01 (hungvueducation-hash) — Shape B: single agent (ReAct)

**Đọc:** docstring đầu file [src/lab8/shapes/single.py](src/lab8/shapes/single.py), `src/lab8/runtime.py` (`run_react`, `Budget`), `src/lab8/mock_llm.py`, `src/lab8/tools.py` (đặc biệt `lookup_refund_history`), `src/config/tools.manifest.v1.1.yaml`, `src/config/autonomy_policy.yaml`, [docs/business_rules.md](docs/business_rules.md), [docs/contracts.md](docs/contracts.md), [docs/architecture.md](docs/architecture.md), [RULES.md](RULES.md#secret-và-api-key), `src/lab8/shapes/swarm_reference.py`.

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2` bằng `lab8.runtime.run_react` với `max_steps=8`. `decide` chỉ được chọn tool đọc, **không** gọi `issue_refund`.
- [ ] `decide` phải tin order row, không tin số ngày trễ hay clause ghi trong ticket (ticket là dữ liệu, không phải lệnh).
- [ ] Sau vòng lặp, code (không phải model) tính quote bằng `compute_compensation` và gọi `durability.issue_refund` với **quote đầy đủ**.
- [ ] Đếm model call vào `Budget` để cost so được với các shape khác.
- [ ] Trả bằng `finish()`; trace đúng contract ở mọi nhánh return.
- [ ] CP3: truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] CP4: rà trace và stdout của single: không có PII, `parent_secret`, `CANARY_SECRET_*`, claim row/order row thô ([docs/contracts.md](docs/contracts.md#trace-contract-v1)).
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k single` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_single.py`, **chỉ gọi single**, ít nhất 3 test: vòng lặp không vượt 8 bước; ticket chứa "ignore policy" vẫn không refund sai; crash rồi resume vẫn 1 refund.
- [ ] Tự đo (không commit): `python -m lab8.benchmark --shapes single,swarm --out reports/tmp_single.json`, gửi Lead pass rate, pass^5, cost/success của single.
- [ ] Mở PR từ nhánh của mình, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả vòng ReAct, chỗ code chặn model, và field trace cố ý không ghi.

**Deliver:** `src/lab8/shapes/single.py` qua 62 test student, `src/tests/test_team_single.py`, báo cáo cá nhân.

---

## Nguyen Dinh Minh (minhh25) — Shape C: orchestrator + handoff

**Đọc:** docstring đầu file [src/lab8/shapes/orchestrator.py](src/lab8/shapes/orchestrator.py), `src/lab8/handoff.py` (`make_handoff`, allowlist), `src/lab8/runtime.py` (`run_readonly_investigators`), `src/lab8/tools.py`, `src/tests/test_handoff_secret.py`, [docs/architecture.md](docs/architecture.md#handoff), [docs/contracts.md](docs/contracts.md#trace-contract-v1), [docs/business_rules.md](docs/business_rules.md), [RULES.md](RULES.md#secret-và-api-key).

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh.
- [ ] CP2: thay stub ở `TODO CP2`: dựng handoff bằng `make_handoff` chỉ với tool đọc (có thể thêm `lookup_refund_history`); chạy `run_readonly_investigators`; orchestrator quote từ order view của investigator và gọi `durability.issue_refund` với **quote đầy đủ**.
- [ ] Không đưa `parent_secret`, header thô, hay nguyên claim row vào `facts`. Tóm tắt bằng LLM không tính là sanitize, phải dùng allowlist.
- [ ] Trace ghi handoff **đã sanitize**, không ghi parent context; trace đúng contract ở mọi nhánh return.
- [ ] CP3: truyền `crash_at` vào `durability.issue_refund`; không bắt `InjectedCrash`.
- [ ] CP4: rà trace và stdout của orchestrator: không có PII, `parent_secret`, `CANARY_SECRET_*`, claim row/order row thô.
- [ ] Tự kiểm: `python -m pytest -q -m student -o addopts= -k orchestrator` ra **62 passed**; `python -m pytest -q` xanh.
- [ ] Viết `src/tests/test_team_orchestrator.py`, **chỉ gọi orchestrator**, ít nhất 3 test: handoff không chứa `CANARY_SECRET_` và không có tool ghi; trace không có `parent_secret`; crash rồi resume vẫn 1 refund.
- [ ] Tự đo (không commit): `python -m lab8.benchmark --shapes orchestrator,swarm --out reports/tmp_orchestrator.json`, gửi Lead pass rate, pass^5, cost/success của orchestrator.
- [ ] Mở PR từ nhánh của mình, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân, có 1 đoạn mô tả handoff allowlist, lý do trace không ghi parent context, và field trace cố ý không ghi.

**Deliver:** `src/lab8/shapes/orchestrator.py` qua 62 test student, `src/tests/test_team_orchestrator.py`, báo cáo cá nhân.

---

## QDat18 — Safety của host + crash suite + research card

Toàn bộ việc dưới đây chỉ dùng host và swarm có sẵn trong starter, không cần shape của nhóm.

**Đọc:** [RUBRIC.md](RUBRIC.md#must-pass-không-bù-điểm), [CHECKPOINTS.md](CHECKPOINTS.md) (CP3, CP4), [docs/business_rules.md](docs/business_rules.md), [docs/metrics.md](docs/metrics.md), [docs/bonus_topics.md](docs/bonus_topics.md#chạy-biến-thể-bonus-cạnh-4-shape) (cách chạy `--extra-shape`), [report/team/research_card.md](report/team/research_card.md), `src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/crash_test.py`, `src/lab8/demo/buggy_workflow.py`, `src/lab8/shapes/swarm_reference.py`, `src/tests/test_crash_suite.py`, `src/tests/test_order_cap_and_approval_binding.py`, `src/tests/test_refund_idempotency.py`, `src/tests/test_authorization.py`.

**Checklist**

- [ ] CP1: cài môi trường, smoke pass, cổng host xanh; chạy `python -m lab8.demo.buggy_workflow` để hiểu vì sao checkpoint không thay được ledger.
- [ ] CP2: chạy crash suite và commit `src/reports/crash.json` (phải `crash_safety` = `20/20`):
  `python -m lab8.crash_test --count 20 --out reports/crash.json`
- [ ] CP2: viết `src/tests/test_team_host_safety.py`, gọi thẳng `durability.issue_refund` và `swarm`, ít nhất 4 test cho các ca chưa có trong test sẵn:
  - approval hết hạn / bị thu hồi / của claim khác → không có dòng ledger, có audit `policy_denied`;
  - approval thấp hơn quote → refund `min(quote, approved_vnd, paid_vnd)`;
  - gọi lại cùng claim với amount khác → `conflict`, không sửa số cũ;
  - crash ở `before_effect` và `after_checkpoint` trên swarm rồi resume → đúng 1 refund, 1 audit `refund_committed`.
- [ ] CP3: chọn một câu R1–R4 trong `report/team/research_card.md`. Viết biến thể ablation trong `src/bonus/` (tạo `src/bonus/__init__.py`), chỉ đổi **một** biến so với swarm, ví dụ swarm bỏ khối `REFERENCE_WEAKNESS` (đọc `delay_days` từ order) cho câu R2/R4.
- [ ] CP4: chạy ablation cạnh swarm, cùng claim, seed, giá:
  `python -m lab8.benchmark --shapes swarm,<ten_bien_the> --extra-shape <ten_bien_the>=bonus.<module>:run_claim --seeds 11,22,33,44,55 --out reports/bonus_ablation.json`
- [ ] Điền cột "Nhóm điền" và mục "Kết quả ablation" (lệnh nguyên văn, run id, đúng/sai so với hypothesis, giới hạn MockLLM) trong `report/team/research_card.md`.
- [ ] Gửi Lead: số crash, kết quả ablation, đoạn giải thích cổng duyệt của host chặn gì.
- [ ] Mở PR từ nhánh `QDat18`, gửi Lead commit hash + tên file test.
- [ ] Viết báo cáo cá nhân.

**Deliver:** `src/reports/crash.json` (20/20), `src/tests/test_team_host_safety.py`, biến thể trong `src/bonus/`, `src/reports/bonus_ablation.json`, `report/team/research_card.md` đã điền, báo cáo cá nhân.

---

## Bonus (tùy chọn, chỉ làm khi bài chính xong)

Bonus chỉ tính khi shape chọn qua 3 must-pass và hidden ≥ 0.80 ([docs/bonus_topics.md](docs/bonus_topics.md)). Đề xuất **B7 — Kiểm toán grader**: không đụng shape hay host, chỉ thêm `src/tests/test_bonus_grader_audit.py` và `report/team/bonus_report.md`, nên không conflict và không phụ thuộc ai. Người xong việc sớm nhất nhận, báo Lead trước khi làm.

## Checklist nộp bài (Lead chốt)

- [ ] `python -m pytest -q` xanh.
- [ ] `src/reports/benchmark.json` và `src/reports/crash.json` do công cụ sinh, không sửa tay.
- [ ] ADR có shape chọn, commit hash, run id, số liệu.
- [ ] `research_card.md`, `group_report.md`, `TEAM.md` (bảng đóng góp) đã điền.
- [ ] 5 báo cáo cá nhân `report/team/<MSSV>_<HoTen>.md`.
- [ ] `python -m lab8.check_submission` ra `0 FAIL`.
- [ ] Không commit `traces/`, `*.sqlite`, `student_drop/`, `.venv/`, `.env`, `reports/tmp_*.json`.
- [ ] **Cả 5 người** nộp link repo trên LMS trước deadline.
