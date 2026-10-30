import unittest
from datetime import datetime,date,timedelta,timezone
from gold_axis_2026.research.case_control_v13.risk_v41_v22_watch_sequential_exit_costs import enhance
from gold_axis_2026.research.case_control_v13.risk_v42_cost_aware_reentry_hysteresis import (
  replay,select,REENTRIES
)
class V42Tests(unittest.TestCase):
 def bars(self):
  start=datetime(2026,1,5,tzinfo=timezone.utc)
  b=[(start+timedelta(minutes=i*15),4200*(1+.00001)**i) for i in range(12*96)]
  return enhance(b)
 def test_no_alert_no_exit(self):
  r=replay(self.bars(),{},2026,"REENTER_24H")
  self.assertEqual(r["exits"],0)
 def test_selected_model_is_only_on_argument_validation(self):
  a={"REENTER_24H":{"netUSD":101,"maxDrawdownPct":-5,"trades":5},
     "NEVER_REENTER":{"netUSD":100,"maxDrawdownPct":-5,"trades":0}}
  self.assertEqual(select(a)[0][1],"REENTER_24H")
 def test_cash_days_have_equity_path_not_skipped(self):
  r=replay(self.bars(),{date(2026,1,5):True},2026,"REENTER_24H")
  self.assertGreater(len(r["dailyEquity"]),8)
 def test_costs_start_at_100_less_buy_fee(self):
  r=replay(self.bars(),{},2026,"NEVER_REENTER")
  expected=100*self.bars()[-1]["p"]/self.bars()[0]["p"]*(.992/1.008)
  self.assertAlmostEqual(r["netUSD"],expected,places=3)
 def test_no_future_lookahead_signal(self):
  d=self.bars()
  r=replay(d,{date(2026,1,5):True},2026,"NEVER_REENTER")
  self.assertTrue(all(x["date"]>"2026-01-05" for x in r["orders"]))
 def test_reentry_candidate_names_frozen(self):
  self.assertEqual(len(REENTRIES),11)
if __name__=="__main__":unittest.main()
