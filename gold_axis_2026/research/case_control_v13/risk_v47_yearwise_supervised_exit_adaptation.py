#!/usr/bin/env python3
"""Gold V47: supervised, year-purged, chronological adaptive sell-signal research.

An EARLY_RISK V22 alert is *not* a sell. The ML learner estimates P(the next
five NY17 FX market sessions hit -4% before +2% price rally). Only observations
known at the current 15m bar are used for features. Labels are created strictly
from future bars; a 12-day purge prevents training on outcomes spilling into
the next calendar cohort. V22 starts an independent WATCH state; learned model
supplies confirmation. No buy/re-entry and no simulated portfolio profit.

Development 2020-22, probability calibration 2023, threshold quantiles from
2024 price distribution WITHOUT 2024 future labels, evaluation 2025 and
2026; 2026 can optionally use retrained 2020-24/calibrated 2025 model.
Prior research observed 2025/26 events, so these are retrospective stress
tests, NOT independent blind tests. Original 2024/25 V22 version != V33/2026.
"""
from __future__ import annotations
import argparse,csv,json,os,hashlib,math
from pathlib import Path
from datetime import timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as v44

FEATURES=("ret1h","ret4h","ret12h","ret24h","ret3d","dd24","dd5d",
          "rangepos24","rangepos5d","ema96","ema480","vol16","vol96",
          "volratio","down16","down96","gap4")
THRESHOLD_QUANTILES=(.7,.8,.9,.95)
RISK_EXPIRY_DAYS=8
TARGET_DOWN=.04
TARGET_UP=.02
FUTURE_SESSIONS=5

def fetch_bars():
    import psycopg
    uri=os.getenv("NEON_DATABASE_URL","")
    if not uri:raise ValueError("NEON_DATABASE_URL missing")
    sql="""SELECT bar_start_utc,close_price::double precision
       FROM public.gold_research_histdata_xau15m_candidate
       WHERE bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-10-02'
       ORDER BY bar_start_utc"""
    with psycopg.connect(uri,options="-c default_transaction_read_only=on",connect_timeout=25) as db:
      with db.cursor() as c:
        c.execute(sql)
        x=c.fetchall()
    if len(x)<140000:raise ValueError("TOO_FEW_HISTORICAL_BARS")
    df=pd.DataFrame(x,columns=["ts","p"])
    df["ts"]=pd.to_datetime(df["ts"],utc=True)
    df["p"]=pd.to_numeric(df["p"])
    if not df.ts.is_monotonic_increasing or df.ts.duplicated().any():
        raise ValueError("OUT_OF_ORDER_OR_DUPLICATES")
    if (df.p<=0).any():raise ValueError("NONPOSITIVE_PRICE")
    df["day"]=df.ts.dt.date
    local=df.ts.dt.tz_convert("America/New_York")
    # NY 17:00 market roll forward; 18:00 Sunday belongs Monday session.
    market=(local.dt.floor("D")+
         pd.to_timedelta((local.dt.hour>=17).astype(int),unit="D")).dt.date
    df["session"]=pd.factorize(market)[0]
    return df

def feature_frame(df):
    p=df.p
    f=pd.DataFrame(index=df.index)
    f["ret1h"]=np.log(p/p.shift(4)).where((df.ts-df.ts.shift(4))==pd.Timedelta(hours=1))
    f["ret4h"]=np.log(p/p.shift(16)).where((df.ts-df.ts.shift(16))==pd.Timedelta(hours=4))
    f["ret12h"]=np.log(p/p.shift(48)).where((df.ts-df.ts.shift(48))==pd.Timedelta(hours=12))
    f["ret24h"]=np.log(p/p.shift(96)).where((df.ts-df.ts.shift(96))==pd.Timedelta(hours=24))
    # Last 288 recorded 15min bars, not mislabeled 3 actual calendar days.
    f["ret3d"]=np.log(p/p.shift(288))
    mx24=p.rolling(96,min_periods=72).max().shift(1)
    mi24=p.rolling(96,min_periods=72).min().shift(1)
    mx5=p.rolling(480,min_periods=360).max().shift(1)
    mi5=p.rolling(480,min_periods=360).min().shift(1)
    f["dd24"]=p/mx24-1
    f["dd5d"]=p/mx5-1
    f["rangepos24"]=((p-mi24)/(mx24-mi24+1e-8)).clip(-2,3)
    f["rangepos5d"]=((p-mi5)/(mx5-mi5+1e-8)).clip(-2,3)
    f["ema96"]=p/p.ewm(span=96,adjust=False).mean()-1
    f["ema480"]=p/p.ewm(span=480,adjust=False).mean()-1
    dr=np.log(p/p.shift(1)).where((df.ts-df.ts.shift(1))==pd.Timedelta(minutes=15))
    f["vol16"]=dr.rolling(16,min_periods=12).std()
    f["vol96"]=dr.rolling(96,min_periods=72).std()
    f["volratio"]=(f["vol16"]/(f["vol96"]+1e-8)).clip(0,8)
    f["down16"]=(dr<0).rolling(16,min_periods=12).mean()
    f["down96"]=(dr<0).rolling(96,min_periods=72).mean()
    f["gap4"]=(df.ts-df.ts.shift(16)!=pd.Timedelta(hours=4)).astype(int)
    return f[list(FEATURES)].replace([np.inf,-np.inf],np.nan).fillna(0).clip(-2,2).astype("float32")

def first_hit_down_label(df,idx):
    """Causal annotation; future is used ONLY for training/evaluation labels.
    Stop at end of fifth NEXT NY17 market session, after current session.
    """
    p=df.p.to_numpy()
    sess=df.session.to_numpy()
    labels=[]
    last=int(sess[-1])
    for i in idx:
        if sess[i]+5>last:
            labels.append(-1);continue
        end=int(np.searchsorted(sess,sess[i]+5,side="right"))
        if end<=i+1:
            labels.append(-1);continue
        after=p[i+1:end]/p[i]-1
        u=np.flatnonzero(after>=TARGET_UP)
        d=np.flatnonzero(after<=-TARGET_DOWN)
        labels.append(1 if len(d) and (not len(u) or d[0]<u[0]) else 0)
    return np.array(labels,dtype="int8")

def fit_model(df,f,train_until,calib_start,calib_until):
    # Purge labels crossing cohort boundary and reduce near-duplicate bars:
    # 1 training point each 2 hours. 12 day embargo at each boundary.
    sample=np.arange(550,len(df),8)
    day=df.ts.dt.date.astype(str).to_numpy()
    train=sample[(day[sample]>= "2020-01-01")&
                 (day[sample] <= train_until)]
    calibrate=sample[(day[sample]>=calib_start)&(day[sample]<=calib_until)]
    yt=first_hit_down_label(df,train)
    yc=first_hit_down_label(df,calibrate)
    train=train[yt>=0];yt=yt[yt>=0]
    calibrate=calibrate[yc>=0];yc=yc[yc>=0]
    if len(train)<5000 or len(calibrate)<800:
        raise RuntimeError(f"MODEL_SAMPLE_TOO_SMALL {len(train)} {len(calibrate)}")
    if len(set(yt))<2 or len(set(yc))<2:
        raise RuntimeError("ONE_CLASS_LABEL_NOT_TRAINABLE")
    model=HistGradientBoostingClassifier(
        max_iter=125,max_leaf_nodes=9,min_samples_leaf=90,
        learning_rate=.035,l2_regularization=12,random_state=47)
    model.fit(f.iloc[train],yt)
    raw=model.predict_proba(f.iloc[calibrate])[:,1]
    # Separate independent chronological Platt calibration cohort.
    z=np.log(np.maximum(raw,1e-6)/(1-np.minimum(raw,.999999))).reshape(-1,1)
    platt=LogisticRegression(C=2,max_iter=2000,random_state=47)
    platt.fit(z,yc)
    calib=platt.predict_proba(z)[:,1]
    return model,platt,{"trainCount":len(train),"calibCount":len(calibrate),
       "trainPositivePct":round(100*float(yt.mean()),3),
       "calibPositivePct":round(100*float(yc.mean()),3),
       "calibBrier":round(float(np.mean((calib-yc)**2)),5),
       "calibModel":"PlattLogit_SeparateChronologicalCohort"}

def proba(model,platt,x):
    raw=np.clip(model.predict_proba(x)[:,1],1e-6,1-1e-6)
    z=np.log(raw/(1-raw)).reshape(-1,1)
    return platt.predict_proba(z)[:,1]

def replay(df,features,diary,year,prob,cutoff,mode):
    # Fully chronological state-machine, no future price used to decide.
    yr=np.flatnonzero(df.ts.dt.year.to_numpy()==year)
    start,end=int(yr[0]),int(yr[-1])+1
    last_risk=None
    state="IDLE";ep=None
    episodes=[];pending=None
    last_day=None
    p=df.p.to_numpy()
    t=df.ts
    lows=df.p.rolling(96,min_periods=72).min().shift(1).to_numpy()
    for k in range(start,end):
        date=df.day.iloc[k]
        ts=t.iloc[k]
        if pending is not None:
            mins=int((ts-pending["signalTS"]).total_seconds()/60)
            pending["proxyFillPrice"]=round(float(p[k]),3)
            pending["fillGapMinutes"]=mins
            pending["valid15mFill"]=mins==15
            pending["fillTS"]=str(ts)
            del pending["signalTS"]
            pending=None
        if last_day is not None and date!=last_day and diary.get(last_day,False):
            last_risk=last_day
            if state=="IDLE":
                ep={"start":str(last_day),"startBar":str(ts),"firstIndex":k,
                    "riskUpdates":1,"lastRisk":str(last_day),"signal":None,"max":float(p[k])}
                episodes.append(ep)
                state="WATCH"
            else:
                ep["riskUpdates"]+=1
                ep["lastRisk"]=str(last_day)
        last_day=date
        if state!="IDLE" and last_risk is not None and (date-last_risk).days>RISK_EXPIRY_DAYS:
            ep["end"]=str(ts)
            ep["lastIndex"]=k
            state="IDLE";ep=None
        if state=="IDLE":continue
        ep["max"]=max(ep["max"],float(p[k]))
        if state=="EXIT_RECORDED":continue
        # Only valid previous 16 bars exactly 4h apart.
        r4=features["ret4h"].iloc[k]
        full4=(ts-t.iloc[k-16]==pd.Timedelta(hours=4)) if k>=16 else False
        structure=full4 and (p[k]<lows[k]) and (p[k]<=ep["max"]*.99) and (r4<=-.01)
        probOK=prob[k]>=cutoff
        if mode=="ML_PROB_TREND":
            trigger=full4 and probOK and r4<=-.0025 and p[k]<=ep["max"]*.995
        elif mode=="ML_PLUS_STRUCT":
            trigger=structure and probOK
        elif mode=="STRUCT_ONLY":trigger=structure
        else:raise ValueError(mode)
        if trigger:
            sig={"ts":str(ts),"pAtSignal":round(float(p[k]),3),
                 "modelProbability":round(float(prob[k]),5),
                 "threshold":round(float(cutoff),5),
                 "drawdownFromWatchHighPct":round(100*(p[k]/ep["max"]-1),3),
                 "r4Pct":round(100*float(np.expm1(r4)),3),
                 "prev96Low":round(float(lows[k]),3),
                 "signalIndex":k,"signalTS":ts,
                 "proxyFillPrice":None,"valid15mFill":False}
            ep["signal"]=sig
            pending=sig
            state="EXIT_RECORDED"
    if ep is not None:
        ep["end"]=str(t.iloc[end-1])
        ep["lastIndex"]=end-1
    by_idx={}
    for e in episodes:
        sig=e["signal"]
        if not sig or not sig["valid15mFill"]:continue
        b=int(sig["signalIndex"])
        if b+1>=len(df):continue
        first_session=int(df.session.iloc[b+1])
        if first_session+FUTURE_SESSIONS>int(df.session.iloc[-1]):
            sig["next5Mature"]=False;continue
        hi=int(np.searchsorted(df.session.to_numpy(),first_session+FUTURE_SESSIONS,side="right"))
        future=p[b+2:hi]
        if not len(future):continue
        fp=sig["proxyFillPrice"]
        sig["next5Mature"]=True
        sig["future5Down4"]=bool(np.min(future)/fp<=.96)
        # Priority target: did a substantial sell-worthy fall arrive BEFORE
        # a subsequent +2% rally? A 4% fall after a 2% rally is NOT a timely exit.
        downside=np.flatnonzero(future/fp<=.96)
        upside=np.flatnonzero(future/fp>=1.02)
        sig["future5Down4BeforeUp2"]=bool(
            len(downside)>0 and (len(upside)==0 or downside[0]<upside[0]))
        sig["future5Up2BeforeDown4"]=bool(
            len(upside)>0 and (len(downside)==0 or upside[0]<downside[0]))
        sig["future5LowestPct"]=round(100*(np.min(future)/fp-1),3)
        sig["future5MaxRisePct"]=round(100*(np.max(future)/fp-1),3)
        # Looking forward here only audits missed upside, never inference.
        e_start=b+1;e_end=e.get("lastIndex",end-1)
        after=p[e_start:e_end+1]
        sig["missedRallyInRiskWindowPct"]=round(100*max(np.max(after)/fp-1,0),3) if len(after) else None
    signaled=[x for x in episodes if x["signal"] is not None]
    evals=[x["signal"] for x in signaled if x["signal"].get("next5Mature")]
    wins=[x for x in evals if x["future5Down4"]]
    firstwins=[x for x in evals if x["future5Down4BeforeUp2"]]
    upfirst=[x for x in evals if x["future5Up2BeforeDown4"]]
    return {"episodes":len(episodes),"signals":len(signaled),
       "valid5SessionSignals":len(evals),"hits4pct":len(wins),
       "noHit4pct":len(evals)-len(wins),
       "down4BeforeUp2":len(firstwins),
       "up2BeforeDown4":len(upfirst),
       "missedEventsByNoSignal":len(episodes)-len(signaled),
       "meanPostExitUpsidePct":round(float(np.mean([x["missedRallyInRiskWindowPct"]
           for x in evals if x.get("missedRallyInRiskWindowPct") is not None])),3) if evals else None,
       "events":[{"watch":x["start"],"riskLast":x["lastRisk"],
         "riskUpdates":x["riskUpdates"],"signal":{k:v for k,v in x["signal"].items()
         if k not in ("signalIndex","signalTS")} if x["signal"] else None}
         for x in episodes]}

def run():
    df=fetch_bars()
    f=feature_frame(df)
    diaries,origin=v44.read_diaries()
    # First independent model: <= 2022-12-16 train, 2023 Jan-Dec17 calibrate.
    model,cal,train=fit_model(df,f,"2022-12-16","2023-01-01","2023-12-17")
    years=df.ts.dt.year.to_numpy()
    p_frozen=np.zeros(len(df),dtype="float64")
    for y in (2024,2025,2026):
        mask=(years==y)
        p_frozen[mask]=proba(model,cal,f.loc[mask])
    # Frozen cutoff ONLY from 2024 score frequency: no 2025 or 2026 labels.
    cuts={str(q):float(np.quantile(p_frozen[years==2024],q))
          for q in THRESHOLD_QUANTILES}
    out={}
    for year in (2025,2026):
        out[str(year)]={"frozen2020_22_calib2023":{}}
        for q,t in cuts.items():
            out[str(year)]["frozen2020_22_calib2023"][q]={
              mode:replay(df,f,diaries[year],year,p_frozen,t,mode)
              for mode in ("STRUCT_ONLY","ML_PROB_TREND","ML_PLUS_STRUCT")
            }
    # 2025 annual model: 2020-2023 train (labels embargoed by Dec16),
    # recalibrate strictly on 2024, apply to 2025. No 2025 outcomes read.
    model25,cal25,train25=fit_model(df,f,"2023-12-16","2024-01-01","2024-12-17")
    new25=np.zeros(len(df),dtype="float64")
    new25[years==2025]=proba(model25,cal25,f.loc[years==2025])
    out["2025"]["refit_through2023_calib2024"]={}
    for q,t in cuts.items():
        out["2025"]["refit_through2023_calib2024"][q]={
          mode:replay(df,f,diaries[2025],2025,new25,t,mode)
          for mode in ("ML_PROB_TREND","ML_PLUS_STRUCT")
        }
    # Annual update at start of 2026, using information no later than 2025-12-17:
    model26,cal26,train26=fit_model(df,f,"2024-12-16","2025-01-01","2025-12-17")
    new26=np.zeros(len(df),dtype="float64")
    new26[years==2026]=proba(model26,cal26,f.loc[years==2026])
    out["2026"]["refit_through2024_calib2025"]={}
    for q,t in cuts.items():
        out["2026"]["refit_through2024_calib2025"][q]={
          mode:replay(df,f,diaries[2026],2026,new26,t,mode)
          for mode in ("ML_PROB_TREND","ML_PLUS_STRUCT")
        }
    # POST-HOC ROBUSTNESS AUDIT ONLY: evaluate ±20% of previously fixed 2024
    # 95th percentile cutoff, DO NOT optimize on 2025 or 2026 results.
    margin={}
    for label,year,probs in (
         ("2025_frozen",2025,p_frozen),
         ("2025_prior_years_refit",2025,new25),
         ("2026_prior_years_refit",2026,new26)):
        margin[label]={}
        for scale in (.8,.9,.95,1.,1.05,1.1,1.2):
            cutoff=cuts["0.95"]*scale
            x=replay(df,f,diaries[year],year,probs,cutoff,"ML_PLUS_STRUCT")
            margin[label][str(scale)]={k:v for k,v in x.items() if k!="events"}
    # These sweeps show instability; cannot pick the best from a held-out year.
    summary={y:{cohort:{q:{mode:{k:v for k,v in result.items() if k!="events"}
                        for mode,result in d.items()} for q,d in vals.items()}
                 for cohort,vals in result.items()} for y,result in out.items()}
    return {"schema":"GOLD_V47_PRIOR_YEARS_FIT_PROBABILISTIC_PRICE_REGIME_EXIT_ONLY",
        "status":"HISTORICAL_RESEARCH_NOT_PIT_NOT_BLIND",
        "features":list(FEATURES),
        "learningTarget":"within_current_remainder_plus_next_5_NY17_trading_sessions_hit_down4_before_up2",
        "training":{"frozen":train,"2025PriorYearsRecalibrated":train25,
                      "2026PriorYearsRecalibrated":train26},
        "cutoffs":{"selection":"2024_unlabeled_prediction_quantiles_only",
                   "2024Levels":cuts},
        "posthocThresholdMarginRobustnessNotForModelSelection":margin,
        "note":"Not all target labels are actual risk episodes; whole-market down-vs-up barriers",
        "primaryPreferredOutcome":"future5Down4BeforeUp2, rather than retrospective min fall after interim rally",
        "source":"Neon HistData 15m historical, not executable broker quotes",
        "diaryVersion":{"2025":origin[2025],"2026":origin[2026]},
        "evaluationYearResults":out,"summary":summary,
        "train2020_22_calibrate2023_validate2024_test2025":True,
        "2026UpdatedPriorDataOnly":True,
        "noBuyOrReentry":True,"noProfitSimulation":True,
        "productionChanged":False,"firstprintCertified":False,
        "researchAlreadySaw2025_26Events":True,
        "limitations":[
          "Original V22 2025 and later V33 2026 are different versions.",
          "Historical V22 not prospective firstprint; price bar may not be available at stated timestamp.",
          "2025/26 not true blind because earlier researchers saw events.",
          "Actual V22 episodes sparse; model trained on all-market surrogate labels.",
          "Cuts come from 2024 price score quantile, not isolated V22 event optimization.",
          "Risk window eight calendar days extended on new V22 signs; one exit per risk window.",
          "5-session percent drop AFTER exit is not recall of all physical large declines.",
          "No bank bid/ask, execution delay, data vendor cross-check or four-metal inputs.",
          "Any calibration using labels not matured before time would be leakage: 12d year embargo."
        ]}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="gold-v47-calibrated-exit-research-2025-2026.json")
    args=a.parse_args()
    result=run()
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str)+"\n",encoding="utf8")
    print("V47_AUDIT_SUMMARY",json.dumps({k:v for k,v in result.items()
         if k!="evaluationYearResults"},ensure_ascii=False,default=str),flush=True)
    print("V47_EVENT_DETAIL",json.dumps(result["evaluationYearResults"],ensure_ascii=False,default=str),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as h:
            h.write("## V47: 2020-23 learning -> 2024 score cutoff -> 2025/26 exit-only audit\n\n")
            h.write("No buy, no live deployment, V22 firstprint unverified.\n\n")
            h.write("| Year | Model | Score quantile | Signal type | Exits | Matched next5 ≥4% | Unmatched | Avg missed upside % |\n|---|---|---|---|---:|---:|---:|---:|\n")
            for yr,cohorts in result["summary"].items():
                for cohort,quantiles in cohorts.items():
                    for q,methods in quantiles.items():
                        for mode,r in methods.items():
                            h.write(f"| {yr} | {cohort} | {q} | {mode} | {r['signals']} | {r['hits4pct']} | {r['noHit4pct']} | {r['meanPostExitUpsidePct']} |\n")
if __name__=="__main__":main()
