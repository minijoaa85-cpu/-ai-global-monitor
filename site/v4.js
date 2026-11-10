"use strict";
const $ = id => document.getElementById(id);
const safe = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const num = value => Number(value).toLocaleString("ko-KR",{maximumFractionDigits:3});
const cols = ["#80b8ff","#6be0c7","#f1bb79"];
const labels = {text:"텍스트",text_style_control:"텍스트 · 스타일 보정",webdev:"웹 개발",search:"검색",vision:"이미지 이해",document:"문서 이해",agent:"에이전트"};
let history=[], status={}, all=[], chosen=[], board="", category="", term="";
const unique = xs => [...new Set(xs)].filter(Boolean);
function setOptions(el,values,format,selected,includeAll=false){
  el.innerHTML=(includeAll?'<option value="*">전체 부문</option>':'')+values.map(v=>'<option value="'+safe(v)+'">'+safe(format(v))+'</option>').join("");
  el.value=values.includes(selected)?selected:(includeAll?"*":values[0]||"");
}
function latest(){return history.length ? history[history.length-1] : {week:null,records:[]}}
function sourceRows(){return all.filter(r=>r.source==="Arena"&&r.benchmark===board)}
function scoped(){return sourceRows().filter(r=>r.category===category)}
function ranked(){return scoped().sort((a,b)=>{
 const ar=a.rank,br=b.rank;
 return ar!=null&&br!=null?ar-br:ar!=null?-1:br!=null?1:b.score-a.score;
})}
function comparePast(r){
 const old=history.length>1?history[history.length-2].records:[];
 return old.find(x=>x.source===r.source && x.benchmark===r.benchmark &&
 x.category===r.category && x.version===r.version && x.model_id===r.model_id);
}
function delta(r){
 const p=comparePast(r);
 return p && Number.isFinite(Number(p.score))?Number(r.score)-Number(p.score):null;
}
function prettyDate(iso){
 if(!iso)return "미수집";
 const d=new Date(iso);return Number.isNaN(d.getTime())?iso:d.toLocaleString("ko-KR",{timeZone:"Asia/Seoul",month:"numeric",day:"numeric",hour:"2-digit",minute:"2-digit"});
}
function renderStats(){
 $("stat-models").textContent=num(unique(all.map(x=>x.model)).length);
 $("stat-records").textContent=num(all.length);
 $("stat-boards").textContent=num(unique(all.map(x=>x.benchmark)).length);
 $("stat-updated").textContent=prettyDate(status.collected_at);
 $("notice").textContent=all.length
 ? "공식 Arena 공개 데이터 수집 성공 · "+num(all.length)+"건 · "+
   "평가 분야마다 점수 체계와 표본 규모가 다릅니다."
 : "표시할 공개 평가 데이터가 없습니다. 수집 실행 로그에서 오류를 확인하세요.";
}
function selectBoard(){
 const boards=unique(all.filter(r=>r.source==="Arena").map(r=>r.benchmark));
 const previous=board;
 setOptions($("board"),boards,v=>labels[v]||v,previous);
 board=$("board").value;
 selectCategory();
}
function selectCategory(){
 const cats=unique(sourceRows().map(r=>r.category)).sort((a,b)=>a==="overall"?-1:b==="overall"?1:a.localeCompare(b));
 setOptions($("category"),cats,v=>v==="overall"?"전체 평가":v,category,false);
 category=$("category").value;
 renderAll();
}
function rowHtml(r){
 const d=delta(r);
 const change=d===null?'<span class="muted">비교 주차 없음</span>':
 '<span class="'+(d>0?"up":d<0?"down":"muted")+'">'+(d>0?"+":"")+num(d)+'</span>';
 const ci=r.ci_low!=null&&r.ci_high!=null?num(r.ci_low)+" – "+num(r.ci_high):"—";
 return '<tr><td><span class="rank">'+safe(r.rank??"—")+'</span></td>'+
 '<td class="model">'+safe(r.model)+'<span class="provider">'+safe(r.provider)+'</span></td>'+
 '<td><strong>'+num(r.score)+'</strong></td><td>'+ci+'</td><td>'+change+'</td><td>'+safe(r.publish_date||"—")+'</td></tr>';
}
function renderRanking(){
 const search=term.toLowerCase(), data=ranked().filter(r=>(r.model+" "+r.provider).toLowerCase().includes(search));
 $("rankings").innerHTML=data.length?data.slice(0,10).map(rowHtml).join("")
 : '<tr><td colspan="6" class="muted">이 조건의 평가 데이터가 없습니다.</td></tr>';
 const count=data.reduce((a,x)=>a+(Number(x.sample_count)||0),0);
 $("rank-foot").textContent="현재 "+(labels[board]||board)+" / "+(category)+
 " · 전체 "+data.length+"개 모델 · 공식 발표 점수 · 발표 시점과 수집 시점은 다를 수 있습니다.";
}
function renderCompareOptions(){
 const top=ranked().filter(r=>!term||(r.model+" "+r.provider).toLowerCase().includes(term.toLowerCase()));
 const options=top.slice(0,12);
 const ids=new Set(options.map(r=>r.model_id));
 chosen=chosen.filter(id=>ids.has(id)).slice(0,3);
 if(!chosen.length)chosen=options.slice(0,3).map(r=>r.model_id);
 $("compare-options").innerHTML=options.map(r=>'<label class="option"><input type="checkbox" data-model="'+safe(r.model_id)+'" '+(chosen.includes(r.model_id)?"checked":"")+'>'+safe(r.model)+'</label>').join("");
 $("compare-options").querySelectorAll("input").forEach(c=>c.addEventListener("change",()=>{
  const id=c.dataset.model;
  if(c.checked&&!chosen.includes(id))chosen.push(id);
  if(!c.checked)chosen=chosen.filter(v=>v!==id);
  chosen=chosen.slice(-3);
  renderCompareOptions();renderCompareChart();renderTrend();
 }));
 renderCompareChart();renderTrend();
}
function renderCompareChart(){
 const rows=ranked().filter(r=>chosen.includes(r.model_id)).slice(0,3);
 if(!rows.length){$("compare-chart").innerHTML='<p class="muted">비교할 모델을 선택하세요.</p>';return}
 const vals=rows.map(x=>x.score),min=Math.min(0,...vals),max=Math.max(...vals),range=max-min||1;
 $("compare-chart").innerHTML=rows.map((r,i)=>'<div class="barrow"><span class="name" title="'+safe(r.model)+'">'+safe(r.model)+'</span>'+
 '<div class="track"><div class="fill '+(i===1?"second":i===2?"third":"")+'" style="width:'+Math.max(2,Math.min(100,100*(r.score-min)/range))+'%"></div></div>'+
 '<strong>'+num(r.score)+'</strong></div>').join("")+'<small>동일 부문 '+safe(rows[0].unit)+
 ' 비교 · 평가 방법론이 다르면 비교하지 않습니다.</small>';
}
function renderTrend(){
 const current=ranked().filter(x=>chosen.includes(x.model_id)).slice(0,3),svg=$("trend-chart");
 if(history.length<2||!current.length){
  svg.innerHTML='<p class="muted">동일 평가의 서로 다른 주차 기록이 2회 이상 축적되면 추세가 나타납니다. 현재는 최초 기록 단계입니다.</p>';
  $("trend-summary").textContent="모델 간 변화는 공식 점수의 불확실성과 평가 방법론 변경을 함께 고려해야 합니다.";return;
 }
 const series=current.map(r=>({name:r.model,points:history.map((h,i)=>({i,week:h.week,r:(h.records||[]).find(x=>x.model_id===r.model_id&&x.category===r.category&&x.benchmark===r.benchmark&&x.version===r.version)})).filter(x=>x.r)}));
 const values=series.flatMap(s=>s.points.map(p=>p.r.score));
 if(!values.length){svg.innerHTML='<p class="muted">이 모델의 과거 기록이 없습니다.</p>';return}
 let lo=Math.min(...values),hi=Math.max(...values);let margin=(hi-lo)*.12||1;lo-=margin;hi+=margin;
 const x=i=>45+i*(580/Math.max(1,history.length-1));
 const y=v=>188-(v-lo)/(hi-lo)*155;
 let body='<svg viewBox="0 0 665 230" role="img" aria-label="주간 AI 성능 지표 추세">';
 for(let t=0;t<4;t++){let yy=188-t*155/3;body+='<line x1="45" y1="'+yy+'" x2="625" y2="'+yy+'" stroke="#30455f" stroke-width="1"/><text x="3" y="'+(yy+3)+'">'+num(lo+(hi-lo)*t/3)+'</text>'}
 series.forEach((s,i)=>{if(!s.points.length)return;body+='<polyline fill="none" stroke="'+cols[i]+'" stroke-width="3" points="'+s.points.map(p=>x(p.i)+","+y(p.r.score)).join(" ")+'"/>';
 s.points.forEach(p=>body+='<circle fill="'+cols[i]+'" cx="'+x(p.i)+'" cy="'+y(p.r.score)+'" r="4"><title>'+safe(s.name+" / "+p.week+": "+num(p.r.score))+'</title></circle>');
 });
 body+='<text x="45" y="218">'+safe(history[0].week)+'</text><text x="535" y="218">'+safe(history.at(-1).week)+'</text></svg>';
 body+='<div class="comparison-controls">'+series.map((s,i)=>'<span style="color:'+cols[i]+'">● '+safe(s.name)+'</span>').join(" · ")+'</div>';
 svg.innerHTML=body;
 $("trend-summary").textContent="동일 영역·모델의 주간 저장 기록 기준입니다. 1주 차에 여러 번 실행해도 1개 주차로 표시됩니다.";
}
function renderSources(){
 const states=status.sources||{};
 const entries=Object.entries(states);
 $("source-state").innerHTML=entries.length?entries.map(([key,val])=>{
  const ok=String(val).startsWith("OK");
  return '<div class="state '+(ok?"good":"bad")+'"><b>'+safe(key)+'</b><span>'+safe(val)+'</span></div>';
 }).join(""):'<p class="muted">공식 출처 상태가 없습니다.</p>';
}
function renderAll(){renderRanking();renderCompareOptions()}
function exportCSV(){
 const cols=["source","benchmark","category","rank","model","provider","score","unit","ci_low","ci_high","sample_count","publish_date","source_url","license"];
 const escapeCSV=v=>{let s=String(v??"");if(/^[=+@\-]/.test(s))s="'"+s;return '"'+s.replace(/"/g,'""')+'"';};
 const lines=[cols.join(",")].concat(ranked().map(r=>cols.map(k=>escapeCSV(r[k])).join(",")));
 const blob=new Blob(["\ufeff"+lines.join("\r\n")],{type:"text/csv;charset=utf-8"});
 const url=URL.createObjectURL(blob),anchor=document.createElement("a");anchor.href=url;anchor.download="arena-"+board+"-"+(status.week||"latest")+".csv";anchor.click();URL.revokeObjectURL(url);
}
async function init(){
 try{
  const stamp=Date.now();
  const [a,b]=await Promise.all([fetch("./data/history.json?v="+stamp,{cache:"no-store"}),fetch("./data/status.json?v="+stamp,{cache:"no-store"})]);
  if(!a.ok||!b.ok)throw Error("데이터 파일 HTTP 상태가 정상적이지 않습니다.");
  history=await a.json();status=await b.json();
  if(!Array.isArray(history))throw Error("기록 파일 형식 오류");
  history.sort((a,b)=>a.week.localeCompare(b.week));all=latest().records||[];
  if(!Array.isArray(all))throw Error("최신 스냅샷 형식 오류");
  renderStats();renderSources();selectBoard();
 }catch(error){$("notice").textContent="데이터를 불러오지 못했습니다: "+error.message;renderSources();}
}
$("board").addEventListener("change",()=>{board=$("board").value;category="";chosen=[];selectCategory()});
$("category").addEventListener("change",()=>{category=$("category").value;chosen=[];renderAll()});
$("search").addEventListener("input",()=>{term=$("search").value.trim();chosen=[];renderAll()});
$("export").addEventListener("click",exportCSV);
$("refresh").addEventListener("click",()=>location.reload());
init();
