# Báo cáo cá nhân — 2A202603863_NguyenNghiemKhanhTiep

## 1. Thông tin thành viên

- Họ tên: Nguyễn Nghiêm Khánh Tiệp
- MSSV: 2A202603863
- Email: tiepnnk04@gmail.com
- GitHub: tiepnnk01-10

## 2. Phần việc phụ trách

Người 3 — Shape C `orchestrator`: `src/lab8/shapes/orchestrator.py`, test riêng `src/tests/test_orchestrator_own.py`, và mục 3.3 trong `report/team/group_report.md`.

## 3. Đóng góp cụ thể

- Commit chính: (điền hash sau khi commit)
- Viết shape orchestrator: dựng handoff có allowlist và chỉ tool đọc, chạy investigator chỉ đọc, orchestrator tự gọi `durability.issue_refund` với quote đầy đủ và `crash_at`.
- Quyết định kỹ thuật:
  - Tiền lấy từ `compute_compensation` trên dòng order, không dùng ngày trễ trong ticket (tránh điểm yếu của swarm tham chiếu ở seed 55).
  - `lookup_order` đứng trước `compute_compensation` trong `allowed_tools`, vì quote cần dữ liệu đơn.
  - Không tự trừ phần đã hoàn trước đó; host tự trừ (T13, T14).
  - `InjectedCrash` chỉ ghi trace rồi `raise` lại.
- Test đã thêm: `src/tests/test_orchestrator_own.py` (16 test): không có secret hay thông tin cá nhân trong trace và kết quả của 14 claim public; handoff không có `parent_secret`, `raw_headers` hay tool ghi; crash vẫn ném `InjectedCrash`.

## 4. Bằng chứng

- `python -m pytest -q -m student -o addopts= -k orchestrator`: 62 passed.
- `python -m pytest -q`: xanh (70 passed).
- `python -m lab8.crash_test --count 20 --out reports/crash.json`: `crash_safety 20/20`.
- Link commit: (điền sau khi push)

## 5. Công cụ AI đã dùng

- Claude Code: đọc tài liệu và code mẫu, gợi ý để hoàn thành file `orchestrator.py`.
- Cách tự kiểm tra: chạy lại các lệnh ở mục 4 và đọc lại code đối chiếu với `docs/business_rules.md` và `docs/contracts.md`. 

## 6. Tự đánh giá


**Phần làm tốt**

- Shape orchestrator đạt 62/62 student test; cổng host `pytest -q` vẫn xanh.
- Số tiền lấy từ dòng order trong database qua `compute_compensation`, không lấy từ ticket, nên không mắc điểm yếu "tin ngày trễ trong ticket" của swarm tham chiếu.
- Handoff đi qua allowlist trong code; trace chỉ ghi dữ liệu đã lọc, và mọi nhánh return đều qua `finish()` nên luôn có trace hợp lệ.
- `crash_at` được truyền xuống host và `InjectedCrash` không bị nuốt.

**Phần còn hạn chế**

- Chưa có số benchmark của orchestrator nên chưa biết cost/success so với workflow, single và swarm.
- Kết quả crash suite 20/20 là của lệnh mặc định; chưa xác nhận riêng cho orchestrator (việc của CP4).
- Orchestrator thêm bước handoff và investigator, có thể tốn chi phí hơn workflow trong khi quy trình claim khá cố định. Đây mới là giả thuyết, cần số đo ở CP5.
- Chưa kiểm ở cấp shape các ca approval hỏng hoặc đơn đã hoàn đủ ngoài bộ public.

**Điều học được**

- Tiền, approval và chống ghi trùng phải do code quyết; model chỉ đọc và soạn chữ. Chữ trong ticket là dữ liệu, không phải lệnh.
- Phải truyền quote đầy đủ vào `issue_refund` vì host tự trừ phần đã hoàn trên cùng đơn; tự trừ trước sẽ bị trừ hai lần.
- Chống ghi trùng dựa vào ledger và idempotency key `refund:{claim_id}`, không dựa vào checkpoint: demo `buggy_workflow` cho `unsafe refund rows: 2` trong khi ledger của host giữ ở 1.
- Handoff phải lọc bằng allowlist trong code; tóm tắt bằng LLM không phải redaction. Trace là ranh giới bảo mật, không phải công cụ debug.
