"""V4 published weekly overview: only Arena's CC BY 4.0 records."""
import datetime as dt
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site"/"data"
history=json.loads((DATA/"history.json").read_text(encoding="utf-8"))
status=json.loads((DATA/"status.json").read_text(encoding="utf-8"))
latest=history[-1] if history else {"records":[],"week":"—"}
rows=[r for r in latest.get("records",[]) if r.get("source")=="Arena"]
prev=history[-2].get("records",[]) if len(history)>1 else []
past={(r.get("benchmark"),r.get("category"),r.get("model_id"),r.get("version")):r
      for r in prev}
groups=defaultdict(list)
for r in rows:
    groups[(r.get("benchmark","?"),r.get("category","overall"))].append(r)
css="""body{max-width:1060px;margin:auto;padding:22px;background:#0b1222;color:#edf3fe;font:15px/1.5 system-ui,sans-serif}a{color:#a5caff}header,section{padding:20px;margin:14px 0;border:1px solid #30415a;border-radius:16px;background:#142137}table{width:100%;border-collapse:collapse}td,th{padding:9px;text-align:left;border-bottom:1px solid #34455f}th{color:#9eafc8}.muted{color:#aab9ce}h1{font-size:30px}h2{font-size:21px}section{overflow-x:auto}"""
line=['<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
      '<title>Global AI Observatory · Weekly Report</title>','<style>'+css+'</style><header>',
      '<p><a href="./index.html">← 관측소 대시보드</a></p>',
      '<h1>글로벌 AI 주간 평가 리포트</h1>',
      '<p>관측 주차: '+html.escape(str(latest.get("week")))+
      ' · 수집: '+html.escape(str(status.get("collected_at","—")))+ '</p>',
      '<p class="muted">공식 Arena 데이터 제공: CC BY 4.0. 동일 벤치마크·카테고리의 이전 주차 점수와만 비교합니다.</p>',
      '</header><section><h2>수집 요약</h2><p>공개 가능한 Arena 레코드: '+str(len(rows))+'건 · 평가 영역: '+str(len(groups))+'개</p>']
for k,v in status.get("sources",{}).items():
    line.append('<p>'+html.escape(k)+': '+html.escape(str(v))+'</p>')
line.append('</section>')
if not rows:
    line.append('<section><p>실제 공개 평가 데이터를 수집하지 못했습니다. 자동화 오류 로그를 확인하세요.</p></section>')
for (board,category),items in sorted(groups.items()):
    items.sort(key=lambda r:(r.get("rank") is None,r.get("rank") or 999999,-r["score"]))
    line.append('<section><h2>'+html.escape(board)+' / '+html.escape(category)+'</h2>')
    line.append('<p class="muted">공식 발표 순위 · 일부 행만 수집됐을 수 있으며 전체 순위를 대표하지 않을 수 있습니다.</p>')
    line.append('<table><tr><th>공식 순위</th><th>모델</th><th>점수</th><th>전주 대비</th><th>95% 신뢰구간</th></tr>')
    for r in items[:10]:
        key=(r.get("benchmark"),r.get("category"),r.get("model_id"),r.get("version"))
        earlier=past.get(key)
        delta=round(r["score"]-earlier["score"],3) if earlier else None
        ci="—" if r.get("ci_low") is None or r.get("ci_high") is None else str(r["ci_low"])+" – "+str(r["ci_high"])
        line.append('<tr><td>'+html.escape(str(r.get("rank") or "—"))+'</td><td>'+
                    html.escape(str(r["model"]))+'</td><td>'+html.escape(str(r["score"]))+
                    '</td><td>'+("—" if delta is None else ("+" if delta>0 else "")+str(delta))+
                    '</td><td>'+html.escape(ci)+'</td></tr>')
    line.append('</table></section>')
line.append('<footer><p><a href="https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset">Original Arena leaderboard dataset · CC BY 4.0</a>. Scientific interpretation requires attention to sample sizes, confidence intervals, and methodology changes.</p><p>Artificial Analysis Free API data is not redistributed here.</p></footer></html>')
(ROOT/"site"/"weekly-report.html").write_text("\n".join(line)+"\n",encoding="utf-8")
print("V4 report:",len(rows),"Arena records in",len(groups),"leaderboard slices")
