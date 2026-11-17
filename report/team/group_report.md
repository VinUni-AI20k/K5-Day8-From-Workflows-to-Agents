# Báo cáo nhóm — Lab 8 LogiX-VN

Số liệu dưới đây lấy từ JSON do công cụ sinh ra trong `src/reports/`. Phần evaluation được tổng hợp bởi Vũ Văn Chu ngày 17/11/2026 (GMT+7).

## 1. Thông tin nhóm

- Tên nhóm: chưa khai báo trong `TEAM.md`; người phụ trách integration bổ sung trước khi nộp.
- Thành viên: Vũ Tuấn Đạt (workflow + integration), Trần Tuấn Anh (single), Đinh Hoài Nam (orchestrator + handoff), Vũ Văn Chu (ledger + evaluation).
- Commit kỹ thuật dùng đánh giá (trùng `report/team/decision_adr.md`): `132507f`. Commit báo cáo bổ sung sau commit kỹ thuật.

## 2. Mục tiêu và cách tiếp cận

Xử lý cùng claim hoàn phí LogiX-VN bằng bốn kiến trúc, rồi chọn mức tự chủ thấp nhất đủ làm việc dựa trên số đo. Ba shape A/B/C đã được thành viên phụ trách triển khai và merge; D là swarm đối chứng có sẵn. Phần ledger + evaluation kiểm tra lại ba shape với host có sẵn, bổ sung fault injection, chạy benchmark và tổng hợp bằng chứng. Không sửa host/thước đo hoặc dữ liệu public.

## 3. Giải pháp

| Shape | Cách xử lý | Ranh giới code/model |
| --- | --- | --- |
| workflow | Các bước cố định: claim → order đúng principal → quote → host | Model chỉ draft lời phản hồi từ status |
| single | Vòng ReAct tối đa 8 bước, tool đọc; sau vòng lặp code gọi host | `decide()` hiện theo kế hoạch cố định, có tính model cost; không lấy số tiền/ngày trễ từ ticket |
| orchestrator | Handoff qua `make_handoff`; investigator đọc order/policy/history/quote; orchestrator gọi host | Handoff allowlist, không parent context, không tool ghi; MockLLM chỉ draft |
| swarm | Peer/parse, investigator và draft; đối chứng có sẵn | Seed 55 cố ý tin delay trong ticket nếu khác order |

Tiền do `compute_compensation` tính từ order và policy hiện hành; khi nhiều clause đủ điều kiện lấy max, không cộng. Shape truyền quote đầy đủ vào `durability.issue_refund`. Host kiểm approval thuộc đúng claim, ownership, cap approval/paid/per-order và idempotency. Refund và audit committed chung transaction; checkpoint ghi sau. Retry đọc ledger thay vì tin checkpoint.

Trace chỉ chứa dữ kiện đã allowlist: claim flags, order view, quote, host outcome và các quyết định; single thêm tool/loop events; orchestrator thêm handoff và investigator. Không ghi ticket thô, secret, raw header, SĐT, địa chỉ, internal note hay tên hàng. `finish()` đối chiếu effect/audit thật và ghi trace đúng run id.

## 4. Kết quả

Từ [benchmark.json](../../src/reports/benchmark.json): 4 shape × 14 claim × 5 seed `11,22,33,44,55`, `as_of=2026-11-15`, cùng world, MockLLM, giá và evaluator; mỗi trial một DB mới. Cost là VND mô phỏng.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1,000000 | 1,000000 | 1–1 | 0 | 28,770000 | 4,428571 / 5 |
| single | 1,000000 | 1,000000 | 1–1 | 0 | 39,348571 | 6,285714 / 7 |
| orchestrator | 1,000000 | 1,000000 | 1–1 | 0 | 56,647143 | 3,714286 / 4 |
| swarm | 0,985714 | 0,928571 | 0,928571–1 | 0,000816327 | 49,566957 | 2,800000 / 3 |

Swarm sai đúng `R-swarm-C-002-s55`: order trễ 2 ngày nhưng ticket nói 5; swarm ghi 20.000 thay vì deny. Host vẫn kiểm approval hợp lệ, nhưng không tự tính lại entitlement. Ba shape nhóm đúng 70/70.

- [crash.json](../../src/reports/crash.json): **20/20** trong suite host + swarm. Test mới kiểm thêm ba shape × ba điểm crash × hai loại refund (18 trường hợp).
- [safety.json](../../src/reports/safety.json): trên **280 trial public**, secret leak/PII leak/approval bypass/unexpected ledger/invalid trace/exception đều **0**. Quét artifacts và stdout/stderr; approval bypass dựa vào ledger và nhãn approval public.
- `python -m pytest -q`: **147 passed, 248 deselected**; `python -m pytest -q -m student -o addopts=`: **248 passed**. Ma trận student assert riêng điểm yếu swarm là một miss mong đợi, khác cách tính pass rate benchmark.
- Hai file test của Chu: **46 passed** (35 ledger, 11 evaluation), bao gồm lỗi audit rollback, checkpoint giả, conflict khi quote đổi, approval hỏng, metric tính tay và đối chiếu SQLite.
- [evaluation_ablation.json](../../src/reports/evaluation_ablation.json): chỉ bỏ draft call của workflow; cả hai nhánh 70/70, pass^5 = 1, variance = 0. Cost/success **28,77 → 27,857143**, tiết kiệm tổng **63,90**; model calls/trial 1 → 0. Kết quả không đánh giá chất lượng lời phản hồi.
- Chưa có `student_drop/`; chưa chạy hidden self-check và chưa biết điểm hidden chính thức.

Chọn workflow theo số đo public: cùng tỷ lệ đúng với B/C, cost thấp nhất và quyền tự chủ ít nhất. Mean/p95 steps là số event trace, không phải latency.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Máy evaluation chạy `python --version` ra **3.15.0**, ngoài dải phiên bản của lab. Dùng `py -3.12 -m venv .venv` trong `src/`, sau đó `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`. Smoke xác nhận **Python 3.12.9 / Windows AMD64**; `pip check` in `No broken requirements found.` Trước khi thêm test, host đạt 101 passed; sau bổ sung đạt 147 passed.

Checkpoint không bảo đảm side effect một lần: test gây crash trước effect, sau effect/trước checkpoint và sau checkpoint; đóng connection rồi resume. Với cap 20.000 và top-up 120.000, mỗi claim vẫn một dòng ledger và một audit. Trigger gây lỗi ghi audit chứng minh refund được rollback khi transaction chưa thể hoàn tất.

Các lệnh tái lập nằm trong báo cáo cá nhân của Chu và ADR. Tất cả JSON sinh bằng runner; không điền tay số liệu hay tạo kết quả hidden giả.

## 6. Tổng hợp đóng góp

| Thành viên | Phần việc | Bằng chứng kỹ thuật |
| --- | --- | --- |
| Vũ Tuấn Đạt | Workflow + integration | `1a607d2`, `test_workflow_shape.py`, báo cáo `2A202603744_VuTuanDat.md` |
| Trần Tuấn Anh | Single | `94bc560` và bản sửa sau merge; `test_single_shape.py`, báo cáo `2A202603909_TranTuanAnh.md` |
| Đinh Hoài Nam | Orchestrator + handoff | `7f91bc6`, ma trận student orchestrator 62/62; báo cáo `2A202603762_DinhHoaiNam.md` ghi chưa thêm test riêng |
| Vũ Văn Chu | Ledger + evaluation | `132507f`, 46 trường hợp mới và bốn report JSON; báo cáo `2A202603873-VuVanChu.md` |

`TEAM.md` đã bổ sung phần của Chu. Integration cần bổ sung thông tin nhóm/URL/commit nộp và mục đóng góp của Nam đang thiếu trong bảng; báo cáo hiện có của Nam chưa ghi test mới theo yêu cầu C8. Không khai thay một test chưa có.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency `unavailable`, cost không phải hóa đơn API. Public chỉ có 14 claim; không suy ra đạt hidden hoặc production. So sánh A/B/C/D còn khác prompt và số tool/model calls nên chưa cô lập ảnh hưởng topology; ablation chỉ kiểm một draft call trong workflow. Trace của hai nhánh ablation dùng cùng run id, nên report JSON lưu số liệu từng lần chạy; trace cuối không phải hai bản độc lập. Chưa kiểm mất điện thực tế hoặc concurrency đa tiến trình.

Chỉ cân nhắc tăng tự chủ khi có benchmark độc lập cho thấy cải thiện trên dữ liệu mơ hồ/đa nguồn, chi phí chấp nhận được và vẫn giữ đủ safety gates. Chất lượng phản hồi khách hàng cần phép đánh giá riêng.

## 8. Tài liệu tham khảo

- [Business rules](../../docs/business_rules.md), [contracts](../../docs/contracts.md), [metrics](../../docs/metrics.md), [RULES](../../RULES.md), [RUBRIC](../../RUBRIC.md).
- Zhang et al., 2026, [Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems](https://aclanthology.org/2026.emnlp-main.798/); sử dụng cho thiết kế ablation R4, xem research card.
