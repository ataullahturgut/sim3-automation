import unittest
import numpy as np
import pandas as pd
from gold_axis_2026.research.case_control_v13.risk_v50_regime_fitted_optimal_stopping import (
    next_session_checkpoint,five_step_maturity,training_selection,
    transition_targets,regime_probabilities,replay,REGIME_FIELDS,
    HORIZON_SESSIONS,RISKS,PERSISTENCES
)
class V50Tests(unittest.TestCase):
 def toy(self,n=800):
  t=pd.date_range("2025-01-01",periods=n,freq="15min",tz="UTC")
  frame=pd.DataFrame({"ts":t,"p":100+np.arange(n)*.002})
  frame["day"]=frame.ts.dt.date
  frame["session"]=np.repeat(np.arange((n+19)//20),20)[:n]
  return frame
 def test_next_session_same_offset(self):
  d=self.toy(120)
  j=next_session_checkpoint(d)
  self.assertEqual(j[0],20)
  self.assertEqual(j[10],30)
  self.assertEqual(j[19],39)
  self.assertEqual(j[-1],-1)
 def test_five_actual_sessions_mature(self):
  d=self.toy(120)
  j=next_session_checkpoint(d)
  m=five_step_maturity(j)
  self.assertEqual(m[0],100)
  self.assertEqual(m[19],119)
  self.assertEqual(m[20],-1)
 def test_regime_soft_weights_normalized(self):
  rng=np.random.default_rng(11)
  a=rng.normal(size=(600,3))
  w,meta=regime_probabilities(a[:300],a)
  self.assertEqual(w.shape,(600,3))
  np.testing.assert_allclose(w.sum(axis=1),1.,atol=1e-8)
  self.assertEqual(meta["trainingSize"],300)
 def test_transition_labels_have_correct_direction(self):
  d=self.toy(120)
  j=next_session_checkpoint(d)
  gain,draw,nxt=transition_targets(d.p.to_numpy(),j,np.array([0,1,2]))
  self.assertTrue(np.all(gain>0))
  self.assertTrue(np.all(draw==0))
  self.assertTrue((nxt>np.arange(3)).all())
 def test_training_selection_maturity_censor(self):
  d=self.toy(1000)
  j=next_session_checkpoint(d);m=five_step_maturity(j)
  # All observations and fully matured next five sessions only.
  s=training_selection(d,j,m,pd.Timestamp("2025-01-10"))
  self.assertGreater(len(s),0)
  self.assertTrue(np.all(m[s]>=0))
  self.assertTrue(all(d.ts.iloc[i]<pd.Timestamp("2025-01-10",tz="UTC") for i in m[s]))
 def test_adaptive_no_immediate_sale_before_v22_day(self):
  d=self.toy(150)
  diary={pd.Timestamp("2025-01-02").date():True}
  q=np.full(len(d),-.2)
  r=replay(d,diary,2025,q,1)
  self.assertEqual(r["riskWindows"],0) # No bar after the risk decision day
 def test_positive_fitted_continuation_causes_wait(self):
  d=self.toy(160)
  diary={pd.Timestamp("2025-01-01").date():True}
  q=np.full(len(d),.2)
  r=replay(d,diary,2025,q,1)
  self.assertEqual(r["signals"],0)
 def test_one_exit_per_watch(self):
  d=self.toy(160)
  diary={pd.Timestamp("2025-01-01").date():True}
  q=np.full(len(d),-.2)
  r=replay(d,diary,2025,q,1)
  self.assertEqual(r["signals"],1)
  self.assertEqual(r["events"][0]["signal"]["decision"],"EXIT_SIGNAL")
 def test_streak_requires_four_bars(self):
  d=self.toy(160)
  diary={pd.Timestamp("2025-01-01").date():True}
  q=np.full(len(d),.2)
  # WATCH opens Jan2. Toy first 20 bar session is 5 hours; calendar day rolls at index96.
  q[100:104]=-.2
  r=replay(d,diary,2025,q,4)
  self.assertEqual(r["signals"],1)
  self.assertEqual(r["events"][0]["signal"]["timeUTC"],str(d.ts.iloc[103]))
 def test_two_cost_weights_predeclared(self):
  self.assertEqual(RISKS,(.35,.8))
  self.assertEqual(HORIZON_SESSIONS,5)
  self.assertEqual(PERSISTENCES,(1,4))
if __name__=="__main__": unittest.main()
