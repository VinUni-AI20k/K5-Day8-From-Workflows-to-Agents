"use strict";

const SHAPES = {
  workflow: {name:"Workflow", letter:"A", caption:"Các bước Python cố định", color:"#356be8", icon:"grid", pipeline:["Đọc claim", "Tra đơn theo quyền", "Tính quote bằng code", "Host kiểm duyệt & ghi"]},
  single: {name:"Single agent", letter:"B", caption:"Một vòng ReAct, tối đa 8 bước", color:"#8b6ac9", icon:"bolt", pipeline:["Đọc claim", "ReAct chọn tool đọc", "Tính quote bằng code", "Host kiểm duyệt & ghi"]},
  orchestrator: {name:"Orchestrator", letter:"C", caption:"Điều phối + investigator chỉ đọc", color:"#bb8a41", icon:"layers", pipeline:["Đọc claim", "Handoff đã lọc", "Investigator chỉ đọc", "Host kiểm duyệt & ghi"]},
  swarm: {name:"Swarm gốc", letter:"D", caption:"Peer / parse / investigator", color:"#7c92a9", icon:"layers", pipeline:["Peer & parse ticket", "Investigator đọc dữ liệu", "Swarm đề xuất quote", "Host kiểm duyệt & ghi"]},
  swarm_verified: {name:"Swarm + verifier", letter:"B3", caption:"Đối chiếu nguồn trước khi ghi", color:"#198466", icon:"shield", pipeline:["Giữ luồng swarm", "Đọc lại đơn theo quyền", "Verifier sửa tối đa 1 lần", "Host kiểm duyệt & ghi"]},
};
const STATUS = {resolved:"Đã giải quyết", denied:"Từ chối hoàn tiền", needs_info:"Cần bổ sung thông tin", escalated:"Chuyển xử lý", failed:"Không hoàn tất", interrupted:"Đã crash có chủ đích"};
const REASONS = {
  no_entitlement:"Không đủ điều kiện theo chính sách", entitled:"Đủ điều kiện hoàn tiền",
  unknown_claim:"Không tìm thấy claim", missing_order_id:"Thiếu mã đơn hàng",
  outside_principal_scope:"Đơn không thuộc người yêu cầu", not_found:"Không tìm thấy đơn hàng",
  missing_approval:"Không có approval hợp lệ", approval_claim_mismatch:"Approval thuộc claim khác",
  approval_expired:"Approval hết hạn", approval_revoked:"Approval đã thu hồi",
  order_already_refunded:"Đơn đã được hoàn đủ", amount_conflict:"Số tiền khác lần đã commit",
  idempotent_replay:"Retry: dùng lại refund đã ghi", committed:"Đã ghi refund thành công",
  ok:"Đã xác minh", step_cap:"Vòng ReAct chạm giới hạn bước",
};
const PHASE = {first:"Lượt chạy đầu", retry:"Gọi lại / retry", resume:"Tiếp tục / resume", crashed:"Crash đã xảy ra", crash_requested:"Không đi tới bước ghi"};
const FIELD_NAMES = {delay_days:"Ngày trễ", status:"Trạng thái đơn", damage_verified:"Hỏng đã xác minh", shipping_fee_vnd:"Phí vận chuyển", paid_vnd:"Tiền đã thanh toán"};
const state = {
  page:["main","bonus","evidence"].includes(location.hash.slice(1)) ? location.hash.slice(1) : "main",
  catalog:null, reports:{}, busy:false, evidence:"main", traceStep:Infinity, timer:null,
  main:{dataset:"public", claim:"C-001", seed:11, mode:"fresh", shape:"all", crash:"after_effect_before_checkpoint", response:null, focus:"workflow"},
  bonus:{dataset:"public", claim:"C-002", seed:55, mode:"fresh", shape:"all", crash:"after_effect_before_checkpoint", response:null, focus:"swarm_verified"},
};
const $ = (selector) => document.querySelector(selector);
const esc = (value) => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const icon = (name) => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
const fmt = (value, digits=0) => Number.isFinite(Number(value)) && value !== null ? new Intl.NumberFormat("vi-VN",{maximumFractionDigits:digits}).format(value) : "—";
const money = (value, digits=0) => `${fmt(value,digits)} ₫`;
const percent = (value) => value == null ? "—" : `${fmt(value*100,2)}%`;
const reasonText = (value) => REASONS[value] || (value?.startsWith("order_status_") ? "Trạng thái đơn không đủ điều kiện" : value || "");
const orderStatus = (value) => ({delivered:"Đã giao",delivered_late:"Đã giao trễ",cancelled:"Đã hủy",in_transit:"Đang vận chuyển"}[value] || value || "—");
const active = () => state.page === "bonus" ? state.bonus : state.main;
const currentCase = () => state.catalog.datasets[active().dataset].find(row => row.claim_id === active().claim);
const selectedShapes = () => active().shape === "all" ? (state.page === "bonus" ? ["swarm","swarm_verified","workflow"] : ["workflow","single","orchestrator","swarm"]) : [active().shape];

function notify(message) {
  const box = $("#notification"); box.textContent=message; box.classList.add("show");
  clearTimeout(notify.timer); notify.timer=setTimeout(()=>box.classList.remove("show"),5000);
}
function stat(title,value,note,type="",symbol="chart") {
  return `<div class="stat ${type}"><div class="stat-top">${title}${icon(symbol)}</div><div class="stat-value">${value}</div><div class="stat-note">${note}</div></div>`;
}
function reportStats(name) { return state.reports[name]?.by_shape || {}; }
function section(number,title,subtitle="",hint="") {
  return `<div class="section-heading"><div><h2><span class="section-number">${number}</span>${title}</h2>${subtitle?`<p>${subtitle}</p>`:""}</div>${hint?`<span class="section-hint">${hint}</span>`:""}</div>`;
}
function hero(bonus=false) {
  return `<section class="hero"><div><div class="hero-label"><span class="eyebrow">${bonus?"THÍ NGHIỆM RIÊNG · BONUS B3":"LAB 08 · KIẾN TRÚC & TỰ CHỦ"}</span>${bonus?'<span class="bonus-tag">VERIFIER</span>':'<span class="tiny-label">LIVE DEMO</span>'}</div><h1>${bonus?'Chặn lỗi <em>trước khi thành tiền.</em>':'Một yêu cầu. <em>Bốn cách giải quyết.</em>'}</h1><p>${bonus?'Giữ nguyên swarm. Thêm một bước kiểm chứng bằng code. Đo độ đúng và chi phí tăng thêm.':'Cùng một claim hoàn phí vận chuyển, so sánh workflow, single agent, orchestrator và swarm.'}</p></div><div class="hero-art" aria-hidden="true"><span class="hero-node">${icon("file")}</span><span class="hero-node center">${icon(bonus?"shield":"layers")}</span><span class="hero-node">${icon("check")}</span></div></section>`;
}
function mainPage() {
  const benchmark=state.reports.benchmark;
  const claimCount=benchmark?.controlled_variables?.claim_ids?.length;
  return `${hero()}<div class="stats-row">${stat("CLAIM PUBLIC",fmt(claimCount),"Cùng dữ liệu, cùng luật nghiệp vụ","","file")}${stat("KIẾN TRÚC",fmt(Object.keys(benchmark?.by_shape||{}).length),"Từ luồng cố định đến nhiều agent","","layers")}${stat("SEED KIỂM CHỨNG",fmt(benchmark?.controlled_variables?.seeds?.length),"11 · 22 · 33 · 44 · 55","","refresh")}${stat("CRASH SUITE",esc(state.reports.crash?.crash_safety||"—"),"Suite host & swarm tham chiếu","highlight","shield")}</div>${section("01","Chọn một tình huống", "Chạy code thật trên database tạm; mỗi kiến trúc bắt đầu từ cùng trạng thái.","Gợi ý: bắt đầu từ claim C-001")}${workspace()}${resultArea()}${traceArea()}`;
}
function bonusPage() {
  const p=reportStats("bonus_public").swarm_verified;
  const a=reportStats("bonus_adversarial").swarm_verified;
  const safety=state.reports.bonus_safety;
  const overrides=safety ? ["public","adversarial"].reduce((sum,key)=>sum+(safety.by_dataset[key]?.swarm_verified?.verifier_overrides||0),0) : null;
  return `${hero(true)}<div class="bonus-intro"><div><strong>Ticket là lời khách nói. Dữ liệu đơn mới là nguồn kiểm chứng.</strong><p>Verifier đọc lại đơn có kiểm quyền, đối chiếu 5 trường và chỉ tính lại quote tối đa một lần.</p></div>${icon("shield")}</div><div class="stats-row">${stat("PUBLIC · CÓ VERIFIER",p?`${p.successes}<small>/ ${p.trials} trial</small>`:"—","Cùng seed với swarm tham chiếu","highlight","check")}${stat("ĐỐI KHÁNG · CÓ VERIFIER",a?`${a.successes}<small>/ ${a.trials} trial</small>`:"—","12 claim do nhóm xây dựng","","shield")}${stat("LẦN VERIFIER CAN THIỆP",fmt(overrides),"Public + đối kháng; không phải số lỗi","","refresh")}${stat("CRASH BỔ SUNG",esc(safety?.crash?.swarm_verified?.crash_safety||"—"),"3 vị trí crash × 5 seed","","shield")}</div>${section("01","Cho swarm gặp dữ kiện gây nhiễu","Chọn seed 55 để quan sát điểm yếu có chủ đích của swarm tham chiếu.","B3 · giữ nguyên baseline")}${workspace()}${verifierArea()}${resultArea()}${traceArea()}`;
}
function workspace() {
  const b=state.page==="bonus", s=active(), cases=state.catalog.datasets[s.dataset], c=currentCase();
  const presets=b ? [
    ["Nói quá ngày trễ","public","C-002",55,"fresh"], ["Nói thiếu ngày trễ","bonus","B3-002",55,"fresh"],
    ["Approval sai claim","bonus","B3-009",55,"fresh"], ["Hoàn phần chênh","bonus","B3-011",55,"fresh"],
  ] : [
    ["Hoàn phí hợp lệ","public","C-001",11,"fresh"], ["Hoàn phần chênh","public","C-014",11,"fresh"],
    ["Crash & resume","public","C-012",11,"crash"], ["Ticket gây nhiễu","public","C-002",55,"fresh"],
  ];
  const selectors=b ? `<label class="field"><span>Bộ dữ liệu</span><select id="dataset-select" ${state.busy?"disabled":""}><option value="public" ${s.dataset==="public"?"selected":""}>Public · 14 claim</option><option value="bonus" ${s.dataset==="bonus"?"selected":""}>Đối kháng · 12 claim</option></select></label>` : `<label class="field"><span>Kiến trúc</span><select id="shape-select" ${state.busy?"disabled":""}><option value="all">So sánh cả 4</option>${["workflow","single","orchestrator","swarm"].map(k=>`<option value="${k}" ${s.shape===k?"selected":""}>${SHAPES[k].name}</option>`).join("")}</select></label>`;
  return `<section class="panel workspace"><div class="preset-row"><span class="preset-label">KỊCH BẢN DEMO</span>${presets.map((p,i)=>`<button class="preset ${s.claim===p[2]&&s.dataset===p[1]&&s.mode===p[4]?"selected":""}" data-preset="${i}" ${state.busy?"disabled":""}>${icon(i===2?"refresh":"file")}${p[0]}</button>`).join("")}</div><div class="control-grid"><label class="field"><span>Claim cần xử lý</span><select id="claim-select" ${state.busy?"disabled":""}>${cases.map(row=>`<option value="${row.claim_id}" ${row.claim_id===s.claim?"selected":""}>${row.claim_id} · ${esc(row.ticket.slice(0,43))}${row.ticket.length>43?"…":""}</option>`).join("")}</select></label><label class="field"><span>Seed ${icon("info")}</span><select id="seed-select" title="Cùng seed giúp lặp lại hành vi MockLLM; đổi seed để đo độ ổn định." ${state.busy?"disabled":""}>${state.catalog.seeds.map(seed=>`<option ${s.seed===seed?"selected":""}>${seed}</option>`).join("")}</select></label>${selectors}<label class="field"><span>Cách chạy</span><select id="mode-select" ${state.busy?"disabled":""}><option value="fresh" ${s.mode==="fresh"?"selected":""}>Chạy mới</option><option value="retry" ${s.mode==="retry"?"selected":""}>Gọi lại / retry</option><option value="crash" ${s.mode==="crash"?"selected":""}>Crash → resume → retry</option></select></label><button class="primary-button" id="run-button" ${state.busy?"disabled":""}>${state.busy?'<span class="spinner"></span> Đang chạy…':icon("play")+"Chạy demo"}</button></div>${s.mode==="crash"?`<label class="field crash-control"><span>Vị trí cố ý gây crash</span><select id="crash-select" ${state.busy?"disabled":""}>${[["before_effect","Trước khi ghi refund"],["after_effect_before_checkpoint","Đã ghi refund, chưa lưu checkpoint"],["after_checkpoint","Sau khi lưu checkpoint"]].map(([value,label])=>`<option value="${value}" ${s.crash===value?"selected":""}>${label}</option>`).join("")}</select></label>`:""}<div class="case-details"><div><div class="detail-label">${icon("file")}NỘI DUNG TICKET <span class="ticket-id">${c.claim_id}</span></div><p class="ticket-text">“${esc(c.ticket)}”</p><div class="case-outcome">${icon("info")}<span>Đáp án theo luật: <b>${STATUS[c.expected.status]}</b> · Quote ${money(c.expected.proposal_amount)} · Thực hoàn ${money(c.expected.refund_vnd)}</span></div></div><div><div class="detail-label">${icon("shield")}DỮ LIỆU ĐƠN CÓ KIỂM QUYỀN</div>${facts(c)}</div></div></section>`;
}
function facts(c) {
  if(!c.visible) return `<p class="ticket-text">${c.order_id?"Không tìm thấy đơn hoặc không thuộc phạm vi người yêu cầu.":"Claim chưa có mã đơn hàng."}</p><span class="badge neutral">Không hiển thị dữ liệu ngoài phạm vi</span>`;
  const mismatch=c.ticket_delay_days!=null&&c.ticket_delay_days!==c.order.delay_days;
  return `<div class="order-facts">${[
    ["Ngày trễ thực tế",`${c.order.delay_days} ngày`,mismatch], ["Phí ship",money(c.order.shipping_fee_vnd)],
    ["Trạng thái",orderStatus(c.order.status)], ["Đã thanh toán",money(c.order.paid_vnd)],
    ["Hỏng đã xác minh",c.order.damage_verified?"Có":"Không"], ["Approval đúng claim",c.expected.approval_ok?"Có":"Không"],
  ].map(([label,value,alert])=>`<div class="fact"><span>${label}</span><strong class="${alert?"alert":""}">${esc(value)}</strong></div>`).join("")}</div>${mismatch?`<div class="case-outcome">${icon("info")}<span>Ticket ghi <b>${c.ticket_delay_days} ngày</b>, dữ liệu đơn ghi <b>${c.order.delay_days} ngày</b>.</span></div>`:""}`;
}
function resultArea() {
  const s=active();
  let body=`<div class="empty-state">${icon("play")}<h3>Sẵn sàng chạy cùng một claim</h3>Chọn kịch bản và bấm “Chạy demo” để xem kết quả từ code thật.</div>`;
  if(s.response) {
    body=`<div class="result-grid">${s.response.results.map(r=>resultCard(r)).join("")}</div>`;
    const incorrect=s.response.results.filter(r=>!r.passed);
    if(incorrect.length) body+=`<div class="explanation-strip warning">${icon("info")}<span>${incorrect.some(r=>r.shape==="swarm")?(state.page==="bonus"?"Swarm gốc cho kết quả lệch luật. Verifier đối chiếu lại dữ kiện và sửa quote trước khi host ghi tiền; đối chiếu hai kết quả ở trên.":"Swarm đang cho kết quả lệch luật. Đây là điểm yếu có chủ đích của baseline trong đề; mở Bonus B3 để xem verifier sửa trước khi ghi tiền."):"Có kết quả lệch đáp án nghiệp vụ. Xem trace và đối chiếu quote với dữ liệu đơn."}</span></div>`;
    if(s.mode==="crash") body+=`<div class="explanation-strip">${icon("refresh")}<span>${s.response.results.some(r=>r.crash_observed)?"Crash đã được kích hoạt thật. Bảng lượt chạy phía dưới cho thấy trạng thái ledger sau crash, resume và retry.":"Claim này không đi tới điểm ghi refund, nên crash không được kích hoạt. Chọn C-001 hoặc C-012 để trình diễn crash/resume."}</span></div>`;
  }
  return `${section("02","Kết quả xử lý", "Quote là đề xuất theo chính sách. Thực hoàn là số tiền host đã ghi vào ledger.",s.response?`Lượt chạy mới · seed ${s.response.seed}`:"")}${body}`;
}
function resultCard(r) {
  const meta=SHAPES[r.shape], selected=active().focus===r.shape;
  return `<button class="result-card ${selected?"selected":""}" style="--shape-color:${meta.color}" data-focus="${r.shape}" aria-pressed="${selected}"><div class="result-name"><span class="shape-dot"></span>${meta.name}<span class="shape-letter">${meta.letter}</span></div><div class="shape-caption">${meta.caption}</div><div class="result-status ${r.passed?"":"wrong"}">${icon(r.passed?"check":"cross")}${r.passed?"Đúng theo luật nghiệp vụ":"Kết quả lệch luật"}</div><span class="badge ${r.status==="resolved"?"":r.passed?"neutral":"red"}">${STATUS[r.status]}</span><div class="money-pair"><div><span>Quote đề xuất</span><strong>${money(r.proposal_amount)}</strong></div><div><span>Thực hoàn</span><strong>${money(r.ledger.refund_amount)}</strong></div></div><div class="result-ledger"><span>${r.ledger.refund_count} refund</span><span>${r.ledger.committed_audit_count} audit committed</span></div><div class="result-cost"><span>${r.model_calls} model · ${r.tool_calls} tool</span><b>${money(r.cost_estimate,2)}</b></div></button>`;
}
function verifierArea() {
  const response=active().response;
  if(!response) return "";
  const result=response.results.find(r=>r.shape==="swarm_verified");
  if(!result) return "";
  const check=result.trace.events.find(e=>e.kind==="verifier_check");
  if(!check) return `<div class="explanation-strip">${icon("info")}Claim dừng trước verifier vì thiếu mã đơn hoặc không có quyền đọc đơn. Không chạy kiểm chứng dữ kiện ngoài phạm vi.</div>`;
  const correction=result.trace.events.find(e=>e.kind==="verifier_override")?.payload;
  const previous=correction?.previous_amount_vnd??result.proposal_amount;
  const corrected=correction?.verified_amount_vnd??result.proposal_amount;
  return `<section class="verifier-panel"><div class="verifier-side"><span class="eyebrow">QUOTE TRƯỚC KIỂM CHỨNG</span><strong class="big-amount">${money(previous)}</strong><p>${correction?"Dựa trên dữ kiện swarm đang dùng":"Dữ kiện swarm khớp nguồn có cấu trúc"}</p></div><div class="verifier-center"><div class="verifier-symbol">${icon("shield")}</div><div><strong>${correction?"Đã sửa trước khi ghi":"Dữ kiện đã khớp"}</strong><span>${correction?"Một vòng sửa · verifier bằng code":"Không gọi tính lại quote"}</span></div></div><div class="verifier-side verified"><span class="eyebrow">QUOTE SAU KIỂM CHỨNG</span><strong class="big-amount">${money(corrected)}</strong><p>${corrected===0?"Quote bằng 0 → không yêu cầu ghi refund":"Host tiếp tục kiểm approval và trần theo đơn"}</p></div><div class="verified-fields">${Object.entries(FIELD_NAMES).map(([field,name])=>`<span class="verified-field ${correction?.changed_fields.includes(field)?"changed":""}">${icon(correction?.changed_fields.includes(field)?"refresh":"check")}${name}</span>`).join("")}</div></section>`;
}
function eventText(event) {
  const p=event.payload;
  const descriptions={
    claim_lookup:["Đọc claim",p.found?"Tìm thấy yêu cầu":"Claim không tồn tại"],
    order_lookup:["Kiểm quyền đọc đơn",p.visible?"Đơn thuộc phạm vi người yêu cầu":reasonText(p.reason)],
    quote:["Tính quote bằng code",`${money(p.amount_vnd)} · ${reasonText(p.reason)}`],
    refund_request:["Gửi quote đầy đủ cho host",money(p.proposal_amount)],
    refund_attempt:["Gửi quote đầy đủ cho host",money(p.proposal_amount)],
    refund_outcome:["Kết quả từ host",reasonText(p.reason)],
    decision:["Quyết định cuối",`${STATUS[p.status]||p.status}${p.reason?" · "+reasonText(p.reason):""}`],
    react_action:["ReAct chọn tool đọc",p.tool],
    handoff:["Chuyển handoff đã lọc",`Chỉ tool đọc: ${(p.allowed_tools||[]).join(", ")}`],
    investigator:["Investigator đọc dữ liệu",p.lookup_order?.visible||p.visible?"Đơn hiển thị trong phạm vi được phép":"Đã kiểm tra quyền đọc"],
    model_override:["Swarm tin dữ kiện ticket",`Đổi ngày trễ thành ${p.delay_days} ngày`],
    verifier_check:["Verifier đọc lại nguồn",p.matched?"Các dữ kiện khớp đơn có cấu trúc":"Phát hiện dữ kiện không khớp"],
    verifier_override:["Verifier sửa quote",`${money(p.previous_amount_vnd)} → ${money(p.verified_amount_vnd)} · ${(p.changed_fields||[]).map(f=>FIELD_NAMES[f]||f).join(", ")}`],
    crash:["Crash được kích hoạt",p.at], error:["Dừng xử lý",reasonText(p.reason)], shape:["Bắt đầu shape","Khởi tạo lượt chạy"],
  };
  return descriptions[event.kind]||[event.kind,"Sự kiện từ trace thực tế"];
}
function traceArea() {
  const s=active(); if(!s.response) return "";
  const r=s.response.results.find(row=>row.shape===s.focus)||s.response.results[0];
  const meta=SHAPES[r.shape]; const events=r.trace.events;
  const position=Number.isFinite(state.traceStep)?Math.min(state.traceStep,events.length-1):events.length-1;
  return `<section class="panel trace-panel"><div class="trace-header"><div><h3>Bên trong ${meta.name}</h3><p>Phát lại trace từ lượt chạy thật · ${esc(r.run_id)}</p></div><div class="trace-actions"><span class="trace-progress">${position+1}/${events.length}</span><button data-trace="play" title="Phát lại từng sự kiện">${icon("play")}Phát lại</button><button data-trace="next" title="Sự kiện tiếp theo">${icon("arrow")}</button></div></div><p class="architecture-note">Luồng thiết kế · một claim có thể dừng sớm trước bước ghi tiền</p><div class="pipeline">${meta.pipeline.map((label,i)=>`<div class="pipeline-step"><span>BƯỚC 0${i+1}</span><strong>${label}</strong></div>`).join("")}</div><div class="timeline">${events.map((event,i)=>{const [title,detail]=eventText(event);return `<div class="event ${i===position?"active":""} ${i>position?"future":""} ${event.kind==="verifier_override"?"override":""}"><strong>${i+1}. ${esc(title)}</strong><p>${esc(detail)}</p></div>`;}).join("")}</div>${r.error_reason?`<div class="case-outcome">${icon("info")}${esc(reasonText(r.error_reason))}</div>`:""}${r.ledger.policy_denied.length?`<div class="case-outcome">${icon("shield")}Host ghi audit policy_denied: ${r.ledger.policy_denied.map(reasonText).map(esc).join(" · ")}</div>`:""}${s.mode!=="fresh"?`<div class="attempts"><div class="attempts-title">LEDGER QUA TỪNG LƯỢT · CÙNG MỘT DATABASE</div>${r.attempts.map(attempt=>`<div class="attempt-row"><strong>${PHASE[attempt.phase]}</strong><span>${STATUS[attempt.status]}</span><span>${attempt.refund_count} refund · ${attempt.committed_audit_count} audit · ${money(attempt.refund_amount)}</span></div>`).join("")}</div>`:""}<details class="raw-trace"><summary>Xem trace JSON và effect trong ledger</summary><pre>${esc(JSON.stringify({run_id:r.run_id,events:r.trace.events,ledger:r.ledger},null,2))}</pre></details></section>`;
}
function evidencePage() {
  const map={main:"benchmark",public:"bonus_public",adversarial:"bonus_adversarial"};
  const key=map[state.evidence], report=state.reports[key];
  const byShape=report?.by_shape||{}, entries=Object.entries(byShape);
  const maxCost=Math.max(...entries.map(([,s])=>s.cost_per_success_vnd||0),1)*1.1;
  const isBonus=state.evidence!=="main";
  const safety=isBonus?state.reports.bonus_safety?.by_dataset[state.evidence]:null;
  const verifiedSafety=safety?.swarm_verified;
  const chart=(cost=false)=>`<section class="panel chart-panel"><h3>${cost?"Chi phí cho một trial thành công":"Tỉ lệ xử lý đúng theo luật"}</h3><p>${cost?"Chi phí mô phỏng · thấp hơn tốt hơn":"Pass rate · cao hơn tốt hơn"}</p>${entries.map(([name,stats])=>`<div class="chart-row"><span class="chart-label"><i class="shape-dot" style="--shape-color:${SHAPES[name]?.color}"></i>${SHAPES[name]?.name||name}</span><div class="bar-track"><div class="bar-fill" style="width:${cost?(stats.cost_per_success_vnd||0)/maxCost*100:(stats.pass_rate||0)*100}%;background:${SHAPES[name]?.color}"></div></div><span class="chart-value">${cost?fmt(stats.cost_per_success_vnd,2):percent(stats.pass_rate)}</span></div>`).join("")}<div class="chart-scale"><span>0${cost?" ₫":"%"}</span><span>${cost?money(maxCost,0):"100%"}</span></div></section>`;
  return `<section class="hero"><div><span class="eyebrow">BENCHMARK & BẰNG CHỨNG</span><h1>Đo trước. <em>Kết luận sau.</em></h1><p>Số liệu đọc trực tiếp từ các file JSON do công cụ của lab sinh ra. Tách rõ bài chính và thí nghiệm B3.</p></div><div class="hero-node center" aria-hidden="true">${icon("chart")}</div></section><div class="evidence-controls">${[["main","Bài chính · Public"],["public","B3 · Public"],["adversarial","B3 · Đối kháng"]].map(([value,label])=>`<button class="segment ${state.evidence===value?"active":""}" data-evidence="${value}" aria-pressed="${state.evidence===value}">${label}</button>`).join("")}</div>${report?`<div class="stats-row">${stat("CLAIM",fmt(report.controlled_variables.claim_ids.length),isBonus&&state.evidence==="adversarial"?"Nhãn khai báo theo luật nghiệp vụ":"Fixture public của lab","","file")}${stat("SEED",fmt(report.controlled_variables.seeds.length),report.controlled_variables.seeds.join(" · "),"","refresh")}${stat("TRIAL",fmt(report.trials.length),"Database mới cho mỗi trial","","layers")}${stat("NGUỒN SỐ LIỆU",`${entries.length}<small>kiến trúc</small>`,`reports/${key}.json`,"highlight","chart")}</div><div class="chart-grid">${chart()}${chart(true)}</div><div class="panel table-panel"><table class="data-table"><thead><tr><th>KIẾN TRÚC</th><th>TRIAL PASS</th><th>PASS RATE</th><th>PASS^5</th><th>SEED VARIANCE</th><th>COST / SUCCESS</th><th>MEAN STEPS</th></tr></thead><tbody>${entries.map(([name,s])=>`<tr><td><span class="table-name"><i class="shape-dot" style="--shape-color:${SHAPES[name]?.color}"></i>${SHAPES[name]?.name||name}</span></td><td>${s.successes}/${s.trials}</td><td>${percent(s.pass_rate)}</td><td>${percent(s.pass_5)}</td><td>${fmt(s.seed_variance,6)}</td><td>${money(s.cost_per_success_vnd,2)}</td><td>${fmt(s.mean_steps,2)}</td></tr>`).join("")}</tbody></table></div><p class="table-note">Pass^5: tỉ lệ claim đúng ở cả 5 seed. Steps được đếm từ sự kiện trace của từng shape.</p><div class="proof-bottom"><section class="panel proof-card"><h3>${isBonus?"Kiểm chứng an toàn của verifier":"An toàn & khả năng tái lập"}</h3><div class="safety-list">${(isBonus?[["Secret / PII leak",`${verifiedSafety?.secret_leak_count??"—"} / ${verifiedSafety?.pii_leak_count??"—"}`],["Approval bypass",fmt(verifiedSafety?.approval_bypass_count)],["Verifier can thiệp",`${fmt(verifiedSafety?.verifier_overrides)} lần`],["Crash bổ sung",state.reports.bonus_safety?.crash.swarm_verified.crash_safety||"—"]]:[["Crash suite host / tham chiếu",state.reports.crash?.crash_safety||"—"],["Cùng seed & bảng giá","Được cố định"],["Dữ liệu tiền từ ledger","Code host kiểm soát"],["Số liệu được sinh tự động","Không chỉnh tay"]]).map(([label,value])=>`<div>${icon("check")}<span>${label}</span><b>${value}</b></div>`).join("")}</div><p class="method-note">${isBonus?"Safety audit đo trên các corpus này; crash bổ sung gồm 3 vị trí × 5 seed. Số lần can thiệp có thể lớn hơn số quyết định sai.":"Crash suite chính kiểm host và swarm tham chiếu. Các shape nhóm viết có test crash/resume riêng."}</p></section><section class="panel proof-card"><h3>Tải bằng chứng gốc</h3><p class="method-note">Dùng các file này để đối chiếu khi trình bày và viết báo cáo.</p><div class="download-list">${[`${key}.json`,isBonus?"bonus_safety.json":"crash.json",...(isBonus?["bonus_verifier_trace.json"]:[])].map(name=>`<a class="download-link" href="/reports/${name}" download>${icon("download")}${name}</a>`).join("")}</div><p class="method-note">Kết quả public và đối kháng không thay thế kết quả hidden. Chi phí là mô phỏng; latency không được đo.</p></section></div>`:'<div class="empty-state">Chưa có file báo cáo cho bộ dữ liệu này. Chạy lệnh benchmark/evaluate theo README của demo.</div>'}`;
}
function render() {
  if(!state.catalog) return;
  $("#content").className=state.page==="bonus"?"bonus-page":"";
  $("#breadcrumb").textContent={main:"Bài chính",bonus:"Bonus B3",evidence:"Bằng chứng"}[state.page];
  document.querySelectorAll("[data-page]").forEach(button=>{button.classList.toggle("active",button.dataset.page===state.page);button.setAttribute("aria-current",button.dataset.page===state.page?"page":"false");});
  $("#content").innerHTML=state.page==="evidence"?evidencePage():state.page==="bonus"?bonusPage():mainPage();
}
async function run() {
  if(state.busy||state.page==="evidence") return;
  const page=state.page, s=active(); state.busy=true; stopReplay(); render();
  $("#server-status").textContent="Đang chạy code thật";
  try {
    const response=await fetch("/api/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({dataset:s.dataset,claim_id:s.claim,seed:s.seed,mode:s.mode,shapes:selectedShapes(),crash_at:s.crash})});
    const body=await response.json(); if(!response.ok) throw new Error(body.error||"Không chạy được demo.");
    s.response=body;
    if(!body.results.some(row=>row.shape===s.focus)) s.focus=body.results[0].shape;
    state.traceStep=Infinity;
    if(state.page===page) notify(`Đã chạy ${body.results.length} kiến trúc · ${body.claim_id} · seed ${body.seed}`);
  } catch(error) { notify(error.message||"Không kết nối được server demo."); }
  finally {state.busy=false;$("#server-status").textContent="Chạy cục bộ";render();}
}
function stopReplay() { if(state.timer) clearInterval(state.timer);state.timer=null; }
function navigate(page) {
  if(!["main","bonus","evidence"].includes(page)) return;
  stopReplay();state.page=page;state.traceStep=Infinity;history.replaceState(null,"",`#${page}`);render();window.scrollTo({top:0,behavior:"smooth"});
  if(page!=="evidence"&&!active().response&&!state.busy) run();
}
function replay(action) {
  const s=active(), row=s.response?.results.find(r=>r.shape===s.focus)||s.response?.results[0]; if(!row) return;
  stopReplay();
  if(action==="next") {state.traceStep=Number.isFinite(state.traceStep)?Math.min(state.traceStep+1,row.trace.events.length-1):0;render();return;}
  state.traceStep=0;render();
  state.timer=setInterval(()=>{state.traceStep++; if(state.traceStep>=row.trace.events.length-1) stopReplay();render();},1000);
}
document.addEventListener("click",event=>{
  const button=event.target.closest("button"); if(!button) return;
  if(button.dataset.page) return navigate(button.dataset.page);
  if(button.dataset.evidence) {state.evidence=button.dataset.evidence;render();return;}
  if(button.dataset.focus) {active().focus=button.dataset.focus;state.traceStep=Infinity;stopReplay();render();return;}
  if(button.dataset.trace) return replay(button.dataset.trace);
  if(button.hasAttribute("data-preset")) {
    if(state.busy) return;
    const presets=state.page==="bonus"?[["public","C-002",55,"fresh"],["bonus","B3-002",55,"fresh"],["bonus","B3-009",55,"fresh"],["bonus","B3-011",55,"fresh"]]:[["public","C-001",11,"fresh"],["public","C-014",11,"fresh"],["public","C-012",11,"crash"],["public","C-002",55,"fresh"]];
    const [dataset,claim,seed,mode]=presets[Number(button.dataset.preset)];
    Object.assign(active(),{dataset,claim,seed,mode,shape:"all",response:null});state.traceStep=Infinity;run();return;
  }
  if(button.id==="run-button") return run();
  if(button.id==="help-button") return $("#help-dialog").showModal();
  if(button.id==="close-help") return $("#help-dialog").close();
  if(button.id==="present-button") {
    const enabled=document.body.classList.toggle("presenting");button.setAttribute("aria-label",enabled?"Thoát chế độ trình chiếu":"Bật chế độ trình chiếu");
    notify(enabled?"Chế độ trình chiếu · nhấn Esc để thoát":"Đã thoát trình chiếu");
  }
});
document.addEventListener("change",event=>{
  if(state.busy||state.page==="evidence") return;
  const s=active(), id=event.target.id, value=event.target.value;
  if(id==="dataset-select") {s.dataset=value;s.claim=state.catalog.datasets[value][0].claim_id;}
  else if(id==="claim-select") s.claim=value;
  else if(id==="seed-select") s.seed=Number(value);
  else if(id==="shape-select") s.shape=value;
  else if(id==="mode-select") s.mode=value;
  else if(id==="crash-select") s.crash=value;
  else return;
  s.response=null;state.traceStep=Infinity;stopReplay();render();
});
document.addEventListener("keydown",event=>{
  if(event.key==="Escape") {document.body.classList.remove("presenting");stopReplay();return;}
  if(["INPUT","SELECT","TEXTAREA"].includes(document.activeElement.tagName)||$("#help-dialog").open||event.ctrlKey||event.metaKey||event.altKey) return;
  if(["1","2","3"].includes(event.key)) navigate({1:"main",2:"bonus",3:"evidence"}[event.key]);
  if(event.key.toLowerCase()==="r") run();
});
window.addEventListener("hashchange",()=>navigate(location.hash.slice(1)));
async function init() {
  try {
    const responses=await Promise.all([fetch("/api/catalog"),fetch("/api/reports")]);
    if(responses.some(response=>!response.ok)) throw new Error("Không tải được dữ liệu demo.");
    [state.catalog,state.reports]=await Promise.all(responses.map(response=>response.json()));
    $("#server-status").textContent="Chạy cục bộ";render();
    if(state.page!=="evidence") run();
  } catch(error) {$("#content").innerHTML=`<div class="empty-state"><h3>Chưa kết nối được demo</h3><p>${esc(error.message)}</p><p>Khởi động bằng <code>python -m demo_ui.server</code> rồi tải lại trang.</p></div>`;$("#server-status").textContent="Chưa kết nối";}
}
init();
