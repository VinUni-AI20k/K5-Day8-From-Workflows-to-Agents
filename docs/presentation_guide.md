# Kịch bản thuyết trình — Problem Solver

Mở presentation/index.html trực tiếp; dữ liệu và SVG đã được nhúng local, không cần mạng hay API key. Chọn “Trình chiếu”, dùng nút trước/sau hoặc phím mũi tên để đổi mục; Esc để thoát. Bật “Gợi ý nói” nếu cần.

1. Quốc Anh (1 phút): mục tiêu chọn mức tự chủ vừa đủ, ranh giới code/model và host.
2. Bình (2 phút): max(ship, damage), missing order, principal, approval, cap theo đơn; phân biệt proposal và effect.
3. Hưng (2 phút): chọn Single trong “Luồng chi tiết”, đọc từ trái sang phải; vòng ReAct tối đa 8 lượt, crash/resume không trả trùng.
4. Vinh (2 phút): chọn Orchestrator rồi Host; investigator chỉ đọc, handoff allowlist. Dùng “Vừa chiều cao” để đọc, “Tiếp →” hoặc phím phải khi focus canvas để cuộn. “Xem trọn luồng” cho toàn cảnh; “Mở rộng” cho màn hình lớn.
5. Quốc Anh + Bình (2 phút): replay C-002 seed 55, ticket nói 5 ngày nhưng order 2; verifier sửa quote về 0. Chuyển Public B3 rồi Đối kháng B3 để chỉ ra chi phí đổi lấy kiểm chứng.
6. Vinh (1 phút): tra cứu trial fail của swarm, nguồn dữ liệu và run id. Kết luận workflow; hidden local 200/200 cho workflow, seed variance 0; phân biệt kết quả kiểm chứng và điểm chính thức, MockLLM và latency unavailable.

Mọi lệnh runtime chạy trong src/:

```text
python -m bonus.reproduce
python -m lab8.check_submission
```

Sinh lại báo cáo và HTML tại gốc repo:

```text
python scripts/build_lab_report.py
python -m presentation.build
```

Các số liệu chỉ được tạo bởi công cụ; không sửa tay JSON. Khi đổi code kỹ thuật, commit rồi chạy lại benchmark và sinh lại báo cáo để hash, run id và dữ liệu khớp nhau. Các thành viên tự xác nhận báo cáo cá nhân và đóng góp trước khi nộp LMS.

## Trình bày kết quả hidden

Chọn bộ Hidden trong Benchmark: 40 claim × 5 seed × 5 shape. So workflow 200/200 và swarm 194/200, rồi swarm + verifier 200/200. Nêu chi phí tăng, safety 0 leak/bypass và crash hidden 30/30. Dùng báo cáo hidden_validation.md để giải thích --labels và provenance. Đồ thị tiếp tục đọc từ trái sang phải.
