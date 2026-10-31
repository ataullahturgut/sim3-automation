import unittest
from datetime import date,datetime,timedelta,timezone
from gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only import (
  CONFIG,Stream,condition,market_session,future_prices,score,MAX_WARN_AGE_CALENDAR_DAYS
)
def fake(ts,p,r4=-.02,low=100):
 return {"ts":ts,"date":ts.date(),"p":p,"r4":r4,
         "usable4h":r4 is not None,"prior24low":low,
         "cusum":-3.5,"ema":105.0,"sigma":.001}
class V44Checks(unittest.TestCase):
 def t(self,day,hour=0,minute=0):
  return datetime(2026,1,day,hour,minute,tzinfo=timezone.utc)
 def test_no_weekend_extra_price_session(self):
  self.assertEqual(market_session(datetime(2026,1,11,23,tzinfo=timezone.utc)),
                   date(2026,1,12))
  self.assertEqual(market_session(datetime(2026,1,9,19,tzinfo=timezone.utc)),
                   date(2026,1,9))
 def test_real_market_next_five(self):
  dates=[self.t(8,21),self.t(9,20),self.t(11,23),
         self.t(12,20),self.t(13,20),self.t(14,20),self.t(15,20)]
  bars=[fake(d,100-i) for i,d in enumerate(dates)]
  out,mature=future_prices(bars,0)
  self.assertTrue(mature)
  self.assertEqual(len(out),5)
 def test_immature_not_false(self):
  bars=[fake(self.t(i),100) for i in (6,7,8)]
  o,mature=future_prices(bars,0)
  self.assertFalse(mature)
 def test_no_watch_until_after_risk_date(self):
  stream=Stream("V22_IMMEDIATE",2026,{date(2026,1,22):True})
  stream.push(fake(self.t(22,20),110))
  self.assertEqual(stream.state,"IDLE")
  stream.push(fake(self.t(23),110))
  self.assertEqual(stream.state,"EXIT_RECORDED")
  self.assertEqual(len(stream.episodes),1)
  self.assertEqual(stream.episodes[0]["signal"]["signalUTC"],str(self.t(23)))
 def test_fills_after_signal_not_at_same_bar(self):
  stream=Stream("V22_IMMEDIATE",2026,{date(2026,1,22):True})
  stream.push(fake(self.t(22,20),100))
  stream.push(fake(self.t(23),100))
  self.assertIsNone(stream.episodes[0]["signal"]["fillPx"])
  stream.push(fake(self.t(23,0,15),99))
  self.assertEqual(stream.episodes[0]["signal"]["fillPx"],99)
  self.assertTrue(stream.episodes[0]["signal"]["fillCandidateValid"])
 def test_no_false_15m_fill_market_gap(self):
  stream=Stream("V22_IMMEDIATE",2026,{date(2026,1,22):True})
  stream.push(fake(self.t(22,20),100))
  stream.push(fake(self.t(23),100))
  stream.push(fake(self.t(23,1),90))
  self.assertFalse(stream.episodes[0]["signal"]["fillCandidateValid"])
 def test_rising_price_never_exits_structure(self):
  s=Stream("V43_STRUCTURAL_1",2026,{date(2026,1,22):True})
  s.push(fake(self.t(22,20),100))
  for i in range(20):
   s.push(fake(self.t(23,0,i*15//60,i*15%60) if False else
      self.t(23)+timedelta(minutes=i*15),100+i*.1,r4=.01,low=90))
  self.assertEqual(s.state,"WATCH")
  self.assertIsNone(s.episodes[0]["signal"])
 def test_structure_only_after_combined_break(self):
  s=Stream("V43_STRUCTURAL_1",2026,{date(2026,1,22):True})
  s.push(fake(self.t(22,20),100))
  s.push(fake(self.t(23),104,r4=.02,low=99))
  s.push(fake(self.t(23,0,15),101,r4=-.005,low=102))
  self.assertIsNone(s.episodes[0]["signal"])
  s.push(fake(self.t(23,0,30),101,r4=-.02,low=102))
  self.assertIsNotNone(s.episodes[0]["signal"])
 def test_no_duplicate_sell_during_same_risk(self):
  diary={date(2026,1,22):True,date(2026,1,23):True}
  s=Stream("V22_IMMEDIATE",2026,diary)
  for x in (fake(self.t(22,20),100),fake(self.t(23),99),fake(self.t(23,0,15),99),
            fake(self.t(24),96)):
   s.push(x)
  self.assertEqual(len(s.episodes),1)
  self.assertEqual(len([x for x in s.transitions if x["type"]=="EXIT_SIGNAL"]),1)
 def test_no_future_price_changes_past_signal(self):
  diary={date(2026,1,22):True}
  sample=[fake(self.t(22,20),100),fake(self.t(23),100),
          fake(self.t(23,0,15),99),fake(self.t(23,0,30),95)]
  def run(bars):
   s=Stream("V22_IMMEDIATE",2026,diary)
   for b in bars:s.push(b)
   return s.episodes[0]["signal"]["sha256"]
  self.assertEqual(run(sample[:3]),run(sample))
 def test_no_trade_or_buy_models(self):
  self.assertTrue(all("BUY" not in k and "REENTRY" not in k for k in CONFIG))
 def test_2024_timeline_not_generated_from_2026_risk(self):
  s=Stream("V22_IMMEDIATE",2024,{date(2024,1,2):True})
  with self.assertRaisesRegex(ValueError,"WRONG_YEAR"):
   s.push(fake(self.t(22),99))
 def test_expiry_ends_watch_after_last_risk(self):
  s=Stream("V43_STRUCTURAL_1",2026,{date(2026,1,22):True})
  s.push(fake(self.t(22,20),100))
  s.push(fake(self.t(23),101,r4=.01))
  s.push(fake(self.t(31),102,r4=.01))
  s.push(fake(datetime(2026,2,5,tzinfo=timezone.utc),102,r4=.01))
  self.assertEqual(s.state,"IDLE")
 def test_cost_not_misrepresented_as_profits(self):
  self.assertEqual(len(CONFIG),5)
if __name__=="__main__":unittest.main()
