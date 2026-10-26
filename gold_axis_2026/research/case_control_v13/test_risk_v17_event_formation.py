"""V17 historical formation study acceptance gates."""
from pathlib import Path
import json, unittest
import pandas as pd
import numpy as np
R=Path(__file__).parent
O=R/"outputs"
class FormationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.a=json.loads((O/"v17_research_audit.json").read_text())
  cls.effects=pd.read_csv(O/"v17_all_feature_effects.csv")
  cls.history=pd.read_csv(O/"v17_history_formation_windows.csv")
 def test_no_2026_fitting_or_selection(self):
  self.assertFalse(self.a["used_2026_in_selection"])
  self.assertTrue(self.a["modern_years_not_used_to_choose_variables"])
  self.assertFalse(self.a["model_production_updated"])
  self.assertFalse(self.a["neon_updated"])
  self.assertFalse(self.a["first_print_PIT_certified"])
 def test_full_variable_screen(self):
  self.assertEqual(self.a["feature_count"],31)
  self.assertEqual(len(self.effects),31)
  self.assertFalse(self.effects.feature.duplicated().any())
  self.assertTrue(self.effects.family.nunique()>=5)
 def test_historical_case_control_universe(self):
  self.assertEqual(self.a["history_event_groups"],27)
  self.assertTrue(self.a["independent_history_contexts"]>=10)
  self.assertEqual(self.history.event_id.nunique(),27)
  self.assertTrue(set(self.history.phase)=={-20,-10,-5,-3,-1})
  self.assertTrue((self.history.origin.str[:4].astype(int)<=2022).all())
  self.assertEqual(self.history[(self.history.role=="DROP_EVENT")&(self.history.phase==-1)].event_id.nunique(),27)
 def test_no_future_prices_as_feature(self):
  names=set(self.effects.feature)
  self.assertFalse(any(k.startswith("future") or "AUDIT_ONLY" in k for k in names))
  self.assertFalse(any("2026" in str(x) for x in self.a["rules"]))
 def test_if_index_generated_pre2026_only(self):
  if not self.a["rules"]:return
  self.assertTrue(all(r["feature"] in set(self.effects.feature) for r in self.a["rules"]))
  d=pd.read_csv(O/"v17_2023_2025_daily_index.csv")
  self.assertTrue((d.origin.str[:4].astype(int)<=2025).all())
  self.assertTrue((d.origin.str[:4].astype(int)>=2023).all())
  self.assertGreater(len(d),500)
  self.assertTrue(d.formation_index.between(0,100).all())
  self.assertTrue(np.isfinite(d.formation_index).all())
  self.assertEqual(d.origin.nunique(),len(d))
 def test_event_precursors_not_onset_or_after(self):
  if not self.a["rules"]:return
  ev=pd.read_csv(O/"v17_2023_2025_real_drawdown_events.csv")
  self.assertGreaterEqual(len(ev),3)
  self.assertTrue((ev.first_attention_before_onset.dropna()<ev.loc[ev.first_attention_before_onset.notna(),"onset_proxy"]).all())
  self.assertTrue((ev.trough<="2025-12-31").all())
if __name__=="__main__":unittest.main(verbosity=2)
