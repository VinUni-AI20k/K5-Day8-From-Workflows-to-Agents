# Báo cáo cá nhân — Chu Thân Nhất

## 1. Thông tin thành viên

- Họ tên: Chu Thân Nhất
- MSSV: 2A202603649
- Email: nhatthanchu@gmail.com
- GitHub: https://github.com/DuyDo1007/K5-L3A-DAY08-Warden-FromWorkflowsToAgents

## 2. Phần việc phụ trách

Triển khai Shape B (`single` ReAct agent) trong `src/lab8/shapes/single.py` và bổ sung kiểm thử tập trung cho shape này.

## 3. Đóng góp cụ thể

- Cài đặt luồng claim lookup, ReAct giới hạn 8 bước với các tool chỉ đọc, quote từ order row và policy, rồi gọi host `issue_refund` với toàn bộ quote.
- Bảo đảm mọi nhánh trả về đi qua `finish(...)`; chuyển tiếp `InjectedCrash` và ghi trace trước khi ném lại.
- Commit code và test: `bb013891c8919658136be99e2a8b2dc8850d641d`.
- Thêm `src/tests/test_single_shape.py` để kiểm tra quote dựa trên order row, trace ở các nhánh kết thúc sớm, và crash được truyền lên.

## 4. Bằng chứng

- Test mới: `tests/test_single_shape.py` — 4 passed.
- Bộ kiểm riêng single: `python -m pytest -q -m student -o addopts= tests/test_public_matrix.py -k 'single and not workflow and not orchestrator and not swarm'` — 62 passed, 186 deselected.
- Bộ kiểm mặc định: `python -m pytest -q` — 58 passed, 248 deselected.
- Run ID kiểm tra order-row quote: `R-single-C-002-s55`.

## 5. Công cụ AI đã dùng

Copilot SDK trong VS Code hỗ trợ triển khai và rà soát test. Đã kiểm tra lại diff, xác nhận giới hạn read-only/8 bước và chạy test mới cùng bộ kiểm riêng `single`.

## 6. Tự đánh giá

Hoàn thành phần shape `single` và kiểm thử các nhánh quan trọng; kết quả test xác nhận quote không phụ thuộc số ngày khách ghi trong ticket.
