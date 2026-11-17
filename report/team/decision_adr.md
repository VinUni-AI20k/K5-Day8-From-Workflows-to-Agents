# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Các số benchmark lấy từ `src/reports/benchmark.json`.

- Shape chọn: workflow
- Commit hash: 0f3c523
- Run id dẫn chứng: R-workflow-C-001-s11
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000–1.000 / 0.000000 (70/70 public trial)
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (`src/reports/crash.json`)
- Secret leak / approval bypass: 0 phát hiện trong public benchmark (`secret_leak_count` = 0, `approval_bypass_count` = 0)

## Vì sao shape này

Trên cùng 14 claim public và 5 seed (`11, 22, 33, 44, 55`), `workflow`, `single` và `orchestrator` đều đạt `pass_rate = 1.000`, `pass^5 = 1.000` và `seed_variance = 0.000000`. Tuy nhiên, `workflow` đạt `cost_per_success_vnd` thấp nhất (`27.86 VND` mô phỏng so với `31.94 VND` của `single` và `56.29 VND` của `orchestrator`), số bước trung bình thấp (`3.43`, p95 `4`), và hoàn toàn không phụ thuộc vào dao động của model. Trong khi đó, `swarm` tham chiếu có `pass_rate = 0.986`, `pass^5 = 0.929`, `seed_variance = 0.000816` do tin vào số ngày trễ trong câu chữ ticket ở T02/seed 55. Theo nguyên tắc chọn kiến trúc ít tự chủ nhất mà vẫn hoàn thành công việc tin cậy, nhóm chọn `workflow`.

## Có đáng đổi lấy multi-agent không

Không đáng đổi trên bài toán hiện tại: việc tăng mức tự chủ lên `single` hoặc multi-agent (`orchestrator`, `swarm`) làm tăng chi phí mô phỏng thêm 14.6%–102.0% nhưng không tăng `pass_rate` hay `pass^5`. Quyết định này chỉ đảo ngược khi cấu trúc bài toán thay đổi: (1) dữ liệu đầu vào thực sự cần suy luận ngữ nghĩa phức tạp hoặc chọn công cụ động khiến luồng cố định của `workflow` có `pass_rate` giảm xuống dưới ngưỡng yêu cầu, và (2) kiến trúc `single`/`orchestrator` chứng minh được mức tăng `pass^5` đủ lớn trên cùng corpus và cùng seed để bù đắp chi phí gọi model và độ phức tạp kiểm soát biên bảo mật.

## Trace và bằng chứng

Trace tuân thủ `Trace contract v1` (`run_id` khớp `RunResult.run_id`, danh sách `events` được ghi mới trong mỗi lần chạy). Các event được ghi gồm: kết quả tra cứu đã qua allowlist (`claim` chỉ lấy `found, claim_id, order_id`; `order` chỉ lấy `visible, reason, order` với 7 trường `ORDER_FIELDS`), gói `handoff` đã qua `sanitize`, kết quả `quote` từ `compute_compensation`, quyết định `decision`, phản hồi cổng `host` (`ok, reason`), và sự kiện `crash` nếu có. Trace cố ý **không** ghi raw claim row (`parent_secret`, `ticket`), raw headers, hay thông tin cá nhân trong order (`phone`, `address`, `item_name`, `internal_note`). Nếu trace nằm ngoài thư mục scanner quét được hoặc bị lỗi định dạng, hệ thống áp dụng cơ chế **fail-closed**: coi mọi log không kiểm chứng được là rủi ro rò rỉ và đánh trượt trial (`missing_trace`, `stale_trace`, `invalid_trace`, `trace_run_id_mismatch`).

## Giới hạn

MockLLM là bộ sinh tất định theo seed, không phản ánh đầy đủ hành vi suy luận hay hallucination của model sản xuất; `cost_estimate` là chi phí VND mô phỏng theo `config/pricing.yaml`; `latency` để `unavailable`. Kết quả trên 14 claim public không thay thế cho bộ chấm hidden 40 claim của giảng viên.
