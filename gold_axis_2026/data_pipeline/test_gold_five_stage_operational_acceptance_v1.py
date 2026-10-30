"""Offline acceptance tests: no future data, no false live promotion."""
import unittest
from datetime import date, datetime, timezone, timedelta
from gold_axis_2026.data_pipeline import gold_five_stage_operational_acceptance_v1 as gate

UTC=timezone.utc
NOW=datetime(2026,10,30,16,0,tzinfo=UTC)
def canonical(now=NOW):
    return [
       {"series_id":name,"quality_status":quality,
        "observation_ts":now-timedelta(days=1)}
       for name,(quality,_) in gate.REQUIRED.items()
    ]
def metal_rows(firstprint=False):
    out=[]
    start=date(2026,10,26)
    for i in range(4):
        for metal in gate.METALS:
            out.append({"price_date":start+timedelta(days=i),
               "metal":metal,
               "evidence_class":"FIRSTPRINT_PROSPECTIVE" if firstprint
                                else "PUBLIC_API_FETCH_NOT_ORIGIN_PIT",
               "first_observed_utc":datetime(2026,10,30,8,tzinfo=UTC)})
    return out
def stats():
    return {"weekly_live":0,"risk_live":0,
            "monthly_input_latest":date(2026,7,1),
            "monthly_forecast_latest":date(2026,10,1)}

class GoldAcceptanceTests(unittest.TestCase):
    def test_sources_current_but_issuance_never_certified(self):
        r=gate.evaluate(NOW,canonical(),metal_rows(),stats())
        self.assertEqual(r["stage1Data"]["canonicalFiveSeries"]["status"],"READY")
        self.assertEqual(r["stage1Data"]["sameSourceFourMetal"]["alignedDays"],4)
        self.assertEqual(r["stage1Data"]["sameSourceFourMetal"]["status"],
                         "WAIT_FOR_ORIGIN_FRIDAY_UTC_COMPLETION")
        self.assertEqual(r["status"],"BLOCKED_NOT_LIVE")
        self.assertFalse(r["promotionAllowed"])
        self.assertFalse(r["tradeAuthorized"])
        self.assertEqual(r["stage2Forecasts"]["weeklyLiveRecords"],0)
    def test_public_backfill_never_becomes_prospective(self):
        now=datetime(2026,11,1,16,tzinfo=UTC)
        r=gate.evaluate(now,canonical(now),metal_rows(),stats())
        self.assertEqual(r["stage1Data"]["sameSourceFourMetal"]["status"],
                         "BLOCKED_PUBLIC_SNAPSHOT_NOT_FIRSTPRINT")
        self.assertEqual(r["stage1Data"]["sameSourceFourMetal"]["unverifiedSourceRows"],16)
    def test_even_firstprint_cannot_certify_missing_model(self):
        now=datetime(2026,11,1,16,tzinfo=UTC)
        r=gate.evaluate(now,canonical(now),metal_rows(True),stats())
        self.assertEqual(r["stage1Data"]["sameSourceFourMetal"]["status"],
                         "INPUT_CANDIDATE_MODEL_NOT_VERIFIED")
        self.assertEqual(r["status"],"BLOCKED_NOT_LIVE")
    def test_broken_quality_and_staleness(self):
        rows=canonical()
        rows[0]["quality_status"]="UNAPPROVED"
        self.assertEqual(gate.feed_audit(NOW,rows)["status"],"BLOCKED")
        rows=canonical()
        rows[0]["observation_ts"]=NOW-timedelta(days=14)
        self.assertEqual(gate.feed_audit(NOW,rows)["series"][0]["status"],"STALE")
    def test_unzoned_future_and_duplicate_guard(self):
        rows=canonical()
        rows[0]["observation_ts"]=NOW+timedelta(days=1)
        self.assertEqual(gate.feed_audit(NOW,rows)["series"][0]["status"],"INVALID_ASOF")
        rows=metal_rows()
        rows.append(rows[0].copy())
        now=datetime(2026,11,1,16,tzinfo=UTC)
        self.assertEqual(gate.four_metal_audit(now,rows)["status"],"BLOCKED_INVALID_ORIGIN_ROWS")
    def test_true_fee_and_no_investment_approval(self):
        r=gate.evaluate(NOW,canonical(),metal_rows(),stats())
        self.assertEqual(r["stage4Positioning"]["buyFee"],0.008)
        self.assertEqual(r["stage4Positioning"]["sellFee"],0.008)
        self.assertFalse(r["stage4Positioning"]["ordersAllowed"])
if __name__=="__main__": unittest.main()
