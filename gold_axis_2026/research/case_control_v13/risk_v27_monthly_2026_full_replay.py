#!/usr/bin/env python3
"""V27 research-only full-year-to-date 2026 monthly next-month gold forecasts.

Strict target-month Y blackout, as-of-origin official GPR archive vintage, true
historical StakTrakr reconstructed daily prices, no DB writes, no new selection.
Models use their existing versions; AOA ELM V2 and SMA ELMFIS V2 are distinct
corrected architectures. Neither scenario is certified current-price firstprint.
"""
from __future__ import annotations
import argparse,json,hashlib,math
from pathlib import Path
import numpy as np
import pandas as pd
import risk_v26_monthly_models_sensitivity as v26
from risk_v26_curated_models_stress import predictor, SELECTED

O=Path(__file__).parent/"outputs"
METALS=("Gold","Silver","Platinum","Palladium")
TARGETS=tuple(v26.base.month_range("2026-01","2026-09"))
SCENARIOS=v26.SCENARIOS
GPR_MIN="2010-01"

def guard(cond,msg):
    if not bool(cond):
        raise RuntimeError("V27_MONTHLY_INTEGRITY_"+msg)

def official_vintage_normalized():
    chunks=[]
    for i in (1,2):
        p=O/f"v27_gpr_normalized_origins_group_{i}.csv"
        z=pd.read_csv(p)
        guard(z.origin.notna().all() and z.source_commit.str.len().eq(40).all(),
              "GPR_GROUP_SOURCE_SHA_"+str(i))
        guard(z.released.notna().all(),"GPR_RELEASE_DATE_MISSING")
        for origin,g in z.groupby("origin"):
            last_day=(pd.Period(origin,freq="M")+1).start_time.tz_localize("UTC")
            guard(pd.to_datetime(g.released,utc=True).max()<last_day,
                  "GPR_REVISION_LATER_THAN_ORIGIN_END_"+origin)
            guard(g.source_commit.nunique()==1,"GPR_MULTIPLE_VERSIONS_"+origin)
        chunks.append(z[["origin","month","gpr_origin_normalized_z"]])
    for origin in ("2026-06","2026-07","2026-08"):
        f=O/f"v27_gpr_normalized_{origin.replace('-','')}.csv"
        chunks.append(pd.read_csv(f)[["origin","month","gpr_origin_normalized_z"]])
    z=pd.concat(chunks,ignore_index=True)
    guard(len(z)==sum(range(191,200)),"GPR_NINE_HISTORY_LENGTH")
    guard(not z.duplicated(subset=["origin","month"]).any(),"GPR_DUPLICATE_MONTHS")
    guard((z.gpr_origin_normalized_z.between(0,1)).all(),"GPR_NORMALIZATION_BOUND")
    out={}
    for origin,g in z.groupby("origin"):
        expected_months=list(v26.base.month_range("2010-01",v26.base.month_shift(origin,-1)))
        months=sorted(g.month.tolist())
        guard(months==expected_months,"GPR_ORIGIN_VINTAGE_MISSING_MONTH_"+origin)
        out[origin]=dict(zip(g.month,g.gpr_origin_normalized_z.astype(float)))
    guard(set(out)=={v26.base.month_shift(t,-1) for t in TARGETS},
          "GPR_FORECAST_ORIGIN_SET_MISMATCH")
    return out

def samples_at_origin(bundle,target,origin_normalized):
    """Mathematically equivalent to base.sample_for_target with identical GPR z.

    base.gpr_norm has z[m] = (GPR[m]-prefix_min)/(prefix_max-prefix_min),
    and we have queried exactly that sufficient statistic from the correct
    official Git/PIT origin vintage in Neon.
    """
    origin=v26.base.month_shift(target,-1)
    gpr=origin_normalized[origin]
    samples={}
    for t in v26.base.month_range("2010-03",target):
        p=v26.base.month_shift(t,-1)
        pp=v26.base.month_shift(t,-2)
        guard(pp in gpr,"MISSING_GPR_LAG_"+origin+"_"+pp)
        z=gpr[pp]
        x=[];y=[]
        for metal in METALS:
            m=bundle.monthly_metal[metal]
            guard(t in m and p in m and pp in m,"MISSING_PRICE_MONTH_"+metal+"_"+t)
            x.extend((math.log(m[p]/m[pp]),
                      v26.base.weighted_daily_return(bundle,metal,p,z)))
            y.append(math.log(m[t]/m[p]))
        sx=np.asarray(x,float)
        need_target=(t==target)
        samples[t]=(sx,None if need_target else np.asarray(y,float))
    guard(len(samples[target][0])==8 and samples[target][1] is None,
          "TARGET_LABEL_NOT_MASKED")
    guard(all(t<=target for t in samples),"FUTURE_MONTH_LEAKAGE")
    guard(sorted(t for t in samples if t<target)[-1]==origin,
          "ORIGIN_MISMATCH")
    return samples

def compute(models,targets,scenarios):
    d=v26.immutable_prices()
    official=official_vintage_normalized()
    recorded=[];fi=[]
    for scenario in scenarios:
        bundle=v26.construct(d,scenario,{})
        for target in targets:
            origin=v26.base.month_shift(target,-1)
            s=samples_at_origin(bundle,target,official)
            fx=s[target][0]
            hv=hashlib.sha256(fx.tobytes()).hexdigest()
            orig=float(bundle.core_gold[origin]);actual=float(bundle.core_gold[target])
            for model in models:
                logr,n,info=predictor(s,target,model)
                forecast=float(orig*math.exp(logr))
                v=dict(target_month=target,origin_month=origin,model=model,
                       scenario=scenario,forecast_gold_usd_oz=forecast,
                       actual_scenario_gold_usd_oz=actual,
                       origin_gold_usd_oz=orig,
                       error_abs_usd_oz=abs(forecast-actual),
                       error_ape_pct=100*abs(forecast-actual)/actual,
                       direction_correct=(forecast>orig)==(actual>orig),
                       predictor_inputs8_sha256=hv,
                       train_rows=n,price_historical_firstprint_proven=False,
                       forecast_is_blind_2026=False,
                       actual_full_month_verified=(target!="2026-02"),
                       target_Y_visible_during_training=False,
                       model_training_history_latest=origin)
                recorded.append(v)
                print("V27_MONTHLY",target,model,scenario,
                      "pred",round(forecast,5),"actual",round(actual,5),
                      "error",round(v["error_abs_usd_oz"],5),flush=True)
            fi.append(dict(target_month=target,origin_month=origin,scenario=scenario,
                feature_sha256=hv,feature8=list(map(float,fx)),
                training_months=len(s)-1,source_GPR_origin=origin,
                source_price_firstprints_PIT_certified=False,
                target_label_given_to_model=False))
    return pd.DataFrame(recorded),fi

def summaries(a,models):
    h=a[a.scenario.eq("CENSORED_ONE_DAY")].copy()
    h["eligible_for_assessed_error"]=h.target_month.ne("2026-02")
    stat=[]
    for model in models:
        x=h[(h.model==model)&h.eligible_for_assessed_error]
        guard(len(x)==8,"EIGHT_COMPARABLE_EVALUATION_MONTHS_"+model)
        stat.append(dict(model=model,months=8,
                 sum_abs_error=float(x.error_abs_usd_oz.sum()),
                 mae_usd_oz=float(x.error_abs_usd_oz.mean()),
                 mape_pct=float(x.error_ape_pct.mean()),
                 direction_correct=int(x.direction_correct.sum()),
                 percent_direction_correct=100*float(x.direction_correct.mean()),
                 worst_month=str(x.loc[x.error_abs_usd_oz.idxmax(),"target_month"]),
                 Feb_excluded_due_to_invalid_monthly_target=True,
                 blind_2026_research_only=True,
                 source_data_firstprints_PIT_proven=False))
    return pd.DataFrame(stat).sort_values("mae_usd_oz")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--months",default=",".join(TARGETS))
    parser.add_argument("--models",default=",".join(SELECTED))
    parser.add_argument("--scenarios",default=",".join(SCENARIOS))
    parser.add_argument("--parity-v26-march",action="store_true")
    args=parser.parse_args()
    t=args.months.split(",");model=args.models.split(",");sc=args.scenarios.split(",")
    guard(set(t).issubset(TARGETS),"BAD_TARGET")
    guard(set(model).issubset(SELECTED),"BAD_MODELS")
    guard(set(sc).issubset(SCENARIOS),"BAD_SCENARIOS")
    a,feat=compute(model,t,sc)
    if args.parity_v26_march:
        guard(t==["2026-03"],"PARITY_ONLY_MARCH")
        reference=pd.read_csv(O/"v26_curated_mar2026_models_COMMITTED.csv")
        for _,r in reference.iterrows():
            q=a[(a.model==r.model)&a.scenario==r.scenario]
            if len(q):
                guard(abs(float(q.forecast_gold_usd_oz.iloc[0])-float(r.forecast_gold_usd_oz))<.0002,
                      "ORIGINAL_V26_MARCH_FORECAST_PARITY_"+r.model+"_"+r.scenario)
        print("V27_V26_MARCH_PARITY_OK",len(a),flush=True)
    else:
        guard(t==list(TARGETS) and model==list(SELECTED) and sc==list(SCENARIOS),
              "FULL_REPLAY_MUST_USE_CANONICAL_SCOPE")
        a.to_csv(O/"v27_monthly_2026_jan_sep_all_models_three_scenarios.csv",index=False)
        p=a[a.scenario.eq("CENSORED_ONE_DAY")].pivot_table(
           index="target_month",columns="model",values="forecast_gold_usd_oz")
        actual=a[a.scenario.eq("CENSORED_ONE_DAY")].groupby("target_month").actual_scenario_gold_usd_oz.first()
        p.insert(0,"actual_research_average_usd_oz",actual)
        p.insert(1,"actual_is_full_month_verified",p.index!="2026-02")
        p.to_csv(O/"v27_2026_monthly_actual_vs_models_CONSERVATIVE_CENSORED.csv")
        stat=summaries(a,model)
        stat.to_csv(O/"v27_2026_models_8month_accuracy_FEB_EXCLUDED.csv",index=False)
        dx=a.pivot_table(index=["target_month","model"],columns="scenario",
                          values="forecast_gold_usd_oz")
        dx["CENSORED_MINUS_RAW_USD"]=dx["CENSORED_ONE_DAY"]-dx["RAW_UNTOUCHED"]
        dx["EXTERNAL_MINUS_RAW_USD"]=dx["EXTERNAL_CLOSE_ONLY_SENSITIVITY"]-dx["RAW_UNTOUCHED"]
        dx.to_csv(O/"v27_2026_model_raw_vs_censored_and_external_deltas.csv")
        (O/"v27_2026_origin_features_provenance.json").write_text(
           json.dumps(feat,indent=2)+"\n")
        meta=dict(targets=t,scenarios=sc,models=model,
           data_contract="STAKTRAKR_RESEARCH_PINNED_NOT_ASOF_CERTIFIED",
           GPR_normalized_from_historical_official_origin_vintages=True,
           model_code_versions_unchanged=True,ANFIS_CHHHO_original_optimizer=True,
           AOA_ELM_V2_distinct_bugfixed=True,SMA_ELMFIS_V2_distinct_inner_safe=True,
           price_firstprints_PIT_certified=False,
           fully_blind_2026_backtest=False,
           confirmed_bad_2026_02_27_all4metals_not_propagated_in_censored=True,
           censored_is_full_verified_month_target=False,
           old_raw_Neon_and_model_snapshots_mutated=False,
           source_day_2026_02_27_foreign_reference_same_fixing_definition_certified=False,
           Feb_2026_excluded_from_comparable_error_metrics=True,
           no_automatic_deployment=True)
        (O/"v27_2026_monthly_replay_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
        print("V27_ALL_2026_MONTHS\n"+p.to_string())
        print("V27_8MONTH_ACCURACY_FEB_EXCLUDED\n"+stat.to_string(index=False))
        print("V27_ALL_SCENARIO_SHIFT\n"+dx.to_string())
        print("V27_MONTHLY_2026_REPLAY_COMPLETE",len(a))
if __name__=="__main__":
    main()
