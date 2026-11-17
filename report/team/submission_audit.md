# Rà soát bài nộp — Problem Solver

Ngày kiểm tra: 16/11/2026 (GMT+7). Commit chứa code được đo: `bd5a602`. Rà soát theo RUBRIC.md, RULES.md và SUBMISSION.md; không tự quy đổi kết quả local thành điểm giảng viên.

## Kết luận

Phần kỹ thuật đã có bằng chứng đáp ứng các gate và bonus B3. Chưa đủ cơ sở khẳng định đạt 100/100 hoặc 110/110, chủ yếu vì đóng góp theo lịch sử Git của từng thành viên và các thao tác nộp bài cần hoàn tất.

| Tiêu chí | Điểm tối đa | Kết quả rà soát |
| --- | ---: | --- |
| C1 Implementation | 20 | Ba shape triển khai, 351 test xanh, bao gồm đầy đủ 248 student test và kiểm ba shape trên host nguyên bản. |
| C2 Hidden | 15 | Workflow 200/200, pass⁵ 1.00 trên pack được cung cấp; source SHA-256 khớp code trong bd5a602. Cần giảng viên xác nhận bằng grader riêng. |
| C3 Durability | 20 | Crash host 20/20; crash hidden 30/30; retry/idempotency và audit được kiểm bằng test. |
| C4 Policy | 10 | Public và hidden của ba shape đều pass; không approval bypass; policy/durability/config/data nguyên bản. |
| C5 Handoff/trace | 10 | Handoff allowlist, investigator chỉ đọc, trace hợp lệ; 1.000 trial hidden recount không secret/PII leak. |
| C6 Benchmark/ADR | 10 | Public 14 claim × 5 seed × 4 shape; đủ metric/run id; ADR được sửa về commit code thật; ablation B3 có biến cố định, hypothesis và giới hạn. |
| C7 Reproducibility | 10 | Chạy lại benchmark.json, bonus_public.json, bonus_adversarial.json và crash.json: khớp toàn bộ object JSON. Repo GitHub public. Chưa có Actions run để xác nhận matrix 3 OS × 2 Python. |
| C8 Đóng góp | 5 | Chưa đủ bằng chứng: chỉ thấy commit code/test của QuocAnhtapcode; chưa thấy commit kỹ thuật riêng của ba thành viên còn lại. Báo cáo cá nhân không thay thế yêu cầu này. |
| Bonus B3 | +10 | Có verifier ba field, tối đa một vòng sửa, 16 case đối kháng có nhãn viết tay, test và bằng chứng chi phí/safety. Gate local của workflow đạt 1.00, không leak/bypass. Điểm phân tích và xác nhận gate do giảng viên quyết định. |

## Lỗi đã sửa trong lượt rà soát

1. TEAM.md thiếu MSSV đầy đủ, email và GitHub dù báo cáo cá nhân đã có: đã đồng bộ bốn người.
2. Tên bốn file cá nhân dùng MSSV rút gọn: đã đổi thành `2A202603707_HoangQuocAnh.md`, `2A202603709_DoThiThanhBinh.md`, `2A202603713_LeGiaHung.md`, `2A202603720_HaQuangVinh.md`, sửa liên kết tương ứng.
3. ADR còn ghi chưa chốt commit/HEAD nền 034c6c4: đã ghi bd5a602, đối chiếu SHA-256 tất cả nguồn trong bằng chứng hidden.
4. CI checkout mặc định chỉ lấy commit mới, trong khi portability test cần commit starter: đã đặt fetch-depth 0. CI cũng được đổi sang student matrix và benchmark đủ bốn shape.
5. B3 report được bổ sung hypothesis, biến giữ cố định/thay đổi và lệnh tái lập rõ ràng; research card làm rõ liên hệ giữa nguồn và verifier.
6. Đã kiểm tra đóng trang: bản A4 ở output/pdf/group_report.pdf có 2 trang (giới hạn 5); output/pdf/bonus_report.pdf có 2 trang (giới hạn 2). Các bảng không bị cắt mất dòng và tiếng Việt hiển thị đúng.

## Khai báo AI và kiểm chứng

- Bốn báo cáo cá nhân ghi Codex hỗ trợ và nêu smoke, pytest, benchmark, crash, safety recount, HTML là cách kiểm chứng. Không còn ghi AI làm nhưng chưa verify trong bốn báo cáo này.
- Câu tự đánh giá “Đã kiểm chứng và điều chỉnh toàn bộ code và báo cáo do AI hỗ trợ viết” là nội dung thành viên đã khai. Kết quả công cụ chứng minh các kiểm thử chạy được; không chứng minh từng người đã trực tiếp đọc/hiểu mọi phần.
- Giữ mục khai công cụ AI vì RULES.md yêu cầu. Không sửa tác giả Git hoặc gán commit chung thành commit cá nhân.
- File MSSV_HoTen.md còn chỗ trống là mẫu phải giữ theo đề, không phải báo cáo cá nhân chưa hoàn thành. Các câu giới hạn MockLLM, latency unavailable và chờ giảng viên xác nhận điểm là cần thiết.

## Việc còn phải hoàn tất

1. Ba thành viên còn lại tự thực hiện đóng góp kỹ thuật và ít nhất một test có nội dung, commit bằng danh tính thật, cập nhật hash vào TEAM.md. Không tạo commit rỗng hoặc sửa author để hợp thức hóa lịch sử.
2. Push các cập nhật hồ sơ/CI sau rà soát lên main; kiểm GitHub Actions chạy xanh. Lúc rà soát, remote main là bd5a602 và Actions có 0 run.
3. Mỗi thành viên tự nộp link repo trên LMS đúng hạn. Công cụ hiện không có bằng chứng việc nộp LMS hoặc phần giải thích trực tiếp trước giảng viên.
4. Sau các commit kỹ thuật mới, chạy lại test/benchmark phù hợp và cập nhật ADR theo commit nguồn đã đo. Các PDF xuất ở lượt này là bản đóng trang của nội dung hiện tại; sửa Markdown thì xuất lại.

## Lệnh kiểm tra

Trong src/: `python -m lab8.smoke`, `python -m pytest -q -o addopts=`, `python -m lab8.check_submission`. Hidden: `python -m bonus.hidden_evidence --pack D:/AIThucChien/DAY08/instructor/instructor`. Lệnh public/bonus đầy đủ ở research_card.md và src/reports/README.md.

Các lần chạy lại benchmark trong lượt rà soát được ghi riêng vào tmp/audit/ để so sánh; không sửa tay JSON bằng chứng nộp bài.
