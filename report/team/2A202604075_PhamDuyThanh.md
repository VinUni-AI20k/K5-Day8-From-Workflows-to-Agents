# Báo cáo cá nhân — 2A202604075_PhamDuyThanh

## 1. Thông tin thành viên

- Họ tên: Phạm Duy Thành
- MSSV: 2A202604075
- Email: thanhteyv2@gmail.com
- GitHub: thanhtey1234
- Nhánh làm việc: `thanh-ledger-evaluation`, xuất phát từ `main` commit `20b2fba`.

## 2. Phần việc phụ trách

Ledger/crash và evaluation: test phục hồi, baseline benchmark, crash report, research card, sau tích hợp sẽ hoàn thiện ADR. Báo cáo này chỉ ghi phần đã thực hiện đến hết giai đoạn 2 ngày 2026-11-17. Single và orchestrator còn stub; chưa chốt kiến trúc, chưa đánh giá hidden, chưa có commit chốt bài.

## 3. Đóng góp cụ thể

**Commit chính:** chưa tạo. `20b2fba` là mốc main ban đầu, không khai là commit đóng góp cá nhân. Điền hash thật sau khi commit.

- `src/tests/test_team_crash_recovery.py`: 8 test. Sáu kịch bản là C-001 và C-014 × ba crash point. Kiểm ledger/audit/checkpoint ngay sau crash, rồi mở lại kết nối, resume và retry ba lần. Hai kịch bản approval kiểm retry khi thiếu approval hoặc dùng approval của claim khác.
- `src/bonus/research_draft_ablation.py`: wrapper gọi lại nguyên workflow, chỉ bỏ draft và đổi tên variant để tách trace. Patch khôi phục khi kết thúc hoặc có exception. Không sửa host hay workflow. Chỉ chạy tuần tự trong một process.
- `src/tests/test_research_draft_ablation.py`: 72 test; 70 cặp claim/seed đối chiếu nghiệp vụ, ledger, audit, trace và accounting; thêm kiểm tra phục hồi sau crash và từ chối bỏ lời gọi không phải draft.
- Tạo `benchmark.json`, `crash.json`, `research_ablation.json` bằng công cụ; điền research card R4, phần kết quả ban đầu trong báo cáo nhóm và dòng đóng góp trong TEAM.

## 4. Bằng chứng

Mọi lệnh dưới chạy trong `src/`, dùng Python 3.11.9 của `.venv`.

```powershell
./.venv/Scripts/python.exe -m pytest -q tests/test_team_crash_recovery.py tests/test_research_draft_ablation.py
./.venv/Scripts/python.exe -m pytest -q
./.venv/Scripts/python.exe -m pytest -q -m student -o addopts= -k 'workflow or swarm'
./.venv/Scripts/python.exe -m lab8.crash_test --count 20 --out reports/crash.json
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
./.venv/Scripts/python.exe -m lab8.benchmark --shapes workflow,workflow_no_draft --extra-shape workflow_no_draft=bonus.research_draft_ablation:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/research_ablation.json
```

Kết quả được chạy và kiểm tra trong phiên Codex:

- Test mới: **80 passed**; test mặc định: **156 passed**; student workflow/swarm: **124 passed**.
- Crash suite: **20/20**. Suite có sẵn chủ yếu đo host/swarm; 8 test mới kiểm thêm workflow, không suy ra single/orchestrator đã an toàn.
- Baseline 280 trial: workflow 70/70, swarm 69/70; single và orchestrator 0/70 vì chưa triển khai. Không dùng stub để kết luận kiến trúc kém hơn.
- Ablation 140 trial: cả hai variant 70/70; cost/success 28.862857 và 27.857143 VND mô phỏng; giảm tổng 70.40 VND, khoảng 3.48%. Run id ví dụ: `R-workflow-C-001-s11`, `R-workflow_no_draft-C-001-s11`.
- Report JSON được công cụ sinh, không sửa tay. Trace/database là artifact local và không commit.
- `./.venv/Scripts/python.exe -m lab8.check_submission`: **9 FAIL, 1 WARN**. Hai shape chưa triển khai và bảy field ADR còn trống là phần chờ tích hợp; WARN do chưa commit. Benchmark, crash report và research card qua kiểm tra cấu trúc.

## 5. Công cụ AI đã dùng

Codex hỗ trợ đọc repo, lập kế hoạch, viết test/helper, chạy lệnh, tổng hợp kết quả và soạn tài liệu. Firecrawl hỗ trợ xác minh nguồn nghiên cứu. Phần thực hiện này được trợ lý AI tạo và kiểm tra bằng các lệnh ở trên; không khai là phần thành viên đã tự viết hoặc tự chạy thủ công.

Trước khi nộp, thành viên cần tự đọc diff và chạy lại test; giải thích được ledger khác checkpoint thế nào, vì sao truyền quote đầy đủ, cách tránh approval bypass và vì sao ablation không chứng minh workflow luôn tốt hơn multi-agent. Ghi thêm kết quả tự kiểm tra sau khi thực hiện.

## 6. Tự đánh giá

Chưa điền thay nhận xét cá nhân của thành viên. Giai đoạn 1–2 có test và số liệu tái tạo được; phần còn lại phụ thuộc hai shape được merge. Thành viên bổ sung điều đã hiểu, khó khăn thực tế và phần cần cải thiện sau khi tự kiểm tra.

Giới hạn kỹ thuật: MockLLM, chi phí mô phỏng, latency `unavailable`; không đánh giá chất lượng văn bản khách hàng vì workflow hiện không đưa kết quả draft vào RunResult. Chưa có kết quả hidden. Thí nghiệm chỉ là research card bắt buộc, không phải bonus.
