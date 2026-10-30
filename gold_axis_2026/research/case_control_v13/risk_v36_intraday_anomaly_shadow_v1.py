#!/usr/bin/env python3
"""READ-ONLY 15m XAU intraday early-warning feasibility, not live signals.

Frozen diagnostic thresholds are learned ONLY from HistData 2024-2025.
2026 is evaluated once; no 2026 tuning, no BASE14/V22 replacement, no trades.
Bar timestamps are historical reconstructions, NOT source firstprint proof.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

SOURCE_CLASS = "HISTDATA_XAU_15M_RETRIEVED_RESEARCH_NOT_PIT"
TRAIN_START = date(2024, 1, 1)
TRAIN_END = date(2025, 12, 31)
EVAL_START = date(2026, 1, 1)
EVAL_END = date(2026, 9, 30)
EVENT_STARTS = {
    "MAY_FOUR_PCT": date(2026, 5, 13),
    "JUNE_FIRST_EIGHT_PCT": date(2026, 6, 4),
    "SEPT_FOUR_PCT": date(2026, 9, 21),
}

def percentile_linear(vals, fraction):
    a = sorted(float(v) for v in vals if v is not None and math.isfinite(float(v)))
    if not a:
        raise ValueError("EMPTY_TRAINING_DISTRIBUTION")
    p = (len(a) - 1) * fraction
    i = int(p)
    return a[i] + (a[min(i + 1, len(a)-1)] - a[i]) * (p - i)

def daily_features(bars):
    """Only current/past bars are accessed for any price-return signal."""
    daily = defaultdict(lambda: {"bars": 0, "worst1h": None,
                                  "worst4h": None, "last": None,
                                  "first1h_at": None, "first4h_at": None})
    history = []
    prev = None
    for ts,price in bars:
        if ts.tzinfo is None or ts.utcoffset() != timedelta(0):
            raise ValueError("BAR_TIMESTAMP_MUST_BE_UTC")
        if prev is not None and ts <= prev:
            raise ValueError("BARS_NOT_STRICTLY_INCREASING")
        if not math.isfinite(price) or price <= 0:
            raise ValueError("INVALID_PRICE")
        d = daily[ts.date()]
        d["bars"] += 1
        d["last"] = float(price)
        for n,key,first_key in ((4,"worst1h","first1h_at"),(16,"worst4h","first4h_at")):
            if len(history) >= n and ts-history[-n][0] == timedelta(minutes=15*n):
                old=history[-n][1]
                pct=100*(price/old-1)
                if d[key] is None or pct<d[key]:
                    d[key]=pct
                    d[first_key]=ts.isoformat()
        history.append((ts,float(price)))
        if len(history)>16:
            history.pop(0)
        prev=ts
    return {d:v for d,v in daily.items() if v["bars"]>=45}

def event_window(daily, start, cut1, cut4):
    eligible=sorted(d for d in daily if d<start and d.year==start.year)
    last10=eligible[-10:]
    hits=[]
    for d in last10:
        x=daily[d]
        if x["worst1h"] is not None and x["worst1h"]<=cut1:
            hits.append({"date":d.isoformat(),"kind":"1H","worstPct":round(x["worst1h"],4),
                         "researchBarTimestamp":x["first1h_at"]})
        if x["worst4h"] is not None and x["worst4h"]<=cut4:
            hits.append({"date":d.isoformat(),"kind":"4H","worstPct":round(x["worst4h"],4),
                         "researchBarTimestamp":x["first4h_at"]})
    return {"start":start.isoformat(),"prior10ObservedDates":list(map(str,last10)),
            "preStartAnomalies":sorted(hits,key=lambda x:(x["date"],x["kind"])),
            "anyPreStartCandidate":bool(hits)}

def evaluate(daily):
    train={d:x for d,x in daily.items() if TRAIN_START<=d<=TRAIN_END}
    evalset={d:x for d,x in daily.items() if EVAL_START<=d<=EVAL_END}
    if len(train)<450 or len(evalset)<150:
        raise ValueError("INSUFFICIENT_TRAIN_OR_EVALUATION_DAYS")
    cut1=percentile_linear((x["worst1h"] for x in train.values()),.05)
    cut4=percentile_linear((x["worst4h"] for x in train.values()),.05)
    evaldates=sorted(evalset)
    scored=[]
    for i,d in enumerate(evaldates):
        if i+5>=len(evaldates):
            continue
        future=evaldates[i+1:i+6]
        if (future[-1]-d).days>12:
            continue
        x=evalset[d]
        future_min=min(evalset[j]["last"] for j in future)
        future4=(100*(future_min/x["last"]-1)<=-4)
        one=x["worst1h"] is not None and x["worst1h"]<=cut1
        four=x["worst4h"] is not None and x["worst4h"]<=cut4
        # Outcome appears here ONLY in separate retrospective score calculation.
        scored.append({"date":d,"outcome":future4,"1h":one,"4h":four,"either":one or four})
    truth=sum(r["outcome"] for r in scored)
    checks={}
    for k in ("1h","4h","either"):
        marked=[r for r in scored if r[k]]
        hits=sum(r["outcome"] for r in marked)
        checks[k]={"alertDays":len(marked),"followedByFourPctWithinFiveSessions":hits,
                   "notFollowedByFourPct":len(marked)-hits,
                   "labeledDaysNotCovered":truth-hits}
    return {
        "schema":"XAU_15M_INTRADAY_RESEARCH_SHADOW_V1",
        "trainPeriod":"2024-2025_HISTDATA_SOURCE_ONLY",
        "evaluationPeriod":"2026_JAN_SEP_HISTDATA_SOURCE_ONLY",
        "target":"next_5_price_sessions_min_daily_close_from_origin_close_drop_4pct",
        "thresholds":{"worst1hPctTrain5th":round(cut1,5),
                      "worst4hPctTrain5th":round(cut4,5)},
        "sample":{"trainDays":len(train),"evaluationDays":len(evalset),
                  "maturedEvaluationDays":len(scored),"futureFourPctDays":truth},
        "warningChecks":checks,
        "events":{name:event_window(evalset,start,cut1,cut4) for name,start in EVENT_STARTS.items()},
        "evidence":SOURCE_CLASS,
        "barAvailableEstimate":"bar_start_plus_15_minutes_NOT_FIRSTPRINT",
        "firstprintCertified":False,"modelRiskEngineChanged":False,
        "productionSignal":False,"promotionApproved":False,"neonWrites":False,
        "tradingActions":False,"not2026Blind":True,
        "notEquivalentToIndependentEconomicEvents":True,
    }

def load_neon():
    import psycopg
    uri=os.getenv("NEON_DATABASE_URL","").strip()
    if not uri: raise RuntimeError("MISSING_NEON_DATABASE_URL")
    with psycopg.connect(uri,connect_timeout=15,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as c:
            c.execute("""
             SELECT bar_start_utc,close_price
             FROM public.gold_research_histdata_xau15m_candidate
             WHERE bar_start_utc >= '2024-01-01'
               AND bar_start_utc < '2026-10-01'
             ORDER BY bar_start_utc
            """)
            for ts,px in c:
                yield ts, float(px)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-intraday-research-shadow-v1.json")
    args=p.parse_args()
    daily=daily_features(load_neon())
    result=evaluate(daily)
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",
                              encoding="utf8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf8") as f:
            f.write("## XAU 15m, historical anomaly research only\n\n")
            f.write(f"Training-only 1h/4h thresholds: {result['thresholds']}\n\n")
            f.write("This job **does not** certify firstprint or issue live alerts.\n")
if __name__=="__main__":
    main()
