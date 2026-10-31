import unittest
from datetime import datetime,timezone,timedelta
import pandas as pd
import numpy as np
from gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation import (
 FEATURES,TARGET_DOWN,TARGET_UP,FUTURE_SESSIONS,THRESHOLD_QUANTILES,
 first_hit_down_label,feature_frame
)
class V47Tests(unittest.TestCase):
 def synthetic(self,values,sessions=None):
  n=len(values)
  data=pd.DataFrame({"ts":pd.date_range("2022-01-03",periods=n,freq="15min",tz="UTC"),
       "p":list(map(float,values))})
  data["session"]=np.repeat(np.arange((n+3)//4),4)[:n] if sessions is None else sessions
  return data
 def test_label_drop_before_rise_is_one(self):
  p=[100]*4+[95]*4+[104]*16
  df=self.synthetic(p)
  label=first_hit_down_label(df,np.array([0]))
  self.assertEqual(int(label[0]),1)
 def test_label_rally_before_drop_is_zero(self):
  p=[100]*4+[103]*4+[94]*16
  df=self.synthetic(p)
  self.assertEqual(int(first_hit_down_label(df,np.array([0]))[0]),0)
 def test_no_both_barriers_is_zero(self):
  df=self.synthetic([100]*24)
  self.assertEqual(int(first_hit_down_label(df,np.array([0]))[0]),0)
 def test_immature_future_not_training_label(self):
  df=self.synthetic([100]*20)
  self.assertEqual(int(first_hit_down_label(df,np.array([0]))[0]),-1)
 def test_current_bar_cannot_trigger_lookahead(self):
  df=self.synthetic([100]*4+[95]*4+[105]*16)
  a=first_hit_down_label(df,np.array([0]))
  b=df.copy()
  b.loc[5:,"p"]=500.0
  self.assertEqual(len(a),1)
  self.assertNotEqual(int(a[0]),int(first_hit_down_label(b,np.array([0]))[0]))
 def test_feature_frame_does_not_use_future_data(self):
  p=[100+0.01*i for i in range(600)]
  df=self.synthetic(p)
  f=feature_frame(df)
  df.loc[540:,"p"]*=5
  f2=feature_frame(df)
  np.testing.assert_array_equal(f.iloc[:540].to_numpy(),f2.iloc[:540].to_numpy())
 def test_feature_list_and_quantiles_frozen(self):
  self.assertEqual(len(FEATURES),17)
  self.assertEqual(THRESHOLD_QUANTILES,(.7,.8,.9,.95))
 def test_synthetic_market_length(self):
  self.assertEqual(FUTURE_SESSIONS,5)
  self.assertEqual(TARGET_DOWN,.04)
  self.assertEqual(TARGET_UP,.02)
if __name__=="__main__":unittest.main()
