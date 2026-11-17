# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: f176005 (commit mã nguồn tại thời điểm chạy benchmark; cần giữ hash này làm mốc mã đã đo)
- Run id dẫn chứng: R-workflow-C-001-s11 (một trial đại diện; benchmark ghi run_id riêng cho từng trial)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70/70 trial public)
- Cost per success (mô phỏng, VND): 28.87
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: hidden-grade counts chưa có; chỉ giảng viên có report hidden chính thức

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng bộ public 14 claim và năm seed, workflow, single và orchestrator đều đạt 70/70 trial,
pass rate 1.000, pass^5 1.000 và variance theo seed bằng 0. Swarm đạt 69/70 (pass rate 0.986,
pass^5 0.929), với lỗi `status resolved != denied` ở seed 55. Trong ba shape của nhóm, workflow
có cost/success mô phỏng thấp nhất: 28.87 VND so với 46.43 của orchestrator và 54.65 của
single. Vì độ chính xác public bằng nhau, chọn workflow theo tiêu chí chi phí và tính đơn giản
của luồng. Đây là quyết định dựa trên public benchmark, chưa thay thế cổng hidden: nếu workflow
không đạt hidden pass rate 0.75 hoặc vi phạm must-pass, nhóm phải đổi lựa chọn.

## Có đáng đổi lấy multi-agent không

Trên public corpus này, multi-agent không tăng pass rate so với workflow. Orchestrator dùng ít
event hơn trung bình (2.79 so với 4.43) nhưng cost/success cao hơn. Số event không phải latency;
latency được ghi `unavailable`, do đó không kết luận multi-agent nhanh/chậm hơn. Nhóm chỉ nên
đổi lựa chọn nếu hidden evaluation hoặc một benchmark được kiểm soát cho thấy shape khác vượt
workflow mà vẫn qua toàn bộ safety gate.

## Trace và bằng chứng

Theo implementation workflow hiện tại, trace ghi claim id/trạng thái tìm thấy/order id, order
đã qua allowlist, quote, verdict host, quyết định và crash nếu có. Trace không ghi ticket text,
raw claim row, approval hay host effect row; các field nhạy cảm này bị loại để tránh lộ secret
hoặc PII. Benchmark report không thay thế hidden leak scanner của giảng viên; số leak/bypass
hidden chính thức hiện chưa có.

## Giới hạn

MockLLM không phải model sản xuất; giá là mô phỏng và latency `unavailable`. Public set chỉ có
14 claim. Người dùng xác nhận đã chạy lại benchmark trong `.venv`; phiên bản Python và output
console lần chạy lại chưa được lưu trong phiên này. Hidden grade không có trong repository nên
lựa chọn workflow chỉ dựa trên public data, không phải khẳng định đã qua hidden gate. Không sửa
JSON bằng tay để đạt ngưỡng.
