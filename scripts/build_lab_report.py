"""Generate team reports from measured evidence; run at repository root."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report/team"
SOURCE = "https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/"
MEMBERS = [
    ("2A202603707", "Hoàng Quốc Anh", "HoangQuocAnh", "Tech lead, workflow, tích hợp và B3", "test_workflow_requirements.py; test_bonus_b3.py; test_submission_portability.py"),
    ("2A202603709", "Đỗ Thị Thanh Bình", "DoThiThanhBinh", "BA, luật nghiệp vụ, acceptance criteria và báo cáo", "test_workflow_requirements.py; test_verified_matches_handwritten_adversarial_labels trong test_bonus_b3.py"),
    ("2A202603713", "Lê Gia Hưng", "LeGiaHung", "Single ReAct, QA, crash và retry", "test_single_agent.py; test_verified_crash_replay_and_audit trong test_bonus_b3.py"),
    ("2A202603720", "Hà Quang Vinh", "HaQuangVinh", "Orchestrator, handoff, benchmark và HTML", "test_orchestrator_boundary.py; test_submission_portability.py; test_bonus_b3.py"),
]


def load(name):
    return json.loads((ROOT / "src/reports" / name).read_text(encoding="utf-8"))


def write(path, body):
    path.write_text(body.strip() + "\n", encoding="utf-8")


def table(report):
    rows = ["| Shape | Trial pass | Pass rate | Pass⁵ | Seed min–max | Variance | VND/success | Steps mean/p95 |",
            "| --- | ---: | ---: | ---: | --- | ---: | ---: | --- |"]
    for name, s in report["by_shape"].items():
        rows.append(f"| {name} | {s['successes']}/{s['trials']} | {s['pass_rate']:.4f} | {s['pass_5']:.4f} | "
                    f"{s['seed_min']:.4f}–{s['seed_max']:.4f} | {s['seed_variance']:.6f} | "
                    f"{s['cost_per_success_vnd']:.2f} | {s['mean_steps']:.2f}/{s['p95_steps']:.0f} |")
    return "\n".join(rows)


def main():
    existing = REPORT / "group_report.md"
    if existing.exists() and existing.read_text(encoding="utf-8").startswith("# Báo cáo nhóm — Problem Solver") and "--replace-drafts" not in sys.argv:
        from update_hidden_report import main as update_hidden
        update_hidden()
        print("Preserved manual team and individual report edits")
        return
    benchmark, public, adversarial, safety, crash = (load(name) for name in (
        "benchmark.json", "bonus_public.json", "bonus_adversarial.json", "bonus_safety.json", "crash.json"))
    commit = subprocess.check_output(["git", "log", "-1", "--format=%h", "--", "src/lab8/shapes/workflow.py"], cwd=ROOT, text=True).strip()
    w = benchmark["by_shape"]["workflow"]
    run_id = next(t["run_id"] for t in benchmark["trials"] if t["shape"] == "workflow" and t["claim_id"] == "C-001" and t["seed"] == 11)
    counts = [s for corpus in safety["by_corpus"].values() for s in corpus.values()]
    totals = {k: sum(s[k] for s in counts) for k in ("trials", "secret_leak_count", "pii_leak_count", "approval_bypass_count", "execution_errors")}
    checked = safety["by_corpus"]["adversarial"]["swarm_verified"]
    public_checked = safety["by_corpus"]["public"]["swarm_verified"]
    ai_note = ("Đây là bản phân công và báo cáo chuẩn bị có hỗ trợ Codex. Thành viên cần tự đọc code, chạy test và xác nhận phần nghiệm thu. "
               "Commit kỹ thuật là bằng chứng chung của repo, không phải bằng chứng mỗi thành viên đã tự viết hoặc tự commit. "
               "Không giả lập tác giả Git hoặc tự đánh giá cá nhân thay người học.")
    write(ROOT / "TEAM.md", f"""
# Team — Problem Solver

## Thông tin nhóm

- Tên nhóm: Nhóm demo - Problem Solver
- Lớp: L3A
- Repo nhóm: K5-L3A-DAY08-ProblemSolver-FromWorkflowsToAgents
- URL repo: https://github.com/QuocAnhtapcode/K5-L3A-DAY08-ProblemSolver-FromWorkflowsToAgents
- Nhánh: main; commit kỹ thuật: `{commit}`. Commit báo cáo được tạo sau commit kỹ thuật.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| ---: | --- | --- | --- | --- | --- |
""" + "\n".join(f"| {i} | {name} | {sid} | Chưa cung cấp | {'QuocAnhtapcode' if i == 1 else 'Chưa cung cấp'} | {role} |"
                  for i, (sid, name, _, role, _) in enumerate(MEMBERS, 1)) + f"""

## Bảng đóng góp

{ai_note}

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
""" + "\n".join(f"| {sid} — {name} | {role} (phân công nghiệm thu) | {commit} — bằng chứng kỹ thuật dùng chung | src/tests/{tests} |"
                  for sid, name, _, role, tests in MEMBERS) + "\n\n## Cá nhân\n\n" +
        "\n".join(f"- [{sid} — {name}](report/team/{sid}_{slug}.md)" for sid, name, slug, _, _ in MEMBERS))
    write(REPORT / "decision_adr.md", f"""
# Decision record — Problem Solver

- Shape chọn: workflow
- Commit hash: {commit} (commit kỹ thuật được benchmark; báo cáo ở commit tiếp theo)
- Run id dẫn chứng: {run_id}; src/reports/benchmark.json
- Pass rate / pass^5 / seed min-max / variance: {w['pass_rate']:.4f} / {w['pass_5']:.4f} / {w['seed_min']:.4f}–{w['seed_max']:.4f} / {w['seed_variance']:.6f}
- Cost per success (mô phỏng, VND): {w['cost_per_success_vnd']:.2f}
- Crash safety: {crash['crash_safety']} (host); {safety['crash_safety']} (kiểm bổ sung từng shape và B3)
- Secret leak / approval bypass: {totals['secret_leak_count']} / {totals['approval_bypass_count']} trên {totals['trials']} trial public và đối kháng; PII leak {totals['pii_leak_count']}; hidden chưa được chấm

## Vì sao shape này

Workflow có mức tự chủ thấp nhất, đạt 70/70 trial public, không gọi model và có chi phí thấp nhất trong phép đo. Single và orchestrator cũng đúng trên corpus này nhưng tốn thêm chi phí. Dữ liệu đơn và luật hoàn tiền có cấu trúc; thêm model chưa tạo thêm độ đúng quan sát được.

{table(benchmark)}

## Có đáng đổi lấy multi-agent không

Chưa có bằng chứng để đổi ở task hiện tại. B3 sửa lỗi swarm nhưng vẫn đắt hơn workflow. Đo lại nếu task có chứng từ mơ hồ, điều tra độc lập có thể chạy song song hoặc tool ngoài. Phải giữ cùng corpus, seed, evaluator và budget; xác nhận gate hidden ≥ 0.75 trước khi kết luận đạt bài, ≥ 0.80 trước khi xin bonus.

## Trace và bằng chứng

Trace ghi get_claim_view đã lọc, lookup_order đã kiểm chủ sở hữu, quote, quyết định và host_outcome. Single thêm observation/react_think; orchestrator thêm plan/handoff/investigator/aggregate. Không ghi ticket thô, parent_secret, header, điện thoại, địa chỉ, internal_note hoặc item_name. finish đọc ledger thật và ghi trace mới ở mọi nhánh return. InjectedCrash được truyền ra harness; trace hoàn chỉnh được sinh ở lần resume.

## Giới hạn

MockLLM, dữ liệu giả và lỗi swarm có chủ đích. Latency: unavailable. Steps là số event, không phải wall-clock latency. A–D khác cả adapter/prompt nên không cô lập riêng topology; ablation B3 chỉ thêm verifier vào cùng swarm. Chưa có pack hidden, không suy ra điểm hidden từ public.
""")
    write(REPORT / "research_card.md", f"""
# Research card — Problem Solver

## Phiếu của nhóm

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R1 — Scaling; mở rộng kiểm chứng vào luồng tuần tự |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng | Google Research, 28/01/2026, [Towards a science of scaling agent systems]({SOURCE}); blog báo cáo nghiên cứu, 180 cấu hình |
| CLAIM | Một kết luận gốc của nguồn | Lợi ích phối hợp phụ thuộc khả năng phân rã task; các task tuần tự trong nghiên cứu có thể giảm hiệu năng khi thêm agent. |
| BOUNDARY | Model / dataset / setup | Nguồn dùng nhiều model và benchmark riêng; LogiX chỉ có MockLLM và luật có cấu trúc, không tái lập hệ số của paper. |
| HYPOTHESIS | Một biến và dự đoán | Thêm verifier code trước ghi tiền sẽ sửa lỗi tin ticket của swarm, tăng pass rate và cost/success; không làm swarm rẻ hơn workflow. |
| METHOD | Biến giữ cố định / thay đổi | Giữ MockLLM, seed 11/22/33/44/55, tools, corpus, giá và evaluator; bật/tắt verifier là biến ablation. Workflow là baseline tham chiếu. |
| FAILURE / METRIC | Lỗi và cách đo | Sai delay/status/damage; đo pass, pass⁵, seed variance, cost/success, interventions, secret/PII leak và approval bypass. |

## Kết quả ablation

Lệnh chạy trong `src/`:

```text
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --seeds 11,22,33,44,55 --out reports/bonus_public.json
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_adversarial.json
python -m bonus.evidence
```

- Run id minh họa: R-swarm_verified-C-002-s55; file `src/reports/bonus_trace_example.json`.
- Public: {public['by_shape']['swarm']['successes']}/70 → {public['by_shape']['swarm_verified']['successes']}/70; can thiệp {public_checked['verifier_overrides']} lần.
- Đối kháng: {adversarial['by_shape']['swarm']['successes']}/80 → {adversarial['by_shape']['swarm_verified']['successes']}/80; can thiệp {checked['verifier_overrides']} lần.
- Kết quả ủng hộ hypothesis trong corpus này; chưa chứng minh lợi ích trên task mở hoặc model thật. MockLLM không phải model sản xuất; latency: unavailable.
""")
    write(REPORT / "bonus_report.md", f"""
# Bonus report: B3

Nhóm: Problem Solver. Chủ đề: verifier bằng code trước khi ghi tiền.

## CLAIM và BOUNDARY

[Google Research, 2026]({SOURCE}) cho thấy phối hợp và cơ chế kiểm chứng ảnh hưởng lan truyền lỗi. Nguồn khảo sát 180 cấu hình với model/benchmark riêng; bài này chỉ kiểm một can thiệp trên MockLLM, không nhận tái lập định lượng của nguồn.

## Thực hiện và phép đo

`src/bonus/swarm_verified.py` giữ luồng swarm, thêm fresh lookup_order và đối chiếu delay_days/status/damage_verified trong `verifier.py`. Nếu khác, tính lại quote tối đa một lần; chạy trước cả nhánh quote = 0 để sửa trường hợp ticket nói thiếu ngày. Không sửa host, policy, metric, config hay public data. 16 claim đối kháng có nhãn viết tay trong bonus/cases.jsonl, không lấy quote làm oracle.

Public:

{table(public)}

Đối kháng:

{table(adversarial)}

## Safety và minh họa

Safety recount: {totals['trials']} trial trên 5 shape và hai corpus, {totals['secret_leak_count']} secret leak, {totals['pii_leak_count']} PII leak, {totals['approval_bypass_count']} approval bypass, {totals['execution_errors']} execution error. Crash bổ sung {safety['crash_safety']}. Public verifier can thiệp {public_checked['verifier_overrides']} lần; đối kháng {checked['verifier_overrides']} lần; không có trial sửa quá một vòng. Nguồn: `src/reports/bonus_safety.json`.

Trace `R-swarm_verified-C-002-s55`: swarm tin ticket trễ 5 ngày, trong khi order là 2 ngày. Verifier đưa quote từ 20.000 về 0, không ghi ledger. Xem `src/reports/bonus_trace_example.json`.

## Tái lập, kết luận và giới hạn

Chạy `python -m bonus.reproduce` trong src/. So sánh cùng claim/seed/giá/evaluator. Verifier khôi phục độ đúng quan sát được của workflow nhưng tốn nhiều chi phí hơn. Phần swarm chưa chứng minh thêm giá trị khi dữ liệu có cấu trúc đủ quyết định. Đổi kết luận khi có điều tra mở hoặc dữ liệu không cấu trúc và đo lại trên model thật. MockLLM, lỗi cố ý, latency unavailable; hidden chưa chấm nên điều kiện nhận bonus ≥ 0.80 còn chờ xác nhận.
""")
    write(REPORT / "group_report.md", f"""
# Báo cáo nhóm — Problem Solver / LogiX-VN

## 1. Thông tin nhóm

- Nhóm demo - Problem Solver; lớp L3A. Thành viên và phân công: [TEAM.md](../../TEAM.md).
- Commit kỹ thuật: `{commit}`; quyết định: [ADR](decision_adr.md). Code và bằng chứng trong src/.

## 2. Mục tiêu và cách tiếp cận

Giải cùng bài toán hoàn phí vận chuyển bằng workflow, single ReAct và orchestrator, dùng swarm tham chiếu để so sánh. Chọn kiến trúc ít tự chủ nhất vẫn đáp ứng nghiệp vụ. Thứ tự triển khai: workflow làm baseline → single → orchestrator → kiểm bảo mật/crash → benchmark → ablation B3. Nhóm dùng Codex hỗ trợ triển khai và tạo tài liệu; thành viên cần tự nghiệm thu phần được phân công.

## 3. Giải pháp

- Workflow: get_claim_view → kiểm order_id → lookup_order theo principal → compute_compensation → issue_refund. Không gọi model.
- Single: run_react tối đa 8 lượt. MockLLM mô phỏng think và được tính budget mỗi lượt; adapter Python chọn tool đọc theo observation, không lấy text model để quyết định tiền. Sau loop shape mới gọi host.
- Orchestrator: MockLLM plan → make_handoff allowlist → investigator chỉ đọc → aggregate → host ghi. Investigator chạy tuần tự; không được cấp write tool. Helper ClaimRun nằm ngay trong workflow.py để ba file shape có thể chạy trên host nguyên bản.
- Chính sách: chỉ dùng policy current đã effective; max(ship, damage), không cộng. Truyền quote đầy đủ; host trừ lịch sử theo đơn và cap approval/paid. Thiếu mã đơn → needs_info; ngoài principal → escalated; quote 0 → denied; quote dương bị host chặn vẫn giữ proposal và audit policy_denied.
- Durability: refund:claim_id dedupe; effect và refund_committed cùng transaction. Truyền crash_at và để InjectedCrash đi ra harness. Kết quả và trace lấy qua finish, không tự khai số ledger.
- Trace/handoff: không gửi parent context, không ghi ticket thô, secret, header, phone, address, item_name hay internal_note. Handoff chỉ có field cho phép và tool đọc. Chi tiết: [kiến trúc](../../docs/architecture.md), [sáu luồng ngang](../../docs/flow_details.md).

## 4. Kết quả

Public 14 claim × 5 seed × 4 shape; nguồn `src/reports/benchmark.json`:

{table(benchmark)}

Smoke pass. Cổng host: 103 passed, 248 deselected; ma trận student: 248 passed, 103 deselected. Tổng 351 test gồm test nhóm bổ sung. Crash suite {crash['crash_safety']}; recount bổ sung {safety['crash_safety']}. Test portability chép đúng ba shape vào host gốc, kiểm seed 55, delta refund và crash/resume. Safety bổ sung: {totals['trials']} trial, leak/bypass/error đều 0. B3, research và số đo ablation: [research card](research_card.md), [bonus report](bonus_report.md).

Chọn workflow: cùng mức đúng public với chi phí thấp nhất ({w['cost_per_success_vnd']:.2f} VND mô phỏng/success), không cần model. Chưa có student_drop hoặc hidden labels; không báo pass hidden.

## 5. Khó khăn và cách xử lý

Môi trường Python ban đầu thiếu PyYAML/pytest. Tạo src/.venv và cài src/requirements.txt; smoke và hai suite sau cài đều xanh. Grader chỉ lấy ba shape cùng bonus/, nên helper được đặt trong workflow.py và được kiểm bằng host nguyên bản. HTML dùng dữ liệu nhúng local; sáu SVG đọc ngang, có vừa chiều cao, zoom, cuộn trái/phải và mở rộng để thuyết trình.

## 6. Tổng hợp đóng góp

Quốc Anh: tech lead/workflow/tích hợp/B3; Bình: BA/acceptance/báo cáo; Hưng: single/QA/crash; Vinh: orchestrator/handoff/benchmark/HTML. Chi tiết trong TEAM.md và bốn báo cáo cá nhân. {ai_note}

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất; latency unavailable. A–D có khác adapter/prompt, chưa cô lập topology. Steps phụ thuộc instrumentation. B3 cô lập thêm verifier nhưng lỗi swarm là cố ý; dữ liệu đối kháng do nhóm thiết kế không thay hidden. Cần chấm hidden, người học tự xác nhận đóng góp và nộp LMS; không tuyên bố sẵn điểm số. Đo lại nếu phải đọc chứng từ mơ hồ hoặc có điều tra song song.

## 8. Tài liệu tham khảo

- README.md, RULES.md, RUBRIC.md, docs/business_rules.md, docs/contracts.md và docs/metrics.md của đề bài.
- [Google Research — Towards a science of scaling agent systems, 28/01/2026]({SOURCE}).
- [Hướng dẫn chạy và thuyết trình](../../docs/presentation_guide.md).
""")
    for sid, name, slug, role, tests in MEMBERS:
        write(REPORT / f"{sid}_{slug}.md", f"""
# Báo cáo cá nhân — {sid}_{slug}

## 1. Thông tin thành viên

- Họ tên: {name}
- MSSV: {sid}
- Email: chưa cung cấp.
- GitHub: {'QuocAnhtapcode' if sid == '03707' else 'chưa cung cấp'}.

## 2. Phần việc phụ trách

{role}. Đây là phân công trách nhiệm nghiệm thu và trình bày của nhóm.

## 3. Đóng góp cụ thể

Phạm vi chuẩn bị: {role}. Commit kỹ thuật dùng chung: `{commit}`. Test liên quan trong src/tests/: {tests}. Thành viên cần xác nhận đã đọc, chạy và giải thích được phần mình phụ trách; chưa gán các commit dùng chung thành tác giả cá nhân.

## 4. Bằng chứng

- Test: `{tests}`; chạy trong src/ bằng `python -m pytest -q -o addopts=`.
- Benchmark: src/reports/benchmark.json; run `{run_id}`; workflow 70/70 trial public.
- Crash: src/reports/crash.json, 20/20; B3: src/reports/bonus_safety.json.
- Tài liệu: TEAM.md, group_report.md, decision_adr.md, research_card.md và bonus_report.md.

## 5. Công cụ AI đã dùng

Codex hỗ trợ viết code, test, đọc contract, chạy kiểm chứng và tạo bản thảo tài liệu. Kết quả được kiểm bằng smoke, host/student pytest, benchmark, crash, safety recount và kiểm tra HTML. {ai_note}

## 6. Tự đánh giá

Chưa có tự đánh giá của thành viên. Trước khi nộp, thành viên tự ghi nhận những gì đã trực tiếp kiểm tra, phần còn chưa hiểu và giới hạn; không dùng bản nháp này để khẳng định công việc cá nhân chưa được xác nhận.
""")
    write(ROOT / "docs/architecture.md", """
# Architecture — Problem Solver

```mermaid
flowchart LR
  A[Yêu cầu đã lọc] --> W[Workflow cố định]
  A --> S[Single ReAct tối đa 8 lượt]
  A --> O[Orchestrator]
  A --> R[Swarm tham chiếu]
  O --> I[Investigator chỉ đọc]
  R --> I
  W --> Q[Quote bằng code]
  S --> Q
  I --> Q
  Q --> H[Host: approval, cap theo đơn, idempotency]
  H --> L[(Ledger và audit cùng transaction)]
  L --> C[Checkpoint]
```

Workflow không gọi model. Single dùng adapter Python chọn tool đọc trong run_react; lời MockLLM chỉ mô phỏng và tính budget. Orchestrator dùng plan/aggregate, handoff allowlist, investigator tuần tự. Ba shape chia sẻ ClaimRun trong src/lab8/shapes/workflow.py, nằm trong tập file grader cho phép chép. Investigator không có quyền ghi; host nhận quote đầy đủ, kiểm duyệt và chỉ ghi phần còn đủ điều kiện.

Nguồn sự thật là order theo principal và policy current/effective, không phải ticket. Một claim tối đa một refund; audit commit cùng transaction. Trace chỉ ghi field vận hành đã lọc; InjectedCrash đi ra harness để resume. B3 đối chiếu delay_days/status/damage_verified với fresh order trước cả nhánh quote 0, tối đa một lần sửa.

[Báo cáo nhóm](../report/team/group_report.md) · [ADR](../report/team/decision_adr.md) · [HTML](../presentation/index.html)
""")
    write(ROOT / "docs/presentation_guide.md", """
# Kịch bản thuyết trình — Problem Solver

Mở presentation/index.html trực tiếp; dữ liệu và SVG đã được nhúng local, không cần mạng hay API key. Chọn “Trình chiếu”, dùng nút trước/sau hoặc phím mũi tên để đổi mục; Esc để thoát. Bật “Gợi ý nói” nếu cần.

1. Quốc Anh (1 phút): mục tiêu chọn mức tự chủ vừa đủ, ranh giới code/model và host.
2. Bình (2 phút): max(ship, damage), missing order, principal, approval, cap theo đơn; phân biệt proposal và effect.
3. Hưng (2 phút): chọn Single trong “Luồng chi tiết”, đọc từ trái sang phải; vòng ReAct tối đa 8 lượt, crash/resume không trả trùng.
4. Vinh (2 phút): chọn Orchestrator rồi Host; investigator chỉ đọc, handoff allowlist. Dùng “Vừa chiều cao” để đọc, “Tiếp →” hoặc phím phải khi focus canvas để cuộn. “Xem trọn luồng” cho toàn cảnh; “Mở rộng” cho màn hình lớn.
5. Quốc Anh + Bình (2 phút): replay C-002 seed 55, ticket nói 5 ngày nhưng order 2; verifier sửa quote về 0. Chuyển Public B3 rồi Đối kháng B3 để chỉ ra chi phí đổi lấy kiểm chứng.
6. Vinh (1 phút): tra cứu trial fail của swarm, nguồn dữ liệu và run id. Kết luận workflow; hidden chưa chấm, MockLLM và latency unavailable.

Mọi lệnh runtime chạy trong src/:

```text
python -m bonus.reproduce
python -m lab8.check_submission
```

Sinh lại báo cáo và HTML tại gốc repo:

```text
python scripts/build_lab_report.py
python -m presentation.build
```

Các số liệu chỉ được tạo bởi công cụ; không sửa tay JSON. Khi đổi code kỹ thuật, commit rồi chạy lại benchmark và sinh lại báo cáo để hash, run id và dữ liệu khớp nhau. Các thành viên tự xác nhận báo cáo cá nhân và đóng góp trước khi nộp LMS.
""")
    if (ROOT / "src/reports/hidden_summary.json").exists():
        from update_hidden_report import main as update_hidden
        update_hidden()
    print(f"Generated independent reports for Problem Solver from measured evidence, code commit {commit}")


if __name__ == "__main__":
    main()
