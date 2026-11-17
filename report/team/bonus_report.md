# Bonus report: B3

- **Topic + nguồn:** B3 · Verifier/aggregator chống khuếch đại lỗi (*Towards a Science of Scaling Agent Systems*, Google Research 2026, Slide 17, 22, 42).
- **CLAIM của nguồn:** Hệ thống multi-agent độc lập (decentralized / swarm) khuếch đại lỗi từ các bước trung gian lên tới 17.2×, trong khi kiến trúc có kiểm soát tập trung (orchestration / verification) giảm hệ số khuếch đại xuống 4.4× hoặc triệt tiêu lỗi.
- **BOUNDARY:** Đo lường trên bài toán xử lý khiếu nại LogiX-VN; mô hình MockLLM xác định với lỗi ảo giác có chủ đích (bias tin số ngày trễ trong ticket thay vì dữ liệu có cấu trúc tại các seed chia hết cho 5); 14 claim public ($70$ trials) và 8 claim đối kháng ($40$ trials) qua 5 seed ngẫu nhiên (`11, 22, 33, 44, 55`).
- **HYPOTHESIS trên LogiX:** Việc tích hợp một tầng **Deterministic Code Verifier** chốt chặn trước khi ghi sổ cái sẽ đối chiếu toàn bộ dữ kiện (`delay_days`, `status`, `damage_verified`) với cơ sở dữ liệu SQLite, giúp triệt tiêu hoàn toàn hiện tượng khuếch đại lỗi ảo giác của Swarm, nâng pass rate của Swarm từ 0.986 (public) và 0.875 (adversarial) lên 1.000 mà không cần sửa đổi giao thức trao đổi giữa các agent.
- **Biến cố định / biến thay đổi:**
  - *Biến cố định:* Cùng database SQLite, danh sách claim, policy (`POL-2026-11`), bảng giá token/tool, số seed (`11, 22, 33, 44, 55`), evaluator và điều kiện must-pass.
  - *Biến thay đổi:* Kiến trúc điều phối (`workflow` xác định, `swarm` phân tán không kiểm duyệt, `swarm_verified` có tầng Code Verifier can thiệp ghi đè `verifier_override`).
- **Lệnh tái lập:**
  ```bash
  # Chạy trên bộ Public:
  python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_benchmark.json

  # Chạy trên bộ đối kháng:
  python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_adversarial_benchmark.json

  # Chạy unit tests:
  python -m pytest -q tests/test_bonus_swarm_verified.py
  ```
- **File report + run id minh họa:**
  - File report: `src/reports/bonus_benchmark.json` và `src/reports/bonus_adversarial_benchmark.json`.
  - Run ID minh họa can thiệp `verifier_override`: `R-swarm_verified-C-002-s55` (trong `src/traces/R-swarm_verified-C-002-s55.json`).

---

## Kết quả

### 1. Bảng số liệu trên bộ dữ liệu Public (14 claims $\times$ 5 seeds = 70 trials)
*Dữ liệu trích xuất từ file `reports/bonus_benchmark.json`:*

| Shape | Pass rate | Pass^5 | Seed Variance | Min Pass | Max Pass | Cost/Success (VND) | Mean Steps | Lỗi thường gặp |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **workflow** | **1.000** | **1.000** | **0.000000** | 1.000 | 1.000 | **27.86** | 3.79 | Không có |
| **swarm** | 0.986 | 0.929 | 0.000816 | 0.929 | 1.000 | 49.57 | 2.80 | `status resolved != denied` (C-002, seed 55) |
| **swarm_verified** | **1.000** | **1.000** | **0.000000** | 1.000 | 1.000 | 49.00 | 2.81 | **Không có (0 lỗi)** |

### 2. Bảng số liệu trên bộ dữ liệu đối kháng (8 claims $\times$ 5 seeds = 40 trials)
*Dữ liệu trích xuất từ file `reports/bonus_adversarial_benchmark.json`:*

| Shape | Pass rate | Pass^5 | Seed Variance | Min Pass | Max Pass | Cost/Success (VND) | Mean Steps | Lỗi thường gặp |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **workflow** | **1.000** | **1.000** | **0.000000** | 1.000 | 1.000 | **30.00** | 4.00 | Không có |
| **swarm** | 0.875 | 0.375 | 0.062500 | 0.375 | 1.000 | 61.92 | 3.17 | `resolved != denied` x3, `denied != resolved` x2 |
| **swarm_verified** | **1.000** | **1.000** | **0.000000** | 1.000 | 1.000 | 55.93 | 3.35 | **Không có (0 lỗi)** |

### 3. Thống kê can thiệp của Verifier và Trace minh họa
- **Số lần Verifier can thiệp (`verifier_override`):**
  - Trên tập Public: **1 lần** (tại seed 55 cho claim C-002: ticket khai khống trễ 5 ngày, DB order chỉ trễ 2 ngày; Verifier ghi đè mức bồi thường từ 20.000 VND về 0 VND và từ chối bồi thường).
  - Trên tập Đối kháng: **5 lần** (tại seed 55 cho các claim C-ADV-01, C-ADV-02, C-ADV-03, C-ADV-07, C-ADV-08: ngăn chặn hoàn toàn việc khách hàng nói dối ngày trễ, nói thiếu ngày trễ hoặc làm nhiễu số ngày trễ).
- **Trace minh họa can thiệp (`R-swarm_verified-C-002-s55.json`):**
  ```json
  {
    "kind": "verifier_override",
    "payload": {
      "mismatches": {
        "delay_days": {
          "expected": 2,
          "actual": 5
        }
      },
      "old_proposal": 20000,
      "corrected_proposal": 0,
      "reason": "structured_data_mismatch"
    }
  }
  ```

---

## Kết luận

1. **Ủng hộ giả thuyết nghiên cứu (Supported):**
   - Kết quả thực nghiệm hoàn toàn ủng hộ phát hiện của Google Research (2026): Swarm không có kiểm soát tập trung bị khuếch đại lỗi nghiêm trọng khi gặp dữ liệu đối kháng (pass^5 giảm sâu từ 0.929 xuống 0.375, phương sai tăng lên 0.0625).
   - Tầng Code Verifier đóng vai trò là một bộ lọc bảo vệ, đưa độ chính xác của Swarm về ngang bằng 100% với Workflow (Pass rate = 1.000, phương sai = 0 trên cả hai tập dữ liệu)

2. **Trả lời câu hỏi cốt lõi của Topic:**
   - *Verifier đưa swarm về gần workflow tới đâu, với cost/success bao nhiêu?*
     - Về mặt độ chính xác, Verifier đưa Swarm ngang bằng Workflow (1.000 pass rate)
     - Tuy nhiên về mặt chi phí, Swarm_verified có chi phí/thành công cao hơn Workflow rất nhiều (49.00 VND vs 27.86 VND trên public; 55.93 VND vs 30.00 VND trên adversarial). Lý do: Swarm vẫn phải chi trả chi phí token cho các bước hội thoại phi tập trung trước khi Verifier can thiệp sửa sai
   - *Nếu Verifier đã thay cả phần quyết định thì Swarm còn giữ lại giá trị gì?*
     - Trong bài toán nghiệp vụ tài chính và bồi thường có quy tắc cứng (Strict Business Rules), Swarm hầu như không giữ lại giá trị quyết định độc lập, giá trị khả dĩ duy nhất của Swarm chỉ là khả năng trích xuất thông tin phi cấu trúc từ ngữ cảnh giao tiếp tự nhiên của khách hàng. Khi đưa ra quyết định tiền tệ, quyền kiểm soát tối hậu bắt buộc phải thuộc về phần code logic chắc chắn. Nếu Verifier phải can thiệp sửa cả số tiền thì Swarm chỉ còn là một lớp vỏ tốn kém bên ngoài Workflow

3. **Điều kiện kết luận đảo ngược:**
   - Kết luận này chỉ đảo ngược khi bài toán là **Open-domain reasoning / Creative exploration** (nơi không tồn tại cơ sở dữ liệu ground truth để Verifier đối chiếu), hoặc khi việc giao tiếp đa chiều giữa các agent đem lại tri thức mới mà code logic không thể diễn đạt trước bằng luật rõ ràng

---

## Giới hạn

1. **Mô hình giả lập (MockLLM):** Hành vi ảo giác của Swarm được mô phỏng xác định bằng luật lập trình (`seed % 5 == 0`), chưa phản ánh hết tính bất định phức tạp của các mô hình LLM thương mại lớn trong thực tế
2. **Kích thước tập kiểm thử:** Bộ kiểm thử gồm 14 claim public và 8 claim đối kháng tuy đủ để đo lường định lượng và chứng minh sai số, nhưng chưa bao quát toàn bộ các vector tấn công prompt injection hoặc ngôn ngữ tự nhiên phức tạp
3. **Mô phỏng độ trễ (Latency):** Do chạy offline với MockLLM, thời gian phản hồi giữa các shape chưa thể hiện được sự khác biệt về network roundtrip hay chi phí tính toán thực tế của LLM
