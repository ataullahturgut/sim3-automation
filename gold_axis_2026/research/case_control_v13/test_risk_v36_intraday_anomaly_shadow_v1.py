"""Offline fail-closed checks for risk_v36 intraday research."""
import unittest
from datetime import date,datetime,timedelta,timezone
from gold_axis_2026.research.case_control_v13.risk_v36_intraday_anomaly_shadow_v1 import (
 daily_features,percentile_linear,event_window,evaluate)
UTC=timezone.utc

def series(start,n,step=15,prices=None):
    a=start
    return [(a+timedelta(minutes=step*i),
             prices[i] if prices is not None else 100-0.1*i) for i in range(n)]
class Tests(unittest.TestCase):
    def test_pct_calibration_not_using_2026(self):
        self.assertEqual(percentile_linear([10,20,30],.5),20)
        self.assertAlmostEqual(percentile_linear([10,20,30],.05),11)
    def test_strict_intraday_utc(self):
        with self.assertRaisesRegex(ValueError,"UTC"):
            daily_features(series(datetime(2026,5,12),50))
    def test_bar_continuity_no_fake_four_hour(self):
        t=datetime(2026,5,12,tzinfo=UTC)
        raw=series(t,16)+series(t+timedelta(days=2),48)
        v=daily_features(raw)
        self.assertIsNotNone(v[date(2026,5,14)]["worst4h"])
        # A discontinuity cannot be joined directly as if bars were adjacent.
        discontinuity=series(t,10)+[(t+timedelta(days=2),60.0)]
        d=daily_features(discontinuity)
        self.assertEqual(d,{})
    def test_negative_prices_rejected(self):
        t=datetime(2026,5,12,tzinfo=UTC)
        with self.assertRaisesRegex(ValueError,"INVALID_PRICE"):
            daily_features([(t,-1)])
    def test_event_window_does_not_include_start_day(self):
        d={}
        for k in range(1,12):
            dy=date(2026,5,k)
            d[dy]={"worst1h":-4 if k==11 else -.01,
                   "worst4h":-4 if k==10 else -.01,
                   "first1h_at":"test","first4h_at":"test"}
        v=event_window(d,date(2026,5,11),-1,-1)
        self.assertTrue(v["anyPreStartCandidate"])
        self.assertEqual(len(v["preStartAnomalies"]),1)
        self.assertEqual(v["preStartAnomalies"][0]["date"],"2026-05-10")
    def test_one_hour_requires_four_15m_intervals(self):
        t=datetime(2026,5,12,tzinfo=UTC)
        prices=[100]*96
        prices[4]=98.7
        d=daily_features(series(t,96,prices=prices))
        self.assertLess(d[date(2026,5,12)]["worst1h"],-1.2)
        self.assertEqual(d[date(2026,5,12)]["bars"],96)
    def test_future_bars_cannot_rewrite_past_features(self):
        t=datetime(2026,5,12,tzinfo=UTC)
        past=series(t,96)
        ref=daily_features(past)[date(2026,5,12)]
        future=series(t+timedelta(days=1),96,prices=[400]*96)
        extended=daily_features(past+future)[date(2026,5,12)]
        self.assertEqual(ref,extended)
if __name__=="__main__":unittest.main()
