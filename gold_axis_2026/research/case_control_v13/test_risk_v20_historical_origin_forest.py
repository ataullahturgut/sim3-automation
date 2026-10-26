import unittest,json
from pathlib import Path
import pandas as pd
O=Path(__file__).parent/"outputs"
class TestedHistoricalWindows(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.metrics=pd.read_csv(O/"v20_annual_results.csv")
  cls.timing=pd.read_csv(O/"v20_physical_peak_replay.csv")
  cls.train=pd.read_csv(O/"v20_fitting_provenance.csv")
  cls.audit=json.loads((O/"v20_research_audit.json").read_text())
 def test_all_2024_2025_2026_windows(self):
  m=self.metrics
  self.assertEqual(set(m.year),{2024,2025,2026})
  self.assertEqual(set(m.model),{"BASE14","CFTC21"})
  self.assertEqual(m.window.nunique(),5)
  self.assertEqual(len(m),30)
 def test_immutable_incumbents(self):
  for year,expected in [(2024,18),(2025,32),(2026,50)]:
   row=self.metrics[(self.metrics.year==year)&(self.metrics.window=="FROZEN_BASELINE")&(self.metrics.model=="BASE14")]
   self.assertEqual(len(row),1)
   self.assertEqual(row.red_days.iloc[0],expected)
  self.assertTrue(self.audit["production_models_untouched"])
  self.assertTrue(self.audit["feature_set_unchanged"])
 def test_models_use_past_only(self):
  for _,row in self.train.iterrows():
   self.assertLess(row.training_last,f"{row.year}-01-01")
   self.assertGreater(row.train_n,170)
 def test_first_print_not_falsely_certified(self):
  self.assertFalse(self.audit["numerical_first_print_PIT_certified"])
  self.assertTrue(self.audit["2026_stress_previously_seen"])
  self.assertFalse(self.audit["fitted_to_drop_outcome"])
 def test_distinct_physical_peaks_per_year(self):
  m=self.metrics
  for year,n in [(2024,1),(2025,2),(2026,3)]:
   self.assertTrue((m.loc[m.year==year,"distinct_physical_peaks_total"]==n).all())
   self.assertTrue((m.loc[m.year==year,"distinct_physical_early_peaks_found"]<=n).all())
 def test_physical_warning_preceded_price_peak(self):
  t=self.timing
  f=t.first_red_at_or_before_true_peak.notna()
  self.assertTrue((t.loc[f,"first_red_at_or_before_true_peak"]<=t.loc[f,"price_peak"]).all())
  self.assertEqual(len(t),30)
if __name__=="__main__":unittest.main(verbosity=2)
