#!/usr/bin/env python3
"""V43: risk watch and SELL SIGNAL are distinct; NO BUY/RE-ENTRY or portfolio return.

2026 retrospective V22, timestamped HistData XAU 15-minute price series.
6 warning clusters (>=8 V33 price sessions with no V22 separates clusters).
One EXIT signal per warning cluster. Research candidates are PRE-SPECIFIED,
not tuned using 2026 labels. All price-derived features causal. Signals at
completed bar t, fill proxy next close t+15min (market gaps explicitly tagged).

Scientific performance: foregone upside AFTER warning, signal/peak lag,
giveback from within-watch high, 5-session post-signal decline >=4%,
false/early exits and exposure to subsequent upside. This is NOT a PnL
optimization; NEVER automatically enters/re-enters the market.

WARNING: V22 retrospective firstprint and HistData execution basis unverified,
and this 2026 history has already been inspected; NOT independent blind or live.
"""
from __future__ import annotations
import csv,json,argparse,os
from datetime import date,timedelta
from pathlib import Path
from statistics import mean,median
from gold_axis_2026.research.case_control_v13.risk_v41_v22_watch_sequential_exit_costs import (
  get_bars, enhance, get_2026_diary, V33,
)
RULES=("V22_IMMEDIATE","FIXED_DRAWDOWN2","TRAIL_1P5_AND_4H_NEG1",
       "TRAIL_2_AND_4H_NEG1","TRAIL_3_AND_4H_NEG1",
       "CUMSUM_2_AND_4H_NEG075","VOL_ADAPTIVE_AND_4H_NEG075",
       "STRUCTURAL_BREAK_1_AND_4H_NEG1")
MAX_FOLLOW_SESSIONS=5
EXTRA_EPISODE_HORIZON=10

def v33_calendar():
    with V33.open(encoding="utf8",newline="") as f:
        prices={}
        for x in csv.DictReader(f):
            if x["scenario"]!="AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES":
                continue
            d=date.fromisoformat(x["date"])
            if d.year!=2026 or not x["price"]:continue
            prices[d]=float(x["price"])
    return prices

def watch_clusters(diary,calendar):
    days=sorted(calendar)
    groups=[]
    last_index=-1000
    for i,d in enumerate(days):
        if not diary.get(d,False):continue
        if not groups or i-last_index>8:
            groups.append({"start":d,"end":d,"warnings":[d],"last_index":i})
        else:
            groups[-1]["end"]=d
            groups[-1]["warnings"].append(d)
            groups[-1]["last_index"]=i
        last_index=i
    for i,g in enumerate(groups):
        next_group=groups[i+1]["start"] if i+1<len(groups) else None
        end_idx=min(g["last_index"]+EXTRA_EPISODE_HORIZON,len(days)-1)
        evaluation_end=days[end_idx]
        # End window at next distinct cluster, avoid double counting same price.
        if next_group and next_group<=evaluation_end:
            evaluation_end=days[days.index(next_group)-1]
        g["evaluation_end"]=evaluation_end
        g["censored_calendar"]=end_idx==len(days)-1
    return groups

def first_after_bar_date(bars,day):
    # Binary search, no time leaks: computed boundaries are for retrospective
    # replay only. Simulated model never uses future prices to decide.
    left,right=0,len(bars)
    while left<right:
        mid=(left+right)//2
        if bars[mid]["date"]<=day:left=mid+1
        else:right=mid
    return left

def prepared(bars,group):
    first=first_after_bar_date(bars,group["start"])
    cut=first_after_bar_date(bars,group["evaluation_end"])
    return first,cut

def signal_condition(kind,x,hi,prior):
    p=x["p"]
    draw=100*(p/hi-1)
    r4=100*x["r4"] if x["r4"] is not None else None
    if kind=="V22_IMMEDIATE":return True
    if r4 is None:return False
    if kind=="FIXED_DRAWDOWN2":return draw<=-2
    if kind=="TRAIL_1P5_AND_4H_NEG1":return draw<=-1.5 and r4<=-1
    if kind=="TRAIL_2_AND_4H_NEG1":return draw<=-2 and r4<=-1
    if kind=="TRAIL_3_AND_4H_NEG1":return draw<=-3 and r4<=-1
    if kind=="CUMSUM_2_AND_4H_NEG075":
        return draw<=-2 and r4<=-.75 and x["cusum"]<=-3
    if kind=="VOL_ADAPTIVE_AND_4H_NEG075":
        # 4h conditional sigma from causal recent 15m data (sqrt(16)).
        # FLOOR 1.5%, CAP 4.0%. All arbitrarily pre-specified.
        adaptive=max(1.5,min(4.,300*x["sigma"]*4))
        return draw<=-adaptive and r4<=-.75
    if kind=="STRUCTURAL_BREAK_1_AND_4H_NEG1":
        return draw<=-1 and r4<=-1 and p<x["prior24low"]
    raise ValueError(kind)

def causal_signal(bars,low,high,rule):
    if low>=high:return None
    running_peak=None
    for j in range(low,high):
        current=bars[j]
        running_peak=max(running_peak or current["p"],current["p"])
        if signal_condition(rule,current,running_peak,bars[max(low,j-1)]):
            # Explicitly avoid same candle executable fill. Find next
            # sequential observed bar; track >15m gaps.
            if j+1>=high or j+1>=len(bars):return None
            nxt=bars[j+1]
            return {
                "warningDate":str(bars[low]["date"]),"signalUTC":str(current["ts"]),
                "signalPx":round(current["p"],4),
                "fillUTC":str(nxt["ts"]),"fillPx":round(nxt["p"],4),
                "fillGapMinutes":int((nxt["ts"]-current["ts"]).total_seconds()/60),
                "firstEligibleUTC":str(bars[low]["ts"]),
                "signalIndex":j,
                "fillIndex":j+1,
                "drawFromWatchPeakPct":round(100*(current["p"]/running_peak-1),4),
                "r4Percent":round(100*current["r4"],4) if current["r4"] is not None else None,
            }
    return None

def future_sessions(bars,start_index,num_sessions):
    # Bars strictly later than signal fill, within subsequent num_sessions
    # completed distinct market dates. Do not over-count intraday samples.
    seen=set()
    end=start_index
    first_future=None
    for k in range(start_index+1,len(bars)):
        d=bars[k]["date"]
        if d<=bars[start_index]["date"]:continue
        if d not in seen:
            if len(seen)>=num_sessions:break
            seen.add(d)
            if first_future is None:first_future=k
        end=k+1
    return bars[first_future:end] if first_future is not None else [],len(seen)>=num_sessions

def retrospect(bars,lo,hi,alert):
    start=bars[lo]["p"]
    actual=bars[lo:hi]
    if not actual:return None
    best=max(actual,key=lambda x:x["p"])
    worst=min(actual,key=lambda x:x["p"])
    maxima=100*(best["p"]/start-1)
    minret=100*(worst["p"]/start-1)
    result={
        "watchStartPx":round(start,4),
        "windowMaxPx":round(best["p"],4),
        "windowMaxUTC":str(best["ts"]),
        "windowMinPx":round(worst["p"],4),
        "windowMinUTC":str(worst["ts"]),
        "maxUpsideAfterWatchPct":round(maxima,3),
        "worstFromWatchPct":round(minret,3),
        "watchHas4PctDrawdown":minret<=-4,
    }
    if alert is None:
        return {**result,"exit":None,"futureMature":False}
    j=alert["fillIndex"]
    fp=bars[j]["p"]
    future,mature=future_sessions(bars,j,MAX_FOLLOW_SESSIONS)
    # data gap or truncated horizon must never be labeled false success.
    future_low=min((x["p"] for x in future),default=None)
    future_high=max((x["p"] for x in future),default=None)
    exit_to_max=(100*(best["p"]/fp-1) if best["ts"]>=bars[j]["ts"]
                 else 0.0)
    # Optimistic oracle was not actionable in real time.
    result["exit"]={
        **{k:v for k,v in alert.items() if k not in ("signalIndex","fillIndex")},
        "maxForegoneRisePostExitPct":round(max(0,exit_to_max),3),
        "oraclePeakPriceGivebackPct":round(100*(best["p"]-fp)/best["p"],3),
        "exitedAfterWindowPeak":bars[j]["ts"]>best["ts"],
        "future5MinPrice":round(future_low,4) if mature else None,
        "future5WorstReturnPct":round(100*(future_low/fp-1),3) if mature else None,
        "future5MaxRisePct":round(100*(future_high/fp-1),3) if mature else None,
        "postExit4PctDecline":(100*(future_low/fp-1)<=-4) if mature else None,
        "postExitDipBeatsRoundTrip1p6Pct":(100*(future_low/fp-1)<=-1.6) if mature else None,
        "priceGapOver15Minutes":alert["fillGapMinutes"]>15,
    }
    result["futureMature"]=mature
    return result

def aggregate(res):
    all_events=list(res.values())
    signaled=[x for x in all_events if x["exit"] is not None]
    mature=[x for x in signaled if x["futureMature"]]
    wins=[x for x in mature if x["exit"]["postExit4PctDecline"]]
    false=[x for x in mature if not x["exit"]["postExit4PctDecline"]]
    return {
        "clusters":len(all_events),"eligibleExits":len(signaled),
        "noExitClusters":len(all_events)-len(signaled),
        "maturePostExit":len(mature),
        "next5Real4PctDecline":len(wins),
        "next5No4PctDecline":len(false),
        "next5PostExitPrecisionPct":round(100*len(wins)/len(mature),2) if mature else None,
        "meanForegoneUpsidePct":round(mean(x["exit"]["maxForegoneRisePostExitPct"] for x in signaled),3) if signaled else None,
        "medianPeakGivebackPct":round(median(x["exit"]["oraclePeakPriceGivebackPct"] for x in signaled),3) if signaled else None,
        "maturePostExit1p6Avoided":sum(bool(x["exit"]["postExitDipBeatsRoundTrip1p6Pct"]) for x in mature),
        "fillsAfterMarketGap":sum(x["exit"]["priceGapOver15Minutes"] for x in signaled),
    }

def run():
    raw=get_bars()
    candles=enhance([r for r in raw if r[0].year==2026])
    diary=get_2026_diary()
    calendar=v33_calendar()
    groups=watch_clusters(diary,calendar)
    scores={method:{} for method in RULES}
    for group in groups:
        low,high=prepared(candles,group)
        if low>=len(candles):continue
        for method in RULES:
            exit=causal_signal(candles,low,high,method)
            sc=retrospect(candles,low,high,exit)
            if sc is None:continue
            scores[method][str(group["start"])]={
                "riskStart":str(group["start"]),"lastV22Warning":str(group["end"]),
                "riskWarningDays":len(group["warnings"]),
                "scoringWindowEnd":str(group["evaluation_end"]),
                "scoringEndCensored":group["censored_calendar"],
                **sc,
            }
    return {
        "schema":"GOLD_V43_RISK_WATCH_TO_EXIT_SIGNALS_NO_REENTRY_RESEARCH_V1",
        "evidence":"2026_RETROSPECTIVE_NOT_BLIND_NO_FIRSTPRINT",
        "title":"V22 early warning does NOT imply sell; sequential turning point for exit signal",
        "source":"NONCANONICAL_HISTDATA_M15_2026_JAN_SEP_AND_V33_V22",
        "timing":"bars timestamp starts; actual arrival and next close executable unverified",
        "ruleSelection":"PREDEFINED_SENSITIVITY_CANDIDATES_WITHOUT_FITTING_2026",
        "evaluatedThrough":"2026-09-30/2026-10-01 04:45 UTC",
        "costAwareness":"1.6% roundtrip hurdle as descriptive post-exit decline metric only; NO trades",
        "riskClusters":len(groups),
        "comparisons":{k:aggregate(v) for k,v in scores.items()},
        "perEpisode":scores,
        "noBuySignals":True,"noPortfolioSimulation":True,
        "noProductionSignals":True,"neonWrites":False,
        "firstprintNotCertified":True,
        "limitations":[
          "V22 diary source timing not firstprint certified",
          "2026 historical events already observed, not blind test",
          "15m price close is not a guaranteed executable sell price",
          "5-day decline score conditional on sell date, not independent episode ground truth",
          "watch clusters based on historic V22 diary; distinct episode count is small",
          "cannot conclude a universal best exit parameter from these 2026 outcomes",
          "6 risk clusters are not 6 independent major decline episodes",
          "post-exit future price only used to audit, never to trigger signals",
          "no reopening, no buy advice, no cost-based trading PnL optimization"
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-v43-watch-to-exit-episode-score.json")
    a=p.parse_args()
    report=run()
    Path(a.out).write_text(json.dumps(report,ensure_ascii=False,default=str,indent=2)+"\n",encoding="utf8")
    print(json.dumps({k:v for k,v in report.items() if k!="perEpisode"},ensure_ascii=False,indent=2,default=str))
    print("EPISODE_EVIDENCE_START",json.dumps({method:[{
        "start":key,"warningUpside":round(record["maxUpsideAfterWatchPct"],2),
        "maxRiskDrawdown":round(record["worstFromWatchPct"],2),
        "signalUTC":record["exit"]["signalUTC"] if record["exit"] else None,
        "fillPx":record["exit"]["fillPx"] if record["exit"] else None,
        "foregoneUpside":record["exit"]["maxForegoneRisePostExitPct"] if record["exit"] else None,
        "future5":record["exit"]["future5WorstReturnPct"] if record["exit"] else None,
        "next5Conf":record["exit"]["postExit4PctDecline"] if record["exit"] else None,
        "gap":record["exit"]["fillGapMinutes"] if record["exit"] else None,
    } for key,record in episodes.items()] for method,episodes in report["perEpisode"].items()},
     ensure_ascii=False,default=str), "EPISODE_EVIDENCE_END",flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## V43: V22 WATCH is not SELL; causal event-level exit signal audit\n\n")
            f.write("| Rule | Signal clusters | 5d >=4% | Unmatched 5d | Mean missed-upside % | Median peak giveback % |\n")
            f.write("|---|---:|---:|---:|---:|---:|\n")
            for rule,x in report["comparisons"].items():
                f.write(f"| {rule} | {x['eligibleExits']} | {x['next5Real4PctDecline']} | {x['next5No4PctDecline']} | "
                        f"{x['meanForegoneUpsidePct']} | {x['medianPeakGivebackPct']} |\n")
            f.write("\n**No buy/reentry/portfolio, no firstprint proof, no live outputs.**\n")
if __name__=="__main__":
    main()
