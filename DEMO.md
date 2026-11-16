# LogiX VN — UI demo

Dashboard offline cho Lab 8, dùng code shape và dữ liệu thật của repo. Không cần cài thư viện mới, Node.js hoặc API key.

## Mở demo

Windows: nhấp đúp `demo.cmd` ở gốc repo. Giữ cửa sổ đó mở trong lúc trình bày; nhấn `Ctrl+C` để dừng server.

Hoặc chạy PowerShell từ gốc repo:

```powershell
cd src
.\.venv\Scripts\python.exe -m demo_ui.server --open
```

Trình duyệt mở tại **http://127.0.0.1:8765**. Nếu cổng đang được dùng, chạy với `--port 8766 --open`. macOS/Linux dùng Python của môi trường lab: `python -m demo_ui.server --open` trong `src/`.

## Nội dung trình bày

| Khu vực | Nội dung |
| --- | --- |
| Bài chính | Bốn kiến trúc trên cùng claim, ticket đối chiếu dữ liệu đơn, quote và tiền thực hoàn, tool/model/cost, trace và ledger |
| Bonus B3 | Thí nghiệm riêng: swarm gốc, swarm có verifier và workflow; quote trước/sau sửa, năm trường verifier đối chiếu, public và bộ đối kháng |
| Bằng chứng | Biểu đồ pass rate, cost/success, bảng pass^5/variance/steps, safety và tải JSON gốc; có tab tách bài chính/B3 |

Kịch bản trình bày khoảng 5 phút:

1. **Bài chính → Hoàn phí hợp lệ**: cùng C-001, bốn kiến trúc đều đề xuất và hoàn đúng 35.000 VND. Chọn từng card để xem luồng và trace.
2. **Hoàn phần chênh**: C-014 đề xuất 150.000 VND, host chỉ ghi 120.000 VND vì trước đó đã hoàn 30.000 VND.
3. **Crash & resume**: quan sát bảng ledger sau crash, resume và retry. Cùng claim vẫn một refund, một audit committed.
4. **Bonus B3 → Nói quá ngày trễ**: C-002, seed 55. Swarm gốc hoàn sai 20.000 VND; verifier đối chiếu dữ liệu đơn, sửa quote về 0 trước khi ghi tiền. Thử thêm “Nói thiếu ngày trễ”.
5. **Bằng chứng**: so số liệu giữa bài chính và bonus, nêu rõ chi phí verifier cao hơn workflow và giới hạn MockLLM.

Nút ở góc phải bật chế độ trình chiếu. Phím `1`, `2`, `3` đổi khu vực; `R` chạy lại; `Esc` thoát trình chiếu. Nút **Hướng dẫn** mở dàn ý ngay trong UI. **Phát lại** chỉ phát trace của lượt đã hoàn thành, không giả lập tiến độ chạy model.

## Dữ liệu và cách chạy

- Bấm **Chạy demo** sẽ thực thi shape thật trong subprocess, với SQLite và trace tạm riêng. Trong một kịch bản retry/resume, các lần gọi dùng chung database; yêu cầu demo tiếp theo bắt đầu lại từ fixture.
- UI không ghi đè báo cáo nộp bài. Biểu đồ đọc các file hiện có trong `src/reports/`; tải lại trang sau khi sinh báo cáo mới.
- Quote và effect lấy từ kết quả/ledger, pass lấy từ evaluator chính thức và nhãn fixture. Cột “Đáp án theo luật” là nhãn dùng để đối chiếu, không phải kết quả vừa chạy.
- Khi claim không đi tới ghi refund, điểm crash không được kích hoạt; UI nêu rõ. Dùng C-001 hoặc C-012 để demo crash.
- Chỉ trả các trường được phép của đơn thuộc principal; không phục vụ database, fixture thô, secret, header hoặc PII. Server chỉ nghe trên loopback của máy.
- Các báo cáo benchmark và bonus đã được tạo sẵn trong repo. Muốn cập nhật B3, chạy `python -m bonus.evaluate` trong `src/`, sau đó tải lại trang. Điểm hidden/bonus chính thức do grader giảng viên xác nhận.
