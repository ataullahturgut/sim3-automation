import unittest
import numpy as np
import pandas as pd
from gold_axis_2026.research.case_control_v13.risk_v52_physical_decline_episode_recall import (
  physical_crossings,earliest_eligible_risk_times,DRAW_THRESHOLD,REARM_THRESHOLD,TRAILING_SESSIONS
)
class V52PhysicalTests(unittest.TestCase):
 def df(self,p):
  n=len(p)
  d=pd.DataFrame({"ts":pd.date_range("2025-01-01",periods=n,freq="15min",tz="UTC"),
       "p":list(map(float,p))})
  d["session"]=np.repeat(np.arange((n+3)//4),4)[:n]
  return d
 def test_simple_four_percent_cross_is_independent_of_model(self):
  z=physical_crossings(self.df([100]*6+[97,95,94,93]+[93]*10))
  self.assertEqual(len(z),1)
  self.assertEqual(z[0]["crossingPrice"],95)
 def test_no_future_price_leak_in_prior_crossing(self):
  p=[100]*6+[97,95,94,93]+[93]*20
  a=physical_crossings(self.df(p))
  p2=list(p);p2[-10:]=[125]*10
  b=physical_crossings(self.df(p2))
  self.assertEqual(a[0],b[0])
 def test_rearm_requires_recovery(self):
  p=[100]*6+[95]*5+[99,100]*4+[95]*4
  x=physical_crossings(self.df(p))
  self.assertGreaterEqual(len(x),2)
 def test_warning_not_available_on_origin_date(self):
  d=self.df([100.]*200)
  d["day"]=d.ts.dt.date
  risk={pd.Timestamp("2025-01-01").date():True}
  t=earliest_eligible_risk_times(d,risk)
  self.assertEqual(len(t),1)
  self.assertEqual(t[0],pd.Timestamp("2025-01-02",tz="UTC"))
 def test_origin_risk_without_next_market_bar_is_not_counted(self):
  d=self.df([100.]*20)
  d["day"]=d.ts.dt.date
  risk={pd.Timestamp("2025-01-01").date():True}
  self.assertEqual(earliest_eligible_risk_times(d,risk),[])
 def test_parameters_frozen_not_model_optimized(self):
  self.assertEqual(DRAW_THRESHOLD,.04)
  self.assertEqual(REARM_THRESHOLD,.02)
  self.assertEqual(TRAILING_SESSIONS,5)
if __name__=="__main__":unittest.main()
