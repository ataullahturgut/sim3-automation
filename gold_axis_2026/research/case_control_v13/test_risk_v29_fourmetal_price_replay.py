"""Independent check for V29 original risk replay. Any failure blocks certification."""
import unittest
import json
from pathlib import Path
import pandas as pd
import numpy as np

O=Path(__file__).parent/"outputs"

class V29GoldRiskReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=pd.read_csv(O/"v29_replayed_BASE14_CFTC21_V22_all_2026_daily.csv")
        cls.events=pd.read_csv(O/"v29_nine_historical_declines_event_sensitivity.csv")
        cls.metrics=pd.read_csv(O/"v29_scenario_model_alarm_2026_metrics.csv")
        cls.recovered=pd.read_csv(O/"v29_recovered_daily_origin_flags.csv")
        cls.m=json.loads((O/"v29_replay_manifest.json").read_text())
    def test_original_model_parameter_unchanged_and_quarantine_restored(self):
        x=self.m
        self.assertTrue(x["full_model_params_unchanged"])
        self.assertTrue(x["original_quarantine_unchanged"])
        self.assertFalse(x["same_session_LBMA_fixing_approved"])
        self.assertFalse(x["source_price_PIT_certified"])
        self.assertFalse(x["no_orig_Neon_mutation"] is False)
    def test_no_future_prices_used_as_model_inputs(self):
        self.assertTrue(self.data.no_future_labels_used.all())
        self.assertFalse(self.data.live_enabled.any())
        self.assertFalse(self.data.signal_price_same_fixing_certified.any())
    def test_all_old_BASE14_CFTC21_scores_unchanged(self):
        for r in self.m["scenarios_comparisons"]:
            self.assertEqual(r["old_model_scores_unchanged"],1572)
            self.assertEqual(r["V22_frozen_2026_score_rows_exactly_reproduced"],161)
            self.assertGreaterEqual(r["additional_days"],10)
    def test_original_march_2026_gap_is_declared(self):
        for s,g in self.data.groupby("scenario"):
            restored=g[g.was_previously_unscored]
            self.assertGreaterEqual(len(restored),10)
            self.assertTrue(restored.origin.between("2026-02-20","2026-03-27").all())
            self.assertTrue(g.origin.is_unique)
    def test_all_nine_predeclared_events_each_scenario(self):
        for s,g in self.events.groupby("scenario"):
            self.assertEqual(len(g),9)
            self.assertEqual(g.event_id.nunique(),9)
            row=g[g.price_peak.eq("2026-03-12")]
            self.assertEqual(len(row),1)
            self.assertGreater(row.days_with_model_score.iloc[0],0)
            self.assertEqual(row.expected_prior10_price_sessions.iloc[0],10)
            self.assertTrue(row.V22_prepeak_visible.iloc[0])
            self.assertTrue(row.V22_coverage_complete.iloc[0])
            self.assertFalse(row.numerical_PIT_certified.any())
    def test_2024_2025_events_preserved_not_falsely_unscorable(self):
        early=self.events[self.events.year.isin((2024,2025))]
        self.assertEqual(len(early),8)
        self.assertTrue((early.days_with_model_score>0).all())
        self.assertFalse(early.V22_verdict.eq("NO_SCORABLE_DAYS").any())

    def test_model_and_overlay_are_not_conflated(self):
        self.assertEqual(set(self.metrics.model),{"BASE14","CFTC21","V22_RESEARCH_REVIEW"})
        self.assertTrue((self.metrics.label_true10+self.metrics.label_false10+
                         self.metrics.label_unknown<=self.metrics.total_RED).all())
        self.assertEqual(self.metrics.scenario.nunique(),2)

if __name__=="__main__":
    unittest.main(verbosity=2)
