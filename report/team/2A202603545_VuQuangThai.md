# Báo cáo cá nhân — 2A202603545_VuQuangThai

## 1. Thông tin thành viên

- Họ tên: Vũ Quang Thái
- MSSV: 2A202603545
- Email: qtvu2k5@gmail.com
- GitHub: vuThai05

## 2. Phần việc phụ trách

- Tạo repo nhóm (fork repo đề bài về `K5-L3A-DAY08-4H45-FromWorkflowsToAgents`).
- CP2: viết shape B `single` (`src/lab8/shapes/single.py`) — vòng ReAct tối đa 8 bước qua `lab8.runtime.run_react` với `worker=True`.
- CP4: tham gia xử lý phần approval hợp lệ trong luồng xử lý claim.
- Tham gia đánh giá, nhận xét các PR trong nhóm.

## 3. Đóng góp cụ thể

- Commit `16496be` ("single content"): viết đầy đủ `single.py` theo docstring — `decide()` đi theo chuỗi tool cố định (`get_claim_view → lookup_order → compute_compensation`), số tiền lấy từ `compute_compensation`, model không tự quyết.
- Viết lại `report/team/research_card.md` (câu R4, sau đó chỉnh sang các trường SOURCE/HYPOTHESIS có trích nguồn và link cụ thể).

## 4. Bằng chứng

- Commit `16496be` trên nhánh `thai` (đã merge vào `main` qua PR #2).
- `python -m pytest -q -m student -k "single]"` chạy trên commit này pass 62/62 (đã được xác minh lại trong quá trình review PR #2).

## 5. Công cụ AI đã dùng

*(Mục này do Thái tự điền — ghi rõ công cụ đã dùng, dùng vào việc gì, và cách đã tự kiểm tra lại kết quả, theo [RULES.md](../../RULES.md). Không được AI tự bịa hộ phần này.)*

## 6. Tự đánh giá

*(Mục này do Thái tự viết — nhìn lại phần mình phụ trách, điểm làm tốt, điểm cần cải thiện.)*
