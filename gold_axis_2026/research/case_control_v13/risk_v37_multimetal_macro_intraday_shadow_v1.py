#!/usr/bin/env python3
"""V37: four-metal daily and macro contextual filter of original V22 + XAU 4h.

RESEARCH_ONLY / NO LIVE ISSUANCE / NO NEON WRITES / NO TRADING.
Thresholds fixed from 2024-2025; evaluation 2026 Jan-Sep. 2026 is NOT
untouched/blind because event labels were previously investigated.
Historical StakTrakr (including 2026-10-30 backfill) cannot certify firstprint.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from gold_axis_2026.research.case_control_v13.risk_v36_intraday_anomaly_shadow_v1 import (
    daily_features, percentile_linear
)

PARENT = Path(__file__).parent
V33 = PARENT / "outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv"
METALS = ("AG", "PT", "PD")
TYPES = ("AU", "AG", "PT", "PD")
TRAIN_LAST = date(2025, 12, 31)
TEST_LAST = date(2026, 9, 30)
SOURCE = "HISTORICAL_BACKFILL_NOT_FIRSTPRINT"

def _ret(v: float | None, prev: float | None) -> float | None:
    if v is None or prev is None or prev <= 0:
        return None
    return 100*(v/prev-1)

def prep_metal_rows(raw: list[dict]) -> list[dict]:
    a = sorted(raw, key=lambda x:x["dt"])
    if len({x["dt"] for x in a}) != len(a):
        raise ValueError("DUPLICATE_FOUR_METAL_DATE")
    for i,r in enumerate(a):
        if any(r.get(s) is None or r[s]<=0 for s in TYPES):
            raise ValueError("MISSING_FOUR_METAL_PRICE")
        for m in TYPES:
            r[m+"1"] = _ret(r[m],a[i-1][m]) if i>=1 else None
            r[m+"5"] = _ret(r[m],a[i-5][m]) if i>=5 else None
        prev = a[i-1] if i>=1 else None
        r["gvz1"] = (r["gvz"]-prev["gvz"]
                     if prev and r.get("gvz") is not None
                     and prev.get("gvz") is not None else None)
        r["rate1"] = (r["rate"]-prev["rate"]
                      if prev and r.get("rate") is not None
                      and prev.get("rate") is not None else None)
    return a

def fixed_thresholds(metals: list[dict], bars_by_date: dict) -> dict:
    train=[r for r in metals if r["dt"]<=TRAIN_LAST]
    prior_bars=[v for d,v in bars_by_date.items() if d<=TRAIN_LAST]
    if len(train)<450 or len(prior_bars)<450:
        raise ValueError("TRAIN_COVERAGE_TOO_LOW")
    keys=[m+period for m in METALS for period in ("1","5")]
    keys+=["gvz1","rate1","gvz"]
    q={}
    for k in keys:
        eligible=[r[k] for r in train if r.get(k) is not None]
        if len(eligible)<300:
            raise ValueError("NO_COMPLETE_TRAINING_FEATURE_"+k)
        q[k]=percentile_linear(eligible, .90 if k in ("gvz1","rate1","gvz") else .10)
    q["worst4h"]=percentile_linear(
        [v["worst4h"] for v in prior_bars if v.get("worst4h") is not None], .05
    )
    return q

def causal_context(rows: list[dict], i: int, q: dict) -> dict:
    """At date D, 3-metal stress ends no later than D-1.
    GVZ/10Y context ends no later than D-2 (publication-time conservatism).
    """
    prior=rows[max(0,i-4):i]
    prev=rows[i-1] if i>=1 else None
    prev2=rows[i-2] if i>=2 else None
    daily=any(
        z.get(m+"1") is not None and z[m+"1"]<=q[m+"1"]
        for z in prior for m in METALS)
    five=any(
        z.get(m+"5") is not None and z[m+"5"]<=q[m+"5"]
        for z in prior for m in METALS)
    strong_metal=daily or five
    macro=bool(prev2 and (
        (prev2.get("gvz") is not None and prev2["gvz"]>=q["gvz"])
        or (prev2.get("gvz1") is not None and prev2["gvz1"]>=q["gvz1"])
        or (prev2.get("rate1") is not None and prev2["rate1"]>=q["rate1"])
    ))
    return {
        "metalDailyTailInLast4":daily,
        "metalFiveDayTailInLast4":five,
        "metalContext":strong_metal,
        "macroContext":macro,
        "contextComplete":bool(prev and prev2 and
             all(z.get(m+"1") is not None for z in prior for m in METALS)),
        "lastMetalDate":str(prev["dt"]) if prev else None,
        "lastMacroDate":str(prev2["dt"]) if prev2 else None,
    }

def flags(v22: bool, shock: bool, ctx: dict) -> dict:
    # Frozen formulations: NO threshold is chosen by observing 2026 labels.
    return {
        "V22":bool(v22),
        "V22_OR_4H":bool(v22 or shock),
        "V22_OR_4H_METALS":bool(v22 or (shock and ctx["metalContext"])),
        "V22_OR_4H_MACRO":bool(v22 or (shock and ctx["macroContext"])),
        "V22_OR_4H_METALS_OR_MACRO":bool(
            v22 or (shock and (ctx["metalContext"] or ctx["macroContext"]))
        ),
    }

def read_inputs():
    import psycopg
    uri=os.getenv("NEON_DATABASE_URL","").strip()
    if not uri:
        raise RuntimeError("MISSING_NEON_DATABASE_URL")
    with psycopg.connect(uri,connect_timeout=15,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as c:
            c.execute("""
              WITH raw AS (
                SELECT observation_ts::date dt,substring(series_id,2,2) metal,value p
                FROM public.observations
                WHERE series_id IN (
                   'XAU_STAKTRAKR_RESEARCH_DAILY_R1',
                   'XAG_STAKTRAKR_RESEARCH_DAILY_R1',
                   'XPT_STAKTRAKR_RESEARCH_DAILY_R1',
                   'XPD_STAKTRAKR_RESEARCH_DAILY_R1')
                 AND observation_ts>='2024-01-01' AND observation_ts<'2026-01-01'
                UNION ALL
                SELECT price_date,metal,spot_usd_oz::float8
                FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
                WHERE price_date>='2026-01-01' AND price_date<'2026-10-01'
              )
              SELECT dt,
                max(p) FILTER(WHERE metal='AU'),
                max(p) FILTER(WHERE metal='AG'),
                max(p) FILTER(WHERE metal='PT'),
                max(p) FILTER(WHERE metal='PD')
              FROM raw
              WHERE extract(isodow FROM dt) BETWEEN 1 AND 5
              GROUP BY dt ORDER BY dt
            """)
            metals=[
                {"dt":r[0],"AU":r[1],"AG":r[2],"PT":r[3],"PD":r[4]}
                for r in c
            ]
            c.execute("""
              SELECT DISTINCT ON (observation_ts::date,series_id)
                observation_ts::date,series_id,value
              FROM public.observations WHERE
              (series_id='GVZ_CBOE_FRED_MIRROR_RESEARCH_V1'
                 AND observation_ts>='2024-01-01'
                 AND observation_ts<'2026-01-01')
              OR (series_id='GVZ_CBOE'
                 AND observation_ts>='2026-01-01'
                 AND observation_ts<'2026-10-01')
              OR (series_id='DGS10_FRB_H15'
                 AND observation_ts>='2024-01-01'
                 AND observation_ts<'2026-10-01')
              ORDER BY observation_ts::date,series_id,observation_ts DESC
            """)
            context={}
            for d,s,v in c:
                context.setdefault(d,{})["gvz" if s.startswith("GVZ") else "rate"]=v
            c.execute("""
              SELECT bar_start_utc,close_price
              FROM public.gold_research_histdata_xau15m_candidate
              WHERE bar_start_utc>='2024-01-01'
                AND bar_start_utc<'2026-10-01'
              ORDER BY bar_start_utc
            """)
            xau_bars=daily_features((r[0],float(r[1])) for r in c)
    for r in metals:
        r.update(context.get(r["dt"],{}))
    with V33.open(encoding="utf-8",newline="") as f:
        original={}
        for r in csv.DictReader(f):
            if r["scenario"]=="AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES":
                original[date.fromisoformat(r["date"])]={
                    "V22":r["model_v22_review"]=="True",
                    "modelPrice":float(r["price"]) if r["price"] else None
                }
    return metals,xau_bars,original

def score(metals: list[dict], xau_bars: dict,
          original: dict) -> dict:
    metals=prep_metal_rows(metals)
    q=fixed_thresholds(metals,xau_bars)
    testdates=sorted(d for d in xau_bars if d.year==2026 and d<=TEST_LAST
                     and d in original)
    eligible=[]
    for i,d in enumerate(testdates):
        if i+5>=len(testdates) or (testdates[i+5]-d).days>12:
            continue
        x=xau_bars[d]
        future_prices=[xau_bars[j]["last"] for j in testdates[i+1:i+6]]
        if not future_prices:
            continue
        label=(100*(min(future_prices)/x["last"]-1)<=-4)
        ix=next((k for k,r in enumerate(metals) if r["dt"]==d),None)
        if ix is None:
            continue
        ctx=causal_context(metals,ix,q)
        shock=x.get("worst4h") is not None and x["worst4h"]<=q["worst4h"]
        r=flags(original[d]["V22"],shock,ctx)
        eligible.append({"date":d,"label":label,"flags":r,"context":ctx,
                         "worst4h":x.get("worst4h")})
    if len(eligible)<175:
        raise ValueError("EVALUATION_COVERAGE_TOO_LOW")
    count_label=sum(r["label"] for r in eligible)
    counts={}
    for key in ("V22","V22_OR_4H","V22_OR_4H_METALS","V22_OR_4H_MACRO",
                "V22_OR_4H_METALS_OR_MACRO"):
        flagged=[r for r in eligible if r["flags"][key]]
        hit=sum(r["label"] for r in flagged)
        counts[key]={"warningDays":len(flagged),
                     "followedByFourPctWithinFiveDays":hit,
                     "unmatchedWarningDays":len(flagged)-hit,
                     "missedLabeledDays":count_label-hit,
                     "labeledDayCoveragePct":round(100*hit/count_label,2)
                       if count_label else None}
    episodes=_episodes(original)
    for e in episodes:
        raw=sorted(d for d in original
                  if d<e["start"] and d.year==2026)
        last10=raw[-10:]
        # For lead-time episodes, early indicators may fall on days
        # not in matured forward-label cohort (e.g. in last part of test).
        by_date={r["date"]:r for r in eligible}
        for key in counts:
            prior=[d for d in last10
                if d in by_date and by_date[d]["flags"][key]]
            e.setdefault("firstEarly",{})[key]=str(prior[0]) if prior else None
    episode_counts={k:sum(bool(e["firstEarly"][k]) for e in episodes)
                    for k in counts}
    return {
        "schema":"GOLD_V37_MULTIMETAL_MACRO_INTRADAY_SHADOW_V1",
        "status":"HISTORICAL_RESEARCH_NOT_PIT_OR_LIVE",
        "calibration":"2024_2025_STAKTRAKR_METALS_GVZ_FRED_H15_HISTDATA",
        "evaluation":"2026_JAN_SEP_STAKTRAKR_BACKFILL_GVZ_CBOE_H15_HISTDATA",
        "fourMetalIntradayAvailable":False,
        "hourlyOnlyXAU":True,"DXYIntradayAvailable":False,
        "monthlyGPRIsNotIntraday":True,
        "sourceFirstprintCertified":False,"modelChanged":False,
        "liveAlertsProduced":False,"databaseWrites":False,"orders":False,
        "thresholds":{k:round(v,5) for k,v in q.items()},
        "temporalRules":{
            "XAU":"15_minute_bars_end_of_current_day",
            "AG_PT_PD":"previous_1_to_4_price_sessions_only",
            "GVZ_DGS10":"previous_2_sessions_at_earliest",
            "outcome":"future_5_completed_price_sessions_only_scoring"
        },
        "trainMetalDays":sum(r["dt"]<=TRAIN_LAST for r in metals),
        "testMatchedMaturedDays":len(eligible),
        "testLabeledFourPctDays":count_label,
        "warningDays":counts,"episodes":episodes,
        "episodeEarlyCounts":episode_counts,
        "selectionBiasWarning":"Some tested variants were inspected after 2026 outcomes were known",
        "notBlindTest":True,
    }

def _episodes(original):
    daily=sorted((d,r["modelPrice"]) for d,r in original.items()
                 if d<=TEST_LAST and r["modelPrice"] and r["modelPrice"]>0)
    pairs=[]
    for i in range(len(daily)-5):
        j=min(range(i+1,i+6),key=lambda k:daily[k][1])
        change=100*(daily[j][1]/daily[i][1]-1)
        if change<=-4:
            pairs.append((i,j,change))
    e=[]
    for i,j,change in pairs:
        if not e or i>e[-1]["lastIdx"]:
            e.append({"startIdx":i,"lastIdx":j,
                      "worst":(i,j,change)})
        else:
            z=e[-1]
            z["lastIdx"]=max(z["lastIdx"],j)
            if change<z["worst"][2]:
                z["worst"]=(i,j,change)
    out=[]
    for z in e:
        a,b,chg=z["worst"]
        out.append({"start":daily[z["startIdx"]][0],
                    "end":daily[z["lastIdx"]][0],
                    "worstStart":daily[a][0],"worstEnd":daily[b][0],
                    "worstFiveDayPct":round(chg,3)})
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-v37-multimetal-macro-shadow.json")
    args=p.parse_args()
    metals,bars,original=read_inputs()
    result=score(metals,bars,original)
    Path(args.out).write_text(json.dumps(result,ensure_ascii=False,indent=2,
                                         default=str)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2,default=str))
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("## V37 four-metal + macro intraday research ONLY\n\n")
            f.write("| Gate | Warn days | Four-percent next5 matches | No match |\n")
            f.write("|---|---:|---:|---:|\n")
            for k,v in result["warningDays"].items():
                f.write(f"| {k} | {v['warningDays']} | "
                        f"{v['followedByFourPctWithinFiveDays']} | "
                        f"{v['unmatchedWarningDays']} |\n")
            f.write("\n**Not live or firstprint-certified.**\n")
if __name__=="__main__":
    main()
