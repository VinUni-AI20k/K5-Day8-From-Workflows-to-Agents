# Báo cáo nhóm — Lab 8 LogiX-VN

Số liệu lấy từ JSON do công cụ lab sinh ra; chi phí là VND mô phỏng.

## 1. Thông tin nhóm

- Tên nhóm: MID
- Thành viên: Quách Ngọc Phúc, Ngô Văn Tuân, Trần Thanh Long, Nguyễn Đức Minh; chi tiết tại [TEAM.md](../../TEAM.md).
- Commit kỹ thuật dùng tái lập (trùng ADR): `b3f45ba`.
- Branch đang tổng hợp: `feature/tuan-evaluation-report`; cần merge vào nhánh nộp sau review.

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng quy trình claim theo ba shape A/B/C và dùng swarm D có sẵn làm đối chứng. Mục tiêu là chọn kiến trúc ít tự chủ nhất nhưng đáp ứng luật hoàn tiền. Phúc phụ trách A, Minh phụ trách B, Long phụ trách C, Tuân phụ trách kiểm thử ledger/crash và evaluation/report.

Code quyết định số tiền, ownership, policy hiện hành, approval, trần theo đơn và idempotency. Ticket là dữ liệu người dùng; số ngày trễ trong ticket không thay thế order row.

## 3. Giải pháp

| Shape | Cách xử lý trong implementation hiện tại |
| --- | --- |
| A `workflow` | Python đọc claim view, lookup order, gọi `compute_compensation`, rồi gọi host nếu quote > 0. Không gọi model. |
| B `single` | `run_react` tối đa 8 bước, chỉ dispatch tool đọc. Callback Python chọn chuỗi tool và gọi MockLLM để ghi nhận cost; model output không điều khiển số tiền. Sau loop, code gọi host. |
| C `orchestrator` | Dựng handoff bằng `make_handoff`, chạy investigator với `lookup_order`, `lookup_refund_history`, `compute_compensation`; orchestrator lấy quote, gọi MockLLM để draft và gọi host. |
| D `swarm` | Reference có các lời gọi peer/parse/draft; ở seed chia hết cho 5 có điểm yếu cố ý tin delay trong ticket. |

Cả bốn truyền quote đầy đủ vào `durability.issue_refund`. Host tự trừ refund lịch sử, cap approval/paid và ghi ledger cùng audit trong một transaction. Các shape truyền `crash_at`, để `InjectedCrash` đi ra ngoài; checkpoint không thay thế ledger.

Handoff C dùng facts rỗng và allowlist tool đọc. Trace C ghi handoff đã sanitize, investigator summary, quote và decision. A ghi claim/order lookup, quote, refund outcome và decision; B ghi claim read, agent tool, quote, refund host và outcome. Các nhánh return dùng `finish()` để ghi trace và đối chiếu ledger. Không dump raw claim/order, parent secret, header, phone, địa chỉ, internal note hoặc tên hàng.

## 4. Kết quả

Benchmark [benchmark.json](../../src/reports/benchmark.json): cùng 14 claim, seed `11,22,33,44,55`, `as_of=2026-11-15`, MockLLM, tool, evaluator và giá; mỗi trial một SQLite mới. Mỗi shape có 70 trial.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| workflow | 1,000000 | 1,000000 | 1,000000–1,000000 | 0 | 27,857143 | 4,428571 / 5 |
| single | 1,000000 | 1,000000 | 1,000000–1,000000 | 0 | 46,398571 | 7,000000 / 8 |
| orchestrator | 1,000000 | 1,000000 | 1,000000–1,000000 | 0 | 47,230000 | 3,714286 / 4 |
| swarm | 0,985714 | 0,928571 | 0,928571–1,000000 | 0,000816327 | 49,566957 | 2,800000 / 3 |

Run id dẫn chứng: `R-workflow-C-001-s11`; lỗi swarm: `R-swarm-C-002-s55`. C-002 có delay thực tế 2 ngày nhưng ticket nói 5 ngày, nên swarm refund sai ở seed 55. Các số đã được chạy lại và JSON khớp bản benchmark trước đó.

Crash suite [crash.json](../../src/reports/crash.json) đạt **20/20**. Ngoài suite host, chín test mới kiểm tra A/B/C với ba điểm crash trên claim hoàn phần chênh lệch C-014: refund cũ 30.000 VND, entitlement 150.000 VND, effect mới 120.000 VND; retry qua ba seed vẫn một refund mới và một committed audit. Toàn bộ host/student đạt **316 passed** tại commit kỹ thuật, gồm 14 trường hợp nhóm thêm. Không có `student_drop/` trên máy ở lần kiểm tra này; chưa kết luận pass rate hidden ≥ 0,75.

Ablation R2 trong [research_peer_ablation.json](../../src/reports/research_peer_ablation.json) tắt riêng lời gọi peer acknowledgement của swarm. Hai nhánh cùng đạt 69/70 trial; cost/success giảm 49,566957 → 48,691594 VND (1,766020%), mean model calls 3 → 2. Cả hai vẫn fail C-002/seed 55: bỏ acknowledgement không sửa việc tin ticket. Đây là ablation phục vụ research card, chưa đăng ký/chấm bonus.

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

- Lần đầu chạy `python -m pytest -q -m student -o addopts= -k orchestrator` đạt 61 passed, 1 failed tại T12, thông báo `crash did not fire`. Nguyên nhân: `del crash_at` và không forward vào `issue_refund`. Commit `06fa360` đã sửa; chạy lại C đạt 62 passed.
- Windows báo `PytestCacheWarning: [WinError 5] Access is denied` khi ghi pytest cache. Chạy với `-p no:cacheprovider`; assertion và lựa chọn test giữ nguyên.
- Các lệnh benchmark, crash và test được lưu trong ADR/research card để chạy lại; không sửa tay JSON.

## 6. Tổng hợp đóng góp

Xem bảng đóng góp [TEAM.md](../../TEAM.md) và [báo cáo Ngô Văn Tuân](2A202603630_NgoVanTuan.md). Lịch sử hiện tại có commit implementation cho cả A/B/C; ba người phụ trách shape còn cần bổ sung test riêng. Báo cáo cá nhân của Phúc và Minh chưa có; báo cáo Long còn nội dung mẫu. Các phần này cần chính thành viên hoàn thiện trước khi nộp.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model production, latency là `unavailable`, cost không phải hóa đơn API. Steps đếm event trace; độ chi tiết event khác giữa shape nên không suy ra latency từ số steps. Benchmark A/B/C/D còn khác implementation, prompt và số tool thực sự gọi; không coi chênh lệch quan sát là tác động riêng của topology. Chỉ ablation peer giữ các yếu tố đó cố định ngoài lời gọi được tắt.

Public có 14 claim và lỗi swarm cố ý; cần hidden và dữ liệu thực tế để kiểm tra khả năng khái quát. Crash là exception định sẵn, chưa mô phỏng mất điện hoặc tranh chấp nhiều process. Chọn workflow trong phạm vi hiện tại; xem xét lại nếu task cần đọc ngôn ngữ mơ hồ/tra cứu thích ứng và shape khác cải thiện đủ trên tập độc lập, vẫn qua safety với cost chấp nhận được.

## 8. Tài liệu tham khảo

- [Luật nghiệp vụ](../../docs/business_rules.md), [contract](../../docs/contracts.md), [metrics](../../docs/metrics.md), [rubric](../../RUBRIC.md).
- Cemri và cộng sự, *Why Do Multi-Agent LLM Systems Fail?*, NeurIPS 2025, [nguồn chính thức](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html). Taxonomy MAST được dùng làm khung phân tích, không coi là bằng chứng trực tiếp cho hiệu năng LogiX-VN.
