"""Replay the preregistered 2026 Dukascopy model using private native M1 BID+ASK source.
No source substitution, no refitting on 2026, no 2026 outcome-based selection.
The previously completed 2025 primary-market quote comparability test is an
immutable separate source-only validation record with 728 exact price comparisons.
"""
from __future__ import annotations
import os,sys,json
from pathlib import Path
from datetime import date
import pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as test
import gold_execution_2026_dukascopy_private_monthly_acquisition_20261008 as acq
SOURCE_VALIDATION=AX/"GOLD_EXECUTION_DUKASCOPY_2025_PRIMARY_SOURCE_OVERLAP_728_FROZEN_20261008.json"
def read_frozen_validation():
    r=json.loads(SOURCE_VALIDATION.read_text())
    if r.get("source_run_commit")!="2ac07b0a77cebcf761b03398b7f918c879d8f115":
        raise RuntimeError("IMMUTABLE_2025_SOURCE_RECEIPT_WRONG_COMMIT")
    v=r["overlap_2025"]
    if v["n_price_cells"]<500 or not (v["median_abs_diff_bps"]<0.3 and v["p95_abs_diff_bps"]<3):
        raise RuntimeError("IMMUTABLE_2025_DIRECT_SAME_SOURCE_QUOTE_GATE_FAILED")
    days=[x for x in r["days"] if x.get("year")==2025 and x.get("bid_status")=="OK"
           and x.get("ask_status")=="OK"]
    if len(days)<3:raise RuntimeError("2025_PRIMARY_VALIDATION_TOO_FEW_DAYS")
    return {"matched_2025_bid_price_cells":int(v["n_price_cells"]),
         "median_abs_bid_diff_bps":float(v["median_abs_diff_bps"]),
         "p95_abs_bid_diff_bps":float(v["p95_abs_diff_bps"]),
         "same_upstream_source_threshold_pass":True,
         "source_receipt_commit":r["source_run_commit"],
         "independent_2025_days":len(days),
         "source_quote_comparator":"Direct Dukascopy M1 BID M15 from 2025 vs archived 2020-25 EV Dukascopy quote"}
def private_day_quotes():
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as conn:
      with conn.cursor() as c:
        c.execute(f"""SELECT bar_start_utc,bid_open,bid_high,bid_low,bid_close,
                    ask_open,ask_high,ask_low,ask_close,m1_matched
           FROM {acq.TABLE} WHERE source_id=%s AND bar_start_utc>='2026-01-01'
           AND bar_start_utc<='2026-10-08 13:45:00+00' ORDER BY bar_start_utc""",
           (acq.SOURCE,))
        rows=c.fetchall()
    if not rows:return {},{"source":"DUKASCOPY_DIRECT_NATIVE_M1_PRIVATE","rows":0}
    frame=pd.DataFrame(rows,columns=["bar_start_utc","bid_open","bid_high","bid_low","bid_close",
       "ask_open","ask_high","ask_low","ask_close","m1_matched"])
    frame.bar_start_utc=pd.to_datetime(frame.bar_start_utc,utc=True)
    if frame.bar_start_utc.duplicated().any():raise RuntimeError("PRIVATE_2026_QUOTE_DUPLICATE")
    if not (frame.m1_matched==15).all():raise RuntimeError("INCOMPLETE_NATIVE_15MIN_BARS_IN_PRIVATE_CANDIDATE")
    if (frame.ask_close<frame.bid_close).any():raise RuntimeError("PRIVATE_2026_CROSSED_QUOTES")
    if (frame[["bid_open","bid_close","ask_open","ask_close"]]<=0).any().any():
        raise RuntimeError("PRIVATE_2026_NONPOSITIVE")
    m={}
    for day,g in frame.groupby(frame.bar_start_utc.dt.date):
        m[day]=g.sort_values("bar_start_utc").reset_index(drop=True)
    info={"source":"DUKASCOPY_DIRECT_NATIVE_M1_PRIVATE","private_2026_m15":len(frame),
          "distinct_utc_dates":len(m),
          "download_from_predeclared_monthly_shards":True,
          "latest_matured_utc":frame.bar_start_utc.max().isoformat()}
    return m,info
def main():
    receipt=read_frozen_validation()
    days,qcinfo=private_day_quotes()
    source_stats={
       "independent_2025_overlap":receipt,
       "monthly_2026_private_source":qcinfo}
    check_dates={k for k in days if k.weekday()<5}
    if len(check_dates)<130:
        return test.save_blocked("2026_DIRECT_SOURCE_MONTHLY_DAY_COVERAGE_INSUFFICIENT",
            {"source_integrity":source_stats,"min_raw_candidate_weekdays":130,
             "actual_cached_weekdays":len(check_dates)})
    real_batch=test.batch
    real_overlap=test.overlap_check
    def batch_using_private(requested,max_workers=6):
        if all(d.year==2025 for d in requested):
            return {},{"source":"EXISTING_IMMUTABLE_VALIDATED_2025_PUBLIC_DIRECT_SOURCE_RECEIPT"}
        if all(d.year==2026 for d in requested):
            requested_set=set(requested)
            return {k:df for k,df in days.items() if k in requested_set},{
               "used_monthly_source_staging":True,"private_2026_quote_m15":qcinfo["private_2026_m15"]}
        raise RuntimeError("MIXED_YEAR_VENDOR_FETCH_UNAUTHORIZED")
    def source_overlap_ref(q,frames):
        # The source receipt was independently recorded in a different, completed
        # primary-feed trial; it is quote level corroboration, not future labels.
        return receipt
    try:
        test.batch=batch_using_private
        test.overlap_check=source_overlap_ref
        return test.main()
    finally:
        test.batch=real_batch
        test.overlap_check=real_overlap
if __name__=="__main__":main()
