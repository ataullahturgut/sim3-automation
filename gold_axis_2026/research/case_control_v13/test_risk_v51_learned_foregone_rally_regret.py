import unittest
import numpy as np
import pandas as pd
from gold_axis_2026.research.case_control_v13.risk_v51_learned_foregone_rally_regret import (
    mature_training_rows,realized_regret_labels,RISK_WEIGHTS,MODES,
    UPSIDE_HORIZON_CALENDAR_DAYS,DOWNSIDE_HORIZON_SESSIONS
)
class V51Tests(unittest.TestCase):
 def df(self,prices=None,n=2500):
  if prices is None: prices=100+np.arange(n,dtype=float)*.0001
  t=pd.date_range("2022-01-01",periods=len(prices),freq="15min",tz="UTC")
  d=pd.DataFrame({"ts":t,"p":prices})
  d["session"]=np.repeat(np.arange((len(t)+31)//32),32)[:len(t)]
  return d
 def test_rally_outcome_and_downside_are_different_training_targets(self):
  price=np.full(2500,100.,dtype=float)
  price[602:650]=110
  price[651:700]=95
  d=self.df(prices=price)
  a,b=realized_regret_labels(d,np.array([600]))
  self.assertAlmostEqual(a[0],.1,places=5)
  self.assertAlmostEqual(b[0],.05,places=5)
 def test_flat_path_has_no_regret(self):
  a,b=realized_regret_labels(self.df(prices=np.full(2500,100)),np.array([600]))
  self.assertEqual(a[0],0)
  self.assertEqual(b[0],0)
 def test_negative_price_moves_only_downside(self):
  p=np.full(2500,100.,dtype=float);p[610:1200]=90
  a,b=realized_regret_labels(self.df(prices=p),np.array([600]))
  self.assertEqual(a[0],0)
  self.assertAlmostEqual(b[0],.1,places=4)
 def test_training_maturity_has_full_20_day_horizon(self):
  d=self.df(n=5500)
  origin=pd.Timestamp("2022-02-20")
  sample=mature_training_rows(d,origin)
  self.assertTrue(len(sample)>0)
  self.assertTrue(all(d.ts.iloc[int(i)]+pd.Timedelta(days=20)<origin.tz_localize("UTC") for i in sample))
 def test_no_buy_or_reentry(self):
  self.assertEqual(RISK_WEIGHTS,(1.0,1.5))
  self.assertTrue(all("BUY" not in m and "REENTRY" not in m for m in MODES))
  self.assertEqual(UPSIDE_HORIZON_CALENDAR_DAYS,20)
  self.assertEqual(DOWNSIDE_HORIZON_SESSIONS,5)
if __name__=="__main__":unittest.main()
