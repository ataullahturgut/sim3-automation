import unittest
import numpy as np
import pandas as pd
import risk_v28_gold_monthly_parameter_study as v28
import risk_v26_monthly_models_sensitivity as v26
import risk_v27_monthly_2026_full_replay as v27

class ParameterStudyV28Tests(unittest.TestCase):
    def test_exact_54_origin_GPR_releases(self):
        g=v28.histories()
        self.assertEqual(len(g),54)
        self.assertEqual(set(g),{v26.base.month_shift(t,-1) for t in v28.DEV+v28.VAL+v28.STRESS})
        for origin,h in g.items():
            self.assertEqual(min(h),"2010-01")
            self.assertEqual(max(h),v26.base.month_shift(origin,-1))
            self.assertGreaterEqual(min(h.values()),0)
            self.assertLessEqual(max(h.values()),1)
    def test_model_features_and_label_mask_on_DEV(self):
        b=v26.construct(v26.immutable_prices(),"CENSORED_ONE_DAY",{})
        s=v27.samples_at_origin(b,"2022-04",v28.histories())
        self.assertIsNone(s["2022-04"][1])
        self.assertEqual(s["2022-04"][0].shape,(8,))
        self.assertEqual(sorted(k for k in s if k<"2022-04")[-1],"2022-03")
    def test_log_return_cap_blocks_absurd_SMA_outlier(self):
        class R:
            origin=5000.
            log_predict=-1.0
        self.assertLessEqual(abs(v28.calibrated_forecast(R,1.,.075)-5000)/5000,.08)
        self.assertEqual(v28.calibrated_forecast(R,0,.15),5000.)
    def test_selected_hyperparameters_depend_on_DEV_only(self):
        months=v28.DEV
        data=[]
        for m in months:
            for model in list(v28.MODELS)+[f"RIDGE8_ALPHA_{x:g}" for x in v28.RIDGE_LAMBDA]:
                ix=int(m[-2:])
                data.append(dict(month=m,model=model,split="DEV",origin=2000.,
                    actual=2000.*np.exp(.01*(ix%5-2)),log_predict=.018*(ix%5-2),
                    forecast=2000.*np.exp(.018*(ix%5-2))))
        baseline=pd.DataFrame(data)
        chosen,_=v28.select_dev_params(baseline)
        junk=pd.DataFrame([dict(month="2026-04",model=v28.MODELS[0],
                split="2026_STRESS",origin=5000.,actual=10000.,
                log_predict=-.9,forecast=2500.)])
        other,_=v28.select_dev_params(pd.concat([baseline,junk],ignore_index=True))
        self.assertEqual(chosen[["model","gain","cap"]].to_json(orient="records"),
                         other[["model","gain","cap"]].to_json(orient="records"))
    def test_ridge_8feature_is_finite_target_Y_hidden(self):
        b=v26.construct(v26.immutable_prices(),"CENSORED_ONE_DAY",{})
        s=v27.samples_at_origin(b,"2025-12",v28.histories())
        self.assertIsNone(s["2025-12"][1])
        q,n=v28.ridge_log_predict(s,"2025-12",10.)
        self.assertGreaterEqual(n,150)
        self.assertTrue(np.isfinite(q))

if __name__=="__main__":
    unittest.main(verbosity=2)
