# Báo cáo cá nhân — 2A202603422_NguyenTranAnhKhoi

## 1. Thông tin thành viên

- Họ tên: Nguyễn Trần Anh Khôi
- MSSV: 2A202603422
- Email: khoinguyentran1111@gmail.com
- GitHub: khoinguyentran1111. Lưu ý: các commit `ff49706`, `5fb3b5d`, `289c88c`, `3b97524` và các commit khác làm từ máy cá nhân trước khi đổi cấu hình git hiện trên GitHub dưới tài khoản `NTAnhKhoi` (cùng một người, do email trong cấu hình git lúc đó); từ commit sau đó dùng `khoinguyentran1111`.

## 2. Phần việc phụ trách

Ledger + evaluation (nhóm 4 người: workflow + integration; single; orchestrator + handoff; ledger + evaluation).

- Ledger: kiểm tra ba shape nhóm viết dùng cổng host `durability.issue_refund` đúng cách (quote đầy đủ, truyền `crash_at`, không bắt `InjectedCrash`, vẫn gọi host khi quote > 0 để có audit `policy_denied`).
- Evaluation: sinh bằng chứng `src/reports/crash.json`, `src/reports/benchmark.json`; điền `report/team/decision_adr.md`, `report/team/research_card.md` và mục 4 "Kết quả" của `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- Commit `ff49706` — `test: add cross-shape ledger, crash and approval invariant tests`: thêm `src/tests/test_ledger_shapes.py`, 8 hàm test (10 ca mỗi shape) chạy trên cả 4 shape (40 ca). Lúc đầu gắn marker `student` để cổng host không đỏ khi shape còn là stub; sau khi ba shape xong, bỏ marker theo yêu cầu của coach để test chạy trong cổng host `python -m pytest -q`. File bổ sung phần ma trận public chưa phủ:
  - `test_crash_at_every_point_then_resume_pays_once`: crash ở `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`, rồi resume → đúng 1 dòng ledger, 1 audit `refund_committed`, có checkpoint.
  - `test_three_retries_of_a_paying_claim_keep_one_row`, `test_retry_of_an_already_refunded_order_stays_denied`: idempotency khi gọi lại nhiều lần.
  - `test_approval_borrowed_from_another_claim_is_denied`, `test_missing_approval_is_denied_with_audit`, `test_revoked_approval_is_denied_with_audit`: cổng approval, phải có audit `policy_denied` đúng lý do.
  - `test_two_claims_on_one_order_pay_once`: trần theo đơn, claim sau vẫn trả quote đầy đủ.
  - `test_public_corpus_in_one_store_keeps_ledger_invariants`: chạy cả 14 claim trên một DB, kiểm mỗi claim ≤ 1 dòng, key `refund:{claim_id}`, mỗi dòng 1 audit, tổng mỗi đơn ≤ `paid_vnd`, không lộ secret/PII.
- Quyết định kỹ thuật: dùng swarm làm đối chứng trong cùng file (swarm pass 10/10 trước khi các shape khác xong) để chứng minh bản thân test viết đúng; các claim giả lập cho ca approval (`C-L01`…`C-L03`) chèn vào DB tạm của từng test, không sửa `data/`.
- Chạy crash suite và benchmark bằng đúng lệnh chính thức; đề xuất chọn `workflow` dựa trên số đo (pass ngang single/orchestrator, ít tự chủ nhất, cost/success thấp nhất); ablation R1 single → orchestrator trong research card.

## 4. Bằng chứng

- Commit test: https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/ff49706
- `python -m pytest -q tests/test_ledger_shapes.py`: 40 passed sau khi ba shape được merge (trước đó: swarm 10/10, orchestrator 10/10).
- `python -m pytest -q` (cổng host, đã gồm test ledger): 106 passed; `python -m pytest -q -m student -o addopts=`: 248 passed.
- `src/reports/hidden_selfcheck.json`: 3 shape × 200 trial trên `student_drop/`, 0 lỗi, 0 nghi lộ secret.
- `src/reports/crash.json`: `crash_safety` = 20/20.
- `src/reports/benchmark.json`: workflow pass 1.000 / pass^5 1.000 / variance 0 / cost/success 28.46 VND; trial fail duy nhất của swarm `R-swarm-C-002-s55`.

## 5. Công cụ AI đã dùng

Claude Code: đọc tài liệu lab và lập danh sách việc theo vai; viết nháp `src/tests/test_ledger_shapes.py`; chạy lệnh benchmark/crash; soạn nháp ADR, research card; soạn nháp mục 6 "Tự đánh giá" chỉ từ các bằng chứng ở mục 3–4, sau đó tôi đọc lại và chỉnh theo ý mình.

## 6. Tự đánh giá

Làm xong phần ledger + evaluation: có test, có `crash.json` 20/20 và `benchmark.json`, điền xong ADR và research card, `check_submission` ra 0 FAIL. Viết test ledger và thử trên swarm trước, khi các bạn merge shape là biết shape đó có đúng không.