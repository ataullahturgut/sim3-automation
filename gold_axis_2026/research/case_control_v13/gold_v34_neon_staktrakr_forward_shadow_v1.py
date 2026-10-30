#!/usr/bin/env python3
"""Run unchanged V34 ANN via Neon StakTrakr 4-metal feed (shadow, not PIT).

Retrospective mode is a late historical run for target 2026-10-26.
Forward mode accepts only a fully completed previous UTC week and prior public
API captures, and issues the next ISO week as research shadow (NOT production).
The original V34 MLP fit, features, original retrospective historic scenario,
and training inputs are unchanged. The intended audit is explicit about the
2026-02-27 source substitution: it is NOT a same-price-benchmark certified feed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import numpy as np
import psycopg
from psycopg.rows import dict_row

import gold_v34_ann_replay as v34
import gold_v34_forward_parity_v1 as forward
import gold_weekly_h1_ann_4metal_v1 as weekly

METALS = ("AU", "AG", "PT", "PD")
MODEL = "WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1"
REFERENCE = "STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17"
EVIDENCE = "RESEARCH_BACKFILL_SHADOW_NOT_FIRSTPRINT"


def require(ok, reason):
    if not ok:
        raise RuntimeError("V34_NEON_SHADOW_GATE_" + reason)


def next_monday(now):
    today = now.date()
    ahead = (7 - today.weekday()) % 7
    return today + timedelta(days=ahead or 7)


def read_recent(db, first, last):
    sql = """
       SELECT DISTINCT ON (price_date,metal)
         price_date,metal,spot_usd_oz,first_observed_utc,
         evidence_class,price_reference,source_row_sha256,raw_snapshot_sha256
       FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
       WHERE price_date BETWEEN %s AND %s
       ORDER BY price_date,metal,first_observed_utc DESC
    """
    with db.cursor() as cur:
        cur.execute(sql, (first,last))
        rows = cur.fetchall()
    return rows


def validate_frozen_october(prices, rows):
    """Do not silently graft a different provider/definition into frozen V34."""
    raw = prices[prices.date.between("2026-10-19","2026-10-23")]
    expected = {r.date: {m:float(getattr(r,m)) for m in METALS}
                for r in raw.itertuples(index=False)}
    require(len(expected)==5, "OCT19_23_FROZEN_SOURCE_MISSING")
    found = defaultdict(dict)
    for row in rows:
        if row["price_date"].isoformat() in expected:
            found[row["price_date"].isoformat()][row["metal"]] = float(row["spot_usd_oz"])
    require(set(found)==set(expected), "OCT19_23_FEED_OVERLAP_INCOMPLETE")
    mismatched = [(d,m,expected[d][m],found[d].get(m))
                  for d in expected for m in METALS
                  if abs(expected[d][m]-found[d].get(m,0))>1e-6]
    require(not mismatched,"OCT19_23_PRICE_CONFLICT_"+str(mismatched[:2]))
    return 20


def new_week_summary(rows, origin_week, origin_end, now):
    grouped = defaultdict(dict)
    for row in rows:
        d=row["price_date"]
        if d<origin_week or d>origin_end or d.weekday()>4:
            continue
        require(row["evidence_class"] == "PUBLIC_API_FETCH_NOT_ORIGIN_PIT",
                "SOURCE_EVIDENCE_CHANGED")
        require(row["price_reference"] == REFERENCE, "PRICE_REFERENCE_CHANGED")
        require(row["first_observed_utc"]<=now, "SOURCE_FUTURE_CAPTURE")
        require(row["metal"] not in grouped[d], "DUPLICATE_METAL_DAY")
        grouped[d][row["metal"]]=row
    aligned = sorted(d for d in grouped if set(grouped[d])==set(METALS))
    require(len(aligned)>=3, "ORIGIN_FOUR_METAL_ALIGNED_LT3")
    # For regular October 2026 target, Friday is a required market session.
    require(origin_end in aligned, "ORIGIN_FRIDAY_NOT_YET_AVAILABLE")
    require(all(m in grouped[d] for d in aligned for m in METALS),
            "ORIGIN_MISSING_METAL")
    price = np.array([[float(grouped[d][m]["spot_usd_oz"])
                       for m in METALS] for d in aligned])
    require(np.isfinite(price).all() and price.min()>0, "NONFINITE_WEEK_SPOT")
    output = dict(week_monday=origin_week.isoformat(),
                  first_observation=aligned[0].isoformat(),
                  last_observation=aligned[-1].isoformat(),
                  shared_trading_days=len(aligned),
                  means=price.mean(0).tolist(),
                  opens=price[0].tolist(), closes=price[-1].tolist(),
                  highs=price.max(0).tolist(), lows=price.min(0).tolist(),
                  daily_realized_vol=np.sqrt(np.sum(
                      np.diff(np.log(price),axis=0)**2,axis=0)).tolist())
    evidence = {
        "date": origin_week.isoformat(),
        "sha256s": {d.isoformat(): {
           m: grouped[d][m]["source_row_sha256"] for m in METALS}
          for d in aligned},
        "maxInputFirstObservedUTC": max(
           grouped[d][m]["first_observed_utc"] for d in aligned
           for m in METALS).isoformat(),
    }
    return output, evidence


def fetch_history():
    snapshot = v34.weekly_snapshot()
    weeks=snapshot["week_summaries"]
    require(weeks[-1]["week_monday"]=="2026-10-19",
            "ORIGINAL_FROZEN_LAST_WEEK_CHANGED")
    require(snapshot["firstprint_PIT_proven"] is False, "OLD_SOURCE_FALSE_PIT")
    original_frame=v34.price_frame()
    return weeks,original_frame


def generate(mode, now):
    target = date(2026,10,26) if mode=="retrospective" else next_monday(now)
    start = target - timedelta(days=7)
    end = target - timedelta(days=3)
    # Prior daily UTC week must be finished before feeding week summary.
    cutoff = datetime.combine(end+timedelta(days=1),datetime.min.time(),
                              tzinfo=timezone.utc)
    report = dict(kind="STAKTRAKR_V34_16D_NEON_SHADOW_V1",
                  mode=mode,nowUTC=now.isoformat(),
                  targetWeek=target.isoformat(),
                  originWeek=start.isoformat(),
                  requiredOriginWeekCompleteUTC=cutoff.isoformat(),
                  productionForecast=False,firstprintPITCertified=False,
                  sourceReference=REFERENCE,
                  original20260227SourceScenario="EXTERNAL_CLOSE_ONLY_SENSITIVITY_NOT_CERTIFIED",
                  forecastPublishedIntoCanonicalNY17=False)
    if mode=="forward" and now<cutoff:
        return {**report,"status":"BLOCKED_ORIGIN_UTC_FRIDAY_INCOMPLETE",
                "forecast":None},None
    uri=os.getenv("NEON_DATABASE_URL","")
    require(bool(uri), "NEON_DATABASE_URL_MISSING")
    with psycopg.connect(uri,connect_timeout=15,row_factory=dict_row,
                         options="-c default_transaction_read_only=on") as db:
        # October 19-23 same-source overlap must match the frozen V34 history.
        # Subsequent weeks must come from the new daily Neon ledger, never
        # from target-week prices or another price reference.
        rows=read_recent(db,date(2026,10,19),end)
    historic,raw=fetch_history()
    overlap=validate_frozen_october(raw,rows)
    if mode=="retrospective":
        weeks=[w for w in historic if w["week_monday"]<target.isoformat()]
        audit={"sourceOverlapMatchedRows":overlap,
               "originSource":"FROZEN_V34_WEEKLY_SNAPSHOT"}
    else:
        require(start>=date(2026,10,26),
                "FORWARD_ORIGIN_OVERLAPS_FROZEN_RESEARCH_WEEK")
        weeks=[w for w in historic if w["week_monday"]<target.isoformat()]
        add = []
        for step in range(0, (start-date(2026,10,26)).days+1, 7):
            monday=date(2026,10,26)+timedelta(days=step)
            friday=monday+timedelta(days=4)
            w, ev=new_week_summary(rows,monday,friday,now)
            require(w["week_monday"] not in {h["week_monday"] for h in weeks},
                    "ORIGIN_WEEK_OVERLAPS_FROZEN")
            weeks.append(w)
            add.append(ev)
        audit={"sourceOverlapMatchedRows":overlap,
               "originSource":"NEON_STAKTRAKR_UTC_DAILY_REFERENCE",
               "appendedWeeks":len(add),
               "appendedWeekEvidence":add}
    result=forward.infer(weeks,target.isoformat())
    require(result["feature_dim"]==16 and result["model"]==MODEL,
            "WRONG_MODEL_OR_FEATURES")
    require(result["origin_week"]==start.isoformat(),"ORIGIN_NOT_PREVIOUS")
    require(result["training_last_week"]<target.isoformat(),
            "TARGET_LEAK_IN_TRAINING")
    report.update(
       status=("RESEARCH_LATE_REPLAY_ONLY" if mode=="retrospective"
               else "READY_TO_APPEND_RESEARCH_SHADOW_NOT_PRODUCTION"),
       generatedUTC=now.isoformat(),
       originalTrainingWeeks=result["training_n"],
       inputSha256=result["input_sha256"],
       trainingFirstWeek=result["training_first_week"],
       trainingLastWeek=result["training_last_week"],
       featureCount=result["feature_dim"],
       forecastMeanUSD=result["forecast_mean_xau"],
       forecastLastSharedDayUSD=result["forecast_close_xau"],
       sourceEvidence=audit,
       fullOriginWeekComplete=(mode=="forward" and now>=cutoff),
       noFutureWeekActuals=True)
    return report,result


def insert_shadow(result,now,report):
    require(report["status"]=="READY_TO_APPEND_RESEARCH_SHADOW_NOT_PRODUCTION",
            "WRONG_PRODUCTION_WRITE_STATUS")
    sql="""
      INSERT INTO gold_weekly_live.staktrakr_v34_ann_shadow_v1(
          target_week, origin_week, model_id, forecast_week_mean_usd_oz,
          forecast_week_last_shared_day_usd_oz, latest_input_date,
          full_origin_week_complete,original_model_params_frozen,
          training_weeks,feature_dim,input_sha256,evidence)
      VALUES (%s,%s,%s,%s,%s,%s,true,true,%s,16,%s,%s::jsonb)
      ON CONFLICT (target_week,input_sha256) DO NOTHING
      RETURNING id
    """
    uri=os.getenv("NEON_DATABASE_URL","")
    require(bool(uri),"NEON_DATABASE_URL_MISSING")
    with psycopg.connect(uri,connect_timeout=15) as db:
        with db.cursor() as cur:
            cur.execute(sql,(result["target_week"],result["origin_week"],
                     MODEL,result["forecast_mean_xau"],result["forecast_close_xau"],
                     (date.fromisoformat(result["origin_week"])+timedelta(days=4)),
                     result["training_n"],result["input_sha256"],
                     json.dumps(report,sort_keys=True,allow_nan=False)))
            row=cur.fetchone()
        db.commit()
    return bool(row)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=["forward","retrospective"],required=True)
    parser.add_argument("--apply-shadow",action="store_true")
    parser.add_argument("--out",default="v34_neon_shadow_result.json")
    args=parser.parse_args()
    require(not args.apply_shadow or args.mode=="forward",
            "HISTORICAL_RUN_NOT_PERMITTED_TO_WRITE")
    now=datetime.now(timezone.utc)
    report,result=generate(args.mode,now)
    report["neonShadowInserted"]=False
    if args.apply_shadow and result is not None:
        report["neonShadowInserted"]=insert_shadow(result,now,report)
    Path(args.out).write_text(json.dumps(report,indent=2,sort_keys=True,
                                         allow_nan=False)+"\n")
    print(json.dumps(report,sort_keys=True,indent=2,allow_nan=False),flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
