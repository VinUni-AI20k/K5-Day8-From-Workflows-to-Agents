# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | ĐẠT (0.757 ≥ 0.6, 0.857 ≥ 0.8, 0.800 ≥ 0.7) | Dùng làm gate phụ (kèm hiệu chỉnh Rogan-Gladen) |
| helpful | 100 | 0.375 | 1.000 | 0.300 | KHÔNG ĐẠT (κ=0.375 < 0.6, Recall=0.3 < 0.7) | LOẠI (không dùng làm gate) |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú & Hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 (tone) | PASS | FAIL | Người đúng | Agent xưng "em" + "nha", quá suồng sã thiếu tính chuẩn mực CSKH B2C; judge nhầm là thân thiện. Cần sửa rubric: cấm dùng ngôi xưng "em/anh" và trợ từ thân mật "nha/nhé". |
| 2 | H-017 (tone) | PASS | FAIL | Người đúng | Agent xưng "bạn ơi... nha" với khách hàng; judge bỏ qua ngữ cảnh lịch sự chuẩn của LogiX. Cần sửa rubric: quy định đại từ nhân xưng chuẩn là "anh/chị" hoặc "quý khách". |
| 3 | H-029 (tone) | PASS | FAIL | Người đúng | Giọng điệu gắt gỏng ra lệnh ("không cần nhắn thêm"); judge bị đánh lừa bởi từ "Dạ, vui lòng chờ". Cần sửa rubric: cấm các mẫu câu mệnh lệnh phủ định gây ức chế cho khách hàng. |
| 4 | H-042 (tone) | FAIL | PASS | Người đúng | Câu trả lời ngắn gọn, đủ thông tin và lịch sự; judge phạt oan vì "thiếu lời xin lỗi". Cần sửa rubric: không bắt buộc xin lỗi với các ca thông báo đã hoàn tiền thành công. |
| 5 | H-051 (tone) | FAIL | PASS | Người đúng | Agent dùng từ "refund" (thuật ngữ e-commerce phổ biến và CSKH LogiX cho phép); judge phạt vì lẫn tiếng Anh. Cần sửa rubric: cho phép các thuật ngữ chuẩn ngành như "refund", "order", "tracking". |
| 6 | HL-015 (helpful) | PASS | FAIL | Người đúng | Reply báo hoàn 55.000đ nhưng sổ cái (ledger) chỉ ghi nhận 40.000đ. Judge chỉ đọc text trôi chảy nên cho PASS, không đối chiếu được ledger. Xác nhận: tiền và sự thật ledger PHẢI chấm bằng code, không dùng LLM Judge! |
| 7 | HL-016 (helpful) | PASS | FAIL | Người đúng | Reply hoa mỹ, xin lỗi lịch sự và báo hoàn 55.000đ nhưng ledger chỉ ghi 35.000đ. Judge bị đánh lừa bởi văn phong xin lỗi ngọt ngào. Khẳng định: LLM Judge bị mù trước sự thật nghiệp vụ (FM-08). |

## Kết luận
- **Tiêu chí bị loại**: `helpful` bị loại hoàn toàn khỏi release gate vì:
  - Ma trận nhầm lẫn: `{'tp': 9, 'fp': 0, 'fn': 21, 'tn': 70}`. Recall chỉ đạt $0.30$ (bỏ sót 21/30 ca lỗi, 70% số lỗi bị lọt!).
  - Hệ số $\kappa = 0.375 < 0.6$ (mức độ đồng thuận yếu).
  - Lý do cốt lõi: Judge chỉ phân tích văn bản (reply text), không kết nối với DB/ledger để kiểm tra tính đúng đắn của số tiền và điều khoản (FM-08 misreport). Do đó, lời văn trôi chảy và xin lỗi dài dòng dễ dàng qua mặt judge.
- **Tiêu chí được giữ**: `tone_ok` đạt chuẩn với $\kappa = 0.757$, Precision = $0.857$, Recall = $0.800$. Được sử dụng nhưng cần áp dụng công thức Rogan-Gladen để ước lượng tỷ lệ lỗi thật trong tổng thể (từ $28\%$ quan sát lên $30\%$ thực tế).
- **Rủi ro còn lại**: Bộ dữ liệu calibration hiện tại là replay tĩnh từ tập public; cần tiếp tục gán nhãn dữ liệu người dùng thật mới phát sinh để tạo tập held-out định kỳ.
