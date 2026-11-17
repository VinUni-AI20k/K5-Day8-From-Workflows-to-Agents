# Bonus report: B7

- Topic + nguồn: Kiểm toán grader; *Rethinking Evaluation of MAS Efficiency*, EMNLP 2026, slide 44/59.
- CLAIM: Một evaluator sai có thể làm sai các so sánh shape, kể cả khi shape không đổi.
- BOUNDARY: Ba candidate grader và các fixture/metamorphic relation được cung cấp trong repo; không suy rộng ra grader khác.
- HYPOTHESIS trên LogiX: grader đúng phải loại trial lỗi hạ tầng khỏi mẫu số pass rate, xử lý lặp trial tuyến tính và tính cost của mỗi trial đúng một lần.
- Biến cố định / biến thay đổi: Giữ nguyên fixtures và quy tắc quote; thay candidate `summarize` hoặc biến đổi danh sách trial theo quan hệ metamorphic.
- Lệnh tái lập (chạy từ `src/`): `python -m pytest -q tests/test_bonus_grader_audit.py`
- File report + run id: `reports/bonus_grader_audit.json`; run ID không áp dụng cho audit test.

## Kết quả

Kết quả được ghi tự động từ test vào `src/reports/bonus_grader_audit.json`.

| Candidate | Infra error không đổi pass rate | Nhân đôi trials: rate giữ, totals gấp đôi | Thêm failure: cost đếm một lần | Kết luận |
|---|---|---|---|---|
| grader_a | Đạt | Lệch: pass^5 giảm 0.667 → 0; total cost 283.5 → 473 thay vì 567; cost/success 31.50 → 26.28 | Lệch: thêm cost 40 làm tổng tăng 80 | Không đạt |
| grader_b | Đạt | Lệch: pass^5 giảm 0.667 → 0 khi lặp mọi trial; các total khác gấp đôi | Đạt | Không đạt relation duplicate |
| grader_c | Lệch: pass rate 0.75 → 0.5625 khi thêm 4 infra trials | Lệch: pass^5 giảm 0.667 → 0; các total khác gấp đôi | Đạt | Không đạt |

Quan hệ nghiệp vụ `delay_days` xác nhận quote đổi từ 0 VND ở 2 ngày sang 35,000 VND ở 3 ngày, theo clause `SHIP-LATE-03`. Fixture duplicate làm cả ba candidate sai ở pass^5: implementation đòi mỗi claim có đúng số row bằng số seed, nên không xử lý danh sách trial bị lặp. Quan hệ mới của nhóm thêm một trial fail có claim ID mới; nó phát hiện lỗi đếm chi phí theo claim ở grader_a mà fixture duplicate đơn thuần chưa định vị rõ.

## Kết luận

Các kết quả bác bỏ hypothesis rằng có một candidate hoàn toàn đúng theo mọi quan hệ hiện có: cả ba sai ở pass^5 khi trials bị lặp. Grader_a đếm cost lặp, grader_c tính trial hạ tầng như failure; grader_b chỉ vượt các quan hệ infra và thêm failure. Một lỗi evaluator có thể lọt qua nếu thiếu quan hệ nhắm vào trường hợp đó; các metamorphic test kiểm tính nhất quán mà không cần oracle tuyệt đối cho mọi đầu ra. Kết luận sẽ đổi nếu quan hệ sai, fixture có lỗi hoặc phát hiện sai khác trong định nghĩa metric.

## Giới hạn

Audit chỉ bao phủ ba implementation và fixtures trong repo, không chứng minh grader_b đúng cho mọi input. Không có `reports/hidden_grade.json` trong workspace nên chưa xác minh được gate bonus bắt buộc về hidden pass rate ≥ 0.80, leak/bypass = 0; vì vậy không khẳng định bonus đủ điều kiện nhận điểm. Không sửa các file grader/fixture được cung cấp.
