# Phân công nhóm: Triển khai các shape xử lý yêu cầu hoàn tiền

Đây là phương án chia việc cho sáu người đối với `specs/001-claim-shape-implementation/`.
Thay `Thành viên 1`–`Thành viên 6` bằng tên thật trước khi triển khai. Mỗi người làm trên
nhánh riêng và gửi thay đổi qua Pull Request để được đánh giá. Không sửa mô-đun do người khác
phụ trách nếu chưa thống nhất.

## Bảng phân công

| Vai trò | Thành viên | Trách nhiệm đề xuất | Task | File chính | Khối lượng/rủi ro dự kiến |
|---|---|---|---|---|---|
| Trưởng nhóm | Đào Đức Duy - 2A202603900 | Trưởng tích hợp; chốt hợp đồng/quyền sở hữu file dùng chung; kiểm tra nộp bài cuối | T001, T003, T014 | `docs/team-assignments.md`, tài liệu hợp đồng (đánh giá/cố định, không sửa code), `src/lab8/check_submission.py` (chỉ chạy/đọc) | Trung bình; rủi ro điều phối. Không sở hữu shape. |
| Thành viên | Bùi Ngọc Hùng - 2A202603770 | Shape A workflow | T004–T005 | `src/lab8/shapes/workflow.py`, `src/tests/test_workflow_shape.py` | Trung bình; luồng xác định, ranh giới kết quả/trace/refund. |
| Thành viên | Nguyễn Minh Nhân - 2A202603723 | Shape B single-agent | T006–T007 | `src/lab8/shapes/single.py`, test riêng chưa có trong lịch sử hiện có | Trung bình-cao; hành vi ReAct/tool và giới hạn 8 bước. |
| Thành viên | Trần Cảnh Hưng - 2A202603759 | Shape C orchestrator/investigator | T008–T009 | `src/lab8/shapes/orchestrator.py`, `src/tests/test_orchestrator_shape.py` | Cao; handoff/quyền riêng tư và quyền của investigator. |
| Thành viên | Nguyễn Vắn Quốc - 2A202603864 | Kiểm tra ban đầu, kiểm thử tổng hợp, an toàn crash, xác minh cuối | T002, T010–T011, T016 | Chỉ chạy lệnh trong `src/`; report sinh ra `src/reports/crash.json`; gửi bằng chứng cho Thành viên 1 cập nhật tài liệu này | Trung bình-cao; chịu trách nhiệm các cổng tích hợp. Không sửa test/host được bảo vệ. |
| Trưởng nhóm (cùng người Thành viên 1) | Đào Đức Duy - 2A202603900 | Benchmark và báo cáo bằng chứng; chỉ làm chủ đề thưởng nếu nhóm chọn | T012–T013, T015 | `src/reports/benchmark.json` do công cụ sinh; các báo cáo team | Cao gần hạn nộp; ADR phụ thuộc kết quả có thể tái lập. |

## Quy ước nhánh và PR

Mỗi thành viên dùng một nhánh riêng, ví dụ `member-01/claim-shapes` đến
`member-06/claim-shapes`. Đây chỉ là tên gợi ý; nhóm có thể theo quy ước nhánh hiện tại miễn
là mỗi người có nhánh riêng. Mỗi PR PHẢI ghi Task ID và Requirement ID liên quan, kèm bằng
chứng kiểm thử hoặc hướng dẫn xác minh có thể tái lập, và không chứa thay đổi ngoài phạm vi.

## Phụ thuộc và các mốc tích hợp

| Mốc | Task bắt buộc | Tiêu chí hoàn tất | Điều phối |
|---|---|---|---|
| Sẵn sàng nền tảng | T001–T003 | Ghi nhận đủ sáu người/nhánh; `lab8.smoke` và host pytest pass; xác nhận hợp đồng dùng chung và ranh giới file. | Thành viên 1 điều phối; Thành viên 5 cung cấp kết quả ban đầu. |
| Lát cắt MVP | T004–T005 | Test workflow và nhóm student test của workflow pass. Đây chưa phải hoàn thành toàn bộ bài. | Thành viên 2 gửi PR; Thành viên 1 đánh giá ranh giới tích hợp. |
| Hoàn thành ba shape | T006–T009 | Test single-agent và orchestrator pass; cả ba PR shape đã được đánh giá/merge. | Thành viên 2–4 làm song song sau khi nền tảng hoàn tất. |
| Cổng tích hợp | T010 | Student matrix và host suite đầy đủ pass; không còn vi phạm chưa xử lý trong rà soát toàn vẹn/bảo mật. | Thành viên 5 chạy; Thành viên 1 điều phối sửa lỗi qua PR của người phụ trách. |
| Sẵn sàng bằng chứng | T011–T013 | Crash report `20/20`; benchmark gồm bốn shape, số claim/seed bắt buộc; báo cáo trích số liệu/run ID/commit từ output. | Thành viên 5 và 6 tạo hai report riêng song song; Thành viên 6 đợi đủ hai report rồi mới viết ADR. |
| Sẵn sàng nộp bài | T014–T016 | Checker `0 FAIL`; rà soát điều kiện nộp; ghi nhận kết quả xác minh theo tài liệu. | Thành viên 1 kiểm tra cuối; Thành viên 5 ghi kết quả; chỉ làm chủ đề thưởng sau khi phần bắt buộc xong. |

## Kiểm soát file dùng chung và xung đột

- **Mô-đun shape**: Thành viên 2, 3, 4 sở hữu độc quyền các mô-đun tương ứng. Không chỉnh sửa đồng thời cùng một mô-đun.
- **Kiểm thử**: mỗi người phụ trách shape chỉ thêm test trong file mới do mình phụ trách. `src/tests/test_public_matrix.py` và host tests là cổng nghiệm thu dùng chung, chỉ đọc.
- **API/host dùng chung**: `src/lab8/schemas.py`, `src/lab8/shapes/common.py`, `tools.py`, `runtime.py`, `handoff.py`, `durability.py`, `policy.py`, `metrics.py`, `db.py`, config và data không phải mục tiêu chỉnh sửa song song; một số file bị quy định bài tập cấm sửa.
- **Báo cáo**: lệnh benchmark và crash ghi ra hai file riêng, vì vậy Thành viên 5 và 6 có thể chạy song song sau T010. Mỗi file chỉ có người được giao tạo; không ai sửa JSON report bằng tay.
- **Tài liệu nhóm**: file này và `TEAM.md` là tài nguyên dùng chung. Thành viên gửi kết quả/dòng đóng góp cho Thành viên 1 tổng hợp thay vì cùng sửa đồng thời.
- **Tệp phát sinh khi chạy**: dùng đường dẫn SQLite riêng cho từng test/run; không dùng chung DB đang chạy và không commit SQLite/trace.
- **Sửa lỗi tích hợp**: chuyển thay đổi cho người phụ trách mô-đun và merge qua PR. Khi cần đổi hợp đồng dùng chung, tạm dừng phần việc phụ thuộc cho đến khi các thành viên liên quan thống nhất và hợp đồng cập nhật được đánh giá.

## Cổng hợp đồng và xác nhận nhóm (T003)

Trước khi bắt đầu triển khai song song, các thành viên xác nhận giữ nguyên các hợp đồng hiện có:

- **Callable/result**: mỗi shape cung cấp `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`; giữ nguyên `run_id`, các status cho phép, amount và budget như trong `specs/001-claim-shape-implementation/contracts/run-claim.md`.
- **Refund/host**: code tính quote, gửi toàn bộ quote cùng `crash_at` đến host; host giữ quyền kiểm tra approval/cap, ghi refund/audit và bảo đảm idempotency. Không bắt `InjectedCrash` trong shape.
- **Trace/privacy**: mỗi lần chạy bình thường có trace mới với run ID khớp và `events` là list; không ghi secret/PII vào trace, side file hoặc stdout.
- **Orchestrator**: chỉ chuyển facts theo allowlist qua handoff; investigator chỉ có tool đọc, không nhận raw parent context/secret và không có quyền ghi.
- **Quyền sở hữu**: Hùng sở hữu `workflow.py` và test riêng; Nhân sở hữu `single.py` và test riêng; Hưng sở hữu `orchestrator.py` và test riêng. Các module host/runtime/schema và test matrix hiện có là ranh giới dùng chung, không được sửa song song.
- **Làm việc nhóm**: mỗi người dùng branch riêng; tích hợp qua PR review; không sửa module người khác nếu chưa thống nhất.

Các chi tiết chuẩn tắc nằm trong `specs/001-claim-shape-implementation/contracts/run-claim.md`,
`specs/001-claim-shape-implementation/contracts/shape-integration.md` và
`specs/001-claim-shape-implementation/plan.md`. Bảng dưới đây ghi nhận xác nhận thực tế; không
được xem việc tài liệu đã ghi contract là sự đồng ý thay cho thành viên.

| Thành viên | Tên trong nhóm | Trạng thái xác nhận contract/file ownership | Ngày |
|---|---|---|---|
| Thành viên 1 | Đào Đức Duy (2A202603900) | Đã thống nhất theo xác nhận của người dùng cho cả nhóm | 2026-11-17 |
| Thành viên 2 | Bùi Ngọc Hùng (2A202603770) | Đã thống nhất theo xác nhận của người dùng cho cả nhóm | 2026-11-17 |
| Thành viên 3 | Nguyễn Minh Nhân (2A202603723) | Đã thống nhất theo xác nhận của người dùng cho cả nhóm | 2026-11-17 |
| Thành viên 4 | Trần Cảnh Hưng (2A202603759) | Đã thống nhất theo xác nhận của người dùng cho cả nhóm | 2026-11-17 |
| Thành viên 5 | Nguyễn Vắn Quốc (2A202603864) | Đã thống nhất theo xác nhận của người dùng cho cả nhóm | 2026-11-17 |
| Thành viên 6 | Đào Đức Duy (2A202603900, cùng người Thành viên 1) | Đã thống nhất theo xác nhận của người dùng cho cả nhóm | 2026-11-17 |

## Trạng thái phần benchmark/report/bonus (T012–T015)

- **T010**: người dùng xác nhận các thành viên khác đã hoàn tất phần việc của họ; output console của host/student tests chưa được lưu trong workspace.
- **T011**: `src/reports/crash.json` hiện có `passed: 20`, `crash_safety: 20/20`.
- **T012**: `src/reports/benchmark.json` được sinh bằng `lab8.benchmark` cho 14 claim × 5 seed × 4 shape. Người dùng xác nhận đã chạy lại bằng `python -m` trong `.venv` theo hướng dẫn; phiên bản Python/output console lần chạy lại chưa được lưu trong workspace.
- **T013**: TEAM và năm báo cáo cá nhân (năm người có tên duy nhất; Đào Đức Duy đảm nhiệm hai vai trò) đã được điền theo assignment và lịch sử Git. Các trường danh tính không có trong nguồn, AI-use cá nhân và output test chưa được xác nhận được đánh dấu rõ. Không có test cá nhân trong commit hiện có của Duy, Nhân hoặc Quốc; đây vẫn là thiếu sót theo checklist nộp bài, không được coi là đã đáp ứng tiêu chí mỗi thành viên có test. `f176005` là HEAD mã nguồn được benchmark; hash nộp cuối cần xác nhận sau khi commit report.
- **T015**: nhóm đã chọn B7. Có test metamorphic và `report/team/bonus_report.md`; full pytest hiện pass 170 test (248 deselected), bonus tests pass 5/5 và checker ra 0 FAIL. `reports/hidden_grade.json` không có trong workspace nên chưa xác minh gate hidden ≥ 0.80/leak/bypass; chưa đủ căn cứ ghi nhận bonus đạt điều kiện tính điểm.

## Truy vết yêu cầu theo người phụ trách

| Mã yêu cầu | Người phụ trách chính | Người xác minh/tích hợp |
|---|---|---|
| M-01–M-07 | Thành viên 2 và 3 | Thành viên 5 tích hợp; Thành viên 1 điều phối contract |
| M-01–M-08 | Thành viên 4 | Thành viên 5 tích hợp; Thành viên 1 điều phối contract |
| M-09 | Thành viên 5 | Thành viên 1 kiểm tra cuối |
| M-10 | Thành viên 5 và 6 | Thành viên 6 tổng hợp báo cáo |
| M-11 | Thành viên 6 | Thành viên 1 đánh giá việc truy vết nguồn |
| M-12 | Thành viên 1 và 6 | Thành viên 1 kiểm tra cuối |
| M-13 | Tất cả thành viên trong phần việc của mình | Thành viên 5 rà soát; Thành viên 1 ghi nhận kết quả |
| O-01 | Thành viên 6, chỉ khi nhóm chọn | Thành viên 5 xác minh các cổng bắt buộc |

## Nhật ký bằng chứng

Thành viên 1 ghi ngày, lệnh, mã thoát và tóm tắt kết quả cho các cổng ban đầu/tích hợp/cuối
tại đây. Không ghi secret, nhãn hidden hoặc dữ liệu kiểm thử được bảo vệ.

| Ngày | Task ID | Lệnh/kiểm tra | Vị trí kết quả/bằng chứng | Người phụ trách |
|---|---|---|---|---|
| 2026-11-17 | T002 | `python -m lab8.smoke`; `python -m pytest -q` từ `src/` | Người dùng xác nhận đã chạy hoàn tất T002 trong `.venv`; output/exit code chi tiết chưa được cung cấp trong phiên này | Thành viên 5 |
| 2026-11-17 | T010 | Toàn bộ host suite và student matrix | Người dùng xác nhận các thành viên hoàn tất; raw output chưa lưu trong workspace | Thành viên 5 |
| 2026-11-17 | T011 | `python -m lab8.crash_test --count 20 --out reports/crash.json` | `src/reports/crash.json`: `passed=20`, `crash_safety=20/20` | Thành viên 5 |
| 2026-11-17 | T012 | `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json` | `src/reports/benchmark.json`; 4 shape × 14 claim × 5 seed; representative run ID `R-workflow-C-001-s11`; người dùng xác nhận chạy lại trong `.venv`, chưa lưu Python version/console output | Thành viên 6 |
| 2026-11-17 | T013 | Điền ADR, research card, group report từ benchmark | Các report đã có bản dựa trên số liệu public; TEAM/personal reports còn thiếu thông tin thành viên | Thành viên 6 |
| 2026-11-17 | T014 | `python3 -m lab8.check_submission` từ `src/` | `1 FAIL`: bảng đóng góp `TEAM.md` trống; có `1 WARN` do report/docs chưa commit | Thành viên 1 |
| 2026-11-17 | T015 | Kiểm tra đăng ký bonus topic | Chưa có topic B1–B7 nào được ghi nhận; không tạo bonus code/report | Thành viên 6 |
