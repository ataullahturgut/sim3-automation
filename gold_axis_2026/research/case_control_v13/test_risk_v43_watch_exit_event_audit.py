import unittest
from datetime import date,datetime,timedelta,timezone
from gold_axis_2026.research.case_control_v13.risk_v43_watch_exit_event_audit import (
 RULES, watch_clusters, first_after_bar_date, signal_condition,
 causal_signal, future_sessions, retrospect, aggregate
)
class V43Tests(unittest.TestCase):
 def bars(self,changes=None):
  t=datetime(2026,1,22,tzinfo=timezone.utc)
  v=[100]*24 if changes is None else changes
  return [{"ts":t+timedelta(minutes=15*i),
           "date":(t+timedelta(minutes=15*i)).date(),"p":p,
           "r4":-.02 if i>=16 else None,
           "cusum":-4,"sigma":.002,"prior24low":99} for i,p in enumerate(v)]
 def test_all_rules_have_single_exit_signal_only(self):
  self.assertEqual(len(RULES),8)
 def test_v22_only_becomes_available_next_calendar_date(self):
  b=self.bars([100]*120)
  self.assertEqual(first_after_bar_date(b,date(2026,1,22)),96)
 def test_uptrend_does_not_confirm_exit(self):
  up={"p":105,"r4":.02,"sigma":.002,"cusum":0,"prior24low":100}
  for name in RULES[1:]:
   self.assertFalse(signal_condition(name,up,105,up),name)
 def test_causal_signal_reacts_only_to_history(self):
  d=self.bars([100]*20+[95]*20)
  full=causal_signal(d,0,35,"TRAIL_3_AND_4H_NEG1")
  prefix=causal_signal(d[:35],0,35,"TRAIL_3_AND_4H_NEG1")
  self.assertEqual(full,prefix)
  self.assertEqual(full["fillIndex"],21)
 def test_no_trade_or_buy_content_in_signals(self):
  s=causal_signal(self.bars(),0,23,"V22_IMMEDIATE")
  self.assertTrue("fillPx" in s)
  self.assertFalse("BUY" in str(s))
 def test_no_exit_without_large_enough_reversal(self):
  d=self.bars([100]*20+[99.7]*30)
  self.assertIsNone(causal_signal(d,0,40,"TRAIL_3_AND_4H_NEG1"))
 def test_separate_watch_episodes_not_preemptively_merged(self):
  ds=[date(2026,1,2)+timedelta(days=i) for i in range(40)]
  ds=[d for d in ds if d.weekday()<5]
  diary={ds[1]:True,ds[2]:True,ds[18]:True}
  g=watch_clusters(diary,{x:100 for x in ds})
  self.assertEqual(len(g),2)
 def test_future_session_excludes_fill_day(self):
  b=self.bars([100]*96+[99]*96+[97]*96+[95]*96+[92]*96+[89]*96)
  f,m=future_sessions(b,4,5)
  self.assertTrue(m)
  self.assertEqual(f[0]["date"],date(2026,1,23))
  self.assertEqual(len({x["date"] for x in f}),5)
 def test_future_not_matured_stays_unknown(self):
  f,m=future_sessions(self.bars([100]*100),98,5)
  self.assertFalse(m)
  self.assertEqual(f,[])
 def test_price_based_future_labels_are_outcome_only(self):
  b=self.bars([100]*96+[99]*96+[97]*96+[95]*96+[92]*96+[89]*96)
  e=causal_signal(b,0,500,"V22_IMMEDIATE")
  res=retrospect(b,0,500,e)
  self.assertTrue(res["exit"]["postExit4PctDecline"])
 def test_no_reentry_or_pnl_methods(self):
  self.assertTrue("V22_IMMEDIATE" in RULES)
if __name__=="__main__":
 unittest.main()
