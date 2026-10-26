import unittest,json
import numpy as np,pandas as pd
from pathlib import Path
O=Path(__file__).parent/"outputs"

class V22PhaseChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.daily=pd.read_csv(O/"v22_daily_decisions.csv")
  cls.metrics=pd.read_csv(O/"v22_three_year_metrics.csv")
  cls.events=pd.read_csv(O/"v22_physical_early_warning.csv")
  cls.limits=json.loads((O/"v22_audit_limits.json").read_text())
 def test_immutable_old_alerts(self):
  a=pd.read_csv(O/"v19_2024_BI_signals.csv")
  a=a[a.model=="BASE14"]
  b=pd.read_csv(O/"v18_daily_business_intelligence.csv")
  original=pd.concat([a,b],ignore_index=True).sort_values("origin").reset_index(drop=True)
  d=self.daily
  self.assertEqual(d.origin.tolist(),original.origin.tolist())
  self.assertEqual(d.BASE14_original_alert_level.tolist(),original.alert_level.tolist())
  np.testing.assert_array_equal(d.BASE14_original_score.values,original.risk_score.values)
  self.assertFalse(d.original_alert_changed.any())
  self.assertFalse(d.live_enabled.any())
 def test_watches_only_original_normal(self):
  d=self.daily
  self.assertTrue(d.loc[d.watch,"BASE14_original_alert_level"].eq("NORMAL").all())
  self.assertTrue(d.loc[d.active_RED_phase,"BASE14_original_alert_level"].eq("RED").all())
 def test_retro_metrics_full_years(self):
  m=self.metrics
  self.assertEqual(set(m.year),{2024,2025,2026})
  get=lambda y,n:m[(m.year==y)&(m.policy==n)].iloc[0]
  for yr,oldf,newf,hit5,hit1 in [(2024,18,12,0,0),(2025,27,15,5,3),(2026,40,22,10,4)]:
   a=get(yr,"BASE14_ORIGINAL_RED")
   b=get(yr,"V22_PRIORITIZED_REVIEW_PLUS_WATCH")
   self.assertEqual((a.false5_days,b.false5_days),(oldf,newf))
   self.assertEqual((b.true5_days,b.nextday3_hit),(hit5,hit1))
 def test_event_peak_not_oversold(self):
  e=self.events
  self.assertEqual(len(e),6)
  self.assertTrue(e.V22_active_before_or_on_peak.all())
  self.assertTrue(e.hypothesis_was_not_blind.all())
  self.assertEqual(e.loc[e.event=="2026_MAY_JUNE","first_V22_attention_last5"].iloc[0],"2026-04-17")
 def test_does_not_claim_blind_or_live_success(self):
  self.assertTrue(self.limits["2024_and_2026_events_known_during_design"])
  self.assertFalse(self.limits["2026_blind_validation"])
  self.assertFalse(self.limits["original_red_changed"])
  self.assertFalse(self.limits["production_promoted"])
  self.assertFalse(self.limits["full_numeric_PIT_certified"])
 def test_horizon_maturity_not_fabricated(self):
  d=pd.read_csv(O/"v22_daily_outcome_audit_ONLY.csv")
  last=d.iloc[-1]
  self.assertFalse(last.ten_day_mature)
  self.assertTrue(np.isnan(last.next10_min_pct_AUDIT_ONLY))
if __name__=="__main__":unittest.main(verbosity=2)
