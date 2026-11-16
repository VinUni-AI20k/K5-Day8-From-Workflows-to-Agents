# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn:
- Commit hash:
- Run id dẫn chứng:
- Pass rate / pass^5 / seed min-max / variance:
- Cost per success (mô phỏng, VND):
- Crash safety:
- Secret leak / approval bypass:

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Viết 1 đoạn. So cùng corpus và cùng seed, không so với một lần chạy lẻ.

## Có đáng đổi lấy multi-agent không

Nếu pass nhỉnh hơn mà cost và variance cao hơn, nhóm giữ hay đổi? Điều kiện nào làm quyết định đảo lại?

## Trace và bằng chứng

Trace của nhóm ghi những event nào? Field nào cố ý **không** ghi, và vì sao? Nếu trace nằm ngoài chỗ scanner quét được, đội security chứng minh thế nào là hệ thống không lộ secret?

Đối với orchestrator, trace được ghi bằng `Trace` và `finish()`, có `run_id` khớp kết quả. Tùy nhánh, các event gồm `handoff`, `investigator`, `quote`, `decision`. Handoff qua allowlist, không chứa ticket hay parent context; investigator chỉ ghi visibility, reason và số policy. Không ghi secret, headers, principal context, số điện thoại, địa chỉ, tên hàng hoặc ghi chú nội bộ. Shape không tạo log phụ và không in dữ liệu ra stdout. Test `test_ticket_injection_cannot_cross_handoff_or_change_quote` kiểm tra handoff thực tế, các file có tiền tố run id, kết quả và stdout/stderr với ticket được cài canary/PII giả. Đây là bằng chứng cho các ca đã thử, chưa phải kết quả hidden hay bằng chứng an toàn tuyệt đối.

## Giới hạn

MockLLM không phải model sản xuất. Latency để `unavailable`. Không sửa JSON cho đủ 0.75.
