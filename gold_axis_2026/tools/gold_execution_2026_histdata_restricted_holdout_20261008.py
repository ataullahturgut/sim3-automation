"""Separate HistData-only 2020-Sep2026 BID direction validation.
This is a RESTRICTED source sensitivity, not same-population as Dukascopy,
not bank-executable, not a license to pool distinct price-vintage labels.
"""
from __future__ import annotations
import os,sys,json,time
from pathlib import Path
import numpy as np,pandas as pd,psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_histdata_one_vendor_origin_gate_20261008 as h
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
import gold_execution_2020_2025_training_start_sensitivity_20261008 as history
NAME="GOLD_EXECUTION_2026_HISTDATA_RESTRICTED_SOURCE_FROZEN_HOLDOUT_20261008"
OUT=AX/(NAME+"_SUMMARY.json")
MET=AX/(NAME+"_YEAR_METRICS.csv")
MON=AX/(NAME+"_MONTH_METRICS.csv")
PAR=AX/(NAME+"_PAIRED_TRAIN_START.csv")
PRIVATE=AX/(NAME+"_DATED_PREDICTIONS_PRIVATE.csv")
LOCKED_MODELS=history.MODELS
LOCKED_START=history.HISTORIES
FREEZE=pd.Timestamp("2026-01-01")

def load_q_t():
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as con:
        q=h.load(con)
        t=h.make_labels(q)
        persisted=pd.read_sql_query(
            "SELECT issue_date,day_y,overnight_y FROM gold_research_xau_execution_origin_quality_candidate_v1 ORDER BY issue_date",
            con)
    if len(q)!=156366 or len(t)!=1739 or len(persisted)!=1739:
        raise RuntimeError("HISTDATA_FROZEN_SOURCE_CARDINALITY_CHANGES")
    persisted["date"]=pd.to_datetime(persisted.issue_date)
    t["date"]=pd.to_datetime(t.issue_date)
    check=t.merge(persisted[["date","day_y","overnight_y"]],on="date",
                  how="inner",validate="one_to_one",suffixes=("_rebuild","_stored"))
    if len(check)!=len(t):raise RuntimeError("HISTDATA_TARGET_DATES_MISMATCH")
    for yname in ("day_y","overnight_y"):
        a=check[yname+"_rebuild"]; bb=check[yname+"_stored"]
        if (a.fillna(-1)!=bb.fillna(-1)).any():
            raise RuntimeError("HISTDATA_FROZEN_TARGET_LABEL_DISAGREEMENT")
    year_counts=t.groupby("year").agg(total=("date","size"),
                          day=("day_y","count"),ovn=("overnight_y","count"))
    if year_counts.loc[2026,"day"]<185 or year_counts.loc[2026,"ovn"]<175:
        raise RuntimeError("2026_SOURCE_GOVERNED_TARGETS_MISSING")
    if year_counts.loc[2023,"day"]>=200:
        raise RuntimeError("2023_GAP_GOVERNANCE_UNEXPECTEDLY_CHANGED")
    old=q[["bar_start_utc","open_price","close_price"]].rename(columns={
        "bar_start_utc":"ts","open_price":"open","close_price":"close"})
    old.ts=pd.to_datetime(old.ts,utc=True)
    if old.ts.duplicated().any():raise RuntimeError("DUPLICATE_HISTDATA_BARS")
    result=old.set_index("ts").sort_index()
    targets=pd.DataFrame({
        "date":t.date,
        "year":t.year.astype(int),
        "next_date":pd.to_datetime(t.next_trading_date),
        "y_DAY":pd.to_numeric(t.day_y,errors="coerce"),
        "y_OVN":pd.to_numeric(t.overnight_y,errors="coerce"),
        "ret_DAY":pd.to_numeric(t.day_return,errors="coerce"),
        "ret_OVN":pd.to_numeric(t.overnight_return,errors="coerce"),
        "day_gate":np.where(t.day_gate.eq("OK"),"COMPLETE_SINGLE_SOURCE","SOURCE_GAP"),
        "overnight_gate":np.where(t.overnight_gate.eq("OK"),"COMPLETE_SINGLE_SOURCE","SOURCE_GAP")
    })
    return result,targets,year_counts.to_dict("index")

def get_fixed(z):
    out=[]
    for target in ("DAY","OVN"):
        data=z[z.target.eq(target)].sort_values("date").reset_index(drop=True)
        test=data[data.year.eq(2026)].copy()
        if len(test)<125:raise RuntimeError("2026_"+target+"_MODEL_FEATURE_POPULATION_TOO_SPARSE")
        for start in LOCKED_START:
            train=data[(data.year>=start)&(data.date<FREEZE)].copy()
            if target=="OVN":train=train[train.next_date<=FREEZE]
            if len(train)<450 or train.y.nunique()!=2:
                raise RuntimeError("INSUFFICIENT_HISTDATA_TRAINING_"+target)
            if train.date.max()>=test.date.min():raise RuntimeError("2026_LABEL_LEAKAGE")
            for model in LOCKED_MODELS:
                cols=((b.BASE_DAY if target=="DAY" else b.BASE_OVN)
                     if model=="BASE_LOGIT" else history.COLUMNS[model])
                if train[cols].isna().any().any() or test[cols].isna().any().any():
                    raise RuntimeError("UNTRACKED_FEATURE_NANS")
                f=history.method_fit(train[cols].to_numpy(float),train.y.to_numpy(int),model)
                probs=np.clip(f.predict_proba(test[cols].to_numpy(float))[:,1],1e-6,1-1e-6)
                for row,prob in zip(test.itertuples(index=False),probs):
                    out.append({"date":row.date.strftime("%Y-%m-%d"),
                                "month":row.date.strftime("%Y-%m"),"year":2026,
                                "train_start":start,"model":model,"target":target,
                                "n_train":len(train),"pred":int(prob>=.5),
                                "p_up":float(prob),"y":int(row.y),
                                "label_source":"HISTDATA_BID_QUALITY_GATED_2026_JAN_SEP",
                                "frozen":True})
    p=pd.DataFrame(out)
    for (target,model),g in p.groupby(["target","model"]):
        sets=[frozenset(t.date) for _,t in g.groupby("train_start")]
        if len(set(sets))!=1:raise RuntimeError("SCORED_ORIGINS_DIFFER_ACROSS_HISTORIES")
    return p

def month_metrics(p):
    rows=[]
    for (month,target,start,model),g in p.groupby(["month","target","train_start","model"]):
        y=g.y.to_numpy(int);v=g.pred.to_numpy(int);pr=g.p_up.to_numpy(float)
        ur=float(np.mean(v[y==1]==1)) if (y==1).any() else None
        dr=float(np.mean(v[y==0]==0)) if (y==0).any() else None
        rows.append({"month":month,"target":target,"train_start":start,
            "model":model,"n":len(g),"accuracy":float(np.mean(y==v)),
            "balanced_accuracy":float(.5*(ur+dr)) if ur is not None and dr is not None else None,
            "up_recall":ur,"down_recall":dr,
            "brier":float(np.mean((pr-y)**2))})
    return pd.DataFrame(rows)

def main():
    started=time.time()
    quotes,labels,count=load_q_t()
    feats=b.features(quotes,labels,min_year=2020,max_year=2026,
       gvz_csv=history.GVZ_FULL,require_full_2023_2025=False)
    accepted=v.joined(feats,require_full_2023_2025=False)
    p=get_fixed(accepted)
    m=history.metrics(p);monthly=month_metrics(p);paired=history.paired(p)
    status={"status":"2026_HISTDATA_SINGLE_PROVIDER_RESTRICTED_FROZEN_HOLDOUT_COMPLETE",
      "source_provider":"HistData M1 BID only 2020–Sep2026, fixed EST normalized UTC",
      "2023_upstream_gap":"PRESERVED_NO_IMPUTATION; 136 full DAY and 145 full OVN source labels before feature gates",
      "validated_source_target_counts":{str(k):{q:int(u) for q,u in v1.items()} for k,v1 in count.items()},
      "model_origin_eligibility_2026":{target:int(len(g))
            for target,g in accepted[accepted.year==2026].groupby("target")},
      "training_histories":list(LOCKED_START),"models":list(LOCKED_MODELS),
      "fit_frozen_as_of":"2026-01-01","last_2026_source_month":"2026-09",
      "2026_training_labels_in_fit":False,"2026_not_used_in_feature_selection":True,
      "2025_2026_vendor_mix":False,"2026_same_as_2020_2025_Dukascopy_quotes":False,
      "bank_executable":False,"source_status":"RESTRICTED_RESEARCH_NOT_CANONICAL",
      "vix_archive_sha":v.VIX_SHA,
      "elapsed_seconds":int(time.time()-started)}
    OUT.write_text(json.dumps(status,indent=2)+"\n")
    MET.write_text(m.to_csv(index=False))
    MON.write_text(monthly.to_csv(index=False))
    PAR.write_text(paired.to_csv(index=False))
    PRIVATE.write_text(p.to_csv(index=False))
    print("2026_HISTDATA_RESTRICTED_SCORE_COMPLETE",json.dumps(status),flush=True)
    print(m.to_string(index=False),flush=True)
    print("PAIRED_TRAINING_STARTS",paired.to_string(index=False),flush=True)
if __name__=="__main__":main()
