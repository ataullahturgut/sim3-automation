#!/usr/bin/env python3
"""Targeted stress: actual research-selected MPA ANN, CHHHO ANFIS, fixed AOA ELM, SMA ELMFIS.

Scientific optimizer versions frozen; 2026 hindsight observation, NOT fit/selection.
The known legacy AOA ELM is structurally defective; use separate repaired V2
for the candidate and label that distinct algorithm explicitly.
"""
from __future__ import annotations
import argparse,json,math,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import risk_v26_monthly_models_sensitivity as source

ROOT=Path(__file__).resolve().parent
OUT=ROOT/"outputs"
TARGET="2026-03"
SELECTED=("MPA_ANN_ORIGINAL","CHHHO_ANFIS_ORIGINAL",
          "AOA_ELM_V2_BUGFIX","SMA_ELMFIS_V2_INNER_SAFE")

def predictor(samples,target,alg):
    if alg=="MPA_ANN_ORIGINAL":
        import gold_monthly_2026_aug_sep_topmodels_v1 as ann
        p,info=ann.pred_component(samples,target,"MPA")
        n=int(info["train_rows"])
    elif alg=="CHHHO_ANFIS_ORIGINAL":
        import vw_midas_anfis_stage3c_literature_v1 as ch
        p,n,info=ch.select(samples,target,"CHHHO")
    elif alg=="AOA_ELM_V2_BUGFIX":
        import gold_monthly_h1_aoa_elm_bugfix_replay_v2 as elm
        p,n,info=elm.corrected_predict(samples,target)
    elif alg=="SMA_ELMFIS_V2_INNER_SAFE":
        import gold_monthly_h1_sma_elmfis_chrono_replay_v2 as e
        p,info=e.corrected(samples,target)
        n=int(info["training_rows"])
    else: raise ValueError(alg)
    p=np.asarray(p,float)
    if p.shape!=(4,) or not np.isfinite(p).all():raise RuntimeError("V26_CURATED_INVALID_OUTPUT_"+alg)
    return float(p[0]),n,info

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--models",default=",".join(SELECTED))
    args=a.parse_args()
    models=args.models.split(",")
    assert models and all(m in SELECTED for m in models)
    d=source.immutable_prices();hist=source.origin_histories()
    rows=[]
    for sc in source.SCENARIOS:
        b=source.construct(d,sc,hist)
        sample=source.make_samples(b,TARGET)
        for model in models:
            p,n,info=predictor(sample,TARGET,model)
            forecast=float(b.core_gold["2026-02"]*math.exp(p))
            actual=float(b.core_gold[TARGET])
            row=dict(target_month=TARGET,model=model,scenario=sc,
                     training_rows=n,forecast_gold_usd_oz=forecast,
                     actual_research_gold_usd_oz=actual,
                     absolute_error_vs_unmodified_March_actual=abs(forecast-actual),
                     input_origin_Feb_mean=b.core_gold["2026-02"],
                     price_firstprint_certified=False,
                     external_close_same_LBMA_fixing_certified=False,
                     target_label_seen=False,
                     original_input_GPR_vintage="2026-02",
                     optimizer_version_from_existing_repository=True)
            rows.append(row)
            print("V26_CURATED_RESULT",model,sc,"forecast",round(forecast,5),
                  "actual",round(actual,5),"train",n,flush=True)
    allrows=pd.DataFrame(rows)
    allrows.to_csv(OUT/"v26_curated_mar2026_models_sensitivity.csv",index=False)
    meta={"target":"2026-03","actual_reference_unchanged":True,
          "frozen_optimizer_code_unmodified":True,
          "legacy_AOA_ELM_zero_factor_bug_avoided_by_distinct_v2":True,
          "SMA_ELMFIS_inner_scaler_leak_avoided_by_distinct_v2":True,
          "not_fully_blind":True,
          "GPR_frozen_origin_vintage":True,
          "target_Y_masked_before_model":True,
          "external_feb27_price_not_certified_identical_definition":True,
          "neon_mutation":False,"models":models}
    (OUT/"v26_curated_mar2026_models_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    pivot=allrows.pivot_table(index="model",columns="scenario",values="forecast_gold_usd_oz")
    if set(source.SCENARIOS)==set(allrows.scenario):
        pivot["EXTERNAL_MINUS_RAW_USD"]=pivot["EXTERNAL_CLOSE_ONLY_SENSITIVITY"]-pivot["RAW_UNTOUCHED"]
        pivot["CENSORED_MINUS_RAW_USD"]=pivot["CENSORED_ONE_DAY"]-pivot["RAW_UNTOUCHED"]
    print("V26_CURATED_STRESS_SUMMARY")
    print(pivot.to_string())

if __name__=="__main__":
    main()
