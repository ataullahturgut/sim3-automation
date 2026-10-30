#!/usr/bin/env python3
"""V34 research-only *daily conditioning*, NOT ANN refitting or bank signals.

A valid preweek V34 shadow forecast must be recorded before Monday 00:00 UTC.
After each completed UTC day Monday-Thursday, the current-week mean estimate
is (sum(known completed weekdays) + remaining_count * original_V34_mean)/5.
Never score Friday as a future forecast; never backfill a prior week as live.
No source is marked firstprint/PIT-certified. No canonical forecast/trade writes.
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import date,datetime,timedelta,timezone
from decimal import Decimal
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

REFERENCE="STAKTRAKR_UTC_DAILY_REFERENCE_NOT_NY17"
MODEL="WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1"
EVIDENCE="FORWARD_CONDITIONING_FIRST_CAPTURE_NOT_PRODUCTION"
SOURCE_CLASS="FORWARD_RESEARCH_SHADOW"

def check(ok,why):
    if not ok:raise RuntimeError("WEEKDAY_CONDITIONING_GATE_"+why)

def current_iso_monday(today):
    return today-timedelta(days=today.weekday())

def evaluate(now,forecast,observed):
    target=current_iso_monday(now.date())
    result={"kind":"GOLD_V34_DAILY_CONDITIONING_SHADOW_V1",
            "status":"BLOCKED_NO_ORIGIN_FORECAST",
            "targetWeek":target.isoformat(),
            "asOfUTC":now.isoformat(),
            "originalANNEdited":False,
            "fitOrRetrainingOccurred":False,
            "priceReference":REFERENCE,
            "productionLive":False,"tradeAuthorized":False,
            "prospectiveFirstprintCertified":False,
            "newConditionedRows":0}
    if forecast is None:
        return result,[]
    check(forecast["target_week"]==target,"WRONG_TARGET_WEEK")
    check(forecast["model_id"]==MODEL,"MODEL_CHANGED")
    check(forecast["feature_dim"]==16 and forecast["training_weeks"]>550,"MODEL_META_CHANGED")
    check(forecast["full_origin_week_complete"] is True,"ORIGIN_NOT_VERIFIED")
    check(forecast["source_utc_day_reference"]==REFERENCE,"UNEXPECTED_PRICE_DEFINITION")
    check(forecast["is_prospective_firstprint"] is False,
          "UNCERTIFIED_RESEARCH_CLAIMED_LIVE")
    check(forecast["historical_source_vintage_certified"] is False,
          "SOURCE_CERTIFICATION_FALSELY_PROMOTED")
    gen=forecast["generated_at_utc"]
    cutoff=datetime.combine(target,datetime.min.time(),tzinfo=timezone.utc)
    check(gen<cutoff and gen<=now,"FORECAST_CREATED_AFTER_WEEK_START")
    check(forecast["origin_week"]==target-timedelta(days=7),"WRONG_ORIGIN_WEEK")
    fc=Decimal(str(forecast["forecast_week_mean_usd_oz"]))
    check(fc>0 and fc.is_finite(),"ANN_NOT_POSITIVE_FINITE")
    expected=target
    seen=Decimal(0)
    created=[]
    last_date=None
    for row in observed:
        d=row["price_date"]
        check(d==expected,"INCOMPLETE_OR_REVISED_WEEKDAY_SEQUENCE")
        check(d.weekday()<4,"FRIDAY_IS_NOT_AN_OPEN_FORECAST_ORIGIN")
        check(d<now.date(),"ORIGIN_PRICE_DATE_NOT_UTC_COMPLETE")
        check(row["price_reference"]==REFERENCE,"MIXED_PRICE_SOURCE")
        check(row["evidence_class"]=="PUBLIC_API_FETCH_NOT_ORIGIN_PIT","SOURCE_PROVENANCE_CHANGED")
        check(row["first_observed_utc"]<=now,"FUTURE_SOURCE_CAPTURE")
        price=Decimal(str(row["spot_usd_oz"]))
        check(price.is_finite() and price>0,"INVALID_SPOT_PRICE")
        seen+=price
        k=(d-target).days+1
        check(k<=4,"INVALID_CALENDAR_DAY_COUNT")
        conditioned=(seen+fc*Decimal(5-k))/Decimal(5)
        check(conditioned>0 and conditioned.is_finite(),"INVALID_CONDITIONED_MEAN")
        created.append({"targetWeek":target.isoformat(),"asOfPriceDate":d.isoformat(),
          "observedWeekdays":k,"remainingWeekdays":5-k,
          "firstANNMeanUSD":str(fc),"knownPriceSumUSD":str(seen),
          "conditionedWeekMeanUSD":str(conditioned),
          "sourceFirstObservedUTC":row["first_observed_utc"].isoformat(),
          "originalForecastCreatedUTC":gen.isoformat(),
          "sourceForecastClass":SOURCE_CLASS,
          "evidenceClass":EVIDENCE,
          "notNewANNFit":True,
          "sourcePriceSha256":row["source_row_sha256"]})
        last_date=d
        expected+=timedelta(days=1)
    result["status"]="RESEARCH_FIVE_DAY_ESTIMATE_UP_TO_COMPLETED_WEEKDAY" if created else "BLOCKED_NO_COMPLETED_WEEKDAY_PUBLICATION"
    result["firstANNMeanUSD"]=str(fc)
    result["latestCompletedPriceDate"]=last_date.isoformat() if last_date else None
    result["latestConditionedMeanUSD"]=created[-1]["conditionedWeekMeanUSD"] if created else None
    result["newConditionedRows"]=len(created)
    return result,created

def source(now):
    uri=os.getenv("NEON_DATABASE_URL","")
    check(bool(uri),"NEON_DATABASE_URL_MISSING")
    monday=current_iso_monday(now.date())
    with psycopg.connect(uri,connect_timeout=15,
        row_factory=dict_row,options="-c default_transaction_read_only=on") as db:
        with db.cursor() as cur:
            cur.execute("""
             SELECT target_week,origin_week,model_id,feature_dim,training_weeks,
                    full_origin_week_complete,source_utc_day_reference,
                    is_prospective_firstprint,historical_source_vintage_certified,
                    generated_at_utc,forecast_week_mean_usd_oz
             FROM gold_weekly_live.staktrakr_v34_ann_shadow_v1
             WHERE target_week=%s
             ORDER BY generated_at_utc ASC LIMIT 1
            """,(monday,))
            fc=cur.fetchone()
            cur.execute("""
             SELECT DISTINCT ON (price_date)
                  price_date,spot_usd_oz,price_reference,evidence_class,
                  first_observed_utc,source_row_sha256
             FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
             WHERE metal='AU' AND price_date >= %s AND price_date < %s
               AND price_date < %s
               AND extract(isodow from price_date) BETWEEN 1 AND 4
             ORDER BY price_date,first_observed_utc ASC
            """,(monday,monday+timedelta(days=4),now.date()))
            spot=cur.fetchall()
    return fc,spot

def append(rows):
    if not rows:return 0
    uri=os.environ["NEON_DATABASE_URL"]
    query="""
      INSERT INTO gold_weekly_live.v34_ann_intraweek_estimates_v1
      (target_week,asof_price_date,observed_weekdays,remaining_weekdays,
       first_ann_mean_usd_oz,conditioned_week_mean_usd_oz,
       observed_price_sum_usd_oz,source_forecast_class,evidence_class,evidence)
      SELECT r.target_week,r.asof_price_date,r.observed_weekdays,r.remaining_weekdays,
       r.first_ann_mean_usd_oz,r.conditioned_week_mean_usd_oz,
       r.observed_price_sum_usd_oz,%s,%s,
       jsonb_build_object('notNewANNFit',true,'sourceFirstObservedUTC',
         r.source_observed,'originalForecastCreatedUTC',r.forecast_created,
         'sourcePriceSha256',r.source_sha,'model',
         'WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1')
      FROM jsonb_to_recordset(%s::jsonb) AS r(
        target_week date,asof_price_date date,observed_weekdays int,
        remaining_weekdays int,first_ann_mean_usd_oz numeric,
        conditioned_week_mean_usd_oz numeric,observed_price_sum_usd_oz numeric,
        source_observed timestamptz,forecast_created timestamptz,source_sha text)
      ON CONFLICT (target_week,asof_price_date,source_forecast_class) DO NOTHING
      RETURNING target_week
    """
    values=[{"target_week":r["targetWeek"],"asof_price_date":r["asOfPriceDate"],
      "observed_weekdays":r["observedWeekdays"],"remaining_weekdays":r["remainingWeekdays"],
      "first_ann_mean_usd_oz":r["firstANNMeanUSD"],
      "conditioned_week_mean_usd_oz":r["conditionedWeekMeanUSD"],
      "observed_price_sum_usd_oz":r["knownPriceSumUSD"],
      "source_observed":r["sourceFirstObservedUTC"],
      "forecast_created":r["originalForecastCreatedUTC"],
      "source_sha":r["sourcePriceSha256"]} for r in rows]
    with psycopg.connect(uri,connect_timeout=15) as db:
        with db.cursor() as cur:
            cur.execute(query,(SOURCE_CLASS,EVIDENCE,json.dumps(values)))
            written=len(cur.fetchall())
        db.commit()
    return written

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--write",action="store_true")
    a.add_argument("--out",default="gold_v34_daily_conditioning_report.json")
    opts=a.parse_args()
    now=datetime.now(timezone.utc)
    fc,prices=source(now)
    report,rows=evaluate(now,fc,prices)
    if opts.write and rows:
        report["newConditionedRowsWritten"]=append(rows)
    else:
        report["newConditionedRowsWritten"]=0
    Path(opts.out).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True),flush=True)

if __name__=="__main__":main()
