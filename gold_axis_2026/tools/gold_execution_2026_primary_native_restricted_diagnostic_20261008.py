"""Dukascopy primary-direct XAU/USD 2026 constrained coverage DIAGNOSTIC.

Predeclared promotion requirement of >=90 nights remains BINDING and FAIL if
direct native source has fewer mature nights. This is deliberately a separate
small-sample descriptive score, never a validated deployment champion.

Frozen 2020-25 Dukascopy-derived EV BID models; 2026 true direct Dukascopy M1
BID+ASK native 15-of-15 M15 to as-of 2026-10-08 17:00 Istanbul only.
No third-party mirror, no HistData, no future targets in training, no selection.
"""
from __future__ import annotations
import os,sys,time,json
from pathlib import Path
import pandas as pd,numpy as np,psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as base_data
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as price
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as vix
import gold_execution_2020_2025_training_start_sensitivity_20261008 as methods
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as primary
import gold_execution_2026_dukascopy_private_monthly_acquisition_20261008 as source
NAME="GOLD_EXECUTION_2026_PRIMARY_DUKASCOPY_RESTRICTED_NATIVE_SUBSET_20261008"
SUM=AX/(NAME+"_SUMMARY.json");MET=AX/(NAME+"_YEAR_METRICS.csv")
PAIR=AX/(NAME+"_PAIRED_HISTORY.csv");PRIVATE=AX/(NAME+"_DATED_PRIVATE.csv")
FREEZE=pd.Timestamp("2026-01-01")
END=pd.Timestamp("2026-10-08T13:45:00Z")
def load():
    q,t=base_data.source_load()
    if len(q)!=141890 or len(t)!=1549:raise RuntimeError("TRAIN_2020_25_CONTRACT_CHANGED")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as con:
      with con.cursor() as c:
        c.execute(f"""SELECT bar_start_utc,bid_open,bid_close,ask_open,ask_close,
                        m1_matched
              FROM {source.TABLE}
              WHERE source_id=%s AND bar_start_utc>='2026-01-01'
                 AND bar_start_utc<='2026-10-08 13:45:00+00'
              ORDER BY bar_start_utc""",(source.SOURCE,))
        records=c.fetchall()
    if len(records)<1000:raise RuntimeError("NO_DIRECT_PRIMARY_2026_SOURCE")
    z=pd.DataFrame(records,columns=["ts","bid_open","bid_close","ask_open","ask_close","n_native"])
    z.ts=pd.to_datetime(z.ts,utc=True)
    if not (z.n_native==15).all():raise RuntimeError("NON_NATURAL_MINUTE_BAR")
    if z.ts.duplicated().any():raise RuntimeError("PRIMARY_2026_DUPLICATE")
    if (z.ask_close<z.bid_close).any():raise RuntimeError("CROSSED_DIRECT_SOURCE")
    dow=z.ts.dt.dayofweek
    if ((dow==5)|((dow==6)&(z.ts.dt.hour<21))).any():
      raise RuntimeError("DEFINITELY_CLOSED_MARKET_PRIMARY_BARS")
    q2026=z.set_index("ts")[["bid_open","bid_close"]].rename(
        columns={"bid_open":"open","bid_close":"close"})
    tl,qc=primary.candidate_targets(t,q2026)
    return q,t,q2026,tl,qc

def score(z):
    rows=[]
    counts={}
    for target in ("DAY","OVN"):
      pool=z[z.target==target].sort_values("date")
      test=pool[pool.year==2026].copy()
      counts[target]={"eligible_matched_origin_features_and_labels":len(test)}
      if len(test)<28:continue
      for start in methods.HISTORIES:
        tr=pool[(pool.year>=start)&(pool.date<FREEZE)].copy()
        if target=="OVN":tr=tr[tr.next_date<=FREEZE]
        if len(tr)<450 or tr.y.nunique()!=2:raise RuntimeError("PRE_2026_TRAIN_SET_FAIL")
        for model in methods.MODELS:
          cols=((price.BASE_DAY if target=="DAY" else price.BASE_OVN)
                if model=="BASE_LOGIT" else methods.COLUMNS[model])
          if tr[cols].isna().any().any() or test[cols].isna().any().any():
            raise RuntimeError("UNCONTROLLED_MISSING_MODEL_FEATURE")
          clf=methods.method_fit(tr[cols].to_numpy(float),tr.y.to_numpy(int),model)
          ps=np.clip(clf.predict_proba(test[cols].to_numpy(float))[:,1],1e-6,1-1e-6)
          for r,prob in zip(test.itertuples(index=False),ps):
            rows.append({"date":r.date.strftime("%Y-%m-%d"),
              "year":2026,"month":r.date.strftime("%Y-%m"),
              "target":target,"train_start":start,"model":model,
              "y":int(r.y),"pred":int(prob>=.5),"p_up":float(prob),
              "n_train":len(tr),"score_source":"DIRECT_DUKASCOPY_PRIMARY_NATIVE_M1",
              "2026_training":False,"population":"RESTRICTED_PRIMARY_QC_SUBSET"})
    return pd.DataFrame(rows),counts

def main():
    tic=time.monotonic()
    rep={"status":"PRIMARY_NATIVE_DIAGNOSTIC_NOT_STARTED",
         "asof":"2026-10-08","primary_2026_source":source.SOURCE,
         "pre_registered_90_night_promotion_gate_still_enforced":True,
         "research_scope":"SECONDARY_LOW_N_EXTERNAL_FIRST_PARTY_SENSITIVITY",
         "bank_price_execution_ready":False,"2026_is_not_unseen":True}
    try:
      q,t,q2026,tl,qc=load()
      rep["native_direct_2026_m15"]=len(q2026)
      rep["native_source_label_quality"]=qc
      rep["pre_registered_2026_overnight_promotable"]=bool(
          qc["raw_2026_regular_overnight_approved"]>=90)
      if rep["pre_registered_2026_overnight_promotable"]:
          rep["sample_status"]="PROMOTION_COUNT_GATE_PASSED_BUT_OTHER_2026_GATES_STILL_OPEN"
      else:rep["sample_status"]="OVN_LT90_NOT_ELIGIBLE_FOR_CHAMPION_CLAIM"
      full=pd.concat([q,q2026]).sort_index()
      targets=pd.concat([t,tl],ignore_index=True).sort_values("date")
      z=price.features(full,targets,min_year=2020,max_year=2026,
           gvz_csv=methods.GVZ_FULL)
      z=vix.joined(z)
      p,cnt=score(z)
      rep["model_eligible_counts"]=cnt
      if p.empty:raise RuntimeError("NO_2026_MATURED_MODEL_SCORE_CASES")
      if p.groupby(["target","model"]).train_start.nunique().min()!=3:
          raise RuntimeError("HISTORIES_NOT_PAIRED")
      metrics=methods.metrics(p);pairs=methods.paired(p)
      rep["actual_yearly_score_windows"]=sorted(p.target.unique())
      rep["models"]=list(methods.MODELS)
      rep["starts"]=list(methods.HISTORIES)
      rep["primary_source_vs_third_party_publisher"]="DIRECT_BROKER_PRIMARY_ONLY"
      rep["score_total_research_predicted_rows"]=len(p)
      rep["source_authority"]="Direct Dukascopy M1 BID ASK, 15 observed native minute bars per 15m, specific maturities only"
      rep["2026_no_training_or_feature_selection"]=True
      rep["promoted_to_trading"]="NO"
      rep["status"]="2026_DIRECT_DUKASCOPY_PRIMARY_RESTRICTED_DIAGNOSTIC_EXECUTED"
      MET.write_text(metrics.to_csv(index=False))
      PAIR.write_text(pairs.to_csv(index=False))
      PRIVATE.write_text(p.to_csv(index=False))
      print("PRIMARY_ONLY_2026_RESTRICTED_ACTUAL_METRICS",metrics.to_string(index=False),flush=True)
      print("PRIMARY_ONLY_2026_TRAIN_HISTORY_PAIRED",pairs.to_string(index=False),flush=True)
    except Exception as ex:
      rep["status"]="2026_PRIMARY_NATIVE_RESTRICTED_RUN_BLOCKED"
      rep["blocking_reason"]=type(ex).__name__+":"+str(ex)[:140]
    rep["elapsed_seconds"]=int(time.monotonic()-tic)
    SUM.write_text(json.dumps(rep,indent=2,default=str)+"\n")
    print("PRIMARY_2026_DIRECT_QC_STATUS",json.dumps(rep,default=str),flush=True)
if __name__=="__main__":main()
