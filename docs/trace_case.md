# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case phân tích: `seeded_regression C-002@11`

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261117-1c18` |
| Triệu chứng | `lab8` grader FAIL (`status resolved != denied`); ledger ghi `refund_vnd=20000`, `refund_count=1` trong khi nhãn yêu cầu `refund_vnd=0`, `refund_count=0`, `status=denied`; reply nói `"Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."` |
| Bước sai đầu tiên | Event `3`, `kind=model_override`, payload `{"delay_days": 5}` |
| Vì sao là bước *đầu tiên* | Event `1` (`handoff`) đúng hợp đồng `handoff.v1` và danh sách tool cho phép; Event `2` (`investigator`) tra cứu đúng đơn `O-202` từ DB với `delay_days=2` (chưa đủ điều kiện hoàn phí ship). Chỉ tới Event `3`, agent mới lấy số `5` ngày từ ticket khách để ghi đè `delay_days` của DB, kéo theo `quote` (Event `4`) tính sai thành `20000`. |
| Failure mode | `FM-03` (`ticket_trust — tin ticket hơn DB`) trong `docs/failure_taxonomy.md` |
| Đối chứng | Cùng `C-002@11` trên shape `fixed`: sau Event `2` (`investigator`), không có `model_override`; Event `3` (`quote`) trả `amount_vnd=0, reason="no_entitlement"`, Event `4` (`reply`) từ chối đúng, ledger `refund_vnd=0`. |
| Regression test | `test_c002_seed11_fixed_passes_and_seeded_regression_fails` trong `src/tests/test_lab9_trace_case.py` dùng `graders.DbFactKept` + `lab8_pass`; đã xác nhận FAIL trên `seeded_regression` và PASS trên `fixed`. |
| Chưa chắc chắn | Trace trên MockLLM không chứng minh được với LLM thật liệu prompt hệ thống hiện tại có đủ ngăn model tự suy diễn `delay_days` từ ticket mà không ghi event `model_override` hay không (ví dụ trường hợp `quiet_override`). |
