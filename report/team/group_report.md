# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: NhomDMTG
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`): 1f4bca2

## 2. Mục tiêu và cách tiếp cận

Bài toán LogiX-VN yêu cầu xử lý khiếu nại hoàn phí vận chuyển qua bốn kiến trúc với mức tự chủ tăng dần (`workflow`, `single`, `orchestrator`, `swarm`), giữ nguyên chữ ký giao diện, đồng thời đảm bảo tiền và quyền duyệt luôn thuộc về code và cổng host chứ không giao cho model.

Nhóm chia 4 đầu việc song song: Hồng Gấm phụ trách `workflow` và tích hợp; Đinh Lê Thịnh phụ trách `single` ReAct có giới hạn bước; Nguyễn Xuân Dương phụ trách `orchestrator` với gói bàn giao allowlist; Trần Duy Mạnh phụ trách kiểm định an toàn sổ cái, bộ crash 20 điểm, bộ test chuẩn nộp bài, chạy benchmark và tổng hợp báo cáo. Thứ tự thực hiện đi từ đọc hợp đồng dữ liệu và cổng host (CP1), cài đặt ba kiến trúc (CP2), hoàn thiện bàn giao an toàn và chống trùng khi crash (CP3–CP4), rồi đo lường bốn kiến trúc trên cùng biến kiểm soát để ra quyết định kiến trúc (CP5).

## 3. Giải pháp

- **Shape A (`workflow`):** Thực thi tuần tự cố định bằng Python: đọc thông tin claim đã lọc secret, kiểm tra mã đơn, tra cứu đơn hàng thuộc quyền sở hữu của người gửi, tính mức bồi thường xác định từ dữ liệu đơn và policy hiệu lực, gọi `MockLLM` 1 lần để soạn câu trả lời mẫu rồi mới gọi host ghi hoàn tiền nếu số tiền > 0.
- **Shape B (`single`):** Dùng vòng lặp ReAct giới hạn tối đa 8 bước với chế độ worker chỉ đọc (`worker=True`). Trong vòng lặp, agent chỉ gọi công cụ đọc đơn hàng và tính mức bồi thường; sau khi vòng lặp kết thúc, phần code bên ngoài mới gọi host để ghi hoàn tiền với mức quote đầy đủ.
- **Shape C (`orchestrator`):** Điều phối viên gọi model lập kế hoạch, đóng gói ngữ cảnh qua bộ tạo bàn giao allowlist (chỉ gồm công cụ đọc, không chứa `parent_secret`, `raw_headers` hay toàn bộ dòng claim), giao cho nhánh điều tra chỉ đọc chạy lấy đơn/policy/quote, rồi điều phối viên gọi host ghi hoàn tiền.
- **Ranh giới code / model & an toàn trace:** Dữ liệu trong `ticket` luôn bị coi là dữ liệu người dùng không đáng tin (chống khai khống số ngày trễ, viện dẫn policy cũ `SHIP-LATE-OLD`, hoặc prompt injection). Mọi kiến trúc chỉ ghi các event đã lọc vào `traces/<run_id>.json`, bỏ qua thông tin cá nhân (SĐT, địa chỉ, tên hàng, ghi chú nội bộ), và luôn ghi lại sự kiện crash trước khi ném lỗi để phục vụ kiểm toán sau sự cố.

## 4. Kết quả

Bảng so sánh 4 kiến trúc trên bộ public (`src/reports/benchmark.json`, 14 claim × 5 seed `11, 22, 33, 44, 55` = 70 trial mỗi shape):

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost / success (VND) | Mean / p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| `workflow` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 28.87 | 2.79 / 3.00 |
| `single` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 29.13 | 6.21 / 7.00 |
| `orchestrator` | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 57.04 | 3.71 / 4.00 |
| `swarm` | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3.00 |

- **Crash safety (`src/reports/crash.json`):** Đạt `20/20` (vượt qua cả 20 kịch bản crash ở `before_effect`, `after_effect_before_checkpoint`, `after_checkpoint`, xung đột số tiền khi gọi lại, từ chối thiếu approval khi thử lại, và resume của shape đối chứng).
- **Kiểm thử tự động:** Cổng host + test đơn vị + kiểm tra chuẩn nộp bài (`pytest -q`) và ma trận 14 claim public (`pytest -m student`) đều xanh; `python -m lab8.check_submission` đạt `0 FAIL`.
- **Quyết định kiến trúc & nghiên cứu:** Nhóm chọn `workflow` (chi tiết tại `report/team/decision_adr.md`) và hoàn thành thí nghiệm đối chứng kiến trúc R3 (chi tiết tại `report/team/research_card.md`).

## 5. Khó khăn và cách xử lý

1. **Môi trường Python mặc định trên Windows (`3.14.5`) mới hơn ngưỡng hỗ trợ (`3.11–3.13`):** Đã chỉ định rõ `py -3.12 -m venv .venv` trong `src/` để đồng bộ môi trường chuẩn.
2. **Thiếu lưu vết trace khi xảy ra `InjectedCrash` ở `workflow` và `single`:** Ban đầu hai shape cho lỗi crash văng thẳng ra ngoài nên file trace tại thời điểm crash chưa được ghi xuống đĩa. Đã bổ sung khối ghi nhận event crash và lưu trace trước khi ném lại lỗi.
3. **Báo cáo ngân sách & khóa quyền worker:** Bổ sung cờ `worker=True` cho `single` để khóa công cụ ghi ở tầng runtime, bổ sung gọi model lập kế hoạch/soạn câu trả lời cho `orchestrator` và `workflow` để số đo chi phí phản ánh đúng kiến trúc, đồng thời tách test riêng cho `workflow` ra khỏi file ma trận đề bài.

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` (bảng đóng góp) và báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency là `unavailable`, và chi phí token chỉ mang tính mô phỏng từ `config/pricing.yaml`. Kết quả `1.000` hiện mới xác nhận trên 14 tình huống public; bộ hidden 40 claim do giảng viên chấm độc lập sẽ kiểm chứng thêm các biến thể biên (homoglyph, injection phức tạp). Khi bài toán mở rộng sang yêu cầu tra cứu động nhiều hệ thống ngoài quy trình cố định, nhóm có thể chuyển sang `single` hoặc `orchestrator` nhưng vẫn giữ nguyên cổng host kiểm duyệt và khóa ghi sổ cái một giao dịch.

## 8. Tài liệu tham khảo

- Tài liệu bài lab: `README.md`, `SUBMISSION.md`, `RULES.md`, `RUBRIC.md`, `docs/business_rules.md`, `docs/contracts.md`, `docs/architecture.md`, `docs/metrics.md`.
- Tài liệu nghiên cứu tham khảo (slide 68–69): AgentArch (AACL 2026); MAST (NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?*); *Towards a Science of Scaling Agent Systems* (Google Research 2026); *Rethinking Evaluation of MAS Efficiency* (EMNLP 2026).
