import unittest
from datetime import date,datetime,timedelta
import gold_risk_release_clock_v8 as c
class ReleaseClockTests(unittest.TestCase):
 def test_fed_monday_holidays(self):
  self.assertEqual(len(c.FED_H10_CLOSED_MONDAYS),25)
  for monday in c.FED_H10_CLOSED_MONDAYS:
   pub=c.next_h10_publication(monday-timedelta(days=3))
   self.assertEqual(pub.date(),monday+timedelta(days=1))
   self.assertEqual((pub.hour,pub.minute),(16,15))
 def test_jan2026_early_release_forbidden(self):
  self.assertEqual(c.next_h10_publication('2026-01-16').isoformat(),'2026-01-20T16:15:00-05:00')
  self.assertFalse(c.h10_is_available('2026-01-16',datetime(2026,1,20,16,14,tzinfo=c.NY)))
  self.assertTrue(c.h10_is_available('2026-01-16',datetime(2026,1,20,16,15,tzinfo=c.NY)))
 def test_2026_publisher_week_examples(self):
  for obs,rel in {'2026-02-13':'2026-02-17','2026-05-22':'2026-05-26','2026-09-04':'2026-09-08','2026-10-09':'2026-10-13'}.items():
   self.assertEqual(c.next_h10_publication(obs).date().isoformat(),rel)
 def test_regular_monday(self):
  self.assertEqual(c.next_h10_publication('2026-01-09').isoformat(),'2026-01-12T16:15:00-05:00')
 def test_tr0900_cannot_see_unreleased_h10(self):
  dt=datetime(2026,1,20,9,tzinfo=c.TR)
  self.assertFalse(c.h10_is_available('2026-01-16',dt))
  self.assertTrue(c.h10_is_available('2026-01-09',dt))
 def test_legacy_date_means_ny1730(self):
  self.assertFalse(c.h10_is_available('2026-01-16','2026-01-19'))
  self.assertTrue(c.h10_is_available('2026-01-16','2026-01-20'))
 def test_h15_still_lagged(self):
  self.assertFalse(c.h15_previous_day_is_available('2026-01-20','2026-01-20'))
  self.assertTrue(c.h15_previous_day_is_available('2026-01-20','2026-01-21'))
 def test_cftc_friday_1530_not_morning(self):
  self.assertFalse(c.cftc_published_is_available('2026-01-30',datetime(2026,1,30,9,tzinfo=c.TR)))
  self.assertTrue(c.cftc_published_is_available('2026-01-30',datetime(2026,1,30,17,30,tzinfo=c.NY)))
 def test_naive_clock_rejected(self):
  with self.assertRaises(ValueError):c.asof_instant(datetime(2026,1,20,9))
 def test_year_outside_source_calendar_fails(self):
  with self.assertRaises(ValueError):c.next_h10_publication('2027-01-01')
if __name__=='__main__':unittest.main()
