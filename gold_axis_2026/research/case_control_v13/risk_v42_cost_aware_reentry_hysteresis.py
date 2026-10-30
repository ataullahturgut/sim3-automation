#!/usr/bin/env python3
"""V42: risk-to-exit transition with cost-aware HYSTERESIS for re-entry.

Frozen exit from V41: only after V22 WATCH and decline >=3% from highest
observed close since WATCH, accompanied by 4h XAU <=-1% (bars contiguous).
Next close fill, 0.8% buy and 0.8% sell. Different re-entry policies selected
2025 on synthetic watch; evaluated on V22 2026 without 2026 rule selection.

Fee-aware no-trade band is testable scientific hypothesis, NOT proof of live
trading performance.  Source is non-canonical and historical V22 not PIT.
"""
from __future__ import annotations
from datetime import date
import os,json,argparse
from pathlib import Path
from gold_axis_2026.research.case_control_v13.risk_v41_v22_watch_sequential_exit_costs import (
  get_bars,enhance,synthetic_diary,get_2026_diary,BUY_COST,SELL_COST,
)
REENTRIES={
  "REENTER_24H":(96,6,0,False),
  "REENTER_48H":(192,6,0,False),
  "REENTER_5D":(480,6,0,False),
  "REENTER_10D":(960,6,0,False),
  "REENTER_5D_PREMIUM2":(480,6,.02,False),
  "REENTER_10D_PREMIUM2":(960,6,.02,False),
  "REENTER_10D_PREMIUM4":(960,6,.04,False),
  "REENTER_5D_WAIT10":(480,10,0,False),
  "REENTER_10D_WAIT10":(960,10,0,False),
  "REENTER_EMA_PREMIUM2":(96,6,.02,True),
  "NEVER_REENTER":(99999,999,999,False),
}
def common_signals(diary,year):
 return {d for d,s in diary.items() if s and d.year==year}

def replay(rows,diary,year,style):
 n_bars,no_risk_days,break_even,ema_only=REENTRIES[style]
 signals=common_signals(diary,year)
 cash=0.0; gold=100/(rows[0]["p"]*(1+BUY_COST)); hold=True
 fee=100*BUY_COST/(1+BUY_COST)
 watch=False;watch_high=0;last_warn=None;last_exit=None;last_exit_px=None
 pending=None;orders=[];maxval=100;mdd=0;daily=[]
 for i,r in enumerate(rows):
  ts=r["ts"];day=ts.date();p=r["p"]
  # Execute at NEXT 15-minute observation; never current bar.
  if pending and i>pending[0]:
   if pending[1]=="SELL" and hold:
    cash=gold*p*(1-SELL_COST);fee+=gold*p*SELL_COST
    gold=0;hold=False;watch=False;last_exit=day;last_exit_px=p
    orders.append({"type":"SELL","date":str(day),"utc":str(ts),"price":round(p,2),"cash":round(cash,2)})
   elif pending[1]=="BUY" and not hold:
    fee+=cash*BUY_COST/(1+BUY_COST)
    gold=cash/(p*(1+BUY_COST));cash=0;hold=True;watch=False;watch_high=0
    orders.append({"type":"BUY","date":str(day),"utc":str(ts),"price":round(p,2)})
   pending=None
  if i and rows[i-1]["date"]!=day:
   d=rows[i-1]["date"]
   if d in signals:
    last_warn=d
  risk=(last_warn is not None and 0<(day-last_warn).days<=12)
  if hold:
   if risk and not watch:
    watch=True;watch_high=p
   if watch:
    if not risk:
     watch=False;watch_high=0
    else:
     watch_high=max(watch_high,p)
     if r["r4"] is not None and p/watch_high<=.97 and r["r4"]<=-.01 and i+1<len(rows):
      if pending is None:
       pending=(i,"SELL")
  elif pending is None and style!="NEVER_REENTER":
   # Each no-reentry condition leaves cash and equity accounting intact.
   eligible=(last_exit is not None and (day-last_exit).days>=3 and
             r["r4"] is not None and i>=max(96,n_bars))
   most_recent=(day-last_warn).days if last_warn else 999
   if eligible and most_recent>no_risk_days:
    prior_high=max(x["p"] for x in rows[i-n_bars:i])
    minimum_price=last_exit_px*(1+break_even)
    improving=(p>r["ema"] and r["r4"]>.0025)
    breakout=(improving if ema_only else p>prior_high and r["r4"]>.0025)
    if breakout and p>=minimum_price and improving and i+1<len(rows):
     pending=(i,"BUY")
  eq=gold*p*(1-SELL_COST) if hold else cash
  maxval=max(maxval,eq)
  mdd=min(mdd,eq/maxval-1)
  if i==len(rows)-1 or rows[i+1]["date"]!=day:
   daily.append([str(day),round(eq,3),int(hold)])
 net=gold*rows[-1]["p"]*(1-SELL_COST) if hold else cash
 return {"netUSD":round(net,4),"maxDrawdownPct":round(100*mdd,2),
         "trades":len(orders),"exits":sum(o["type"]=="SELL" for o in orders),
         "feesUSD":round(fee,2),"lastHolding":hold,
         "orders":orders,"dailyEquity":daily}

def select(validation):
 # 2025 only. Do not use 2026 to choose.
 ranked=[]
 for name,r in validation.items():
  # net USD - small penalty for max drawdown and per executed transaction.
  score=r["netUSD"]+.2*r["maxDrawdownPct"]-.2*r["trades"]
  ranked.append((round(score,5),name))
 return sorted(ranked,reverse=True)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--out",default="gold-v42-hysteresis-cost-aware-reentry.json")
 a=ap.parse_args()
 bars=get_bars()
 byyear={year:enhance([x for x in bars if x[0].year==year]) for year in (2024,2025,2026)}
 if any(len(x)<15000 for x in byyear.values()):
  raise ValueError("INCOMPLETE_HISTDATA_YEAR")
 diary={2024:synthetic_diary(byyear[2024]),
        2025:synthetic_diary(byyear[2025]),2026:get_2026_diary()}
 results={year:{k:replay(byyear[year],diary[year],year,k) for k in REENTRIES}
          for year in (2024,2025,2026)}
 ranked=select(results[2025])
 selected=ranked[0][1]
 summary={str(year):{name:{k:v for k,v in r.items() if k not in ("orders","dailyEquity")}
           for name,r in group.items()} for year,group in results.items()}
 result={
  "schema":"GOLD_V42_COST_AWARE_EXIT_REENTRY_HYSTERESIS_HISTORICAL_V1",
  "source":"noncanonical_histdata_15min_and_retrospective_v22",
  "status":"RESEARCH_ONLY_NOT_PIT",
  "riskToExit":"V22 WATCH, post-watch high retrace -3%, negative XAU 4h -1%",
  "fixedExitSelected2025EarlierV41":True,
  "reentrySelectedOnlyWith2025SyntheticWatch":True,
  "selectedReentryPolicy":selected,
  "selectionRanking2025":ranked,
  "period2026":"2026-01-01_to_2026-10-01_UTC_not_full_2026",
  "costs":"0.8pct_buy_plus_0.8pct_sell_at_next_15m_close",
  "resultSummary":summary,
  "selectedOrders2026":results[2026][selected]["orders"],
  "other2026Orders":{"NEVER_REENTER":results[2026]["NEVER_REENTER"]["orders"]},
  "selected2026Equity":results[2026][selected]["dailyEquity"],
  "limitations":[
   "Synthetic watch 2024-25 is not real V22; domain shift likely",
   "2026 prices and event outcomes previously reviewed; not blind holdout",
   "2026 retrospective V22 not firstprint-certified",
   "Timestamped 15m CLOSE is a proxy, not a guaranteed executable broker quote",
   "0.8% each side excludes further slippage, variable spreads and taxes",
   "Only through 1 October 2026; no extrapolation to October 30",
   "No 2026 re-entry selection, no live actions, no Neon writes"
  ],
  "productionChanged":False,"ordersSent":False,"neonWrites":False
 }
 Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:v for k,v in result.items() if k not in ("selected2026Equity",)},ensure_ascii=False,indent=2))
 if os.getenv("GITHUB_STEP_SUMMARY"):
  with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
   f.write("## V42 re-entry: transaction cost hysteresis (historical only)\n\n")
   f.write(f"Selected on 2025: **{selected}**\n\n")
   f.write("| Policy | 2025 net | 2026 net | 2026 exits | 2026 max drawdown |\n|---|---:|---:|---:|---:|\n")
   for name,r in results[2026].items():
    f.write(f"| {name} | {results[2025][name]['netUSD']} | "
            f"{r['netUSD']} | {r['exits']} | {r['maxDrawdownPct']} |\n")
   f.write("\nNo prospective firstprint or model promotion.\n")
if __name__=="__main__":main()
