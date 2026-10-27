#!/usr/bin/env python3
"""V28 gold monthly: chronological parameter improvement, no 2026 tuning.

* DEV authority = 2022-04..2024-12 (33), 2025 = locked validation (12).
* 2026 Jan..Sep evaluated once after configs frozen on DEV.
* Reuses EXACT four original V27 optimizers, not substitute algorithms.
* Tunes 2 inference hyperparameters (forecast log-return scale/cap) for
  each frozen base algorithm against only original DEV monthly targets.
* Separately tunes an 8-feature multioutput ridge benchmark using DEV.
* All models use original origin-specific GPR historical release vintages.
* No model choices, thresholds, feature choices can see 2025/2026 labels.
* Data source: same quarantined 2010-2026 StakTrakr research read-only CSV.
* Scientific caution: 2026 observations already informed earlier development;
  this is retrospective and cannot establish truly independent 2026 testing.
"""
from __future__ import annotations
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import pandas as pd
import risk_v27_monthly_2026_full_replay as v27
import risk_v26_monthly_models_sensitivity as v26
from risk_v26_curated_models_stress import predictor,SELECTED

OUT=Path(__file__).parent/"outputs"
DEV=list(v26.base.month_range("2022-04","2024-12"))
VAL=list(v26.base.month_range("2025-01","2025-12"))
STRESS=list(v26.base.month_range("2026-01","2026-09"))
MODELS=tuple(SELECTED)
GAMMA=(0.,.25,.4,.55,.7,.85,1.,1.15)
CAP=(.03,.05,.075,.10,.15,.25,math.inf)
RIDGE_LAMBDA=(.01,.1,1.,10.,100.)
PRICE_SCENARIO="CENSORED_ONE_DAY"
EPS=1e-9

def ck(ok,msg):
    if not bool(ok):raise RuntimeError("V28_PARAMETER_GATE_"+msg)

def histories():
    """2022-03..2025-11 GPR vintages plus 2025-12..2026-08 V27."""
    z=[]
    for i in range(1,10):
        p=OUT/f"v28_DEV_2022_2025_official_gpr_origin_group_{i}.csv"
        q=pd.read_csv(p)
        ck(len(q)>=700 and q.source_commit.str.len().eq(40).all(),
           "MISSING_HISTORICAL_GPR_GROUP_"+str(i))
        for origin,g in q.groupby("origin"):
            cutoff=(pd.Period(origin,freq="M")+1).start_time.tz_localize("UTC")
            ck(pd.to_datetime(g.released,utc=True).max()<cutoff,
               "GPR_PREVIEW_FUTURE_REVISION_"+origin)
            ck(g.source_commit.nunique()==1,"GPR_ORIGIN_SOURCE_CONFLICT_"+origin)
        z.append(q[["origin","month","gpr_origin_normalized_z"]])
    old=pd.concat(z,ignore_index=True)
    newest=v27.official_vintage_normalized()
    dev_origins={v26.base.month_shift(m,-1) for m in DEV+VAL}
    ck(set(old.origin)==dev_origins,"MISSING_DEV_OR_VALIDATION_ORIGIN")
    out={}
    for origin,g in old.groupby("origin"):
        expected=list(v26.base.month_range("2010-01",v26.base.month_shift(origin,-1)))
        ck(g.month.tolist()==expected,"CHRONO_OR_GPR_MONTH_GAP_"+origin)
        ck((g.gpr_origin_normalized_z.between(0,1)).all(),"GPR_Z_OUT_OF_RANGE_"+origin)
        out[origin]=dict(zip(g.month,g.gpr_origin_normalized_z.astype(float)))
    ck(not (set(out)&set(newest)),"OVERLAPPING_GPR_FILES")
    out.update(newest)
    all_origins={v26.base.month_shift(m,-1) for m in DEV+VAL+STRESS}
    ck(set(out)==all_origins,"MISSING_SOME_OF_54_GPR_ORIGINS")
    return out

def ridge_log_predict(samples,target,alpha):
    keys=sorted(k for k in samples if k<target)
    ck(len(keys)>=120 and all(k<target for k in keys),"RIDGE_CAUSAL_HISTORY")
    X=np.vstack([samples[k][0] for k in keys]);Y=np.vstack([samples[k][1] for k in keys])
    tx=samples[target][0].reshape(1,-1)
    ck(samples[target][1] is None,"RIDGE_TARGET_Y_LEAK")
    mean=X.mean(0);sd=np.maximum(X.std(0),1e-9)
    ym=Y.mean(0);ys=np.maximum(Y.std(0),1e-9)
    A=(X-mean)/sd;B=(Y-ym)/ys
    Xt=(tx-mean)/sd
    # Center and scale using prior origin training months exclusively;
    # exact multioutput ridge solution; unpenalized intercept via centered A/B.
    beta=np.linalg.solve(A.T@A+alpha*np.eye(A.shape[1]),A.T@B)
    p=(Xt@beta)[0]*ys+ym
    ck(np.isfinite(p).all(),"RIDGE_NONFINITE")
    return float(p[0]),len(keys)

def predict_months(bundle,vintages,months,original_models=MODELS,include_ridge=True):
    rows=[]
    for target in months:
        origin=v26.base.month_shift(target,-1)
        samples=v27.samples_at_origin(bundle,target,vintages)
        ck(samples[target][1] is None,"MODEL_TARGET_Y_LEAK_"+target)
        p=float(bundle.core_gold[origin]);a=float(bundle.core_gold[target])
        ck(p>0 and a>0,"NONPOSITIVE_GOLD_"+target)
        for model in original_models:
            q,n,info=predictor(samples,target,model)
            rows.append(dict(month=target,model=model,origin=p,actual=a,log_predict=q,
                             forecast=p*math.exp(q),train_rows=n,split=
                             "DEV" if target in DEV else "VALIDATION" if target in VAL else "2026_STRESS"))
            print("V28_BASE_MODEL",target,model,"pred",round(rows[-1]["forecast"],4),
                  "actual",round(a,4),flush=True)
        if include_ridge:
            for alpha in RIDGE_LAMBDA:
                q,n=ridge_log_predict(samples,target,alpha)
                model=f"RIDGE8_ALPHA_{alpha:g}"
                rows.append(dict(month=target,model=model,origin=p,actual=a,log_predict=q,
                                 forecast=p*math.exp(q),train_rows=n,split=
                                 "DEV" if target in DEV else "VALIDATION" if target in VAL else "2026_STRESS"))
    return pd.DataFrame(rows)

def calibrated_forecast(row,k,cap):
    val=float(row.log_predict)*float(k)
    if math.isfinite(cap):val=float(np.clip(val,-cap,cap))
    return float(row.origin*math.exp(val))

def metrics(rows,forecast_col="forecast"):
    r=rows
    err=np.abs(r[forecast_col].to_numpy()-r.actual.to_numpy())
    rw=np.abs(r.origin.to_numpy()-r.actual.to_numpy())
    act=r.actual.to_numpy()
    dirs=((r[forecast_col].to_numpy()>r.origin.to_numpy())==(r.actual.to_numpy()>r.origin.to_numpy()))
    return dict(n=int(len(r)),sumAE=float(err.sum()),MAE=float(err.mean()),
        MAPE_pct=float(np.mean(err/act)*100),
        direction_correct=int(dirs.sum()),direction_pct=float(dirs.mean()*100),
        randomwalk_MAE=float(rw.mean()),
        improvement_vs_raw_pct=0.0)

def select_dev_params(original):
    chosen=[];leader=[]
    for model in list(MODELS)+[f"RIDGE8_ALPHA_{x:g}" for x in RIDGE_LAMBDA]:
        d=original[(original.model==model)&original.split.eq("DEV")].copy()
        ck(len(d)==33,"INVALID_DEV_COUNT_"+model)
        for gain in GAMMA:
            for cap in CAP:
                d["calibrated"]= [calibrated_forecast(r,gain,cap) for r in d.itertuples()]
                m=metrics(d,"calibrated")
                leader.append(dict(model=model,gain=gain,cap=cap,**m))
    grid=pd.DataFrame(leader)
    # Inner selection solely 2022-2024, tie-break deterministic and simpler:
    # 1 total absolute errors (primary), 2 more directions, 3 less
    # aggressive gain, 4 smaller cap, 5 chosen candidate name.
    grid=grid.sort_values(["model","sumAE","direction_correct","gain","cap"],
                          ascending=[True,True,False,True,True])
    for model,g in grid.groupby("model",sort=False):
        chosen.append(g.iloc[0].to_dict())
    return pd.DataFrame(chosen),grid

def calibrate_all(original,selected,models):
    out=[]
    for model in models:
        c=selected[selected.model.eq(model)].iloc[0]
        v=original[original.model.eq(model)].copy()
        ck(len(v)==54,"MODEL_54_ROWS_MISSING_"+model)
        v["chosen_dev_gain"]=float(c.gain)
        v["chosen_dev_cap"]=float(c.cap)
        v["tuned_forecast"]=[calibrated_forecast(r,c.gain,c.cap) for r in v.itertuples()]
        v["raw_abs_error"]=np.abs(v.forecast-v.actual)
        v["tuned_abs_error"]=np.abs(v.tuned_forecast-v.actual)
        v["tuning_scope"]="DEV_2022_04_THROUGH_2024_12_ONLY"
        out.append(v)
    return pd.concat(out,ignore_index=True)

def score_by_split(df,models):
    out=[]
    for model in models:
        for role,months in (("DEV",DEV),("VALIDATION",VAL),("2026_STRESS",STRESS),
                            ("2026_STRESS_EXCLUDE_FEB",[x for x in STRESS if x!="2026-02"])):
            k=df[(df.model==model)&df.month.isin(months)].copy()
            ck(len(k)==len(months),"MISSING_EVAL_ROWS_"+role+"_"+model)
            old=metrics(k)
            new=metrics(k,"tuned_forecast")
            out.append(dict(model=model,role=role,months=len(k),
                original_MAE=old["MAE"],tuned_MAE=new["MAE"],
                delta_MAE=new["MAE"]-old["MAE"],original_MAPE=old["MAPE_pct"],
                tuned_MAPE=new["MAPE_pct"],original_direction=old["direction_correct"],
                tuned_direction=new["direction_correct"],
                rw_MAE=old["randomwalk_MAE"],
                VALIDATION_GATE_PASS=bool(new["MAE"]<old["MAE"]-1e-9
                   and new["MAE"]<old["randomwalk_MAE"]-1e-9) if role=="VALIDATION"
                   else None,
                no_2025_2026_tuning=True,source_PIT_fully_certified=False))
    return pd.DataFrame(out)

def check_v27_parity(test_original):
    v=pd.read_csv(OUT/"v27_all_2026_monthly_results_COMMITTED.csv")
    v=v[v.scenario.eq("CENSORED_ONE_DAY")]
    for m in MODELS:
        for t in STRESS:
            z=test_original[(test_original.month==t)&test_original.model.eq(m)]
            a=v[(v.target_month==t)&v.model.eq(m)]
            ck(len(z)==1 and len(a)==1,"V27_ROW_MISSING_"+t+"_"+m)
            ck(abs(float(z.forecast.iloc[0])-float(a.forecast_usd_oz.iloc[0]))<.001,
               "V27_FROZEN_MODEL_PARITY_"+t+"_"+m)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--phase",choices=["tune","final"],default="tune")
    args=a.parse_args()
    d=v26.immutable_prices()
    vint=histories()
    price=v26.construct(d,PRICE_SCENARIO,{})
    if args.phase=="tune":
        allrows=predict_months(price,vint,DEV+VAL,include_ridge=True)
        ck(len(allrows)==45*(len(MODELS)+len(RIDGE_LAMBDA)),"REPLAY_NINE_MODELS_45_TARGETS")
        allrows.to_csv(OUT/"v28_2022_2025_DEV_VALIDATION_original_models.csv",index=False)
        chosen,grid=select_dev_params(allrows)
        chosen.to_csv(OUT/"v28_dev_selected_parameters_all_model_families.csv",index=False)
        grid.to_csv(OUT/"v28_dev_all_parameter_candidates.csv",index=False)
        print("V28_DEV_SELECTED_PARAMETERS\n"+chosen.to_string(index=False),flush=True)
        # The canonical variant in each model type is selected by
        # original fixed model ID; Ridge alpha candidates cannot be chosen
        # based on 2025 (rank on 2022-2024 DEV only).
        rid=chosen[chosen.model.str.startswith("RIDGE8_ALPHA_")].sort_values(
              ["sumAE","direction_correct","model"],ascending=[True,False,True]).iloc[0]
        plan=dict(original_models=list(MODELS), ridge_model=str(rid.model),
                  model_params={k:{"gain":float(v.gain),"cap":float(v.cap)}
                  for k,v in chosen.set_index("model").iterrows()},
                  selected_by="DEV_2022_04..2024_12_ONLY",
                  model_release="V28_RESEARCH_NOT_LIVE",
                  no_2025_2026_in_selection=True,
                  original_GPR_origin_vintage_count=len(vint),
                  external_price_firstprint_certified=False)
        (OUT/"v28_FROZEN_tuning_plan_after_DEV.json").write_text(json.dumps(plan,indent=2)+"\n")
        # Holdout 2025 gate: objectively report; no fallback or re-selection.
        models=list(MODELS)+[str(rid.model)]
        done=calibrate_all(allrows,chosen,list(MODELS)+[f"RIDGE8_ALPHA_{v:g}" for v in RIDGE_LAMBDA])
        results=score_by_split(done,models)
        results[results.role.eq("VALIDATION")].to_csv(
            OUT/"v28_validation_2025_NO_RETUNE.csv",index=False)
        print("V28_2025_LOCKED_HOLDOUT_RESULTS\n"+results[results.role.eq("VALIDATION")].to_string(index=False),flush=True)
        print("V28_TUNE_PHASE_COMPLETED",len(allrows),flush=True)
    else:
        plan=json.loads((OUT/"v28_FROZEN_tuning_plan_after_DEV.json").read_text())
        old=pd.read_csv(OUT/"v28_2022_2025_DEV_VALIDATION_original_models.csv")
        picked=pd.read_csv(OUT/"v28_dev_selected_parameters_all_model_families.csv")
        ck(plan["no_2025_2026_in_selection"],"PLAN_NOT_FROZEN")
        new=predict_months(price,vint,STRESS,include_ridge=True)
        check_v27_parity(new)
        full=pd.concat([old,new],ignore_index=True)
        all_selected=list(MODELS)+[plan["ridge_model"]]
        tuned=calibrate_all(full,picked,all_selected)
        result=score_by_split(tuned,all_selected)
        evalrows=tuned[tuned.split.eq("2026_STRESS")].copy()
        evalrows["month_full_target_verified"]=evalrows.month.ne("2026-02")
        evalrows["2026_score_out_of_sample_blind"]=False
        evalrows.to_csv(OUT/"v28_2026_orig_and_locked_param_tuned_MONTHLY.csv",index=False)
        result.to_csv(OUT/"v28_DEV_2025_VALIDATION_2026_results.csv",index=False)
        result.to_csv(OUT/"v28_MODEL_SELECTION_NO_2026_PEEK.csv",index=False)
        # Explicitly compare tuned 2026 to V27 and random walk; 2026 does
        # not decide whether a tuned option is eligible for production.
        outcome={"status":"HISTORICAL_RESEARCH_ONLY",
            "all_months":STRESS,"frozen_model_params":plan["model_params"],
            "data_mutation":False,"active_forecast_writes":False,
            "2025_holdout_used_to_choose_parameters":False,
            "2026_stress_used_to_choose_parameters":False,
            "price_firstprints_PIT_certified":False,
            "Feb_2026_verified_full_month":False,
            "year2026_forecasts_considered_truly_blind":False,
            "2025_gate_policy":"PASS only when BOTH 2025 tune MAE < 2025 original MAE AND < 2025 RW MAE. No auto promotion.",
            "model_selection_scope":"2022-04..2024-12",
            "2026_role":"EX_POST_STRESS",
            "model_variants_mechanism":"original full algorithm unchanged, only log-return inference scale and cap; ridge8 separate benchmark"}
        (OUT/"v28_parameter_tuning_integrity_manifest.json").write_text(json.dumps(outcome,indent=2)+"\n")
        print("V28_COMPARISON_SUMMARY\n"+result.to_string(index=False),flush=True)
        p=evalrows[evalrows.model.isin(all_selected)].pivot_table(
            index="month",columns="model",values="tuned_forecast",aggfunc="first")
        p.insert(0,"research_actual",evalrows.groupby("month").actual.first())
        print("V28_2026_MONTHLY_TUNED_FORECASTS\n"+p.to_string(),flush=True)
        print("V28_FINAL_RESULTS_COUNT",len(evalrows),flush=True)
if __name__=="__main__":
    main()
