"""Offline no database: original V34 daily update strictly uses source days available."""
import unittest
from datetime import date,datetime,timezone
from gold_axis_2026.data_pipeline import gold_v34_weekday_conditioned_shadow_v1 as m

NOW=datetime(2026,11,4,9,0,tzinfo=timezone.utc)
def forecast(issued=datetime(2026,11,1,8,0,tzinfo=timezone.utc)):
    return {
      "target_week":date(2026,11,2),"origin_week":date(2026,10,26),
      "model_id":m.MODEL,"feature_dim":16,"training_weeks":875,
      "full_origin_week_complete":True,"source_utc_day_reference":m.REFERENCE,
      "is_prospective_firstprint":False,
      "historical_source_vintage_certified":False,
      "generated_at_utc":issued,
      "forecast_week_mean_usd_oz":4200
    }
def sample(d,price):
    return {"price_date":date.fromisoformat(d),"spot_usd_oz":price,
     "price_reference":m.REFERENCE,"evidence_class":"PUBLIC_API_FETCH_NOT_ORIGIN_PIT",
     "first_observed_utc":datetime(2026,11,int(d[-2:])+1,6,0,tzinfo=timezone.utc),
     "source_row_sha256":"a"*64}

class V34DayByDayTests(unittest.TestCase):
    def test_no_weekly_ANN_never_invents_prediction(self):
        z,rows=m.evaluate(NOW,None,[sample("2026-11-02",4000)])
        self.assertEqual(z["status"],"BLOCKED_NO_ORIGIN_FORECAST")
        self.assertEqual(rows,[])
        self.assertFalse(z["tradeAuthorized"])
    def test_completed_weekdays_only_and_explicit_5_day_projection(self):
        z,rows=m.evaluate(NOW,forecast(),[sample("2026-11-02",4000),sample("2026-11-03",4100)])
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]["conditionedWeekMeanUSD"],"4160")
        self.assertEqual(rows[1]["conditionedWeekMeanUSD"],"4140")
        self.assertEqual(rows[1]["observedWeekdays"],2)
        self.assertEqual(rows[1]["remainingWeekdays"],3)
        self.assertFalse(z["fitOrRetrainingOccurred"])
        self.assertFalse(z["prospectiveFirstprintCertified"])
    def test_monday_future_friday_and_lookahead_blocked(self):
        with self.assertRaisesRegex(RuntimeError,"INCOMPLETE_OR_REVISED"):
            m.evaluate(NOW,forecast(),[sample("2026-11-03",4100)])
        with self.assertRaisesRegex(RuntimeError,"ORIGIN_PRICE_DATE_NOT_UTC_COMPLETE"):
            m.evaluate(NOW,forecast(),[sample("2026-11-02",4000),
              sample("2026-11-03",4100),sample("2026-11-04",4110)])
        with self.assertRaisesRegex(RuntimeError,"FORECAST_CREATED_AFTER_WEEK_START"):
            m.evaluate(NOW,forecast(datetime(2026,11,2,5,tzinfo=timezone.utc)),[])
    def test_source_or_historical_ANN_cannot_be_promoted(self):
        x=forecast();x["is_prospective_firstprint"]=True
        with self.assertRaisesRegex(RuntimeError,"UNCERTIFIED_RESEARCH_CLAIMED_LIVE"):
            m.evaluate(NOW,x,[])
        x=forecast();x["source_utc_day_reference"]="XAU_EOD_TWELVE_NY17"
        with self.assertRaisesRegex(RuntimeError,"UNEXPECTED_PRICE_DEFINITION"):
            m.evaluate(NOW,x,[])
        d=sample("2026-11-02",4000);d["price_reference"]="XAU_EOD_TWELVE_NY17"
        with self.assertRaisesRegex(RuntimeError,"MIXED_PRICE_SOURCE"):
            m.evaluate(NOW,forecast(),[d])

if __name__=="__main__":unittest.main()
