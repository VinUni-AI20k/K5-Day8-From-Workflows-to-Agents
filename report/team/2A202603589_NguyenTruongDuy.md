# Bao cao ca nhan - Nguyen Truong Duy

## 1. Thong tin thanh vien

- Ho ten: Nguyen Truong Duy
- MSSV: 2A202603589
- Email: ntduy279@gmail.com
- GitHub: https://github.com/Dizo279

## 2. Phan viec phu trach

Phu trach Shape B - single ReAct agent:

- Hoan thien `src/lab8/shapes/single.py` theo contract `run_claim`.
- Bao dam agent chi dung read-only tools; quote tien do `compute_compensation` tinh va host la noi duy nhat goi `issue_refund`.
- Truyen `crash_at` xuong durability de kiem tra retry/idempotency.
- Them test contract tap trung cho single trong `src/tests/test_single_shape.py`.
- Cap nhat ADR/research card va ghi nhan so lieu benchmark cho quyet dinh kien truc.

## 3. Dong gop cu the

Commit chinh: `67a3a24` - `feat: update single ReAct shape implementation and add focused contract tests`.

Cac dong gop ky thuat:

- Xay dung vong ReAct gioi han 8 buoc, lan luot doc claim, order, policy, refund history roi goi `compute_compensation`.
- Khong dua ticket/raw claim/order vao prompt hoac trace; trace chi ghi cac summary da allowlist.
- Khong de model tu chon so tien hoac goi tool ghi tien; truyen full quote cho host de host kiem tra approval, idempotency va cap theo order.
- Xu ly cac ket qua `resolved`, `denied`, `needs_info`, `escalated` va `failed` bang `lab8.shapes.common.finish()`.
- Test ba nhom rui ro chinh: khong tin ticket thay cho order (`C-002`, seed 55), truyen full quote de host ap cap (`C-014`) va crash/retry khong tao refund kep (`C-012`).

## 4. Bang chung

- Commit: `67a3a24e5df0766f7b4169da318c030637efb865`.
- Test: `src/tests/test_single_shape.py`.
- Benchmark: `src/reports/benchmark.json`, cac run single co dang `R-single-C-001-s11`.
- Single dat `70/70` trial hop le tren 14 claim x 5 seed; `pass_rate = 1.000`, `pass^5 = 1.000`, seed min-max `1.000-1.000`, variance `0.000000`.
- Chi phi mo phong: `47.852857 VND/success` (xap xi `47.85`), trung binh `8.5` buoc, `5.5` model calls va `4.5` tool calls moi trial.
- Crash suite chung: `20/20` trong `src/reports/crash.json`; test single rieng chung minh crash sau effect truoc checkpoint retry van chi co mot dong ledger.
- Run tieu bieu: `R-single-C-002-s55` bi deny dung vi quote dua tren order la 0, khong tin so ngay trong ticket; `R-single-C-014-s11` co proposal `150000` nhung effect thuc te `120000` do host ap cap theo order.

## 5. Cong cu AI da dung

Da dung Codex/AI de doc cau truc repo, ra contract, goi y cac truong hop test va ho tro dien giai so lieu. AI khong duoc dung de sinh hoac sua benchmark, run id, commit hash hay ket qua danh gia.

Tu kiem tra bang cach doi chieu code voi `docs/contracts.md`, `docs/business_rules.md`, doc diff cua commit, kiem tra test source va doi chieu so lieu trong `src/reports/benchmark.json`/`crash.json`. Cac quyet dinh ve quote, approval, cap, idempotency va du lieu trace deu duoc kiem chung tu code host va test contract.

## 6. Tu danh gia

Phan single dat muc tieu public benchmark va giu dung ranh gioi tin cay: model dieu phoi cac buoc doc, con code/host quyet dinh tien va ghi ledger. Diem manh la flow xac dinh, de kiem thu, khong phu thuoc ticket text va an toan khi retry/crash.

Han che la single ton chi phi mo phong cao hon workflow (`47.85` so voi `27.86` VND/success) vi co them model calls, trong khi bo public chua cho thay loi ich pass-rate. Benchmark dung MockLLM va 14 claim synthetic nen chua du de ket luan cho production; hidden benchmark va latency thuc te can duoc danh gia them.
