"""Official-source weekly AI benchmark collector. Python 3.12 standard library."""
import datetime as dt
import json
import os
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"
AA_URL = "https://artificialanalysis.ai/api/v2/language/models/free"
HF_URL = "https://huggingface.co/api/datasets/{}/leaderboard"
LIVE_URL = "https://api.github.com/repos/LiveBench/new-livebench/contents/public"
HEADERS = {"User-Agent": "AI-Global-Monitor/1.0", "Accept": "application/json"}

def fetch(url, headers=None):
    request = urllib.request.Request(url, headers={**HEADERS, **(headers or {})})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)

def nested(obj, path):
    for key in path.split("."):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj

def number(v):
    if isinstance(v, bool) or v is None:
        return None
    try:
        n = float(v)
        if n != n or abs(n) > 1e12:
            return None
        return round(n, 6)
    except (TypeError, ValueError):
        return None

def record(source, benchmark, model, model_id, provider, score, url,
           version="published", unit="score", higher=True):
    n = number(score)
    if not model or n is None:
        return None
    return dict(source=source, benchmark=benchmark, model=str(model),
                model_id=str(model_id or model), provider=str(provider or "Unknown"),
                score=n, source_url=url, version=str(version), unit=unit,
                higher_is_better=higher)

def artificial_analysis():
    key = os.getenv("AA_API_KEY", "").strip()
    if not key:
        return [], "SKIPPED: AA_API_KEY not set"
    data = fetch(AA_URL, {"x-api-key": key})
    models = data.get("data", [])
    if not isinstance(models, list):
        raise ValueError("Unexpected Artificial Analysis schema")
    specs = [
        ("Intelligence Index", ["evaluations.artificial_analysis_intelligence_index", "evaluations.intelligence_index"], "index", True),
        ("Coding Agent Index", ["evaluations.artificial_analysis_coding_agent_index", "evaluations.coding_agent_index"], "index", True),
        ("Agentic Index", ["evaluations.artificial_analysis_agentic_index", "evaluations.agentic_index"], "index", True),
        ("Median output speed", ["median_output_tokens_per_second"], "tokens/sec", True),
        ("Input price / 1M tokens", ["pricing.price_1m_input_tokens", "pricing.input_price_per_million_tokens"], "USD/1M tokens", False),
        ("Output price / 1M tokens", ["pricing.price_1m_output_tokens", "pricing.output_price_per_million_tokens"], "USD/1M tokens", False),
    ]
    rows = []
    for model in models:
        if not isinstance(model, dict):
            continue
        maker = model.get("model_creator") or {}
        provider = maker.get("name") if isinstance(maker, dict) else str(maker)
        for metric, paths, unit, higher in specs:
            value = next((x for p in paths if (x := nested(model, p)) is not None), None)
            r = record("Artificial Analysis", metric, model.get("name"),
                       model.get("id") or model.get("slug"), provider, value,
                       "https://artificialanalysis.ai/", "provider-current", unit, higher)
            if r:
                rows.append(r)
    if not rows:
        raise ValueError("No recognized evaluation metrics in response")
    return rows, "OK: %d records" % len(rows)

def huggingface():
    targets = os.getenv("HF_BENCHMARK_DATASETS", "").strip()
    if not targets:
        return [], "SKIPPED: HF_BENCHMARK_DATASETS not configured"
    rows = []
    for target in targets.split(","):
        target = target.strip()
        if not target:
            continue
        data = fetch(HF_URL.format(target))
        entries = data if isinstance(data, list) else (data.get("leaderboard") or data.get("entries") or data.get("results") or [])
        if isinstance(entries, dict):
            entries = entries.get("entries") or entries.get("results") or []
        if not isinstance(entries, list):
            raise ValueError("Unexpected HF leaderboard format for " + target)
        for item in entries:
            if not isinstance(item, dict):
                continue
            model = item.get("model_id") or item.get("model") or item.get("id")
            if isinstance(model, dict):
                model = model.get("id") or model.get("name")
            metric = item.get("metric_name") or item.get("metric") or "Published score"
            if isinstance(metric, dict):
                metric = metric.get("name") or "Published score"
            score = next((item.get(k) for k in ("score", "value", "metric_value", "primary_score") if item.get(k) is not None), None)
            r = record("Hugging Face", target + " · " + str(metric), model, model,
                       str(model).split("/")[0] if model else "", score,
                       "https://huggingface.co/datasets/" + target)
            if r:
                rows.append(r)
    if not rows:
        raise ValueError("No HF rows found; check source leaderboard endpoint")
    return rows, "OK: %d records" % len(rows)

def livebench():
    # Discovery only: GitHub repository content layout can change. Avoid fabricating results.
    if os.getenv("ENABLE_LIVEBENCH", "0") != "1":
        return [], "SKIPPED: LiveBench adapter disabled"
    response = fetch(LIVE_URL)
    if not isinstance(response, list):
        raise ValueError("LiveBench directory schema changed")
    return [], "NOT MAPPED: official public directory found; versioned score parser required"

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    week = now.date().isoformat()
    statuses, records = {}, []
    for name, fn in (("Artificial Analysis", artificial_analysis),
                     ("Hugging Face", huggingface),
                     ("LiveBench", livebench)):
        try:
            rows, state = fn()
            records.extend(rows)
            statuses[name] = state
        except Exception as ex:
            statuses[name] = "ERROR: " + str(ex)[:250]
    # If a source fails, retain the prior working data for that same source but never
    # display it as though fresh. Status makes freshness explicit.
    path = DATA / "history.json"
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            history = []
    except (OSError, ValueError):
        history = []
    history = [x for x in history if x.get("week") != week]
    history.append({"week": week, "collected_at": now.isoformat(), "records": records})
    history = sorted(history, key=lambda x: x["week"])[-104:]
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    status = {"week": week, "collected_at": now.isoformat(), "sources": statuses}
    (DATA / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    print("Collected records:", len(records))

if __name__ == "__main__":
    main()
