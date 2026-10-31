#!/usr/bin/env python3
"""V45 robustness: risk-watch duration 4..16d, full 2024-2026 V22 research.

No 2026 fitted threshold selection or 'one perfect duration'. All options are
evaluated to expose bookkeeping sensitivity and avoid hidden April false exit.
"""
import json,argparse,os
from pathlib import Path
import gold_axis_2026.research.case_control_v13.risk_v44_three_year_v22_streaming_sell_only as m

DURATIONS=(4,6,8,10,12,16)
RULES=("V22_IMMEDIATE","V43_STRUCTURAL_1","TRAIL2_4H_NEG1","TRAIL3_4H_NEG1")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",default="gold-v45-duration-sensitivity-three-year.json")
 a=p.parse_args()
 raw=m.get_bars()
 diaries,sources=m.read_diaries()
 grouped={}
 for year in (2024,2025,2026):
  bars=m.enhance([row for row in raw if row[0].year==year])
  if len(bars)<m.COVERAGE[year]:raise ValueError("INSUFFICIENT_BAR_COVERAGE")
  year_results={}
  for duration in DURATIONS:
   m.MAX_WARN_AGE_CALENDAR_DAYS=duration
   comparisons={}
   for rule in RULES:
    engine=m.Stream(rule,year,diaries[year])
    for b in bars:engine.push(b)
    engine.end(bars[-1])
    result=m.score(engine,bars)
    mm=result["metrics"]
    comparisons[rule]={
      **mm,"episodeRiskStart":[
        {"date":x["firstRiskDate"],
         "signalDate":x["signal"]["signalUTC"] if x["signal"] else None,
         "drawNext5":x["outcome5"]} for x in result["episodes"]
      ]
    }
   year_results[str(duration)]=comparisons
  grouped[str(year)]=year_results
 report={
  "schema":"GOLD_V45_STREAMING_V22_WATCH_DURATION_SENSITIVITY",
  "status":"RESEARCH_NONPIT_AND_2026_NONBLIND",
  "cohorts":"2024_25_orig_V22_effective_review_2026_later_V33",
  "label":"next five distinct NY17 trading sessions >=4pct price loss",
  "durationsCalendarDays":DURATIONS,
  "rulesCompared":RULES,
  "noProductionPromotion":True,"noBuysOrTrades":True,
  "years":grouped,
  "warning":"different risk grouping and suppression gives different false-alarm denominator; no single best duration selected"
 }
 Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 abridged={yr:{dur:{rule:{
   "risk":v["riskEpisodes"],"signal":v["signalEpisodes"],
   "hit":v["matureHitNext5FourPct"],"false":v["matureNoHitNext5FourPct"],
   "unknown":v["outcomesPending"],"noExit":v["noSignalRiskEpisodes"],
  } for rule,v in data.items()} for dur,data in ages.items()}
  for yr,ages in grouped.items()}
 print("THREE_YEAR_WATCH_DURATION_SENSITIVITY",json.dumps(abridged,ensure_ascii=False),flush=True)
 if os.getenv("GITHUB_STEP_SUMMARY"):
  with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
   f.write("## V45 Watch expiry sensitivity: full 2024-26 streaming\n\n")
   f.write("| Year | Risk duration | Rule | Risk clusters | Exits | Valid 5d hits | False 5d | Unknown |\n")
   f.write("|---|---:|---|---:|---:|---:|---:|---:|\n")
   for yr,ages in abridged.items():
    for dur,rules in ages.items():
     for rule,v in rules.items():
      f.write(f"| {yr} | {dur} | {rule} | {v['risk']} | {v['signal']} | {v['hit']} | {v['false']} | {v['unknown']} |\n")
   f.write("\nNo optimized selection and no firstprint/live evidence.\n")
if __name__=="__main__":main()
