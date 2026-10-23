"""Regression: monthly model must NEVER ingest mixed metal vendors (no Neon writes)."""
from __future__ import annotations

import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import vw_midas_msvr_successor_v1 as model

METALS = ("Gold", "Silver", "Platinum", "Palladium")

def month_rows(year, month, provider="LBMA", payload="seed", weekends=False):
    d = date(year, month, 1)
    rows = []
    while d.month == month:
        if weekends or d.weekday() < 5:
            for i, metal in enumerate(METALS):
                rows.append({
                    "day": d.isoformat(), "metal": metal,
                    "value": float(800 + 500 * i + d.day),
                    "provider_label": provider,
                    "payload_source_label": payload,
                    "provenance": "single synthetic frozen archive",
                })
        d += timedelta(days=1)
    return rows

class SingleProviderMonthlyModel(unittest.TestCase):
    def test_one_good_month_and_bad_month_excluded(self):
        good = month_rows(2025, 1)
        mixed = month_rows(2026, 2)
        for r in mixed:
            if r["day"] >= "2026-02-12":
                r["provider_label"] = "MetalPriceAPI"
        daily, monthly, audit = model.select_single_source_metal_prices(good + mixed)
        self.assertEqual(audit["accepted_months"], ["2025-01"])
        self.assertEqual(audit["quarantined_months"], ["2026-02"])
        for m in METALS:
            self.assertEqual(set(daily[m]), {"2025-01"})
            self.assertEqual(set(monthly[m]), {"2025-01"})
        self.assertNotIn("2026-02", monthly["Gold"])
        self.assertEqual(monthly["Gold"]["2025-01"],
                         sum(r["value"] for r in good if r["metal"] == "Gold") /
                         sum(r["metal"] == "Gold" for r in good))

    def test_sqld_weekend_month_wholly_excluded(self):
        jan = month_rows(2026, 1)
        apr = month_rows(2026, 4, provider=None, payload="sqld", weekends=True)
        _, monthly, panel = model.select_single_source_metal_prices(jan + apr)
        self.assertEqual(panel["accepted_months"], ["2026-01"])
        self.assertNotIn("2026-04", monthly["Gold"])
        self.assertIn("WEEKEND_OBSERVATIONS_PRESENT", panel["month_audit"]["2026-04"]["reasons"])

    def test_one_unmatched_metal_day_never_forward_filled(self):
        rows = month_rows(2021, 12)
        rows = [r for r in rows if not (
            r["day"] == "2021-12-24" and r["metal"] in ("Platinum", "Palladium"))]
        daily, _, audit = model.select_single_source_metal_prices(rows)
        self.assertEqual(audit["accepted_months"], ["2021-12"])
        self.assertEqual(len(daily["Gold"]["2021-12"]), 22)
        self.assertEqual(len(daily["Palladium"]["2021-12"]), 22)

    def test_second_archive_lineage_is_not_silently_merged(self):
        rows = month_rows(2025, 1) + month_rows(2025, 2)
        for row in rows:
            if row["day"] >= "2025-02-01":
                row["provenance"] = "different archival source"
        with self.assertRaisesRegex(RuntimeError, "MULTIPLE_OR_MISSING_APPROVED_METAL_ARCHIVE_LINEAGES"):
            model.select_single_source_metal_prices(rows)

    def test_no_certifiable_provider_rows_fails_closed(self):
        bad = month_rows(2026, 3, provider=None, payload="sqld")
        with self.assertRaisesRegex(RuntimeError, "NO_FOUR_METAL_SINGLE_PROVIDER"):
            model.select_single_source_metal_prices(bad)

    def test_no_metal_price_fabrication_or_extra_months(self):
        rows = month_rows(2025, 12) + month_rows(2026, 1)
        _, monthly, panel = model.select_single_source_metal_prices(rows)
        self.assertEqual(sorted(monthly["Gold"]), ["2025-12", "2026-01"])
        self.assertFalse(panel["policy"]["live_pit_certified"])
        self.assertIn("2026-08", panel["missing_expected_months"])
        self.assertIn("2026-09", panel["missing_expected_months"])

if __name__ == "__main__":
    unittest.main()
