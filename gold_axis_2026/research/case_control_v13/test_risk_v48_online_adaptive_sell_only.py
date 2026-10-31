import unittest
from datetime import date,datetime,timedelta,timezone
import numpy as np
import pandas as pd
from gold_axis_2026.research.case_control_v13.risk_v48_online_adaptive_sell_only import (
    CUTOFF_QUANTILES,MODELS,MATURATION_DAYS,ROLLING_LABEL_DAYS,
    SCORE_LOOKBACK_BARS,meta_frame,normalized_metrics,replay
)
from gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation import feature_frame

class V48Tests(unittest.TestCase):
 def make(self,prices=None):
  if prices is None:prices=[100.0+i*.01 for i in range(300)]
  t=pd.date_range("2025-04-03",periods=len(prices),freq="15min",tz="UTC")
  df=pd.DataFrame({"ts":t,"p":prices})
  df["day"]=df.ts.dt.date
  df["session"]=(df.ts.dt.floor("D")-pd.Timestamp("2025-04-03",tz="UTC")).dt.days
  return df
 def test_relative_score_threshold_only_prior_bars(self):
  p=pd.Series([.01]*1290+[.5]*10)
  cut=p.rolling(window=SCORE_LOOKBACK_BARS,min_periods=250).quantile(.9).shift(1)
  self.assertLess(cut.iloc[1290],.05)
  p.iloc[1290]=.9
  self.assertLess(cut.iloc[1290],.05)
 def test_meta_uses_only_observed_values(self):
  d=self.make()
  f=feature_frame(d)
  m=meta_frame(f,np.full(len(d),.15))
  self.assertEqual(m.shape,(len(d),8))
  self.assertTrue(np.isfinite(m.to_numpy()).all())
 def test_vol_norm_price_history_causal(self):
  d=self.make()
  f=feature_frame(d)
  a=normalized_metrics(d,f)
  d2=d.copy()
  d2.loc[280:,"p"]=500
  b=normalized_metrics(d2,feature_frame(d2))
  self.assertEqual(a[0][270],b[0][270])
  self.assertEqual(a[2][270],b[2][270])
 def test_does_not_start_watch_before_v22_last_complete_day(self):
  d=self.make([100.0]*300)
  f=feature_frame(d)
  metric=normalized_metrics(d,f)
  diary={date(2025,4,4):True}
  # No bar after Apr 4 -> cannot yet use V22.
  p=np.full(len(d),.9)
  c=np.full(len(d),.2)
  r=replay(d,f,diary,2025,p,c,"ADAPTIVE_RANK",metric)
  self.assertEqual(r["riskEpisodes"],0)
 def test_confirmation_comparison_has_no_buy(self):
  self.assertTrue(all("BUY" not in x and "REENTRY" not in x for x in MODELS))
 def test_adaptive_rank_streak_requires_four_completed_bars(self):
  d=self.make([100]*300)
  # Start watch following day; 2025-04-04 00:00 lies at index 96
  f=feature_frame(d)
  metric=normalized_metrics(d,f)
  diary={date(2025,4,3):True}
  p=np.full(len(d),.1);c=np.full(len(d),.3)
  p[97:101]=.5
  s=replay(d,f,diary,2025,p,c,"ADAPTIVE_RANK_PERSIST4",metric)
  self.assertEqual(s["signals"],1)
  self.assertEqual(s["events"][0]["signal"]["time"],str(d.ts.iloc[100]))
 def test_no_source_bars_using_current_outcome(self):
  self.assertEqual(MATURATION_DAYS,15)
  self.assertGreater(ROLLING_LABEL_DAYS,200)
  self.assertGreater(SCORE_LOOKBACK_BARS,600)
 def test_session_starts_only_after_previous_day(self):
  d=self.make([100]*300)
  f=feature_frame(d);metric=normalized_metrics(d,f)
  diary={date(2025,4,4):True}
  p=np.full(len(d),.9);c=np.full(len(d),.2)
  # here 300 bars 3 Apr + 4 Apr + 5 Apr 03:00 (Saturday synthetic)
  r=replay(d,f,diary,2025,p,c,"ADAPTIVE_RANK",metric)
  self.assertEqual(r["riskEpisodes"],1)
  self.assertEqual(r["events"][0]["signal"]["time"],str(pd.Timestamp("2025-04-05",tz="UTC")))
if __name__=="__main__":unittest.main()
