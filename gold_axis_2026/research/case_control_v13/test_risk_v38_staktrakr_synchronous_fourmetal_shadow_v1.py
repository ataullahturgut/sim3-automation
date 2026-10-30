import unittest
from datetime import date,timedelta
from gold_axis_2026.research.case_control_v13.risk_v38_staktrakr_synchronous_fourmetal_shadow_v1 import flags,mature_calendar,SQL

class V38Safety(unittest.TestCase):
    def test_continuous_four_hours(self):
        self.assertIn("interval '4 hours'",SQL)
    def test_same_hour_metals(self):
        self.assertIn("au4<=-1 AND ag4<=-1 AND pt4<=-1 AND pd4<=-1",SQL)
    def test_old_v22_is_retained(self):
        x=flags(True,{"xau_hard":0,"four_same_1pct":0,"xau1_two_others1_5":0})
        self.assertTrue(all(x.values()))
    def test_fourmetal_can_warn_without_hard_gold(self):
        x=flags(False,{"xau_hard":0,"four_same_1pct":1,"xau1_two_others1_5":1})
        self.assertTrue(x["V22_OR_ALL_FOUR_NEGATIVE_ONE_PCT"])
        self.assertFalse(x["V22_OR_XAU4_HIST_THRESHOLD"])
    def test_future_only_label(self):
        start=date(2026,4,6)
        days=[start+timedelta(days=i) for i in [0,1,2,3,4,7,8,9]]
        rows=[{"date":d,"price":100 if i<5 else 96,"stak_price":100 if i<5 else 96} for i,d in enumerate(days)]
        x=mature_calendar(rows,"price")
        self.assertEqual(len(x),3)
        self.assertTrue(x[0]["outcome"])
    def test_future_price_difference(self):
        start=date(2026,4,6)
        days=[start+timedelta(days=i) for i in [0,1,2,3,4,7,8,9]]
        rows=[{"date":d,"price":100,"stak_price":100 if i!=1 else 94} for i,d in enumerate(days)]
        self.assertFalse(mature_calendar(rows,"price")[0]["outcome"])
        self.assertTrue(mature_calendar(rows,"stak_price")[0]["outcome"])
if __name__=="__main__":unittest.main()
