#!/usr/bin/env python3
"""V26 controlled real ANN/ANFIS/ELM source-sensitivity replays.

NEVER call these sensitivity price scenarios "verified correct historical
benchmark". The alternative closes are not a licensed identical fixing.
Uses original frozen feature equations & original model functions. Does not
alter model code, Neon, model registry, or existing forecasts.
GPR historical monthly origin vintage is frozen and source pinned.
Target Y is withheld from estimator by replacing it with None.
"""
from __future__ import annotations
import argparse,hashlib,json,math,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_vanilla_v3_checked as anfis
import vw_midas_elm_baseline_v1 as elm
import gold_monthly_2026_aug_sep_topmodels_v1 as ann

OUT=HERE/"outputs"
METALS={"AU":"Gold","AG":"Silver","PT":"Platinum","PD":"Palladium"}
TEST_TARGETS=("2026-02","2026-03","2026-04")
REFERENCE_CLOSE={"AU":5222.30,"AG":89.975,"PT":2366.00,"PD":1793.00}
SCENARIOS=("RAW_UNTOUCHED","CENSORED_ONE_DAY","EXTERNAL_CLOSE_ONLY_SENSITIVITY")

def need(x,s):
    if not bool(x):raise RuntimeError("V26_MONTHLY_REPLAY_"+s)

def immutable_prices():
    d=pd.concat([pd.read_csv(OUT/f"v26_internal_fourmetal_{a}_{b}_NOT_PIT.csv")
       for a,b in ((2010,2018),(2019,2026))],ignore_index=True)
    need(len(d)==4234 and d.date.is_unique and d.date.is_monotonic_increasing,
         "IMMUTABLE_PRICE_ROW_CONTRACT")
    need(d.date.min()=="2010-01-04" and d.date.max()=="2026-09-30","SOURCE_DATE_RANGE")
    f=d.set_index("date").loc["2026-02-27"]
    for m,v in {"AU":3516.02,"AG":62.15,"PT":1585.39,"PD":1201.26}.items():
        need(abs(float(f[m])-v)<1e-7,"FOUR_METAL_FALSE_DAY_"+m)
    return d

def origin_histories():
    g=pd.read_csv(OUT/"v26_gpr_official_origin_vintages_Jan_Apr_2026_RESEARCH.csv")
    expected={"2026-01":492,"2026-02":493,"2026-03":494,"2026-04":495}
    need(g.groupby("origin").size().to_dict()==expected,"GPR_VINTAGE_COVERAGE")
    history={}
    for origin,z in g.groupby("origin"):
        need(z.observation_month.is_unique,"GPR_MONTH_DUPLICATION_"+origin)
        need(z.source_commit.nunique()==1 and len(z.source_commit.iloc[0])==40,
             "GPR_SOURCE_COMMIT_"+origin)
        need(pd.to_datetime(z.released,utc=True).max()<pd.Timestamp(
             origin+"-01",tz="UTC")+pd.offsets.MonthEnd(1)+pd.Timedelta(days=1),
             "GPR_AVAILABLE_AFTER_FORECAST_CUTOFF_"+origin)
        need(z.observation_month.max() < origin,"GPR_FUTURE_VALUE_"+origin)
        history[origin]=dict(zip(z.observation_month,z.gpr_value.astype(float)))
    return history

def construct(d,sc,history):
    x=d.copy(deep=True)
    if sc=="CENSORED_ONE_DAY":
        x=x.loc[x.date.ne("2026-02-27")].copy()
    elif sc=="EXTERNAL_CLOSE_ONLY_SENSITIVITY":
        for m,v in REFERENCE_CLOSE.items():
            x.loc[x.date.eq("2026-02-27"),m]=v
    elif sc!="RAW_UNTOUCHED":
        raise ValueError(sc)
    daily={}
    monthly={}
    for code,metal in METALS.items():
        dates=defaultdict(list)
        for date,v in zip(x.date,x[code]):
            dates[str(date)[:7]].append(float(v))
        daily[metal]={k:np.asarray(v,float) for k,v in dates.items()}
        monthly[metal]={k:float(np.mean(v)) for k,v in dates.items()}
    need(len(monthly["Gold"])==201,"MONTHLY_GOLD_LENGTH")
    need(all(m in monthly["Gold"] for m in ("2026-01","2026-02","2026-03","2026-04")),
         "TARGET_COVERAGE")
    need(all(len(daily[m]["2026-02"])== (19 if sc=="CENSORED_ONE_DAY" else 20)
             for m in METALS.values()),"FEB_MONTH_DAYS")
    return base.DataBundle(core_gold=dict(monthly["Gold"]),core_gpr={},
        daily_month_values=daily,monthly_metal=monthly,gpr_vintages=history,
        source_checks={"clean_certified":False,"research_only":True,
            "price_first_print_PIT_proven":False,"scenario":sc},
        invariants_before={})

def make_samples(bundle,t):
    s=base.all_samples_at_origin(bundle,t,governed=True)
    # Absolutely no target Y passed to the estimator.
    s[t]=(s[t][0].copy(),None)
    keys=sorted(q for q in s if q<t)
    need(len(keys)>=185 and keys[-1]==base.month_shift(t,-1),"TRAINING_CHRONOLOGY")
    need(s[t][1] is None,"TARGET_LABEL_LEAK")
    need(all(s[q][1] is not None for q in keys),"MISSING_TRAINING_TARGET")
    return s

def fitted_predict(s,target,model):
    if model=="ANN_FROZEN_VANILLA":
        p,diag=ann.pred_component(s,target,"VANILLA")
        n=int(diag["train_rows"])
    elif model=="ANFIS_V3_ORIGINAL":
        p,n,counts,diag=anfis.predict(s,target)
        diag={"rule_counts":counts,**diag}
    elif model=="ELM_FROZEN_BASELINE":
        p,n=elm.predict(s,target,(16,"tanh",.001))
        diag={"hidden":16,"act":"tanh","alpha":.001}
    else:raise ValueError(model)
    p=np.asarray(p,float)
    need(p.shape==(4,) and np.isfinite(p).all(),"MODEL_PREDICTION_"+model)
    return float(p[0]),n,diag

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--models",default="ANN_FROZEN_VANILLA,ANFIS_V3_ORIGINAL,ELM_FROZEN_BASELINE")
    ap.add_argument("--targets",default="2026-02,2026-03,2026-04")
    ap.add_argument("--scenarios",default=",".join(SCENARIOS))
    args=ap.parse_args()
    models=args.models.split(",")
    targets=args.targets.split(",")
    scenarios=args.scenarios.split(",")
    need(all(t in TEST_TARGETS for t in targets),"UNAPPROVED_TARGET")
    need(all(z in SCENARIOS for z in scenarios),"UNAPPROVED_SCENARIO")
    d=immutable_prices();hist=origin_histories()
    rows=[];inputs=[]
    for sc in scenarios:
        b=construct(d,sc,hist)
        for t in targets:
            s=make_samples(b,t);origin=base.month_shift(t,-1)
            v=s[t][0]
            inp={"target":t,"origin":origin,"scenario":sc,
              "gold_origin_month_avg":b.core_gold[origin],
              "gold_target_month_avg_EXPOST_ONLY":b.core_gold[t],
              "origin8":list(map(float,v)),"train_rows":len(s)-1,
              "source_gpr_vintage_origin":origin,"source_readonly":True,
              "target_label_visible_to_estimator":False}
            inp["origin8_sha256"]=hashlib.sha256(json.dumps(inp["origin8"],
                separators=(",",":"),allow_nan=False).encode()).hexdigest()
            inputs.append(inp)
            for model in models:
                pred,n,meta=fitted_predict(s,t,model)
                forecast=float(b.core_gold[origin]*math.exp(pred))
                actual=float(b.core_gold[t])
                z={"target":t,"origin":origin,"scenario":sc,"model":model,
                  "train_rows":n,"forecast_gold_usd_oz":forecast,
                  "actual_research_gold_usd_oz":actual,
                  "origin_gold_usd_oz":b.core_gold[origin],
                  "abs_error_against_SAME_SCENARIO_REFERENCE":abs(forecast-actual),
                  "ape_against_SAME_SCENARIO_REFERENCE_pct":100*abs(forecast-actual)/actual,
                  "log_prediction":pred,"origin8_sha256":inp["origin8_sha256"],
                  "model_original_implementation_unchanged":True,
                  "target_label_seen":False,"same_benchmark_price_definition_verified":False,
                  "forecast_certified_for_live":False,
                  "diag":meta}
                rows.append(z)
                print("V26_FAMILY_REPLAY",t,sc,model,
                      "forecast",format(forecast,".5f"),
                      "actual",format(actual,".5f"),
                      "origin",format(b.core_gold[origin],".5f"),
                      flush=True)
    result=pd.DataFrame(rows)
    inp=pd.DataFrame(inputs)
    # Keep model-specific source hashes and 8 inputs in JSON, not as
    # production dataset. Scenario results intentionally not compared
    # against one another as if their target definitions were identical.
    result.drop(columns=["diag"]).to_csv(OUT/"v26_monthly_models_scenario_comparison.csv",index=False)
    (OUT/"v26_monthly_models_full_diagnostics.json").write_text(
        json.dumps(rows,indent=2,allow_nan=False)+"\n")
    (OUT/"v26_monthly_origin_feature_sensitivity.json").write_text(
        json.dumps(inputs,indent=2,allow_nan=False)+"\n")
    pivot=result.pivot_table(index=["target","model"],columns="scenario",
                             values="forecast_gold_usd_oz",aggfunc="first")
    if set(scenarios)==set(SCENARIOS):
        pivot["EXTERNAL_MINUS_RAW_USD"]=(
             pivot["EXTERNAL_CLOSE_ONLY_SENSITIVITY"]-pivot["RAW_UNTOUCHED"])
        pivot["CENSORED_MINUS_RAW_USD"]=(
             pivot["CENSORED_ONE_DAY"]-pivot["RAW_UNTOUCHED"])
    pivot.to_csv(OUT/"v26_monthly_model_forecast_shifts.csv")
    manifest={"models":models,"targets":targets,"scenarios":scenarios,
      "prices_days_original":len(d),"gpr_origin_vintages":sorted(hist),
      "original_training_code_modified":False,
      "GPR_retro_git_origin_vintages_used":True,
      "target_label_visible_to_estimators":False,
      "no_Neon_reads_in_this_replay":True,"no_Neon_writes":True,
      "all_price_sources_historical_first_print_PIT_verified":False,
      "censored_Feb_is_not_true_full_month_actual":True,
      "external_PM_close_is_not_certified_same_price_definition":True,
      "2026_result_is_not_blind":True,
      "can_promote_clean_model_to_live":False}
    (OUT/"v26_monthly_model_sensitivity_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("V26_MODEL_SENSITIVITY_TABLE")
    print(pivot.to_string())
    print("V26_MODEL_SENSITIVITY_MANIFEST",json.dumps(manifest))

if __name__=="__main__":
    main()
