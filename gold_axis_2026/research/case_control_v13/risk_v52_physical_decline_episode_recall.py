#!/usr/bin/env python3
"""V52 read-only physical large drawdown event recall audit independent of V22.

Defines one raw XAU physical episode at FIRST 4% intraday close drawdown
relative to trailing FIVE NY17 trading-session running maximum. Re-arm
only after drawdown recovers to less than 2%. Label is computed independent
of V22 models and their exit signal grouping.

For each first physical 4% crossing, audit V22 history or learned EXIT
in preceding 10 calendar days (not precision, not causal firstprint).
Data are historical candidate close, not executable price; this is a
research backtest, not a live inference / trading system.
"""
from __future__ import annotations
import argparse,json
from collections import deque
from pathlib import Path
import pandas as pd
import numpy as np
import gold_axis_2026.research.case_control_v13.risk_v47_yearwise_supervised_exit_adaptation as v47
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as v44

TRAILING_SESSIONS=5
DRAW_THRESHOLD=.04
REARM_THRESHOLD=.02
BEFORE_EVENT_CALENDAR_DAYS=10

def physical_crossings(df):
    p=df.p.to_numpy(dtype=float)
    sess=df.session.to_numpy(dtype=int)
    t=df.ts
    q=deque()
    armed=True;events=[]
    for i in range(len(df)):
        # Descending monotonic max-queue; source uses present and last 4
        # trading sessions, no future observations.
        while q and sess[q[0]]<sess[i]-TRAILING_SESSIONS+1:q.popleft()
        while q and p[q[-1]]<=p[i]:q.pop()
        q.append(i)
        peak=q[0]
        dd=1-p[i]/p[peak]
        if armed and dd>=DRAW_THRESHOLD:
            event={"first4PctCrossUTC":str(t.iloc[i]),
                   "peakUTC":str(t.iloc[peak]),"peakPrice":round(float(p[peak]),3),
                   "crossingPrice":round(float(p[i]),3),
                   "drawdownAtCrossPct":round(100*float(dd),3),
                   "year":int(t.iloc[i].year)}
            events.append(event);armed=False
        elif not armed and dd<REARM_THRESHOLD:
            armed=True
    return events

def earliest_eligible_risk_times(df,diary):
    """Use an entire day D V22 label only at first observed market bar
    strictly AFTER D. Never pretend a warning was visible at D 00:00.
    Firstprint is not verified, so even this is optimistic day+1 proxy.
    """
    days=np.asarray(df.day.to_numpy(),dtype="datetime64[D]")
    times=df.ts
    usable=[]
    for day,alert in diary.items():
        if not alert:continue
        after=int(np.searchsorted(days,np.datetime64(day),side="right"))
        if after<len(df):
            usable.append(times.iloc[after])
    return usable

def audit(report,df):
    events=physical_crossings(df)
    v22,_=v44.read_diaries()
    by_year={}
    for year in (2024,2025,2026):
        cohort=[x for x in events if x["year"]==year]
        s=report["results"][str(year)]
        choices={
            "R1_GUARD_4":s["1.0"]["LEARNED_REGRET_REGIME_GUARD"]["4"],
            "R1_5_GUARD_4":s["1.5"]["LEARNED_REGRET_REGIME_GUARD"]["4"],
        }
        warning_days=earliest_eligible_risk_times(df,v22[year])
        signals={key:[pd.Timestamp(x["signal"]["timeUTC"])
                       for x in data["events"] if x["signal"]]
                 for key,data in choices.items()}
        for ev in cohort:
            crossing=pd.Timestamp(ev["first4PctCrossUTC"])
            lower=crossing-pd.Timedelta(days=BEFORE_EVENT_CALENDAR_DAYS)
            ev["V22WarningInPrior10Days"]=any(lower<=w<=crossing for w in warning_days)
            for key,times in signals.items():
                qualifying=[t for t in times if lower<=t<=crossing]
                ev[key+"_EXIT_InPrior10Days"]=bool(qualifying)
                ev[key+"_LastEXITBeforeCrossUTC"]=str(max(qualifying)) if qualifying else None
        by_year[str(year)]={
           "physical4pctDrawdownEpisodes":len(cohort),
           "V22Covered":sum(e["V22WarningInPrior10Days"] for e in cohort),
           **{key+"_Covered":sum(e[key+"_EXIT_InPrior10Days"] for e in cohort)
                 for key in signals},
           "events":cohort
        }
    return {
      "schema":"GOLD_V52_INDEPENDENT_PHYSICAL_FIVE_SESSION_4PCT_DRAWDOWN_CROSSINGS",
      "status":"RETROSPECTIVE_NONCANONICAL_SOURCE_NOT_FIRSTPRINT",
      "definition":"first -4% from current+past4 NY17 trading-session maximum; re-arm when drawdown <2%",
      "match":"V22 label day+1 first available market bar or V51 exit in prior ten calendar days, never assumed day-start known",
      "parameters":{"sessions":TRAILING_SESSIONS,"dropPct":4,
                    "rearmPct":2,"leadWindowDays":10},
      "limitations":[
         "Physical crossing is already a 4% drawdown, not a forecast date",
         "Grouping depends on 2% recovery threshold, can merge separate declines",
         "10-day match is arbitrary sensitivity definition, not model training",
         "V22 historical different vintages and neither firstprint-certified",
         "V22 dated D enters only at first observed bar with date > D; same-day declines do not count as prewarned",
         "Candidate XAUUSD close not executable bid/ask or universal truth",
         "Precision measures and sell-after-cross episodes are not counted here",
      ],
      "years":by_year
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--research-json",required=True)
    a.add_argument("--out",default="gold-v52-physical-decline-recall.json")
    args=a.parse_args()
    report=json.loads(Path(args.research_json).read_text(encoding="utf8"))
    if report.get("schema")!="GOLD_V51_LEARNED_REGRET_OPPORTUNITY_COST_VS_DOWNSIDE_RESEARCH":
        raise ValueError("EXPECTED_V51_RESEARCH_JSON")
    df=v47.fetch_bars()
    output=audit(report,df)
    Path(args.out).write_text(json.dumps(output,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
    print("V52_PHYSICAL_EVENT_COVERAGE",json.dumps({
      y:{k:v for k,v in o.items() if k!="events"}
      for y,o in output["years"].items()},ensure_ascii=False),flush=True)
    print("V52_PHYSICAL_EPISODES",json.dumps(output["years"],ensure_ascii=False),flush=True)
    import os
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as h:
            h.write("## V52 Physical independent large-price-decline recall\n\n")
            h.write("| Year | Raw physical -4% crossings | V22 covered | V51 low risk+guard covered | V51 high risk+guard covered |\n")
            h.write("|---|---:|---:|---:|---:|\n")
            for year,m in output["years"].items():
                h.write(f"| {year} | {m['physical4pctDrawdownEpisodes']} | {m['V22Covered']} | {m['R1_GUARD_4_Covered']} | {m['R1_5_GUARD_4_Covered']} |\n")
if __name__=="__main__":main()
