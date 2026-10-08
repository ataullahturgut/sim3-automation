"""Same-date source-audited comparison of 2020/2021/2022 training histories.

Scientific design registered before this run:
- 2020-2025 one-vendor BID XAU, frozen independently audited DAY and weekday OVN labels.
- Official Cboe GVZ full-year archive; Cboe VIX previous-day daily close.
- 2023/2024 expanding monthly refits with only mature historical outcomes; 2025 fixed
  2024 parameters retrospective, not an untouched OOS holdout.
- Every trial uses fixed original exact 2026-10-08 model family and hyperparameters.
- 2026 intentionally handled in SEPARATE source identity/label audit.
"""
from __future__ import annotations
import sys,time,json
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as b
import gold_execution_origin_safe_vix_gvz_ml_challenge_20261008 as v
OUTPUT="GOLD_EXECUTION_2020_2025_TRAIN_START_COMPARISON_20261008"
SUMMARY=AX/(OUTPUT+"_SUMMARY.json")
METRICS=AX/(OUTPUT+"_METRICS.csv")
PAIRED=AX/(OUTPUT+"_PAIRED_HISTORY.csv")
PRIVATE=AX/(OUTPUT+"_DATED_PREDICTIONS_PRIVATE.csv")
HISTORIES=(2020,2021,2022)
MODELS=("BASE_LOGIT","SHAPE_LOGIT","SHAPE_GVZ_LOGIT","SHAPE_GVZ_HGB","VIX_GVZ_LOGIT","VIX_GVZ_HGB")
GVZ_FULL=AX/"GOLD_EXECUTION_GVZ_FREE_CANDIDATE_2020_20261007.csv"
COLUMNS={
    "BASE_LOGIT":None,
    "SHAPE_LOGIT":b.PRICE,
    "SHAPE_GVZ_LOGIT":b.PRICE+["gvz_log","gvz_x_early","gvz_x_late"],
    "SHAPE_GVZ_HGB":b.PRICE+["gvz_log","gvz_x_early","gvz_x_late"],
    "VIX_GVZ_LOGIT":v.COLS,
    "VIX_GVZ_HGB":v.COLS,
}
FIRST_DATE=pd.Timestamp("2023-01-01")
FREEZE=pd.Timestamp("2025-01-01")

def loaded():
    q,t=src.source_load()
    if len(q)!=141890 or len(t)!=1549:raise RuntimeError("2020_2025_SOURCE_CONTRACT_CHANGED")
    if not GVZ_FULL.exists():raise RuntimeError("OFFICIAL_GVZ_2020_CANDIDATE_MISSING")
    fullgvz=pd.read_csv(GVZ_FULL,usecols=["date","value"])
    fullgvz["date"]=pd.to_datetime(fullgvz.date)
    for yr in (2020,2021,2022,2023,2024,2025):
        if len(fullgvz[fullgvz.date.dt.year==yr])<245:
            raise RuntimeError("OFFICIAL_GVZ_MISSING_YEAR_"+str(yr))
    z=b.features(q,t,min_year=2020,max_year=2025,gvz_csv=GVZ_FULL)
    z=v.joined(z)
    for win in ("DAY","OVN"):
        for yr in (2020,2021,2022,2023,2024,2025):
            n=len(z[(z.target==win)&(z.year==yr)])
            if n < (150 if win=="OVN" else 220):
                raise RuntimeError("MISSING_"+win+"_"+str(yr)+"_SOURCE_FEATURE_COVERAGE")
    if z.duplicated(["target","date"]).any():raise RuntimeError("DUPLICATE_DATES")
    return q,t,z

def method_fit(X,y,name):
    if name.endswith("_HGB"):
        clf=HistGradientBoostingClassifier(max_iter=90,learning_rate=.04,
            max_leaf_nodes=7,min_samples_leaf=35,max_depth=3,
            l2_regularization=10.,random_state=1808)
    else:
        clf=make_pipeline(StandardScaler(),LogisticRegression(C=.3,max_iter=1000))
    return clf.fit(X,y)

def predictions(z):
    out=[]
    for target in ("DAY","OVN"):
        k=z[z.target==target].sort_values("date").reset_index(drop=True)
        for start in HISTORIES:
            history=k[k.year>=start].copy()
            if start==2020 and (history.year==2020).sum()<(150 if target=="OVN" else 220):
                raise RuntimeError("LONG_HISTORY_SOURCE_THIN")
            cache={}
            for record in k[k.year.isin((2023,2024,2025))].itertuples(index=False):
                date=pd.Timestamp(record.date)
                if record.year==2025:
                    cutoff=FREEZE
                    fit_label="FROZEN_PRE_2025"
                else:
                    cutoff=pd.Timestamp(year=date.year,month=date.month,day=1)
                    fit_label=cutoff.strftime("%Y-%m")
                train=history[history.date<cutoff]
                if target=="OVN":
                    train=train[train.next_date<=cutoff]
                if len(train)<150 or train.y.nunique()!=2:
                    raise RuntimeError("MISSING_TRAIN_LABELS_"+target+"_"+str(start)+"_"+str(date))
                if not (train.date<date).all():raise RuntimeError("FEATURE_OR_LABEL_FUTURE_DATE")
                if target=="OVN" and not (train.next_date<=cutoff).all():
                    raise RuntimeError("UNMATURED_OVN_LABEL")
                if record.year==2025 and not (train.year<=2024).all():
                    raise RuntimeError("2025_LOOKAHEAD")
                row=k[k.date==date]
                for name in MODELS:
                    cols=(b.BASE_DAY if target=="DAY" else b.BASE_OVN) if name=="BASE_LOGIT" else COLUMNS[name]
                    if row[cols].isna().any().any() or train[cols].isna().any().any():
                        raise RuntimeError("MISSING_FEATURE_UNTRACKED")
                    key=(fit_label,name)
                    if key not in cache:
                        cache[key]=method_fit(train[cols].to_numpy(float),train.y.to_numpy(int),name)
                    pp=float(np.clip(cache[key].predict_proba(row[cols].to_numpy(float))[0,1],1e-6,1-1e-6))
                    out.append({"date":date.strftime("%Y-%m-%d"),"year":int(record.year),
                      "target":target,"train_start":int(start),"model":name,
                      "y":int(record.y),"pred":int(pp>=.5),"p_up":pp,
                      "n_train":len(train),"research_scope":"RETROSPECTIVE_2025_NOT_BLIND" if record.year==2025 else "CHRONOLOGICAL_2023_2024"})
    return pd.DataFrame(out)

def metrics(p):
    from sklearn.metrics import confusion_matrix
    rows=[]
    for (target,start,name,year),g in p.groupby(["target","train_start","model","year"]):
        y=g.y.to_numpy(int);pred=g.pred.to_numpy(int);pr=g.p_up.to_numpy(float)
        tn,fp,fn,tp=map(int,confusion_matrix(y,pred,labels=[0,1]).ravel())
        nr=tn/(tn+fp) if (tn+fp)>0 else np.nan
        ur=tp/(tp+fn) if (tp+fn)>0 else np.nan
        rows.append({"target":target,"train_start":int(start),"model":name,"year":int(year),
          "n":int(len(g)),"accuracy":float(np.mean(y==pred)),
          "balanced_accuracy":float(.5*(ur+nr)),"down_recall":nr,"up_recall":ur,
          "predicted_up_fraction":float(np.mean(pred)),
          "brier":float(np.mean((pr-y)**2)),
          "logloss":float(-np.mean(y*np.log(pr)+(1-y)*np.log(1-pr))),
          "tn":tn,"fp":fp,"fn":fn,"tp":tp})
    return pd.DataFrame(rows)

def paired(p):
    rows=[]
    for (target,model,year),g in p.groupby(["target","model","year"]):
        ref=g[g.train_start==2022].set_index("date").sort_index()
        for start in (2020,2021):
            alt=g[g.train_start==start].set_index("date").sort_index()
            if len(ref)!=len(alt) or not ref.index.equals(alt.index) or not (ref.y==alt.y).all():
                raise RuntimeError("TRAINING_HISTORY_SCORE_DATES_DIFFER")
            y=ref.y.to_numpy(int)
            r=ref.pred.to_numpy(int);a=alt.pred.to_numpy(int)
            save=int(((a==y)&(r!=y)).sum())
            breakc=int(((a!=y)&(r==y)).sum())
            def ba(pred):
                return .5*(np.mean(pred[y==0]==0)+np.mean(pred[y==1]==1))
            rows.append({"target":target,"year":int(year),"model":model,
               "extended_start":start,"benchmark_start":2022,
               "same_n":len(y),"rescues":save,"newly_broken":breakc,
               "net_rescues":save-breakc,
               "delta_balanced_accuracy":float(ba(a)-ba(r)),
               "delta_brier":float(np.mean((alt.p_up.to_numpy(float)-y)**2-
                                           (ref.p_up.to_numpy(float)-y)**2)),
               "mcnemar_exact_p":float(binomtest(save,save+breakc,.5).pvalue) if save+breakc else 1.,
               "retrospective_2025":bool(year==2025)})
    return pd.DataFrame(rows)

def main():
    tic=time.time()
    q,t,z=loaded()
    print("TRAIN_START_SOURCE_READY",len(q),len(t),z.groupby(["target","year"]).size().to_dict(),flush=True)
    p=predictions(z);m=metrics(p);paired_df=paired(p)
    if p.groupby(["target","year","model"]).train_start.nunique().min()!=3:
        raise RuntimeError("ONE_HISTORY_DID_NOT_RUN")
    summary={
      "status":"THREE_HISTORICAL_STARTS_2020_2021_2022_ACTUALLY_REFIT",
      "source_id":src.SOURCE,"source_bars":len(q),"frozen_target_rows":len(t),
      "date_spans":{str(k[0])+"_"+str(k[1]):int(c) for k,c in z.groupby(["target","year"]).size().items()},
      "gvz_official_full_2020_2025":True,"vix_official_hash":v.VIX_SHA,
      "histories_compared":list(HISTORIES),"tested_models":list(MODELS),
      "scored_years":[2023,2024,2025],
      "2023_2024":"chronological prior-month matured labels only",
      "2025":"frozen pre-2025 fit, already-inspected retrospective NOT blind",
      "same_rows_across_histories":True,
      "friday_64h_overnight":"excluded_separate_horizon",
      "2026":"NOT_IN_THIS_RUN; HOLDOUT_REQUIRES_AUDITED_SAME_SOURCE_2026_M15_AND_FROZEN_LABELS",
      "never_relabel_existing_session_results":True,"bank_executable":False,
      "elapsed_seconds":int(time.time()-tic)}
    SUMMARY.write_text(json.dumps(summary,indent=2)+"\n")
    METRICS.write_text(m.to_csv(index=False))
    PAIRED.write_text(paired_df.to_csv(index=False))
    PRIVATE.write_text(p.to_csv(index=False))
    print("TRAIN_START_COMPARISON_FINISHED",json.dumps(summary),flush=True)
    print(m.to_string(index=False),flush=True)
    print("PAIRED_START_HISTORY_AUDIT",paired_df.to_string(index=False),flush=True)
if __name__=="__main__":main()
