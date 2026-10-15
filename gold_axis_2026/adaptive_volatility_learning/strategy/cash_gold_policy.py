"""CASH->GOLD->CASH event-aware intramonth strategy research (stdlib only).

NO short/leverage; start USD 100 cash; 0.8% fee EACH side; spot bank spread
NOT INCLUDED (optimistic). Ex-ante rule selection: 2023/24; validation
2025; chronological Jan 2026. Checkpoint signal uses only closed M15 bars,
next M15 open for fills. Macro calendar is only a scheduled event RISK GATE;
12 OLAY/OGREN mechanisms remain unknown until independently verified.
"""
from __future__ import annotations
import argparse,csv,json,itertools,math
from datetime import datetime,timedelta,timezone
from pathlib import Path

FEE=0.008
START=100.0
UTC=timezone.utc
def parse(s):
    v=datetime.fromisoformat(s.replace("Z","+00:00"))
    if v.tzinfo is None: raise ValueError("Timezone required")
    return v.astimezone(UTC)
def num(x):
    try: return float(x)
    except (ValueError,TypeError): return float('nan')

def checkpoints(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        raw=list(csv.DictReader(f))
    records=[]
    for r in raw:
        v={k:num(r.get(k)) for k in ("close","next_open","r4h","r1d","r3d","r5d","dd3d","range1d","age1_sec","age3_sec")}
        if any(not math.isfinite(x) for x in v.values()): continue
        if r["next_contig"]!="1" or v["age1_sec"]>6*86400 or v["age3_sec"]>16*86400:
            continue
        t=parse(r["bar_start_utc"])+timedelta(minutes=15)
        records.append(dict(t=t,**v))
    records.sort(key=lambda x:x["t"])
    return records
def macro_events(path):
    with open(path,encoding="utf-8-sig",newline="") as f:
        return sorted([dict(t=parse(r["event_utc"]),id=r["event_id"],
                     kind=r["kind"],source=r["source"]) for r in csv.DictReader(f)],
                      key=lambda r:r["t"])

def context(events,t):
    """Planned macro event clock; no use of unknown surprise or future outcome."""
    before=[x for x in events if t<=x["t"]<=t+timedelta(hours=6)]
    after=[x for x in events if x["t"]<=t<x["t"]+timedelta(hours=3)]
    return dict(near=bool(before or after),
                ids=[x["id"] for x in before+after])

def simulate(rows,events,pars,year=None,start_at=None,end_at=None):
    if year is not None:
        rows=[r for r in rows if (r["t"]+timedelta(hours=3)).year==year]
        # End-UTC near Jan1 can map to next/previous local calendar day.
    else:
        rows=[r for r in rows if (start_at is None or r["t"]>=start_at)
                                and (end_at is None or r["t"]<=end_at)]
    if not rows:return dict(final=START,net_pct=0,round_trips=0,
                           buyhold_pct=0,max_dd_pct=0,trades=[],daily=[],invested_checkpoints=0,n=0)
    cash=START;units=0.0;peak=0.0;peak_equity=START;max_dd=0.0
    last_exit=None;entries=0;exits=0;invested=0
    trades=[];daily={}
    for idx,r in enumerate(rows):
        t=r["t"];p=r["next_open"];c=r["close"]
        old_pos=units>0
        if old_pos:
            peak=max(peak,c)
        ex=context(events,t) if pars.get("calendar_gate") else {"near":False,"ids":[]}
        # Signal must be formed at t, and fill at next bar's start=t.
        # Historical input has verified next-contiguous full bar; open is the
        # first available modelled fill, not executable bank ASK/BID.
        why=None
        if units>0:
            trail_dd=100*(c/peak-1)
            if trail_dd<=-pars["trail"]:
                why="SELL_TRAILING_DRAW_DOWN"
            elif r["r4h"]<=-2.0:
                why="SELL_FAST_SHOCK"
            elif r["r1d"]<=pars["sell_fast"] and r["r4h"]<0:
                why="SELL_TREND_BREAK"
            elif r["r3d"]<-2.0 and r["r4h"]<-.5:
                why="SELL_SLOW_BREAK"
            if why:
                cash=units*p*(1-FEE);units=0.;last_exit=t;exits+=1;peak=0.
                trades.append(dict(at_tr=(t+timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                    side="SELL",executed_price=round(p,3),
                    reason=why,macro_gate_ids="|".join(ex["ids"]),
                    cash_after=round(cash,6)))
        else:
            cooled=last_exit is not None and t-last_exit>=timedelta(hours=pars["cooldown_h"])
            if (last_exit is None or cooled) and not ex["near"] and (
                r["r1d"]>=pars["buy_1d"] and r["r3d"]>=pars["buy_3d"]
                and r["r4h"]>=-0.25 and r["dd3d"]>=-3.5
                and r["range1d"]<=pars["max_1d_range"]):
                units=cash*(1-FEE)/p;cash=0.;peak=p;entries+=1
                why="BUY_CONFIRMED_MULTI_SESSION_TREND"
                trades.append(dict(at_tr=(t+timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
                    side="BUY",executed_price=round(p,3),reason=why,
                    macro_gate_ids="|".join(ex["ids"]),cash_after=0.))
        if units>0:invested+=1
        liquid=cash if units==0 else units*c*(1-FEE)
        peak_equity=max(peak_equity,liquid)
        max_dd=max(max_dd,100*(1-liquid/peak_equity))
        day=(t+timedelta(hours=3)).strftime("%Y-%m-%d")
        daily[day]=dict(day=day,at_tr=(t+timedelta(hours=3)).strftime("%H:%M"),
                        position="GOLD" if units>0 else "CASH",
                        liquidation_equity=round(liquid,4),
                        recent_r1d=round(r["r1d"],3),recent_r3d=round(r["r3d"],3))
    final_price=rows[-1]["close"]
    if units>0:
        cash=units*final_price*(1-FEE);units=0.;exits+=1
        trades.append(dict(at_tr=(rows[-1]["t"]+timedelta(hours=3)).strftime("%Y-%m-%d %H:%M"),
          side="SELL",executed_price=round(final_price,3),
          reason="MANDATORY_PERIOD_END_LIQUIDATION",macro_gate_ids="",cash_after=round(cash,6)))
    # Comparator: buy on first model checkpoint, sell at last checkpoint.
    buyhold=START*(1-FEE)/rows[0]["next_open"]*final_price*(1-FEE)
    return dict(final=round(cash,5),net_pct=round(cash-START,5),
      buyhold_final=round(buyhold,5),buyhold_pct=round(buyhold-START,5),
      round_trips=exits,max_dd_pct=round(max_dd,3),trades=trades,
      daily=list(daily.values()),invested_checkpoints=invested,n=len(rows),
      first_tr=(rows[0]["t"]+timedelta(hours=3)).isoformat(),
      last_tr=(rows[-1]["t"]+timedelta(hours=3)).isoformat(),
      first_gold_quote=rows[0]["next_open"],last_gold_quote=final_price)

def selections(rows,events):
    """Choose only on years 2023 and 2024; never inspect Jan 2026."""
    entry=(.3,.6,1.0)
    slower=(-.5,0.,.5)
    fast_exit=(-.5,-1.2,-2.)
    trailing=(2.,3.5,5.)
    vol=(4.,7.)
    results=[]
    for e,s,ex,tr,mr,gate in itertools.product(entry,slower,fast_exit,trailing,vol,(False,True)):
        p=dict(buy_1d=e,buy_3d=s,sell_fast=ex,trail=tr,max_1d_range=mr,
               cooldown_h=12,calendar_gate=gate)
        a=simulate(rows,events,p,year=2023);b=simulate(rows,events,p,year=2024)
        if not a["round_trips"] or not b["round_trips"]:continue
        # Penalize poor worst year, drawdowns and excessive round trips.
        returns=[a["net_pct"],b["net_pct"]]
        score=(.6*min(returns)+.4*(sum(returns)/2)
              -.22*(a["max_dd_pct"]+b["max_dd_pct"])/2
              -.12*(a["round_trips"]+b["round_trips"]))
        results.append((round(score,5),p,a,b))
    results.sort(key=lambda x:(-x[0],x[2]["round_trips"]+x[3]["round_trips"],
                               json.dumps(x[1],sort_keys=True)))
    return results

def run(data,calendar):
    train=selections(data,calendar)
    if not train:raise RuntimeError("No strategy had trades in both training years")
    score,p,a,b=train[0]
    hold=simulate(data,calendar,p,year=2025)
    jan=simulate(data,calendar,p,start_at=parse("2026-01-01T00:00:00+03:00"),
                 end_at=parse("2026-02-01T00:00:00+03:00"))
    alternate_calendar=dict(p,calendar_gate=not p["calendar_gate"])
    jan_alt_gate=simulate(data,calendar,alternate_calendar,
        start_at=parse("2026-01-01T00:00:00+03:00"),
        end_at=parse("2026-02-01T00:00:00+03:00"))
    return dict(name="CASH_GOLD_POLICY_V1",status="RESEARCH_NOT_TRADABLE",
      data="NEON historical XAU15M derived 3-hour snapshots",
      decision="3h signal, buy/sell at next 15m open; no fixed holding horizon",
      costs="0.8pct each side, extra bank bid/ask spread unavailable",
      training_years=[2023,2024],selection_score=score,selected=p,
      training={2023:a,2024:b},validation_2025=hold,
      january_2026=jan,january_toggled_event_calendar=jan_alt_gate,
      top5=[dict(score=s,params=q,train2023=m["net_pct"],train2024=n["net_pct"])
            for s,q,m,n in train[:5]],
      warnings=[
        "Technical parameters selected on 2023-24; January dates and price path have been previously studied and are not fully blind.",
        "BLS/Fed date calendar uses historical schedule retrospectively; year-2023-25 release calendar vintage not independently authenticated.",
        "OLAY02/OGREN03 macro layer is an event timing entry veto only; full economic DNA ORG01-12 attribution and firstprint is NOT VALIDATED.",
        "Trading at next-bar XAU spot opening quote is optimistic; no actual bank BID/ASK, slippage, spread, FX, taxes or latency.",
        "All equity return amounts are USD/XAU denominated, not Turkish gram-gold/bank TRY returns.",
        "At end of the period, any gold is hypothetically liquidated at the last sampled checkpoint, not necessarily final actual bank trade.",
        "No leverage, no shorts, no partial position; 100 USD fully in cash or spot XAU.",
        "This is not a calibrated actionable live portfolio strategy."])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True)
    ap.add_argument("--events",required=True)
    ap.add_argument("--output",default=None)
    args=ap.parse_args()
    result=run(checkpoints(args.data),macro_events(args.events))
    compact=dict(selected=result["selected"],train_score=result["selection_score"],
                 train={y:{k:v for k,v in z.items() if k not in ("trades","daily")}
                        for y,z in result["training"].items()},
                 validation={k:v for k,v in result["validation_2025"].items()
                         if k not in ("trades","daily")},
                 january={k:v for k,v in result["january_2026"].items()
                          if k not in ("daily",)},
                 january_toggled_calendar={k:v for k,v in result["january_toggled_event_calendar"].items()
                          if k not in ("daily","trades")},
                 top5=result["top5"])
    print("STRATEGY_RESULT_BEGIN")
    print(json.dumps(compact,ensure_ascii=False,indent=2))
    print("STRATEGY_RESULT_END")
    if args.output:
        Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__": main()
