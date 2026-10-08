"""2026 as-of Oct 8 truly frozen-price-history direction holdout on SAME Dukascopy
upstream feed, pending independent direct BID/ASK M1 -> M15 year-boundary audit.

NO 2026 result is considered certified if 2025 overlap/source checks fail.
Full 2026 Direct Dukascopy is PRIVATE Neon candidate; no bid/ask levels in Git.
Original 2020-25 Dukascopy-derived EV candidate, original targets intact.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import date,timedelta
from pathlib import Path
import json,time,sys
import numpy as np,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_dukascopy_independent_xau_pilot_20261008 as direct
import gold_execution_2020_2025_all_existing_model_replay_20261008 as old
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
import gold_execution_2020_2025_training_start_sensitivity_20261008 as train2020

ASOF=date(2026,10,8)
BEGIN=date(2026,1,1)
SRC2026="DUKASCOPY_DIRECT_XAUUSD_M1_BIDASK_2026_ASOF_20261008_RESEARCH"
NAME="GOLD_EXECUTION_2026_FROZEN_HISTORY_SAME_VENDOR_CHALLENGE_20261008"
SUMMARY=AX/(NAME+"_SUMMARY.json")
YEAR_MET=AX/(NAME+"_YEARLY_METRICS.csv")
MONTH_MET=AX/(NAME+"_MONTHLY_METRICS.csv")
PAIRED=AX/(NAME+"_PAIRED_HISTORY.csv")
PROVENANCE=AX/(NAME+"_DATA_QC.json")
PRIVATE=AX/(NAME+"_DATED_PREDICTIONS_PRIVATE.csv")
QC_PRICE=AX/(NAME+"_PRIVATE_2026_DIRECT_BIDASK_M15.csv")
LOCKED_MODELS=train2020.MODELS
LOCKED_HISTORIES=train2020.HISTORIES
MIN_SOURCE_QUOTE_OVERLAP=500

def save_blocked(reason,extra=None):
    d={"status":"BLOCKED_NO_AUTHORIZED_2026_DIRECTION_SCORE",
       "reason":reason,"source_2026":SRC2026,"asof":"2026-10-08",
       "source_label_training_identity":"EV Trading Labs Dukascopy 2020-25 + direct Dukascopy M1 2026",
       "source_cross_vendor_mixing":False,"not_a_2026_model_success_claim":True}
    if extra:d.update(extra)
    SUMMARY.write_text(json.dumps(d,indent=2,default=str)+"\n")
    print("2026_FROZEN_SCORE_BLOCKED",json.dumps(d,default=str),flush=True)
    return

def fetch_daily(d):
    a={}
    for side in ("BID","ASK"):
        frame,info=direct.pull(d.isoformat(),side)
        a[side]=(frame,info)
    if a["BID"][0] is None or a["ASK"][0] is None:
        return d,None,{"status":"MISSING_OR_INVALID_BID_OR_ASK",
              "bid":a["BID"][1].get("result"),"ask":a["ASK"][1].get("result")}
    try:
        m,gate=direct.derive(a["BID"][0],a["ASK"][0])
        if m.empty:return d,None,{"status":"EMPTY_OR_MARKET_CLOSED"}
        if ((m.bar_start_utc.dt.dayofweek==5)|
            ((m.bar_start_utc.dt.dayofweek==6)&(m.bar_start_utc.dt.hour<21))).any():
            raise RuntimeError("BARS_INSIDE_DEFINITELY_CLOSED_SPOT_MARKET")
        return d,m,{"status":"QC_ACCEPTED","m15_all":len(m),
            "m15_native_15":int((m.m1_matched==15).sum()),
            "m15_native_ge14":int((m.m1_matched>=14).sum()),
            "median_spread_bps":gate.get("median_spread_bps")}
    except Exception as e:
        return d,None,{"status":"REJECTED_GEOMETRY_OR_BIDASK","error_type":type(e).__name__}

def batch(dates,max_workers=6):
    accepted={};qc={}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures={pool.submit(fetch_daily,d):d for d in dates}
        for f in as_completed(futures):
            d,frame,info=f.result()
            qc[d.isoformat()]=info
            if frame is not None:accepted[d]=frame
    return accepted,qc

def overlap_check(q_2025,overlap):
    sample=[]
    for d,m in overlap.items():
        native=m[m.m1_matched>=14].copy().set_index("bar_start_utc")
        benchmark=q_2025.loc[q_2025.index.date==d,["open","close"]]
        shared=benchmark.join(native[["bid_open","bid_close"]],
             how="inner",validate="one_to_one")
        for original,new in [("open","bid_open"),("close","bid_close")]:
            delta=(10000*np.abs(shared[original].to_numpy(float)-shared[new].to_numpy(float))
                /shared[original].to_numpy(float))
            sample.extend([float(x) for x in delta])
    n=len(sample)
    status=n>=MIN_SOURCE_QUOTE_OVERLAP and float(np.median(sample))<=.3 and float(np.quantile(sample,.95))<=3
    return {"matched_2025_bid_price_cells":n,
            "median_abs_bid_diff_bps":float(np.median(sample)) if n else None,
            "p95_abs_bid_diff_bps":float(np.quantile(sample,.95)) if n else None,
            "same_upstream_source_threshold_pass":bool(status),
            "source_quote_comparator":"2020-2025 stored EVTradingLabs Dukascopy BID M15 versus newly downloaded direct Dukascopy M1 resampled M15"}

def candidate_targets(previous,q2026):
    # DAY must have each 15m bar 09:00..16:45, all key anchors 15 native minutes.
    # OVN normal Tue-Thu decisions with exact next-morning anchor and sufficient
    # open intervals, do not silently pool Friday->Monday 64h.
    dates=sorted(set(x.date() for x in q2026.index
                     if x.hour==6 and x.minute==0 and x.date()<=ASOF))
    result=[];gates={}
    idx=q2026.index
    for i,dt in enumerate(dates):
        d=pd.Timestamp(dt,tz="UTC")
        start=d+pd.Timedelta(hours=6)
        end=d+pd.Timedelta(hours=13,minutes=45)
        dt_next=dates[i+1] if i+1<len(dates) else None
        anchor_day=(start in idx and end in idx)
        day_slots=pd.date_range(start,end,freq="15min")
        full_day=anchor_day and day_slots.isin(idx).all()
        # When all 32 bars exist, DAY return uses bar-start OPEN at 09TR and
        # last 15min CLOSE at 17TR (matured at 14:00 UTC).
        day=float(np.log(q2026.at[end,"close"]/q2026.at[start,"open"])) if full_day else np.nan
        overnight=np.nan
        overnight_gate="SOURCE_GAP_OR_UNMATURED"
        if dt_next is not None:
            nextday=pd.Timestamp(dt_next,tz="UTC")
            is_regular=(nextday-d==pd.Timedelta(days=1)) and d.dayofweek!=4
            tail=nextday+pd.Timedelta(hours=5,minutes=45)
            st=d+pd.Timedelta(hours=14)
            if is_regular and st in idx and tail in idx:
                # Normal next weekday hold, observed 17TR open and next09TR end.
                # Reject if severely incomplete within 16h, accounting for
                # usual documented evening trading break.
                actual=q2026.loc[(q2026.index>=st)&(q2026.index<=tail)]
                if len(actual)>=48:
                    overnight=float(np.log(q2026.at[tail,"close"]/q2026.at[st,"open"]))
                    overnight_gate="COMPLETE_SINGLE_SOURCE"
        row={"date":pd.Timestamp(dt),"year":dt.year,
             "next_date":pd.Timestamp(dt_next) if dt_next else pd.NaT,
             "y_DAY":float(day>0) if np.isfinite(day) else np.nan,
             "y_OVN":float(overnight>0) if np.isfinite(overnight) else np.nan,
             "ret_DAY":day,"ret_OVN":overnight,
             "day_gate":"COMPLETE_SINGLE_SOURCE" if full_day else "SOURCE_GAP_OR_UNMATURED",
             "overnight_gate":overnight_gate}
        result.append(row)
        gates[str(dt)]={"day":row["day_gate"],"overnight":overnight_gate}
    z=pd.DataFrame(result)
    if z.empty:raise RuntimeError("NO_2026_RAW_SOURCE_DATES")
    return z,{
        "raw_2026_issue_candidates":len(z),
        "raw_2026_day_approved":int(z.ret_DAY.notna().sum()),
        "raw_2026_regular_overnight_approved":int(z.ret_OVN.notna().sum()),
        "first_eligible":str(z.date.min().date()),
        "last_eligible":str(z.date.max().date()),
        "qc_day_overnight_by_month":{str(k):{
               "issue_dates":len(g),
               "complete_day":int(g.ret_DAY.notna().sum()),
               "complete_overnight":int(g.ret_OVN.notna().sum())
           } for k,g in z.groupby(z.date.dt.strftime("%Y-%m"))}
    }

def train_and_score(qfull,tfull):
    z=b.features(qfull,tfull,min_year=2020,max_year=2026,gvz_csv=train2020.GVZ_FULL)
    z=v.joined(z)
    out=[]
    for target in ("DAY","OVN"):
        pool=z[z.target==target].sort_values("date")
        check=pool[pool.year==2026].copy()
        if len(check)<90:raise RuntimeError("2026_"+target+"_ACCEPTED_MODEL_SAMPLE_TOO_SPARSE")
        for start in LOCKED_HISTORIES:
            training=pool[(pool.year>=start)&(pool.date<pd.Timestamp("2026-01-01"))]
            if target=="OVN":training=training[training.next_date<=pd.Timestamp("2026-01-01")]
            if training.y.nunique()!=2 or len(training)<500:raise RuntimeError("HISTORY_FIT_NOT_MATURE")
            if not (training.date<check.date.min()).all():raise RuntimeError("2026_TRAINING_HINDSIGHT")
            for model in LOCKED_MODELS:
                cols=(b.BASE_DAY if target=="DAY" else b.BASE_OVN) if model=="BASE_LOGIT" else train2020.COLUMNS[model]
                if training[cols].isna().any().any() or check[cols].isna().any().any():
                    raise RuntimeError("MISSING_MODEL_FEATURE_UNDOCUMENTED")
                f=train2020.method_fit(training[cols].to_numpy(float),training.y.to_numpy(int),model)
                ps=np.clip(f.predict_proba(check[cols].to_numpy(float))[:,1],1e-6,1-1e-6)
                for r,p in zip(check.itertuples(index=False),ps):
                    out.append({"date":r.date.strftime("%Y-%m-%d"),"month":r.date.strftime("%Y-%m"),
                        "year":2026,"target":target,"train_start":start,"model":model,
                        "pred":int(p>=.5),"y":int(r.y),"p_up":float(p),
                        "n_train":len(training),"fit_end":"2025-12-31_FROZEN",
                        "2026_was_used_in_training":False})
    p=pd.DataFrame(out)
    for (target,model),g in p.groupby(["target","model"]):
        sets=[frozenset(x.date) for _,x in g.groupby("train_start")]
        if len(set(sets))!=1:raise RuntimeError("2026_PAIRED_SAME_DATES_FAILED")
    return p

def main():
    tic=time.monotonic()
    qold,told=old.source_load()
    sample=[date(2025,12,d) for d in (9,10,11,12,15,16,17,18)]
    frames,qc=batch(sample,max_workers=6)
    ov=overlap_check(qold,frames)
    if not ov["same_upstream_source_threshold_pass"]:
        return save_blocked("2025_PUBLIC_PRIMARY_BID_CLOSE_OVERLAP_GATE_FAIL",
             {"source_2025_overlap":ov,"source_samples":qc})
    days=[];day=BEGIN
    while day<=ASOF:
        if day.weekday()<5:days.append(day)
        day+=timedelta(days=1)
    retrieved,qcs=batch(days,max_workers=6)
    frames=[retrieved[k] for k in sorted(retrieved)]
    if not frames:return save_blocked("2026_DIRECT_DUKASCOPY_CANDLES_UNAVAILABLE",{"2025_overlap":ov})
    allm=pd.concat(frames,ignore_index=True).sort_values("bar_start_utc")
    if allm.bar_start_utc.duplicated().any():raise RuntimeError("2026_DUPLICATE_MIN15")
    full_m15=allm[allm.m1_matched>=14].copy()
    q2026=full_m15.set_index("bar_start_utc")[["bid_open","bid_close"]].rename(
        columns={"bid_open":"open","bid_close":"close"})
    # No later than mature 17TR close on October 8 2026.
    maturity_cut=pd.Timestamp("2026-10-08T14:00:00Z")-pd.Timedelta(minutes=15)
    q2026=q2026[q2026.index<=maturity_cut].copy()
    if len(q2026)<11000:return save_blocked("2026_DUKASCOPY_PRIMARY_RAW_COVERAGE_THIN",
          {"2025_overlap":ov,"primary_2026_m15":len(q2026)})
    t2026,labqc=candidate_targets(told,q2026)
    qcinfo={"status":"2026_DIRECT_PRIMARY_SOURCE_2025_OVERLAP_PASSED",
      "2025_overlap":ov,"source_2026":SRC2026,
      "asof":"2026-10-08","last_bar_start_matured_cut_utc":str(maturity_cut),
      "requested_weekdays":len(days),"successful_direct_vendor_days":len(retrieved),
      "2026_m15_raw":len(allm),"2026_m15_approved_native_ge14":len(q2026),
      "provider_download_day_receipts":qcs,"2026_label_quality":labqc,
      "no_price_quote_data_ever_committed_public":True}
    PROVENANCE.write_text(json.dumps(qcinfo,indent=2,default=str)+"\n")
    if labqc["raw_2026_day_approved"]<90 or labqc["raw_2026_regular_overnight_approved"]<90:
        return save_blocked("2026_ELIGIBLE_MATURED_LABEL_COUNT_TOO_LOW",
                    {"2025_overlap":ov,"label_quality":labqc})
    # Source lineages separated even when the upstream is Dukascopy.
    qfull=pd.concat([qold,q2026]).sort_index()
    if qfull.index.duplicated().any():raise RuntimeError("2025_2026_BAR_OVERLAP_CONFLICT")
    tfull=pd.concat([told,t2026],ignore_index=True).sort_values("date").reset_index(drop=True)
    if tfull.date.duplicated().any():raise RuntimeError("2025_2026_ORIGIN_DUPLICATES")
    p=train_and_score(qfull,tfull)
    m=train2020.metrics(p)
    if not ((m.year==2026).all() and p.year.eq(2026).all()):
        raise RuntimeError("WRONG_OUTCOME_YEAR")
    by_month=[]
    for (month,target,start,model),g in p.groupby(["month","target","train_start","model"]):
        yy=g.y.to_numpy(int);pp=g.pred.to_numpy(int);prob=g.p_up.to_numpy(float)
        # Month with a single class must not be assigned a fake 50% balanced score.
        down=np.mean(pp[yy==0]==0) if (yy==0).any() else np.nan
        up=np.mean(pp[yy==1]==1) if (yy==1).any() else np.nan
        by_month.append({"month":month,"target":target,"train_start":start,"model":model,
             "n":len(g),"accuracy":float(np.mean(pp==yy)),
             "balanced_accuracy":float(.5*(up+down)) if np.isfinite(up) and np.isfinite(down) else np.nan,
             "down_recall":float(down),"up_recall":float(up),
             "brier":float(np.mean((prob-yy)**2)),
             "two_class_month":bool(np.isfinite(up) and np.isfinite(down))})
    qmonth=pd.DataFrame(by_month)
    pa=train2020.paired(p)
    report={"status":"2026_FROZEN_SAME_UPSTREAM_DIRECT_DUKASCOPY_RESEARCH_HOLDOUT_COMPLETE",
      "asof":"2026-10-08","2025_direct_primary_overlap":ov,
      "source_2026":"DUKASCOPY_PUBLIC_M1_DIRECT_BIDASK_2026_CANDIDATE_NOT_ORIGINAL_EV_MIRROR",
      "historical_2020_2025":old.SOURCE,
      "source_fidelity":"matched 2025 upstream M15, direct 2026 independently native-minute vetted",
      "raw_2026_m15_approved":len(q2026),"target_gates":labqc,
      "training_histories":list(LOCKED_HISTORIES),"models":list(LOCKED_MODELS),
      "refit_rule":"2020-25 fixed through 2025-12-31; no 2026 labels/training/tuning",
      "excluded":"2026 days with source gaps, no matured bar, Fri->Mon 64h OVN",
      "2026_months_only_through_oct_08":True,
      "not_a_live_bank_bidask_PnL":True,
      "2026_followup_model_selection_invalidates_holdout":True,
      "elapsed_seconds":int(time.monotonic()-tic)}
    SUMMARY.write_text(json.dumps(report,indent=2,default=str)+"\n")
    YEAR_MET.write_text(m.to_csv(index=False))
    MONTH_MET.write_text(qmonth.to_csv(index=False))
    PAIRED.write_text(pa.to_csv(index=False))
    PRIVATE.write_text(p.to_csv(index=False))
    QC_PRICE.write_text(full_m15.to_csv(index=False))
    print("2026_FROZEN_HOLDOUT_RESULTS",json.dumps(report,default=str),flush=True)
    print(m.to_string(index=False),flush=True)
    print("2026_HISTORY_PAIRED",pa.to_string(index=False),flush=True)
if __name__=="__main__":main()
