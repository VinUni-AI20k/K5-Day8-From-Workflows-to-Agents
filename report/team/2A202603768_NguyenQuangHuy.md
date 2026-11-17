# Báo cáo cá nhân — 2A202603768_NguyenQuangHuy

## 1. Thông tin thành viên

- Họ tên: Nguyễn Quang Huy
- MSSV: 2A202603768
- Email: 26ai.huynq13@vinuni.edu.vn
- GitHub: https://github.com/nguyenquanghuy091204

## 2. Phần việc phụ trách

- **Shape phụ trách (CP2, CP3)**: Hiện thực kiến trúc **Shape B (`single` — Single ReAct Agent)** trong file `src/lab8/shapes/single.py`.
- **Kiểm thử kỹ thuật**: Viết mới test suite `src/tests/test_single.py` kiểm tra toàn diện vòng lặp ReAct, trần hoàn tiền theo đơn (per-order cap), ranh giới bảo mật và khả năng phục hồi sau crash.
- **Báo cáo**: Tham gia viết phần Shape B cho báo cáo nhóm và cập nhật bảng đóng góp trong `TEAM.md`.

## 3. Đóng góp cụ thể

### 3.1. Quyết định kỹ thuật chính
1. **Ranh giới Code vs Model (Least Autonomy)**:
   - Sử dụng `lab8.runtime.run_react` với chặn trần tối đa 8 bước (`max_steps=8`) và gắn cờ `worker=True`.
   - Agent (`decide`) chỉ gọi các tool đọc (`lookup_order`, `compute_compensation`). Tuyệt đối không cấp tool ghi (`issue_refund`).
   - Host là bên duy nhất thực hiện ghi `issue_refund` sau khi vòng lặp ReAct kết thúc.
2. **Chống ảo giác & Prompt Injection**:
   - Tiền hoàn do tool `compute_compensation` tính toán dựa trên dữ liệu thật của đơn hàng, không dựa vào câu chữ của khách trong ticket (vượt qua T02 khai khống ngày trễ và T09 prompt injection).
3. **Tuân thủ trần theo đơn (Per-order cap)**:
   - Truyền **quote đầy đủ** vào `durability.issue_refund`, không tự trừ tiền đã hoàn trước đó để host tự đối soát và trừ trong transaction (đạt chuẩn T13, T14).
4. **Xử lý Crash & Idempotency (CP3)**:
   - Truyền tham số `crash_at` vào `durability.issue_refund`. Bắt ngoại lệ `InjectedCrash` để ghi log trace và gọi `trace.write()`, sau đó **re-raise ngoại lệ ra ngoài** theo đúng contract của bài lab.
   - Dựa vào khóa `refund:{claim_id}` để đảm bảo tính idempotent: chạy lại (T11) hoặc resume sau crash (T12) chỉ tạo đúng 1 dòng ledger và 1 audit event `refund_committed`.
5. **Trace Contract v1 & An toàn Secret**:
   - Sử dụng `_Trace` ghi nhận log tại mọi nhánh thoát (`finish()`). Loại bỏ toàn bộ `parent_secret`, headers và thông tin PII (SĐT, địa chỉ, tên hàng) khỏi trace.

### 3.2. Commit và Test đã thêm
- **Commit**: `b7df328` (hoặc hash commit bạn push code Shape B) — *Implement Shape B Single ReAct Agent (CP2, CP3) with unit tests*.
- **Test đã thêm**: File `src/tests/test_single.py` (8 test cases kiểm thử các ca: T01, T02, T04, T05, T09, T11 retry, T12 crash recovery, T13-T14 per-order cap).

## 4. Bằng chứng

- **Test ma trận student của bài lab**:
  - Lệnh: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"`
  - Kết quả: **`62 passed, 240 deselected`** (100% pass trên 5 seed public).
- **Test suite cá nhân mới tạo**:
  - Lệnh: `python -m pytest -v tests/test_single_agent.py`
  - Kết quả: **`8 passed`**.
- **Công cụ kiểm tra nộp bài**:
  - Lệnh: `python -m lab8.check_submission`
  - Kết quả máy đọc: `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.

## 5. Công cụ AI đã dùng

- **Công cụ**: Antigravity.
- **Mục đích**:
  - Hỗ trợ xây dựng luồng tương tác giữa hàm `decide` và `run_react` để dừng chính xác ở bước 3, không bị chạm trần 8 bước.
  - Tư vấn cơ chế bắt và re-raise ngoại lệ `InjectedCrash` đúng chuẩn của test suite CP3.
- **Cách tự kiểm tra**:
  - Kiểm tra trực tiếp các file trong `traces/` để đảm bảo không rò rỉ token `CANARY_SECRET_*`.

## 6. Tự đánh giá

- **Kết quả**: Hoàn thành yêu cầu kỹ thuật của CP2 và CP3 cho Shape B.
- **Chất lượng**: Code chạy ổn định, không lỗi ngoại lệ, đảm bảo nguyên tắc an toàn dữ liệu, tính idempotent và sẵn sàng giải trình toàn bộ cơ chế hoạt động khi vấn đáp.