# Tóm tắt công việc Người 4 (Durability + Eval)

## 1. Đọc hiểu hệ thống & chạy demo ledger

- Đã đọc và nắm rõ cơ chế của các module:
  - [`src/lab8/durability.py`](../../src/lab8/durability.py): `issue_refund` ghi `refund_ledger` + `audit_events` (`refund_committed`) trong cùng 1 transaction `BEGIN IMMEDIATE`, kiểm tra lại `order_refunded_vnd` trước khi insert, hỗ trợ idempotent replay / `amount_conflict`, và 3 điểm `InjectedCrash` (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`).
  - [`src/lab8/policy.py`](../../src/lab8/policy.py): `authorize` kiểm tra `claims.approval_id` phải thuộc đúng `claim_id`, `status == "valid"`, chưa hết hạn, và trừ `already_refunded_vnd` theo trần đơn hàng (`cap_per_order`, `cap_at_approved_amount`, `cap_at_paid_amount`).
  - [`src/lab8/metrics.py`](../../src/lab8/metrics.py): `trial_pass` đối chiếu kết quả trả về với SQLite ledger (`unexpected_ledger_rows`, `result_ledger_mismatch`, `audit_count_mismatch`), kiểm tra `check_trace` (Trace contract v1) và quét `forbid_substrings` trên `artifact_blob`.
  - [`src/lab8/crash_test.py`](../../src/lab8/crash_test.py): bộ kiểm thử 20 kịch bản crash (`CR-01`..`CR-20`).
  - [`src/lab8/benchmark.py`](../../src/lab8/benchmark.py): chạy benchmark cô lập DB theo từng `(shape, claim_id, seed)` và phát hiện `LEAK_MARKERS` khi không có nhãn.
- Đã chạy `cd src && .venv/bin/python -m lab8.demo.buggy_workflow`:
  - Output: `unsafe refund rows: 2 (the host ledger must stay at 1)` — minh họa lỗi double-pay khi bảng demo không dùng chung transaction/idempotency key với checkpoint.

## 2. Kịch bản test chéo đã tạo (`src/tests/test_durability_eval_extra.py`)

Đã tạo [`src/tests/test_durability_eval_extra.py`](../../src/tests/test_durability_eval_extra.py) bao gồm:

1. **T11 Idempotency (`test_t11_idempotency_and_conflict`)**:
   - Replay cùng số tiền (`35000`) trả về `idempotent_replay`, chỉ giữ 1 dòng `refund_ledger` và 1 audit `refund_committed`.
   - Replay khác số tiền (`20000`) trả về `amount_conflict` và giữ nguyên số tiền đã commit (`35000`).
2. **T12 Crash & Resume ở 3 điểm crash**:
   - `test_t12_host_crash_and_resume_three_points` và `test_t12_swarm_crash_and_resume_three_points` kiểm tra cả 3 điểm: `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`.
   - Xác minh trạng thái ledger/checkpoint ngay tại điểm crash và sau khi resume vẫn chỉ có đúng 1 dòng ledger, 1 audit `refund_committed`, `trial_pass` đạt.
3. **Approval sai claim / không hợp lệ (`test_approval_wrong_claim_and_invalid_states`)**:
   - Kiểm tra `approval_claim_mismatch` (dùng `A-001` của `C-001` cho claim khác), `approval_expired`, `approval_revoked`, `missing_approval` đều bị từ chối, không ghi `refund_ledger`, có audit `policy_denied`.
4. **Tràn trần đơn (`test_order_cap_blocks_second_claim_and_tops_up_difference`, `test_pre_subtracting_before_issue_refund_causes_underpayment`, `test_order_paid_amount_cap_prevents_over_refund`)**:
   - `C-013` trên `O-505` bị từ chối với `order_already_refunded`.
   - `C-014` trên `O-515` (đã hoàn `30000`) truyền full quote `150000` -> host chỉ hoàn phần chênh `120000` (tổng đơn `150000`).
   - Minh họa nếu shape tự trừ trước (`120000`) sẽ bị host trừ lần 2 thành `90000` và trượt `trial_pass` (`refund_mismatch`).
   - Kiểm tra trần `paid_vnd` (`cap_at_paid_amount`).
5. **Leak canary secret / PII (`test_swarm_does_not_leak_canary_or_pii_to_trace_or_stdout`, `test_trial_pass_catches_forbidden_substring_in_trace`)**:
   - Kiểm tra `C-005`, `C-010` trên `swarm` không làm lọt `CANARY_SECRET_*`, `CANARY_INTERNAL_*`, số điện thoại, địa chỉ, `SECRET_ITEM_VANG` vào `RunResult`, trace JSON, file phụ `<run_id>*` hay `stdout`/`stderr`.
6. **Trace contract v1 (`test_trace_contract_v1_rejects_bad_traces_and_accepts_valid`)**:
   - Kiểm tra các lỗi `missing_trace`, `invalid_trace`, `trace_run_id_mismatch`, `stale_trace` và trường hợp hợp lệ.
7. **Ma trận test chéo 4 shape (`@pytest.mark.student`)**:
   - `test_student_shapes_t12_crash_three_points` (4 shapes × 3 crash points) và `test_student_shapes_pii_leak_and_order_cap` (4 shapes × `C-005`, `C-010`, `C-013`, `C-014`).

### Kết quả chạy test

- `cd src && .venv/bin/pytest tests/test_durability_eval_extra.py -v`: **15 passed**, 28 deselected (các test `@pytest.mark.student`).
- `cd src && .venv/bin/pytest -q`: **69 passed**, 276 deselected.

## 3. Review code của Người 1, 2, 3

Đã kiểm tra 3 file shape của nhóm:

- [`src/lab8/shapes/workflow.py`](../../src/lab8/shapes/workflow.py) (Người 1)
- [`src/lab8/shapes/single.py`](../../src/lab8/shapes/single.py) (Người 2)
- [`src/lab8/shapes/orchestrator.py`](../../src/lab8/shapes/orchestrator.py) (Người 3)

**Tình trạng hiện tại:** Cả 3 file đều đang ở trạng thái **stub mặc định** (`return not_implemented(...)` với `# TODO CP2` và `# TODO CP3`, `del store_path, crash_at`), chưa có code triển khai của Người 1, 2, 3 trên nhánh `chinh`.

**Checklist cần xác nhận khi Người 1, 2, 3 đẩy code lên:**
1. **Không nuốt `InjectedCrash`**: phải truyền `crash_at=crash_at` vào `durability.issue_refund(...)` và không bắt `InjectedCrash` (nếu có `try/except InjectedCrash` để flush trace như `swarm_reference.py` thì bắt buộc `raise` lại).
2. **Không tự trừ tiền đã hoàn trước khi gọi `issue_refund`**: phải truyền full quote (`compute_compensation`) vào `issue_refund`; host sẽ tự trừ phần đã hoàn của các claim trước trên cùng đơn.
3. **Không để lọt secret/PII vào trace/stdout**: đọc claim qua `get_claim_view` (không `SELECT *` lấy `parent_secret` / `raw_headers_json`), không copy `phone`, `address`, `item`, `internal_note` từ `lookup_order` vào trace/handoff/stdout.
4. Sau khi Người 1, 2, 3 hoàn thành, chạy lệnh sau để nghiệm thu chéo:
   ```bash
   cd src && .venv/bin/pytest tests/test_durability_eval_extra.py -m student -o addopts= -v
   ```
