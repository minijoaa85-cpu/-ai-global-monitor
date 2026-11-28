"use strict";
(() => {
  const $=id=>document.getElementById(id);
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const drawer=$("history-drawer"),overlay=$("history-backdrop"),openButtons=[...document.querySelectorAll("[data-history-open]")];
  let history=null,group="all";
  const versionGroup=v=>String(v).match(/^V(\d+)/)?.[1]||"?";
  function openHistory(){
    drawer.hidden=false;overlay.hidden=false;document.body.classList.add("history-open");
    openButtons.forEach(b=>b.setAttribute("aria-expanded","true"));$("history-close").focus();
  }
  function closeHistory(){
    drawer.hidden=true;overlay.hidden=true;document.body.classList.remove("history-open");
    openButtons.forEach(b=>b.setAttribute("aria-expanded","false"));
    openButtons[0]?.focus();
  }
  openButtons.forEach(b=>b.addEventListener("click",openHistory));
  $("history-close").addEventListener("click",closeHistory);
  overlay.addEventListener("click",closeHistory);
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!drawer.hidden)closeHistory();});
  function render(){
    if(!history)return;
    const entries=[...history.entries].reverse().filter(e=>group==="all"||versionGroup(e.version)===group);
    $("history-current-version").textContent=history.latest_version;
    $("history-version-count").textContent=history.entries.length+"개";
    $("history-updated-on").textContent=history.updated_on;
    $("ui-release-label").textContent="현재 UI "+history.latest_version;
    $("history-list").innerHTML=entries.map(e=>'<article class="history-entry"><div class="history-meta"><strong>'+esc(e.version)+'</strong><span>'+esc(e.date)+'</span></div>'+
      '<h3>'+esc(e.title)+'</h3><p>'+esc(e.summary)+'</p>'+
      '<details><summary>WHY · WHAT · VALUE 상세보기</summary>'+
      '<dl><dt>WHY · 개발 배경</dt><dd>'+esc(e.background)+'</dd>'+
      '<dt>WHAT · 핵심 변경</dt><dd>'+esc(e.changes)+'</dd>'+
      '<dt>VALUE · 사용자 가치</dt><dd>'+esc(e.value)+'</dd></dl>'+
      (String(e.ref||"").startsWith("https://github.com/")?'<a href="'+esc(e.ref)+'" target="_blank" rel="noopener noreferrer">근거 기록 ↗</a>':"")+
      '</details></article>').join("")||'<p class="muted">기록된 버전이 없습니다.</p>';
    $("history-status").textContent=entries.length+"개 버전 표시 · GitHub 구현 기록 기준";
  }
  $("history-filter").addEventListener("change",e=>{group=e.target.value;render();});
  fetch("./version_history.json?v="+Date.now(),{cache:"no-store"}).then(r=>{if(!r.ok)throw Error("HTTP "+r.status);return r.json();})
   .then(data=>{
     if(data.schema_version!==1||!Array.isArray(data.entries)||!data.latest_version)throw Error("형식 불일치");
     history=data;
     const groups=[...new Set(data.entries.map(e=>versionGroup(e.version)))].sort((a,b)=>Number(b)-Number(a));
     $("history-filter").innerHTML='<option value="all">전체 버전</option>'+groups.map(g=>'<option value="'+esc(g)+'">V'+esc(g)+'.x</option>').join("");
     render();
   }).catch(err=>{
     $("history-status").textContent="이력 로딩 오류: "+err.message;
     $("history-list").textContent="version_history.json 파일 및 배포 상태를 확인하세요.";
   });
})();