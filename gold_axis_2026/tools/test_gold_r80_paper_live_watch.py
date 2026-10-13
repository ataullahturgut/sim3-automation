#!/usr/bin/env python3
"""R80 smoke checks: observed movement, feed/vintage/spread guards, future-prefix invariance."""
import datetime as dt
import importlib.util
import pathlib
import unittest

SCRIPT=pathlib.Path(__file__).resolve().with_name("gold_r80_paper_live_watch.py")
spec=importlib.util.spec_from_file_location("gold_r80_paper_live_watch",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
UTC=dt.timezone.utc
START=dt.datetime(2026,10,13,6,0,tzinfo=UTC) # Tuesday 09 TR
def iso(t):return t.isoformat().replace("+00:00","Z")
def spot(i, delay=5):
    t=START+dt.timedelta(minutes=15*i)
    mid=4000+9*i
    return {"kind":"spot","event_at":iso(t),"received_at":iso(t+dt.timedelta(seconds=delay)),
            "instrument":"XAUUSD","provider":"TEST_SYNTHETIC_ONLY","bid":mid-.15,"ask":mid+.15}
def monthly():
    t=START-dt.timedelta(minutes=10)
    return {"kind":"monthly","event_at":iso(t),"received_at":iso(t+dt.timedelta(seconds=1)),
      "direction":"DOWN","target_month":"2026-10","evidence_class":"HISTORICAL_REPLAY"}

class R80SafetyTests(unittest.TestCase):
    def test_observed_onset_never_economic_advice(self):
        o=list(m.run([monthly()]+[spot(i) for i in range(19)]))
        self.assertEqual(len(o),19)
        self.assertTrue(any(x["observed_onset"]=="UP" for x in o))
        self.assertEqual({x["recommendation"] for x in o},{"BEKLE"})
        self.assertTrue(all(x["mode"]=="SHADOW_NO_TRADE" for x in o))
        self.assertTrue(all("NO_PROSPECTIVELY_VALIDATED_CONDITIONAL_ALPHA" in x["reason_codes"] for x in o))
        self.assertTrue(all(x["monthly_state_verified"] is None for x in o))
        self.assertTrue(o[-1]["matured_outcomes"]>0)
    def test_future_data_cannot_change_past_snapshot(self):
        a=list(m.run([spot(i) for i in range(9)]))
        b=list(m.run([spot(i) for i in range(19)]))
        self.assertEqual(a,b[:len(a)])
    def test_stale_quote_blocks_and_cannot_mature_labels(self):
        e=m.ShadowEngine()
        for i in range(8):e.accept(spot(i))
        old=len(e.matured)
        q=e.accept(spot(8,delay=7200))
        self.assertIn("STALE_SPOT_SOURCE",q["reason_codes"])
        self.assertEqual(q["recommendation"],"BEKLE")
        self.assertEqual(old,len(e.matured))
    def test_spoofed_monthly_and_bank_do_not_trigger_trade(self):
        t=START-dt.timedelta(minutes=10)
        mo={"kind":"monthly","event_at":iso(t),"received_at":iso(t+dt.timedelta(seconds=2)),
            "direction":"DOWN","target_month":"2026-10","evidence_class":"PROSPECTIVE_APPROVED"}
        bk={"kind":"bank","event_at":iso(t+dt.timedelta(minutes=1)),
            "received_at":iso(t+dt.timedelta(minutes=1,seconds=2)),
            "instrument":"XAUUSD","bid":3998.2,"ask":4001.8}
        xs=list(m.run([mo,bk]+[spot(i) for i in range(12)]))
        self.assertTrue(any(x["candidate_if_model_validated"]=="AL" for x in xs))
        self.assertEqual({x["recommendation"] for x in xs},{"BEKLE"})
    def test_no_future_quotes(self):
        bad=spot(0)
        bad["event_at"]=iso(START+dt.timedelta(minutes=10))
        with self.assertRaises(ValueError):m.parse(bad)

if __name__=="__main__":
    unittest.main()
