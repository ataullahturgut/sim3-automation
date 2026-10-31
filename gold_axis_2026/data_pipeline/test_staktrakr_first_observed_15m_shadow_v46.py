import unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import json
from gold_axis_2026.data_pipeline import staktrakr_first_observed_15m_shadow_v46 as m

class FutureCollectorTests(unittest.TestCase):
 def now(self,y=2026,mo=10,d=30,h=10,mn=52):
  return datetime(y,mo,d,h,mn,tzinfo=timezone.utc)
 def test_date_aware_market_gate(self):
  self.assertTrue(m.market_open(self.now()))
  self.assertFalse(m.market_open(self.now(d=31)))
  self.assertFalse(m.market_open(self.now(d=31,h=2)))
 def test_sunday_ny17_open(self):
  self.assertTrue(m.market_open(self.now(y=2026,mo=11,d=1,h=22,mn=30)))
  self.assertFalse(m.market_open(self.now(y=2026,mo=11,d=1,h=20,mn=30)))
 def test_previous_complete_quarter_window(self):
  a=m.windows(self.now())
  self.assertEqual(a[0],self.now(mn=30).replace(second=0,microsecond=0))
  self.assertEqual(a[1],self.now(mn=15).replace(second=0,microsecond=0))
  self.assertEqual(len(a),5)
 def test_original_firstprint_never_declared(self):
  self.assertIn("original_provider_firstprint_certified=false",m.DDL)
  self.assertIn("is_production_signal=false",m.DDL)
  self.assertNotIn("DO UPDATE",m.INSERT)
 def test_recent_provider_quote_is_not_production_risk(self):
  q=m.quality(self.now(),self.now(mn=30))
  self.assertTrue(q["recent"])
  self.assertTrue(q["eligibleForFutureMonitoring"])
 def test_old_archive_cannot_claim_fresh(self):
  q=m.quality(self.now(),self.now(h=9))
  self.assertFalse(q["recent"])
  self.assertFalse(q["eligibleForFutureMonitoring"])
 def test_future_quote_rejected(self):
  with self.assertRaises(ValueError):
   m.quality(self.now(),self.now()+timedelta(minutes=4))
 def test_weekend_snapshot_not_live_market(self):
  now=self.now(d=31)
  q=m.quality(now,now-timedelta(minutes=15))
  self.assertFalse(q["marketOpen"])
  self.assertFalse(q["eligibleForFutureMonitoring"])
 def test_fresh_snapshot_quality_recorded(self):
  now=self.now()
  snap=[
   {"metal":metal,"spot":spot,"provider":"StakTrakr",
    "source":"seed","timestamp":"2026-10-30 10:30:01"}
    for metal,spot in (("Gold",4100),("Silver",50),
                       ("Platinum",1500),("Palladium",1000))
  ]
  with patch.object(m,"get_source",return_value=(json.dumps(snap).encode(),
                                "https://raw.githubusercontent.com/test.json")):
   rows,source,errs=m.retrieve(now)
  self.assertEqual(len(rows),4)
  self.assertEqual(len(errs),0)
  self.assertTrue(source["quotes"]["AU"]["marketOpen"])
  self.assertEqual(rows[0]["source_quote_timestamp_utc"],"2026-10-30T10:30:01+00:00")
 def test_dedupe_not_fake_live_exit(self):
  self.assertIn("ON CONFLICT(metal,window_start_utc,source_row_sha256) DO NOTHING",m.INSERT)
  self.assertNotIn("INSERT INTO gold_weekly_live.downside_signal_records",m.INSERT)
if __name__=="__main__":unittest.main()
