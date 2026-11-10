"""V4 collector. Publishes only CC BY 4.0 Arena official leaderboard data.

Artificial Analysis Free API is for INTERNAL use only and must not be
republished to this public GitHub Pages repository. AA_API_KEY stays in
GitHub Secrets but is deliberately not accessed by this public collector.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"
API = "https://datasets-server.huggingface.co/rows"
DATASET = "lmarena-ai/leaderboard-dataset"
ARENA = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset"
# Source-defined leaderboards; avoid blending ratings across categories.
CONFIGS = ("text", "text_style_control", "webdev", "search", "vision", "document", "agent")
HEADERS = {"User-Agent": "AI-Global-Monitor/4.0 (public benchmark dashboard)"}
MAX_PAGES = 1
PAGE_SIZE = 100

def http_json(url: str) -> dict:
    error = None
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers=HEADERS), timeout=45) as res:
                return json.load(res)
        except Exception as exc:
            error = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    raise RuntimeError(str(error))

def numeric(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
        if not -1e12 < number < 1e12 or number != number:
            return None
        return round(number, 6)
    except (ValueError, TypeError):
        return None

def convert_arena_row(row, config):
    """Keep official rank, uncertainty, and source publication date."""
    if not isinstance(row, dict):
        return None
    model = row.get("model_name")
    score_field = "score" if config == "agent" else "rating"
    score = numeric(row.get(score_field))
    if not isinstance(model, str) or not model.strip() or score is None:
        return None
    low_field = "score_ci_lower" if config == "agent" else "rating_lower"
    high_field = "score_ci_upper" if config == "agent" else "rating_upper"
    rank = row.get("rank")
    try:
        rank = int(rank) if rank is not None else None
    except (ValueError, TypeError):
        rank = None
    if rank is not None and rank < 1:
        rank = None
    date = str(row.get("leaderboard_publish_date") or "").split("T")[0][:10]
    category = str(row.get("category") or "overall")
    if category.lower() in ("nan", "none"):
        category = "overall"
    return {
        "source": "Arena", "benchmark": config, "category": category,
        "model": model.strip(),
        "model_id": config + ":" + model.strip().lower(),
        "provider": str(row.get("organization") or "Unknown"),
        "score": score, "unit": "IPS" if config == "agent" else "Arena rating",
        "rank": rank, "ci_low": numeric(row.get(low_field)),
        "ci_high": numeric(row.get(high_field)),
        "sample_count": int(row.get("observation_count") or 0) if config == "agent" else int(row.get("vote_count") or 0),
        "publish_date": date, "source_url": ARENA,
        "license": "CC BY 4.0", "higher_is_better": True,
        "version": config, "rating_method": "IPS" if config == "agent" else "Bradley-Terry",
    }

def get_config(config):
    results = []
    offset = 0
    total = None
    for _ in range(MAX_PAGES):
        params = urlencode(dict(dataset=DATASET, config=config, split="latest",
                                offset=offset, length=PAGE_SIZE))
        response = http_json(API + "?" + params)
        rows = response.get("rows", [])
        if not isinstance(rows, list):
            raise ValueError("Invalid dataset rows shape")
        for entry in rows:
            parsed = convert_arena_row(entry.get("row", {}), config)
            if parsed:
                results.append(parsed)
        total = response.get("num_rows_total", total)
        offset += len(rows)
        if not rows or (isinstance(total, int) and offset >= total) or len(rows) < PAGE_SIZE:
            break
    if not results:
        raise ValueError("No usable models in latest split")
    # Latest split sampled up to 100 rows per category to respect public API rate limits.
    # IMPORTANT: this is a partial leaderboard, not the complete official ranking.
    # Most recently published rows per model/category, when a config has duplicates.
    best = {}
    for row in results:
        key = (row["model_id"], row["category"])
        if key not in best or row["publish_date"] > best[key]["publish_date"]:
            best[key] = row
    return list(best.values())

def main():
    DATA.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    today = now.date()
    monday = (today - dt.timedelta(days=today.weekday())).isoformat()
    sources, records = {}, []
    previous = []
    try:
        snapshots = json.loads((DATA / "history.json").read_text(encoding="utf-8"))
        if isinstance(snapshots, list):
            for snapshot in reversed(snapshots):
                candidate = snapshot.get("records", [])
                if any(r.get("source") == "Arena" and r.get("license") == "CC BY 4.0" for r in candidate):
                    previous = candidate
                    break
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    fresh_count = 0
    stale_count = 0
    for config in CONFIGS:
        label = "Arena / " + config
        try:
            data = get_config(config)
            records.extend(data)
            fresh_count += len(data)
            sources[label] = "OK: %d fresh rows" % len(data)
        except Exception as exc:
            old = [dict(r, stale=True) for r in previous
                   if r.get("source") == "Arena" and r.get("benchmark") == config
                   and r.get("license") == "CC BY 4.0"]
            records.extend(old)
            stale_count += len(old)
            sources[label] = ("ERROR: %s (retained %d stale rows)" %
                              (str(exc)[:160], len(old)))
    sources["Artificial Analysis"] = "INTERNAL ONLY: Free API redistribution restricted; not published"
    sources["LiveBench"] = "NOT ENABLED: license/schema verification pending"
    path = DATA / "history.json"
    try:
        history = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(history, list):
            history = []
    except (OSError, ValueError):
        history = []
    # Rebuild from sources we are legally authorized to publish; old AA data
    # is intentionally not copied into new public snapshots.
    history = [h for h in history if h.get("week") != monday]
    history = [{
        "week": h["week"], "collected_at": h.get("collected_at"),
        "records": [r for r in h.get("records", [])
                    if r.get("source") == "Arena" and r.get("license") == "CC BY 4.0"]
    } for h in history if isinstance(h, dict) and h.get("week")]
    if records:
        history.append(dict(week=monday, collected_at=now.isoformat(), records=records))
    history = sorted(history, key=lambda h: h["week"])[-104:]
    status = {
        "version": "4.0", "week": monday, "collected_at": now.isoformat(),
        "sources": sources, "published_records": len(records),
        "fresh_records": fresh_count, "stale_records": stale_count,
        "license_note": "Arena CC BY 4.0; each leaderboard is a partial sample (up to 100 rows) of the latest split. AA Free API is not published.",
    }
    path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA / "status.json").write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    print("Published Arena rows:", len(records))
    # An entirely failed official source pull should fail the Action, rather than
    # silently showing the previous data as fresh.
    if not fresh_count:
        raise SystemExit("No fresh benchmark records collected; see source errors.")

if __name__ == "__main__":
    main()
