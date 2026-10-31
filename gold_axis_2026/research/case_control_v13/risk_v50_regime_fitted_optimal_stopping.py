#!/usr/bin/env python3
"""V50 — learned market regimes + fitted finite-horizon optimal stopping, SELL ONLY.

Research, never production. V22 is an EARLY_RISK gate, not an immediate exit.

At month start:
  1. Fit a 3-component, *current/past-only* latent regime mixture (K-means)
     on trailing 730 calendar days of 15m trend/volatility features.
  2. Use a rolling 730-day historical cohort with a 5-trading-session
     MATURITY CHECK (not a naïve calendar-day embargo) to train a backwards
     five-session Fitted-Q stopping policy. Features include 3 regime
     proximity weights and causal momentum/volatility state.
  3. Q_H(s) is predicted risk-adjusted incremental value of waiting through
     the next trading session and keeping the option to sell later.
     Sell payoff is 0, continuation target for backward induction:
       log(P_next/P_now) - lambda * worst_intraperiod_drawdown
         + max(0, Q_{h-1}(s_next))
     Train h=1..5. STOP if Q_5(s)<=0, otherwise WAIT.
     Separate 0.35 and 0.8 adverse-move cost variants are PREDECLARED,
     not picked using 2025/26 results.
  4. Only act when V22 has started an active WATCH. Signalled exits are
     *research only*; no buy/reentry/real broker fills or portfolio P&L.

CAVEATS: Fits on all-market states, NOT on a unified firstprint V22 risk
population. Original V22 vintage 2025 != later V33 vintage 2026. Both years
previously examined, so 2025/26 evaluation is retrospective, NOT blind OOS.
"""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from datetime import timedelta
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor
import gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation as v47
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as v44

REGIME_FIELDS=("ret4h","ret24h","ret3d","dd24","dd5d","ema480","vol96","volratio","down96")
POLICY_FIELDS=("ret1h","ret4h","ret12h","ret24h","ret3d","dd24","dd5d",
               "rangepos24","rangepos5d","ema96","ema480","vol16",
               "vol96","volratio","down16","down96","gap4")
RISKS=(.35,.8)
TRAIN_DAYS=730
HORIZON_SESSIONS=5
SAMPLE_STEP=12  # one labeled point every 3 observed hours, not every 15m
V22_EXPIRY_DAYS=8
PERSISTENCES=(1,4)
FUTURE_SESSIONS=5

def next_session_checkpoint(df):
    """A causal *schedule* for future training labels, not a signal feature.
    Check the same within-session offset on the NEXT known NY17 session.
    Each source is a bar start time; target only used once it has matured.
    """
    sess=df.session.to_numpy(dtype=int)
    n=len(sess)
    starts=np.flatnonzero(np.r_[True,sess[1:] != sess[:-1]])
    ends=np.r_[starts[1:],n]
    nxt=np.full(n,-1,dtype=int)
    for sid in range(len(starts)-1):
        b,e=starts[sid],ends[sid]
        next_b,next_e=starts[sid+1],ends[sid+1]
        offset=np.arange(e-b,dtype=int)
        nxt[b:e]=np.minimum(next_b+offset,next_e-1)
    return nxt

def five_step_maturity(nextidx):
    result=np.arange(len(nextidx),dtype=int)
    for _ in range(HORIZON_SESSIONS):
        updated=np.full(len(nextidx),-1,dtype=int)
        eligible=result>=0
        updated[eligible]=nextidx[result[eligible]]
        result=updated
    return result

def regime_probabilities(train_features, predict_features):
    """Soft assignment to unsupervised 3-state training clusters.
    Fits StandardScaler and KMeans on training rows only. The current bar
    uses no future state smoothing or Viterbi look-ahead.
    """
    scaler=StandardScaler().fit(train_features)
    fitted=scaler.transform(train_features)
    km=KMeans(n_clusters=3,n_init=5,random_state=50)
    km.fit(fitted)
    dist=km.transform(scaler.transform(predict_features))
    # Stable softmax of negative relative squared distance.
    dist=dist*dist
    temp=np.median(np.min(dist,axis=1)) + 1e-6
    z=np.clip(-(dist - dist.min(axis=1,keepdims=True)) / max(temp,1e-5),-40,0)
    weights=np.exp(z)
    weights/=weights.sum(axis=1,keepdims=True)
    return weights,{"centers":km.cluster_centers_.round(4).tolist(),
                    "trainingSize":int(len(train_features)),
                    "softTemperature":round(float(temp),4)}

def training_selection(df, nextidx, five, month_start):
    """All supervised future targets MUST mature BEFORE first bar of month."""
    ts=df.ts.dt.tz_localize(None).to_numpy()
    start=np.datetime64(month_start.to_pydatetime())
    earliest=start-np.timedelta64(TRAIN_DAYS,"D")
    samples=np.arange(600,len(df),SAMPLE_STEP)
    samples=samples[(ts[samples]>=earliest) & (ts[samples]<start) & (five[samples]>=0)]
    samples=samples[ts[five[samples]]<start]
    # Ensure 5-session next-price outcomes have truly matured before training.
    assert np.all(ts[five[samples]]<start)
    return samples

def transition_targets(price, nextidx, samples):
    """One next-session return and worst adverse move before next checkpoint.
    Used ONLY to fit past examples. Current online stream never calls this.
    """
    j=nextidx[samples]
    if (j<=samples).any():raise ValueError("BAD_NEXT_SESSION_TRANSITION")
    delta=np.log(price[j]/price[samples])
    adverse=np.array([max(0.0, 1.0-float(np.min(price[i+1:k+1]))/price[i])
                      for i,k in zip(samples,j)],dtype="float64")
    return delta,adverse,j

def fit_fitted_stopping(df,raw_features,train_ix,pred_ix,regime,lam):
    """Finite horizon fitted continuation values, non-clairvoyant inference.
    All regressors fit on matured past only. Q_h is trained via backward
    induction on historical transitions (fitted regression estimate).
    """
    weights,desc=regime
    # Predict regime weights for union of training, training next-index states
    # and current month. Caller provides a dense causal feature array for the
    # window [min train index .. end current month].
    X=np.column_stack([raw_features.to_numpy(dtype="float32"),
                      weights]).astype("float32")
    prices=df.p.to_numpy(dtype="float64")
    nextidx=next_session_checkpoint(df)
    gain,adverse,next_positions=transition_targets(prices,nextidx,train_ix)
    a=X[train_ix]
    next_a=X[next_positions]
    last_model=None
    stage=[]
    for h in range(1,HORIZON_SESSIONS+1):
        continuation=np.zeros(len(train_ix),dtype="float64")
        if last_model is not None:
            continuation=np.clip(last_model.predict(next_a),0,.5)
        targets=np.clip(gain - lam*adverse + continuation,-.5,.5)
        reg=HistGradientBoostingRegressor(
          max_iter=65,max_leaf_nodes=7,min_samples_leaf=75,
          learning_rate=.06,l2_regularization=12,random_state=50+h)
        reg.fit(a,targets)
        stage.append({"h":h,"labelMean":round(float(targets.mean()),6),
                      "fittedQMean":round(float(reg.predict(a).mean()),6)})
        last_model=reg
    q=last_model.predict(X[pred_ix])
    return q,stage,desc

def prepare_month(df,features,nxt,five,month,weights_lambda=RISKS):
    """One month independent model; every stage uses only historical labels.
    K-means trained on same matured cohort; applies to data up to month end.
    """
    ts=df.ts.dt.tz_localize(None).to_numpy()
    begin=np.datetime64(month.to_pydatetime())
    end=np.datetime64((month+pd.offsets.MonthBegin(1)).to_pydatetime())
    current=np.flatnonzero((ts>=begin)&(ts<end))
    if not len(current):return None
    train=training_selection(df,nxt,five,month)
    if len(train)<1900:raise RuntimeError(f"V50_INSUFFICIENT_TRAINING {month} {len(train)}")
    regweights,regdesc=regime_probabilities(
      features.iloc[train][list(REGIME_FIELDS)].to_numpy(dtype="float64"),
      features[list(REGIME_FIELDS)].to_numpy(dtype="float64"))
    models={}
    for lam in weights_lambda:
        q,stages,_=fit_fitted_stopping(
            df,features[list(POLICY_FIELDS)],train,current,
            (regweights,regdesc),lam)
        models[str(lam)]={
            "values":q,
            "stageTraining":stages,
            "qNegativeSharePct":round(float(100*(q<=0).mean()),3),
            "qMean":round(float(q.mean()),6)}
    month_info={
       "month":str(month.date()),"trainingSamples":len(train),
       "firstSample":str(df.ts.iloc[train[0]]),
       "lastSample":str(df.ts.iloc[train[-1]]),
       "lastFiveSessionOutcomeMaturedUTC":str(df.ts.iloc[five[train[-1]]]),
       "regimeFit":regdesc,
       "fits":{key:{k:v for k,v in value.items() if k!="values"}
               for key,value in models.items()}
    }
    return current,models,month_info

def replay(df,diary,year,qvalues,persistence):
    """Strict one-bar-at-a-time WATCH. No market prices from future used
    to decide. qvalues are monthly fitted before each month's first bar.
    """
    ys=np.flatnonzero(df.ts.dt.year.to_numpy()==year)
    start,end=int(ys[0]),int(ys[-1])+1
    px=df.p.to_numpy()
    ts=df.ts
    timestamps_ns=df.ts.astype("int64").to_numpy()
    prior_day=None;last_warn=None;state="IDLE"
    episode=None;episodes=[];pending=None;streak=0
    for j in range(start,end):
        bar_ts=ts.iloc[j]
        day=df.day.iloc[j]
        if pending is not None:
            gap=int((bar_ts-pending["internalTimestamp"]).total_seconds()/60)
            pending["fill15m"]=gap==15
            pending["fillUTC"]=str(bar_ts)
            pending["fillPrice"]=round(float(px[j]),3)
            pending["gapMinutes"]=gap
            pending.pop("internalTimestamp")
            pending=None
        if prior_day is not None and prior_day!=day and diary.get(prior_day,False):
            last_warn=prior_day
            if state=="IDLE":
                episode={"firstV22":str(prior_day),"lastV22":str(prior_day),
                         "warnings":1,"startUTC":str(bar_ts),"signal":None}
                episodes.append(episode)
                state="WATCH";streak=0
            else:
                episode["warnings"]+=1
                episode["lastV22"]=str(prior_day)
        prior_day=day
        if state!="IDLE" and last_warn is not None and (day-last_warn).days>V22_EXPIRY_DAYS:
            episode["endUTC"]=str(bar_ts)
            state="IDLE";episode=None;streak=0
        if state!="WATCH":continue
        value=qvalues[j]
        if np.isfinite(value) and value<=0:
            streak+=1
        else:
            streak=0
        if streak>=persistence:
            signal={"timeUTC":str(bar_ts),"price":round(float(px[j]),3),
                    "qContinuation":round(float(value),6),
                    "decision":"EXIT_SIGNAL","internalTimestamp":bar_ts,
                    "fillUTC":None,"fillPrice":None,"fill15m":False}
            episode["signal"]=signal
            pending=signal
            state="EXIT_RECORDED"
    if episode is not None:
        episode["endUTC"]=str(ts.iloc[end-1])
    session=df.session.to_numpy(dtype=int)
    for e in episodes:
        s=e["signal"]
        if not s or not s["fill15m"]:continue
        idx=int(np.searchsorted(timestamps_ns,pd.Timestamp(s["fillUTC"]).value))
        if idx>=len(px):continue
        ss=session[idx]
        if ss+FUTURE_SESSIONS>int(session[-1]):continue
        end_idx=int(np.searchsorted(session,ss+FUTURE_SESSIONS,side="right"))
        future=px[idx+1:end_idx]
        if not len(future):continue
        down=np.flatnonzero(future<=s["fillPrice"]*.96)
        up=np.flatnonzero(future>=s["fillPrice"]*1.02)
        s["mature5"]=True
        s["hitDrop4"]=bool(len(down))
        s["downFirst"]=bool(len(down) and (not len(up) or down[0]<up[0]))
        s["rallyFirst"]=bool(len(up) and (not len(down) or up[0]<down[0]))
        s["fiveWorstPct"]=round(100*(float(future.min())/s["fillPrice"]-1),3)
        s["fiveBestPct"]=round(100*(float(future.max())/s["fillPrice"]-1),3)
        # Retrospective opportunity cost, NOT used in the signal decision.
        t0=int(np.searchsorted(timestamps_ns,pd.Timestamp(s["fillUTC"]).value))
        risk_stop=idx
        if "endUTC" in e:
            risk_stop=int(np.searchsorted(timestamps_ns,pd.Timestamp(e["endUTC"]).value))
        if risk_stop>t0:
            s["rallyMissedWithinRiskPct"]=round(100*max(0,float(px[t0:risk_stop+1].max())/s["fillPrice"]-1),3)
        # Additional +20 calendar day missed rally (regardless of risk expiry)
        stop_ts=pd.Timestamp(s["fillUTC"])+pd.Timedelta(days=20)
        bound=int(np.searchsorted(timestamps_ns,stop_ts.value,side="right"))
        s["rallyMissed20CalendarDaysPct"]=round(
            100*max(0,float(px[t0:bound].max())/s["fillPrice"]-1),3)
    signals=[e for e in episodes if e["signal"]]
    mature=[e["signal"] for e in signals if e["signal"].get("mature5") is True]
    return {
      "riskWindows":len(episodes),
      "signals":len(signals),
      "validSignals":len(mature),
      "drop4":sum(s["hitDrop4"] for s in mature),
      "downBeforeUp":sum(s["downFirst"] for s in mature),
      "rallyBeforeDown":sum(s["rallyFirst"] for s in mature),
      "noDrop":sum(not s["hitDrop4"] for s in mature),
      "noSignalWindows":len(episodes)-len(signals),
      "meanMissed20DayUpside":round(float(np.mean([s["rallyMissed20CalendarDaysPct"] for s in mature])),3) if mature else None,
      "events":episodes
    }

def run():
    df=v47.fetch_bars()
    f=v47.feature_frame(df)
    nxt=next_session_checkpoint(df)
    five=five_step_maturity(nxt)
    diaries,vintage=v44.read_diaries()
    q={str(r):np.full(len(df),np.nan) for r in RISKS}
    monthly=[]
    for month in pd.date_range("2025-01-01","2026-09-01",freq="MS"):
        result=prepare_month(df,f,nxt,five,month)
        if result is None:continue
        pos,models,desc=result
        for risk,values in models.items():q[risk][pos]=values["values"]
        monthly.append(desc)
    results={}
    for year in (2025,2026):
        results[str(year)]={}
        for risk in RISKS:
            results[str(year)][str(risk)]={
               str(n):replay(df,diaries[year],year,q[str(risk)],n)
               for n in PERSISTENCES
            }
    aggregate={year:{risk:{per:{k:v for k,v in result.items() if k!="events"}
                 for per,result in strats.items()}
                 for risk,strats in yr.items()} for year,yr in results.items()}
    return {
      "schema":"GOLD_V50_KMEANS_REGIME_FITTED_Q_FINITE_HORIZON_STOPPING_RESEARCH_V1",
      "scope":"V22 early risk -> WATCH -> learned WAIT vs EXIT only; no trading",
      "model":"3 latent KMeans regimes; monthly 730d fitted-Q dynamic programming 5 next NY17 trading sessions",
      "trainingMaturity":"five actual market-session checkpoints before each month start",
      "decision":"at each 15m bar, q_continue <= 0 for N continuous bars => EXIT",
      "riskCoefficients":RISKS,
      "persistenceSettings":PERSISTENCES,
      "allMarketTrainingNotV22Specific":True,
      "observationSource":"Neon public.gold_research_histdata_xau15m_candidate noncanonical",
      "v22Provenance":{"2025":vintage[2025],"2026":vintage[2026]},
      "researchNotLive":True,"noBuy":True,"noReentry":True,
      "notBlindYearsPreviouslyObserved":True,
      "yearResults":results,
      "summary":aggregate,
      "monthlyFitJournal":monthly,
      "caveats":[
        "Fitted-Q is approximate regression-based risk-adjusted stopping, not globally optimal execution.",
        "No verified firstprint timestamp or bank bid/ask, broker spread or slippage.",
        "2025 original V22 and 2026 V33 have different model vintages.",
        "2025/26 history previously explored: not independent blind validation.",
        "All-market fitted-Q samples not conditional on V22 since no genuine 2020-23 V22 risk history.",
        "Risk aversion coefficients and eight-day risk expiry were predeclared not learned.",
        "A correct five-session dip after a signal does not imply the signal beat a prior 2% rally.",
        "Risk gated to V22 cannot catch physical major declines with no prior V22 alert.",
      ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="gold-v50-regime-fitted-stopping-2025-2026.json")
    args=ap.parse_args()
    result=run()
    Path(args.out).write_text(json.dumps(result,indent=2,ensure_ascii=False,default=str)+"\n",encoding="utf8")
    print("V50_MONTHLY_JOURNAL",json.dumps([{
        k:v for k,v in item.items() if k!="regimeFit"
      } for item in result["monthlyFitJournal"]],ensure_ascii=False),flush=True)
    print("V50_SUMMARY",json.dumps(result["summary"],ensure_ascii=False),flush=True)
    print("V50_EPISODES",json.dumps({
      yr:{risk:{persist:[{
       "warning":e["firstV22"],
       "exit":e["signal"]["timeUTC"] if e["signal"] else None,
       "price":e["signal"]["fillPrice"] if e["signal"] else None,
       "value":e["signal"]["qContinuation"] if e["signal"] else None,
       "drop4":e["signal"].get("hitDrop4") if e["signal"] else None,
       "downBeforeUp":e["signal"].get("downFirst") if e["signal"] else None,
       "rally20d":e["signal"].get("rallyMissed20CalendarDaysPct") if e["signal"] else None
      } for e in result["yearResults"][yr][risk][persist]["events"]]
      for persist in strats} for risk,strats in groups.items()}
      for yr,groups in result["yearResults"].items()
    },ensure_ascii=False),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as h:
            h.write("## Gold V50 regime + fitted stopping | genuine prior-year learning\n\n")
            h.write("Research only; same-model original firstprint unavailable. NO trades or BUY.\n\n")
            h.write("| Year | Downside penalty | Persistence bars | V22 risk windows | EXIT | Dip >=4% | Dip before +2% | False | 20d missed rally % |\n")
            h.write("|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
            for year,groups in result["summary"].items():
                for r,settings in groups.items():
                    for k,v in settings.items():
                        h.write(f"| {year} | {r} | {k} | {v['riskWindows']} | {v['signals']} | {v['drop4']} | {v['downBeforeUp']} | {v['noDrop']} | {v['meanMissed20DayUpside']} |\n")
if __name__=="__main__":main()
