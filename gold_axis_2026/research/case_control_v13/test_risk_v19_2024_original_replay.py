from pathlib import Path
import json,unittest
import pandas as pd
D=Path(__file__).parent/"outputs"
class Validation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.audit=json.loads((D/"v19_audit.json").read_text())
  cls.day=pd.read_csv(D/"v19_2024_BI_signals.csv")
  cls.model=pd.read_csv(D/"v19_2024_original_models.csv")
  cls.events=pd.read_csv(D/"v19_2024_physical_onset.csv")
  cls.metrics=pd.read_csv(D/"v19_2024_replay_metrics.csv")
 def test_2024_untuned_original_math(self):
  self.assertEqual(self.audit["fit_period"],"2023")
  self.assertEqual(self.audit["validation"],"2024")
  self.assertTrue(self.audit["prior_2025_2026_models_unchanged"])
  self.assertFalse(self.audit["fit_on_2024_outcomes"])
  self.assertFalse(self.audit["fit_on_2025_outcomes"])
  self.assertFalse(self.audit["fit_on_2026_outcomes"])
  self.assertFalse(self.audit["numeric_first_print_PIT_certified"])
 def test_data_is_2024_only(self):
  self.assertTrue(self.day.origin.str[:4].eq("2024").all())
  self.assertTrue(self.model.origin.str[:4].eq("2024").all())
  self.assertTrue(self.day.origin.is_unique)
  self.assertEqual(len(self.model),2*len(self.day))
  self.assertGreater(len(self.day),175)
 def test_historic_casebook_never_uses_future_samples(self):
  self.assertTrue(self.day.closest_case.str[:4].astype(int).le(2022).all())
  self.assertTrue(self.day.closest_negative.str[:4].astype(int).le(2022).all())
 def test_new_bi_only_marks_red_or_one_day_yellow(self):
  s=self.day
  self.assertTrue((s.loc[s.BI_high_attention,"alert_level"].isin(["RED","YELLOW"])).all())
  self.assertFalse(s.loc[s.alert_level=="NORMAL","BI_high_attention"].any())
  self.assertTrue(s.loc[s.priority_YELLOW_CARRY,"alert_level"].eq("YELLOW").all())
 def test_large_2024_case_appears(self):
  self.assertEqual(len(self.events),1)
  self.assertEqual(self.events.onset_proxy.iloc[0],"2024-11-06")
 def test_correctness_vs_2024_origins(self):
  for _,row in self.metrics.iterrows():
   self.assertLessEqual(row.hit1,row.total1)
   self.assertLessEqual(row.hit5,row.total5)
   self.assertLessEqual(row.groups_hit,row.groups)
   self.assertEqual(row.alerted,row.hit5+row.false5)
if __name__=="__main__":unittest.main(verbosity=2)
