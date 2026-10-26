import unittest
from pathlib import Path
import pandas as pd
from risk_v24_event_timelines import load,event_timeline,research_summary,family_timeline,O

class StrictNineEventTimeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prices,cls.daily,cls.ledger=load()
        cls.events=event_timeline(cls.prices,cls.daily,cls.ledger)
    def test_nine_nonduplicated_events_and_correct_year_counts(self):
        self.assertEqual(len(self.events),9)
        self.assertEqual(self.events.year.value_counts().sort_index().to_dict(),
                         {2024:1,2025:3,2026:5})
        self.assertTrue(self.events.event_id.is_unique)
    def test_2024_watch_on_peak_not_called_before_peak(self):
        x=self.events.set_index("event_id").loc["2024_11"]
        self.assertEqual(x.V22_first_any_before_or_on_peak,"2024-10-30")
        self.assertFalse(bool(x.V22_first_any_prior5))
        self.assertFalse(bool(x.V22_first_any_prior10))
        self.assertEqual(x.verdict,"NO_PREPEAK_REVIEW")
    def test_2026_march_is_unscorable_not_missed(self):
        x=self.events.set_index("event_id").loc["2026_002"]
        self.assertEqual(x.verdict,"NOT_EVALUABLE_NO_MODEL_SCORES")
        self.assertEqual(x.prior10_scoreable_sessions,0)
    def test_no_april_peak_misassigned_to_june(self):
        e=self.events.set_index("event_id")
        self.assertEqual(e.loc["2026_003","price_peak"],"2026-06-04")
        self.assertEqual(e.loc["2026_004","price_peak"],"2026-06-17")
    def test_prepeak_dates_strict_and_no_lookahead(self):
        for _,r in self.events.iterrows():
            if pd.notna(r.V22_first_any_prior10) and r.V22_first_any_prior10:
                self.assertLess(r.V22_first_any_prior10,r.price_peak)
            if pd.notna(r.V22_first_any_prior5) and r.V22_first_any_prior5:
                self.assertLess(r.V22_first_any_prior5,r.price_peak)
            self.assertLess(r.price_peak,r.original_v13_onset_proxy)
            self.assertGreaterEqual(r.price_trough,r.original_v13_onset_proxy)
            self.assertLess(r.peak_to_trough_pct,0)
    def test_2025_and_2026_price_sources_not_pit(self):
        self.assertFalse(bool(self.events.numerical_macro_firstprint_PIT_verified.any()))
        self.assertFalse(bool(self.events.true_intraday_onset_verified.any()))
        self.assertEqual(self.prices.loc[self.prices.quarantined,"date"].tolist(),
                         ["2026-02-27"])
    def test_seven_families_first_episode_credited_once(self):
        f=family_timeline(self.events).set_index("economic_family")
        self.assertEqual(len(f),7)
        self.assertEqual(f.family_verdict.value_counts().to_dict(),
                         {"EARLY":4,"MISSED_STRICT_PREPEAK":2,
                          "UNKNOWN_NO_MODEL_COVERAGE":1})
        self.assertEqual(f.loc["2026_JUNE","first_component_peak"],"2026-06-04")
        self.assertEqual(f.loc["2026_JUNE","family_verdict"],"MISSED_STRICT_PREPEAK")
        self.assertEqual(f.loc["2026_MAR","family_verdict"],"UNKNOWN_NO_MODEL_COVERAGE")
        self.assertEqual(f.loc["2025_APR_MAY","component_count"],2)
    def test_quality_counts_partition(self):
        m=research_summary(self.events)
        self.assertTrue((m.events == m.strict_early_signal +
                         m.partial_windows + m.completely_unscorable +
                         m.complete_no_early).all())

if __name__=="__main__":unittest.main(verbosity=2)
