#!/usr/bin/env python3
"""V51 — learn the ACTUAL regret of premature EXIT and the price risk of WAIT.

Risk-gated, no BUY / reentry / cash PnL. Improves the V50 research question:
* EXIT now costs the upside to be missed in the following 20 calendar days;
* WAIT exposes holder to worst price loss in the next five NY17 sessions.
Estimate both from PREVIOUS 730 days with matured labels, condition on
CURRENT causal trend / volatility regime (3 learned K-means states).

Policy is a learned-cost comparison / approximate stopping decision, not
the exact Bellman optimum. Two predeclared risk-weight parameters and a
regime guard are compared, never selected using 2024/25/26 outcomes.

Historical V22 originally recorded 2024/25 vs later replay 2026 are different
vintages, firstprint not certified. All results retrospective nonblind.
"""
from __future__ import annotations
import json,argparse,os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
import gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation as v47
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as v44
import gold_axis_2026.research.case_control_v13.risk_v50_regime_fitted_optimal_stopping as v50

RISK_WEIGHTS=(1.0,1.5)
MODES=("LEARNED_REGRET","LEARNED_REGRET_REGIME_GUARD")
TREND_CONFIRM=(1,4)
HISTORY_DAYS=730
UPSIDE_HORIZON_CALENDAR_DAYS=20
DOWNSIDE_HORIZON_SESSIONS=5
STEP=12

def mature_training_rows(df,month):
    ts=df.ts.dt.tz_localize(None).to_numpy()
    sess=df.session.to_numpy(dtype=int)
    start=np.datetime64(month.to_pydatetime())
    earliest=start-np.timedelta64(HISTORY_DAYS,"D")
    bars=np.arange(600,len(df),STEP,dtype=int)
    bars=bars[(ts[bars]>=earliest)&(ts[bars]+np.timedelta64(UPSIDE_HORIZON_CALENDAR_DAYS,"D")<start)]
    # First 20 calendar days must be present before this month.
    # All 5 future NY17 trading sessions must also have fully concluded.
    five=np.searchsorted(sess,sess[bars]+DOWNSIDE_HORIZON_SESSIONS,side="right")
    valid=(five>bars+1)&(five<len(df))&(ts[five-1]<start)
    bars=bars[valid]
    if len(bars)<1800:raise RuntimeError(f"V51_TRAIN_MATURE_TOO_SMALL {month} {len(bars)}")
    return bars

def realized_regret_labels(df,indices):
    """Future only for training. For every sample compute maximum price
    the holder could have captured during 20 days (selling now regret),
    and maximum 5-session drawdown while holding (waiting risk).
    Both are ex-post ORACLES to train expectation, never input at decision.
    """
    price=df.p.to_numpy(dtype="float64")
    ts=df.ts.astype("int64").to_numpy()
    sess=df.session.to_numpy(dtype=int)
    ups=np.zeros(len(indices))
    downs=np.zeros(len(indices))
    for k,i in enumerate(indices):
        stop=int(np.searchsorted(ts,ts[i]+20*24*3600*10**9,side="right"))
        hi=int(np.searchsorted(sess,sess[i]+DOWNSIDE_HORIZON_SESSIONS,side="right"))
        if stop<=i+1 or hi<=i+1:raise ValueError("LABEL_NOT_MATURED")
        ups[k]=max(0,float(np.max(price[i+1:stop])/price[i]-1))
        downs[k]=max(0,float(1-np.min(price[i+1:hi])/price[i]))
    return np.clip(ups,0,.30),np.clip(downs,0,.30)

def fit_month(df,features,month):
    ts=df.ts.dt.tz_localize(None).to_numpy()
    a=np.datetime64(month.to_pydatetime())
    b=np.datetime64((month+pd.offsets.MonthBegin(1)).to_pydatetime())
    current=np.flatnonzero((ts>=a)&(ts<b))
    if not len(current):return None
    train=mature_training_rows(df,month)
    labels_up,labels_down=realized_regret_labels(df,train)
    regimes,desc=v50.regime_probabilities(
       features.iloc[train][list(v50.REGIME_FIELDS)].to_numpy(dtype=float),
       features[list(v50.REGIME_FIELDS)].to_numpy(dtype=float))
    X=np.column_stack([features[list(v50.POLICY_FIELDS)].to_numpy(dtype="float32"),
                      regimes]).astype("float32")
    models={}
    for target,name,qt in [(labels_up,"rally",.65),(labels_down,"down",.75)]:
        reg=HistGradientBoostingRegressor(
            loss="quantile",quantile=qt,max_iter=95,max_leaf_nodes=9,
            min_samples_leaf=85,learning_rate=.05,
            l2_regularization=12,random_state=51)
        reg.fit(X[train],target)
        models[name]=reg
    expected_rally=np.clip(models["rally"].predict(X[current]),0,.3)
    expected_drop=np.clip(models["down"].predict(X[current]),0,.3)
    # An unsupervised bullish regime is the cluster with highest trailing
    # 24h log price return in the training cohort (NOT future price).
    center_signals=[float(np.mean(features.ret24h.iloc[train].to_numpy() *
                         regimes[train,k])) for k in range(3)]
    bullish=int(np.argmax(center_signals))
    bull_weight=regimes[current,bullish]
    bull_cut=float(np.quantile(regimes[train,bullish],.25))
    policies={}
    for risk in RISK_WEIGHTS:
        value=expected_rally-risk*expected_drop
        policies[(str(risk),"LEARNED_REGRET")]=value
        policies[(str(risk),"LEARNED_REGRET_REGIME_GUARD")]=np.where(
            bull_weight>bull_cut,np.maximum(value,.00001),value)
    meta={"month":str(month.date()),"trainN":len(train),
          "lastOriginUTC":str(df.ts.iloc[train[-1]]),
          "upsideLabelMeanPct":round(100*float(labels_up.mean()),3),
          "downsideLabelMeanPct":round(100*float(labels_down.mean()),3),
          "last20DayOutcomeMaturedUTC":str(df.ts.iloc[train[-1]]+pd.Timedelta(days=20)),
          "bullClusterId":bullish,"bullGuardQ25":round(bull_cut,5),
          "rallyPredAvgPct":round(100*float(expected_rally.mean()),3),
          "downPredAvgPct":round(100*float(expected_drop.mean()),3),
          "policies":{k[0]+"_"+k[1]:{
                "percentWouldExit":round(100*float((v<=0).mean()),3),
                "meanExpectedNetPct":round(100*float(v.mean()),3)
          } for k,v in policies.items()}}
    return current,policies,meta

def run():
    df=v47.fetch_bars()
    f=v47.feature_frame(df)
    diaries,vintage=v44.read_diaries()
    allq={(str(risk),mode):np.full(len(df),np.nan)
          for risk in RISK_WEIGHTS for mode in MODES}
    journal=[]
    for month in pd.date_range("2024-01-01","2026-09-01",freq="MS"):
        current,q,meta=fit_month(df,f,month)
        for name,vals in q.items():allq[name][current]=vals
        journal.append(meta)
    results={}
    for year in (2024,2025,2026):
        results[str(year)]={}
        for risk in RISK_WEIGHTS:
            results[str(year)][str(risk)]={}
            for mode in MODES:
                results[str(year)][str(risk)][mode]={
                 str(streak):v50.replay(df,diaries[year],year,allq[(str(risk),mode)],streak)
                 for streak in TREND_CONFIRM}
    summary={year:{risk:{mode:{persist:{k:v for k,v in r.items() if k!="events"}
                             for persist,r in x.items()}
                         for mode,x in schemes.items()}
                  for risk,schemes in groups.items()}
             for year,groups in results.items()}
    return {
      "schema":"GOLD_V51_LEARNED_REGRET_OPPORTUNITY_COST_VS_DOWNSIDE_RESEARCH",
      "research":"V22 gated, regime conditioned, monthly 730d trained two-quantile opportunity cost regression",
      "costOfSelling":"estimated future 20 calendar day max upside (unrealizable oracle expectation)",
      "costOfWaiting":"estimated next five NY17 market sessions max price drawdown",
      "decision":"EXIT if estimated lost upside <= risk_weight*estimated downside",
      "riskWeightsPredeclared":RISK_WEIGHTS,
      "marketRegimeGuard":"optional low bullish-state posterior",
      "sameV22VintageBetweenYears":False,
      "firstprintCertified":False,
      "2024_2026YearsPreviouslyExamined":True,
      "noBuysOrReentries":True,"liveModelNotChanged":True,"noDatabaseWrites":True,
      "provenance":{str(k):v for k,v in vintage.items()},
      "monthsFitted":len(journal),
      "monthly":journal,"summary":summary,"results":results,
      "limitations":[
        "Estimated future pathwise maximum upside is not executable; label is a training oracle.",
        "Policy is approximate learned cost-based stopping, not provably optimal decision rule.",
        "Three clustering regimes are not structural causal macro regimes.",
        "Firstprint and bank transaction quotes not certified.",
        "Uses all-market training rather than genuine older V22 historical risk episodes.",
        "2025 Nisan/2026 outcomes previously viewed in research, not blind.",
        "A model that declines to exit could miss a real market collapse; compare event-based recall.",
        "2024-25 original V22 does not match 2026 later V33 diary version.",
      ]
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--out",default="gold-v51-true-foregone-rally-cost-2024-2026.json")
    z=a.parse_args()
    report=run()
    Path(z.out).write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str)+"\n",encoding="utf8")
    print("V51_SUMMARY",json.dumps(report["summary"],ensure_ascii=False),flush=True)
    print("V51_MONTHS",json.dumps(report["monthly"],ensure_ascii=False),flush=True)
    print("V51_EVENTS",json.dumps({yr:{risk:{mode:{streak:[{
        "risk":e["firstV22"],
        "exit":e["signal"]["timeUTC"] if e["signal"] else None,
        "price":e["signal"]["fillPrice"] if e["signal"] else None,
        "fiveDrop4":e["signal"].get("hitDrop4") if e["signal"] else None,
        "downBeforeUp":e["signal"].get("downFirst") if e["signal"] else None,
        "missed20":e["signal"].get("rallyMissed20CalendarDaysPct") if e["signal"] else None
        } for e in rec["events"]] for streak,rec in runs.items()}
        for mode,runs in modes.items()} for risk,modes in risks.items()}
        for yr,risks in report["results"].items()},ensure_ascii=False),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## V51: explicit cost of missed rally versus risk of waiting, 2024-2026\n\n")
            f.write("NO live execution, no BUY, years not blind, noncanonical 15m source.\n\n")
            f.write("| Year | Risk weight | Method | Streak | Risk episodes | Exit | Dip >=4% | Down before +2% | False | Mean missed 20d upside |\n")
            f.write("|---|---:|---|---:|---:|---:|---:|---:|---:|---:|\n")
            for y,a in report["summary"].items():
                for risk,methods in a.items():
                    for mode,streaks in methods.items():
                        for count,x in streaks.items():
                            f.write(f"| {y} | {risk} | {mode} | {count} | {x['riskWindows']} | {x['signals']} | {x['drop4']} | {x['downBeforeUp']} | {x['noDrop']} | {x['meanMissed20DayUpside']} |\n")
if __name__=="__main__":main()
