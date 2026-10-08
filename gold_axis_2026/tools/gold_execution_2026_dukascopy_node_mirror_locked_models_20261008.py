"""Pre-2026 frozen original M15 models on 2026 third-party Dukascopy-node BID mirror.

This is conditional on TWO independent, pre-result price identity audits:
EVTradingLabs 2025 (the actual training publisher), and direct Dukascopy M1 2026
(same upstream broker). Public republisher fills closed-market minutes; these
and flat 15m intervals MUST be quarantined and never identified as native ticks.
Research-only cross-publisher same-upstream test; not primary-direct validation.
"""
from __future__ import annotations
from pathlib import Path
import os,sys,json,time
import numpy as np,pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as core
import gold_execution_2020_2025_all_existing_model_replay_20261008 as hist
import gold_execution_2020_2025_training_start_sensitivity_20261008 as spec
import gold_execution_2026_dukascopy_node_mirror_forensic_20261008 as cand
BASENAME="GOLD_EXECUTION_2026_DUKASCOPY_NODE_MIRROR_FIXED_MODELS_20261008"
SUMMARY=AX/(BASENAME+"_SUMMARY.json")
YEAR=AX/(BASENAME+"_YEAR_METRICS.csv")
MONTH=AX/(BASENAME+"_MONTH_METRICS.csv")
PAIRED=AX/(BASENAME+"_PAIRED_HISTORY.csv")
PRIVATE=AX/(BASENAME+"_DATED_PREDICTIONS_PRIVATE.csv")
AUDIT=cand.OUT

def blocked(reason,proof=None):
    report={"status":"BLOCKED_NO_APPROVED_2026_MIRROR_DIRECTION_SCORE",
            "reason":reason,"asof":"2026-10-08",
            "mirror_source":cand.SOURCE,"2026_prices_used_for_model_selection":False,
            "different_from_true_direct_primary_2026_m1":True,
            "2026_model_accuracy_claim":False}
    if proof:report["gate_proof"]=proof
    SUMMARY.write_text(json.dumps(report,indent=2)+"\n")
    print("MIRROR_MODEL_BLOCKED",json.dumps(report),flush=True)

def load_approved():
    if not AUDIT.exists():raise RuntimeError("MIRROR_SOURCE_QC_NOT_RECORDED")
    proof=json.loads(AUDIT.read_text())
    if proof.get("status")!="THIRD_PARTY_DUKASCOPY_MIRROR_SAMPLED_PRICE_GATES_PASS_RESEARCH_CANDIDATE":
        raise RuntimeError("2026_MIRROR_PRICE_SOURCE_GATE_NOT_PASSED")
    a=proof.get("2025_original_ev_quote_gate",{})
    b=proof.get("2026_direct_primary_overlap_gate",{})
    if not a.get("price_gate_pass") or not b.get("price_gate_pass"):
        raise RuntimeError("MIRROR_2025_2026_PRICE_OVERLAPS_FAILED")
    if min(a.get("matched_price_cells",0),b.get("matched_price_cells",0))<500:
        raise RuntimeError("SOURCE_SAMPLE_BELOW_PREREG_GATE")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as conn:
      with conn.cursor() as c:
        c.execute(f"""SELECT bar_start_utc,bid_open,bid_high,bid_low,bid_close,
                    ask_open,ask_high,ask_low,ask_close,matched_calendar_m1_count
               FROM {cand.TABLE} WHERE source_id=%s
               AND bar_start_utc >= '2026-01-01' AND bar_start_utc < '2026-08-21'
               ORDER BY bar_start_utc""",(cand.SOURCE,))
        rows=c.fetchall()
    if not rows:raise RuntimeError("MIRROR_PRIVATE_2026_PRICE_ROWS_NOT_FOUND")
    z=pd.DataFrame(rows,columns=["bar_start_utc","bid_open","bid_high","bid_low","bid_close",
                 "ask_open","ask_high","ask_low","ask_close","matched_calendar_m1_count"])
    z.bar_start_utc=pd.to_datetime(z.bar_start_utc,utc=True)
    if z.bar_start_utc.duplicated().any():raise RuntimeError("RESEARCH_MIRROR_DUPLICATE_M15")
    if not (z.matched_calendar_m1_count==15).all():
        raise RuntimeError("MIRROR_CALENDAR_M1_15BAR_NOT_COMPLETE")
    if ((z.bid_high-z.bid_low)<=0).any() or ((z.ask_high-z.ask_low)<=0).any():
        raise RuntimeError("MIRROR_STILL_CONTAINS_STATIC_FILL")
    if (z.ask_close<z.bid_close).any():raise RuntimeError("BID_ASK_CROSSED_2026")
    dow=z.bar_start_utc.dt.dayofweek
    if ((dow==5)|((dow==6)&(z.bar_start_utc.dt.hour<21))).any():
        raise RuntimeError("CLOSED_MARKET_15M_MIRROR_CONTAMINATION")
    return z,proof

def monthly_metric(p):
    rows=[]
    for (month,target,start,model),g in p.groupby(["month","target","train_start","model"]):
        y=g.y.to_numpy(int); pred=g.pred.to_numpy(int);pr=g.p_up.to_numpy(float)
        down=float(np.mean(pred[y==0]==0)) if (y==0).any() else None
        up=float(np.mean(pred[y==1]==1)) if (y==1).any() else None
        rows.append({"month":month,"target":target,"train_start":start,"model":model,
           "n":len(g),"accuracy":float(np.mean(pred==y)),
           "balanced_accuracy":float(.5*(up+down)) if up is not None and down is not None else None,
           "down_recall":down,"up_recall":up,
           "brier":float(np.mean((pr-y)**2)),"two_class_month":up is not None and down is not None})
    return pd.DataFrame(rows)

def main():
    now=time.monotonic()
    try:
        z,proof=load_approved()
        qold,told=hist.source_load()
        if len(qold)!=141890 or len(told)!=1549:
            raise RuntimeError("TRAINING_SOURCE_2020_25_CARDINALITY_CHANGED")
        q2026=z.set_index("bar_start_utc")[["bid_open","bid_close"]].rename(
            columns={"bid_open":"open","bid_close":"close"}).sort_index()
        # We know the public mirror's last published minute ends Aug 20.
        # Current-year Sep/Oct are NOT drawn from HistData, Twelve, or synthetic fills.
        if q2026.index.max()>pd.Timestamp("2026-08-20T23:59Z"):
            raise RuntimeError("2026_MIRROR_FUTURE_DATE_SOURCE_CONTAMINATION")
        t2026,labelq=core.candidate_targets(told,q2026)
        if labelq["raw_2026_day_approved"]<90 or labelq["raw_2026_regular_overnight_approved"]<90:
            raise RuntimeError("MIRROR_TARGETS_INSUFFICIENT_MATURED_2026")
        qfull=pd.concat([qold,q2026]).sort_index()
        if qfull.index.duplicated().any():raise RuntimeError("SOURCE_BOUNDARY_OVERLAP")
        tfull=pd.concat([told,t2026],ignore_index=True).sort_values("date")
        if tfull.date.duplicated().any():raise RuntimeError("MIRROR_DUPLICATE_DATES")
        p=core.train_and_score(qfull,tfull)
        if p.empty:raise RuntimeError("NO_MODEL_PREDICTIONS")
        m=spec.metrics(p)
        mm=monthly_metric(p)
        paired=spec.paired(p)
        if not ((p.year==2026).all() and
                p.groupby(["target","model"]).train_start.nunique().min()==3):
            raise RuntimeError("HISTORY_SCORE_PAIRED_CONTRACT_FAILED")
        result={"status":"2026_SAME_DUKASCOPY_UPSTREAM_CROSS_PUBLISHER_M15_RESEARCH_SCORE_COMPLETE",
            "asof":"2026-10-08","actual_2026_last_data_utc":q2026.index.max().isoformat(),
            "upstream_price_provider":"Dukascopy XAUUSD spot BID ASK",
            "historical_2020_2025_publisher":"EVTradingLabs derived Dukascopy",
            "2026_publisher":"Third party github dukascopy-node monthly M1",
            "2026_not_direct_primary_feed":True,
            "source_proof":{"ev2025":proof["2025_original_ev_quote_gate"],
                           "primary2026":proof["2026_direct_primary_overlap_gate"]},
            "closed_market_and_zero_range_m15_removed":True,
            "2026_M15_bar_count":len(q2026),
            "target_gates":labelq,
            "models":list(spec.MODELS),"training_start":list(spec.HISTORIES),
            "no_2026_training_targets":True,
            "2026_already_inspected_for_earlier_histdata_research":True,
            "bank_execution_PnL":False,
            "is_strict_direct_primary_2026_validation":False,
            "no_2026_sep_oct_data_from_this_mirror":True,
            "elapsed_seconds":int(time.monotonic()-now)}
        SUMMARY.write_text(json.dumps(result,indent=2,default=str)+"\n")
        YEAR.write_text(m.to_csv(index=False))
        MONTH.write_text(mm.to_csv(index=False))
        PAIRED.write_text(paired.to_csv(index=False))
        PRIVATE.write_text(p.to_csv(index=False))
        print("2026_MIRROR_MODEL_SCORE",json.dumps(result,default=str),flush=True)
        print("2026_YEARLY_METRICS",m.to_string(index=False),flush=True)
        print("2026_PAIRED_HISTORY",paired.to_string(index=False),flush=True)
    except Exception as e:
        blocked(type(e).__name__+":"+str(e)[:150])
if __name__=="__main__":main()
