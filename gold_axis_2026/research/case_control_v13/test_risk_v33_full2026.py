import json
import unittest
from pathlib import Path
import pandas as pd

O=Path(__file__).parent/"outputs"
class Full2026NoFutureLabelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=pd.read_csv(O/"v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv")
        cls.m=pd.read_csv(O/"v33_2026_jan_oct27_MONTHLY_all_models_and_outcomes.csv")
        cls.manifest=json.loads((O/"v33_full_2026_asof_audit_manifest.json").read_text())
    def test_includes_all_weekdays_and_months_january_october(self):
        for scenario,z in self.d.groupby("scenario"):
            self.assertEqual(len(z),len(pd.bdate_range("2026-01-01","2026-10-27")))
            self.assertEqual(z.date.nunique(),len(z))
            self.assertEqual(z.date.max(),"2026-10-27")
        self.assertEqual(self.m.month.nunique(),10)
    def test_new_october_daily_scores_beyond_september_21(self):
        for scenario,z in self.d.groupby("scenario"):
            self.assertEqual(z[z.date.le("2026-09-21")].has_legacy_model_score.sum(),187)
            self.assertGreater(z[z.date.ge("2026-09-22")].has_legacy_model_score.sum(),0)
            self.assertTrue(z.loc[z.date.eq("2026-10-23"),"has_same_source_gold"].all())
    def test_original_params_parity_without_model_retraining(self):
        self.assertTrue(self.manifest["original_frozen_187_output_parity"])
        self.assertTrue(self.manifest["original_model_params_unchanged"])
        self.assertTrue(self.manifest["new_model_scoring_does_not_require_five_future_trading_sessions"])
    def test_never_invent_oct26_oct27_prices(self):
        q=self.d[self.d.date.isin(("2026-10-26","2026-10-27"))]
        self.assertEqual(len(q),4)
        self.assertTrue(q.price.isna().all())
        self.assertTrue(q.model_data_status.eq("PRICE_NOT_FOUND").all())
        self.assertTrue(q.BASE14_original_score.isna().all())
        self.assertFalse(q.next5_drop5_AUDIT_ONLY.eq(True).any())
    def test_october_macro_event_history_gap_not_silent_zero(self):
        z=self.d[self.d.date.ge("2026-10-01")]
        self.assertTrue(z.V31_event_coverage.eq("EVENT_SOURCE_ENDS_2026_09_11").all())
    def test_unmatured_5day_never_false_alarm(self):
        z=self.d[self.d.five_day_label_status.eq("UNMATURED_OR_PRICE_NOT_FOUND")]
        self.assertTrue(z.next5_drop5_AUDIT_ONLY.isna().all())
        self.assertTrue(z.next5_drop4_AUDIT_ONLY.isna().all())
    def test_research_only_not_live(self):
        self.assertFalse(self.manifest["candidate_score_timing_PIT_certified"])
        self.assertTrue(self.manifest["no_production_writes"])
        self.assertTrue(self.manifest["no_neon_modification"])
        self.assertTrue((self.d.original_params_changed==False).all())
    def test_4models_only(self):
        self.assertEqual(set(self.m.model),{"BASE14","CFTC21","V22","V22_PLUS_V31"})
        self.assertEqual(self.m.scenario.nunique(),2)

if __name__=="__main__":unittest.main(verbosity=2)
