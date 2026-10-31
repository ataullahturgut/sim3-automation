import unittest
import numpy as np
import pandas as pd
from gold_axis_2026.research.case_control_v13.risk_v49_online_three_class_exit import (
  competing_labels,QS,META_FEATURES,MATURITY,LOOKBACK
)
class V49Tests(unittest.TestCase):
 def make(self,seq):
  d=pd.DataFrame({"ts":pd.date_range("2022-01-01",periods=len(seq),freq="15min",tz="UTC"),
     "p":list(map(float,seq))})
  d["session"]=np.repeat(np.arange((len(d)+3)//4),4)[:len(d)]
  return d
 def test_earlier_up_barrier_win(self):
  d=self.make([100]*4+[103]*4+[93]*16)
  self.assertEqual(competing_labels(d,np.array([0])).tolist(),[2])
 def test_earlier_down_barrier_win(self):
  d=self.make([100]*4+[95]*4+[103]*16)
  self.assertEqual(competing_labels(d,np.array([0])).tolist(),[1])
 def test_neither_barrier_win(self):
  d=self.make([100]*24)
  self.assertEqual(competing_labels(d,np.array([0])).tolist(),[0])
 def test_future_not_matured(self):
  d=self.make([100]*20)
  self.assertEqual(competing_labels(d,np.array([0])).tolist(),[-1])
 def test_training_cannot_use_unmatured_targets(self):
  self.assertEqual(MATURITY,15)
  self.assertEqual(LOOKBACK,540)
 def test_rolling_scores_preserve_tradeoff(self):
  a=.09;b=.36
  self.assertAlmostEqual(a/(a+b),.2)
 def test_mode_and_quantiles(self):
  self.assertEqual(QS,(.8,.9,.95))
  self.assertIn("ret24h",META_FEATURES)
if __name__=="__main__":unittest.main()
