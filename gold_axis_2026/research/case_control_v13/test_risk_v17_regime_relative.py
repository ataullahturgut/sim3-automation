"""Check objective 62-feature screening, onset-safe and no 2026 tuning."""
from pathlib import Path
import json,unittest
import pandas as pd
import numpy as np
D=Path(__file__).parent/"outputs"
class RelativeFormationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=json.loads((D/"v17r_audit.json").read_text())
  cls.f=pd.read_csv(D/"v17r_all_62_metrics.csv")
  cls.w=pd.read_csv(D/"v17r_historical_relative_windows.csv")
 def test_62_full_variable_candidates(self):
  self.assertEqual(self.a["candidate_descriptors"],62)
  self.assertEqual(len(self.f),62)
  self.assertGreaterEqual(self.f.family.nunique(),5)
  self.assertTrue(self.f.metric.str.startswith(("REGIME:","CHANGE5:")).all())
 def test_no_future_selection(self):
  self.assertFalse(self.a["selection_uses_2023_2025"])
  self.assertFalse(self.a["selection_uses_2026"])
  self.assertFalse(self.a["rule_is_forecast"])
  self.assertFalse(self.a["original_risk_alarms_changed"])
  self.assertFalse(self.a["numerical_first_print_PIT_certified"])
 def test_historic_event_dates_only(self):
  self.assertEqual(self.w.event_id.nunique(),27)
  self.assertTrue((self.w.origin.str[:4].astype(int)<=2022).all())
 def test_signs_and_effects_are_numeric(self):
  self.assertTrue(set(self.f.direction).issubset({"HIGH","LOW"}))
  self.assertTrue(self.f.consistency.between(0,1).all())
  self.assertTrue(np.isfinite(self.f.cluster_effect_IQR).all())
 def test_index_2023_to_2025_only(self):
  if not self.a["picked"]:return
  modern=pd.read_csv(D/"v17r_modern_daily.csv")
  self.assertTrue(modern.origin.str[:4].astype(int).between(2023,2025).all())
  self.assertTrue(modern.regime_formation_index.between(0,100).all())
  self.assertEqual(len(modern.origin.unique()),len(modern))
  self.assertGreater(len(modern),600)
  ev=pd.read_csv(D/"v17r_modern_event_timing.csv")
  self.assertEqual(len(ev),4)
  self.assertTrue((ev.trough<="2025-12-31").all())
if __name__=="__main__":unittest.main(verbosity=2)
