# Bonus report: B3

- Topic + nguồn (tên, năm, slide): Verifier/aggregator chống khuếch đại lỗi; Google Research, *Towards a Science of Scaling Agent Systems*, bài giới thiệu ngày 28/01/2026; slide 17, 22, 42. [Nguồn chính thức](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/), [paper](https://arxiv.org/abs/2512.08296).
- CLAIM của nguồn (1 câu): Trong nghiên cứu, lỗi lan truyền ở kiến trúc độc lập tới 17,2×, còn điều phối tập trung giới hạn ở 4,4× nhờ có bước kiểm chứng kết quả.
- BOUNDARY (model / dataset / setup): Nguồn khảo sát 180 cấu hình, ba họ LLM và bốn benchmark; LogiX dùng MockLLM và luật hoàn tiền cố định, không tái lập các hệ số khuếch đại đó.
- HYPOTHESIS trên LogiX: Verifier bằng code sửa được quyết định sai do ticket làm lệch dữ kiện, tăng pass rate và độ ổn định của swarm nhưng tăng chi phí; workflow vẫn là baseline đơn giản hơn.
- Biến cố định / biến thay đổi: Cùng corpus, seed `11,22,33,44,55`, policy, pricing, evaluator và database mới mỗi trial. Giữ peer/parse/draft và lỗi theo seed của swarm tham chiếu; chỉ thêm verifier trước khi từ chối quote 0 hoặc gọi host ghi tiền. Verifier đọc lại order theo principal, kiểm `delay_days`, `status`, `damage_verified`, `shipping_fee_vnd`, `paid_vnd`; nếu lệch thì quote lại đúng một lần. Giữ cách đếm chi phí swarm tham chiếu và cộng các tool call bổ sung.
- Lệnh tái lập (copy-paste được): Chạy trong `src/`, với môi trường đã cài `requirements.txt`:

```powershell
.\.venv\Scripts\python.exe -m bonus.evaluate
.\.venv\Scripts\python.exe -m pytest -q tests/test_bonus_swarm_verified.py -p no:cacheprovider --basetemp ".venv/pytest-tmp-$([guid]::NewGuid().ToString('N'))"
```

- File report + run id: `src/reports/bonus_public.json`, `bonus_adversarial.json`, `bonus_safety.json`, `bonus_verifier_trace.json`; trace minh họa `R-swarm_verified-C-002-s55`. Script gọi benchmark chính thức bằng `--extra-shape swarm_verified=bonus.swarm_verified:run_claim`, rồi chạy kiểm toán safety độc lập. SHA-256 của code, fixture và cấu hình nằm trong `bonus_safety.json`.

## Kết quả

Public: 14 claim × 5 seed mỗi shape. Đối kháng: 12 claim × 5 seed mỗi shape. Nhãn tiền và trạng thái là các giá trị khai báo theo luật nghiệp vụ, có `label_reason` trong `src/bonus/cases.jsonl`; không sinh bằng hàm tính compensation. Các ca phủ nói quá/nói thiếu ngày trễ, nhiều con số, khai hỏng hàng sai, đơn hủy/đang giao, approval thiếu/sai claim, đã hoàn tiền, hoàn phần chênh và ngoài phạm vi principal.

| Corpus | Shape | Pass | Pass rate | Pass^5 | Variance | Cost/success (VND) |
| --- | --- | --- | --- | --- | --- | --- |
| Public | workflow | 70/70 | 1,000000 | 1,000000 | 0 | 34,285714 |
| Public | swarm | 69/70 | 0,985714 | 0,928571 | 0,000816 | 49,566957 |
| Public | swarm_verified | 70/70 | 1,000000 | 1,000000 | 0 | 57,572857 |
| Đối kháng | workflow | 60/60 | 1,000000 | 1,000000 | 0 | 35,000000 |
| Đối kháng | swarm | 54/60 | 0,900000 | 0,500000 | 0,040000 | 58,852963 |
| Đối kháng | swarm_verified | 60/60 | 1,000000 | 1,000000 | 0 | 63,635000 |

Verifier kiểm 60 trial public và 55 trial đối kháng sau khi đã qua kiểm tra mã đơn/phạm vi; can thiệp lần lượt 1 và 9 lần. Can thiệp không luôn thay đổi số tiền: có sai dữ kiện nhưng entitlement vẫn giữ nguyên. Trace C-002/55 ghi `verifier_override`: `delay_days` lệch, quote 20.000 → 0, `repair_round=1`; host không được gọi ghi refund cho quote đã sửa về 0.

Safety audit kiểm đủ 130 trial mỗi shape: secret leak, PII leak, approval bypass, sai principal, refund trùng, ledger ngoài claim và lỗi trace đều bằng 0 ở cả ba shape. Số trial trả quá entitlement theo nhãn là 3 ở swarm (1 public, 2 đối kháng), bằng 0 ở workflow và swarm_verified. Suite bổ sung cho mỗi shape đạt 15/15 (ba vị trí crash × năm seed), resume/retry vẫn một refund và một audit committed. Test còn cố ý làm sai từng trường quote và kết quả investigator để kiểm verifier đọc lại nguồn độc lập.

## Kết luận

Kết quả ủng hộ hypothesis trong phạm vi đã đo: verifier đưa pass rate và độ ổn định của swarm về mức workflow, với chi phí cao hơn cả swarm và workflow. Với task này, swarm chưa cho thấy lợi ích về độ đúng so với workflow; code và host quyết định số tiền. Swarm có thể có giá trị nếu mở rộng sang công việc đọc/soạn nội dung khó quy tắc hóa và đo được lợi ích đủ bù chi phí. Kết luận sẽ thay đổi nếu verifier bỏ sót dữ kiện, nguồn cấu trúc sai hoặc task mới cho thấy lợi ích đó.

## Giới hạn

MockLLM và lỗi delay theo seed là mô phỏng, không đại diện lỗi model sản xuất. Bộ đối kháng nhỏ, chủ đích nhắm lỗi đã biết; baseline hiện chỉ làm lệch delay, các trường khác được kiểm thêm bằng fault injection trong test. Chi phí là VND mô phỏng, latency là `unavailable`; không khẳng định ý nghĩa thống kê hay tái lập hệ số 17,2×/4,4×. Kết quả public/đối kháng không thay kết quả hidden: điểm bonus còn phụ thuộc shape nhóm chọn đạt hidden ≥ 0,80 và đủ ba must-pass theo đề.
