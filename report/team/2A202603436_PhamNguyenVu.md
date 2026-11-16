# Báo cáo cá nhân — 2A202603436_PhamNguyenVu

## 1. Thông tin thành viên

- Họ tên: Phạm Nguyên Vũ
- MSSV: 2A202603436
- GitHub: `phamvu65`

## 2. Phần việc phụ trách

Shape B (`single`) trong `src/lab8/shapes/single.py`, gồm vòng ReAct, xử lý kết quả và kiểm thử hành vi hoàn tiền.

## 3. Đóng góp cụ thể

- Commit `22387b7` triển khai `run_claim`. Hàm `decide` mô phỏng chọn hành động theo quan sát từ tool, còn MockLLM ghi nhận chi phí từng lượt vào `Budget`. Vòng ReAct chạy tối đa 8 bước với các tool chỉ đọc.
- `compute_compensation` tính quote từ đơn hàng và chính sách hiện hành. Shape chuyển nguyên quote cho `issue_refund` để host kiểm tra approval, trần theo đơn và ghi ledger. `crash_at` được chuyển tới host để kiểm tra retry sau crash.
- Trace ghi tên tool và kết quả quyết định. Test `test_single_keeps_untrusted_ticket_out_of_trace` chèn chỉ dẫn và một canary vào ticket, sau đó kiểm tra số tiền, giới hạn gọi model và nội dung trace/stdout.

## 4. Bằng chứng

- Ma trận student riêng cho `single`: **62 passed**, gồm T11 (retry) và T12 (crash rồi chạy lại).
- Bộ test host: **55 passed**, gồm test mới trong `src/tests/test_single_agent.py`.
- Benchmark riêng `single` trên 14 claim public × 5 seed (`11,22,33,44,55`): **70/70** trial pass, `pass^5 = 1.0`, `seed_variance = 0`, chi phí mô phỏng **29,46 VND/lượt thành công**. Run ID ví dụ: `R-single-C-014-s11`.

Lệnh tái tạo benchmark từ `src`:

```powershell
python -m lab8.benchmark --shapes single --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out .pytest_cache/single-benchmark.json
```

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc contract, viết code và test, chạy ma trận student, bộ test host và benchmark public. Kết quả ở trên lấy từ các lệnh đã chạy trong repo.

## 6. Tự đánh giá

Kết quả kiểm thử hiện tại giới hạn ở dữ liệu public và MockLLM. Thành viên bổ sung nhận xét cá nhân và cách tự kiểm tra kết quả trước khi nộp.
