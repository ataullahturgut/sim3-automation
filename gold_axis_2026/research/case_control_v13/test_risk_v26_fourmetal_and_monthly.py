"""Cross-check each permanent V26 four-metal and monthly source-vintage artifact."""
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
import risk_v26_monthly_models_sensitivity as m
from risk_v26_fourmetal_external_comparison import internal_snapshot
from risk_v25_price_health_gate import verify as v25

O=m.OUT

class DataHealthAndCausalModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.daily=m.immutable_prices()
        cls.vintages=m.origin_histories()
        cls.by={sc:m.construct(cls.daily,sc,cls.vintages) for sc in m.SCENARIOS}
    def test_full_fourmetal_intersection_and_no_negative_prices(self):
        self.assertEqual(len(self.daily),4234)
        self.assertTrue((self.daily[["AU","AG","PT","PD"]]>0).all().all())
        self.assertEqual(len(self.daily.date.unique()),4234)
    def test_annual_independent_checks_cover_all_four(self):
        z=pd.read_csv(O/"v26_independent_all_fourmetals_annual_checks.csv")
        self.assertEqual(len(z),68)
        self.assertEqual(set(z.metal),{"AU","AG","PT","PD"})
        self.assertEqual(int(z.external_matched.sum()),16837)
        self.assertEqual(int(z.differences_gt_5pct.sum()),30)
        self.assertEqual(int(z.loc[z.metal.eq("AG")&z.year.le(2025),"differences_gt_5pct"].sum()),0)
    def test_quarantined_Feb_2026_never_backfilled(self):
        self.assertEqual(len(self.by["RAW_UNTOUCHED"].daily_month_values["Gold"]["2026-02"]),20)
        self.assertEqual(len(self.by["CENSORED_ONE_DAY"].daily_month_values["Gold"]["2026-02"]),19)
        self.assertEqual(len(self.by["EXTERNAL_CLOSE_ONLY_SENSITIVITY"].daily_month_values["Gold"]["2026-02"]),20)
        raw=self.by["RAW_UNTOUCHED"].monthly_metal
        cen=self.by["CENSORED_ONE_DAY"].monthly_metal
        self.assertAlmostEqual(raw["Gold"]["2026-02"],4934.0445,places=5)
        self.assertAlmostEqual(cen["Gold"]["2026-02"],5008.677368421052,places=5)
        self.assertAlmostEqual(self.by["EXTERNAL_CLOSE_ONLY_SENSITIVITY"].monthly_metal["Gold"]["2026-02"],5019.3585,places=4)
    def test_prior_months_past_data_unchanged(self):
        for metal in m.METALS.values():
            for mm,price in self.by["RAW_UNTOUCHED"].monthly_metal[metal].items():
                if mm<"2026-02":
                    for sc in m.SCENARIOS[1:]:
                        self.assertEqual(price,self.by[sc].monthly_metal[metal][mm])
    def test_gpr_origin_vintage_correct(self):
        self.assertEqual({x:len(y) for x,y in self.vintages.items()},
               {"2026-01":492,"2026-02":493,"2026-03":494,"2026-04":495})
        self.assertTrue(all(max(history)<origin for origin,history in self.vintages.items()))
    def test_target_Y_masked_no_lookahead(self):
        for sc,bundle in self.by.items():
            for target in m.TEST_TARGETS:
                samples=m.make_samples(bundle,target)
                self.assertIsNone(samples[target][1])
                self.assertEqual(max(samples),target)
                self.assertEqual(max(k for k in samples if k<target),m.base.month_shift(target,-1))
                self.assertEqual(len(samples[target][0]),8)
    def test_feb_forecast_features_unaffected_but_march_changed(self):
        f={s:m.make_samples(b,"2026-02")["2026-02"][0]
           for s,b in self.by.items()}
        np.testing.assert_array_equal(f["RAW_UNTOUCHED"],f["CENSORED_ONE_DAY"])
        np.testing.assert_array_equal(f["RAW_UNTOUCHED"],f["EXTERNAL_CLOSE_ONLY_SENSITIVITY"])
        g={s:m.make_samples(b,"2026-03")["2026-03"][0]
           for s,b in self.by.items()}
        self.assertFalse(np.array_equal(g["RAW_UNTOUCHED"],g["CENSORED_ONE_DAY"]))
        self.assertFalse(np.array_equal(g["RAW_UNTOUCHED"],g["EXTERNAL_CLOSE_ONLY_SENSITIVITY"]))
    def test_censored_monthly_research_is_not_full_month_truth(self):
        q=pd.read_csv(O/"v26_censored_monthly_fourmetal_research_NOT_CERTIFIED.csv")
        self.assertEqual(len(q),804)
        x=q[q.month.eq("2026-02")]
        self.assertEqual(len(x),4)
        self.assertTrue((x.contaminated_days_removed==1).all())
        self.assertFalse(x.month_full_target_is_observed.any())
        self.assertFalse(q.firstprint_pit_certified.any())
    def test_curated_models_results_are_not_consistent_with_claimed_live_success(self):
        t=pd.read_csv(O/"v26_curated_mar2026_models_COMMITTED.csv")
        self.assertEqual(len(t),12)
        self.assertEqual(set(t.model),{"MPA_ANN_ORIGINAL","CHHHO_ANFIS_ORIGINAL",
                         "AOA_ELM_V2_BUGFIX","SMA_ELMFIS_V2_INNER_SAFE"})
        self.assertFalse(t.price_same_fixing_certified.any())
        p=t.pivot(index="model",columns="scenario",values="forecast_gold_usd_oz")
        self.assertGreater(float((p["CENSORED_ONE_DAY"]-p["RAW_UNTOUCHED"]).abs().min()),100)
        self.assertGreater(float((p["EXTERNAL_CLOSE_ONLY_SENSITIVITY"]-p["RAW_UNTOUCHED"]).abs().max()),900)
    def test_health_gate_still_rejects_promotion(self):
        s=v25()
        self.assertFalse(s["data_health_certified"])
        self.assertFalse(s["monthly_H1_train_replay_safe"])

if __name__=="__main__":
    unittest.main(verbosity=2)
