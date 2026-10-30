#!/usr/bin/env python3
"""Original BASE14/CFTC21 21-feature forest and V22 extension to current Neon spot.

This is a research-only D-1 latest-observed scoring run. Prior-price historical
snapshots and the one-day substituted bad Feb-27 gold price are NOT same-fixing
PIT-certified. CFTC recent normal-week release may be a dated proxy. Everything
is labelled RESEARCH_SHADOW_UNCERTIFIED, NOT A LIVE TRADE SIGNAL.

Frozen original model code, 200-tree IF fits, 90/95% thresholds, V22 P1..P7,
historical casebook and original 187-date parity are retained, not approximated.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import os
from collections import defaultdict
from datetime import date,datetime,timezone
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from psycopg.rows import dict_row

import risk_v29_fourmetal_price_replay as v29
import risk_v33_2026_full_asof_oct27_replay as v33

HERE=Path(__file__).resolve().parent
METALS=("AU","AG","PT","PD")
MACRO=("GVZ_CBOE","DGS10_FRB_H15","DTWEXBGS_FRB_H10")
DATA_END="2026-10-29"
DATE_ORIGINAL_CUTOFF="2026-10-23"
RESEARCH="RESEARCH_SHADOW_UNCERTIFIED_ORIGINAL_FOURMETAL_V22_V35"

def check(ok,key):
    if not bool(ok): raise AssertionError("V35_V22_NEON_GUARD_"+key)

def latest_completed_fourmetal_date(now):
    uri=os.getenv("NEON_DATABASE_URL","")
    check(bool(uri),"NEON_URL_MISSING")
    with psycopg.connect(uri,connect_timeout=12,row_factory=dict_row,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as cur:
            cur.execute("""
              SELECT max(price_date) AS latest_complete
              FROM (
                SELECT price_date
                FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
                WHERE price_date >= DATE '2026-10-29' AND price_date < %s
                  AND EXTRACT(ISODOW FROM price_date)<=5
                GROUP BY price_date
                HAVING count(DISTINCT metal)=4
              ) d
            """,(now.date(),))
            row=cur.fetchone()
    check(row["latest_complete"] is not None, "NO_COMPLETE_LATEST_WEEKDAY")
    result=row["latest_complete"]
    check(result.isoformat()>="2026-10-29" and result.year==2026,
          "LATEST_DATE_OUT_OF_SUPPORTED_2026_HORIZON")
    check((now.date()-result).days<=5,"STAK_REFERENCE_FEED_STALE")
    return result.isoformat()


def source_from_neon(now):
    uri=os.getenv("NEON_DATABASE_URL","").strip()
    check(bool(uri),"NEON_URL_MISSING")
    with psycopg.connect(uri,connect_timeout=12,row_factory=dict_row,
                         options="-c default_transaction_read_only=on") as db:
        with db.cursor() as cur:
            cur.execute("""
               SELECT DISTINCT ON (price_date,metal)
                 price_date,metal,spot_usd_oz,first_observed_utc,
                 source_row_sha256,evidence_class,price_reference
               FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
               WHERE price_date BETWEEN '2026-10-19' AND %s
                 AND EXTRACT(ISODOW FROM price_date) <= 5
               ORDER BY price_date,metal,first_observed_utc ASC
            """,(DATA_END,))
            prices=cur.fetchall()
            cur.execute("""
               SELECT DISTINCT ON (series_id,observation_ts)
                 series_id,observation_ts,value,available_as_of,
                 quality_status,source
               FROM public.observations
               WHERE series_id=ANY(%s)
                 AND observation_ts::date BETWEEN '2026-10-19' AND %s
               ORDER BY series_id,observation_ts,available_as_of ASC
            """,(list(MACRO),DATA_END))
            macro=cur.fetchall()
            cur.execute("""
              SELECT DISTINCT ON (market,report_date)
                market,contract_code,report_date,open_interest,
                managed_money_long,managed_money_short,
                managed_money_net_over_oi,managed_money_short_over_oi,
                raw_row_sha256,earliest_model_use_date,retrieved_utc
              FROM gold_weekly_live.cftc_gc_si_futuresonly_official_v1
              WHERE report_date >= DATE '2026-10-20'
                AND report_date <= %s
              ORDER BY market,report_date,retrieved_utc ASC
            """,(DATA_END,))
            official_cot=cur.fetchall()
    seen=defaultdict(dict)
    for row in prices:
        d=row["price_date"].isoformat()
        m=row["metal"]
        check(m in METALS,"UNEXPECTED_METAL")
        check(row["evidence_class"]=="PUBLIC_API_FETCH_NOT_ORIGIN_PIT","BAD_METAL_CLASS")
        check(row["price_reference"]=="STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17",
              "UNEXPECTED_PRICE_REFERENCE")
        check(row["first_observed_utc"]<=now,"FUTURE_PRICE_CAPTURE")
        check(m not in seen[d],"DUPLICATE_SPOT_DATE")
        seen[d][m]=row
    for d in pd.bdate_range("2026-10-19",DATA_END).strftime("%Y-%m-%d"):
        check(set(seen[d])==set(METALS),"MISSING_FOURMETAL_DATE_"+d)
    macro_new=defaultdict(dict)
    for r in macro:
        day=r["observation_ts"].date().isoformat()
        code=r["series_id"]
        check(code in MACRO,"INVALID_MACRO_SERIES")
        check(r["available_as_of"]<=now,"MACRO_FUTURE_CAPTURE")
        check(code not in macro_new[day],"MACRO_DUPLICATE_DAY")
        check(np.isfinite(float(r["value"])) and float(r["value"])>0,
              "INVALID_MACRO_VALUE")
        macro_new[day][code]=r
    check("GVZ_CBOE" in macro_new[DATA_END],"NO_LATEST_GVZ")
    check("DGS10_FRB_H15" in macro_new["2026-10-28"],
          "LATEST_H15_BEHIND")
    return seen, macro_new, official_cot

def append_source(src,seen,macro_new,now,existing_asof):
    previous=src["prices"]
    check(previous[-1]["date"]==DATE_ORIGINAL_CUTOFF,
          "FROZEN_BASE_DATE_CHANGED")
    original_dates={r["date"] for r in previous}
    frozen_parity=0
    for d in sorted(seen):
        if d>DATE_ORIGINAL_CUTOFF:continue
        row=next((r for r in previous if r["date"]==d),None)
        check(row is not None,"MISSING_FROZEN_PRICE_"+d)
        for i,m in enumerate(METALS):
            check(abs(float(row["metals"][i])-float(seen[d][m]["spot_usd_oz"]))<1e-7,
                  "FROZEN_LATE_PRICE_REVISION_"+d+"_"+m)
            frozen_parity+=1
    check(frozen_parity==20,"OCT19_TO23_PRICE_PARITY")
    appended=[]
    for d in sorted(seen):
        if d<=DATE_ORIGINAL_CUTOFF:continue
        check(d not in original_dates,"DUPLICATE_APPEND_DATE")
        src["prices"].append(dict(date=d,metals=[
            float(seen[d][m]["spot_usd_oz"]) for m in METALS]))
        appended.append(d)
    expected=pd.bdate_range("2026-10-26",DATA_END).strftime("%Y-%m-%d").tolist()
    check(appended==expected,"CURRENT_WEEK_INCOMPLETE")
    available=dict(existing_asof)
    for d in sorted(macro_new):
        for series,r in macro_new[d].items():
            target=(src["gvz"] if series=="GVZ_CBOE"
                    else src["macro"][series])
            if d in target:
                check(abs(float(target[d])-float(r["value"]))<1e-7,
                      "REVISED_OLD_MACRO_"+series+"_"+d)
            else:
                target[d]=float(r["value"])
            # Historical 2026 values can only be used as-of origin day
            # once verified, but THIS current final origin may use all rows
            # physically retrieved before current real inference UTC.
            avail_date=r["available_as_of"].date().isoformat()
            if (series,d) not in available:
                available[(series,d)]=avail_date
    return appended,available,frozen_parity

def extend_official_cot(cot,official,now):
    """Only add strictly later paired official weekly reports. Historical frozen
    GC/SI rows never rewritten. Missing/modified overlap is reported as
    unverified source differences and blocks promotion.
    """
    last=cot["GC"][-1]["date"]
    check(last==cot["SI"][-1]["date"],"CFTC_ORIGINAL_MARKET_MISALIGNED")
    by=defaultdict(dict)
    for row in official:
        d=row["report_date"].isoformat()
        m=row["market"]
        check(m in ("GC","SI"),"CFTC_UNKNOWN_MARKET")
        check(m not in by[d],"CFTC_DUPLICATE_WEEK")
        check(row["retrieved_utc"]<=now,"CFTC_FUTURE_FIRST_CAPTURE")
        by[d][m]=row
    overlap=by.get(last)
    if overlap:
        check(set(overlap)=={"GC","SI"},"CFTC_OFFICIAL_OVERLAP_MISSING_MARKET")
        for market in ("GC","SI"):
            z=overlap[market]
            prior=cot[market][-1]
            print("CFTC_FROZEN_OFFICIAL_OVERLAP_DIAGNOSTIC",json.dumps({
                "market":market,"date":last,
                "frozen_net_fraction":float(prior["mm_net_fraction_oi"]),
                "official_net_fraction":float(z["managed_money_net_over_oi"]),
                "frozen_oi":float(prior["open_interest"]),
                "official_oi":float(z["open_interest"]),
                "frozen_short":float(prior["managed_money_short"]),
                "official_short":float(z["managed_money_short"])
                },sort_keys=True),flush=True)
            check(abs(float(prior["mm_net_fraction_oi"])-
                      float(z["managed_money_net_over_oi"]))<=5.1e-9,
                  "CFTC_OFFICIAL_VS_FROZEN_OVERLAP_NET_"+market)
            check(abs(float(prior["managed_money_short"])/float(prior["open_interest"])-
                      float(z["managed_money_short_over_oi"]))<=1e-9,
                  "CFTC_OFFICIAL_VS_FROZEN_OVERLAP_SHORT_"+market)
    added=[]
    for d in sorted(by):
        if d<=last:continue
        day=by[d]
        check(set(day)=={"GC","SI"},"UNPAIRED_NEW_CFTC_"+d)
        allowed=day["GC"]["earliest_model_use_date"]
        check(day["SI"]["earliest_model_use_date"]==allowed,
              "DIFFERENT_CFTC_MARKET_AVAILABILITY")
        check(day["GC"]["contract_code"]=="088691" and
              day["SI"]["contract_code"]=="084691",
              "CFTC_WRONG_CONTRACT_CODE")
        check(allowed>date.fromisoformat(d),"CFTC_BEFORE_PUBLICATION")
        # Keep first actual capture and conservative usable date, not guessed
        # historical publication time. Original release-clock helper handles
        # as-of eligibility by the (future) observation day.
        for m in ("GC","SI"):
            z=day[m]
            cot[m].append({
              "date":d,"available":allowed.isoformat(),
              "quality":"OFFICIAL_SOCRATA_FIRST_CAPTURE_CONSERVATIVE_LAG",
              "mm_net_fraction_oi":float(z["managed_money_net_over_oi"]),
              "open_interest":float(z["open_interest"]),
              "managed_money_net":float(z["managed_money_long"]-z["managed_money_short"]),
              "managed_money_short":float(z["managed_money_short"]),
            })
        added.append(d)
    return {"originalLastReport":last,"newReportDates":added,
            "frozenOfficialOverlapVerified":bool(overlap)}


def original_risk_rows(src,cot,available,now):
    # Original v8 make_rows source dynamically frozen but NO changes to its
    # original feature formula or 21 feature order; ONLY remove future labels
    # and enforce genuine first-retrieval floor for newly extended macro data.
    macro_ready_date=now.date().isoformat()
    target=DATA_END
    repl=[
     ("for i in range(260,len(days)-5):",
      "for i in range(260,len(days)):"),
     ("if not '2023-01-01'<=d<='2026-09-21':continue",
      f"if not '2023-01-01'<=d<='{target}':continue"),
     ("valid_u=[k for k in udays if h10_is_available(k,d)]",
      "valid_u=[k for k in udays if h10_is_available(k,d) and (extra_asof.get(('DTWEXBGS_FRB_H10',k),'1900-01-01')<=d or (d==CURRENT and extra_asof.get(('DTWEXBGS_FRB_H10',k),'1900-01-01')<=INFERENCE))]"),
     ("valid_r=[k for k in rdays if (date.fromisoformat(k)+timedelta(days=1)).isoformat()<=d]",
      "valid_r=[k for k in rdays if (date.fromisoformat(k)+timedelta(days=1)).isoformat()<=d and (extra_asof.get(('DGS10_FRB_H15',k),'1900-01-01')<=d or (d==CURRENT and extra_asof.get(('DGS10_FRB_H15',k),'1900-01-01')<=INFERENCE))]"),
     ("next_day=px[i+1,0]/px[i,0]-1",
      "next_day=px[i+1,0]/px[i,0]-1 if i+1<len(days) else float('nan')"),
     ("m5=float(np.min(px[i+1:i+6,0]/px[i,0]-1))",
      "m5=float(np.min(px[i+1:i+6,0]/px[i,0]-1)) if i+5<len(days) else float('nan')"),
     ("'first_target':days[i+1],",
      "'first_target':days[i+1] if i+1<len(days) else 'UNMATURED',"),
     ("'target_mature':days[i+5],",
      "'target_mature':days[i+5] if i+5<len(days) else '9999-12-31',"),
     ("'y_next5_abs5':bool(np.max(abs(px[i+1:i+6,0]/px[i,0]-1))>=.05)",
      "'y_next5_abs5':(bool(np.max(abs(px[i+1:i+6,0]/px[i,0]-1))>=.05) if i+5<len(days) else None)")
    ]
    fn=v33.patched(v29.original.make_rows,repl,{
        **vars(v29.original),
        "BAD_DAY":"1900-01-01",  # explicit research alternative only
        "extra_asof":available,"CURRENT":DATA_END,
        "INFERENCE":macro_ready_date,
    })
    rows=fn(src,cot)
    current=[r for r in rows if r["origin"]==DATA_END]
    check(len(current)==1,"LATEST_DAY_NOT_SCOREABLE")
    check(current[0]["target_mature"]=="9999-12-31",
          "INCOMPLETE_NEXT_FIVE_MISLABELED")
    check(not np.isfinite(current[0]["next5_min_return_pct"]),
          "NEXT_FIVE_LABEL_LEAK")
    check(current[0]["cftc_available_date"]<=DATA_END,
          "FUTURE_CFTC_USED")
    return rows,current[0]

def scores_and_v22(src,cot,rows):
    scorer=v33.patched(
       v29.original.compute,
       [("('2026','2025-12-31','2026-01-01','2026-09-21')",
         "('2026','2025-12-31','2026-01-01','2026-10-29')")],
       vars(v29.original))
    predictions=pd.DataFrame(scorer(rows)[1])
    frame=v29.source_panel(src,rows)
    fn=v33.patched(
       v29.reconstruct_2026_triage,
       [('testing=[q for q in altrows if "2026-01-01"<=q["origin"]<="2026-09-21"]',
         'testing=[q for q in altrows if "2026-01-01"<=q["origin"]<="2026-10-29"]')],
       vars(v29))
    risk=fn(rows,predictions,frame)
    check(risk.origin.max()==DATA_END,"LATEST_V22_MISSING")
    # Numeric unchanged original model and V22 decisions on all 187 frozen
    # pre-September origins (except documented Feb27 source scenarios).
    return predictions,risk

def one_scenario(base,cot,price,macro_new,seen,now,scenario,existing_asof,cftc_evidence):
    src=copy.deepcopy(base)
    bad=[p for p in src["prices"] if p["date"]=="2026-02-27"]
    check(len(bad)==1,"BAD_FEB27_MISSING")
    bad[0]["metals"]=[float(price[m]) for m in METALS]
    _,released,overlap=append_source(src,seen,macro_new,now,existing_asof)
    rows,current=original_risk_rows(src,cot,released,now)
    model,triage=scores_and_v22(src,cot,rows)
    today=triage[triage.origin.eq(DATA_END)]
    check(len(today)==1,"NO_CURRENT_TRIAGE")
    v=today.iloc[0].to_dict()
    # Explicit publication-time caveat: historical source replacements, fresh
    # H.15 H.10 snapshots, CFTC conservative lag proxies not certified PIT.
    result=dict(schema="GOLD_BASE14_CFTC21_V22_NEON_SHADOW_V35",
        scenario=scenario,date=DATA_END,
        runAtUTC=now.isoformat(),source=RESEARCH,
        sourcePriceKind="STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17",
        gold=float(current["gold_price_usd_oz"]),
        scoreInputFeatureCount=len(current["features"]),
        sourceDaysAppended=(date.fromisoformat(DATA_END)-date(2026,10,23)).days,
        sourceOverlapMatchedMetalRows=overlap,
        officialCotExtension=cftc_evidence,
        CFTCReportDate=current["cftc_observed_position_date"],
        CFTCConservativeUsableDate=current["cftc_available_date"],
        CFTCReleaseQuality=current["cftc_publication_status"],
        CFTCStalenessDays=current["cftc_staleness_days"],
        H10LastEligibleObservation=current["usd_observation_date"],
        H15LastEligibleObservation=current["rate_observation_date"],
        originalParametersChanged=False,
        allFutureOutcomeLabelsCensored=True,
        firstprintPITCertified=False,
        tradeSignal=False,
        officialLiveSignal=False,
        base14Level=str(v["BASE14_original_alert_level"]),
        base14Score=float(v["BASE14_original_score"]),
        cftc21Level=str(v["CFTC21_original_alert_level"]),
        cftc21Score=float(v["CFTC21_original_score"]),
        v22Level=str(v["effective_level"]),
        v22EffectiveReview=bool(v["effective_review"]),
        v22Reasons=str(v["effective_reasons"]),
        v22OriginalReason=str(v["original_reason"]),
        scoredHistory2026=len(triage),
    )
    check(result["scoreInputFeatureCount"]==21,"CURRENT_FEATURES_21")
    check(result["date"]==DATA_END,"NO_CURRENT_RISK")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="v35_current_base14_v22_shadow.json")
    ap.add_argument("--write-shadow",action="store_true")
    args=ap.parse_args()
    now=datetime.now(timezone.utc)
    global DATA_END
    DATA_END=latest_completed_fourmetal_date(now)
    seen,macro,official_cot=source_from_neon(now)
    raw,historical_through_oct23,cot,historic_asof=v33.source_and_inputs()
    cftc_evidence=extend_official_cot(cot,official_cot,now)
    check(cot["GC"][-1]["available"]=="2026-10-27",
          "CFTC_SOURCE_DATE_UNEXPECTED")
    outcomes=[]
    for scenario,prices in v29.SOURCES.items():
        outcomes.append(one_scenario(historical_through_oct23,cot,prices,macro,seen,now,scenario,historic_asof,cftc_evidence))
    status="RESEARCH_V22_CURRENT_DATE_RUN_COMPLETED_NOT_LIVE"
    if any(outcomes[0][k]!=outcomes[1][k] for k in [
       "base14Level","cftc21Level","v22Level","v22EffectiveReview"]):
        status="RESEARCH_SOURCE_SCENARIOS_DISAGREE_NO_PROMOTION"
    report={"status":status,"results":outcomes,"databaseWrites":False,
            "metadata":"2026 Oct29 fourmetal from Neon, Feb27 research scenario uncertainty"}
    encoded=json.dumps(report,sort_keys=True,allow_nan=False)
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    if args.write_shadow:
        sql="""
          INSERT INTO gold_weekly_live.staktrakr_v22_risk_shadow_v1
          (origin_date,scenario,source_sha256,base14_level,base14_score,
           cftc21_level,cftc21_score,v22_level,effective_review,evidence)
          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
          ON CONFLICT (origin_date,scenario,source_sha256) DO NOTHING
          RETURNING id
        """
        with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=15) as db:
            with db.cursor() as cur:
                written=0
                for row in outcomes:
                    stable={k:v for k,v in row.items() if k not in ("runAtUTC",)}
                    h=hashlib.sha256(json.dumps(
                        stable,sort_keys=True,allow_nan=False).encode()).hexdigest()
                    cur.execute(sql,(DATA_END,row["scenario"],h,
                        row["base14Level"],row["base14Score"],
                        row["cftc21Level"],row["cftc21Score"],row["v22Level"],
                        row["v22EffectiveReview"],json.dumps(row,sort_keys=True)))
                    written+=int(cur.fetchone() is not None)
            db.commit()
        report["databaseWrites"]=True
        report["newShadowRows"]=written
        Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True,allow_nan=False),flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
