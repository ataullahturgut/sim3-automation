#!/usr/bin/env python3
"""V38: actual four-metal SAME-UTC-HOUR 4h stress, versus original V22.

READ-ONLY HISTORICAL RESEARCH; not prospective/firstprint/blind or trading.
Critical: legacy -1.7952% XAU gate from 2024-25 *HistData* does not have
source parity with 2026 StakTrakr hourly. Alternative all-four -1% in 4h
is an exploratory sensitivity case, not calibrated by 2024-25 hourly metals.
All signals use only a completed 4h hour (no future prices). At evaluation,
daily bar signals are scored against the FOLLOWING five model price sessions;
different research price definitions are audited separately.
"""
from __future__ import annotations
import argparse,csv,json,os
from datetime import date,timedelta
from pathlib import Path

ROOT=Path(__file__).parent
ORIGINAL=ROOT/"outputs"/"v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv"
YEAR=2026
GOLD_TRAIN_THRESHOLD=-1.7952
MODELS=("V22","V22_OR_XAU4_HIST_THRESHOLD","V22_OR_ALL_FOUR_NEGATIVE_ONE_PCT",
        "V22_OR_XAU1_TWO_OTHER1_5")
EVENTS=(
    ("Mayıs",date(2026,5,13)),
    ("Haziran ilk",date(2026,6,4)),
    ("Haziran ikinci",date(2026,6,17)),
    ("Ağustos–Eylül",date(2026,8,25)),
    ("Eylül sonu",date(2026,9,21)),
)
SOURCE_CLASS="STAKTRAKR_V2_HOURLY_HISTORICAL_RESEARCH_NOT_FIRSTPRINT"
SQL="""
WITH latest AS(
 SELECT DISTINCT ON (metal,bar_start_utc)
  metal,bar_start_utc AS ts,spot_close_usd_oz::float8 AS px
 FROM gold_weekly_live.staktrakr_fourmetal_hourly_ohlca_research_v1
 WHERE bar_start_utc >= '2026-03-25' AND bar_start_utc < '2026-10-30'
 ORDER BY metal,bar_start_utc,ingested_at_utc DESC
), ret AS(
 SELECT metal,ts,px,
 CASE WHEN ts-LAG(ts,4) OVER(PARTITION BY metal ORDER BY ts)
                     =interval '4 hours'
      THEN 100*(px/LAG(px,4) OVER(PARTITION BY metal ORDER BY ts)-1)
 ELSE NULL END r4
 FROM latest
), hourly AS(
 SELECT ts,
 max(r4) FILTER(WHERE metal='AU') au4,
 max(r4) FILTER(WHERE metal='AG') ag4,
 max(r4) FILTER(WHERE metal='PT') pt4,
 max(r4) FILTER(WHERE metal='PD') pd4,
 max(px) FILTER(WHERE metal='AU') au_close
 FROM ret GROUP BY ts
), daily AS(
 SELECT ts::date dt,
 count(*) FILTER(WHERE au4 IS NOT NULL AND ag4 IS NOT NULL
                    AND pt4 IS NOT NULL AND pd4 IS NOT NULL) complete_4h_hours,
 count(*) FILTER(WHERE au4<=-1.7952) xau_hard,
 count(*) FILTER(WHERE au4<=-1 AND ag4<=-1 AND pt4<=-1 AND pd4<=-1) four_same_1pct,
 count(*) FILTER(WHERE au4<=-1 AND
    ((ag4<=-1.5)::int+(pt4<=-1.5)::int+(pd4<=-1.5)::int)>=2) xau1_two_others1_5,
 min(au4) min_au4,min(ag4) min_ag4,min(pt4) min_pt4,min(pd4) min_pd4,
 (array_agg(au_close ORDER BY ts DESC))[1] stak_eod_price
 FROM hourly GROUP BY ts::date
)
SELECT dt,complete_4h_hours,xau_hard,four_same_1pct,xau1_two_others1_5,
 min_au4,min_ag4,min_pt4,min_pd4,stak_eod_price
FROM daily ORDER BY dt
"""

def flags(v22,daily):
    return {
      "V22":bool(v22),
      "V22_OR_XAU4_HIST_THRESHOLD":bool(v22 or daily["xau_hard"]>0),
      "V22_OR_ALL_FOUR_NEGATIVE_ONE_PCT":bool(v22 or daily["four_same_1pct"]>0),
      "V22_OR_XAU1_TWO_OTHER1_5":bool(v22 or daily["xau1_two_others1_5"]>0),
    }

def original_rows():
    with ORIGINAL.open(encoding="utf-8",newline="") as f:
        rows={}
        for row in csv.DictReader(f):
            if row["scenario"]!="AM_MIXED_FIX_REFERENCE_NOT_SAME_SERIES":
                continue
            day=date.fromisoformat(row["date"])
            if day.year!=YEAR:continue
            price=float(row["price"]) if row["price"] else None
            rows[day]={"date":day,
                       "v22":row["model_v22_review"]=="True",
                       "base14":row["BASE14_original_alert_level"],
                       "price":price}
    return rows

def read_neon():
    import psycopg
    uri=os.getenv("NEON_DATABASE_URL","")
    if not uri:raise RuntimeError("MISSING_NEON_DATABASE_URL")
    with psycopg.connect(uri,connect_timeout=25,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as c:
            c.execute(SQL)
            result=c.fetchall()
    return [{
       "date":r[0],"hours":r[1],
       "xau_hard":r[2],"four_same_1pct":r[3],
       "xau1_two_others1_5":r[4],
       "minAu":r[5],"minAg":r[6],"minPt":r[7],"minPd":r[8],
       "stak_price":r[9]
    } for r in result]

def compile_calendar(observations,original):
    # Explicit original price calendar Mon–Fri; reject same-day 4h data without
    # an aligned 4-metal price basis.
    result=[]
    for x in observations:
        day=x["date"]
        orig=original.get(day)
        if day.weekday()>=5 or not orig or x["hours"]<12:
            continue
        result.append({**x,**orig,"signals":flags(orig["v22"],x)})
    return sorted(result,key=lambda r:r["date"])

def mature_calendar(calendar,price_key):
    # Future labels are only used AFTER research warnings have been computed.
    mature=[]
    for i,row in enumerate(calendar):
        if i+5>=len(calendar):continue
        future=calendar[i+1:i+6]
        if (future[-1]["date"]-row["date"]).days>12:
            continue
        p=row[price_key]
        if not p or any(not x[price_key] for x in future):
            continue
        drop=100*(min(float(x[price_key]) for x in future)/float(p)-1)
        mature.append({**row,"outcome":drop<=-4,
                       "next5WorstDropPercent":round(drop,4)})
    return mature

def daily_metrics(mature):
    positives=sum(r["outcome"] for r in mature)
    if not positives:raise ValueError("NO_MATURED_FOUR_PCT_LABELS")
    scores={}
    for key in MODELS:
        alerts=[r for r in mature if r["signals"][key]]
        hits=sum(r["outcome"] for r in alerts)
        scores[key]={
          "warningDays":len(alerts),"matchedWarningDays":hits,
          "unmatchedWarningDays":len(alerts)-hits,
          "missedPositiveOriginDays":positives-hits,
          "precisionPercent":round(100*hits/len(alerts),2) if alerts else None,
          "positiveOriginRecallPercent":round(100*hits/positives,2)
        }
    return {"evaluatedDays":len(mature),
            "positiveOriginDays":positives,"models":scores}

def episodes(calendar):
    out=[]
    for name,event in EVENTS:
        eligible=[x for x in calendar if x["date"]<event]
        before=eligible[-10:]
        if len(before)<10:raise ValueError("INSUFFICIENT_EVENT_PREHISTORY_"+name)
        ev={"event":name,"start":str(event),"priorTenDates":[str(x["date"]) for x in before],
            "warning":{}}
        for model in MODELS:
            hits=[x for x in before if x["signals"][model]]
            if hits:
                ev["warning"][model]={
                    "firstDate":str(hits[0]["date"]),
                    "businessDaysBefore":10-before.index(hits[0]),
                    "warningDays":len(hits)
                }
            else:ev["warning"][model]=None
        out.append(ev)
    return out

def report(calendar):
    matched=mature_calendar(calendar,"price")
    stak=mature_calendar(calendar,"stak_price")
    if len(matched)<130 or len(stak)<130:
        raise ValueError("LOW_COMMON_CALENDAR_COVERAGE")
    timeline=episodes(calendar)
    event_counts={model:sum(bool(e["warning"][model]) for e in timeline)
                  for model in MODELS}
    overlap_events={}
    return {
      "schema":"V38_SAME_SOURCE_FOUR_METAL_HOURLY_STAKTRAKR_V22_REPLAY_V1",
      "scope":"StakTrakr 2026-03-25 to 2026-10-29 + original V33 model diary",
      "sourceFirstprintCertified":False,"researchNotBlind":True,
      "no2024to2025FourMetalHourlyTraining":True,
      "newFourMetalThresholdsResearchHeuristicsNotFitted":True,
      "strictSourceParityOfLegacyGoldThreshold":False,
      "warningDefinition":"intraday 4h price returns ending at same UTC hour, aggregated only after day closes",
      "labelDefinitionOriginal":"next 5 completed V33 weekday prices <= -4pct from origin V33 price",
      "labelDefinitionAlt":"next 5 completed StakTrakr weekday hourly-last prices <= -4pct",
      "missingFuturesNeverImputed":True,"V22ModelChanged":False,
      "productionSignalIssued":False,"neonWrites":False,"trades":False,
      "originalPriceScoring":daily_metrics(matched),
      "sameSourcePriceScoring":daily_metrics(stak),
      "episodeEarlyAlerts":event_counts,
      "episodes":timeline,
      "sourceRevisionPolicy":"latest ingested source revision per metal-hour; immutable original retained",
      "researchComparabilityWarning":"2026 early lookups influenced alternative heuristic selection; do not claim independent blind test"
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-v38-staktrakr-fourmetal-hourly-risk-audit.json")
    args=p.parse_args()
    orig=original_rows()
    calendar=compile_calendar(read_neon(),orig)
    results=report(calendar)
    out=Path(args.out)
    out.write_text(json.dumps(results,ensure_ascii=False,default=str,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(results,ensure_ascii=False,default=str,indent=2),flush=True)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:
            f.write("## V38 new four-metal same-hour intraday research (not live)\n\n")
            f.write(f"Common price days: {len(calendar)}; eligible "
                    f"{results['originalPriceScoring']['evaluatedDays']}.\n\n")
            f.write("| Model | Flags | Matches | Nonmatches |\n|---|---:|---:|---:|\n")
            for model,metrics in results["originalPriceScoring"]["models"].items():
                f.write(f"| {model} | {metrics['warningDays']} | "
                        f"{metrics['matchedWarningDays']} | "
                        f"{metrics['unmatchedWarningDays']} |\n")
            f.write("\n**No live outputs or model promotion.**\n")
if __name__=="__main__":
    main()
