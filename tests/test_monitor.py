import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from monitor import numeric,convert_arena_row

class ArenaValidation(unittest.TestCase):
    def test_text_row(self):
        r=convert_arena_row(dict(model_name="Test Model",organization="test-org",
          rating=1420,rating_lower=1400,rating_upper=1440,rank=2,vote_count=125,
          category="overall",leaderboard_publish_date="2026-11-08"),"text")
        self.assertEqual(r["source"],"Arena")
        self.assertEqual(r["rank"],2)
        self.assertEqual(r["ci_low"],1400)
        self.assertEqual(r["sample_count"],125)
        self.assertEqual(r["license"],"CC BY 4.0")
    def test_agent_score(self):
        r=convert_arena_row(dict(model_name="Agent One",score=.12,
          score_ci_lower=.10,score_ci_upper=.14,rank=3,observation_count=300),"agent")
        self.assertEqual(r["rating_method"],"IPS")
        self.assertEqual(r["score"],.12)
    def test_missing_score_not_zero(self):
        self.assertIsNone(convert_arena_row(dict(model_name="Unknown"),"text"))
    def test_no_boolean_score(self):
        self.assertIsNone(numeric(True))
    def test_no_nan(self):
        self.assertIsNone(numeric("nan"))
    def test_version_identity(self):
        a=convert_arena_row(dict(model_name="same",rating=3),"text")
        b=convert_arena_row(dict(model_name="same",rating=3),"webdev")
        self.assertNotEqual(a["model_id"],b["model_id"])

if __name__=="__main__": unittest.main()
