# Báo cáo cá nhân — 2A202604000 Đồng Hữu Nguyên Khoa

## 1. Thông tin thành viên

- Họ tên: Đồng Hữu Nguyên Khoa
- MSSV: 2A202604000
- Email: donghuunguyenkhoa@gmail.com / 26ai.khoadhn@vinuni.edu.vn
- GitHub: [github.com/lit1numyt](https://github.com/lit1numyt)

## 2. Phần việc phụ trách

- **Shape B — `single` (một agent ReAct):** `src/lab8/shapes/single.py`, từ CP2 đến CP4.
- **Cài đặt và khung ban đầu (CP1–CP2):** dựng môi trường, chạy smoke và cổng host, viết bản đầu của ba shape `workflow`, `single`, `orchestrator` để cả nhóm có baseline chạy được.
- **Bằng chứng CP4–CP5:** sinh `src/reports/crash.json` và `src/reports/benchmark.json`.

## 3. Đóng góp cụ thể

**Commit chính**

| Commit | Nội dung |
| --- | --- |
| `62932fd` — (starter) cp1 + cp2 | Cài đặt, bản đầu ba shape A/B/C, mỗi shape qua 62 test student |
| `caebbbe` — (shape-B) cp3 + cp4 | Hoàn thiện shape B, thêm `tests/test_single_shape.py`, sinh `reports/crash.json` |
| PR #1, PR #2 | Merge `khoa/starter` và `khoa/shapeB` vào `main` |

**Test đã thêm:** `src/tests/test_single_shape.py` — 34 test, chạy trong cổng host `python -m pytest -q`:

- Approval: approval mượn của claim khác (`approval_claim_mismatch`), approval bị thu hồi, hết hạn, thiếu, hoặc bằng 0 → `denied`, không có dòng ledger, có audit `policy_denied` đúng lý do.
- Secret/PII: với cả 14 claim public, result và trace không chứa `CANARY_SECRET_`, `CANARY_INTERNAL_`, header `Authorization`, SĐT, địa chỉ, tên hàng; chữ trong ticket (ví dụ "ignore policy") không bị chép vào trace.
- Crash: ở cả 3 điểm crash (`before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`), resume xong vẫn đúng một refund và một audit `refund_committed`; trace vẫn được ghi khi crash.
- Ranh giới agent: số ngày trễ trong ticket không ghi đè dòng order (C-002 trên cả 5 seed); không lấy `order_id` từ chữ trong ticket; agent chỉ chọn tool đọc; vượt 8 bước → `failed` / `step_cap`; model đòi gọi `issue_refund` → `tool_rejected`, không ghi ledger.

**Quyết định kỹ thuật trong shape B**

1. **Model không quyết số tiền.** `decide` chỉ trả về "quote đã sẵn sàng"; số tiền đưa vào `durability.issue_refund` là kết quả tool `compute_compensation` do code lưu lại trong `memory`, không phải số model viết trong câu trả lời cuối.
2. **Chỉ tool đọc.** Agent chỉ được chọn trong `AGENT_TOOLS = (lookup_order, lookup_refund_history, compute_compensation)`; host là nơi duy nhất ghi tiền, gọi sau khi vòng ReAct kết thúc.
3. **Ticket là dữ liệu.** Agent đọc được ticket, nhưng mọi con số đều lấy từ tool đọc trên DB; ticket không bao giờ được ghi vào trace.
4. **Truyền quote đầy đủ** cho host (để host tự trừ phần đã hoàn của đơn — T13, T14), truyền `crash_at` và không nuốt `InjectedCrash` (ghi trace rồi `raise` lại — T12).
5. **Đếm chi phí công bằng:** mỗi bước ReAct là một lần gọi MockLLM, cộng thêm một lần soạn câu trả lời; tối đa 8 bước.

## 4. Bằng chứng

- Ma trận student: `python -m pytest -q -m student -o addopts=` → **248 passed** (62 test mỗi shape × 4 shape).
- Cổng host: `python -m pytest -q` → **88 passed** (gồm 34 test của shape B).
- Crash suite: `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety` **20/20**.
- Benchmark chính thức (`src/reports/benchmark.json`, 14 claim × seed `11,22,33,44,55`), dòng của shape B:

  | Shape | Pass rate | pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean / p95 steps | Model calls TB |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | single | 1.000 | 1.000 | 1.000–1.000 | 0 | 39.35 | 7.93 / 9 | 4.64 |

- Run id ví dụ: `R-single-C-001-s11`, `R-single-C-002-s55` (claim mà swarm fail ở seed 55, shape B vẫn `denied` đúng).

## 5. Công cụ AI đã dùng

- **Claude Code (Anthropic):** dùng để đọc repo và tài liệu (README, CHECKPOINTS, contracts, business rules), viết bản đầu ba shape, viết bộ test `test_single_shape.py`, chạy lệnh kiểm tra và soạn nháp báo cáo này.
- **Cách tự kiểm tra:** chạy lại toàn bộ cổng host, ma trận student, crash suite và benchmark trên máy mình; đọc lại từng nhánh return của `single.py` so với bảng trong `docs/contracts.md`; grep trace để chắc không có secret/PII; tự đọc và chỉnh lại nội dung báo cáo cho đúng phần mình làm.
- Có một lỗi do mình gây ra khi giải conflict lúc merge `main` vào `khoa/shapeB` (`86a21fe`): giữ dòng của cả hai phía nên `single.py` bị lỗi cú pháp. Phát hiện khi chạy benchmark, sửa bằng cách khôi phục file từ commit sạch `caebbbe` rồi chạy lại toàn bộ test.

## 6. Tự đánh giá

- **Làm tốt:** shape B đạt pass rate 1.0, pass^5 1.0, variance 0 trên bộ public; qua cả ba điều kiện must-pass có test riêng chứng minh; tiền và quyền ghi luôn nằm ở code/host, không ở model.
- **Chưa tốt:** shape B tốn hơn workflow khoảng 36% chi phí mô phỏng (39.35 so với 28.87 VND/success) và gần gấp đôi số bước, trong khi không pass thêm claim nào — tức là phần tự chủ thêm chưa mua được gì trên bộ public. Lỗi merge conflict cho thấy cần chạy `pytest` trước mỗi lần merge.
- **Nếu làm lại:** thêm test cho ticket chứa homoglyph và principal lẫn (bộ hidden có phủ), và bỏ bước `lookup_refund_history` nếu không dùng để quyết định gì, để giảm chi phí.
