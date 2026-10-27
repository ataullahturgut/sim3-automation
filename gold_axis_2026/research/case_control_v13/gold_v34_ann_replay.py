#!/usr/bin/env python3
"""Gold V34 original weekly ANN + MPA monthly ANN replay, no new tuning.

2024/25 learns only META position policy, 2026 evaluated after policy frozen.
Weekly ANN: exact gold_weekly_h1_ann_4metal_v1.fit_predict, 16 features,
MLP8 tanh lbfgs alpha=1 seed=1701. Original fit function untouched.
Monthly ANN: original MPA_ANN_ORIGINAL 8 features including origin-vintage
GPR; original optimizer untouched, NO V28 gain/cap tuning.
Single four-metal StakTrakr reconstructed source, Feb27 alternative
reference, NOT same-seance/firstprint certified.
"""
from __future__ import annotations
import argparse,copy,json,sys
from collections import defaultdict
from datetime import date,timedelta
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
TOOLS=HERE.parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
import gold_weekly_h1_ann_4metal_v1 as weekly
import risk_v26_monthly_models_sensitivity as v26
import risk_v28_gold_monthly_parameter_study as v28

O=HERE/"outputs"
TARGET_START="2024-01-01"
TARGET_END="2026-10-19"
SCENARIO="EXTERNAL_CLOSE_ONLY_SENSITIVITY"
MODEL_MONTHLY="MPA_ANN_ORIGINAL"
MODEL_WEEKLY=weekly.MODEL

def guard(test,msg):
    if not bool(test): raise AssertionError("V34_ANN_INTEGRITY_"+msg)

def price_frame():
    d=v26.immutable_prices()
    # Keep raw source unchanged; EXTERNAL reference is a transparent,
    # uncertified scenario, and is used identically in monthly and weekly.
    for code,value in v26.REFERENCE_CLOSE.items():
        d.loc[d.date.eq("2026-02-27"),code]=value
    source=pd.concat([pd.read_csv(O/"v33_oct01_16_frozen_2026_four_metals_weekday_20261023_snapshot.csv"),
            pd.read_csv(O/"v33_staktrakr_4metals_2026_10_19_to_10_23_FIXED_COMMIT.csv")],ignore_index=True)
    guard(len(source)==68 and source.groupby("date").metal.nunique().eq(4).all(),"OCT_PRICE_COMPLETE")
    pivot=source.pivot(index="date",columns="metal",values="price_usd_oz")
    toadd=pivot.reset_index()[["date","AU","AG","PT","PD"]]
    d=pd.concat([d,toadd],ignore_index=True).sort_values("date")
    guard(d.date.is_unique and d.date.max()=="2026-10-23","SAME_SOURCE_PRICE_END")
    guard(len(d)==4234+17,"PRICE_LENGTH")
    guard(d.loc[d.date.eq("2026-02-27"),"AU"].iloc[0]==5222.3,"FEB_SCENARIO")
    return d

def weekly_snapshot():
    d=price_frame()
    grp=defaultdict(dict)
    for r in d.itertuples():
        dt=date.fromisoformat(r.date)
        mon=weekly.mon(dt)
        grp[mon][dt]=dict(AU=float(r.AU),AG=float(r.AG),PT=float(r.PT),PD=float(r.PD))
    end=date.fromisoformat(d.date.max())
    weeks=[]
    for monday,days in sorted(grp.items()):
        if (monday+timedelta(days=4)>end or
            monday+timedelta(days=6)>date(2026,10,27) or len(days)<3):continue
        ordered=sorted(days)
        x=np.array([[days[k][m] for m in weekly.M] for k in ordered],float)
        guard(np.isfinite(x).all() and x.min()>0,"WEEKLY_NONFINITE_SOURCE")
        weeks.append(dict(week_monday=monday.isoformat(),
            first_observation=ordered[0].isoformat(),
            last_observation=ordered[-1].isoformat(),
            shared_trading_days=len(days),
            means=x.mean(0).tolist(),
            opens=x[0].tolist(),
            closes=x[-1].tolist(),
            highs=x.max(0).tolist(),
            lows=x.min(0).tolist(),
            daily_realized_vol=np.sqrt(np.sum(np.diff(np.log(x),axis=0)**2,axis=0)).tolist()))
    targets=[w["week_monday"] for w in weeks if TARGET_START<=w["week_monday"]<=TARGET_END]
    guard(len(weeks)>800 and len(targets)>=140 and targets[-1]=="2026-10-19","WEEKLY_TARGET_SCOPE")
    return dict(week_summaries=weeks,targets=targets,
        firstprint_PIT_proven=False,
        weekly_original_hyperparameters_unchanged=True,
        external_2026_02_27_same_benchmark_certified=False,
        source="STAKTRAKR_ORIGINAL_2010_SEP_2026_OCT_UPDATED_FIXED_2026_OCT23")

def replay_weekly(snapshot,shard,shards):
    out=[]
    for i,t in enumerate(snapshot["targets"]):
        if i%shards!=shard:continue
        z=weekly.fit_predict(snapshot,t)
        guard(z["training_last_week"]<z["target_week"],"WEEKLY_TRAINING_LEAK")
        guard(z["origin_week"]<z["target_week"],"WEEKLY_ORIGIN_FUTURE")
        z["research_price_scenario"]=SCENARIO
        z["firstprint_PIT_proven"]=False
        z["old_model_parameters_unchanged"]=True
        z["forecast_exists_before_target_week"]=True
        z["training_uses_2026_target_labels"]=False
        out.append(z)
        print("V34_WEEKLY_ORIGINAL_ANN",t,"fc_mean",round(z["forecast_mean_xau"],4),
              "actual_mean",round(z["actual_mean_xau"],4),
              "fc_close",round(z["forecast_close_xau"],4),flush=True)
    guard(len(out)>28,"INSUFFICIENT_WEEKLY_SHARD")
    return out

def replay_monthly():
    # monthly source has exact 2010-Sep2026 normal frozen horizon, no Oct target
    data=v26.construct(v26.immutable_prices(),SCENARIO,{})
    vintages=v28.histories()
    months=list(v26.base.month_range("2024-01","2026-09"))
    rows=v28.predict_months(data,vintages,months,
                             original_models=(MODEL_MONTHLY,),include_ridge=False)
    guard(len(rows)==33 and rows.model.eq(MODEL_MONTHLY).all(),"33_MONTHLY_ORIGINAL_ANN")
    guard(rows.month.tolist()==months,"MONTHLY_ORIGINAL_TARGETS")
    guard(rows[rows.split.eq("2026_STRESS")].shape[0]==9,"2026_NINE_MONTHS")
    rows["target_month"]=rows.month
    rows["forecast_pre_target_month"]=True
    rows["feb_2026_full_target_verified"]=rows.month.ne("2026-02")
    rows["original_params_unchanged"]=True
    rows["V28_gain_cap_inference_used"]=False
    rows["same_fixing_price_firstprint_PIT_certified"]=False
    rows["research_price_scenario"]=SCENARIO
    rows.to_csv(O/"v34_monthly_MPA_ANN_ORIGINAL_2024_2026_33_month_predictions.csv",index=False)
    m=rows.groupby(rows.month.str[:4]).agg(n=("month","count"),
         MAE=("forecast",lambda f: float(np.nan)),).reset_index()
    print("V34_MONTHLY_ANN_ORIGINAL_33_COMPLETE",len(rows),flush=True)
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("source","weekly","monthly"),required=True)
    p.add_argument("--shard",type=int,default=0)
    p.add_argument("--shards",type=int,default=4)
    a=p.parse_args()
    if a.mode=="source":
        payload=weekly_snapshot()
        (O/"v34_weekly_ann_input_2010_2026_reconstructed_sensitivity.json").write_text(
            json.dumps(payload,allow_nan=False,separators=(",",":"))+"\n")
        print("V34_PRICE_SOURCE",len(payload["week_summaries"]),
              len(payload["targets"]),payload["targets"][-1],flush=True)
    elif a.mode=="monthly":
        replay_monthly()
    else:
        s=json.loads((O/"v34_weekly_ann_input_2010_2026_reconstructed_sensitivity.json").read_text())
        z=replay_weekly(s,a.shard,a.shards)
        p=O/f"v34_weekly_ANN_ORIGINAL_shard{a.shard}.csv"
        pd.DataFrame(z).to_csv(p,index=False)
        print("V34_WEEKLY_ANN_SHARD_COMPLETE",a.shard,len(z),flush=True)
if __name__=="__main__":main()
