#!/usr/bin/env python3
"""Read-only five-stage GOLD operational acceptance gate.

PASS of this audit means the audit ran, NEVER that a live model exists.
No model fitting, trading, signal publication, backdating, or Neon writes.
Source timestamps and original model checkpoint proof are required separately.
"""
from __future__ import annotations
import argparse
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REQUIRED={
 "XAU_EOD_TWELVE_NY17":("APPROVED_CANONICAL_TWELVE_NY17",2),
 "GVZ_CBOE":("APPROVED_AUTHORITY_RETRIEVAL_FLOOR",3),
 "VIX_CBOE":("APPROVED_AUTHORITY_RETRIEVAL_FLOOR",3),
 "DGS10_FRB_H15":("APPROVED_DIRECT_AUTHORITY",4),
 "EFFR_NYFED":("APPROVED_DIRECT_AUTHORITY",4),
}
METALS=("AU","AG","PT","PD")
MODEL="WEEKLY_H1_ANN_MLP8_TANH_ALPHA1_V1"

def monday_after(now):
    today=now.astimezone(timezone.utc).date()
    return today+timedelta(days=7-today.weekday())

def business_lag(d,today):
    if d>today: raise ValueError("FUTURE_OBSERVATION")
    n=0
    while d<today:
        d+=timedelta(days=1)
        n+=d.weekday()<5
    return n

def feed_audit(now,rows):
    last={r["series_id"]:r for r in rows}
    output=[]
    for name,(accepted,max_lag) in REQUIRED.items():
        r=last.get(name)
        if not r:
            output.append({"series":name,"status":"MISSING"})
            continue
        ts=r["observation_ts"]
        if isinstance(ts,str): ts=datetime.fromisoformat(ts.replace("Z","+00:00"))
        if ts.tzinfo is None or ts>now:
            output.append({"series":name,"status":"INVALID_ASOF"})
            continue
        lag=business_lag(ts.astimezone(timezone.utc).date(),now.date())
        state=("UNAPPROVED" if r["quality_status"]!=accepted else
               "STALE" if lag>max_lag else "READY")
        output.append({"series":name,"status":state,"latest":ts.isoformat(),
                       "businessLag":lag,"maxBusinessLag":max_lag})
    return {"status":"READY" if all(x["status"]=="READY" for x in output) else "BLOCKED",
            "series":output}

def four_metal_audit(now,rows):
    target=monday_after(now)
    start=target-timedelta(days=7)
    friday=start+timedelta(days=4)
    cutoff=datetime.combine(friday+timedelta(days=1),datetime.min.time(),tzinfo=timezone.utc)
    by_day={}
    issues=[]
    for r in rows:
        d=r["price_date"]
        if isinstance(d,str): d=date.fromisoformat(d)
        metal=r["metal"]
        if d<start or d>friday or metal not in METALS: issues.append("OUT_OF_RANGE")
        elif metal in by_day.setdefault(d,{}): issues.append("DUPLICATE")
        else: by_day[d][metal]=r
    aligned=[d for d in sorted(by_day) if d.weekday()<5 and len(by_day[d])==4]
    unverified=[]
    capture_errors=[]
    for d in aligned:
        for metal in METALS:
            r=by_day[d][metal]
            if r["evidence_class"]!="FIRSTPRINT_PROSPECTIVE":
                unverified.append(f"{d}:{metal}:{r['evidence_class']}")
            ts=r.get("first_observed_utc")
            if isinstance(ts,str): ts=datetime.fromisoformat(ts.replace("Z","+00:00"))
            if ts is None or ts.tzinfo is None or ts>now:
                capture_errors.append(f"{d}:{metal}")
    if now<cutoff: state="WAIT_FOR_ORIGIN_FRIDAY_UTC_COMPLETION"
    elif issues: state="BLOCKED_INVALID_ORIGIN_ROWS"
    elif len(aligned)<3: state="BLOCKED_INSUFFICIENT_FOUR_METAL_OVERLAP"
    elif unverified: state="BLOCKED_PUBLIC_SNAPSHOT_NOT_FIRSTPRINT"
    elif capture_errors: state="BLOCKED_INVALID_CAPTURE_TIME"
    else: state="INPUT_CANDIDATE_MODEL_NOT_VERIFIED"
    return {"status":state,"targetWeek":str(target),"originWeek":str(start),
            "originFridayUtcCompleteAfter":cutoff.isoformat(),
            "alignedDays":len(aligned),"alignedDates":list(map(str,aligned)),
            "unverifiedSourceRows":len(unverified),"invalidCaptureRows":len(capture_errors),
            "rowIssues":sorted(set(issues)),"minimumSharedDays":3,
            "priceDefinition":"STAKTRAKR_UTC_DAY_FOUR_METAL_NOT_XAU_NY17"}

def evaluate(now,feeds,metals,stats):
    market=feed_audit(now,feeds)
    four=four_metal_audit(now,metals)
    weekly=int(stats["weekly_live"])
    risk=int(stats["risk_live"])
    monthly_latest=stats.get("monthly_input_latest")
    monthly_fc=stats.get("monthly_forecast_latest")
    return {
      "schema":"GOLD_FIVE_STAGE_OPERATIONAL_ACCEPTANCE_V1",
      "asOfUTC":now.isoformat(),
      "status":"BLOCKED_NOT_LIVE",
      "stage1Data":{"status":"RESEARCH_FEEDS_READY_NOT_ORIGIN_CERTIFIED" if market["status"]=="READY" else "BLOCKED_SOURCE_FRESHNESS",
                    "canonicalFiveSeries":market,"sameSourceFourMetal":four,
                    "monthlyModelInputLatest":str(monthly_latest) if monthly_latest else None,
                    "monthlyInputCutoffBehindCurrentMonth":not monthly_latest or monthly_latest<date(now.year,now.month,1)},
      "stage2Forecasts":{"status":"BLOCKED_NO_VERIFIED_LIVE_FORECAST_EXECUTORS",
         "weeklyLiveRecords":weekly,"nextOrigin":four["originWeek"],
         "monthlyLatestForecastMonth":str(monthly_fc) if monthly_fc else None,
         "required":["four_metal_origin_firstprint","original_ANN_weights_and_normalizer",
                     "original_monthly_eight_feature_vector_hash","frozen_prospective_prediction_proof"]},
      "stage3Risk":{"status":"BLOCKED_NO_VERIFIED_LIVE_RISK_ISSUER",
         "liveRiskRecords":risk,"required":["original_BASE14_CFTC21_V22_asof",
                             "seven_rules_and_prior_day_state","firstprint_signal_capture"]},
      "stage4Positioning":{"status":"BLOCKED_NO_PROVEN_FORWARD_BACKTEST",
         "buyFee":0.008,"sellFee":0.008,"calibration":"2024-2025_ONLY",
         "evaluation":"2026_OUT_OF_SAMPLE","ordersAllowed":False},
      "stage5Application":{"status":"UNVERIFIED_REQUIRES_INDEPENDENT_APP_CI",
                            "researchArchiveIsNotLive":True},
      "neonWrites":False,"forecastWrites":False,"tradeAuthorized":False,
      "promotionAllowed":False,
    }

def from_neon(now):
    import psycopg
    from psycopg.rows import dict_row
    uri=os.getenv("NEON_DATABASE_URL","").strip()
    if not uri: raise RuntimeError("MISSING_NEON_DATABASE_URL")
    target=monday_after(now); start=target-timedelta(days=7)
    with psycopg.connect(uri,row_factory=dict_row,connect_timeout=15,
                         options="-c default_transaction_read_only=on") as db:
      with db.cursor() as cur:
        cur.execute("""
          SELECT DISTINCT ON (series_id) series_id,observation_ts,quality_status
          FROM public.canonical_latest WHERE series_id=ANY(%s)
          ORDER BY series_id,observation_ts DESC
        """,(list(REQUIRED),))
        feeds=cur.fetchall()
        cur.execute("""
          SELECT DISTINCT ON (price_date,metal) price_date,metal,evidence_class,
                first_observed_utc
          FROM gold_weekly_live.staktrakr_daily_utc_reference_v1
          WHERE price_date BETWEEN %s AND %s
          ORDER BY price_date,metal,first_observed_utc ASC
        """,(start,start+timedelta(days=4)))
        metals=cur.fetchall()
        cur.execute("""
          SELECT (SELECT count(*) FROM gold_weekly_live.weekly_forecast_records) AS weekly_live,
                 (SELECT count(*) FROM gold_weekly_live.downside_signal_records) AS risk_live,
                 (SELECT max(observed_month) FROM gold_monthly_h1.monthly_metal_observations) AS monthly_input_latest,
                 (SELECT max(target_month) FROM gold_monthly_h1.forecast_records) AS monthly_forecast_latest
        """)
        stats=cur.fetchone()
    return evaluate(now,feeds,metals,stats)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="gold-five-stage-operational-audit.json")
    p.add_argument("--strict",action="store_true",
                   help="Exit 3 while not certified live (intended for go-live checks)")
    a=p.parse_args()
    report=from_neon(datetime.now(timezone.utc))
    Path(a.out).write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n")
    print(json.dumps(report,ensure_ascii=False,indent=2,default=str))
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf8") as f:
            f.write("## GOLD five-stage acceptance (read-only)\n\n")
            f.write("| Stage | Result |\n|---|---|\n")
            for i,name in enumerate(("stage1Data","stage2Forecasts","stage3Risk",
                                     "stage4Positioning","stage5Application"),1):
                f.write(f"| {i} | {report[name]['status']} |\n")
            f.write("\n**Audit workflow success is not live-model approval.**\n")
    return 3 if a.strict and report["status"]!="READY" else 0
if __name__=="__main__": raise SystemExit(main())
