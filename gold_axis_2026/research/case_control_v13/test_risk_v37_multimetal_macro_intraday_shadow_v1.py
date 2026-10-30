"""Temporal, feature-selection and 'no 2026 training' regression checks for V37."""
import unittest
from datetime import date,timedelta
from copy import deepcopy

from gold_axis_2026.research.case_control_v13.risk_v37_multimetal_macro_intraday_shadow_v1 import (
    prep_metal_rows, causal_context, flags, fixed_thresholds, _episodes
)

Q={"AG1":-2.0,"PT1":-2.0,"PD1":-2.5,
   "AG5":-4.0,"PT5":-4.0,"PD5":-5.0,
   "gvz1":1.1,"rate1":.07,"gvz":23.0,"worst4h":-1.8}

def fake_history():
    # 2024/2025 train + 2026 observation, no source assumptions.
    a=[]
    dt=date(2024,1,1)
    for n in range(540):
        day=dt+timedelta(days=n)
        a.append({"dt":day,"AU":2200.0+n,"AG":27.0+n*.01,
                  "PT":900.0+n*.1,"PD":1000.0+n*.15,
                  "gvz":20.0+(n%7)*.1,"rate":4.0+(n%3)*.01})
    return prep_metal_rows(a)

class V37Tests(unittest.TestCase):
    def test_no_intraday_is_sufficient_without_metal_confirmation(self):
        c={"metalContext":False,"macroContext":False}
        s=flags(False,True,c)
        self.assertTrue(s["V22_OR_4H"])
        self.assertFalse(s["V22_OR_4H_METALS"])
        self.assertFalse(s["V22_OR_4H_MACRO"])
    def test_original_v22_is_never_vetoed(self):
        c={"metalContext":False,"macroContext":False}
        self.assertTrue(flags(True,False,c)["V22_OR_4H_METALS"])
        self.assertTrue(flags(True,False,c)["V22_OR_4H_MACRO"])
    def test_metal_daily_values_are_lagged(self):
        a=fake_history()
        i=300
        before=causal_context(a,i,Q)
        a[i]["AG1"]=-200
        a[i]["AG5"]=-200
        after=causal_context(a,i,Q)
        self.assertEqual(before["metalContext"],after["metalContext"])
        self.assertEqual(before["lastMetalDate"],str(a[i-1]["dt"]))
    def test_macro_uses_at_least_two_days_lag(self):
        a=fake_history()
        i=300
        a[i-2]["gvz"]=50.0
        c=causal_context(a,i,Q)
        self.assertTrue(c["macroContext"])
        a[i-2]["gvz"]=15.0
        a[i-2]["gvz1"]=0
        a[i-2]["rate1"]=0
        a[i-1]["gvz"]=50.0
        c=causal_context(a,i,Q)
        self.assertFalse(c["macroContext"])
    def test_thresholds_cannot_read_test_year(self):
        a=fake_history()
        # Construct enough training days with numeric intraday data.
        a[520]["dt"]=date(2026,1,2)
        for j in range(521,540):
            a[j]["dt"]=date(2026,1,2)+timedelta(days=j-520)
        b={r["dt"]:{"worst4h":-.1-(i%10)*.15}
           for i,r in enumerate(a)}
        first=fixed_thresholds(a,b)
        for r in a:
            if r["dt"].year==2026:
                r["AG1"]=-500.0
                r["PT5"]=-500.0
                r["gvz1"]=500.0
                b[r["dt"]]["worst4h"]=-500.0
        second=fixed_thresholds(a,b)
        self.assertEqual(first,second)
    def test_no_duplicate_date_accepted(self):
        a=[{"dt":date(2026,5,20),"AU":4,"AG":3,"PT":2,"PD":1}]
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            prep_metal_rows(a+a)
    def test_episode_detection_uses_only_price_sequence(self):
        start=date(2026,5,1)
        original={}
        for i,px in enumerate([100,101,102,101,99,96,97,98,99]):
            original[start+timedelta(days=i)]={"modelPrice":px,"V22":False}
        e=_episodes(original)
        self.assertGreaterEqual(len(e),1)
        self.assertLessEqual(e[0]["worstFiveDayPct"],-4.0)

if __name__=="__main__":
    unittest.main()
