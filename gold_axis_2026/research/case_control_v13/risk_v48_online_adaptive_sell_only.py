#!/usr/bin/env python3
"""V48: adaptive ONLINE learned and volatility-normalized SELL-only V22 confirmation.

What changes with time:
  * A foundational non-linear price-pattern model is fitted ONLY on 2020–22.
  * The competing-barrier probability calibrator is RE-FITTED at each
    month boundary using the PREVIOUS 540 calendar days, with a 15-day label
    maturation embargo (so no current-month outcomes enter its training).
  * The decision threshold moves with the LAST 1280 observed 15m scores,
    using a quantile of score DISTRIBUTION, not a fixed price percentage.
  * A volatility-normalized optional trend-break confirmation uses only
    trailing bars. No future price, no actual BUY, no cash strategy.
  * All risk episodes are watched only following V22 alerts; they expire
    8 calendar days after the LAST V22 reminder.

This is a HYPOTHESIS test, NOT a live / PIT-certified trading system.
Source V22 vintage differs: original 2025 daily V22, V33 replays for 2026.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from datetime import timedelta,date
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation as base
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as v44

CUTOFF_QUANTILES=(.80,.90,.95)
MODELS=("ADAPTIVE_RANK","ADAPTIVE_RANK_PERSIST4",
        "ADAPTIVE_RANK_VOL_BREAK","V43_FIXED_REFERENCE")
META_FEATURES=("base_logit","ret4h","ret24h","ret3d","dd5d",
               "ema480","volratio","down16")
RISK_LIFETIME_DAYS=8
MATURATION_DAYS=15
ROLLING_LABEL_DAYS=540
SCORE_LOOKBACK_BARS=1280

def meta_frame(features,base_p):
    x=pd.DataFrame(index=features.index)
    p=np.clip(base_p,1e-6,1-1e-6)
    x["base_logit"]=np.log(p/(1-p))
    for k in META_FEATURES[1:]:
        x[k]=features[k]
    return x.astype("float32")

def monthly_online_meta_scores(df,features):
    """At month t, only train on labels with origin <= t-15 days.
    Each future LABEL is from next 5 NY17 sessions, which mature before
    the 15-day embargo. A label never enters model before cutoff.
    All probability and threshold values at bar t depend only on bars <=t.
    """
    model,cal,training=base.fit_model(df,features,
                                  "2022-12-16","2023-01-01","2023-12-17")
    yrs=df.ts.dt.year.to_numpy()
    ts=df.ts.to_numpy()
    relevant=yrs>=2023
    base_p=np.zeros(len(df),dtype="float64")
    base_p[relevant]=base.proba(model,cal,features.loc[relevant])
    inputs=meta_frame(features,base_p)
    sample=np.arange(550,len(df),8)
    sample=sample[yrs[sample]>=2023]
    labels=base.first_hit_down_label(df,sample)
    assert len(sample)==len(labels)
    dates=df.ts.dt.tz_localize(None).to_numpy()
    scores=np.full(len(df),np.nan,dtype="float64")
    dynamic={str(q):np.full(len(df),np.nan,dtype="float64") for q in CUTOFF_QUANTILES}
    monthly=[]
    for month in pd.date_range("2025-01-01","2026-09-01",freq="MS"):
        monthend=month+pd.offsets.MonthBegin(1)
        start=np.datetime64(month.to_pydatetime())
        end=np.datetime64(monthend.to_pydatetime())
        training_end=start-np.timedelta64(MATURATION_DAYS,"D")
        training_start=start-np.timedelta64(ROLLING_LABEL_DAYS,"D")
        training_idx=sample[
            (dates[sample]>=training_start)&
            (dates[sample]<=training_end)&
            (labels>=0)]
        yy=labels[(dates[sample]>=training_start)&
            (dates[sample]<=training_end)&
            (labels>=0)]
        if len(training_idx)<1000 or len(np.unique(yy))<2:
            raise RuntimeError(f"META_TRAIN_NOT_SUFFICIENT {month} {len(training_idx)}")
        fit=make_pipeline(StandardScaler(),LogisticRegression(
            C=.18,max_iter=500,random_state=48))
        fit.fit(inputs.iloc[training_idx],yy)
        current=np.flatnonzero((dates>=start)&(dates<end))
        if not len(current):continue
        # Seed current month's threshold from earlier (already observed) bars;
        # predictions on those past bars use this month's now-current model.
        seedstart=max(0,int(current[0])-SCORE_LOOKBACK_BARS)
        all_indices=np.arange(seedstart,int(current[-1])+1,dtype=int)
        pred=fit.predict_proba(inputs.iloc[all_indices])[:,1]
        probs=pd.Series(pred,index=all_indices)
        scores[current]=probs.loc[current].to_numpy()
        for q in CUTOFF_QUANTILES:
            cut=probs.rolling(window=SCORE_LOOKBACK_BARS,
                             min_periods=250).quantile(q).shift(1)
            dynamic[str(q)][current]=cut.loc[current].to_numpy()
        monthly.append({
            "month":str(month.date()),
            "trainingWindowStart":str(pd.Timestamp(training_start).date()),
            "trainingOriginEnd":str(pd.Timestamp(training_end).date()),
            "trainingSamples":int(len(training_idx)),
            "positiveRatePct":round(100*float(np.mean(yy)),3),
            "currentScoreMean":round(float(np.mean(scores[current])),5),
            "currentQ90Mean":round(float(np.nanmean(dynamic[str(.90)][current])),5)
        })
    return scores,dynamic,monthly,training

def normalized_metrics(df,features):
    p=df.p.to_numpy()
    ts=df.ts
    low=df.p.rolling(96,min_periods=72).min().shift(1).to_numpy()
    ret4=features.ret4h.to_numpy()
    # Features scaling: 4h sigma under iid approximation used as volatility
    # baseline; NOT an executable price quote.
    vol4=np.maximum(4*features.vol96.to_numpy(),.0003)
    peakdraw_vol=2.5*vol4
    # Continuity matters; don't validate 4h ret through overnight gap.
    complete=np.zeros(len(df),dtype=bool)
    complete[16:]=((ts.iloc[16:].to_numpy() -
                   ts.iloc[:-16].to_numpy())==
                   np.timedelta64(4,"h"))
    return low,ret4,vol4,peakdraw_vol,complete

def replay(df,features,diary,year,prob,qcut,method,metric):
    idx=np.flatnonzero(df.ts.dt.year.to_numpy()==year)
    if not len(idx):return {}
    first,last=int(idx[0]),int(idx[-1])+1
    price=df.p.to_numpy()
    ts=df.ts
    low,ret4,vol4,peakdraw_vol,complete=metric
    state="IDLE";episode=None;episodes=[]
    last_day=None;last_risk=None;pending=None
    streak=0
    for i in range(first,last):
        t=ts.iloc[i]
        today=df.day.iloc[i]
        if pending is not None:
            mins=int((t-pending["rawTimestamp"]).total_seconds()/60)
            pending["fillTime"]=str(t)
            pending["fillPrice"]=round(float(price[i]),3)
            pending["fillGapMinutes"]=mins
            pending["validFill"]=mins==15
            pending.pop("rawTimestamp")
            pending=None
        if last_day is not None and today!=last_day and diary.get(last_day,False):
            last_risk=last_day
            if state=="IDLE":
                episode={"firstWarning":str(last_day),"lastWarning":str(last_day),
                         "riskRefreshes":1,"firstBar":str(t),
                         "maxSoFar":float(price[i]),"signal":None}
                episodes.append(episode)
                state="WATCH";streak=0
            else:
                episode["lastWarning"]=str(last_day)
                episode["riskRefreshes"]+=1
        last_day=today
        if state!="IDLE" and last_risk is not None and (today-last_risk).days>RISK_LIFETIME_DAYS:
            episode["lastBar"]=str(t)
            state="IDLE";episode=None;streak=0
        if state=="IDLE":continue
        episode["maxSoFar"]=max(episode["maxSoFar"],float(price[i]))
        if state=="EXIT_RECORDED":continue
        # Predeclared historical benchmark with fixed price pattern.
        if method=="V43_FIXED_REFERENCE":
            active=complete[i] and price[i]<low[i] and ret4[i]<=-.01 \
                   and price[i]<=episode["maxSoFar"]*.99
        else:
            th=qcut[i]
            ok=np.isfinite(prob[i]) and np.isfinite(th) and prob[i]>=th
            # Avoid maintaining streak across market gaps.
            if i==first or ((ts.iloc[i]-ts.iloc[i-1])!=pd.Timedelta(minutes=15)):
                streak=0
            streak=streak+1 if ok else 0
            if method=="ADAPTIVE_RANK":
                active=bool(ok)
            elif method=="ADAPTIVE_RANK_PERSIST4":
                active=bool(streak>=4)
            elif method=="ADAPTIVE_RANK_VOL_BREAK":
                # volatility-scaled not static % distance; still technical
                # confirmation, empirically stronger if no false break.
                active=bool(ok and complete[i] and
                    np.isfinite(low[i]) and price[i]<low[i] and
                    ret4[i]<=-vol4[i] and
                    price[i]/episode["maxSoFar"]-1<=-peakdraw_vol[i])
            else:raise ValueError(method)
        if active:
            signal={"time":str(t),"price":round(float(price[i]),3),
              "riskProbability":round(float(prob[i]),5) if np.isfinite(prob[i]) else None,
              "dynamicThreshold":round(float(qcut[i]),5) if np.isfinite(qcut[i]) else None,
              "rollingVol4":round(float(vol4[i]),5),
              "trend4hPct":round(100*float(np.expm1(ret4[i])),3),
              "peakDrawPct":round(100*(price[i]/episode["maxSoFar"]-1),3),
              "rawTimestamp":t,
              "fillTime":None,"fillPrice":None,"validFill":False}
            episode["signal"]=signal
            pending=signal
            state="EXIT_RECORDED"
    if episode is not None:
        episode["lastBar"]=str(ts.iloc[last-1])
    # Outcome audit. No future data used in the state transition.
    for e in episodes:
        s=e["signal"]
        if not s or not s["validFill"]:continue
        fill_ix=int(df.index[df.ts==pd.Timestamp(s["fillTime"])][0])
        if fill_ix>=len(price):continue
        current_session=int(df.session.iloc[fill_ix])
        if current_session+5>int(df.session.iloc[-1]):
            s["matured5"]=False;continue
        end=int(np.searchsorted(df.session.to_numpy(),current_session+5,side="right"))
        follow=price[fill_ix+1:end]
        if len(follow)<1:continue
        fp=s["fillPrice"]
        down=np.flatnonzero(follow/fp<=.96)
        up=np.flatnonzero(follow/fp>=1.02)
        s["matured5"]=True
        s["hitDrop4"]=bool(len(down))
        s["hitDropBeforeUp"]=bool(len(down) and (not len(up) or down[0]<up[0]))
        s["hitUpBeforeDrop"]=bool(len(up) and (not len(down) or up[0]<down[0]))
        s["worst5Pct"]=round(100*(float(np.min(follow))/fp-1),3)
        s["best5Pct"]=round(100*(float(np.max(follow))/fp-1),3)
        start_ix=int(df.index[df.ts==pd.Timestamp(e["firstBar"])][0])
        end_ix=int(df.index[df.ts==pd.Timestamp(e.get("lastBar",ts.iloc[last-1]))][0])
        s["lostUpsideInRiskEpisodePct"]=round(100*max(
            float(np.max(price[fill_ix:end_ix+1]))/fp-1,0),3) if end_ix>=fill_ix else 0
    signals=[x["signal"] for x in episodes if x["signal"] is not None]
    mature=[x for x in signals if x.get("matured5") is True]
    return {
      "riskEpisodes":len(episodes),
      "signals":len(signals),
      "mature5":len(mature),
      "drop4Within5":sum(bool(x["hitDrop4"]) for x in mature),
      "drop4BeforeUp2":sum(bool(x["hitDropBeforeUp"]) for x in mature),
      "up2BeforeDrop4":sum(bool(x["hitUpBeforeDrop"]) for x in mature),
      "noDrop4":sum(not x["hitDrop4"] for x in mature),
      "noSignal":len(episodes)-len(signals),
      "meanLostUpsidePct":round(float(np.mean([x["lostUpsideInRiskEpisodePct"] for x in mature])),3) if mature else None,
      "events":[{"firstWarning":x["firstWarning"],"lastWarning":x["lastWarning"],
                 "updates":x["riskRefreshes"],
                 "signal":x["signal"]} for x in episodes]
    }

def run():
    df=base.fetch_bars()
    features=base.feature_frame(df)
    scores,dynamic,updates,foundation=monthly_online_meta_scores(df,features)
    diaries,provenance=v44.read_diaries()
    metric=normalized_metrics(df,features)
    outcomes={}
    for yr in (2025,2026):
        cohort={}
        for q in CUTOFF_QUANTILES:
            name=str(q)
            cohort[name]={mode:replay(df,features,diaries[yr],yr,scores,dynamic[name],mode,metric)
                for mode in MODELS}
        outcomes[str(yr)]=cohort
    aggregate={
       year:{q:{mode:{k:v for k,v in info.items() if k!="events"}
            for mode,info in x.items()} for q,x in cohort.items()}
       for year,cohort in outcomes.items()
    }
    return {
      "schema":"GOLD_V48_ROLLING_META_CALIBRATION_ADAPTIVE_RISK_RANK_EXIT_ONLY",
      "evidence":"RETROSPECTIVE_NONPIT_HISTDATA_AND_DIFFERENT_V22_VERSIONS",
      "learned": "base HistGB 2020-22 + Platt 2023; monthly refit meta on matured trailing 540d",
      "adaptations":{
        "model":"rolling 540 calendar days, monthly updates",
        "outcomeMaturationBufferDays":MATURATION_DAYS,
        "riskQuantile":"last 1280 price-bar scores, excluding current",
        "quantilesFixedForRobustness":CUTOFF_QUANTILES,
        "volatileBreakpoint":"4h sigma*past vol (no absolute fixed % thresholds)",
        "v22RiskExpiryCalendarDays":RISK_LIFETIME_DAYS,
      },
      "primaryOutcome":"next5 NY17 sessions -4pct before +2pct",
      "labelTraining":"all-market proxy first-hit; this is not V22-specific hazard labeling",
      "foundation":foundation,
      "monthlyLearningJournal":updates,
      "source":"Neon HistData candidate 2020-2026 + V22 research diary",
      "v22Vintage":{"2025":provenance[2025],"2026":provenance[2026]},
      "noBuys":True,"noTrading":True,"productionChanged":False,
      "noVerifiedFirstprint":True,
      "results":outcomes,"summary":aggregate,
      "limitations":[
        "Original V22 2025 and later V33 2026 aren't identical historical model versions.",
        "All years were previously seen in research; 2025/26 is not truly blind.",
        "Risk episodes defined by V22 coverage, not full physical decline recall.",
        "Rolling threshold uses past scores from current fitted model; training uses only matured labels.",
        "Meta labels are all-market 5-session first hits, not direct V22 risk episodes.",
        "Insufficient warning events for reliable precision interval; thresholds were not selected on 2025/26 outcomes.",
        "HistData candidate bars not authenticated as firstprint or actual bank executable prices.",
        "A fixed quantile and risk-lifetime are policy parameters; 'adaptive' does not eliminate design choices.",
      ],
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="gold-v48-rolling-adaptive-exit-2025-2026.json")
    args=a.parse_args()
    report=run()
    Path(args.out).write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
    print("V48_FOUNDATION",json.dumps(report["foundation"],ensure_ascii=False))
    print("V48_MONTHLY",json.dumps(report["monthlyLearningJournal"],ensure_ascii=False))
    print("V48_COMPARE",json.dumps(report["summary"],ensure_ascii=False),flush=True)
    print("V48_EVENTS",json.dumps({year:{q:{mode:[
      {"firstWarning":z["firstWarning"],
       "signal":z["signal"]["time"] if z["signal"] else None,
       "score":z["signal"].get("riskProbability") if z["signal"] else None,
       "threshold":z["signal"].get("dynamicThreshold") if z["signal"] else None,
       "price":z["signal"].get("fillPrice") if z["signal"] else None,
       "down4":z["signal"].get("hitDrop4") if z["signal"] else None,
       "downBeforeUp":z["signal"].get("hitDropBeforeUp") if z["signal"] else None,
       "upBeforeDown":z["signal"].get("hitUpBeforeDrop") if z["signal"] else None
       } for z in r["events"]] for mode,r in cohort.items()}
       for q,cohort in qset.items()} for year,qset in report["results"].items()},
       ensure_ascii=False),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
      with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as h:
        h.write("## V48 month-wise online adaptive sell-only audit\n\n")
        h.write("Research-only, no live promotion or buy/reentry.\n\n")
        h.write("| Year | Quantile | Model | V22 windows | EXIT | Dip ≥4% | Drop-first | Rally-first | False |\n")
        h.write("|---|---:|---|---:|---:|---:|---:|---:|---:|\n")
        for yr,qs in report["summary"].items():
          for q,methods in qs.items():
            for mode,m in methods.items():
              h.write(f"| {yr} | {q} | {mode} | {m['riskEpisodes']} | {m['signals']} | {m['drop4Within5']} | {m['drop4BeforeUp2']} | {m['up2BeforeDrop4']} | {m['noDrop4']} |\n")
if __name__=="__main__":main()
