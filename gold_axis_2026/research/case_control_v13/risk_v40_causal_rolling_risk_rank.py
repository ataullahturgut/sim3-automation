#!/usr/bin/env python3
"""V40: causal rolling rank of ridge risk forecasts + four-metal hourly shock.

A 60-day moving empirical rank detects regime shifts without forcing the
unstable 2025 absolute probability threshold onto 2026. 2024 fit, 2025
threshold/cooldown selection (5-day drop), 2026 historical evaluation.
ALL DATA research-only, NOT blind/PIT or production-safe.  No Neon writes.
"""
from __future__ import annotations
import argparse,json,os
import numpy as np
from pathlib import Path
from gold_axis_2026.research.case_control_v13.risk_v39_ridge_prior_fourmetal_confirmation import (
  read_daily,add_features,label_targets,transform,
  read_intraday,original_rows,compile_calendar,episode_stats,
)
WINDOW=60
CUTOFFS=(.75,.80,.85,.90,.95,.975,1.01)

def past_only_ranks(previous_scores, new_scores, lookback=WINDOW):
    """Rank of score D uses strictly D-1..D-lookback, never D+1."""
    history=list(map(float,previous_scores))
    ranks=[]
    for p in new_scores:
        past=history[-lookback:]
        ranks.append(None if len(past)<lookback
                 else (1+sum(x<=float(p) for x in past))/(len(past)+1))
        history.append(float(p))
    return ranks

def evaluate():
    prices=read_daily()
    rows=add_features(prices)
    labels=label_targets(rows)
    train=[r for r in labels if r["date"].year==2024]
    valid=[r for r in labels if r["date"].year==2025]
    # All 2025 scores, including end-of-year 5 sessions omitted from validation,
    # can be computed for an unsupervised 2026 rank reference.
    valid_all=[r for r in rows if r["date"].year==2025]
    test_all=[r for r in rows if r["date"].year==2026]
    valp,testp,meta=transform(train,valid_all,test_all)
    val_map={r["date"]:float(p) for r,p in zip(valid_all,valp)}
    valid_ranks=past_only_ranks([],valp)
    for r,p,rank in zip(valid_all,valp,valid_ranks):
        r["riskProb"]=float(p)
        r["riskRank"]=rank
    test_ranks=past_only_ranks(valp,testp)
    for r,p,rank in zip(test_all,testp,test_ranks):
        r["riskProb"]=float(p)
        r["riskRank"]=rank
    valid_rankable=[r for r in valid if
                     val_map.get(r["date"]) is not None and
                     next((a.get("riskRank") for a in valid_all
                         if a["date"]==r["date"]),None) is not None]
    # valid and valid_all refer to independent copied dicts, so bind ranks
    # explicitly by date; no price, label or risk score can look into 2026.
    known_rank={r["date"]:r["riskRank"] for r in valid_all}
    for r in valid_rankable:r["riskRank"]=known_rank[r["date"]]
    if len(valid_rankable)<160:raise ValueError("NOT_ENOUGH_VALIDATION_HISTORY")
    chosen=[]
    for threshold in CUTOFFS:
        fn=lambda r,t=threshold:r["riskRank"] is not None and r["riskRank"]>=t
        stats=episode_stats(valid_rankable,fn)
        if stats["noHitNext5"]<=3:
            chosen.append((stats["hitNext5"],-stats["noHitNext5"],
                           -stats["alerts"],threshold,stats))
    if not chosen:raise ValueError("NO_VALIDATION_THRESHOLD")
    best=max(chosen,key=lambda x:x[:3])
    threshold=best[3]
    original=original_rows()
    intraday=compile_calendar(read_intraday(),original)
    bydate={r["date"]:r for r in intraday}
    common=[r for r in test_all if r["date"] in bydate]
    if len(common)<145:raise ValueError("NO_HOURLY_COMMON_HISTORY")
    for r in common:
        r["v22"]=bydate[r["date"]]["v22"]
        r["fourShock"]=bydate[r["date"]]["four_same_1pct"]>0
        r["goldHard"]=bydate[r["date"]]["xau_hard"]>0
    specs={
     "V22":lambda r:r["v22"],
     "V22_OR_RAW_FOURMETAL":lambda r:r["v22"] or r["fourShock"],
     "ROLLING_RANK_PRIOR_ONLY":lambda r:r["riskRank"] is not None and r["riskRank"]>=threshold,
     "V22_OR_FOURMETAL_AND_ROLLING_RANK":lambda r:
         r["v22"] or (r["fourShock"] and r["riskRank"] is not None
                     and r["riskRank"]>=threshold),
     "V22_AND_ROLLING_RANK_PRIORITY":lambda r:
         r["v22"] and r["riskRank"] is not None and r["riskRank"]>=threshold,
     "V22_OR_GOLD_HARD_AND_ROLLING_RANK":lambda r:
         r["v22"] or (r["goldHard"] and r["riskRank"] is not None
                     and r["riskRank"]>=threshold),
    }
    matured=[]
    for i,r in enumerate(common):
        if i+5>=len(common):continue
        future=common[i+1:i+6]
        if (future[-1]["date"]-r["date"]).days>12:continue
        outcome=100*(min(x["au"] for x in future)/r["au"]-1)<=-4
        matured.append({**r,"target":outcome})
    truth=sum(r["target"] for r in matured)
    if len(matured)<130 or not truth:raise ValueError("INSUFFICIENT_MATURED_TARGETS")
    scores={}
    for name,fn in specs.items():
        flagged=[r for r in matured if fn(r)]
        h=sum(r["target"] for r in flagged)
        scores[name]={
          "warningDays":len(flagged),"next5Matched":h,
          "next5Unmatched":len(flagged)-h,
          "recallPct":round(100*h/truth,2),
          "precisionPct":round(100*h/len(flagged),2) if flagged else None,
          "episodes":episode_stats(common,fn),
        }
    events=[]
    for name,day in (
      ("Mayıs","2026-05-13"),("Haziran I","2026-06-04"),
      ("Haziran II","2026-06-17"),("Ağustos","2026-08-25"),
      ("Eylül","2026-09-21")):
        before=[r for r in common if str(r["date"])<day][-10:]
        events.append({
          "name":name,"start":day,
          "warnings":{k:(str(next((r["date"] for r in before if f(r)),None))
             if any(f(r) for r in before) else None) for k,f in specs.items()}
        })
    absolute=.9098297729049727 # V39 2025 separately calibrated threshold; not reused
    def pcounts(a):
        return {"n":len(a),"medianProb":round(float(np.median([r["riskProb"] for r in a])),4),
                "p90Prob":round(float(np.quantile([r["riskProb"] for r in a],.90)),4),
                "aboveV39AbsoluteThreshold":sum(r["riskProb"]>=absolute for r in a),
                "aboveAdaptiveRankThreshold":sum(r.get("riskRank") is not None and
                     r["riskRank"]>=threshold for r in a)}
    return {
      "schema":"GOLD_V40_CAUSAL_ROLLING_RANK_FOURMETAL_FALSE_ALERT_GATES_V1",
      "status":"HISTORICAL_RESEARCH_NONBLIND_NO_FIRSTPRINT",
      "trainDays":len(train),"trainPositive":meta["trainPositive"],
      "validationDays":len(valid_rankable),"frozenRankThreshold":threshold,
      "validationChoice":best[4],"2026CommonDays":len(common),
      "2026MaturedDays":len(matured),"2026FourPctOriginDays":truth,
      "riskScoreDrift":{"2025":pcounts(valid_all),"2026Matched":pcounts(common)},
      "warningRules":scores,"events":events,
      "noLiveSignal":True,"noDatabaseWrites":True,"noTrades":True,
      "caution":[
         "2026 test prices were previously inspected; not untouched blind",
         "StakTrakr hourly only since 2026-03-25; 2024 hourly four-metal calibration unavailable",
         "Historical four-metal source quotes not firstprint-certified",
         "Empirical rolling ranks do not guarantee conformal false-alarm coverage under dependence/drift",
         "Alarm eight-session suppression changes messages, not truth",
         "Only 7 positive origin days in 2024; ridge probability unstable"]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-v40-causal-rolling-risk-rank.json")
    args=p.parse_args()
    r=evaluate()
    Path(args.out).write_text(json.dumps(r,ensure_ascii=False,default=str,indent=2)+"\n",encoding="utf8")
    print(json.dumps(r,ensure_ascii=False,default=str,indent=2))
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## V40 causal rolling 60-day regime rank research\n\n")
            f.write(f"2025 frozen rank threshold: {r['frozenRankThreshold']}; common days: {r['2026CommonDays']}\n\n")
            f.write("| Strategy | Days | 5d matches | 5d unmatched | Alert episodes | 10d nonmatches |\n|---|---:|---:|---:|---:|---:|\n")
            for k,v in r["warningRules"].items():
                f.write(f"| {k} | {v['warningDays']} | {v['next5Matched']} | "
                        f"{v['next5Unmatched']} | {v['episodes']['alerts']} | "
                        f"{v['episodes']['noHitNext10']} |\n")
            f.write("\nNot firstprint or production approved.\n")
if __name__=="__main__":
    main()
