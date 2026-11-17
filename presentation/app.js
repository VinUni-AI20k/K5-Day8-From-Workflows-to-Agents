/* Offline report viewer. All metrics are generated in data.js, never hardcoded. */
(() => {
  'use strict';
  const D = window.LAB_DATA;
  if (!D) { document.querySelector('h1').textContent = 'Chạy python -m presentation.build để tạo số liệu.'; return; }
  const $ = id => document.getElementById(id);
  const names = {workflow:'Workflow', single:'Single ReAct', orchestrator:'Orchestrator', swarm:'Swarm', swarm_verified:'Swarm + Verifier'};
  const pct = v => v == null ? '—' : (v * 100).toLocaleString('vi-VN',{maximumFractionDigits:2}) + '%';
  const number = (v, digits=2) => v == null ? '—' : Number(v).toLocaleString('vi-VN',{maximumFractionDigits:digits});
  const escape = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const allSafety = [...Object.values(D.safety.by_corpus).flatMap(c => Object.values(c)), ...Object.values(D.hidden?.safety_by_shape || {})];
  const total = k => allSafety.reduce((n,s)=>n+s[k],0);
  $('hero-pass').textContent = pct(D.main.by_shape.workflow.pass_rate);
  $('hero-crash').textContent = D.crash.crash_safety;
  $('hero-bonus').textContent = pct(D.adversarial.by_shape.swarm_verified.pass_rate);
  $('hero-safety').textContent = `${total('secret_leak_count')} / ${total('pii_leak_count')} / ${total('approval_bypass_count')}`;
  if(D.hidden){
    const h=D.hidden, w=h.by_shape.workflow;
    $('hidden-local-status').textContent=`local · workflow ${pct(w.pass_rate)}`;
    $('hidden-summary').hidden=false;
    $('hidden-summary').textContent=`HIDDEN LOCAL · Workflow ${w.successes}/${w.trials} · Pass⁵ ${pct(w.pass_5)} · ${number(w.cost_per_success_vnd)} VND/success · Crash ${h.crash_safety}`;
    const option=new Option('Hidden local · 5 kiến trúc','hidden');
    $('corpus').add(option);$('corpus').value='hidden';
    $('decision-limit').textContent='Workflow đạt 200/200 trial hidden local, qua ngưỡng kỹ thuật bài chính và điều kiện B3 trên pack được cung cấp. Điểm chính thức do giảng viên xác nhận. MockLLM, dữ liệu synthetic, lỗi swarm có chủ đích; latency unavailable. Không suy rộng thành nhiều agent luôn kém hơn.';
  }else{
    $('hidden-local-status').textContent='chưa có số liệu local';
  }
  const shapes = {
    workflow:{label:'A / WORKFLOW',title:'Một đường đi rõ ràng.',copy:'Chương trình làm theo các bước đã viết sẵn: tìm yêu cầu, kiểm tra chủ đơn, tính tiền theo chính sách rồi xin phép ghi khoản hoàn. Không cần gọi AI.',nodes:['Nhận yêu cầu của khách','Kiểm tra đơn và người sở hữu','Tính tiền theo chính sách','Duyệt và ghi khoản hoàn']},
    single:{label:'B / SINGLE REACT',title:'Một tác nhân, tối đa tám lượt.',copy:'Lặp lại việc quan sát, chọn việc và tra cứu. AI chỉ mô phỏng suy nghĩ; Python mới chọn bước tiếp theo. Mỗi lượt gọi AI đều được tính chi phí.',nodes:['Nhận yêu cầu của khách','Lặp quan sát và chọn việc','Tra cứu đơn rồi tính tiền','Duyệt và ghi khoản hoàn']},
    orchestrator:{label:'C / ORCHESTRATOR',title:'Giao việc, giữ quyền kiểm soát.',copy:'Bộ điều phối giao việc trong phạm vi cho phép. Bộ tra cứu chỉ đọc thông tin, không được ghi tiền. Kết quả được tập hợp trước khi xét hoàn.',nodes:['Lập kế hoạch xử lý','Giao việc trong phạm vi cho phép','Tra cứu dữ liệu, không ghi tiền','Tập hợp kết quả và đề nghị hoàn']},
    swarm:{label:'D / SWARM',title:'Làm lần lượt, thêm điểm có thể sai.',copy:'Các vai mô phỏng lần lượt góp ý, đọc lời nhắn, tra cứu và soạn phản hồi. Một số lần mô phỏng cố ý tin số ngày khách nói. Cổng ghi tiền không tự sửa dữ kiện đó.',nodes:['Mô phỏng ý kiến và đọc lời nhắn','Tra cứu đơn và chính sách','Lỗi cố ý: tin số ngày khách nói','Soạn phản hồi rồi xét ghi tiền']}
  };
  function setShape(shape) {
    const c=shapes[shape];
    $('architecture-label').textContent=c.label; $('architecture-title').textContent=c.title; $('architecture-copy').textContent=c.copy;
    $('architecture-diagram').innerHTML=c.nodes.map((n,i)=>`${i?'<div class="flow-arrow" aria-hidden="true">→</div>':''}<div class="flow-node ${i===1?'featured':''}">${escape(n)}</div>`).join('');
    document.querySelectorAll('[data-shape]').forEach(b=>{b.classList.toggle('active',b.dataset.shape===shape);b.setAttribute('aria-pressed',String(b.dataset.shape===shape));});
  }
  document.querySelectorAll('[data-shape]').forEach(b=>b.addEventListener('click',()=>setShape(b.dataset.shape)));
  setShape('workflow');
  function renderMetrics() {
    const key=$('corpus').value, report=D[key], entries=Object.entries(report.by_shape);
    $('metrics-body').innerHTML=entries.map(([shape,s])=>`<tr class="${shape==='workflow'?'best-row':''}"><td>${names[shape]}</td><td>${pct(s.pass_rate)}</td><td>${pct(s.pass_5)}</td><td>${pct(s.seed_min)} – ${pct(s.seed_max)}</td><td>${number(s.seed_variance,6)}</td><td>${number(s.cost_per_success_vnd)}</td><td>${number(s.mean_steps)} / ${number(s.p95_steps)}</td></tr>`).join('');
    $('pass-chart').innerHTML=entries.map(([shape,s])=>`<div class="bar-row"><span>${names[shape]}</span><div class="bar-track" role="img" aria-label="${names[shape]} ${pct(s.pass_rate)}"><div class="bar-fill ${shape}" style="width:${Math.max(0,Math.min(100,s.pass_rate*100))}%"></div></div><b>${pct(s.pass_rate)}</b></div>`).join('');
    $('corpus-description').textContent=`${key==='hidden'?'Chấm local bằng nhãn riêng · ':''}${report.controlled_variables.claim_ids.length} claim × ${report.controlled_variables.seeds.length} seed × ${entries.length} shape. Mỗi trial dùng SQLite mới.`;
  }
  $('corpus').addEventListener('change',renderMetrics);renderMetrics();
  function renderDemo(){
    const seed=Number($('demo-seed').value), rows=D.public.trials.filter(t=>t.claim_id==='C-002'&&t.seed===seed);
    const before=rows.find(t=>t.shape==='swarm'), after=rows.find(t=>t.shape==='swarm_verified');
    $('demo-before').textContent=before.status==='resolved'?'20.000 đ':'0 đ';
    $('demo-after').textContent=after.status==='resolved'?'20.000 đ':'0 đ';
    $('demo-before-status').textContent=`${before.status} · ${before.passed?'PASS':'FAIL'}`;
    $('demo-after-status').textContent=`${after.status} · ${after.passed?'PASS':'FAIL'}`;
    $('demo-explanation').textContent=seed===55?'Seed 55: swarm dùng delay 5 thay cho 2. Verifier đọc lại order, phát hiện lệch và quote lại từ 20.000 về 0; không tạo refund.':'Seed 11: swarm đã dùng delay 2 đúng. Verifier xác nhận khớp, không quote lại. Vẫn phát sinh chi phí cho một lần đọc kiểm chứng.';
  }
  $('demo-seed').addEventListener('change',renderDemo);renderDemo();
  $('trace-example').textContent=JSON.stringify({run_id:D.example.result.run_id,events:D.example.trace.events.filter(e=>['model_override','verifier_check','verifier_override','quote'].includes(e.kind)),ledger:D.example.ledger},null,2);
  function renderEvidence(){
    const corpus=$('evidence-corpus').value, shape=$('evidence-shape').value, seed=Number($('evidence-seed').value), onlyFail=$('evidence-filter').value==='fail';
    const rows=D[corpus].trials.filter(r=>r.shape===shape&&r.seed===seed&&(!onlyFail||!r.passed));
    const cases=new Map(D.cases[corpus].map(c=>[c.claim_id,c]));
    $('evidence-body').innerHTML=rows.length?rows.map(r=>`<tr><td>${escape(r.claim_id)}${cases.get(r.claim_id)?.title?'<br><small>'+escape(cases.get(r.claim_id).title)+'</small>':''}</td><td>${escape(r.status)}</td><td><span class="${r.passed?'pass-badge':'fail-badge'}">${r.passed?'PASS':'FAIL'}</span></td><td>${escape(r.reason)}</td><td class="run-id">${escape(r.run_id)}</td></tr>`).join(''):'<tr><td colspan="5">Không có trial phù hợp bộ lọc.</td></tr>';
    $('evidence-count').textContent=`Đang hiển thị ${rows.length} trial · ${names[shape]} · seed ${seed}`;
  }
  ['evidence-corpus','evidence-shape','evidence-seed','evidence-filter'].forEach(id=>$(id).addEventListener('change',renderEvidence));renderEvidence();
  $('safety-description').textContent=`${total('trials')} trial được chạy lại: ${total('secret_leak_count')} secret leak, ${total('pii_leak_count')} PII leak, ${total('approval_bypass_count')} approval bypass, ${total('execution_errors')} execution error. Crash public bổ sung: ${D.safety.crash_safety}${D.hidden?`; hidden ${D.hidden.crash_safety}`:''}.`;
  const workflow=D.main.by_shape.workflow, verified=D.public.by_shape.swarm_verified;
  $('decision-metric').textContent=(D.hidden?`Hidden local ${pct(D.hidden.by_shape.workflow.pass_rate)} · Pass⁵ ${pct(D.hidden.by_shape.workflow.pass_5)} · ${number(D.hidden.by_shape.workflow.cost_per_success_vnd)} VND/success. `:'')+`Public ${pct(workflow.pass_rate)} · Pass⁵ ${pct(workflow.pass_5)} · ${number(workflow.cost_per_success_vnd)} VND mô phỏng / success`;
  $('decision-b3').textContent=`Public: ${pct(verified.pass_rate)} pass, ${number(verified.cost_per_success_vnd)} VND/success; ${number(verified.cost_per_success_vnd/workflow.cost_per_success_vnd)}× workflow. Mức tăng chi phí không tạo thêm độ đúng so với workflow trên corpus này.`;
  $('download').addEventListener('click',()=>{const blob=new Blob([JSON.stringify(D,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='logix-lab08-evidence.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
  const sections=[...document.querySelectorAll('.page-section')], navs=[...document.querySelectorAll('nav a')];let current=0, requestedSlide=null;
  function selectSlide(index){current=Math.max(0,Math.min(sections.length-1,index));sections.forEach((s,i)=>s.classList.toggle('active',i===current));navs.forEach((a,i)=>a.classList.toggle('selected',i===current));$('slide-position').textContent=`${current+1} / ${sections.length}`;$('previous').disabled=current===0;$('next').disabled=current===sections.length-1;if(document.body.classList.contains('presenting'))window.scrollTo(0,0);}
  function presentation(on){if(on&&requestedSlide!==null)current=requestedSlide;document.body.classList.toggle('presenting',on);$('slide-controls').hidden=!on;$('present').textContent=on?'Đang trình chiếu · Esc':'Trình chiếu ↗';$('present').setAttribute('aria-pressed',String(on));selectSlide(current);if(!on){requestedSlide=current;sections[current].scrollIntoView({behavior:'instant'});}}
  $('present').addEventListener('click',()=>presentation(!document.body.classList.contains('presenting')));$('exit').addEventListener('click',()=>presentation(false));$('next').addEventListener('click',()=>selectSlide(current+1));$('previous').addEventListener('click',()=>selectSlide(current-1));
  navs.forEach((a,i)=>a.addEventListener('click',e=>{e.preventDefault();requestedSlide=i;selectSlide(i);if(!document.body.classList.contains('presenting')){history.replaceState(null,'',a.getAttribute('href'));sections[i].scrollIntoView({behavior:'instant',block:'start'});}}));
  document.addEventListener('focusin',e=>{const section=e.target.closest('.page-section');if(section)requestedSlide=sections.indexOf(section);});
  window.addEventListener('wheel',()=>{if(!document.body.classList.contains('presenting'))requestedSlide=null;},{passive:true});
  window.addEventListener('touchmove',()=>{if(!document.body.classList.contains('presenting'))requestedSlide=null;},{passive:true});
  document.querySelector('.text-link').addEventListener('click',e=>{if(document.body.classList.contains('presenting')){e.preventDefault();selectSlide(sections.findIndex(s=>s.id==='benchmark'));}});
  $('notes-toggle').addEventListener('click',()=>{const on=document.body.classList.toggle('show-notes');$('notes-toggle').setAttribute('aria-pressed',String(on));});
  document.addEventListener('keydown',e=>{if(e.target.closest('.flow-workspace, #flow-dialog')||document.querySelector('#flow-dialog[open]'))return;if(!document.body.classList.contains('presenting')||/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName))return;if(e.key===' '&&document.activeElement.tagName==='BUTTON')return;if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();selectSlide(current+1);}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();selectSlide(current-1);}if(e.key==='Escape')presentation(false);});
  // Escape also works while a presentation control has focus.
  document.addEventListener('keydown',e=>{if(!document.querySelector('#flow-dialog[open]')&&e.key==='Escape'&&document.body.classList.contains('presenting'))presentation(false);});
  const observer=new IntersectionObserver(entries=>{if(document.body.classList.contains('presenting'))return;for(const e of entries)if(e.isIntersecting){current=sections.indexOf(e.target);navs.forEach((a,i)=>a.classList.toggle('selected',i===current));}},{rootMargin:'-10% 0px -65% 0px'});sections.forEach(s=>observer.observe(s));
  selectSlide(0);
})();
