# Decision record

- Shape chọn: workflow
- Commit hash: 3614266 (implementation and generated evidence)
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (`reports/benchmark.json`, 70 trials)
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: No leak or bypass detected in host, public student, trace and crash checks; hidden grader not run.

## Vì sao shape này

Chọn workflow cho nhóm claim hoàn phí này vì workflow đạt 70/70 trial, pass^5 = 1.000 và cost/success mô phỏng thấp nhất (27.86 VND). Single và orchestrator cũng đạt 70/70 nhưng tốn lần lượt 31.54 và 46.43 VND/success. Swarm đạt 69/70, pass^5 = 0.929, variance = 0.000816 và tốn 49.57 VND/success. Kết quả dùng cùng 14 claim, 5 seed, MockLLM, tool price và evaluator; đây là bằng chứng trong fixture của lab, không phải kết luận cho tác vụ khác.

## Có đáng đổi lấy multi-agent không

Trong corpus này, orchestrator không cải thiện pass rate so với workflow và tốn thêm khoảng 66.7% mỗi lần thành công. Swarm có thêm một lỗi ở C-002 seed 55: tin số ngày trong ticket thay vì order. Multi-agent chỉ đáng cân nhắc lại nếu workload có nhiều phần việc độc lập mà investigator tăng độ đúng đủ để bù chi phí, và kết quả được xác nhận trên workload đại diện mới.

## Trace và bằng chứng

Trace ghi các bước đã allowlist như claim/order identifiers, order fields được phép, quote, handoff đã lọc và quyết định; không ghi ticket nguyên văn, principal ID, raw headers, parent secret, địa chỉ, số điện thoại hay ghi chú nội bộ. Handoff được dựng bằng `make_handoff`; worker chỉ nhận tool đọc. Bằng chứng hiện có là các test host/public và crash suite. Hidden grader không có trong workspace nên chưa thể kết luận về hidden set.

## Giới hạn

MockLLM không phải model sản xuất; chi phí là mô phỏng VND và latency không khả dụng. Public benchmark chỉ có 14 claim × 5 seed. Chưa chạy hidden self-check. Thành viên cần xác nhận attribution, cá nhân cần bổ sung báo cáo và nhóm cần thay nhãn commit sau code commit cuối.
