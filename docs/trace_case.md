# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Mẫu điền (mỗi nhóm 1 case, lấy từ trial đang fail trong report)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run_id: `seeded_regression-C-002-s11` |
| Triệu chứng | Lab 8 grader FAIL (status resolved != denied); ledger ghi nhận hoàn 20.000đ (nhãn = 0đ); reply nói "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202." |
| Bước sai đầu tiên | Event 3: `model_override` `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event 1 (`handoff`) và Event 2 (`investigator`) hoàn toàn đúng, DB ghi nhận đơn O-202 có `delay_days: 0` (hoặc 1); Event 3 tự ý lấy số ngày từ ticket để đè lên DB |
| Failure mode | `FM-03` (`ticket_trust`) |
| Đối chứng | Cùng `C-002@11` trên shape `fixed`: không có event `model_override`, Event 3 là `quote` trả về 0đ (`no_entitlement`), trạng thái `denied` |
| Regression test | Grader `DbFactKept` kiểm tra không có event `model_override`; fail trên `seeded_regression` và pass trên `fixed` |
| Chưa chắc chắn | Ticket người dùng có chủ ý gian lận hay do nhầm lẫn ngày giao hàng |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
