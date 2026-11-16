# Kế hoạch phân công & Quy trình phối hợp không xung đột — Lab 8 (LogiX-VN)

Tài liệu này quy định phạm vi file, nhánh Git, checklist kỹ thuật và thứ tự tích hợp cho 2 thành viên để làm việc song song **không xung đột (zero-conflict)** và đáp ứng đầy đủ tiêu chí chấm điểm trong [RUBRIC.md](../../RUBRIC.md) & [SUBMISSION.md](../../SUBMISSION.md).

## 1. Thành viên nhóm

| STT | Họ tên | MSSV | Vai trò chính | Nhánh Git |
| --: | --- | --- | --- | --- |
| 1 | Nguyễn Viết Mạnh Khải | `2A202603664` | Shape A (`workflow`) + Shape B (`single`) + Benchmark & `decision_adr.md` | `feat/khai-workflow-single` |
| 2 | Vũ Đức Anh | `2A202603573` | Shape C (`orchestrator`) + Security/Handoff + Crash suite & `research_card.md` | `feat/ducanh-orchestrator` |

---

## 2. Ma trận sở hữu file (Tránh merge conflict)

Nguyên tắc: **trong giai đoạn code & viết test (CP2–CP3), mỗi người chỉ sửa các file thuộc quyền sở hữu của mình.** Không ai sửa chéo file của người kia.

| File / Thư mục | Người sở hữu | Ghi chú |
| --- | --- | --- |
| `src/lab8/shapes/workflow.py` | **Khải** (`2A202603664`) | Cài Shape A (`workflow`) |
| `src/lab8/shapes/single.py` | **Khải** (`2A202603664`) | Cài Shape B (`single`) |
| `src/tests/test_student_workflow_single.py` | **Khải** (`2A202603664`) | Tạo mới — test riêng của Khải (bắt buộc cho tiêu chí C8) |
| `report/team/2A202603664_NguyenVietManhKhai.md` | **Khải** (`2A202603664`) | Copy từ `report/team/MSSV_HoTen.md` |
| `report/team/decision_adr.md` | **Khải** (`2A202603664`) | Điền số liệu từ `benchmark.json`, `crash.json`, commit hash |
| `src/reports/benchmark.json` | **Khải** (`2A202603664`) | Sinh bằng `python -m lab8.benchmark ...` (không sửa tay) |
| `src/lab8/shapes/orchestrator.py` | **Đức Anh** (`2A202603573`) | Cài Shape C (`orchestrator`) |
| `src/tests/test_student_orchestrator_security.py` | **Đức Anh** (`2A202603573`) | Tạo mới — test riêng của Đức Anh (bắt buộc cho tiêu chí C8) |
| `report/team/2A202603573_VuDucAnh.md` | **Đức Anh** (`2A202603573`) | Copy từ `report/team/MSSV_HoTen.md` |
| `report/team/research_card.md` | **Đức Anh** (`2A202603573`) | Chọn R1–R4, chạy ablation và điền đủ 7 dòng cột `Nhóm điền` |
| `src/reports/crash.json` | **Đức Anh** (`2A202603573`) | Sinh bằng `python -m lab8.crash_test ...` (không sửa tay) |
| `TEAM.md` | **Cập nhật tuần tự** | Mỗi người tự thêm Email/GitHub và 1 dòng vào `## Bảng đóng góp` ở CP5 |
| `report/team/group_report.md` | **Cập nhật tuần tự** | Khải viết mục 1, 2, 4; Đức Anh viết mục 3, 5, 7 (merge lần lượt ở CP5) |

### File tuyệt đối KHÔNG sửa & KHÔNG commit

- **Không sửa thước đo & dữ liệu gốc:** `src/lab8/metrics.py`, `src/lab8/durability.py`, `src/lab8/policy.py`, `src/lab8/shapes/swarm_reference.py`, `src/config/*.yaml`, `src/data/*`.
- **Giữ nguyên file mẫu:** `report/team/MSSV_HoTen.md` (chỉ copy sang file mới, không xóa/sửa bản gốc).
- **Không commit output tạm/nhạy cảm:** `src/traces/`, `*.sqlite`, `student_drop/`, `src/eval/instructor/`, `.venv/`, `.env` (đã có trong `.gitignore`).

---

## 3. Checklist kỹ thuật chi tiết từng người

### Phần A — Nguyễn Viết Mạnh Khải (`2A202603664`)

1. **Đọc bắt buộc trước khi code:**
   - [docs/business_rules.md](../../docs/business_rules.md), [docs/contracts.md](../../docs/contracts.md)
   - [src/lab8/shapes/swarm_reference.py](../../src/lab8/shapes/swarm_reference.py) (xem cách mở DB, `finish()`, `Trace`, xử lý `InjectedCrash` — **lưu ý không copy khối `REFERENCE_WEAKNESS`**)
   - Docstring đầu file [workflow.py](../../src/lab8/shapes/workflow.py) và [single.py](../../src/lab8/shapes/single.py), cùng [runtime.py](../../src/lab8/runtime.py) (`run_react`, `dispatch`).

2. **Cài đặt `src/lab8/shapes/workflow.py` (`TODO CP2`, `TODO CP3`):**
   - Giữ nguyên chữ ký `run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult`.
   - Đọc claim bằng `get_claim_view` (không `SELECT *` làm lộ `parent_secret` vào trace).
   - Không có claim → `status="failed"`, `proposal_amount=0`, `error_reason="unknown_claim"`.
   - Thiếu `order_id` → `status="needs_info"`, `proposal_amount=0` (không lấy `order_id` từ ticket text).
   - Gọi `lookup_order`: nếu `not visible` → `status="escalated"`, `proposal_amount=0` (không ghi SĐT, địa chỉ, tên hàng, internal note vào trace).
   - Tính quote từ order row bằng `compute_compensation(conn, order)` (bỏ qua số ngày/clause giả trong ticket).
   - Nếu `quote <= 0` → `status="denied"`, `proposal_amount=0`, **không** gọi `issue_refund`.
   - Nếu `quote > 0` → gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` với **quote đầy đủ** (không tự trừ phần đã hoàn trước đó ở T13/T14). **Không bắt `InjectedCrash`** (chỉ flush trace nếu muốn rồi re-raise giống `swarm_reference.py`).
   - Kết quả từ `issue_refund`:
     - `ok=True` → `status="resolved"`, `proposal_amount=proposal`.
     - `ok=False` và `conflict=True` → `status="failed"`, `proposal_amount=proposal`.
     - `ok=False` và `conflict=False` → `status="denied"`, `proposal_amount=proposal` (host đã tự ghi `policy_denied`).
   - Trả kết quả qua `lab8.shapes.common.finish(...)` trên mọi nhánh, có `Trace` hợp lệ theo `Trace contract v1`.

3. **Cài đặt `src/lab8/shapes/single.py` (`TODO CP2`, `TODO CP3`):**
   - Dùng `lab8.runtime.run_react(conn, budget, observation=..., decide=..., max_steps=8, worker=False)`.
   - Trong `decide`: chỉ chọn tool đọc (`get_claim_view`, `lookup_order`, `lookup_policy`, `lookup_refund_history`, `compute_compensation`), có đếm gọi `MockLLM` vào `budget` (`complete(...)`) để `cost_estimate` công bằng. Tuyệt đối **không** tin delay/lệnh trong ticket, **không** gọi `issue_refund` trong vòng lặp ReAct.
   - Sau vòng lặp `run_react`, code của shape kiểm `needs_info` / `escalated` / `denied` / `quote > 0` và gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` (không bắt `InjectedCrash`), trả về bằng `finish(...)`.

4. **Viết test riêng (`src/tests/test_student_workflow_single.py`):**
   - Ít nhất 2–3 test case kiểm tra:
     - Ticket nói dối `delay_days` / prompt injection ("ignore policy", "trễ 9 ngày") nhưng `workflow` và `single` vẫn quote đúng theo DB & policy hiện hành (`is_current=True`).
     - T13/T14 (`order_already_refunded` và hoàn bù phần chênh): `proposal_amount` giữ nguyên full quote và không tự trừ trước khi gọi `issue_refund`.
     - `single` tuân thủ giới hạn `max_steps=8` và không gọi write tool trong vòng lặp.

5. **Lệnh tự kiểm tra của Khải (chạy trong `src/`):**
   ```powershell
   python -m pytest -q
   python -m pytest -q -m student -o addopts= -k "workflow or single"
   python -m pytest -q tests/test_student_workflow_single.py
   ```
   Kỳ vọng: cổng host (`pytest -q`) xanh, và `124 passed` cho `workflow` + `single`.

---

### Phần B — Vũ Đức Anh (`2A202603573`)

1. **Đọc bắt buộc trước khi code:**
   - [docs/business_rules.md](../../docs/business_rules.md), [docs/contracts.md](../../docs/contracts.md), [docs/architecture.md](../../docs/architecture.md)
   - [src/lab8/handoff.py](../../src/lab8/handoff.py) (`make_handoff`, `sanitize`, `READONLY_TOOLS`, `ALLOWED_FIELDS`)
   - [src/lab8/runtime.py](../../src/lab8/runtime.py) (`run_readonly_investigators`)
   - [src/lab8/shapes/swarm_reference.py](../../src/lab8/shapes/swarm_reference.py) và docstring đầu file [orchestrator.py](../../src/lab8/shapes/orchestrator.py).

2. **Cài đặt `src/lab8/shapes/orchestrator.py` (`TODO CP2`, `TODO CP3`):**
   - Giữ nguyên chữ ký `run_claim(claim_id: str, *, seed: int, store_path: str, crash_at: str | None = None) -> RunResult`.
   - Đọc claim bằng `get_claim_view` (không `SELECT *`). Xử lý các nhánh `unknown_claim` (`failed`), thiếu `order_id` (`needs_info`) trước khi dựng handoff hoặc trước khi chi trả.
   - Tạo handoff bằng `lab8.handoff.make_handoff(...)` với `allowed_tools` chỉ gồm tool đọc (ví dụ `["lookup_order", "lookup_policy", "lookup_refund_history", "compute_compensation"]`). **Tuyệt đối không** đưa `parent_secret`, `raw_headers`, toàn bộ claim row hay PII (SĐT, địa chỉ, tên hàng, ghi chú nội bộ) vào `facts`.
   - Gọi `lab8.runtime.run_readonly_investigators(conn, budget, handoff, principal_id=claim_row["principal_id"])`.
   - Kiểm `lookup_order`: nếu `not visible` → `status="escalated"`, `proposal_amount=0`.
   - Lấy quote từ `compute_compensation` trên order view có cấu trúc (không tin text trong ticket).
   - Nếu `quote <= 0` → `status="denied"`, `proposal_amount=0`, không gọi `issue_refund`.
   - Nếu `quote > 0` → gọi `durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)` với **quote đầy đủ**, không bắt `InjectedCrash`.
   - Trace chỉ ghi `handoff` đã qua `make_handoff`/`sanitize` (không ghi parent context thô, không dùng LLM summary làm redaction), trả kết quả qua `finish(...)` trên mọi nhánh.

3. **Viết test riêng (`src/tests/test_student_orchestrator_security.py`):**
   - Ít nhất 2–3 test case kiểm tra:
     - Trace và `RunResult` của `orchestrator` không chứa `CANARY_SECRET_*`, `parent_secret`, SĐT, địa chỉ, tên hàng hoặc ghi chú nội bộ (kể cả khi ticket/claim có dữ liệu nhạy cảm).
     - `make_handoff` từ chối write tool (`issue_refund`, `append_audit`) và lọc bỏ key ngoài `ALLOWED_FIELDS`.
     - `approval_claim_mismatch` (approval cấp cho claim khác) bị host chặn, không ghi ledger, có audit `policy_denied`, `status="denied"`, `proposal_amount` giữ nguyên full quote.

4. **Lệnh tự kiểm tra của Đức Anh (chạy trong `src/`):**
   ```powershell
   python -m pytest -q
   python -m pytest -q -m student -o addopts= -k orchestrator
   python -m pytest -q tests/test_student_orchestrator_security.py
   ```
   Kỳ vọng: cổng host (`pytest -q`) xanh, và `62 passed` cho `orchestrator`.

---

## 4. Quy trình Git từng bước (Làm đúng thứ tự để 0 conflict)

### Bước 0 — Khởi tạo & Đồng bộ (Khải làm trước, Đức Anh pull sau)
1. **Khải:**
   - Đổi tên repo GitHub nếu vẫn còn chữ `TenNhom` (theo mẫu `K5-L3A-DAY08-<TenNhom>-FromWorkflowsToAgents` trong [SUBMISSION.md](../../SUBMISSION.md)), đặt repo public hoặc mời giảng viên.
   - Commit và push `TEAM.md` + `report/team/WORKPLAN.md` lên `main`.
2. **Đức Anh:**
   - `git pull origin main` (hoặc clone repo mới).
   - Cài môi trường theo [src/README.md](../../src/README.md), chạy kiểm tra đầu buổi trong `src/`:
     ```powershell
     python -m lab8.smoke
     python -m pytest -q
     ```

### Bước 1 — Làm việc song song trên nhánh riêng (CP2–CP3)
- **Khải:**
  ```bash
  git checkout -b feat/khai-workflow-single
  # Code workflow.py, single.py + tests/test_student_workflow_single.py
  # Chạy pytest xác nhận xanh
  git add src/lab8/shapes/workflow.py src/lab8/shapes/single.py src/tests/test_student_workflow_single.py
  git commit -m "feat(shapes): implement workflow and single ReAct shapes with tests"
  git push -u origin feat/khai-workflow-single
  ```
- **Đức Anh:**
  ```bash
  git checkout -b feat/ducanh-orchestrator
  # Code orchestrator.py + tests/test_student_orchestrator_security.py
  # Chạy pytest xác nhận xanh
  git add src/lab8/shapes/orchestrator.py src/tests/test_student_orchestrator_security.py
  git commit -m "feat(shapes): implement orchestrator shape with handoff sanitization and security tests"
  git push -u origin feat/ducanh-orchestrator
  ```

### Bước 2 — Merge về `main` (Không conflict vì file tách biệt hoàn toàn)
1. Merge `feat/khai-workflow-single` vào `main` trước, rồi merge `feat/ducanh-orchestrator` vào `main`.
2. Cả 2 bạn chuyển về `main` và `git pull origin main`, chạy kiểm tra toàn bộ trong `src/`:
   ```powershell
   python -m pytest -q
   python -m pytest -q -m student -o addopts=
   ```
   *(Lưu ý: ở `swarm` seed 55 T02, test kiểm tra điểm yếu cố ý của swarm tham chiếu; tất cả test của `workflow`, `single`, `orchestrator` phải xanh 100%).*

### Bước 3 — Crash suite, Benchmark, Ablation & Báo cáo (CP4–CP5, làm tuần tự trên `main`)
1. **Đức Anh làm trước trên `main`:**
   - Chạy crash suite 20 điểm:
     ```powershell
     python -m lab8.crash_test --count 20 --out reports/crash.json
     ```
     Đảm bảo `"crash_safety": "20/20"`.
   - Thực hiện ablation theo 1 câu R1–R4, điền `report/team/research_card.md`.
   - Copy `report/team/MSSV_HoTen.md` → `report/team/2A202603573_VuDucAnh.md` và điền đầy đủ (gồm cả mục công cụ AI đã dùng).
   - Điền mục 3, 5, 7 trong `report/team/group_report.md`, điền dòng của mình vào `TEAM.md` (Email, GitHub, bảng đóng góp).
   - Commit và `git push origin main`.
2. **Khải kéo về và hoàn thiện bước chốt trên `main`:**
   - `git pull origin main`
   - Chạy benchmark 4 shape × 5 seed:
     ```powershell
     python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
     ```
   - Nếu được phát `student_drop/`, chạy thêm tự kiểm hidden:
     ```powershell
     python -m lab8.benchmark --shapes workflow,single,orchestrator --cases student_drop/hidden_claims.jsonl --world student_drop/hidden_world_state.json --out reports/hidden_selfcheck.json
     ```
   - Điền số liệu từ `src/reports/benchmark.json` và `src/reports/crash.json` vào `report/team/decision_adr.md` (giữ nguyên các dòng nhãn `- ...:`).
   - Điền mục 1, 2, 4 trong `report/team/group_report.md`.
   - Copy `report/team/MSSV_HoTen.md` → `report/team/2A202603664_NguyenVietManhKhai.md` và điền đầy đủ.
   - Điền dòng của Khải vào `TEAM.md`.
   - Commit code + report (`git commit -m "docs: add benchmark, crash evidence, ADR, and team reports"`), chạy `git rev-parse --short HEAD` để lấy commit hash điền vào `report/team/decision_adr.md` và `report/team/group_report.md`, rồi commit chốt cuối (`git commit -m "docs: record final commit hash in ADR"`).
3. **Kiểm tra cổng nộp bài (bắt buộc ra `0 FAIL`):**
   ```powershell
   python -m pytest -q
   python -m lab8.check_submission
   ```
   Sau khi ra `0 FAIL`, `git push origin main`.
4. **Nộp bài trên LMS:**
   - **Cả 2 thành viên** đều phải tự nộp **cùng link repo GitHub nhóm** lên LMS bằng tài khoản cá nhân trước deadline.
