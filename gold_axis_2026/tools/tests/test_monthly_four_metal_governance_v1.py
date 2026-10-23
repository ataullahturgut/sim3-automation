"""Source governance regressions; synthetic records, no Neon mutation."""
from __future__ import annotations
import copy
import sys
import unittest
from datetime import date,timedelta
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gold_monthly_four_metal_governance_v1 as gov

def fake_month(year,month,provider="LBMA",source="seed",include_weekends=False):
    first=date(year,month,1)
    records=[]
    dt=first
    while dt.month==month:
        if dt.isoweekday()<=5 or include_weekends:
            for j,metal in enumerate(gov.METALS):
                records.append({
                    "day":dt.isoformat(),"metal":metal,"value":1000+j*100+dt.day,
                    "provider_label":provider,"payload_source_label":source,
                    "provenance":"frozen synthetic test",
                })
        dt+=timedelta(days=1)
    return records

class SourcePolicy(unittest.TestCase):
    def test_clean_month_passes_but_not_live_certified(self):
        panel=gov.build_governed_panel(fake_month(2023,3))
        self.assertEqual(panel["accepted_months"],["2023-03"])
        self.assertEqual(panel["quarantined_months"],[])
        self.assertFalse(panel["policy"]["live_pit_certified"])
        self.assertEqual(len(panel["clean_four_metal_rows"]),23)

    def test_missing_pt_pd_one_holiday_is_dropped_without_imputation(self):
        rows=fake_month(2021,12)
        day="2021-12-24"
        rows=[r for r in rows if not(r["day"]==day and r["metal"] in ("Platinum","Palladium"))]
        panel=gov.build_governed_panel(rows)
        self.assertEqual(panel["accepted_months"],["2021-12"])
        self.assertEqual(panel["month_audit"]["2021-12"]["missing_metal_days"],[
            {"date":day,"missing_metals":["Palladium","Platinum"]}])
        self.assertNotIn(day,[r["day"] for r in panel["clean_four_metal_rows"]])
        self.assertEqual(panel["month_audit"]["2021-12"]["matched_business_days"],22)

    def test_weekends_quarantine_entire_month(self):
        rows=fake_month(2026,4,provider=None,source="sqld",include_weekends=True)
        panel=gov.build_governed_panel(rows)
        self.assertEqual(panel["accepted_months"],[])
        flags=panel["month_audit"]["2026-04"]["reasons"]
        self.assertIn("WEEKEND_OBSERVATIONS_PRESENT",flags)
        self.assertIn("MIXED_OR_UNVERIFIED_PROVIDER_PAYLOAD",flags)
        self.assertEqual(panel["clean_four_metal_rows"],[])

    def test_mixed_provider_quarantines_metal_panel(self):
        rows=fake_month(2026,2)
        for r in rows:
            if r["day"]>="2026-02-12":
                r["provider_label"]="MetalPriceAPI"
        panel=gov.build_governed_panel(rows)
        self.assertEqual(panel["quarantined_months"],["2026-02"])
        self.assertIn("MIXED_OR_UNVERIFIED_PROVIDER_PAYLOAD",
                      panel["month_audit"]["2026-02"]["reasons"])

    def test_weekend_removal_does_not_erase_audit(self):
        rows=fake_month(2026,6,provider="LBMA",source="seed",include_weekends=True)
        panel=gov.build_governed_panel(rows)
        self.assertEqual(panel["quarantined_months"],["2026-06"])
        self.assertEqual(panel["month_audit"]["2026-06"]["matched_business_days"],22)
        self.assertTrue(panel["month_audit"]["2026-06"]["weekend_dates"])

    def test_unknown_provenance_fail_closed(self):
        rows=fake_month(2023,5,provider=None,source=None)
        panel=gov.build_governed_panel(rows)
        self.assertEqual(panel["quarantined_months"],["2023-05"])

    def test_duplicate_date_metal_rejected(self):
        rows=fake_month(2025,1)
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaisesRegex(RuntimeError,"DUPLICATE_DATE_METAL"):
            gov.build_governed_panel(rows)

    def test_nonfinite_and_negative_rejected(self):
        for price in (float("nan"),float("inf"),0,-20):
            rows=fake_month(2025,4)
            rows[0]["value"]=price
            with self.assertRaisesRegex(ValueError,"NONPOSITIVE_OR_NONFINITE"):
                gov.build_governed_panel(rows)

    def test_historical_gpr_vintage_not_mislabeled_as_pit(self):
        summary=gov.inspect_historical_gpr(["2022-03","2022-04"],start="2010-01",last="2022-04")
        self.assertEqual(summary["covered_origin_vintages"],2)
        self.assertGreater(summary["unverified_origin_vintages"],140)
        self.assertFalse(summary["pre-vintage_original_PIT_certified"])
        self.assertTrue(summary["older_historical_values_can_be_training_at_later_origin"])

    def test_missing_month_is_not_implicitly_filled(self):
        rows=fake_month(2023,1)+fake_month(2023,3)
        panel=gov.build_governed_panel(rows)
        self.assertEqual(panel["accepted_months"],["2023-01","2023-03"])
        self.assertNotIn("2023-02",panel["month_audit"])

    def test_clean_panel_preserves_price_values_and_date_order(self):
        rows=fake_month(2020,1)+fake_month(2020,2)
        panel=gov.build_governed_panel(list(reversed(rows)))
        dates=[r["day"] for r in panel["clean_four_metal_rows"]]
        self.assertEqual(dates,sorted(dates))
        self.assertEqual(panel["clean_four_metal_rows"][0]["prices"]["Gold"],1001)

if __name__=="__main__":
    unittest.main()
