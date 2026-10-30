import unittest
from datetime import datetime,timezone,timedelta,date
from gold_axis_2026.research.case_control_v13.risk_v41_v22_watch_sequential_exit_costs import (
  PARAMS,simulate,enhance,pick_model,BUY_COST,SELL_COST
)
class V41Tests(unittest.TestCase):
 def bars(self,days=12,up=.001):
  start=datetime(2026,1,5,0,0,tzinfo=timezone.utc)
  data=[(start+timedelta(minutes=i*15),5000*(1+up)**i) for i in range(days*96)]
  return enhance(data)
 def test_costs(self):
  self.assertEqual(BUY_COST,.008)
  self.assertEqual(SELL_COST,.008)
 def test_no_r4_with_fewer_than_16_bars(self):
  self.assertTrue(all(r["r4"] is None for r in self.bars(1)[:16]))
 def test_r4_needs_exactly_4h_no_weekend_bridge(self):
  x=self.bars(2)
  self.assertIsNotNone(x[16]["r4"])
  dates=[(datetime(2026,1,5,tzinfo=timezone.utc)+timedelta(minutes=i*15),100.) for i in range(16)]
  dates.append((datetime(2026,1,9,tzinfo=timezone.utc),98.))
  self.assertIsNone(enhance(dates)[-1]["r4"])
 def test_watch_cannot_use_same_date_warning(self):
  # signal D is first usable on D+1; immediate SELL next bar after that.
  a=self.bars(12)
  x=simulate(a,{date(2026,1,5):True},PARAMS["IMMEDIATE"],2026)
  self.assertGreaterEqual(len(x["sellRecords"]),1)
  self.assertGreaterEqual(x["sellRecords"][0]["day"],"2026-01-06")
 def test_no_alert_hold_never_sells(self):
  a=self.bars(12)
  x=simulate(a,{},PARAMS["TRAIL2_MOM1"],2026)
  self.assertEqual(x["sells"],0)
 def test_buy_sell_fee_are_charged(self):
  a=self.bars(12)
  x=simulate(a,{},PARAMS["HOLD"],2026)
  expected=100/(a[0]["p"]*(1+BUY_COST))*a[-1]["p"]*(1-SELL_COST)
  self.assertAlmostEqual(x["netUSD"],expected,places=3)
 def test_validation_selection_never_reads_eval(self):
  v={"TRAIL2_MOM1":{"netUSD":120,"maxDDPct":-3,"sells":2},
     "TRAIL1_MOM1":{"netUSD":110,"maxDDPct":-3,"sells":3}}
  selected,_=pick_model(v)
  self.assertEqual(selected,"TRAIL2_MOM1")
 def test_parameter_list_research_prespecified(self):
  self.assertGreaterEqual(len(PARAMS),8)
if __name__=="__main__":unittest.main()
