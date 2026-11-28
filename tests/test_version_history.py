"""Guard release history parity with PSI Radar's single-source workflow."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HISTORY=ROOT/"site"/"version_history.json"
HTML=ROOT/"site"/"index.html"
JAVASCRIPT=ROOT/"site"/"history.js"
BUILD=ROOT/"scripts"/"build_history_slides.py"
class ReleaseHistoryTests(unittest.TestCase):
 def test_reviewed_entries(self):
  d=json.loads(HISTORY.read_text(encoding="utf-8"))
  self.assertEqual(d["schema_version"],1)
  entries=d["entries"]
  self.assertGreaterEqual(len(entries),5)
  self.assertEqual(d["latest_version"],entries[-1]["version"])
  self.assertEqual(len(set(x["version"] for x in entries)),len(entries))
  for x in entries:
   for key in ("version","title","date","summary","background","changes","value","ref"):
    self.assertGreaterEqual(len(str(x[key])),4,(x["version"],key))
   self.assertTrue(x["ref"].startswith("https://github.com/"))
 def test_history_interface(self):
  html=HTML.read_text(encoding="utf-8")
  js=JAVASCRIPT.read_text(encoding="utf-8")
  for mark in ('id="history-drawer"','id="history-list"','id="history-filter"',
      'id="history-close"','id="history-current-version"',
      'docs/ai-observatory-version-history.pdf',
      'docs/ai-observatory-version-history.pptx'):
   self.assertIn(mark,html)
  self.assertIn("version_history.json",js)
  self.assertIn("e.background",js)
  self.assertIn("e.changes",js)
  self.assertIn("e.value",js)
 def test_both_downloads_from_same_json(self):
  src=BUILD.read_text(encoding="utf-8")
  self.assertIn('site"/"version_history.json"',src)
  for ext in ("pdf","pptx"):
   self.assertIn("ai-observatory-version-history."+ext,src)
 def test_news_and_benchmark_unchanged(self):
  self.assertTrue((ROOT/"site"/"news.js").exists())
  self.assertTrue((ROOT/"src"/"monitor.py").exists())
  self.assertTrue((ROOT/"src"/"news.py").exists())
if __name__=="__main__":unittest.main()
