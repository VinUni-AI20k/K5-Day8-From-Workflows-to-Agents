# Báo cáo cá nhân — Đỗ Minh Hoàng — 2A202603554

## 1. Thông tin thành viên

- Họ tên: Đỗ Minh Hoàng
- MSSV: 2A202603554
- Email: hoangcoihd6@gmail.com
- GitHub: worryveem
- Repo nhóm: https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents
- Nhánh làm việc: `hoang` (đã merge vào `main` qua PR #3)

## 2. Phần việc phụ trách

- Shape A `workflow`: `src/lab8/shapes/workflow.py`.
- Test riêng của Shape A: `src/tests/test_team_workflow.py`.
- Sau khi merge đủ ba shape: chạy crash suite, benchmark 4 shape × 5 seed, điền `report/team/decision_adr.md`.
- Phần Shape A và bảng kết quả trong `report/team/group_report.md`.

## 3. Đóng góp cụ thể

Commit chính:

- [`9cdc97b`](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/9cdc97b): cài Shape A và 25 test riêng.
- [`e99c5f2`](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/e99c5f2): `src/reports/benchmark.json` (4 shape × 14 claim × 5 seed). Đây là commit ghi trong ADR.
- [`a7d2ace`](https://github.com/congcoderht/K5-L3A-Day08-NhomV3-FromWorkflowsToAgents/commit/a7d2ace): điền `decision_adr.md`.

Quyết định kỹ thuật trong Shape A:

- Luồng cố định 8 bước: `get_claim_view` → thiếu `order_id` thì `needs_info` → `lookup_order` không thấy thì `escalated` → `compute_compensation` → quote 0 thì `denied` (không gọi host) → `durability.issue_refund` với **quote đầy đủ** và `crash_at` → host từ chối thì `denied`, xung đột thì `failed` → còn lại `resolved`.
- Truyền quote đầy đủ vì host tự trừ phần các claim khác đã nhận trên cùng đơn. Nếu shape tự trừ trước, host trừ lần hai và T14 sai (ledger phải là 120.000, proposal 150.000).
- Không đọc ticket để lấy số ngày trễ hay mã đơn: ticket là dữ liệu người dùng (C-002 ghi trễ 5 ngày nhưng order row ghi 2 ngày).
- Không gọi MockLLM: shape không cần model để ra quyết định, nên `model_calls = 0` và cost thấp nhất.
- `InjectedCrash` không bị bắt: ghi event `crash` vào trace rồi ném lại, để T12 và crash suite thấy crash thật.
- Trace chỉ ghi 5 field đơn trong allowlist (`order_id`, `status`, `delay_days`, `shipping_fee_vnd`, `damage_verified`); không ghi ticket, claim row, order row thô (SĐT, địa chỉ, tên hàng, internal note).

Test riêng (25 test trong `src/tests/test_team_workflow.py`):

- Gọi lại cùng claim giữ 1 dòng ledger và 1 audit `refund_committed`.
- Crash `after_effect_before_checkpoint` được ném ra, resume chỉ trả 1 lần.
- Số ngày trễ trong ticket bị bỏ qua ở cả 5 seed.
- Full quote: C-014 proposal 150.000, ledger 120.000.
- Đơn đã hoàn đủ (C-013): host ghi `policy_denied`.
- Thiếu `order_id` (C-004), claim không tồn tại.
- Trace đúng contract và không chứa `forbid_substrings`, `CANARY_SECRET`, `CANARY_INTERNAL` hay ticket cho cả 14 claim public.

## 4. Bằng chứng

- Ma trận student Shape A: `62 passed`. Sau khi merge đủ ba shape: ma trận 4 shape `248 passed`, bộ test mặc định `102 passed`.
- Test riêng: `25 passed`.
- `src/reports/crash.json`: `crash_safety 20/20`.
- `src/reports/benchmark.json`: workflow pass rate 1.000, pass^5 1.000, variance 0, cost/success 34.29 VND mô phỏng, mean/p95 steps 4.43/5, 0 model call. Run id: `R-workflow-C-001-s11`, `R-workflow-C-002-s55`, `R-workflow-C-014-s11`.
- Quét 282 trace của ba shape nhóm viết sau merge: không có secret hay PII.
- `python -m lab8.check_submission`: `0 FAIL`.

## 5. Công cụ AI đã dùng

- Claude Code: đọc đề và contract, gợi ý cách chia việc, gợi ý code Shape A và test, chạy lệnh kiểm tra, soạn nháp ADR và báo cáo.
- Cách tự kiểm tra: chạy `python -m pytest -q`, ma trận student, crash suite và benchmark chính thức; mọi số liệu lấy từ `src/reports/*.json`, không chép từ câu trả lời của AI. Đọc lại code để tự giải thích được ranh giới code/model, vì sao truyền quote đầy đủ và trace cố ý không ghi field nào. Code lab chỉ dùng MockLLM, không gọi API model thật.

## 6. Tự đánh giá

Shape A đạt toàn bộ test public, crash 20/20, và là shape rẻ nhất trong benchmark nên được nhóm chọn cho cổng hidden. Giới hạn: kết quả mới là bộ public 14 claim với MockLLM; chưa chứng minh ngưỡng hidden 0.75. Luồng cố định có thể không xử lý được loại claim cần hiểu ngôn ngữ để chọn nhánh, nếu bộ hidden có loại đó.
