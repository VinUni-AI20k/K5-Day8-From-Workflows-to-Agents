# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Tên nhóm: 4AnhEm
- Thành viên: bốn thành viên ghi trong `TEAM.md`; GitHub issue #1 đã đóng sau khi ghi nhận danh tính.
- Commit mã nguồn và bằng chứng benchmark: `3614266`; nội dung báo cáo được cập nhật trong các commit tiếp theo.

## 2. Mục tiêu và cách tiếp cận

So sánh workflow, tác tử đơn ReAct, orchestrator và swarm trên cùng yêu cầu, seed, dữ liệu thế giới, chính sách giá và bộ đánh giá. Mã host quyết định số tiền, approval, quyền sở hữu, giới hạn hoàn tiền theo đơn, tính lặp an toàn và ghi sổ. Shape không tự ghi refund; phải gửi đầy đủ báo giá để host áp dụng giới hạn.

## 3. Giải pháp

- **Workflow:** đọc phần claim view được phép, tra đơn theo chủ thể, tính báo giá từ dữ liệu đơn và chính sách hiện hành, rồi gọi host. Không dùng nội dung phiếu để tính tiền.
- **Single:** chạy vòng ReAct tối đa 8 bước với công cụ chỉ đọc; model không có công cụ ghi. Báo giá lấy từ công cụ tính trong mã, sau đó shape gọi host.
- **Orchestrator:** tạo handoff theo allowlist, chỉ cấp công cụ đọc cho investigator và chỉ ghi handoff đã lọc vào trace; orchestrator chuyển báo giá cho host.
- **Swarm:** shape tham chiếu để đối chứng. Với seed chia hết cho 5, shape này cố ý tin số ngày ghi trong phiếu; điểm yếu xuất hiện ở C-002, seed 55.

Trace không chứa nguyên văn phiếu, mã chủ thể, thông tin liên hệ, ghi chú nội bộ, header thô hoặc canary secret. Handoff chỉ chứa tác vụ, mã yêu cầu/claim, facts được allowlist và tên công cụ đọc.

## 4. Kết quả

Nguồn số liệu: `src/reports/benchmark.json` (14 yêu cầu × 5 seed, 70 lượt/shape) và `src/reports/crash.json`.

| Kiến trúc | Tỷ lệ đạt | Pass^5 | Seed thấp–cao | Phương sai | Chi phí/lần đạt (VND mô phỏng) | Bước trung bình / p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Workflow | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 27.86 | 2.86 / 3 |
| Single | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 31.54 | 2.79 / 3 |
| Orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0.000000 | 46.43 | 3.71 / 4 |
| Swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 |

Bộ kiểm tra crash đạt 20/20. Cổng kiểm tra host: 54 đạt. Ma trận student: 248 đạt. Bộ kiểm tra hồ sơ báo 0 lỗi, 0 cảnh báo. Chọn workflow vì tỷ lệ đạt tương đương các shape khác nhưng chi phí thấp nhất trên bộ dữ liệu này. Xem chi tiết và giới hạn trong `decision_adr.md`; phép so sánh kiến trúc ở `research_card.md`.

## 5. Khó khăn và cách xử lý

Ba shape ban đầu là stub. Đã triển khai theo contract, chuyển tiếp điểm crash vào durability và giữ host làm nơi duy nhất ghi refund. Kết quả được kiểm tra bằng cổng host, toàn bộ ma trận student, benchmark và crash suite. Trace không ghi nguyên văn nội dung phiếu.

## 6. Tổng hợp đóng góp

Cả bốn thành viên cùng thực hiện các phần việc và kiểm tra. Nguyen Quoc Viet là nhóm trưởng. Bảng đóng góp và bốn báo cáo cá nhân trong `TEAM.md` / `report/team/` ghi nhận phần việc chung, cùng commit và kết quả kiểm tra.

## 7. Hạn chế và hướng cải thiện

MockLLM không đại diện cho mô hình sản xuất; giá là mô phỏng bằng VND và không có số đo độ trễ. Bộ dữ liệu public chỉ có 14 yêu cầu và 5 seed; chưa chạy hidden grader/tự kiểm tra hidden. So sánh shape là so sánh các triển khai đầy đủ, chưa cô lập riêng ảnh hưởng của topology. Cần kiểm tra thêm trên dữ liệu đại diện và xác nhận kết quả hidden trước khi khái quát kết luận.

## 8. Tài liệu tham khảo

- Bogavelli, T., Subramani, H. và Sharma, R. (2026). *AgentArch: A Benchmark for Evaluating Agent Architectures in Enterprise Workflows*. AACL-IJCNLP 2026. https://aclanthology.org/2026.aacl-long.44/
