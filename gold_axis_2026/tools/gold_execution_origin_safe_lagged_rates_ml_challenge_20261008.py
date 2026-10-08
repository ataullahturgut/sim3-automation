"""Pre-registered lagged Fed 2Y + real 10Y direction-ablation challenge.
Official H15 observations used strictly from dates BEFORE issue date; no current-day yields.
Same audited BID price labels and Stage-1 model identities. Historical 2025 is NOT blind.
"""
from __future__ import annotations
import os,sys,json,time
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from scipy.stats import binomtest

AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as base
import gold_execution_2020_2025_all_existing_model_replay_20261008 as source

NAME="GOLD_EXECUTION_ORIGIN_SAFE_LAGGED_RATES_ML_CHALLENGE_20261008"
MFILE=AX/(NAME+"_METRICS.csv")
PAIRFILE=AX/(NAME+"_PAIRED_AUDIT.csv")
SFILE=AX/(NAME+"_SUMMARY.json")
PFILE=AX/(NAME+"_DATED_PREDICTIONS_PRIVATE.csv")
RATES=["dgs2_level","dgs2_change","dfii10_level","dfii10_change"]
COLS=base.PRICE+["gvz_log","gvz_x_early","gvz_x_late"]+RATES
MODEL_NAMES=("RATES_LOGIT","RATES_HGB")
SOURCES={
 "dgs2":AX/"GOLD_EXECUTION_DGS2_FREE_CANDIDATE_2020_20261007.csv",
 "dfii10":AX/"GOLD_EXECUTION_DFII10_FREE_CANDIDATE_2020_20261007.csv"
}

def joined(z):
    z=z.sort_values("date").copy().reset_index(drop=True)
    for tag,path in SOURCES.items():
        r=pd.read_csv(path)
        if not {"date","value"}.issubset(r):raise RuntimeError(tag+":H15_SOURCE_SCHEMA")
        r=r[["date","value"]].copy()
        r["date"]=pd.to_datetime(r.date,errors="raise")
        r["value"]=pd.to_numeric(r.value,errors="coerce")
        r=r.dropna().sort_values("date").drop_duplicates("date",keep="last")
        if len(r)<1500 or r.date.min()>pd.Timestamp("2020-02-01") or r.date.max()<pd.Timestamp("2025-12-01"):
            raise RuntimeError(tag+":INCOMPLETE_H15_SOURCE")
        r["chg"]=r.value.diff()
        r=r.dropna()
        r=r.rename(columns={"date":tag+"_known_date","value":tag+"_level","chg":tag+"_change"})
        z=pd.merge_asof(z.sort_values("date"),r,left_on="date",
            right_on=tag+"_known_date",direction="backward",allow_exact_matches=False)
        accepted=z[tag+"_known_date"].notna()
        z=z.loc[accepted].copy()
        if not (z[tag+"_known_date"]<z.date).all():
            raise RuntimeError(tag+":SAME_OR_FUTURE_DAY_YIELD")
        if (z.date-z[tag+"_known_date"]).dt.days.gt(7).any():
            raise RuntimeError(tag+":STALE_H15_YIELD")
    z=z.dropna(subset=COLS).sort_values(["target","date"]).reset_index(drop=True)
    if len(z[z.year==2023])<380 or len(z[z.year==2024])<390 or len(z[z.year==2025])<380:
        raise RuntimeError("SOURCE_ALIGNED_RATES_POPULATION_THIN")
    if z.duplicated(["target","date"]).any():raise RuntimeError("DUPLICATE_LABEL_DATE")
    return z

def predict_rates(z):
    out=[]
    for target in ("DAY","OVN"):
        k=z[z.target==target].sort_values("date").reset_index(drop=True)
        frozen=k[(k.date<pd.Timestamp("2025-01-01")) &
              ((k.next_date<=pd.Timestamp("2025-01-01")) if target=="OVN" else True)].copy()
        if len(frozen)<530:raise RuntimeError(target+":RATES_FROZEN_HISTORY_SHORT")
        cache={}
        for r in k[k.year.isin([2023,2024,2025])].itertuples(index=False):
            d=pd.Timestamp(r.date)
            if r.year==2025:
                training=frozen;key="FROZEN_2024"
            else:
                ms=pd.Timestamp(year=d.year,month=d.month,day=1)
                training=(k[(k.date<ms)&(k.next_date<=ms)] if target=="OVN"
                     else k[k.date<ms])
                key=ms.strftime("%Y-%m")
            if len(training)<base.MIN_TRAIN or training.y.nunique()!=2:continue
            if not (training.date<d).all():raise RuntimeError("TRAINING_DATE_LEAKAGE")
            if r.year==2025 and training.year.max()>2024:raise RuntimeError("2025_LABEL_LEAK")
            x=training[COLS].to_numpy(float);y=training.y.to_numpy(int)
            xx=k.loc[k.date==d,COLS].to_numpy(float)
            for model in MODEL_NAMES:
                identity=(target,key,model)
                if identity not in cache:
                    if model=="RATES_LOGIT":
                        f=make_pipeline(StandardScaler(),LogisticRegression(C=.3,max_iter=1000))
                    else:
                        f=HistGradientBoostingClassifier(max_iter=90,learning_rate=.04,
                              max_leaf_nodes=7,min_samples_leaf=35,max_depth=3,
                              l2_regularization=10.,random_state=1808)
                    cache[identity]=f.fit(x,y)
                p=float(np.clip(cache[identity].predict_proba(xx)[0,1],1e-6,1-1e-6))
                out.append({"date":d.strftime("%Y-%m-%d"),"year":int(r.year),
                    "target":target,"model":model,"n_train":len(training),
                    "y":int(r.y),"p_up":p,"pred":int(p>=.5),
                    "research_scope":"EXAMINED_RETROSPECTIVE_2025" if r.year==2025
                       else "CHRONOLOGICAL_MONTHLY_DEVELOPMENT"})
    return pd.DataFrame(out)

def pairs(p):
    rows=[]
    for (target,year),subset in p.groupby(["target","year"]):
        for ref in ("BASE_LOGIT","SHAPE_GVZ_HGB"):
            a=subset[subset.model==ref].set_index("date").sort_index()
            for model in MODEL_NAMES:
                b=subset[subset.model==model].set_index("date").sort_index()
                joint=a[["y","pred","p_up"]].join(b[["y","pred","p_up"]],how="inner",
                        lsuffix="_ref",rsuffix="_new",validate="one_to_one")
                if len(joint)!=len(a) or len(joint)!=len(b) or (joint.y_ref!=joint.y_new).any():
                    raise RuntimeError("UNPAIRED_COMPARISON")
                y=joint.y_ref.to_numpy(int)
                pred=joint.pred_new.to_numpy(int)
                refpred=joint.pred_ref.to_numpy(int)
                saved=int(((pred==y)&(refpred!=y)).sum())
                broken=int(((pred!=y)&(refpred==y)).sum())
                def ba(x):
                    return .5*(np.mean(x[y==0]==0)+np.mean(x[y==1]==1))
                bs=np.mean((joint.p_up_new-y)**2-(joint.p_up_ref-y)**2)
                rows.append({"year":int(year),"target":target,"reference":ref,
                  "challenger":model,"n":len(joint),"saved":saved,"broken":broken,
                  "net_rescue":saved-broken,"ba_delta":float(ba(pred)-ba(refpred)),
                  "brier_delta":float(bs),
                  "mcnemar_exact_p":float(binomtest(saved,saved+broken,.5).pvalue)
                           if saved+broken else 1.0,
                  "2025_is_exploratory":bool(year==2025)})
    return pd.DataFrame(rows)

def main():
    start=time.time()
    q,t=source.source_load()
    z=joined(base.features(q,t))
    old=base.predictions(z)
    new=predict_rates(z)
    p=pd.concat([old,new],ignore_index=True)
    if set(p.model.unique())!=set(base.MODELS)|set(MODEL_NAMES):
        raise RuntimeError("FROZEN_HEAD_IDENTITY_MISSING")
    for (target,year),group in p.groupby(["target","year"]):
        date_sets=[frozenset(x.date) for _,x in group.groupby("model")]
        if len(set(date_sets))!=1: raise RuntimeError(target+":NOT_IDENTICAL_SAMPLE")
    m=base.metrics(p);pa=pairs(p)
    gates={}
    for model in MODEL_NAMES:
        for target in ("DAY","OVN"):
            d=m[(m.model==model)&(m.target==target)&m.year.isin([2023,2024])]
            gates[target+"_"+model]={"dev_BA_gt_50_both":bool(len(d)==2 and (d.balanced_accuracy>.5).all()),
              "dev_DOWN_recall_ge_30_both":bool(len(d)==2 and (d.down_recall>=.3).all())}
    summary={"status":"COMPLETED_OFFICIAL_H15_PRIORDAY_RATES_ABLATION",
      "source_id":source.SOURCE,"source_bars":len(q),"source_targets":len(t),
      "source_gvz":"strict previous day","rate_source":"Fed H15 DGS2 + DFII10 official daily candidate",
      "rate_date_rule":"strict observation date < origin date; use previous two available observations; max 7 calendar day staleness",
      "models_added":list(MODEL_NAMES),"benchmark_models":list(base.MODELS),
      "all_comparisons_exact_paired":True,"scope":"regular weekday16h OVN and DAY separately",
      "result_2025":"ALREADY_EXAMINED_RETROSPECTIVE_NOT_FRESH_HOLDOUT",
      "no_2025_model_selection":True,"no_production_promotion":True,
      "development_gates":gates,
      "date_counts":{str(k[0])+"_"+str(k[1]):int(v) for k,v in z.groupby(["target","year"]).size().items()},
      "elapsed_sec":int(time.time()-start)}
    SFILE.write_text(json.dumps(summary,indent=2)+"\n")
    MFILE.write_text(m.to_csv(index=False))
    PAIRFILE.write_text(pa.to_csv(index=False))
    PFILE.write_text(p.to_csv(index=False))
    print("DONE_RATES_TEST",json.dumps(summary),flush=True)
    print(m.to_string(index=False),flush=True)
    print("MATCHED_IMPROVEMENTS",pa.to_string(index=False),flush=True)
if __name__=="__main__":main()
