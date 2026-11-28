"""Rules that keep weekly headlines grounded in matching benchmark data."""
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from weekly_brief import digest, matched_changes

NOW=datetime(2026,11,28,0,0,tzinfo=timezone.utc)
def row(model,score,board="text",version="text",rank=3):
 return {"source":"Arena","model":model,"model_id":board+model,
 "benchmark":board,"category":"overall","version":version,
 "score":score,"rank":rank,"unit":"Arena rating","rating_method":"Bradley-Terry"}
def news(title,kind):
 return {"source":"OpenAI","title":title,"category":kind,
 "url":"https://openai.com/index/example","published_at":"2026-11-27T10:00:00+00:00"}
class BriefTests(unittest.TestCase):
 def test_mismatched_benchmark_not_compared(self):
  self.assertEqual(matched_changes([row("A",100)],[row("A",110,board="vision")]),[])
 def test_stale_excluded(self):
  recent=row("A",112);recent["stale"]=True
  self.assertEqual(matched_changes([row("A",100)],[recent]),[])
 def test_headline_reports_only_available_data(self):
  history=[{"week":"2026-11-16","records":[row("A",101)]},
   {"week":"2026-11-23","records":[row("A",110)]}]
  r=digest(history,{"items":[news("New AI update","업데이트")]},
    {"collected_at":"2026-11-23T01:00:00+00:00"},NOW)
  self.assertEqual(r["benchmark_week"],"2026-11-23")
  self.assertEqual(r["benchmark_records"],1)
  self.assertEqual(r["weekly_news_count"],1)
  self.assertIn("업데이트",r["headline"])
  self.assertTrue(any("상승" in v for v in r["insights"]))
 def test_no_previous_week_does_not_claim_rank_change(self):
  a=digest([{"week":"2026-11-23","records":[row("A",100)]}],
   {"items":[]},{"collected_at":"2026-11-23T00:00:00+00:00"},NOW)
  self.assertIn("전주 비교 자료 없음",a["quality_flags"])
  self.assertTrue(any("보류" in s for s in a["insights"]))
 def test_previous_empty_snapshot_ignored(self):
  h=[{"week":"2026-11-23","records":[row("A",100)]},{"week":"2026-11-24","records":[]}]
  a=digest(h,{"items":[]},{},NOW)
  self.assertEqual(a["benchmark_week"],"2026-11-23")
 def test_future_news_excluded(self):
  n=news("Future release","신모델·출시");n["published_at"]="2026-12-01T00:00:00+00:00"
  a=digest([{"week":"2026-11-23","records":[row("A",100)]}],
    {"items":[n]}, {},NOW)
  self.assertEqual(a["weekly_news_count"],0)
if __name__=="__main__":unittest.main()
