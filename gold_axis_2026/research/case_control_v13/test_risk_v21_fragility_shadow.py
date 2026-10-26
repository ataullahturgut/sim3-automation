"""Strict V21 shadow safeguards and honest 2024-2026 audit."""
import unittest,json
from pathlib import Path
import pandas as pd
import numpy as np
OUT=Path(__file__).parent/"outputs"

class FragilityShadowTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.daily=pd.read_csv(OUT/"v21_daily_shadow.csv")
  cls.stats=pd.read_csv(OUT/"v21_2024_2026_comparison.csv")
  cls.events=pd.read_csv(OUT/"v21_6_events_peak_audit.csv")
  cls.outcome=pd.read_csv(OUT/"v21_outcome_audit_ONLY.csv")
  cls.hist=json.loads((OUT/"v21_historical_casebook_limitations.json").read_text())
  cls.audit=json.loads((OUT/"v21_audit.json").read_text())
 def test_only_original_normal_may_create_shadow(self):
  d=self.daily
  self.assertTrue(d.loc[d.BI_v21_fragility_watch,"alert_level"].eq("NORMAL").all())
  self.assertTrue((d.BI_new_RED_count==0).all())
  self.assertFalse(d.BI_is_live_enabled.any())
 def test_exact_five_origin_safe_factors_no_future_leakage(self):
  d=self.daily
  right=(d.alert_level.eq("NORMAL")&d.rsi14.ge(.74)&
       d.AU_ret20.between(.04,.06,inclusive="both")&
       d.gvz_z252.ge(0)&d.GC_d1.lt(0))
  self.assertEqual(right.tolist(),d.BI_v21_fragility_watch.tolist())
 def test_replay_no_year_metric_hidden(self):
  stats=self.stats.set_index("year")
  self.assertEqual(stats.loc[2024,"new_shadow_watch_days"],4)
  self.assertEqual(stats.loc[2025,"new_shadow_watch_days"],0)
  self.assertEqual(stats.loc[2026,"new_shadow_watch_days"],1)
  self.assertEqual(stats.loc[2024,"new_watch_next10_false_5pct"],2)
  self.assertEqual(stats.loc[2026,"new_watch_next10_true_5pct"],1)
  self.assertEqual(stats.combined_BI_peak_coverage.sum(),6)
  self.assertEqual(stats.original_BI_peak_coverage.sum(),4)
 def test_knew_outcomes_and_admits_did_not_generalize_historically(self):
  self.assertTrue(self.audit["2024_2026_feature_band_selected_with_prior_outcome_knowledge"])
  self.assertFalse(self.audit["2010_2022_history_has_supporting_cases"])
  self.assertFalse(self.audit["prospective_holdout_completed"])
  self.assertFalse(self.audit["production_modified"])
  self.assertFalse(self.hist["supports_generalization"])
  self.assertEqual(self.hist["positive_case_examples_without_NORMAL_req"],0)
 def test_no_future_outcome_controls_shadow(self):
  d=self.daily
  q=self.outcome
  self.assertEqual(d.origin.tolist(),q.origin.tolist())
  self.assertEqual(d.BI_v21_fragility_watch.tolist(),q.watch.tolist())
  self.assertFalse(d.BI_first_numerical_PIT_certified.any())
 def test_distinct_event_counts_and_daily_score_clocks(self):
  e=self.events
  self.assertEqual(e.groupby("year").size().to_dict(),{2024:1,2025:2,2026:3})
  self.assertEqual(len(e),6)
  self.assertTrue(e.not_certified_intraday.all())
  self.assertTrue(e.event_dates_were_known_during_rule_research.all())
 def test_dont_change_existing_alert_level_and_score(self):
  old24=pd.read_csv(OUT/"v19_2024_BI_signals.csv")
  old24=old24[old24.model=="BASE14"]
  old25=pd.read_csv(OUT/"v18_daily_business_intelligence.csv")
  o=pd.concat([old24,old25],ignore_index=True).sort_values("origin").reset_index(drop=True)
  d=self.daily
  self.assertEqual(o.alert_level.tolist(),d.alert_level.tolist())
  np.testing.assert_allclose(o.risk_score,d.risk_score,rtol=0,atol=0)
if __name__=="__main__":
 unittest.main(verbosity=2)
