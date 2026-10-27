"""V32 independent output gate: full calendar, 2026 decline families,
original parity, chronologic difference from post-release detection."""
from __future__ import annotations
import json
import unittest
import pandas as pd
import risk_v32_2026_full_calendar_joint_replay as r

class V32Unbiased2026Audit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        o=r.O
        cls.d=pd.read_csv(o/"v32_2026_all_days_base14_cftc21_v22_plus_v31_scenario.csv")
        cls.s=pd.read_csv(o/"v32_2026_common_denominator_alert_day_comparison.csv")
        cls.peaks=pd.read_csv(o/"v32_2026_5_peak_prepeak_early_warning_comparison.csv")
        cls.e=pd.read_csv(o/"v32_2026_23_event_time_observations.csv")
        cls.m=json.loads((o/"v32_combined_2026_replay_manifest.json").read_text())
    def test_scenarios_equal_and_no_original_alarms_changed(self):
        self.assertEqual(self.d.scenario.nunique(),2)
        for scenario,g in self.d.groupby("scenario"):
            self.assertGreaterEqual(len(g),185)
            self.assertEqual(g.legacy_scored.sum(),187)
            self.assertEqual(g.legacy_BASE14_red.sum(),63)
            self.assertEqual(g.legacy_CFTC21_red.sum(),43)
            self.assertEqual(g.date.nunique(),len(g))
            self.assertTrue(g.date.between("2026-01-01","2026-09-30").all())
        self.assertTrue(self.m["original_baseline_parity_confirmed_161_days_each_scenario"])
        self.assertTrue(self.m["prior_original_scores_equal_1572_each_scenario"])
    def test_no_historical_true_live_signal_or_trades(self):
        self.assertFalse(self.d.v31_historical_live_signal_eligible.any())
        self.assertFalse(self.d.PIT_price_certified.any())
        self.assertFalse(self.d.any_sell_trade_executed.any())
        self.assertTrue(self.m["no_live_alarms_sent"])
        self.assertFalse(self.m["macros_prior_consensus_capture_proven"])
    def test_macros_have_precise_release_asof_and_no_backdating(self):
        self.assertEqual(len(self.e),23)
        for ev in self.e.itertuples():
            first=pd.Timestamp(ev.earliest_state_known_TR)
            release=pd.Timestamp(ev.release_utc)
            self.assertGreaterEqual(first,release+pd.Timedelta(minutes=35))
            if ev.bank_hours_research_extreme:
                self.assertFalse(ev.outside_bank)
        self.assertEqual(self.e.event_id.nunique(),23)
    def test_june_first_leg_cannot_gain_early_warning_from_postpeak_NFP(self):
        for scenario,g in self.peaks.groupby("scenario"):
            a=g[g.economic_phase.eq("JUNE_FIRST")].iloc[0]
            self.assertFalse(a.V22_strict_prepeak_hit)
            self.assertFalse(a.V31_new_strict_prepeak_win)
            self.assertFalse(a.combined_strict_prepeak_hit)
            nfp=self.e[self.e.event_id.str.startswith("NFP_2026-06-05")].iloc[0]
            self.assertGreater(nfp.date,a.peak_date)
    def test_scenario_peak_contract_and_no_retune(self):
        for scenario,g in self.peaks.groupby("scenario"):
            self.assertEqual(len(g),5)
            self.assertEqual(set(g.economic_phase),set(r.FAMILIES))
            self.assertTrue((g.pre_peak_price_sessions==10).all())
        self.assertEqual(self.m["v31_train_years"],"2023-2024")
        self.assertTrue(self.m["v31_2025_and_2026_unused_for_threshold_selection"])
        self.assertFalse(self.m["same_session_2026_Feb27_fourmetal_price_certified"])
    def test_all_price_days_not_only_23_macro_events(self):
        for scenario,g in self.d.groupby("scenario"):
            self.assertGreater(len(g),180)
            self.assertEqual(int(g.macro_events.sum()),int(self.e.has_2026_price_day.sum()))
            self.assertEqual((g.next5_matured).sum(),len(g)-5)
            self.assertTrue(((g.combined_attention_research)|
                             (~g.legacy_V22_attention & ~g.macro_research_in_bank.gt(0))).all())
    def test_common_denominator_maturity_and_false_alarm_counts(self):
        for scenario,g in self.s.groupby("scenario"):
            self.assertEqual(len(g),5)
            self.assertEqual(set(g.strategy),{"BASE14_RED","CFTC21_RED","V22_ATTENTION","V31_ADDITIONAL_BANK_REPRICING","V22_PLUS_V31_BANK"})
            self.assertEqual(g.common_score_and_5day_label_days.nunique(),1)
            self.assertTrue((g.next5_drop_ge5_alert_days+
                             g.next5_NO_drop_ge5_alert_days==
                             g.alert_days_on_common_scored_dates).all())
    def test_only_one_price_day_for_each_2026_origin(self):
        for scenario,g in self.d.groupby("scenario"):
            self.assertEqual(int(g.date.eq("2026-06-04").sum()),1)
            pre=g[g.date.lt("2026-06-04") & g.date.ge("2026-05-20")]
            self.assertFalse(pre.macro_research_in_bank.gt(0).any())

if __name__=="__main__": unittest.main(verbosity=2)
