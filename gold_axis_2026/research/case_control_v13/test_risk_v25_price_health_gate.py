import unittest
from pathlib import Path
import pandas as pd
from risk_v25_price_health_gate import verify, require_certified, O

class FourMetalDataHealthV25(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit=verify()
    def test_quarantine_four_metals_and_february(self):
        self.assertEqual(self.audit["known_bad_2026_02_27_metals"],["AG","AU","PD","PT"])
        self.assertTrue(self.audit["february_2026_target_is_contaminated"])
        self.assertTrue(self.audit["march_2026_origin_features_may_be_contaminated"])
    def test_external_2010_2024_comparison_is_not_spurious_certification(self):
        self.assertEqual(self.audit["independent_compared_AU_AG_PT_days"],11068)
        self.assertEqual(self.audit["comparisons_above_5pct_requiring_definition_review"],49)
        self.assertFalse(self.audit["those_49_are_confirmed_errors"])
        self.assertEqual(self.audit["independent_compared_PD_days"],0)
    def test_no_historical_asof_or_monthly_training_promoted(self):
        self.assertFalse(self.audit["data_health_certified"])
        self.assertFalse(self.audit["monthly_H1_train_replay_safe"])
        self.assertFalse(self.audit["PIT_gold_prices_verified"])
        self.assertFalse(self.audit["raw_Neon_modified"])
        self.assertFalse(self.audit["old_monthly_forecast_records_modified"])
    def test_fail_closed_when_model_attempts_certification(self):
        with self.assertRaisesRegex(RuntimeError,"PRICE_HEALTH_BLOCKED_V25"):
            require_certified(self.audit)
    def test_source_disagreements_are_adjudicated_not_blindly_replaced(self):
        a=pd.read_csv(O/"v25_gold_discrepancy_adjudication.csv").set_index("date")
        self.assertEqual(len(a),3)
        self.assertEqual(a.loc["2024-05-17","decision"],
                         "EXTERNAL_REFERENCE_TRANSCRIPTION_ERROR")
        self.assertEqual(a.loc["2026-01-02","decision"],
                         "EXTERNAL_REFERENCE_TRANSCRIPTION_ERROR")
        self.assertEqual(a.loc["2026-02-27","decision"],
                         "RESEARCH_DATABASE_GOLD_OUTLIER")
        self.assertTrue((a.original_data_mutated==False).all())
    def test_all_references_include_independent_corroboration(self):
        a=pd.read_csv(O/"v25_gold_discrepancy_adjudication.csv")
        self.assertTrue(a.corroboration_1.str.startswith("https://").all())
        self.assertTrue(a.corroboration_2.str.startswith("https://").all())

    def test_only_one_partial_2021_date_is_ignored_as_not_all_four(self):
        p=pd.read_csv(O/"v25_historical_partial_holiday.csv")
        self.assertEqual(p.date.tolist(),["2021-12-24"])
        self.assertEqual(p.missing_metals.tolist(),["PT|PD"])

if __name__=="__main__":unittest.main(verbosity=2)
