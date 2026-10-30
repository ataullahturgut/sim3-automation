#!/usr/bin/env python3
"""V39 low-false-alarm feasibility: frozen probabilistic risk prior + hourly 4-metal concurrence.

RESEARCH ONLY, not prospective or live. Gold-origin >=4% drop next 5 price
sessions is the sole learning target. 2024: model-fit; 2025: false-alarm
budget selection; 2026: chronological replay. All price/vintage limitations
of 2026 backfills retained. 4-metal hourly thresholds are exploratory
(because source has no 2024-25 same-asset hourly history).
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from datetime import date
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from gold_axis_2026.research.case_control_v13.risk_v38_staktrakr_synchronous_fourmetal_shadow_v1 import (
    read_neon as read_intraday,original_rows,compile_calendar,mature_calendar
)
FEATURES=("au_ret1","au_ret5","au_trough10","ag_ret1","ag_ret5",
          "pt_ret1","pt_ret5","pd_ret1","pd_ret5",
          "metal_breadth1","metal_average5","metal_dispersion1",
          "gvz_old","gvz_change_old","rate_change_old")
SQL_PRICES="""
WITH raw AS(
 SELECT observation_ts::date AS dt,substring(series_id,2,2) AS metal,value AS p
 FROM public.observations WHERE series_id IN(
  'XAU_STAKTRAKR_RESEARCH_DAILY_R1','XAG_STAKTRAKR_RESEARCH_DAILY_R1',
  'XPT_STAKTRAKR_RESEARCH_DAILY_R1','XPD_STAKTRAKR_RESEARCH_DAILY_R1')
 AND observation_ts>='2023-12-01' AND observation_ts<'2026-01-01'
 UNION ALL SELECT price_date,metal,spot_usd_oz::float8
 FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
 WHERE price_date>='2026-01-01' AND price_date<'2026-11-01'
),p AS(
 SELECT dt,max(p) FILTER(WHERE metal='AU') au,
 max(p) FILTER(WHERE metal='AG') ag,max(p) FILTER(WHERE metal='PT') pt,
 max(p) FILTER(WHERE metal='PD') pd
 FROM raw GROUP BY 1
)
SELECT dt,au,ag,pt,pd
FROM p WHERE extract(isodow from dt) BETWEEN 1 AND 5
AND au>0 AND ag>0 AND pt>0 AND pd>0 ORDER BY dt
"""
SQL_MACRO="""
SELECT DISTINCT ON (observation_ts::date,series_id)
 observation_ts::date AS dt,series_id,value
FROM public.observations WHERE
 (series_id='GVZ_CBOE_FRED_MIRROR_RESEARCH_V1'
  AND observation_ts>='2023-12-01' AND observation_ts<'2026-01-01')
 OR(series_id='GVZ_CBOE'
  AND observation_ts>='2026-01-01' AND observation_ts<'2026-11-01')
 OR(series_id='DGS10_FRB_H15'
  AND observation_ts>='2023-12-01' AND observation_ts<'2026-11-01')
ORDER BY observation_ts::date,series_id,observation_ts DESC
"""
def read_daily():
    import psycopg
    uri=os.getenv("NEON_DATABASE_URL","")
    if not uri:raise RuntimeError("MISSING_NEON_DATABASE_URL")
    with psycopg.connect(uri,connect_timeout=22,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as c:
            c.execute(SQL_PRICES)
            p=[{"date":r[0],"au":float(r[1]),"ag":float(r[2]),
                "pt":float(r[3]),"pd":float(r[4])} for r in c]
            c.execute(SQL_MACRO)
            macro={}
            for d,s,v in c:
                macro.setdefault(d,{})["gvz" if s.startswith("GVZ") else "rate"]=float(v)
    for r in p:r.update(macro.get(r["date"],{}))
    return p

def add_features(prices):
    # At day d: only returns from completed d-1 and earlier price days.
    out=[]
    for i,r in enumerate(prices):
        if i<12:continue
        prev=prices[i-1]
        prior5=prices[i-6]
        prev10=prices[i-11:i]
        macro=prices[i-2]
        earlier_macro=prices[i-3]
        f={}
        for m in ("au","ag","pt","pd"):
            f[m+"_ret1"]=100*(prev[m]/prices[i-2][m]-1)
            f[m+"_ret5"]=100*(prev[m]/prior5[m]-1)
        f["au_trough10"]=100*(prev["au"]/max(x["au"] for x in prev10)-1)
        f["metal_breadth1"]=sum(f[m+"_ret1"]<0 for m in ("ag","pt","pd"))
        f["metal_average5"]=sum(f[m+"_ret5"] for m in ("ag","pt","pd"))/3
        f["metal_dispersion1"]=float(np.std([f[m+"_ret1"] for m in ("au","ag","pt","pd")]))
        f["gvz_old"]=macro.get("gvz",float("nan"))
        f["gvz_change_old"]=(macro["gvz"]-earlier_macro["gvz"] if
                             "gvz" in macro and "gvz" in earlier_macro else float("nan"))
        f["rate_change_old"]=(macro["rate"]-earlier_macro["rate"] if
                              "rate" in macro and "rate" in earlier_macro else float("nan"))
        row={**r,"features":f,"lastSourceDay":prev["date"],"lastMacroDay":macro["date"]}
        out.append(row)
    return out

def label_targets(rows):
    # Only completed future prices; year boundary embargo prevents a 2024
    # training label reading January 2025, and likewise validation into 2026.
    a=[]
    for i,r in enumerate(rows):
        if i+5>=len(rows):continue
        future=rows[i+1:i+6]
        if (future[-1]["date"]-r["date"]).days>12:continue
        if future[-1]["date"].year!=r["date"].year:continue
        target=(100*(min(x["au"] for x in future)/r["au"]-1)<=-4)
        a.append({**r,"label":bool(target)})
    return a

def transform(fit,valid,eval_rows):
    Xtr=np.array([[r["features"][f] for f in FEATURES] for r in fit],dtype=float)
    Xval=np.array([[r["features"][f] for f in FEATURES] for r in valid],dtype=float)
    Xt=np.array([[r["features"][f] for f in FEATURES] for r in eval_rows],dtype=float)
    imp=SimpleImputer(strategy="median",keep_empty_features=True)
    scaler=RobustScaler()
    Xtr=scaler.fit_transform(imp.fit_transform(Xtr))
    Xval=scaler.transform(imp.transform(Xval))
    Xt=scaler.transform(imp.transform(Xt))
    model=LogisticRegression(C=0.12,class_weight="balanced",solver="liblinear",max_iter=700)
    y=np.array([int(r["label"]) for r in fit],dtype=int)
    if len(set(y))<2:raise ValueError("NOT_ENOUGH_TRAIN_POSITIVES")
    model.fit(Xtr,y)
    return model.predict_proba(Xval)[:,1],model.predict_proba(Xt)[:,1],{
        "nonzeroCoefficients":dict(zip(FEATURES,np.round(model.coef_[0],4).tolist())),
        "trainPositive":int(sum(y))}

def emitted_episodes(rows,flag_fn,quiet=8):
    # Stateful alert policy: next independent alert only after quiet sessions.
    # This changes message frequency, NOT raw signal predictive accuracy.
    alerts=[]
    last=-100
    for i,r in enumerate(rows):
        if flag_fn(r) and i-last>quiet:
            alerts.append((i,r))
            last=i
    return alerts

def episode_stats(rows,flag_fn):
    emitted=emitted_episodes(rows,flag_fn)
    # Condition: after alert day, a >=4% fall within the next 10
    # completed observation days, relative to the alert's own close.
    # Tighter five-day outcome remains separately reported.
    good5=0;good10=0
    for i,r in emitted:
        for n in (5,10):
            later=rows[i+1:i+n+1]
            hit=(len(later)==n and
                 (later[-1]["date"]-r["date"]).days<=22 and
                 100*(min(x["au"] for x in later)/r["au"]-1)<=-4)
            if n==5 and hit:good5+=1
            if n==10 and hit:good10+=1
    return {"alerts":len(emitted),"hitNext5":good5,"noHitNext5":len(emitted)-good5,
            "hitNext10":good10,"noHitNext10":len(emitted)-good10,
            "dates":[str(r["date"]) for _,r in emitted]}

def calibrate_threshold(validation,probs,budget):
    # 2025-only ranking of thresholds, maximizing 2025 next5-detection
    # while limiting *unmatched* alert EPISODES to budget.
    # Strictly zero 2026 labels or prices may be used here.
    opts=sorted(set([1.0,*[float(x) for x in np.quantile(probs,np.linspace(.50,.995,90))]]))
    chosen=[]
    for cutoff in opts:
        label=lambda r:r["riskProb"]>=cutoff
        stats=episode_stats(validation,label)
        if stats["noHitNext5"]<=budget:
            chosen.append((stats["hitNext5"],-stats["noHitNext5"],
                           -stats["alerts"],cutoff,stats))
    if not chosen:raise ValueError("NO_THRESHOLD_IN_VALIDATION_BUDGET")
    best=max(chosen,key=lambda z:z[:3])
    return best[3],best[4]

def build():
    prices=read_daily()
    allfeatures=add_features(prices)
    labeled=label_targets(allfeatures)
    train=[r for r in labeled if r["date"].year==2024]
    validation=[r for r in labeled if r["date"].year==2025]
    eval_all=[r for r in allfeatures if r["date"].year==2026]
    if len(train)<200 or len(validation)<200 or len(eval_all)<175:
        raise ValueError("NOT_ENOUGH_PRICE_OR_FEATURE_DAYS")
    valp,testp,coeff=transform(train,validation,eval_all)
    for r,p in zip(validation,valp):r["riskProb"]=float(p)
    for r,p in zip(eval_all,testp):r["riskProb"]=float(p)
    val_selected={}
    for budget in (3,6,10):
        threshold,validated=calibrate_threshold(validation,valp,budget)
        val_selected[budget]={"threshold":threshold,"validation":validated}
    original=original_rows()
    intraday=compile_calendar(read_intraday(),original)
    intramap={r["date"]:r for r in intraday}
    matched=[r for r in eval_all if r["date"] in intramap]
    if len(matched)<145:raise ValueError("TOO_FEW_2026_FOUR_METAL_DAYS")
    for r in matched:
        x=intramap[r["date"]]
        r["v22"]=bool(x["v22"])
        r["goldHard"]=x["xau_hard"]>0
        r["fourMetal"]=x["four_same_1pct"]>0
        r["stakPrice"]=float(x["stak_price"])
    # Preserve chronological matched calendar; labels for next5 price
    # days evaluated on this common 4metal hourly coverage.
    matured=[r for i,r in enumerate(matched)
             if i+5<len(matched) and
             (matched[i+5]["date"]-r["date"]).days<=12]
    for r in matured:
        i=matched.index(r)
        r["future4"]=100*(min(z["au"] for z in matched[i+1:i+6])/r["au"]-1)<=-4
    if len(matured)<130:raise ValueError("NOT_ENOUGH_MATURED_2026_DAYS")
    models={"V22":lambda r:r["v22"],
            "V22_OR_RAW_ALL4":lambda r:r["v22"] or r["fourMetal"]}
    for budget,d in val_selected.items():
        c=d["threshold"]
        models[f"PRIOR_RISK_ONLY_B{budget}"]=lambda r,c=c:r["riskProb"]>=c
        models[f"V22_OR_ALL4_AND_RISK_B{budget}"]=(
            lambda r,c=c:r["v22"] or(r["fourMetal"] and r["riskProb"]>=c))
        models[f"HIGH_PRIORITY_V22_AND_RISK_B{budget}"]=(
            lambda r,c=c:r["v22"] and r["riskProb"]>=c)
    score={}
    truth=sum(r["future4"] for r in matured)
    for name,fn in models.items():
        alert=[r for r in matured if fn(r)]
        hits=sum(r["future4"] for r in alert)
        score[name]={"warningDays":len(alert),"next5MatchedDays":hits,
                     "next5UnmatchedDays":len(alert)-hits,
                     "positiveOriginRecallPct":round(100*hits/truth,2) if truth else None,
                     "dayPrecisionPct":round(100*hits/len(alert),2) if alert else None,
                     "episode":episode_stats(matched,fn)}
    # Each original BASE14/V22 risk diary available only after day close.
    event_dates=(("Mayıs",date(2026,5,13)),("Haziran_I",date(2026,6,4)),
                 ("Haziran_II",date(2026,6,17)),
                 ("Ağustos",date(2026,8,25)),("Eylül",date(2026,9,21)))
    events=[]
    for name,d in event_dates:
        prior=[r for r in matched if r["date"]<d][-10:]
        events.append({"name":name,"start":str(d),
                       "firstSignals":{m:(str(next((r["date"] for r in prior if fn(r)),None))
                                           if any(fn(r) for r in prior) else None)
                                       for m,fn in models.items()}})
    return {
      "schema":"GOLD_V39_FROZEN_REGIME_PRIOR_AND_SAME_HOUR_FOURMETAL_RISK_GATE",
      "status":"HISTORICAL_RESEARCH_NOT_PIT_OR_LIVE",
      "training":"2024_4metal_daily_lagged_logit_7_or_fewer_independent_events",
      "validation":"2025_heldout_budget_select_no_2026_labels",
      "evaluation":"2026_MARCH_OCT_HOURLY_BACKFILLED_NOT_BLIND",
      "trainRows":len(train),"validationRows":len(validation),
      "testPriceDays":len(eval_all),"testCommonFourMetalDays":len(matched),
      "testScoredDays":len(matured),"testFuture4OriginDays":truth,
      "sourceSameForHourly2024_2025":False,"prospectiveCertified":False,
      "oldV22Overwritten":False,"neonWrites":False,"tradingActions":False,
      "modelDetails":coeff,
      "calibration":val_selected,"tests":score,"events":events,
      "warnings":[
        "2024 has very few >=4pct next5 target days; coefficients unstable",
        "2026 has already been inspected during research; NOT untouched blind holdout",
        "4metal hourly shock threshold (all 4 <=-1%) is heuristic, NOT 2024-25 hourly calibrated",
        "episode 8-session suppression controls message count, not predictive truth",
        "historical source firstprint and daily model timestamp certs incomplete",
        "no live signals or automatic upgrades; research shadow only"
      ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-v39-low-false-alarm-validation.json")
    a=p.parse_args()
    report=build()
    Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2,default=str))
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:
            f.write("## V39 2024 train / 2025 false-alarm calibration / 2026 shadow audit\n\n")
            f.write("| Model | Alerts | Next5 matched | Unmatched | Episode alerts | Episode next10 unmatched |\n")
            f.write("|---|---:|---:|---:|---:|---:|\n")
            for model,r in report["tests"].items():
                f.write(f"| {model} | {r['warningDays']} | {r['next5MatchedDays']} | "
                        f"{r['next5UnmatchedDays']} | {r['episode']['alerts']} | "
                        f"{r['episode']['noHitNext10']} |\n")
            f.write("\n**Historical research only, no firstprint and no live changes.**\n")
if __name__=="__main__":main()
