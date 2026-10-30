import unittest
from datetime import date,timedelta
from gold_axis_2026.research.case_control_v13.risk_v39_ridge_prior_fourmetal_confirmation import (
 FEATURES,add_features,label_targets,emitted_episodes,episode_stats,calibrate_threshold
)
class V39SafetyTests(unittest.TestCase):
 def source(self):
  d=date(2024,1,1)
  return [{"date":d+timedelta(days=i),
   "au":100+i*.01,"ag":20+i*.01,"pt":900+i*.02,"pd":800+i*.03,
   "gvz":20+(i%4)*.1,"rate":4.0+(i%5)*.02} for i in range(30)]
 def test_at_least_four_metal_features(self):
  self.assertTrue(all(x in FEATURES for x in ("ag_ret1","pt_ret1","pd_ret1","au_ret1")))
 def test_future_change_does_not_change_past_features(self):
  p=self.source()
  f=add_features(p)[4]["features"].copy()
  for i in range(17,len(p)):
   p[i]["ag"]=10000
   p[i]["gvz"]=10000
  self.assertEqual(f,add_features(p)[4]["features"])
 def test_last_metal_is_previous_price_day(self):
  p=self.source()
  v=add_features(p)
  self.assertEqual(v[0]["lastSourceDay"],p[11]["date"])
  self.assertEqual(v[0]["lastMacroDay"],p[10]["date"])
 def test_2024_label_embargo(self):
  p=self.source()
  for n,r in enumerate(p):
   r["date"]=date(2024,12,15)+timedelta(days=n)
  f=add_features(p)
  l=label_targets(f)
  self.assertTrue(all(r["date"]<=date(2024,12,26) for r in l if r["date"].year==2024))
 def test_episode_suppression_not_improving_day_labels(self):
  d=date(2025,1,1)
  a=[{"date":d+timedelta(days=i),"au":100.0} for i in range(22)]
  x=emitted_episodes(a,lambda r:True,quiet=8)
  self.assertEqual([i for i,_ in x],[0,9,18])
 def test_threshold_uses_validation_only(self):
  d=date(2025,1,1)
  a=[{"date":d+timedelta(days=i),"au":100.0,
      "riskProb":i/20} for i in range(20)]
  th,stats=calibrate_threshold(a,[r["riskProb"] for r in a],budget=2)
  self.assertTrue(0<=th<=1)
  self.assertLessEqual(stats["noHitNext5"],2)
if __name__=="__main__":unittest.main()
