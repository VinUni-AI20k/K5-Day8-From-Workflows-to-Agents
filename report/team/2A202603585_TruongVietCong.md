# Báo cáo cá nhân — MSSV_HoTen

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Trương Việt Công
- MSSV: 2A202603585
- Email: vietcongtruong07@gmail.com
- GitHub: congcoderht
- Nhánh làm việc: feature/single
## 2. Phần việc phụ trách

- Triển khai Shape B trong src/lab8/shapes/single.py, gồm vòng ReAct, ranh giới quyền đọc/ghi và trace.
- Viết bốn test riêng trong src/tests/test_team_single.py.
- Rà approval và trần hoàn tiền theo đơn trên ba shape sau merge. Viết mục Shape B trong báo cáo nhóm và cập nhật bảng đóng góp.-

## 3. Đóng góp cụ thể

Commit kỹ thuật cbc72cc,  chứa phần triển khai Shape B và bốn test riêng. run_react giới hạn vòng lặp tối đa 8 bước. Callback decide chọn tool từ kế hoạch đọc cố định gồm lookup_order, lookup_refund_history và lookup_policy. Ticket được đưa vào bước phân tích của MockLLM, còn dữ liệu đơn và chính sách hiện hành là đầu vào của phép tính bồi thường. Các lượt gọi model được tính vào Budget.

Shape dùng compute_compensation sau vòng lặp và truyền nguyên số tiền đề xuất vào issue_refund. Host là nơi duy nhất ghi refund và kiểm approval, áp trần theo đơn, xử lý retry dựa trên ledger. Tất cả nhánh trả kết quả đều ghi quyết định và dùng finish(). Khi xảy ra crash mô phỏng, shape ghi trace rồi ném lại InjectedCrash cho bên gọi.

## 4. Bằng chứng

Các lệnh chạy từ thư mục src/ tại bản tích hợp **cface9a**.

python -m pytest -q -m student -o addopts= -k 'single and not (workflow or orchestrator or swarm)'
python -m pytest -q tests/test_team_single.py

- Ma trận student riêng Shape B đạt 62 passed. Bộ lọc loại ba shape còn lại vì hàm test dùng chung có tên test_public_single_run_cases.
- Bộ test nhóm đạt 4 passed, kiểm C-002 qua 5 seed, retry C-011 chỉ tạo một dòng ledger, trace của các nhánh mẫu và giới hạn số lượt gọi model.
- [Benchmark public](../../src/reports/benchmark.json) ghi 70/70 trial pass, pass^5 100%, phương sai 0, chi phí mô phỏng 47,94 VND/lần thành công, mean/p95 trace steps 8,07/9. Run id đối chiếu: R-single-C-001-s11.
- Kiểm tra approval sau merge đạt 15/15 lượt (5 tình huống × 3 shape, seed 11). Bốn ca bị từ chối gồm approval bị thu hồi, approval hết hạn, approval của claim khác và đơn đã hoàn đủ. Tất cả có audit policy_denied và không ghi refund mới. Ca C-014 chỉ ghi thêm 120.000 VND để tổng tiền hoàn theo đơn đạt 150.000 VND.
- Tự kiểm hidden đang chờ bộ dữ liệu student_drop/.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc diff, chạy lại pytest, kiểm approval và soạn bản nháp từ mã nguồn cùng kết quả benchmark của nhóm. Các số liệu được đối chiếu với output kiểm thử và file JSON trong repo. Phần mô tả cách sử dụng AI trong quá trình viết code cần được xác nhận trước khi nộp.

## 6. Tự đánh giá

Bằng chứng hiện có cho thấy Shape B đáp ứng các ca public về dữ liệu ticket sai lệch, retry và crash/resume. Bước tự kiểm còn lại là chạy bộ student_drop/ và lưu src/reports/hidden_selfcheck.json khi có dữ liệu.
