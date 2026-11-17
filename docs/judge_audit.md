# Judge audit

Chạy:
- `python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 5`
- `python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có (κ=0.757≥0.6, P=0.857≥0.8, R=0.8≥0.7); RG: 0.28 → 0.30 | dùng |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không (κ=0.375<0.6, R=0.300<0.7); RG: 0.09 → 0.30 | loại |

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú |
|---|---|---|---|---|---|
| 1 | H-008 (`tone_ok`) | PASS | FAIL | Người đúng | Xưng "em" + "nha" quá suồng sã với khách; judge chỉ thấy giọng thân thiện. Bổ sung ví dụ negative về đại từ nhân xưng vào rubric `tone_ok`. |
| 2 | H-017 (`tone_ok`) | PASS | FAIL | Người đúng | Xưng "bạn" với khách hàng; cần quy định rõ trong rubric chỉ chấp nhận "anh/chị" + "LogiX". |
| 3 | H-029 (`tone_ok`) | PASS | FAIL | Người đúng | Câu "không cần nhắn thêm" mang tính ra lệnh; judge bị đánh lừa bởi cụm "Dạ, vui lòng" ở đầu câu. |
| 4 | H-042 (`tone_ok`) | FAIL | PASS | Người đúng | Câu trả lời ngắn gọn, lịch sự, đủ thông tin nhưng judge bắt lỗi khắt khe quá mức. Thêm ví dụ positive câu ngắn chuẩn mực vào rubric. |
| 5 | HL-015 (`helpful`) | PASS | FAIL | Người đúng | Reply báo hoàn `55.000đ` nhưng ledger chỉ ghi `40.000đ` (FM-08). Judge chỉ đọc text reply nên không thể kiểm tra đối chiếu ledger. |
| 6 | HL-016 (`helpful`) | PASS | FAIL | Người đúng | Reply xin lỗi dài dòng, lịch sự nhưng sai số tiền (`55.000đ` vs ledger `35.000đ`). Judge bị thiên kiến độ dài/lịch sự đánh lừa. |

## Kết luận
- **Tiêu chí bị loại:** `helpful` bị loại hoàn toàn khỏi gate vì ma trận nhầm lẫn cho thấy `tp=9, fp=0, fn=21, tn=70` — Recall chỉ đạt `0.300` (bỏ sót 21/30 ca lỗi thật) và `κ=0.375 < 0.6`. Do đó tỉ lệ lỗi quan sát chỉ là `0.09` trong khi tỉ lệ lỗi hiệu chỉnh Rogan-Gladen thực tế là `0.30`. Nguyên nhân gốc rễ: lỗi sai số tiền (FM-08) cần đối chiếu với `refund_ledger`, phải chấm bằng **code grader** (`ReplyLedgerMatch`), không thể dùng LLM judge chỉ đọc văn bản.
- **Tiêu chí được giữ lại:** `tone_ok` đạt cả 3 ngưỡng (`κ=0.757`, `P=0.857`, `R=0.800`), có thể dùng để theo dõi chất lượng văn phong sau khi bổ sung các trường hợp biên về xưng hô và giọng ra lệnh vào rubric.
- **Rủi ro còn lại:** judge chỉ được kiểm trên dữ liệu replay đã công khai; cần nhãn người mới để có tập held-out thật.
