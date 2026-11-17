Với **Lab 8 – From Workflows to Agents**, mình đề xuất chia 4 người theo mô hình **3 người triển khai kiến trúc + 1 người phụ trách Reliability & Evaluation**.

Cách này giúp các thành viên có thể code song song, hạn chế conflict Git và mỗi người có sản phẩm cụ thể để chứng minh đóng góp.

## **1. Bảng phân chia công việc**

| Thành viên | Phụ trách                | Công việc chính                                                   | Độ khó     |
| ---------- | ------------------------ | ----------------------------------------------------------------- | ---------- |
| **TV1**    | Workflow (A)             | Implement pipeline cố định, policy flow, unit test                | Trung bình |
| **TV2**    | Single Agent (B)         | Implement ReAct loop, tool calling, kiểm soát số bước và lỗi      | Khá        |
| **TV3**    | Orchestrator (C)         | Implement điều phối, investigator, handoff an toàn                | Khó        |
| **TV4**    | Reliability & Evaluation | Crash testing, benchmark, phân tích metrics, ADR và research card | Khá–Khó    |

**Swarm (D) đã được cung cấp sẵn**, nên không cần phân một người viết lại.

## **2. Đầu ra cụ thể của từng người**

**TV1 — Workflow Engineer**

Hoàn thiện `workflow.py`, xây dựng pipeline theo business rules, gọi đúng các hàm xử lý và đảm bảo refund chỉ được thực hiện thông qua host.

**Đầu ra:** Workflow chạy được, test riêng cho Workflow và phần phân tích A trong báo cáo.

**TV2 — Agent Engineer**

Hoàn thiện `single.py`, xử lý ReAct loop tối đa 8 bước, gọi read-only tools, kiểm soát kết quả model và chuyển quyết định cuối cùng cho host.

**Đầu ra:** Single Agent chạy được, test trường hợp model trả lỗi và phần phân tích B.

**TV3 — Multi-Agent Engineer**

Hoàn thiện `orchestrator.py`, thiết kế investigator, kiểm soát dữ liệu handoff bằng `make_handoff`, phối hợp kết quả và bảo vệ thông tin nhạy cảm trong trace.

**Đầu ra:** Orchestrator chạy được, test handoff và phần phân tích C.

**TV4 — Reliability & Evaluation Engineer**

Viết test bổ sung cho idempotency, crash recovery, policy/approval; chạy crash suite và benchmark 4 kiến trúc trên cùng seeds. Tổng hợp số liệu, soạn ADR và research card với sự đóng góp của các thành viên.

**Đầu ra:** `benchmark.json`, `crash.json`, test reliability, `decision_adr.md`, `research_card.md`.

## **3. Phối hợp để không bị lệch khối lượng**

Điểm cần lưu ý là **TV3 có phần code khó nhất**, còn **TV4 có nhiều việc ở giai đoạn cuối**. Vì vậy, mình đề xuất phân bổ hỗ trợ như sau:

| Giai đoạn | TV1         | TV2         | TV3          | TV4                          |
| --------- | ----------- | ----------- | ------------ | ---------------------------- |
| Setup     | Setup chung | Đọc ReAct   | Đọc handoff  | Chuẩn bị test                |
| Implement | Workflow    | Single      | Orchestrator | Viết reliability tests       |
| Kiểm thử  | Test A      | Test B      | Test C       | Crash suite, test tổng hợp   |
| Benchmark | Phân tích A | Phân tích B | Phân tích C  | Chạy benchmark D và tổng hợp |
| Báo cáo   | Viết phần A | Viết phần B | Viết phần C  | Tổng hợp ADR, research card  |

**Quy tắc phối hợp:** TV1–TV3 phải tự sửa lỗi của kiến trúc mình phụ trách. TV4 không phải người sửa mọi lỗi, mà chịu trách nhiệm phát hiện lỗi hệ thống, xác minh độ tin cậy và tổng hợp kết quả.

## **4. Phân chia Git để tránh conflict**

```
main
├── feature/workflow        # TV1
├── feature/single-agent    # TV2
├── feature/orchestrator    # TV3
└── feature/evaluation      # TV4
```

Mỗi người làm trên branch riêng, tạo Pull Request và được ít nhất một thành viên khác review trước khi merge.

Về báo cáo, mỗi người viết phần kiến trúc hoặc kết quả mình phụ trách. TV4 tổng hợp, nhưng quyết định cuối cùng trong ADR cần được cả nhóm thống nhất.

**Kết luận:** Mình đánh giá đây là phương án chia hợp lý nhất cho 4 người vì có 3 đầu việc code độc lập, một đầu việc kiểm chứng chất lượng, và cả nhóm đều có đóng góp kỹ thuật rõ ràng. Đặc biệt, đừng để TV4 chỉ làm báo cáo: người này cần thực sự viết test và thực hiện evaluation để khối lượng công việc tương xứng.