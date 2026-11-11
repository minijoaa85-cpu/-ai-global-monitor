"use strict";
(()=>{
 const root=document.getElementById("ai-news-board");
 if(!root)return;
 const $=id=>document.getElementById(id);
 const escape=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 const fmtDate=v=>{let d=new Date(v);return isNaN(d.getTime())?"발표일 미확인":d.toLocaleDateString("ko-KR",{timeZone:"Asia/Seoul",year:"numeric",month:"short",day:"numeric"});};
 let records=[],kind="전체",publisher="전체";
 const safeURL=s=>{try{let u=new URL(s);return u.protocol==="https:"?u.href:""}catch{return ""}};
 function render(){
  let arr=records.filter(x=>(kind==="전체"||x.category===kind)&&(publisher==="전체"||x.source===publisher));
  $("ai-news-items").innerHTML=arr.length?arr.slice(0,16).map(item=>{
   let link=safeURL(item.url);
   return '<article class="news-item"><div class="news-meta"><span class="news-tag">'+escape(item.category)+'</span><span>'+escape(item.source)+'</span><span>'+escape(fmtDate(item.published_at))+'</span>'+(item.stale?'<span class="news-stale">이전 수집</span>':'')+'</div><h3>'+escape(item.title)+'</h3><p>'+escape(item.summary)+'</p><a href="'+escape(link)+'" target="_blank" rel="noopener noreferrer">원문 기사 보기 ↗</a></article>';
  }).join(""):'<p class="muted">현재 조건에 맞는 뉴스가 없습니다. 분야 또는 출처 필터를 바꿔 보세요.</p>';
  $("ai-news-count").textContent=arr.length+"건 표시";
 }
 async function load(){
  try{
   const res=await fetch("./data/news.json?v="+Date.now(),{cache:"no-store"});
   if(!res.ok)throw new Error("HTTP "+res.status);
   let data=await res.json();
   if(!Array.isArray(data.items))throw new Error("기사 파일 형식 오류");
   records=data.items.filter(x=>x&&x.title&&safeURL(x.url)&&x.source&&x.published_at);
   let groups=["전체",...new Set(records.map(x=>x.category))],sources=["전체",...new Set(records.map(x=>x.source))];
   const fill=(id,opts)=>{$(id).innerHTML=opts.map(x=>'<option value="'+escape(x)+'">'+escape(x)+'</option>').join("")};
   fill("ai-news-kind",groups);fill("ai-news-source",sources);
   const date=data.updated_at?new Date(data.updated_at).toLocaleString("ko-KR",{timeZone:"Asia/Seoul",month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"}):"미확인";
   $("ai-news-updated").textContent="수집: "+date+" · 공식 게시물 제목·소개문 요약";
   let failed=Object.entries(data.sources||{}).filter(([k,v])=>!String(v).startsWith("OK"));
   if(failed.length)$("ai-news-status").textContent="일부 공식 피드를 확인하지 못했습니다: "+failed.map(([k])=>k).join(", ");
   else $("ai-news-status").textContent="공식 발표를 기준으로 업데이트합니다. 기사만으로 다음 주 성능 순위를 예측하지 않습니다.";
   render();
  }catch(e){
   $("ai-news-status").textContent="뉴스 수집 데이터를 아직 불러올 수 없습니다: "+e.message;
   $("ai-news-items").innerHTML='<p class="muted">자동 수집 작업이 끝나면 공식 업데이트와 기사 링크가 표시됩니다.</p>';
  }
 }
 $("ai-news-kind").addEventListener("change",()=>{kind=$("ai-news-kind").value;render()});
 $("ai-news-source").addEventListener("change",()=>{publisher=$("ai-news-source").value;render()});
 load();
})();