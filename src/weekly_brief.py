"""Evidence-bound weekly briefing for the top of the AI Observatory.

Produces one concise Korean headline + three insight lines from the public Arena
weekly snapshots and publisher RSS articles. No speculative performance claim,
no comparisons between different benchmark methodologies, and no paid LLM needed.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site"/"data"
SOURCES={"OpenAI","Google AI","GitHub Copilot","Hugging Face Blog"}
LABELS={"text":"텍스트","text_style_control":"텍스트(스타일 보정)","webdev":"웹 개발",
        "search":"검색","vision":"시각 이해","document":"문서 이해","agent":"에이전트"}
CATEGORIES={"신모델·출시":"신모델·출시","업데이트":"기능 업데이트",
            "평가·성능":"평가·성능","연구·동향":"연구·동향"}

def parse_dt(value):
    try:
        if not value:return None
        return datetime.fromisoformat(str(value).replace("Z","+00:00")).astimezone(timezone.utc)
    except (TypeError,ValueError):return None

def safe_latest(history):
    valid=[h for h in history if isinstance(h,dict) and isinstance(h.get("records"),list)
           and any(r.get("source")=="Arena" and not r.get("stale") for r in h["records"])]
    valid.sort(key=lambda h:h.get("week",""))
    return valid[-2:]

def matched_changes(old_rows,new_rows):
    previous={(r.get("benchmark"),r.get("category"),r.get("version"),r.get("model_id")):r
              for r in old_rows if r.get("source")=="Arena" and not r.get("stale")}
    result=[]
    for r in new_rows:
        if r.get("source")!="Arena" or r.get("stale"):continue
        key=(r.get("benchmark"),r.get("category"),r.get("version"),r.get("model_id"))
        before=previous.get(key)
        if not before:continue
        if not isinstance(r.get("score"),(int,float)) or not isinstance(before.get("score"),(int,float)):continue
        if before.get("rating_method")!=r.get("rating_method"):continue
        diff=r["score"]-before["score"]
        if not diff:continue
        rank1=before.get("rank")
        rank2=r.get("rank")
        rank_change=(rank1-rank2) if isinstance(rank1,int) and isinstance(rank2,int) else None
        result.append({"model":str(r.get("model") or "Unknown"),"board":str(r.get("benchmark") or ""),
                       "category":str(r.get("category") or "overall"),"delta":round(diff,3),
                       "rank_change":rank_change,"unit":str(r.get("unit") or "points")})
    return result

def digest(history, news, status, now=None):
    now=now or datetime.now(timezone.utc)
    snapshots=safe_latest(history)
    latest=snapshots[-1] if snapshots else {}
    records=[r for r in latest.get("records",[]) if r.get("source")=="Arena"]
    latest_date=latest.get("week") or "미수집"
    previous=snapshots[-2] if len(snapshots)>=2 else None
    old=previous.get("records",[]) if previous else []
    changes=matched_changes(old,records)
    total_changed=len(changes)
    categories=Counter()
    recent=[]
    for x in news.get("items",[]):
        if x.get("source") not in SOURCES:continue
        stamp=parse_dt(x.get("published_at"))
        if not stamp or stamp>now or stamp<now-timedelta(days=7):continue
        categories[x.get("category","연구·동향")]+=1
        recent.append(x)
    recent.sort(key=lambda x:x.get("published_at",""),reverse=True)
    top_categories=sorted(categories.items(),key=lambda x:(-x[1],x[0]))
    headlines=[x for x in recent if x.get("category") in ("신모델·출시","업데이트","평가·성능")][:3]
    latest_models=len({r.get("model") for r in records if r.get("model")})
    boards=len({r.get("benchmark") for r in records if r.get("benchmark")})
    stale_age=(now-parse_dt(status.get("collected_at"))).days if parse_dt(status.get("collected_at")) else None
    remarks=[]
    if top_categories:
        label=CATEGORIES.get(top_categories[0][0],top_categories[0][0])
        remarks.append(f"공식 링크 기준 최근 7일은 {label} 기사 {top_categories[0][1]}건이 가장 많이 수집됐습니다. 수집량은 업계 전체 관심도를 대표하지 않습니다.")
    else:
        remarks.append("최근 7일 내 검증된 공식 뉴스 링크가 없어 주목 분야를 판단하지 않았습니다.")
    if previous:
        if changes:
            up=sum(1 for x in changes if x["delta"]>0)
            down=sum(1 for x in changes if x["delta"]<0)
            remarks.append(f"동일 모델·평가 조건에서 확인된 점수 변동은 상승 {up}건, 하락 {down}건(합계 {total_changed}건)입니다. 점수 변화만으로 통계적 우위를 판단할 수 없습니다.")
        else:
            remarks.append("직전 주와 조건이 일치하는 점수 변화가 없어 상승·하락 판단을 보류했습니다.")
    else:
        remarks.append("비교 가능한 직전 주 자료가 없어 모델별 상승·하락 분석은 보류했습니다.")
    if headlines:
        item=headlines[0]
        remarks.append(f"최근 공식 발표: {item['source']}의 ‘{item['title'][:85]}’ 관련 세부 사항은 원문을 확인하세요.")
    else:
        remarks.append("신규 모델과 기능 업데이트 발표는 아래 원문 뉴스 보드에서 확인할 수 있습니다.")
    if not records:
        heading="이번 주 공식 평가 스냅샷이 확인되지 않았습니다."
    elif top_categories:
        heading=f"이번 주는 {CATEGORIES.get(top_categories[0][0],top_categories[0][0])} 소식이 두드러졌으며, Arena {boards}개 평가 영역의 최신 공개 점수를 확인했습니다."
    else:
        heading=f"Arena {boards}개 평가 영역의 최신 공개 점수를 확인했으며, 뉴스 변화는 확인된 기사에 한해 해석합니다."
    quality=[]
    if stale_age is not None and stale_age>=10:quality.append("벤치마크 수집 후 10일 이상 경과")
    if not previous:quality.append("전주 비교 자료 없음")
    if len(recent)<3:quality.append("최근 7일 공식 뉴스 표본 부족")
    return {"schema_version":1,"generated_at":now.isoformat(),"benchmark_week":latest_date,
      "latest_model_count":latest_models,"benchmark_records":len(records),"benchmark_boards":boards,
      "weekly_news_count":len(recent),"headline":heading,"insights":remarks,"quality_flags":quality,
      "top_news":[{"source":x.get("source"),"title":x.get("title"),"url":x.get("url"),
                   "published_at":x.get("published_at")} for x in headlines],
      "benchmark_source_url":"https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
      "scope":"공식 공개 데이터에 대한 규칙 기반 관측 요약. 관심도·미래 순위 예측 또는 인과관계 주장 아님."}

def read(path,default):
    try:return json.loads(path.read_text(encoding="utf-8"))
    except (OSError,ValueError):return default

def main():
    history=read(DATA/"history.json",[])
    news=read(DATA/"news.json",{})
    status=read(DATA/"status.json",{})
    output=digest(history,news,status)
    (DATA/"weekly_brief.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"week":output["benchmark_week"],"models":output["latest_model_count"],
        "news":output["weekly_news_count"],"quality":output["quality_flags"]},ensure_ascii=False))

if __name__=="__main__":main()
