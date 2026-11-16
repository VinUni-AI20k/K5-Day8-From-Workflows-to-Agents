# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.

- Shape chọn: workflow
- Commit hash: ebd88eb
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0 trên bộ public; hidden chưa được chấm

## Vì sao shape này

Chọn workflow vì trên cùng 14 claim × 5 seed, workflow đạt pass rate 1.000 và pass^5 1.000, bằng single và orchestrator, nhưng có cost/success thấp nhất (27.86 VND mô phỏng; single 47.85, orchestrator 61.51). Workflow cũng có variance bằng 0 và chỉ 3.50 bước trung bình. Đây là quyết định cho bộ public và MockLLM; cần xem lại nếu hidden hoặc dữ liệu thật cho thấy các claim cần xử lý ngôn ngữ linh hoạt hơn.

## Có đáng đổi lấy multi-agent không

Trong lần đo này, không: orchestrator không tăng pass rate so với workflow nhưng tốn khoảng 2.21 lần cost/success và cần thêm handoff. Quyết định có thể đổi nếu hidden hoặc một bộ dữ liệu đại diện hơn cho thấy investigator giúp giảm lỗi đủ nhiều để bù chi phí, hoặc nếu yêu cầu triển khai tách ranh giới tin cậy.

## Trace và bằng chứng

Trace ghi các bước đọc claim/order, handoff đã sanitize, số policy, quote và quyết định an toàn. Cố ý không ghi ticket, parent secret, raw headers, principal ID, số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng để giảm rò dữ liệu cá nhân và bí mật. Benchmark public báo 70/70 trial workflow hợp lệ; crash suite đạt 20/20. Chưa có kết quả grader hidden.

## Giới hạn

MockLLM không đại diện model sản xuất; cost là giá mô phỏng và latency là `unavailable`. Benchmark có 14 claim public, không đủ để suy rộng cho mọi dạng claim. Hidden chưa được chạy vì workspace hiện không có `student_drop/` hay grader của giảng viên. Không sửa JSON report bằng tay.
