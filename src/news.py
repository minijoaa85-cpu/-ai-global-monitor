"""Collect source-linked AI updates from publishers' public RSS/Atom feeds.

This is a *news monitor*, not a benchmark ranking or an AI-generated prediction.
We store links, dates, publisher titles and a short attributed feed description.
No full articles are copied. No unofficial Anthropic feed is mislabelled official.
"""
from __future__ import annotations
import datetime as dt
import email.utils
import html
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"site"/"data"/"news.json"
SOURCES=[
    ("OpenAI", "https://openai.com/news/rss.xml", "openai.com"),
    ("Google AI", "https://blog.google/innovation-and-ai/technology/ai/rss/", "blog.google"),
    ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml", "huggingface.co"),
    ("GitHub Copilot", "https://github.blog/changelog/all.atom", "github.blog"),
]
KEYWORDS=("model","gpt","chatgpt","gemini","claude","copilot","llm","reason","benchmark","agent","release","update","launch","api","coding","deepseek","performance","intelligence","frontier","openai","anthropic","google","search","vision","multimodal","code","inference","fast","efficien","tool")
NAMESPACE={"a":"http://www.w3.org/2005/Atom"}
TAG=re.compile(r"<[^>]*>")
SPACE=re.compile(r"\s+")

def clean(value,limit):
    text=html.unescape(TAG.sub(" ",value or ""))
    text=SPACE.sub(" ",text).strip()
    return text[:limit].rstrip()+"…" if len(text)>limit else text

def date_of(value):
    if not value:return None
    try:
        parsed=email.utils.parsedate_to_datetime(value)
        if parsed and parsed.tzinfo is None:parsed=parsed.replace(tzinfo=dt.timezone.utc)
        if parsed:return parsed.astimezone(dt.timezone.utc)
    except (ValueError,TypeError):pass
    try:
        return dt.datetime.fromisoformat(value.replace("Z","+00:00")).astimezone(dt.timezone.utc)
    except ValueError:return None

def category(title):
    t=title.lower()
    if any(k in t for k in ("benchmark","leaderboard","evaluation","performance","reasoning")):return "평가·성능"
    if any(k in t for k in ("launch","introducing","new model","release","available","announc","gpt-","gemini","claude","deepseek")):return "신모델·출시"
    if any(k in t for k in ("update","improv","upgrade","copilot","api","feature")):return "업데이트"
    return "연구·동향"

def describe(title,description,kind):
    excerpt=clean(description,160)
    if excerpt:return excerpt
    return {"신모델·출시":"새 모델·제품 공개 관련 공식 발표입니다. 세부 출시 조건은 원문을 확인하세요.",
            "평가·성능":"AI 평가 및 성능 관련 발표입니다. 방법론과 근거는 원문에서 확인하세요.",
            "업데이트":"서비스 또는 모델 기능 변경 관련 발표입니다. 변경 범위는 원문을 확인하세요."}.get(kind,"AI 업계 공식 소식입니다. 자세한 내용은 원문을 확인하세요.")

def korean_summary(title,source,kind):
    # Strict, title-based explanatory label: no fabricated benchmark gains or launch dates.
    t=title.lower()
    models=("GPT","ChatGPT","Claude","Gemini","DeepSeek","Grok","Copilot","Llama","Qwen","Mistral")
    hit=next((m for m in models if m.lower() in t),None)
    subject=hit+" 관련" if hit else "AI 관련"
    if kind=="신모델·출시":
        return "%s에서 %s 모델·제품 출시 또는 제공 확대 소식을 발표했습니다. 변경 범위와 제공 시점은 원문을 확인하세요."%(source,subject)
    if kind=="평가·성능":
        return "%s의 %s 평가·성능 관련 발표입니다. 실제 순위 및 비교 근거는 원문에서 확인하세요."%(source,subject)
    if kind=="업데이트":
        return "%s의 %s 기능·지원 범위 업데이트 소식입니다. 구체적인 변경 사항은 원문을 확인하세요."%(source,subject)
    return "%s에서 발표한 %s 연구·산업 동향입니다. 세부 내용과 근거는 원문을 확인하세요."%(source,subject)

def allowed_link(link,domain):
    try:
        p=urlsplit(link)
        return p.scheme=="https" and (p.hostname==domain or (p.hostname or "").endswith("."+domain))
    except ValueError:return False

def parse_feed(raw,name,source_url,domain,now):
    root=ET.fromstring(raw)
    result=[]
    is_atom=root.tag.endswith("feed")
    if is_atom:
        items=root.findall("a:entry",NAMESPACE)
    else:
        items=root.findall("./channel/item")
    for node in items:
        def field(label):
            x=node.find(("a:"+label) if is_atom else label,NAMESPACE if is_atom else None)
            return "".join(x.itertext()).strip() if x is not None else ""
        title=clean(field("title"),180)
        if not title:continue
        if name=="GitHub Copilot" and "copilot" not in title.lower():continue
        if name in ("Google AI","OpenAI","Hugging Face Blog") and not any(k in title.lower() for k in KEYWORDS):continue
        link=field("link")
        if is_atom:
            for atom_link in node.findall("a:link",NAMESPACE):
                if atom_link.attrib.get("rel","alternate")=="alternate":
                    link=atom_link.attrib.get("href","");break
        if not allowed_link(link,domain):continue
        date=date_of(field("updated") or field("published") or field("pubDate"))
        if not date or date>now or date<now-dt.timedelta(days=21):continue
        kind=category(title)
        description=field("summary") or field("description")
        result.append(dict(source=name,title=title,summary=describe(title,description,kind),
            summary_ko=korean_summary(title,name,kind),
            url=link,category=kind,published_at=date.isoformat(),published_day=date.date().isoformat()))
    return result

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"AI-Observatory-News/1.0 (public RSS reader)","Accept":"application/atom+xml, application/rss+xml, application/xml, text/xml"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        return resp.read(1_500_000)

def main():
    now=dt.datetime.now(dt.timezone.utc)
    items,states=[],{}
    for name,url,domain in SOURCES:
        try:
            feed=fetch(url)
            found=parse_feed(feed,name,url,domain,now)
            if not found:raise ValueError("No relevant recent feed entries")
            items.extend(found[:10])
            states[name]="OK: %d recent links"%len(found)
        except Exception as ex:
            states[name]="ERROR: "+str(ex)[:160]
        time.sleep(0.4)
    dedup={}
    for item in items:dedup[item["url"].split("?")[0]]=item
    result=sorted(dedup.values(),key=lambda x:x["published_at"],reverse=True)[:36]
    # Preserve previous valid links during a temporary outage; label as stale.
    if not result and DEST.exists():
        try:
            old=json.loads(DEST.read_text(encoding="utf-8"))
            result=[dict(r,stale=True) for r in old.get("items",[]) if r.get("url")]
        except (OSError,ValueError):pass
    payload=dict(updated_at=now.isoformat(),items=result,sources=states,
                 policy="Source titles and short feed excerpts only; open the publisher URL for full details.",
                 note="These releases can inform future rankings but are NOT performance forecasts.")
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"updated_at":payload["updated_at"],"items":len(result),"sources":states},ensure_ascii=False))
    if not result:raise SystemExit("No recent news available: check source errors")

if __name__=="__main__":main()
