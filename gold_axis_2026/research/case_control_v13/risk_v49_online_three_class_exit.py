#!/usr/bin/env python3
"""V49: ONLINE 3-class competing-barrier learner for V22 WATCH -> EXIT signal.

Learns actual competing cases, not the complement of down:
  0 neither barrier within five NY17 sessions
  1 price -4% occurs before +2%
  2 price +2% occurs before -4%

Frozen foundational price pattern 2020-22. Every month, multiclass Logistic
Regression meta calibrator is fitted on previous 540 calendar days using
ALL-MARKET labels whose origin is at least 15 days in the past.
At each 15m bar, derived conditional P(down-first | either barrier hits)
is scored. Risk threshold is the past 1280 score-bar quantile, shifted by
one bar; a vol-normalized price break may also be required. No BUY/PnL.

CRITICAL: 2025/26 events were previously observed, NOT blind. 2025 original
V22 vs 2026 later V33 different research vintage. Timestamp firstprint and
executable quote never proven. No live signals.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation as v47
import gold_axis_2026.research.case_control_v13.risk_v48_online_adaptive_sell_only as v48
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as v44

QS=(.8,.9,.95)
META_FEATURES=("base_logit","ret1h","ret4h","ret24h","ret3d",
               "dd24","dd5d","ema96","ema480","volratio","down16")
MATURITY=15
LOOKBACK=540
SCORE_BARS=1280
METHODS=("ADAPTIVE_RANK","ADAPTIVE_RANK_PERSIST4",
         "ADAPTIVE_RANK_VOL_BREAK","V43_FIXED_REFERENCE")

def competing_labels(df,indices):
    """Future-only annotation for a fully ended FIVE-session horizon.

    Classes are mutually exclusive. Returns -1 for not-yet-matured.
    Same bar would hit neither %4 down and %2 up (single-price bars).
    This function must never be called by actual live signal decision.
    """
    p=df.p.to_numpy()
    session=df.session.to_numpy()
    last=int(session[-1])
    out=np.full(len(indices),-1,dtype="int8")
    for n,i in enumerate(indices):
        i=int(i)
        if session[i]+5>last:continue
        stop=int(np.searchsorted(session,session[i]+5,side="right"))
        a=p[i+1:stop]/p[i]-1
        downs=np.flatnonzero(a<=-.04)
        ups=np.flatnonzero(a>=.02)
        if len(downs) and (not len(ups) or downs[0]<ups[0]):
            out[n]=1
        elif len(ups):
            out[n]=2
        else:
            out[n]=0
    return out

def online_scores(df,f):
    base_model,platt,base_training=v47.fit_model(
        df,f,"2022-12-16","2023-01-01","2023-12-17")
    years=df.ts.dt.year.to_numpy()
    mask=years>=2023
    base_p=np.zeros(len(df),dtype="float64")
    base_p[mask]=v47.proba(base_model,platt,f.loc[mask])
    x=v48.meta_frame(f,base_p)
    for k in META_FEATURES:
        if k not in x:
            x[k]=f[k]
    x=x[list(META_FEATURES)].astype("float32")
    date=df.ts.dt.tz_localize(None).to_numpy()
    sample=np.arange(550,len(df),8)
    sample=sample[years[sample]>=2023]
    labels=competing_labels(df,sample)
    score=np.full(len(df),np.nan,dtype="float64")
    p_down=np.full(len(df),np.nan,dtype="float64")
    p_up=np.full(len(df),np.nan,dtype="float64")
    levels={str(q):np.full(len(df),np.nan,dtype="float64") for q in QS}
    journal=[]
    for t0 in pd.date_range("2025-01-01","2026-09-01",freq="MS"):
        t1=t0+pd.offsets.MonthBegin(1)
        first=np.datetime64(t0.to_pydatetime())
        last=np.datetime64(t1.to_pydatetime())
        rawmask=(date[sample]>=first-np.timedelta64(LOOKBACK,"D")) & \
                (date[sample]<=first-np.timedelta64(MATURITY,"D")) & \
                (labels>=0)
        idx=sample[rawmask]
        y=labels[rawmask]
        if len(idx)<1000 or len(set(y.tolist()))<3:
            raise RuntimeError(f"COMPETING_CLASS_DATA_TOO_SMALL {t0} {len(idx)} {sorted(set(y.tolist()))}")
        fit=make_pipeline(StandardScaler(),LogisticRegression(C=.18,max_iter=800,random_state=49))
        fit.fit(x.iloc[idx],y)
        current=np.flatnonzero((date>=first)&(date<last))
        if not len(current):continue
        seed=max(0,int(current[0])-SCORE_BARS)
        allix=np.arange(seed,int(current[-1])+1)
        res=fit.predict_proba(x.iloc[allix])
        classes=fit.named_steps["logisticregression"].classes_
        dd=res[:,int(np.where(classes==1)[0][0])]
        uu=res[:,int(np.where(classes==2)[0][0])]
        conditional=dd/(dd+uu+1e-8)
        n=len(current)
        score[current]=conditional[-n:]
        p_down[current]=dd[-n:]
        p_up[current]=uu[-n:]
        cond=pd.Series(conditional)
        for q in QS:
            cuts=cond.rolling(SCORE_BARS,min_periods=250).quantile(q).shift(1)
            levels[str(q)][current]=cuts.to_numpy()[-n:]
        counts=np.bincount(y,minlength=3).tolist()
        journal.append({
          "month":str(t0.date()),
          "usedOriginThrough":str(pd.Timestamp(first-np.timedelta64(MATURITY,"D")).date()),
          "sampleSize":len(idx),"classCounts":[int(v) for v in counts],
          "classDownFirstPct":round(100*counts[1]/len(y),3),
          "classUpFirstPct":round(100*counts[2]/len(y),3),
          "monthAvgDownProb":round(float(np.mean(p_down[current])),4),
          "monthAvgUpProb":round(float(np.mean(p_up[current])),4),
          "monthAvgRelativeDown":round(float(np.mean(score[current])),4),
          "monthAvgQ90":round(float(np.mean(levels[str(.9)][current])),4)
        })
    return score,levels,p_down,p_up,journal,base_training

def run():
    df=v47.fetch_bars()
    f=v47.feature_frame(df)
    score,levels,pdown,pup,journal,foundation=online_scores(df,f)
    diary,origin=v44.read_diaries()
    metrics=v48.normalized_metrics(df,f)
    outcomes={}
    for year in (2025,2026):
        x={}
        for q in QS:
            x[str(q)]={}
            for model in METHODS:
                data=v48.replay(df,f,diary[year],year,score,levels[str(q)],model,metrics)
                for entry in data["events"]:
                    sig=entry["signal"]
                    if sig:
                        # Here "riskProbability" is conditional likelihood
                        # P(down-first | either barrier hit), NOT P(down).
                        signal_day= pd.Timestamp(sig["time"])
                        ix=int(df.index[df.ts==signal_day][0])
                        sig["absoluteDownFirstProb"]=round(float(pdown[ix]),5)
                        sig["absoluteUpFirstProb"]=round(float(pup[ix]),5)
                        sig["relativeDownConditional"]=round(float(score[ix]),5)
                        sig["riskProbabilityMeaning"]="conditional_down_before_up_given_a_barrier"
                x[str(q)][model]=data
        outcomes[str(year)]=x
    totals={year:{q:{mode:{k:v for k,v in data.items() if k!="events"}
                         for mode,data in cohort.items()} for q,cohort in qs.items()}
            for year,qs in outcomes.items()}
    return {
      "schema":"GOLD_V49_MONTHLY_ROLLING_THREE_CLASS_COMPETING_RISK_EXIT_ONLY",
      "model":"rolling_540_day_three_class_none_downfirst_upfirst",
      "signal":"V22 early WATCH then evidence of -4% before +2%, never buy",
      "trainedBase":"HistGB 2020-22+Platt 2023",
      "trainedMeta":"monthly 540d, labels known >=15d before month",
      "scores":"P(downfirst)/(P(downfirst)+P(upfirst)), conditional risk, rolling quantile",
      "quantilesExplored":QS,
      "firstPrintVerified":False,
      "yearsPreviouslyInspected":True,
      "tradingOrders":False,"buySignals":False,
      "sameV22VintageBetweenYears":False,
      "baseFit":foundation,
      "monthlyModelDiary":journal,
      "V22Provenance":{"2025":origin[2025],"2026":origin[2026]},
      "summary":totals,"yearDetail":outcomes,
      "riskWarnings":[
        "2025/2026 known to research; this is not blind forward testing",
        "No unified firstprint V22 series for 2024–26",
        "No independent physical decline episode recall yet",
        "A lost rising rally after a signal remains a serious error even if a later drop follows",
        "5 NY17 session labels are retrospective; no future input in signal",
        "Last 15 days of maturation buffer used for all training examples",
        "No actual bank bids, quotes, execution, slippage, fees here",
        "A score percentile quantile is a fixed decision policy despite adapting to score distribution",
      ]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="gold-v49-online-competing-barrier-2025-2026.json")
    z=a.parse_args()
    x=run()
    Path(z.out).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
    print("V49_STATS",json.dumps(x["summary"],ensure_ascii=False),flush=True)
    print("V49_EVENTS",json.dumps({year:{q:{k:[{
       "warn":e["firstWarning"],
       "sig":e["signal"]["time"] if e["signal"] else None,
       "pdown":e["signal"].get("absoluteDownFirstProb") if e["signal"] else None,
       "pup":e["signal"].get("absoluteUpFirstProb") if e["signal"] else None,
       "down_first":e["signal"].get("hitDropBeforeUp") if e["signal"] else None,
       "down4":e["signal"].get("hitDrop4") if e["signal"] else None,
       "up_first":e["signal"].get("hitUpBeforeDrop") if e["signal"] else None
    } for e in d["events"]] for k,d in modes.items()} for q,modes in qs.items()}
       for year,qs in x["yearDetail"].items()},ensure_ascii=False),flush=True)
    print("V49_MONTHLY_MODEL_JOURNAL",json.dumps(x["monthlyModelDiary"],ensure_ascii=False),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## V49 rolling 3-class competing-barrier model\n\n")
            f.write("NO live deployment, no buy/re-entry, 2025/26 nonblind.\n\n")
            f.write("| year | quantile | method | exits | 4% dips | down-before-up | up-before-down | unmatched |\n")
            f.write("|---|---:|---|---:|---:|---:|---:|---:|\n")
            for yr,qs in x["summary"].items():
                for q,methods in qs.items():
                    for mode,r in methods.items():
                        f.write(f"| {yr} | {q} | {mode} | {r['signals']} | {r['drop4Within5']} | {r['drop4BeforeUp2']} | {r['up2BeforeDrop4']} | {r['noDrop4']} |\n")
if __name__=="__main__":main()
