"""Fixture tests for official RSS and Atom parser. No live API required."""
import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from news import parse_feed,allowed_link,category,clean,describe

NOW=dt.datetime(2026,11,11,6,0,tzinfo=dt.timezone.utc)
RSS=b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Publisher</title><item><title>Introducing GPT Test 7</title>
<link>https://openai.com/news/example</link><description>New model with expanded tool support.</description>
<pubDate>Tue, 10 Nov 2026 10:00:00 GMT</pubDate></item></channel></rss>"""
ATOM=b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Copilot model update</title>
<link href="https://github.blog/changelog/copilot-new" rel="alternate"/>
<updated>2026-11-11T00:01:00Z</updated><summary>Copilot adds new model support.</summary>
</entry></feed>"""

class TestNews(unittest.TestCase):
 def test_rss(self):
  data=parse_feed(RSS,"OpenAI","https://openai.com/news/rss.xml","openai.com",NOW)
  self.assertEqual(len(data),1)
  self.assertEqual(data[0]["category"],"신모델·출시")
  self.assertEqual(data[0]["url"],"https://openai.com/news/example")
  self.assertIn("expanded tool support",data[0]["summary"])
 def test_atom(self):
  data=parse_feed(ATOM,"GitHub Copilot","https://github.blog/changelog/all.atom","github.blog",NOW)
  self.assertEqual(len(data),1)
  self.assertEqual(data[0]["source"],"GitHub Copilot")
 def test_reject_domain(self):
  self.assertFalse(allowed_link("https://github.blog.evil.example/abc","github.blog"))
  self.assertFalse(allowed_link("javascript:alert(1)","github.blog"))
 def test_classify(self):
  self.assertEqual(category("Introducing Gemini New"),"신모델·출시")
 def test_clean_html(self):
  self.assertEqual(clean("<b>Hello</b>   world",100),"Hello world")
 def test_no_fabricated_summary(self):
  self.assertIn("원문",describe("News item","","연구·동향"))

if __name__=="__main__":unittest.main()
