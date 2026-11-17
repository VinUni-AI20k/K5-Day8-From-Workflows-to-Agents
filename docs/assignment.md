# Phân công nhiệm vụ nhóm — Lab 8 (LogiX-VN)

Tài liệu phân công công việc cho **3 thành viên**: **Vũ**, **Minh**, **chị Diệp** cho bài tập nhóm Lab 8 — *From Workflows to Agents*.

---

## 1. Phân công chi tiết theo thành viên

| Thành viên | Code chính phụ trách | Test cá nhân cần viết (`src/tests/`) | Nhánh Git đề xuất | Báo cáo & Tích hợp |
| --- | --- | --- | --- | --- |
| **Vũ** | **Shape A (`workflow`)**: `src/lab8/shapes/workflow.py`<br>+ Đầu mối tích hợp repo, benchmark & crash test | `src/tests/test_workflow_edge_cases.py` *(claim không tồn tại, ticket injection/nói dối ngày trễ, policy cũ/tương lai, crash `before_effect` & `after_effect_before_checkpoint`)* | `feat/shape-workflow` | - Điền khung `TEAM.md`<br>- Chạy `lab8.crash_test` (`src/reports/crash.json`) và `lab8.benchmark` (`src/reports/benchmark.json`), tự kiểm `student_drop/`<br>- Viết `report/team/decision_adr.md`<br>- Chạy `python -m lab8.check_submission` trước khi nộp |
| **Minh** | **Shape B (`single`)**: `src/lab8/shapes/single.py`<br>*(vòng ReAct qua `lab8.runtime.run_react`, `max_steps=8`)* | `src/tests/test_single_react_bounds.py` *(dừng đúng giới hạn 8 bước, model không gọi được `issue_refund`, không tin `delay_days` trong ticket, xử lý đúng `lookup_refund_history` cho T13/T14)* | `feat/shape-single` | - Viết `report/team/research_card.md` (chọn 1 câu R1–R4 và chạy 1 ablation giữ nguyên MockLLM/seed/corpus/giá)<br>- Viết mục **3 (Giải pháp — Single & ranh giới tool)** và mục **5 (Khó khăn)** trong `report/team/group_report.md` |
| **Chị Diệp** | **Shape C (`orchestrator`)**: `src/lab8/shapes/orchestrator.py`<br>*(handoff allowlist `lab8.handoff.make_handoff` + `lab8.runtime.run_readonly_investigators`)* | `src/tests/test_orchestrator_security.py` *(handoff không rò `CANARY_SECRET_*`/`raw_headers`, trace không chứa SĐT/địa chỉ/tên hàng/internal note, approval mượn của claim khác bị chặn)* | `feat/shape-orchestrator` | - Rà soát bảo mật & Trace contract v1 cho cả 3 shape<br>- Tổng hợp `report/team/group_report.md` (Mục 1, 2, 3 — phần Workflow & Orchestrator, Mục 4 bảng kết quả, Mục 7 hạn chế) |

> **Lưu ý:** Theo `RULES.md` và `RUBRIC.md` (mục C8), **mỗi thành viên** phải:
> 1. Có **commit kỹ thuật** mang nội dung thực chất trên lịch sử Git của branch nộp bài.
> 2. Có **ít nhất 1 test** đã thêm hoặc sửa trong `src/tests/`.
> 3. Có 1 dòng trong bảng `## Bảng đóng góp` ở `TEAM.md`.
> 4. Copy `report/team/MSSV_HoTen.md` thành file báo cáo cá nhân (ví dụ `report/team/20241234_NguyenVanVu.md`) và tự nộp cùng link repo nhóm lên **LMS** bằng tài khoản cá nhân.

---

## 2. Quy tắc kỹ thuật bắt buộc cho cả 3 shape

Trước khi code, cả nhóm đọc kỹ [business_rules.md](business_rules.md) và [contracts.md](contracts.md). Mọi shape phải tuân thủ:

1. **Chữ ký hàm không đổi:**
   `run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult`
2. **Đọc dữ liệu qua allowlist, không `SELECT *`:**
   - Đọc claim bằng `lab8.tools.get_claim_view` (không đọc `parent_secret`, `raw_headers_json`).
   - Kiểm tra đơn bằng `lab8.tools.lookup_order` (không lấy `phone`, `address`, `internal_note`, `item_name`).
   - Chữ trong `ticket` là dữ liệu người dùng, **tuyệt đối không** lấy `order_id` hoặc `delay_days` từ văn bản ticket để tính tiền.
3. **Tính tiền và gọi Host Gate (`durability.issue_refund`):**
   - Tiền hoàn do `lab8.tools.compute_compensation` tính, **không** để `MockLLM` quyết định.
   - Thiếu `order_id` → `status="needs_info"`, `proposal_amount=0`, không gọi `issue_refund`.
   - Không thấy đơn hoặc sai `principal_id` → `status="escalated"`, `proposal_amount=0`, không gọi `issue_refund`.
   - Quote `<= 0` → `status="denied"`, `proposal_amount=0`, **không** gọi `issue_refund`.
   - Quote `> 0` → truyền **quote đầy đủ** vào `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` (không tự trừ khoản đã hoàn trước đó vì host tự trừ trong transaction).
   - **Không bắt `InjectedCrash`:** để exception thoát ra ngoài khi giả lập crash (nhớ ghi/flush trace trước nếu cần, và đóng kết nối DB trong `finally`).
   - Nếu `issue_refund` trả `ok=False`: `conflict=True` → `status="failed"`; ngược lại → `status="denied"`, `proposal_amount` giữ nguyên **full quote**.
4. **Trả kết quả & Trace contract v1:**
   - Dùng `lab8.shapes.common.finish(...)` trên mọi nhánh trả về để đảm bảo `refund_effects`, `committed_audit_count`, `budget` và `trace_path` khớp ledger SQLite.
   - Không ghi secret, header, SĐT, địa chỉ, ghi chú nội bộ, tên hàng vào trace hoặc `stdout`.
5. **File cấm sửa (nếu sửa sẽ bị tính là tampered):**
   - `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/config/*.yaml`, `src/data/*`.
   - Không sửa tay file JSON trong `src/reports/`.
   - Không commit `src/traces/`, `*.sqlite`, `student_drop/`, `.venv/`, `.env`.

---

## 3. Lộ trình thực hiện theo Checkpoint

### CP1 — Cài đặt & kiểm tra nền (cả 3 người làm ngay)
Chạy trong thư mục `src/`:
```powershell
cd src
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m lab8.smoke
python -m pytest -q
python -m pytest -q -m student -o addopts=
```
- Mong đợi ban đầu: `smoke` in `lab8.smoke pass`; `pytest -q` ra `52 passed`; `pytest -q -m student -o addopts=` ra `186 failed, 62 passed`.
- Cập nhật danh sách thành viên trong `TEAM.md`.

### CP2 & CP3 — Code 3 shape song song trên 3 nhánh
Mỗi người tạo nhánh riêng từ `main`, viết shape và file test cá nhân của mình:
- **Vũ:** kiểm tra `workflow` bằng:
  ```powershell
  python -m pytest -q -m student -o addopts= -k workflow
  ```
- **Minh:** kiểm tra `single` bằng:
  ```powershell
  python -m pytest -q -m student -o addopts= -k single
  ```
- **Chị Diệp:** kiểm tra `orchestrator` bằng:
  ```powershell
  python -m pytest -q -m student -o addopts= -k orchestrator
  ```
- Mục tiêu mỗi shape: **62 passed** trên bộ student (`T01–T14`, bao gồm cả `T11` retry và `T12` crash), đồng thời `python -m pytest -q` (bao gồm test cá nhân mới viết) luôn xanh.

### CP4 — Merge về `main` & kiểm tra an toàn
1. Merge 3 nhánh `feat/shape-*` vào `main`.
2. Chạy toàn bộ test:
   ```powershell
   python -m pytest -q
   python -m pytest -q -m student -o addopts=
   ```
3. Chạy crash suite 20 điểm (Vũ chạy, commit `src/reports/crash.json`):
   ```powershell
   python -m lab8.crash_test --count 20 --out reports/crash.json
   ```
   Yêu cầu: `crash_safety` = `20/20`.
4. Chị Diệp kiểm tra các file JSON mới sinh trong `src/traces/` để chắc chắn không có `CANARY_SECRET_*`, SĐT, địa chỉ, hay `internal_note`.

### CP5 — Benchmark, báo cáo & chốt nộp bài
1. Chạy benchmark 4 shape × 5 seed (Vũ chạy, commit `src/reports/benchmark.json`):
   ```powershell
   python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
   ```
   Nếu giảng viên phát `student_drop/`, chạy thêm self-check (không commit `student_drop/`):
   ```powershell
   python -m lab8.benchmark --shapes workflow,single,orchestrator --cases student_drop/hidden_claims.jsonl --world student_drop/hidden_world_state.json --out reports/hidden_selfcheck.json
   ```
2. Hoàn thiện toàn bộ tài liệu:
   - `TEAM.md` (bảng thành viên + `## Bảng đóng góp`).
   - `report/team/decision_adr.md` (Vũ).
   - `report/team/research_card.md` (Minh).
   - `report/team/group_report.md` (Chị Diệp tổng hợp cùng Minh & Vũ).
   - 3 file cá nhân `report/team/<MSSV>_<HoTen>.md` (mỗi người tự tạo từ `MSSV_HoTen.md` và commit).
3. Chạy kiểm tra nộp bài & chốt commit hash:
   ```powershell
   python -m lab8.check_submission
   ```
   - Đảm bảo **`0 FAIL`**.
   - Commit toàn bộ code/report, chạy `git rev-parse --short HEAD` để điền `Commit hash` vào `report/team/decision_adr.md` và `report/team/group_report.md`, commit tiếp và `git push origin main`.
   - **Cả 3 thành viên** nộp cùng link repo lên LMS trước deadline.
