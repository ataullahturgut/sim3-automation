#!/usr/bin/env python3
"""Regression tests for the V23 ten-PRICE-session audit correction."""
import unittest
import numpy as np
import pandas as pd
from pathlib import Path
from risk_v23_calendar_safe_audit import outcome_for_origin, build_daily, daily_metrics, episode_metrics, O

class CalendarSafeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.daily = pd.read_csv(O / "v23_calendar_safe_daily.csv")
        cls.prices = pd.read_csv(O / "v23_price_calendar_RESEARCH_NOT_PIT.csv")
        cls.metrics = pd.read_csv(O / "v23_calendar_safe_daily_metrics.csv")
        cls.episodes = pd.read_csv(O / "v23_calendar_safe_episode_metrics.csv")

    def record(self, date):
        return self.daily.loc[self.daily.origin.eq(date)].iloc[0]

    def test_source_parity_for_all_647_origins(self):
        self.assertEqual(len(self.daily), 647)
        self.assertEqual(len(self.prices), 713)
        self.assertEqual(self.prices.quarantined.sum(), 1)
        prices = self.prices.set_index("date").loc[self.daily.origin]
        np.testing.assert_allclose(prices.price.to_numpy(),
                                   self.daily.price.to_numpy(), rtol=0, atol=1e-8)
        self.assertFalse(prices.quarantined.any())

    def test_five_day_original_labels_are_reproduced(self):
        for _, r in self.daily.iterrows():
            status, value = outcome_for_origin(self.prices, str(r.origin), horizon=5)
            self.assertIn(status, ("TRUE_DROP_5PCT", "FALSE_DROP_5PCT"), r.origin)
            self.assertEqual(status == "TRUE_DROP_5PCT", bool(r.y5_AUDIT_ONLY), r.origin)

    def test_feb10_no_spurious_ten_percent_decline(self):
        r = self.record("2026-02-10")
        self.assertEqual(r.ten_day_status, "FALSE_DROP_5PCT")
        self.assertAlmostEqual(r.next10_min_pct_AUDIT_ONLY, -3.4071256648738557, places=7)

    def test_feb_bad_price_not_used_or_silently_skipped(self):
        bad = ["2026-02-13","2026-02-16","2026-02-17","2026-02-18","2026-02-19"]
        self.assertEqual(sorted(self.daily.loc[self.daily.ten_day_unknown, "origin"].tolist()), bad)
        for day in bad:
            r = self.record(day)
            self.assertEqual(r.ten_day_status, "UNKNOWN_QUARANTINED_FUTURE_PRICE")
            self.assertTrue(np.isnan(r.next10_min_pct_AUDIT_ONLY))

    def test_october_prices_mature_september_decisions(self):
        r = self.record("2026-09-21")
        self.assertTrue(r.ten_day_mature)
        self.assertEqual(r.ten_day_status, "FALSE_DROP_5PCT")
        self.assertAlmostEqual(r.next10_min_pct_AUDIT_ONLY, -4.759498555291664, places=7)
        self.assertEqual(self.prices.date.iloc[-1], "2026-10-16")

    def test_real_2025_gap_does_not_extend_horizon(self):
        r = self.record("2025-10-17")
        self.assertEqual(r.ten_day_status, "TRUE_DROP_5PCT")
        self.assertAlmostEqual(r.next10_min_pct_AUDIT_ONLY, -9.866881807180317, places=7)

    def test_synthetic_missing_calendar_and_quarantined_prices(self):
        price = pd.DataFrame({"date":["2026-01-05","2026-01-06","2026-01-20"],
                              "price":[100.,101.,80.],
                              "source":["RESEARCH_NOT_PIT"]*3,
                              "quarantined":[False]*3})
        self.assertEqual(outcome_for_origin(price, "2026-01-05", 2)[0],
                         "UNKNOWN_PRICE_CALENDAR_GAP")
        price.loc[1, "quarantined"] = True
        self.assertEqual(outcome_for_origin(price, "2026-01-05", 1)[0],
                         "UNKNOWN_QUARANTINED_FUTURE_PRICE")
        self.assertEqual(outcome_for_origin(price, "2026-01-20", 1)[0],
                         "UNKNOWN_NOT_MATURE")

    def test_alarm_episode_partition_and_corrected_2026_count(self):
        m = self.episodes
        self.assertTrue((m.episodes_total == m.episodes_true10 +
                         m.episodes_false10 + m.episodes_unknown10).all())
        r = m[(m.year==2026) & (m.gap_days==4) &
              (m.policy=="V22_PRIORITIZED_PLUS_WATCH")].iloc[0]
        self.assertEqual(tuple(map(int, (r.episodes_total,r.episodes_true10,
                                        r.episodes_false10,r.episodes_unknown10))),
                         (9,5,3,1))

    def test_original_alert_decisions_frozen(self):
        r = self.daily
        self.assertFalse(r.original_alert_changed.any())
        self.assertFalse(r.live_enabled.any())
        self.assertFalse(r.horizon_price_source_PIT_certified.any())
        self.assertTrue((self.metrics.flagged_days ==
                         self.metrics.true10_days + self.metrics.false10_days +
                         self.metrics.unknown10_days).all())

if __name__ == "__main__":
    unittest.main(verbosity=2)
