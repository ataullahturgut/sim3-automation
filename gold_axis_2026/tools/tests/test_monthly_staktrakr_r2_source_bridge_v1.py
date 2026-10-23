"""Bridge safety tests: synthetic four-metal source panels and revision gates."""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gold_monthly_staktrakr_r2_source_bridge_v1 as bridge

def rows(month: str,ndates: int):
    from datetime import date,timedelta
    first=date.fromisoformat(month+"-01")
    out={}
    d=first
    while (d-first).days<ndates:
        for i,m in enumerate(bridge.METALS):
            out[(d.isoformat(),m)]={"price":1000.0+(d-first).days+i*300,
            "source":"sqld","provider":None,"source_timestamp":d.isoformat()+" 12:00:00"}
        d+=timedelta(days=1)
    return out

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.old=rows("2026-08",19)
        self.new=rows("2026-08",31)
        self.new.update(rows("2026-09",30))

    def test_recovery_both_months_but_not_live_certification(self):
        r=bridge.summarize(self.old,self.new)
        self.assertEqual(r["august_september"]["2026-08"]["complete_four_metal_dates"],31)
        self.assertEqual(r["august_september"]["2026-09"]["complete_four_metal_dates"],30)
        self.assertEqual(r["august_september"]["2026-08"]["complete_weekdays"],21)
        self.assertEqual(r["august_september"]["2026-09"]["complete_weekdays"],22)
        self.assertFalse(r["result_guard"]["auto_model_promotion"])

    def test_recovered_panel_is_research_only_and_dated_october(self):
        panel=bridge.candidate_four_metal_business_panel(self.new)
        self.assertEqual(panel["n_business_days"],43)
        self.assertEqual(panel["n_metal_prices"],172)
        self.assertEqual(panel["source_commit_date"],"2026-10-17")
        self.assertFalse(panel["first_publication_timestamp_verified"])
        self.assertFalse(panel["auto_model_promotion"])
        self.assertEqual(panel["business_rows"][0]["day"],"2026-08-03")

    def test_old_price_revisions_not_silently_discarded(self):
        changed=dict(self.new)
        z=changed[("2026-08-02","Gold")]
        changed[("2026-08-02","Gold")]={**z,"price":z["price"]+5.0}
        d=bridge.summarize(self.old,changed)
        self.assertEqual(d["old_new_revised_common_rows"],1)
        self.assertFalse(d["result_guard"]["real_time_asof_approved"])

    def test_incomplete_four_metals_rejected(self):
        missing=dict(self.new)
        del missing[("2026-09-15","Palladium")]
        with self.assertRaisesRegex(RuntimeError,"FOUR_METAL_DATE_MISMATCH"):
            bridge.summarize(self.old,missing)

    def test_insufficient_business_days_rejected(self):
        truncated={k:v for k,v in self.new.items() if k[0][:7]=="2026-08" or k[0]<="2026-09-15"}
        with self.assertRaisesRegex(RuntimeError,"MONTH_UNDER_20"):
            bridge.summarize(self.old,truncated)

    def test_old_observation_removal_rejected(self):
        missing=dict(self.new)
        del missing[("2026-08-03","Silver")]
        with self.assertRaisesRegex(RuntimeError,"OLDER_SOURCE_OBSERVATIONS_REMOVED"):
            bridge.summarize(self.old,missing)

if __name__=="__main__":unittest.main()
