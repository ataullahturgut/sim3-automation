"""Origin monthly price proxy guards; synthetic dated observations only."""
from __future__ import annotations
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from gold_monthly_chhho_origin_anchor_replay_v1 import prefix_origin_price, origin_cutoff


class TestOriginAnchor(unittest.TestCase):
    def setUp(self):
        self.rows=[{"date":f"2024-01-{d:02d}", "Gold":float(2000+d)}
                   for d in range(1,32) if date(2024,1,d).isoweekday()<6]

    def test_month_end_date_is_excluded_in_strict_arm(self):
        a=prefix_origin_price(self.rows,"2024-01",strict=True)
        b=prefix_origin_price(self.rows,"2024-01",strict=False)
        self.assertEqual(a["cutoff_day_inclusive"],"2024-01-30")
        self.assertEqual(b["cutoff_day_inclusive"],"2024-01-31")
        self.assertEqual(b["observed_business_day_count"],a["observed_business_day_count"]+1)
        self.assertNotEqual(a["anchor_usd_oz"],b["anchor_usd_oz"])
        self.assertFalse(a["first_publication_time_verified"])

    def test_target_month_future_price_mutation_invariant(self):
        a=prefix_origin_price(self.rows,"2024-01")
        bad=self.rows+[{"date":"2024-02-01","Gold":999999999}]
        self.assertEqual(a,prefix_origin_price(bad,"2024-01"))

    def test_weekend_record_rejected(self):
        bad=self.rows+[{"date":"2024-01-06","Gold":3000.0}]
        bad.sort(key=lambda r:r["date"])
        with self.assertRaisesRegex(RuntimeError,"NON_BUSINESS_DAY"):
            prefix_origin_price(bad,"2024-01")

    def test_duplicate_date_rejected(self):
        bad=self.rows+[dict(self.rows[0])]
        bad.sort(key=lambda r:r["date"])
        with self.assertRaisesRegex(RuntimeError,"NOT_SORTED_OR_UNIQUE"):
            prefix_origin_price(bad,"2024-01")

    def test_insufficient_price_rows_rejected(self):
        with self.assertRaisesRegex(RuntimeError,"COVERAGE_FAIL"):
            prefix_origin_price(self.rows[:9],"2024-01")

    def test_bad_price_rejected(self):
        bad=[dict(x) for x in self.rows]
        bad[0]["Gold"]=0
        with self.assertRaisesRegex(RuntimeError,"BAD_PRICE"):
            prefix_origin_price(bad,"2024-01")

    def test_february_end_and_cross_year(self):
        self.assertEqual(origin_cutoff("2024-02",True),"2024-02-28")
        self.assertEqual(origin_cutoff("2024-02",False),"2024-02-29")
        self.assertEqual(origin_cutoff("2023-12",True),"2023-12-30")

if __name__=="__main__":
    unittest.main()
