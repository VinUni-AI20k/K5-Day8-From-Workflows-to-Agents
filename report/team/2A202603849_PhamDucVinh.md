# Báo cáo cá nhân — 2A202603849_PhamDucVinh

## 1. Thông tin thành viên

- Họ tên: Phạm Đức Vinh
- MSSV: 2A202603849
- Email: 26ai.vinhpd@vinuni.edu.vn
- GitHub: vindpd203

## 2. Phần việc phụ trách

- **Shape B `single`** (`src/lab8/shapes/single.py`): một agent ReAct, tối đa 8 bước, chỉ có tool đọc.
- **Research card R2** (`report/team/research_card.md`): phân loại trial fail của swarm theo MAST, kèm một ablation chạy được.
- **CP4 — rà nhánh approval** trên `workflow` và `single`.
- **Báo cáo nhóm** (`report/team/group_report.md`).

## 3. Đóng góp cụ thể

- **`single.py`.** Vòng `run_react` dùng hàm `decide` chỉ được chọn hai tool đọc: `get_claim_view` rồi `lookup_order`. Mỗi bước tính một model call vào `Budget`. Vì `run_react` chỉ giữ kết quả của tool gần nhất, agent tự giữ dữ kiện đã đọc trong biến `facts`. Sau vòng lặp, **code** tính quote bằng `compute_compensation` từ order row, không dùng số ngày trễ ghi trong ticket, rồi gọi `durability.issue_refund` với quote đầy đủ. `crash_at` được chuyển vào host. Khi có `InjectedCrash`, shape ghi trace rồi ném lỗi tiếp ra ngoài.
- **Quyết định kỹ thuật:**
  - Không cho model chọn số tiền.
  - Không gọi `lookup_refund_history`, vì host đã tự trừ phần hoàn trước đó. Gọi thêm chỉ tăng cost mà không đổi kết quả.
  - Trace chỉ ghi tên tool, order view đã giới hạn field, quote và quyết định. Không ghi ticket hay claim row.
- **Sửa lỗ hổng lộ dữ liệu khi host từ chối.** Host tạo reason dạng `approval_<status>`, trong đó `status` lấy từ database. Bản đầu của `single` chép reason này nguyên văn ra `error_reason` và trace. Mình chuyển sang dùng allowlist `SAFE_DENIAL_REASONS` có sẵn trong `workflow.py`. Reason không có trong danh sách sẽ thành `policy_denied`.
- **Ablation R2.** Viết `src/research/r2_swarm_no_ticket_delay.py`: bọc nguyên swarm tham chiếu, chỉ tắt kênh đọc số ngày trễ từ ticket. Chạy cùng swarm gốc trong một lệnh `lab8.benchmark --extra-shape`.
- **Test** trong `src/tests/test_team_single.py`, 9 test:
  - C-002 (ticket khai trễ 5 ngày, order row ghi 2) phải bị từ chối ở cả 5 seed. Trace không chứa nội dung ticket hay `CANARY_SECRET`.
  - Ở seed 55, swarm trả tiền còn `single` không trả.
  - Approval có `status` bị cài `CANARY_SECRET_STATUS` thì kết quả là `denied` / `policy_denied`, không lộ chuỗi.
  - Số model call nằm trong giới hạn 8 bước.

## 4. Bằng chứng

- Commit `8ba0422`: `feat(single): ReAct shape with read-only tools and team test`.
- Commit `9aa1dd9`: `research(R2): swarm ticket-delay ablation and research card`.
- Commit `85c0a35`: `fix(single): filter host denial reasons; add personal and draft group report`. Đây là commit vá lỗ hổng reason, kèm test mới.
- Commit `2c2c7c2`: `docs(report): fill results section; regenerate benchmark and security audit with workflow implemented`. Commit này điền mục 4 của báo cáo nhóm và sinh lại `benchmark.json`, `orchestrator_security.json` bằng công cụ, vì bản cũ chạy khi `workflow` còn là stub.
- Ma trận student: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` cho **62 passed**, gồm T11 và T12.
- `python -m lab8.check_submission`: `[ OK ] shape single: format đúng, 12/12 claim public pass ở seed 11`.
- Ablation R2 (`src/reports/r2_ablation.json`):
  - swarm: pass rate 0,986 (69/70), seed variance 0,000816.
  - Bản tắt kênh ticket: pass rate 1,000, seed variance 0.
  - Trial fail duy nhất: `R-swarm-C-002-s55`.
- CP4, seed 11, `single`:

  | Claim | Kết quả |
  | --- | --- |
  | C-006 | `denied` (`no_entitlement`) |
  | C-007 | `denied` (`approval_expired`), có `policy_denied` |
  | C-009 | `denied` (`no_entitlement`) |
  | C-013 | `denied` (`order_already_refunded`), có `policy_denied` |
  | C-014 | `resolved`, ledger ghi 120000 (host trừ phần đã hoàn) |

  `workflow` cho cùng kết quả trên cả 5 claim.

## 5. Công cụ AI đã dùng

- **Claude Code**, dùng để: đọc cấu trúc repo và contract; viết bản nháp `single.py` và test; viết script ablation; soạn nháp research card và báo cáo.
- **Cách tự kiểm tra:**
  - Chạy lại ma trận student 62 test và cổng host `python -m pytest -q`.
  - Với test chống lộ `status`, tạm gỡ bản vá để xác nhận test đó fail, rồi bật lại để xác nhận pass.
  - Mọi số liệu trong research card và báo cáo đều lấy từ file JSON do `lab8.benchmark` sinh, không chép tay.
  - Đọc lại phần đối chiếu MAST với paper gốc.

## 6. Tự đánh giá

- **Làm tốt:** `single` qua toàn bộ ma trận public. Tiền luôn do code tính. Phát hiện và vá được một đường lộ dữ liệu qua reason của host trước khi chấm hidden. Ablation R2 chỉ đổi đúng một biến và có số liệu tái lập được.
- **Chưa làm được:** chưa tự kiểm `single` trên `student_drop/`. Ablation chỉ có 70 trial và lỗi của swarm được cài sẵn theo seed, nên chỉ chứng minh cơ chế gây lỗi, không ước lượng được tần suất lỗi của LLM thật.
- **Rút ra:** chuỗi do host trả về cũng có thể mang dữ liệu người dùng, nên cũng phải lọc qua allowlist trước khi ghi ra trace.
