# Báo cáo cá nhân — Nguyễn Tiến Đạt

## 1. Thông tin thành viên

- Họ tên: Nguyễn Tiến Đạt
- MSSV: 2A202603922
- Lớp: L3B
- Email: ntdkhongdeptrailam5924@gmail.com
- GitHub: duhocsinh4to10

## 2. Phần việc phụ trách

Triển khai và tích hợp ba shape `workflow`, `single`, `orchestrator`; thêm kiểm tra cho claim không tồn tại.

## 3. Đóng góp cụ thể

- Commit triển khai và bằng chứng benchmark: `7b108e8`.
- Dùng `finish()` để tạo `RunResult`/trace; giữ toàn bộ quyết định tiền và ghi ledger ở host.
- Thêm `src/tests/test_shape_unknown_claim.py` cho bốn shape.

## 4. Bằng chứng

- `python -m pytest -q`: 54 passed.
- `python -m pytest -q -m student -o addopts=`: 252 passed.
- Smoke pass; crash suite `20/20`.
- Benchmark run id `R-workflow-C-001-s11`; số liệu trong `src/reports/benchmark.json`.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc yêu cầu, triển khai code và soạn báo cáo. Kết quả được kiểm tra bằng smoke, hai bộ pytest, benchmark và crash suite; mã và số liệu cần được giải thích theo contract trong `docs/business_rules.md` và `docs/contracts.md`.

## 6. Tự đánh giá

Ba shape đáp ứng ma trận public và crash suite. Benchmark public ủng hộ `workflow` vì đạt cùng tỷ lệ pass với chi phí mô phỏng thấp nhất. Kết quả hidden chính thức chưa có nên chưa thể kết luận ngưỡng pass 0.75.
