#!/usr/bin/env python3
"""V41 Research-only V22 WATCH -> sequential CHANG EPOINT EXIT -> re-enter.

Objective: do not sell on early V22 warning while price still trends upward.
Train/design 2024, SELECT fixed execution rules using 2025 only, EVALUATE
historical 2026, with next completed 15m close fills and 0.8% each leg.
No lookahead, no same-bar fills, no signal/time-provenance certification.
Historical HistData candidate is not price execution proof or tradable quote.
"""
from __future__ import annotations
import csv,json,os,argparse
from pathlib import Path
from collections import deque
from datetime import date,timedelta,datetime,timezone
import math

ROOT=Path(__file__).parent
V33=ROOT/"outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv"
BUY_COST=.008
SELL_COST=.008
PARAMS={
 "IMMEDIATE":(0.,0.,0,False,"immediate"),
 "TRAIL1_MOM1":(.01,-.01,0,False,"trail"),
 "TRAIL2_MOM1":(.02,-.01,0,False,"trail"),
 "TRAIL2_MOM15":(.02,-.015,0,False,"trail"),
 "TRAIL3_MOM1":(.03,-.01,0,False,"trail"),
 "TRAIL2_MOM1_EMA":(.02,-.01,0,True,"trail"),
 "TRAIL1_VOLCUSUM":(.01,-.008,3,True,"cusum"),
 "TRAIL2_VOLCUSUM":(.02,-.008,3,True,"cusum"),
 "TRAIL1_EMA_BREAK":(.01,-.008,0,True,"break"),
 "TRAIL2_EMA_BREAK":(.02,-.008,0,True,"break"),
 "MOM15_ONLY":(0,-.015,0,True,"trail"),
 "HOLD":(0,0,0,False,"hold"),
}
def get_bars():
 import psycopg
 uri=os.getenv("NEON_DATABASE_URL","").strip()
 if not uri:raise RuntimeError("MISSING_NEON_DATABASE_URL")
 sql="""SELECT bar_start_utc,close_price
 FROM public.gold_research_histdata_xau15m_candidate
 WHERE bar_start_utc>='2024-01-01' AND bar_start_utc<'2026-10-01'
 ORDER BY bar_start_utc"""
 with psycopg.connect(uri,connect_timeout=25,
                      options="-c default_transaction_read_only=on") as con:
  with con.cursor() as cur:
   cur.execute(sql)
   a=[(ts, float(p)) for ts,p in cur]
 if len(a)<60000:raise ValueError("HISTDATA_15M_TOO_FEW_ROWS")
 for i in range(1,len(a)):
  if a[i][0]<=a[i-1][0]:raise ValueError("NONMONOTONIC_INTRA")
 return a

def get_2026_diary():
 with V33.open(encoding="utf8",newline="") as f:
  rows={}
  for r in csv.DictReader(f):
   if r["scenario"]!="AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES":continue
   day=date.fromisoformat(r["date"])
   if day.year!=2026:continue
   rows[day]=bool(r["model_v22_review"]=="True")
 return rows

def enhance(bars):
 # 15m observation can be used only at or after its timestamp.
 # EMA and CUSUM are computed strictly forward, never filled backwards.
 close=[]
 ema=None
 last=None
 cusum=0.
 out=[]
 for i,(ts,p) in enumerate(bars):
  close.append(p)
  ema=p if ema is None else p*(2/97)+ema*(95/97)
  # For 4h momentum, count 16 historical 15m steps only if continuous
  r4=(p/close[i-16]-1 if i>=16
       and ts-bars[i-16][0]==timedelta(hours=4) else None)
  hourly=100*r4 if r4 is not None else None
  # drift scale computed from strictly previous 96 increments (no future).
  prev_ret=[math.log(close[j]/close[j-1]) for j in range(max(i-95,1),i+1)
            if bars[j][0]-bars[j-1][0]==timedelta(minutes=15)]
  if len(prev_ret)>=36:
   mu=sum(prev_ret)/len(prev_ret)
   sigma=math.sqrt(sum((x-mu)**2 for x in prev_ret)/len(prev_ret))
  else:sigma=0
  # one-sided volatility-aware downside CUSUM (only sigma known as of now)
  if i>=1 and ts-bars[i-1][0]==timedelta(minutes=15) and sigma>0:
   z=math.log(p/close[i-1])/sigma
   cusum=min(0.,cusum+z+.25)
  else:cusum=0.
  prior24=max(close[max(0,i-96):i]) if i>0 else p
  priorlow24=min(close[max(0,i-96):i]) if i>0 else p
  out.append({"ts":ts,"date":ts.date(),"p":p,"ema":ema,
              "r4":r4,"cusum":cusum,"prior24high":prior24,
              "prior24low":priorlow,"sigma":sigma,
              "usable4h":r4 is not None})
 return out

def synthetic_diary(rows):
 # 2024–25 proxy WITHOUT 2026 data, used solely to choose parameters.
 # One signal at D close when previous five complete weekdays' price
 # falls more than 2% or last 4-hour drop at D is severe.
 days={}
 for x in rows:days[x["date"]]=x
 dates=[d for d in sorted(days) if d.weekday()<5]
 risk={}
 for i,d in enumerate(dates):
  if i<10:continue
  p=days[d]["p"]
  ret5=p/days[dates[i-5]]["p"]-1
  worst=max(0, -min((r["r4"] for r in rows
          if r["date"]==d and r["r4"] is not None),default=0))
  # This proxy is an untrained stress alert, not V22; never conflate.
  risk[d]=(ret5<=-.02 or worst>=.016)
 return risk

def bar_session(diaries,year,rows):
 # Signals for date D are available ONLY from the FIRST NEXT calendar date bar.
 # No same-day use, and weekends are excluded from waiting day count.
 dates=sorted(d for d in diaries if d.year==year and d.weekday()<5)
 signal=sorted(d for d in dates if diaries[d])
 return signal

def simulate(data,diary,param,year):
 max_drop,neg4,cusum_min,require_ema,kind=param
 candles=[r for r in data if r["ts"].year==year]
 if len(candles)<15000:raise ValueError("MISSING_YEAR_BARS_"+str(year))
 signals=bar_session(diary,year,candles)
 signal_set=set(signals)
 # Starting position: $100, first executable bar costs 0.8% upfront.
 gold=100/(candles[0]["p"]*(1+BUY_COST))
 cash=0.;holding=True;fee=100-100/(1+BUY_COST)
 watch=False;high=None;last_warn=None;last_sell_day=None
 pending=None; sell_records=[];buy_records=[]; daily_eq=[]
 peak_equity=100.;mdd=0.;recent_signal=[]
 for i,r in enumerate(candles):
  p=r["p"];day=r["date"]
  # Execute pending signal at next 15-minute bar, never same close
  if pending and i>pending["i"]:
   # Skip if next bar after large market closure > 6h (execution impossible
   # at next close; wait for next actual candidate bar, do not fake fills).
   if pending["type"]=="SELL" and holding:
    cash=gold*p*(1-SELL_COST);fee+=gold*p*SELL_COST
    gold=0.;holding=False;watch=False;high=None
    last_sell_day=day
    sell_records.append({"day":str(day),"time":str(r["ts"]),
                         "px":round(p,3),"reason":pending["name"],
                         "watchStart":pending["watchStart"]})
   elif pending["type"]=="BUY" and not holding:
    gold=cash/(p*(1+BUY_COST));fee+=cash*BUY_COST/(1+BUY_COST)
    cash=0.;holding=True;watch=False;high=None
    buy_records.append({"day":str(day),"time":str(r["ts"]),"px":round(p,3)})
   pending=None
  # A signal at D is known when UTC date > D, never on D itself.
  if i==0 or candles[i-1]["date"]!=day:
   # Introduce all signals from the LAST completed date only.
   # Weekend news/data not assumed.
   last_completed=candles[i-1]["date"] if i else None
   if last_completed and last_completed in signal_set:
    last_warn=last_completed
   recent_signal=[s for s in recent_signal if (day-s).days<=21]
   if last_completed and last_completed in signal_set:
    recent_signal.append(last_completed)
  # Hold a WATCH state for up to 10 calendar days from most recent V22.
  risk=(last_warn is not None and 0<(day-last_warn).days<=12)
  if holding:
   if risk and not watch:
    watch=True;high=p;watch_start=str(day)
   if watch and risk:
    high=max(high,p)
   if watch and not risk:
    watch=False;high=None
   if watch and kind!="hold" and not pending and r["r4"] is not None:
    dd=(p/high-1) if high else 0
    moment=r["r4"]<=neg4
    trend=(p<r["ema"]) if require_ema else True
    if kind=="immediate":trigger=True
    elif kind=="trail":trigger=(dd<=-max_drop and moment and trend)
    elif kind=="cusum":trigger=(dd<=-max_drop and moment and trend
                              and r["cusum"]<=-cusum_min)
    elif kind=="break":trigger=(dd<=-max_drop and moment and trend
                               and p<r["prior24low"])
    else:raise ValueError("BAD_KIND")
    if trigger and i+1<len(candles):
     pending={"type":"SELL","i":i,"name":kind,"watchStart":watch_start}
   # Immediate is triggered as soon as watch starts even when r4 unavailable
   if watch and kind=="immediate" and not pending and i+1<len(candles):
    pending={"type":"SELL","i":i,"name":kind,"watchStart":watch_start}
  elif not pending:
   # Common re-entry for EVERY sell strategy; settle out of risk first.
   # No signal in preceding 4 completed weekday sessions and 3 calendar
   # days in cash, plus positive 4h momentum and reclaim above 24h EMA.
   risk_quiet=all((day-s).days>6 for s in recent_signal)
   days_cash=(day-last_sell_day).days if last_sell_day else 999
   if risk_quiet and days_cash>=3 and r["r4"] is not None and r["r4"]>.0025 and p>r["ema"] and p>r["prior24high"]*.996:
    if i+1<len(candles):pending={"type":"BUY","i":i,"name":"reenter"}
  eq=gold*p*(1-SELL_COST) if holding else cash
  peak_equity=max(peak_equity,eq);mdd=min(mdd,eq/peak_equity-1)
  if i==len(candles)-1 or candles[i+1]["date"]!=day:
   daily_eq.append([str(day),round(eq,5),int(holding)])
 end=candles[-1]["p"];net=gold*end*(1-SELL_COST) if holding else cash
 return {"year":year,"method":kind,"netUSD":round(net,4),
         "returnPct":round(net-100,4),"maxDDPct":round(mdd*100,3),
         "sells":len(sell_records),"buys":len(buy_records),
         "feeUSDEstimate":round(fee,3),
         "entryPx":round(candles[0]["p"],2),"lastPx":round(end,2),
         "finalHolding":holding,
         "sellRecords":sell_records,"buyRecords":buy_records,
         "dailyEquity":daily_eq}

def pick_model(validation):
 # Optimize on 2025 ONLY, freeze before testing 2026.
 # Strong preference for net final value and risk: 2025 worst DD penalty.
 # Never select a model using 2026.
 scored=[]
 for k,v in validation.items():
  if k in ("IMMEDIATE","HOLD"):continue
  score=v["netUSD"] + .22*v["maxDDPct"] - .35*v["sells"]
  scored.append((score,k))
 return max(scored)[1], sorted(scored,reverse=True)

def run():
 raw=get_bars()
 byyear={y:enhance([x for x in raw if x[0].year==y]) for y in (2024,2025,2026)}
 di2024=synthetic_diary(byyear[2024])
 di2025=synthetic_diary(byyear[2025])
 di2026=get_2026_diary()
 diaries={2024:di2024,2025:di2025,2026:di2026}
 results={}
 for year in (2024,2025,2026):
  results[year]={}
  for name,p in PARAMS.items():
   results[year][name]=simulate(byyear[year],diaries[year],p,year)
 selected,ranking=pick_model(results[2025])
 eval_summary={year:{name:{k:v for k,v in res.items()
                if k not in ("sellRecords","buyRecords","dailyEquity")}
          for name,res in group.items()} for year,group in results.items()}
 winner=results[2026][selected]
 return {
  "schema":"V41_V22_WATCH_VOLATILITY_SEQUENCE_EXIT_REENTRY_HISTORICAL_V1",
  "status":"RESEARCH_ONLY_BACKFILLED_NOT_PIT",
  "source":"HistData_15m_noncanonical_research_candidate_XAUUSD",
  "pricing":"100USD_start_0.8pct_buy_0.8pct_sell_next_15m_close",
  "training_proxy":"2024_2025_daily_5day_drop2pct_or_worst4h_drop1.6pct_NOT_V22",
  "selectionYear":2025,"evaluationYear":2026,
  "2026V22Reference":"V33 retrospective original V22 diary date D applied after day D",
  "evaluationThrough":"2026-10-01 04:45UTC",
  "no2026BasedParameterSelection":True,
  "sameSourceDailyV22PriceCertified":False,
  "firstprintCertified":False,"realExecutionCertified":False,
  "modelPromotion":False,"neonWrites":False,"ordersCreated":False,
  "chosenOn2025":selected,
  "2025CandidateRanking":ranking,
  "summary":eval_summary,
  "selected2026Trades":{"sells":winner["sellRecords"],"buys":winner["buyRecords"]},
  "reference2026Trades":{"sells":results[2026]["IMMEDIATE"]["sellRecords"],
                         "buys":results[2026]["IMMEDIATE"]["buyRecords"]},
  "2026DailyEquity":{
      "HOLD":results[2026]["HOLD"]["dailyEquity"],
      "IMMEDIATE":results[2026]["IMMEDIATE"]["dailyEquity"],
      "SELECTED":winner["dailyEquity"]},
  "limitations":[
    "2024-25 synthetic WATCH is NOT original V22 and is selection-domain shift",
    "2026 outcome has already been inspected during prior research, not blind",
    "HistData candidate is retrospective, not execution-quality bid/ask quote",
    "V22 issue time cannot be proved PIT; next UTC date is conservative proxy",
    "Trading fee model is stylized and excludes slippage/tax/overnight spread",
    "Next 15-minute close may not be fillable; portfolio metrics are research-only",
    "2026 test ends Oct1 because HistData intraday does, NOT Oct23",
    "2024-25 data may have different source transformations from 2026"
  ]
 }

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--out",default="gold-v41-risk-to-exit-cost-sensitive-replay.json")
 args=p.parse_args()
 r=run()
 Path(args.out).write_text(json.dumps(r,ensure_ascii=False,default=str,indent=2)+"\n",encoding="utf8")
 print(json.dumps({k:v for k,v in r.items() if k not in ("2026DailyEquity",)},ensure_ascii=False,default=str,indent=2))
 if os.environ.get("GITHUB_STEP_SUMMARY"):
  with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
   f.write("## V41 exit timing study: **research only**\n\n")
   f.write(f"Selected using 2025 only: **{r['chosenOn2025']}**\n\n")
   f.write("| Method | 2025 proxy final USD | 2026 final USD | 2026 max DD | 2026 exits |\n")
   f.write("|---|---:|---:|---:|---:|\n")
   for k,v in r["summary"][2026].items():
    f.write(f"| {k} | {r['summary'][2025][k]['netUSD']} | "
            f"{v['netUSD']} | {v['maxDDPct']} | {v['sells']} |\n")
   f.write("\nNo promotion, no live execution/PIT proof.\n")
if __name__=="__main__":main()
