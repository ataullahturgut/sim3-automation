"""V18 genuine replay acceptance; preserve base red, show 2025/2026 tradeoff."""
import unittest,json
from pathlib import Path
import numpy as np
import pandas as pd
D=Path(__file__).parent/"outputs"

class ActualV18Study(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.day=pd.read_csv(D/"v18_daily_business_intelligence.csv")
  cls.m=pd.read_csv(D/"v18_2025_2026_same_day_replay.csv")
  cls.original=pd.read_csv(D/"v16_bi_daily.csv")
  cls.audit=json.loads((D/"v18_audit.json").read_text())

 def test_dont_change_existing_red_or_scores(self):
  b=self.original[self.original.model=="BASE14"].sort_values("origin")
  a=self.day.sort_values("origin")
  np.testing.assert_array_equal(a.origin,b.origin)
  np.testing.assert_array_equal(a.alert_level,b.alert_level)
  np.testing.assert_array_equal(a.risk_score,b.risk_score)
  self.assertTrue(a.BI_does_not_change_original_alert.all())
  self.assertFalse(a.BI_first_print_PIT_certified.any())

 def test_three_distinct_path_causes_existing_red(self):
  d=self.day
  new=d[(d.alert_level=="RED") & d.BI_strong_attention]
  self.assertTrue((new.BI_reason_three_paths.str.contains(
       "GVZ_ANOMALY|HISTORIC_CASEBOOK|CFTC_CONFIRMED_RISK_ACCELERATION",
       regex=True)).all())
  self.assertFalse(d.loc[d.alert_level=="NORMAL","BI_strong_attention"].any())

 def test_last_day_2025_yellow_continuity(self):
  d=self.day.set_index("origin")
  x=d.loc["2025-05-09"]
  self.assertEqual(x.alert_level,"YELLOW")
  self.assertTrue(x.BI_hysteresis_yellow)
  self.assertTrue(x.BI_strong_attention)
  self.assertFalse(d.loc["2025-11-20","BI_hysteresis_yellow"],
                   "Never carry score across a 1-month non-trading data gap")

 def test_risk_acceleration_route_rescues_2026_june9(self):
  x=self.day.set_index("origin").loc["2026-06-09"]
  self.assertTrue(x.BI_strong_attention)
  self.assertTrue(x.BI_risk_score_increased_vs_previous_session)
  self.assertIn("CFTC_CONFIRMED_RISK_ACCELERATION",x.BI_reason_three_paths)

 def test_sensitivity_stats_are_not_red_correction(self):
  d=self.m
  get=lambda year,name:d[(d.year==year)&(d.policy==name)].iloc[0]
  for yr,orig,high,extra,events,nextday in [
      (2025,32,28,30,3,3),(2026,50,32,34,4,4)]:
   base=get(yr,"BASE14_ORIGINAL_RED")
   conf=get(yr,"V18_THREE_PATH_RED")
   carry=get(yr,"V18_THREE_PATH_WITH_ONE_DAY_CARRY")
   self.assertEqual((base.marked_days,conf.marked_days,carry.marked_days),
                    (orig,high,extra))
   self.assertEqual((carry.five_day_label_clusters_hit,
                     carry.nextday3_hits),(events,nextday))
  self.assertFalse(self.audit["2026_is_not_blind"]==False)
  self.assertFalse(self.audit["production_promoted"])
  self.assertFalse(self.audit["price_prediction_model"])

 def test_early_stage_only_daily_proxy(self):
  timelines=pd.read_csv(D/"v18_actual_drawdown_onset_timeline.csv")
  self.assertGreaterEqual(len(timelines),8)
  self.assertTrue(timelines.intraday_start_unverified.all())
if __name__=="__main__":
 unittest.main(verbosity=2)
