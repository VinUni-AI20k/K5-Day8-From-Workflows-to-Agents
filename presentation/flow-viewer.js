/* Documentation viewer only. Does not read/write ledger or benchmark results. */
(() => {
  'use strict';
  const catalog = window.LAB_FLOWS;
  if (!catalog) return;
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const flows = catalog.flows;
  let index = 0, scale = 1, fitPending = true, fitMode = 'height';
  const canvas = $('flow-canvas'), workspace = $('flow-workspace'), dialog = $('flow-dialog');
  const placeholder = $('flow-placeholder');
  $('flow-select').innerHTML = flows.map((f,i)=>`<option value="${i}">${i+1}. ${esc(f.title)}</option>`).join('');
  $('flow-legend').innerHTML = catalog.legend.map(l=>`<span style="background:${l.fill};border-color:${l.stroke};color:${l.stroke}">${esc(l.tag)}</span>`).join('')+'<span style="background:#fff;border-color:#708077">◇ Quyết định: Có / Không</span>';
  $('flow-comparison-body').innerHTML = catalog.comparison.map(row=>'<tr>'+row.map(cell=>`<td>${esc(cell)}</td>`).join('')+'</tr>').join('');
  function sizeDiagram(next, preserveCenter=false){
    const svg = canvas.querySelector('svg'); if(!svg) return;
    const old = scale, cx=(canvas.scrollLeft+canvas.clientWidth/2)/old, cy=(canvas.scrollTop+canvas.clientHeight/2)/old;
    scale=Math.max(.025,Math.min(2.5,next));
    svg.style.width = `${Number(svg.getAttribute('width'))*scale}px`;
    svg.style.height = `${Number(svg.getAttribute('height'))*scale}px`;
    svg.style.marginLeft = scale*Number(svg.getAttribute('width'))<canvas.clientWidth ? 'auto' : '0';
    svg.style.marginRight = svg.style.marginLeft;
    $('flow-zoom').textContent=`${Math.round(scale*100)}%`;
    if(preserveCenter){canvas.scrollLeft=cx*scale-canvas.clientWidth/2;canvas.scrollTop=cy*scale-canvas.clientHeight/2;}
  }
  function fit(mode=fitMode){
    fitMode=mode;
    canvas.classList.toggle('flow-overview',mode==='whole');
    const svg=canvas.querySelector('svg');if(!svg)return;
    if(canvas.clientWidth<30){fitPending=true;return;}
    fitPending=false;
    const width=(canvas.clientWidth-20)/Number(svg.getAttribute('width'));
    const height=(canvas.clientHeight-20)/Number(svg.getAttribute('height'));
    sizeDiagram(mode==='whole'?Math.min(width,height):mode==='height'?Math.min(1,height):width);
    canvas.scrollTop=0;canvas.scrollLeft=0;
  }
  function renderDiagram(){
    const f=flows[index];
    $('flow-panel-title').textContent=`${f.title} · Toàn bộ quy trình`;
    $('flow-dialog-title').textContent=f.title;
    $('flow-panel-note').textContent=f.difference;
    canvas.innerHTML=f.svg;
    scale=1;fit();
  }
  function renderFlow(){
    const f=flows[index];
    const labels=[['Đầu vào',f.input],['Các bước',f.steps],['Ai quyết định',f.owner],['Đầu ra',f.output],['Khác biệt',f.difference]];
    $('flow-summary').innerHTML='<dl>'+labels.map(([key,value])=>`<dt>${key}</dt><dd>${esc(value)}</dd>`).join('')+'</dl><ul>'+f.notes.map(n=>`<li>${esc(n)}</li>`).join('')+'</ul><p class="scope-note">Đối chiếu: '+f.files.map(file=>`<a href="../${file}">${esc(file)}</a>`).join(' · ')+'</p>';
    $('flow-technical-body').innerHTML=f.technical.map(r=>`<tr><td>${esc(r.step)}</td><td><code>${esc(r.code)}</code></td><td><a href="../${esc(r.file)}">${esc(r.file)}</a></td></tr>`).join('');
    renderDiagram();
  }
  $('flow-select').addEventListener('change',e=>{index=Number(e.target.value);renderFlow();});
  $('flow-fit').addEventListener('click',()=>fit('height'));
  $('flow-pan-back').addEventListener('click',()=>canvas.scrollBy({left:-canvas.clientWidth*.8,behavior:'smooth'}));
  $('flow-pan-next').addEventListener('click',()=>canvas.scrollBy({left:canvas.clientWidth*.8,behavior:'smooth'}));
  canvas.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();canvas.scrollBy({left:canvas.clientWidth*.65*(e.key==='ArrowRight'?1:-1),behavior:'smooth'});}});
  $('flow-whole').addEventListener('click',()=>fit('whole'));
  $('flow-actual').addEventListener('click',()=>sizeDiagram(1,true));
  $('flow-zoom-in').addEventListener('click',()=>sizeDiagram(scale*1.3,true));
  $('flow-zoom-out').addEventListener('click',()=>sizeDiagram(scale/1.3,true));
  $('flow-expand').addEventListener('click',()=>{
    placeholder.before(workspace); // Stable original position before moving it.
    $('flow-dialog-content').append(workspace);
    dialog.showModal();$('flow-expand').hidden=true;fit('height');
    $('flow-close').focus();
  });
  function restore(){placeholder.before(workspace);$('flow-expand').hidden=false;fit();$('flow-expand').focus();}
  $('flow-close').addEventListener('click',()=>dialog.close());
  dialog.addEventListener('close',restore);
  // Esc closes only the dialog; do not also exit the presentation underneath.
  dialog.addEventListener('keydown',e=>e.stopPropagation());
  new ResizeObserver(()=>{if(fitPending&&canvas.clientWidth>30)fit();}).observe(canvas);
  window.addEventListener('resize',()=>{fitPending=true;fit();});
  let printed=false;
  function printPages(){
    if(printed)return;printed=true;
    $('flow-print-pages').innerHTML=flows.map((f,fi)=>`<article class="flow-print-sheet"><h3>${fi+1}. ${esc(f.title)} — toàn bộ quy trình</h3><p class="flow-print-label">${esc(f.owner)}. Hình thoi: Có/Không. Một sơ đồ nguyên vẹn trên một trang in; sơ đồ dài có thể cần phóng to PDF để đọc kỹ.</p>${f.svg.replaceAll(f.id+'_whole-', 'print-'+f.id+'_whole-')}<p class="flow-print-foot">${esc(f.difference)}</p></article>`).join('');
  }
  window.addEventListener('beforeprint',printPages);
  $('flow-print').addEventListener('click',()=>{printPages();document.body.classList.add('print-flows-only');window.print();});
  window.addEventListener('afterprint',()=>document.body.classList.remove('print-flows-only'));
  renderFlow();
})();
