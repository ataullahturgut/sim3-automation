"""Cost accounting, no-lookahead event timing and cash/gold state tests."""
import unittest
from datetime import datetime,timedelta,timezone
from cash_gold_policy import simulate,context,parse,FEE,START

class CashGoldTests(unittest.TestCase):
    def setUp(self):
        self.params=dict(buy_1d=.3,buy_3d=-.5,sell_fast=-.8,trail=2.0,
                         max_1d_range=7.0,cooldown_h=12,calendar_gate=False)
        self.t=parse("2026-01-09T12:00:00Z")
        self.row=dict(close=2000.,next_open=2000.,r4h=.5,r1d=1.,r3d=2.,
                      r5d=3.,dd3d=-.2,range1d=2.)
    def test_buy_fee_and_sell_fee(self):
        rows=[dict(self.row,t=self.t),
              dict(self.row,t=self.t+timedelta(hours=3),close=2020.,next_open=2020.)]
        p=simulate(rows,[],self.params)
        self.assertEqual([x["side"] for x in p["trades"]],["BUY","SELL"])
        expected=100*(1-FEE)*2020/2000*(1-FEE)
        self.assertAlmostEqual(p["final"],expected,places=5)
        self.assertEqual(p["round_trips"],1)
    def test_no_buy_when_future_macro_announcement_is_near(self):
        events=[dict(t=self.t+timedelta(hours=2),id="NFP",kind="NFP",source="calendar")]
        x=dict(self.params,calendar_gate=True)
        out=simulate([dict(self.row,t=self.t)],events,x)
        self.assertEqual(out["trades"],[])
        self.assertAlmostEqual(out["final"],START)
        self.assertTrue(context(events,self.t)["near"])
        self.assertFalse(context(events,self.t-timedelta(hours=7))["near"])
    def test_shock_exit_uses_only_observed_bar(self):
        rows=[dict(self.row,t=self.t),
              dict(self.row,t=self.t+timedelta(hours=3),close=1940.,
                    next_open=1940.,r4h=-2.1,r1d=-2.,r3d=-1.)]
        p=simulate(rows,[],self.params)
        self.assertEqual(p["trades"][1]["reason"],"SELL_TRAILING_DRAW_DOWN")
        self.assertLess(p["final"],START)
    def test_no_shorts_and_initial_cash(self):
        rows=[dict(self.row,t=self.t,r1d=-1.,r3d=-1.),
              dict(self.row,t=self.t+timedelta(hours=3),r1d=-2.,r3d=-2.)]
        p=simulate(rows,[],self.params)
        self.assertEqual(p["final"],START)
        self.assertEqual(p["round_trips"],0)
        self.assertEqual(p["trades"],[])
    def test_timezone_normalization(self):
        self.assertEqual(parse("2026-01-09T15:00:00+03:00"),parse("2026-01-09T12:00:00Z"))
        with self.assertRaises(ValueError):
            parse("2026-01-09T15:00:00")

if __name__=="__main__": unittest.main()
