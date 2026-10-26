"""Acceptance tests for explanation-only risk BI; no classifier or changed signals."""
import json
from pathlib import Path
import unittest
import pandas as pd

ROOT=Path(__file__).parent
OUT=ROOT/"outputs"


class BusinessIntelligenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=pd.read_csv(OUT/"v15_daily_intelligence.csv")
        cls.p=pd.read_csv(OUT/"v15_parameter_trace.csv")
        cls.h=pd.read_csv(OUT/"v15_historical_cases_and_controls.csv")
        cls.audit=json.loads((OUT/"v15_audit.json").read_text())
        cls.orig=pd.read_csv(OUT/"daily_core_models.csv")

    def test_original_alerts_identical_each_origin(self):
        a=self.d.set_index(["origin","model"]).sort_index()
        b=self.orig[self.orig.model.isin(["BASE14","CFTC21"])].set_index(["origin","model"]).sort_index()
        self.assertEqual(set(a.index),set(b.index))
        for key in a.index:
            self.assertEqual(a.loc[key,"alert_level"]=="RED",str(b.loc[key,"red"]).lower()=="true")

    def test_original_performance_metrics_unchanged(self):
        for year,expected in [(2025,{"BASE14":(32,27),"CFTC21":(21,17)}),
                              (2026,{"BASE14":(50,40),"CFTC21":(32,25)})]:
            for model,(n,wrong) in expected.items():
                d=self.d[(self.d.origin.str[:4]==str(year))&(self.d.model==model)]
                red=d[d.alert_level=="RED"]
                self.assertEqual(len(red),n)
                self.assertEqual(int((~red.future_drop5_AUDIT_ONLY).sum()),wrong)

    def test_2013_events_in_casebook(self):
        e=self.h[self.h.type=="PRE_DECLINE_PEAK"]
        self.assertEqual(len(e),27)
        self.assertEqual(len(e[e.peak.str.startswith("2013")]),5)
        self.assertEqual(len(self.h[self.h.type=="MATCHED_NO_DROP"]),81)

    def test_historical_analogue_does_not_modify_alerts(self):
        a=pd.read_csv(OUT/"v15_historical_parameter_analogues.csv")
        self.assertTrue((a.nearest_historic_crash_date.str[:4].astype(int)<=2022).all())
        self.assertTrue((a.nearest_historic_no_crash_date.str[:4].astype(int)<=2022).all())
        self.assertFalse(a.historical_analog_used_to_change_alarm.any())
        self.assertTrue(a.does_not_estimate_future_drop_probability.all())
        existing=self.d[self.d.alert_level=="RED"]
        self.assertEqual(len(a),len(existing))

    def test_no_new_prediction_model(self):
        self.assertFalse(self.audit["classifier_or_forecast_trained"])
        self.assertFalse(self.audit["added_alarm_rule"])
        self.assertFalse(self.audit["original_BASE14_CFTC21_levels_changed"])
        self.assertFalse(self.audit["first_print_PIT_certified"])
        self.assertFalse(self.audit["neon_modified"])
        self.assertFalse(self.d.changes_original_alert.any())
        self.assertFalse(self.d.new_prediction_model.any())

    def test_every_origin_has_all_original_parameters(self):
        c=self.p.groupby(["origin","model"]).size()
        self.assertEqual(set(c.loc[pd.IndexSlice[:,"BASE14"]].unique()),{14})
        self.assertEqual(set(c.loc[pd.IndexSlice[:,"CFTC21"]].unique()),{21})
        self.assertEqual(len(self.d),786)

    def test_frozen_thresholds(self):
        for (model,period),g in self.d.groupby(["model",self.d.origin.str[:4]]):
            self.assertEqual(g.red_threshold.nunique(),1)
            self.assertEqual(g.yellow_threshold.nunique(),1)
            self.assertTrue((g.red_threshold>g.yellow_threshold).all())

    def test_no_outcome_in_model_inputs(self):
        import inspect
        import risk_v15_business_intelligence as bi
        code=inspect.getsource(bi.explain_models).split("records.append")[0]
        self.assertNotIn("GradientBoosting",code)
        self.assertNotIn("LogisticRegression",code)
        self.assertNotIn("future_drop5_AUDIT_ONLY",code)
        self.assertNotIn("future_5day_min_pct_AUDIT_ONLY",code)

if __name__=="__main__":
    unittest.main(verbosity=2)
