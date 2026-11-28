"use strict";
(async function(){
 const $=id=>document.getElementById(id);
 const safe=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 try{
  const r=await fetch("./data/weekly_brief.json?v="+Date.now(),{cache:"no-store"});
  if(!r.ok)throw Error("HTTP "+r.status);
  const d=await r.json();
  if(d.schema_version!==1||!Array.isArray(d.insights))throw Error("Invalid weekly brief format");
  $("weekly-pulse-headline").textContent=d.headline||"이번 주 AI 동향을 확인할 데이터가 부족합니다.";
  $("weekly-pulse-date").textContent="평가 주차 "+(d.benchmark_week||"미수집")+" · 뉴스 최근 7일 "+Number(d.weekly_news_count||0)+"건";
  $("weekly-pulse-insights").innerHTML=d.insights.slice(0,3).map(x=>'<p>'+safe(x)+'</p>').join("");
  const flags=d.quality_flags||[];
  $("weekly-pulse-quality").textContent=flags.length?"분석 한계: "+flags.join(" · "):"공식 공개 자료 기반 요약 · 미래 순위 예측 아님";
  if(String(d.benchmark_source_url||"").startsWith("https://huggingface.co/"))
   $("weekly-pulse-benchmark-link").href=d.benchmark_source_url;
 }catch(e){
  $("weekly-pulse-headline").textContent="이번 주 요약을 불러오지 못했습니다.";
  $("weekly-pulse-date").textContent="자동 분석 대기";
  $("weekly-pulse-insights").innerHTML="<p>주간 수집 또는 뉴스 수집이 완료되면 공식 근거를 기준으로 자동 작성됩니다.</p>";
  $("weekly-pulse-quality").textContent="요약 생성·배포 상태를 확인하세요.";
 }
})();