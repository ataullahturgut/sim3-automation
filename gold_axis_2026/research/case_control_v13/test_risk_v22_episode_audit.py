import unittest,json
from pathlib import Path
import pandas as pd
O=Path(__file__).parent/"outputs"
class StrictEpisodeAudit(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.ep=pd.read_csv(O/"v22_alarm_episodes.csv")
  cls.m=pd.read_csv(O/"v22_episode_sensitivity.csv")
  cls.flags=json.loads((O/"v22_episode_caveat.json").read_text())
 def test_do_not_confuse_signal_day_with_independent_event(self):
  self.assertEqual(set(self.m.gap_days),{4,6,10})
  for _,r in self.m.iterrows():
   self.assertEqual(r.episodes_total,r.episodes_true10+r.episodes_false10+r.episodes_unknown10)
 def test_2024_does_not_improve_false_episode_count(self):
  q=self.m[(self.m.year==2024)&(self.m.gap_days==4)].set_index("policy")
  self.assertEqual(q.loc["BASE14_ORIGINAL_RED","episodes_false10"],4)
  self.assertEqual(q.loc["V22_ACTIVE_RED_ONLY","episodes_false10"],4)
  self.assertEqual(q.loc["V22_PRIORITIZED_PLUS_WATCH","episodes_false10"],7)
  self.assertTrue(self.flags["2024_composite_review_episodes_increased_due_to_nonred_watches"])
 def test_future_horizon_is_censored(self):
  q=self.m[(self.m.year==2026)&(self.m.gap_days==4)].set_index("policy")
  self.assertEqual(q.loc["BASE14_ORIGINAL_RED","episodes_unknown10"],1)
  self.assertEqual(q.loc["V22_ACTIVE_RED_ONLY","episodes_unknown10"],0)
 def test_false_episode_counts_are_distinct_from_false_days(self):
  q=self.m[(self.m.year==2026)&(self.m.gap_days==4)].set_index("policy")
  self.assertEqual(q.loc["BASE14_ORIGINAL_RED","episodes_false10"],3)
  self.assertEqual(q.loc["V22_ACTIVE_RED_ONLY","episodes_false10"],2)
  self.assertFalse(self.ep.never_inferred_intraday.eq(False).any())
if __name__=="__main__":unittest.main(verbosity=2)
