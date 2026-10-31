#!/usr/bin/env python3
"""V46 detailed 2025 real V22 risk -> EXIT timeline; no buy, re-entry or PnL.

Outputs 2025 event-by-event, including whether newer risk signs arrived while
EXIT_RECORDED, and historical missed upside. Audits 4,6,8,10,12,16 days
without fitting thresholds on 2025 or using future prices for signals.
"""
from __future__ import annotations
import argparse,json,os
from pathlib import Path
from datetime import timedelta
from gold_axis_2026.research.case_control_v13.risk_v41_v22_watch_sequential_exit_costs import get_bars,enhance
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as m

AGES=(4,6,8,10,12,16)
RULES=("V22_IMMEDIATE","V43_STRUCTURAL_1","TRAIL2_4H_NEG1")
def evaluate():
    diaries,sources=m.read_diaries()
    barrows=[v for v in get_bars() if v[0].year==2025]
    if len(barrows)<m.COVERAGE[2025]:raise ValueError("2025_INSUFFICIENT_BARS")
    bars=enhance(barrows)
    by_ts={str(b["ts"]):i for i,b in enumerate(bars)}
    result={}
    for days in AGES:
        m.MAX_WARN_AGE_CALENDAR_DAYS=days
        byrule={}
        for rule in RULES:
            e=m.Stream(rule,2025,diaries[2025])
            for b in bars:e.push(b)
            e.end(bars[-1])
            scored=m.score(e,bars)
            events=[]
            for s in scored["episodes"]:
                risk=s["firstRiskDate"]
                sig=s["signal"]
                x={
                   "riskFirst":risk,
                   "riskLast":s["lastRiskDate"],
                   "riskUpdates":s["riskUpdates"],
                   "watchStartUTC":s["watchStartUTC"],
                   "watchEndUTC":s["watchEndUTC"],
                   "signalUTC":sig["signalUTC"] if sig else None,
                   "next15Price":sig["fillPx"] if sig else None,
                   "follow5MinReturnPct":s["outcome5"],
                   "follow5Drop4Confirmed":s.get("confirmed4Pct"),
                   "maxRiseSinceWatchPct":s.get("maxRiseSinceWatchPct"),
                   "additionalUpsideWithinEpisodeAfterExitPct":s.get("foregoneRiseWithinEpisodePct"),
                   "closePriceReferenceIsExecutable":False,
                }
                if sig and sig["fillUTC"] and sig["fillUTC"] in by_ts:
                    j=by_ts[sig["fillUTC"]]
                    after=[b for b in bars[j:] if b["ts"]<=bars[j]["ts"]+timedelta(days=24)]
                    p=max(after,key=lambda b:b["p"])
                    x["postSignal24CalendarDayMaxPrice"]=round(p["p"],3)
                    x["postSignal24CalendarDayMaxDateUTC"]=str(p["ts"])
                    x["postSignal24CalendarDayMaxRisePct"]=round(100*(p["p"]/sig["fillPx"]-1),3)
                events.append(x)
            byrule[rule]={"metrics":scored["metrics"],"episodes":events}
        result[str(days)]=byrule
    return {
      "schema":"GOLD_V46_2025_ORIGINAL_V22_RISK_TO_EXIT_FULL_MONTHLY_EVENT_TIMELINE",
      "source":"2025_original_v22_daily_decisions_effective_review_and_HistData_15m_NOT_PIT",
      "year":2025,
      "2025V22RiskDays":sum(diaries[2025].values()),
      "2025OriginalV22DecisionRows":len(diaries[2025]),
      "2025RiskDates":[str(d) for d,x in sorted(diaries[2025].items()) if x],
      "15mBars":len(bars),
      "period":str(bars[0]["ts"])+" / "+str(bars[-1]["ts"]),
      "risksNotVerifiedFirstprint":True,
      "noBuys":True,"noReentry":True,"noPortfolio":True,
      "parametersFixedBeforeThisReview":True,
      "maxAfterSignal24DayOnlyAuditNeverSignal":True,
      "durationSensitivities":result
    }
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="gold-v46-2025-real-v22-all-alerts-and-exits.json")
    args=parser.parse_args()
    r=evaluate()
    Path(args.out).write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("V46_2025_RISK_DATES",json.dumps(r["2025RiskDates"]),flush=True)
    for age,data in r["durationSensitivities"].items():
        print("V46_2025_DURATION",age,json.dumps(data,ensure_ascii=False),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
      with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
        f.write("## V46 full 2025 original V22 signal / exit audit\n\n")
        f.write("| Watch age | Method | Risk clusters | Exit alerts | Matched next5 >=4% | Unmatched | No exit |\n")
        f.write("|---:|---|---:|---:|---:|---:|---:|\n")
        for age,data in r["durationSensitivities"].items():
          for rule,v in data.items():
            a=v["metrics"]
            f.write(f"| {age} | {rule} | {a['riskEpisodes']} | {a['signalEpisodes']} | "
                    f"{a['matureHitNext5FourPct']} | {a['matureNoHitNext5FourPct']} | "
                    f"{a['noSignalRiskEpisodes']} |\n")
        f.write("\nNo buys, 2025 retrospective, not PIT.\n")
if __name__=="__main__":main()
