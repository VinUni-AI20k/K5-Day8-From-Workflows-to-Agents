# Báo cáo cá nhân — DoanNhatAnh

## 1. Thông tin thành viên

- Họ tên: DoanNhatAnh
- MSSV: 2A202603408
- Email: nhatanhdoan1@gmail.com
- GitHub: [nhatanh2901](https://github.com/nhatanh2901)
- Vai trò: Phần 3 — Orchestrator, handoff và bảo mật trace.

## 2. Phần việc phụ trách

- Triển khai shape C tại `src/lab8/shapes/orchestrator.py`.
- Dựng handoff bằng allowlist và giới hạn investigator ở các tool đọc.
- Giữ ranh giới giữa tính tiền bằng code, ghi tiền bằng host và soạn phản hồi bằng MockLLM.
- Kiểm tra trace không chứa ticket, parent context, secret hoặc thông tin cá nhân.
- Thêm test bảo mật; viết phần giải pháp orchestrator và khó khăn kỹ thuật trong báo cáo nhóm, phần trace và bằng chứng trong ADR.

## 3. Đóng góp cụ thể

- Đọc claim qua `get_claim_view`; xử lý claim không tồn tại (`failed`) và thiếu mã đơn (`needs_info`) trước khi giao việc.
- Tạo handoff bằng `make_handoff`, với `facts` rỗng và danh sách tool `lookup_order`, `lookup_policy`, `compute_compensation`. Không chuyển ticket hay parent context vào handoff.
- Gọi `run_readonly_investigators` với principal của claim để kiểm tra quyền xem đơn. Đơn không tồn tại hoặc không thuộc principal trả `escalated`.
- Lấy quote từ code `compute_compensation` dựa trên dữ kiện đơn và policy hiện hành. Không dùng số ngày trễ hoặc chỉ dẫn trong ticket để quyết định tiền.
- Truyền quote đầy đủ vào `durability.issue_refund`; host kiểm approval, trần theo đơn và idempotency. Không tự trừ khoản đã hoàn trước đó.
- Truyền `crash_at` vào host, không bắt `InjectedCrash`, đóng kết nối trong `finally`.
- Dùng `finish()` trên mọi nhánh trả kết quả bình thường để ghi trace và lấy refund effects/audit từ ledger. Trace chỉ ghi các event và field cần thiết.
- Chỉ dùng MockLLM để soạn phản hồi từ status và proposal đã được code quyết định.
- Thêm `src/tests/test_orchestrator_security.py` với ba ca kiểm thử bảo mật và nhánh trả về sớm.
- Commit chính: [158d999](https://github.com/Dovanngoc05/K5-L3A-DAY08-Random-FromWorkflowsToAgents/commit/158d999) — triển khai orchestrator, test bảo mật và báo cáo.

## 4. Bằng chứng

Các lệnh sau đã được trợ lý Codex chạy trong thư mục `src/` trong phiên thực hiện phần việc:

| Lệnh | Kết quả quan sát |
| --- | --- |
| `python -m pytest -q -m student -o addopts= -k orchestrator` | 62 passed, 240 deselected; chạy trước khi thêm file test bảo mật |
| `python -m pytest -q` | 57 passed, 248 deselected; gồm test host và ba ca kiểm thử mới |
| `git diff --check` | Không báo lỗi whitespace |
| `python -m lab8.smoke` | Chưa đạt do môi trường Python 3.10; yêu cầu Python 3.11+ |

Test thêm mới:

- `test_ticket_injection_cannot_cross_handoff_or_change_quote`: chèn chỉ dẫn giả, canary và PII giả vào ticket; kiểm tra handoff thực tế chỉ cấp tool đọc, quote không bị thay đổi, các file theo run id cùng kết quả và stdout/stderr không chứa chuỗi nhạy cảm đã chèn.
- `test_early_return_does_not_delegate_and_writes_trace`: hai ca claim không tồn tại và thiếu mã đơn; xác nhận không gọi investigator, không có refund và vẫn ghi trace khớp run id.

Bộ student có kiểm tra chạy lại claim và crash/resume. Chưa có benchmark đủ bốn shape, crash suite 20/20 hoặc kết quả hidden cho báo cáo này; không suy ra các số liệu đó từ kết quả pytest.

## 5. Công cụ AI đã dùng

Sử dụng ChatGPT/Codex để đọc yêu cầu lab, hỗ trợ triển khai orchestrator, viết test, chạy lệnh kiểm tra và soạn bản nháp báo cáo. Code lab dùng MockLLM có sẵn, không gọi model thật hoặc dùng API key.

Các kết quả kiểm thử ở trên do Codex thực thi và báo lại. Phần tự kiểm tra của cá nhân cần hoàn tất: đọc lại diff, giải thích luồng handoff/host/trace, chạy lại smoke và pytest trên Python 3.11–3.13, rồi đối chiếu kết quả trước khi nộp. Chưa ghi nhận các bước này là đã tự thực hiện.

## 6. Tự đánh giá

Phần triển khai và test hiện đã đáp ứng các ca public được chạy cho orchestrator. Test ticket injection bổ sung kiểm tra trực tiếp ranh giới handoff và artifact trace. Phạm vi bằng chứng hiện giới hạn ở dữ liệu public và các ca kiểm thử đã nêu; chưa có cơ sở kết luận về hidden hoặc ưu thế của orchestrator so với các shape khác. MockLLM không đại diện model sản xuất; latency là `unavailable`.

Các việc còn cần hoàn tất trước khi nộp:

- Tự đọc, chạy lại và giải thích được code cùng test trên Python 3.11–3.13.
- Đã tạo commit kỹ thuật `158d999` với tác giả Doan Nhat Anh; khi tích hợp cần giữ bằng chứng commit này trong lịch sử nhánh nộp.
- Phối hợp thành viên đánh giá chạy benchmark bốn shape và crash suite; cung cấp phân tích trace cho ADR, không tự điền số liệu chưa có.
- Kiểm tra báo cáo cùng cả nhóm, chạy `check_submission`, push và tự nộp link repo nhóm trên LMS.
