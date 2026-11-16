# Báo cáo nhóm — Lab 8 LogiX-VN

## 1. Thông tin nhóm

- Nhóm: Mien Nui, lớp L3A.
- Thành viên: Nguyễn Lâm Hoàng, Nguyễn Tiến Khoa, Nguyễn Tuấn Quang và Phan Hải Đăng. [TEAM.md](../../TEAM.md)
- Commit chốt trong ADR: `7d7506e`. Mã tích hợp và hai JSON được đưa vào từ `ede52b8`. [ADR](decision_adr.md)

## 2. Mục tiêu và cách tiếp cận

Nhóm triển khai cùng bài toán xét hoàn phí cho LogiX-VN bằng ba shape `workflow`, `single` và `orchestrator`. `swarm` có sẵn trong đề bài và được dùng làm đối chứng. Sau khi tích hợp với host, nhóm chạy ma trận public, kiểm thử crash và đo cả bốn shape trên cùng tập claim, seed và bảng giá mô phỏng. Mục tiêu là chọn kiến trúc có mức tự chủ thấp nhất vẫn đáp ứng yêu cầu về kết quả, an toàn và khả năng chạy lại.

## 3. Giải pháp

| Shape | Luồng xử lý và ranh giới quyền |
| --- | --- |
| A · `workflow` | Python đọc claim, tra đơn theo chủ sở hữu và gọi `compute_compensation` với dữ liệu đơn cùng policy hiện hành. Khi đề xuất dương, shape gọi host. Shape dùng 0 lần gọi MockLLM. |
| B · `single` | Sau khi đọc claim, shape dùng `run_react(max_steps=8, worker=True)`. Hàm `decide` dùng kết quả bước trước để gọi `lookup_order` rồi `compute_compensation`. MockLLM được gọi trong vòng lặp và được tính vào `Budget`. Kết quả văn bản từ MockLLM chưa tham gia chọn tool. Yêu cầu hoàn phí được gửi sau khi vòng lặp kết thúc. |
| C · `orchestrator` | Orchestrator đọc claim, gửi `handoff.v1` cho investigator và nhận dữ liệu đơn từ tool `lookup_order`. Orchestrator tính khoản đề xuất bằng code và gọi host. Shape dùng 0 lần gọi MockLLM. |

**Handoff và trace.** `make_handoff` áp danh sách trường được phép. Payload của orchestrator dùng phạm vi `owner_order_only`, `facts` rỗng và một tool đọc duy nhất là `lookup_order`. Trace của shape C ghi handoff đã lọc, trạng thái truy cập đơn, số tiền đề xuất, lần yêu cầu hoàn phí và trạng thái cuối. Workflow và single ghi thêm bước đọc claim, kết quả host và quyết định. Single có event `react_action` cho lần chọn tool. Trace tránh ghi ticket, dữ liệu thô của claim hoặc đơn, header, secret và các trường PII. `common.finish()` ghi trace cho mỗi nhánh trả kết quả và lấy effect cùng số audit từ sổ hoàn tiền.

**Quyền ghi và phục hồi.** Cả ba shape truyền toàn bộ khoản đề xuất vào `durability.issue_refund`. Host kiểm approval đúng claim, trừ số đã hoàn trước đó và áp trần theo đơn. Với C-014, đề xuất là 150.000 VND và effect là 120.000 VND sau khi host trừ 30.000 VND đã hoàn. Ledger sử dụng khóa `refund:{claim_id}` và ghi refund cùng audit `refund_committed` trong một transaction. Các shape chuyển `crash_at` xuống host và để `InjectedCrash` truyền ra ngoài. [Luật nghiệp vụ](../../docs/business_rules.md) · [Contract](../../docs/contracts.md)

## 4. Kết quả

Benchmark chạy 14 claim public với seed `11,22,33,44,55`, tổng cộng 280 lượt. Mỗi lượt dùng một DB SQLite mới. Chi phí là VND mô phỏng và số bước là số event trong trace. [Benchmark JSON](../../src/reports/benchmark.json) · [Định nghĩa metric](../../docs/metrics.md)

| Shape | Lượt đạt | Pass rate | Pass^5 | Seed min–max | Variance | VND/lượt đạt | Mean/p95 steps |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| `workflow` | 70/70 | 1,0000 | 1,0000 | 1,0000–1,0000 | 0,000000 | 34,29 | 5,07 / 6 |
| `single` | 70/70 | 1,0000 | 1,0000 | 1,0000–1,0000 | 0,000000 | 35,42 | 6,86 / 8 |
| `orchestrator` | 70/70 | 1,0000 | 1,0000 | 1,0000–1,0000 | 0,000000 | 43,57 | 4,36 / 5 |
| `swarm` | 69/70 | 0,9857 | 0,9286 | 0,9286–1,0000 | 0,000816 | 49,57 | 2,80 / 3 |

`swarm` sai ở `R-swarm-C-002-s55`. Ở seed 55, shape tham chiếu dùng số ngày trễ trong ticket và trả `resolved`, trong khi dữ liệu đơn cho kết quả `denied`. Ba shape nhóm đạt cả năm seed ở claim này. Crash suite đạt **20/20** cho host và swarm. Các ca T11/T12 trong ma trận student kiểm retry và crash/resume của từng shape. Lần kiểm tra bản tích hợp có **104 test mặc định** và **248 test student** đạt. Repo chưa có báo cáo tự kiểm `student_drop/`. [Crash JSON](../../src/reports/crash.json) · [Ma trận public](../../src/tests/test_public_matrix.py)

**Quyết định của nhóm:** chọn `workflow`. Shape đạt 70/70 trên bộ public và có chi phí mô phỏng thấp nhất, 34,29 VND mỗi lượt đạt. Kiểm tra hidden local bằng benchmark có nhãn cho `workflow`, `single` và `orchestrator` cùng đạt 200/200, còn `swarm` đạt 194/200. Phiếu nghiên cứu R3 đối chiếu `single` và `swarm` trên public, với giới hạn là hai cách triển khai còn khác nhau về luồng tool và lỗi có chủ đích. [ADR](decision_adr.md) · [Research card](research_card.md)

## 5. Khó khăn và cách xử lý

Khi mô phỏng cách grader chép ba file shape của nhóm vào starter, lệnh `python -c "from lab8.shapes import SHAPES"` từng báo `ModuleNotFoundError: No module named 'lab8.shapes.ledger'`. File helper do nhóm thêm nằm ngoài danh sách được chép. Commit `ede52b8` chuyển ba shape sang gọi trực tiếp `durability.issue_refund` và `common.finish`. Sau sửa, phép import thành công trên bản sạch. Chạy lại benchmark và crash suite trên bản đó cho nội dung JSON khớp hoàn toàn với hai file đã commit. [Cách grader nạp shape](../../docs/instructor.md) · [Lệnh tạo lại bằng chứng](../../src/reports/README.md)

## 6. Tổng hợp đóng góp

| Thành viên | Phần phụ trách và bằng chứng |
| --- | --- |
| Nguyễn Lâm Hoàng · `2A202603448` | Workflow và tích hợp, gồm test workflow và test tích hợp các shape. [Báo cáo cá nhân](2A202603448_NguyenLamHoang.md) |
| Nguyễn Tiến Khoa · `2A202603460` | Triển khai single ban đầu trong `1198aab`. Vòng `run_react` hiện tại nằm trong commit tích hợp `ede52b8`. [Báo cáo cá nhân](2A202603460_NguyenTienKhoa.md) |
| Nguyễn Tuấn Quang · `2A202603392` | Orchestrator, handoff chỉ đọc và test ranh giới handoff tại `8939976`. [Báo cáo cá nhân](2A202603392_NguyenTuanQuang.md) |
| Phan Hải Đăng · `2A202603409` | Ledger và kiểm thử tích hợp CP3 tại `2b641f6` và `45fcb56`. [Báo cáo cá nhân](2A202603409_PhanHaiDang.md) |

## 7. Hạn chế và hướng cải thiện

Benchmark public giới hạn ở 14 claim và năm seed. Các ngưỡng hidden cho shape chọn, gồm pass rate tối thiểu 0,75 và các cổng approval, secret, crash, cần được xác nhận bằng bộ chấm chính thức. Lab dùng MockLLM và bảng giá mô phỏng, latency là `unavailable`. Chênh lệch số bước phản ánh số event mỗi shape ghi trong trace. Với `single`, việc chọn tool hiện do `decide` thực hiện theo logic cố định, nên số liệu chỉ mô tả cách cài đặt này.

Có thể xem lại lựa chọn `workflow` nếu tập đánh giá mở rộng cho thấy shape khác xử lý thêm được các claim mà workflow bỏ sót, vẫn đạt các cổng an toàn và mức tăng tỷ lệ thành công đủ lớn so với chi phí tăng thêm.

## 8. Tài liệu tham khảo

- [Đề bài và checkpoint](../../README.md) · [CHECKPOINTS.md](../../CHECKPOINTS.md)
- [Kiến trúc](../../docs/architecture.md) · [Luật nghiệp vụ](../../docs/business_rules.md) · [Contract kết quả và trace](../../docs/contracts.md)
- [Metric](../../docs/metrics.md) · [Rubric](../../RUBRIC.md) · [Yêu cầu nộp bài](../../SUBMISSION.md)
