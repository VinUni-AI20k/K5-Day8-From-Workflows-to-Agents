# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Các số benchmark lấy từ `src/reports/benchmark.json`.

- Shape chọn: workflow
- Commit hash: 03f0731
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70/70 public trial)
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: 0 phát hiện trong public benchmark; grader hidden chính thức chưa chạy

## Vì sao shape này

Trên cùng 14 claim và 5 seed, workflow đạt pass rate và pass^5 bằng 1.000 như single và orchestrator. Workflow có cost/success thấp nhất (27.86 VND mô phỏng, so với 31.94 và 56.29), không phụ thuộc quyết định model, và có variance 0 trên public. Swarm rẻ hơn orchestrator nhưng pass thấp hơn (0.986) và seed variance lớn hơn do T02/seed 55. Vì vậy chọn workflow theo bằng chứng public.

## Có đáng đổi lấy multi-agent không

Chưa thấy tăng pass trên public để bù cost thêm cho multi-agent. Quyết định sẽ đổi nếu grader hidden cho thấy workflow dưới 0.75 hoặc orchestrator cải thiện độ đúng/ổn định đủ lớn để bù cost. Kết quả public không chứng minh được ngưỡng hidden.

## Trace và bằng chứng

Trace ghi run id, kết quả read tool đã lọc, quote, handoff đã sanitize, trạng thái và phản hồi host. Trace không ghi ticket, parent secret, raw headers, số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng. Scanner kiểm tra trace và output trong các trial public.

## Giới hạn

MockLLM, token cost và benchmark corpus là mô phỏng/fixture; latency không đo được. Báo cáo này ghi kết quả public, không thay cho grader hidden của giảng viên.
