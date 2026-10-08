"""Preregistered previous-close Cboe equity-fear (VIX) versus gold-specific GVZ
risk-divergence test for exact Turkey DAY and regular 16h OVERNIGHT direction.
No 2025-dependent tuning. No exchange prices or original data published.
"""
from __future__ import annotations
import os,sys,json,time,io,hashlib,urllib.request
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
NAME="GOLD_EXECUTION_ORIGIN_SAFE_VIX_GVZ_ML_CHALLENGE_20261008"
MFILE=AX/(NAME+"_METRICS.csv")
PAIRFILE=AX/(NAME+"_PAIRED_AUDIT.csv")
SFILE=AX/(NAME+"_SUMMARY.json")
PFILE=AX/(NAME+"_DATED_PREDICTIONS_PRIVATE.csv")
VIX_FEATURES=["vix_log","vix_last_log_return","vix_vs_gvz_log_spread"]
COLS=base.PRICE+["gvz_log","gvz_x_early","gvz_x_late"]+VIX_FEATURES
MODEL_NAMES=("VIX_GVZ_LOGIT","VIX_GVZ_HGB")
VIX_SHA=None
VIX_URLS=[
    "https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
    "https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv",
]

def joined(z,require_full_2023_2025=True):
    global VIX_SHA
    blob=None;errors=[]
    for url in VIX_URLS:
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 research historical csv"})
            with urllib.request.urlopen(req,timeout=30) as resp:
                blob=resp.read(2000000)
            if len(blob)<100000:raise RuntimeError("CBOE_UNEXPECTED_SMALL_PAYLOAD")
            break
        except Exception as e:errors.append(str(e))
    if blob is None:raise RuntimeError("CBOE_VIX_SOURCE_UNAVAILABLE: "+str(errors))
    VIX_SHA=hashlib.sha256(blob).hexdigest()
    v=pd.read_csv(io.BytesIO(blob))
    v.columns=[c.strip().upper() for c in v.columns]
    if not {"DATE","CLOSE"}.issubset(v.columns):
        raise RuntimeError("CBOE_VIX_SCHEMA_NOT_DATE_CLOSE: "+str(v.columns.tolist()))
    v=v[["DATE","CLOSE"]].rename(columns={"DATE":"vix_known_date","CLOSE":"vix_level"})
    v["vix_known_date"]=pd.to_datetime(v.vix_known_date,format="%m/%d/%Y",errors="coerce")
    if v.vix_known_date.isna().any():
        v["vix_known_date"]=pd.to_datetime(v.vix_known_date,errors="coerce")
    v["vix_level"]=pd.to_numeric(v.vix_level,errors="coerce")
    v=v.dropna()
    v=v[(v.vix_level>0)].sort_values("vix_known_date")
    v=v.drop_duplicates("vix_known_date",keep="last")
    if len(v)<2000 or v.vix_known_date.min()>pd.Timestamp("2020-02-01") or v.vix_known_date.max()<pd.Timestamp("2025-12-01"):
        raise RuntimeError("VIX_HISTORY_INSUFFICIENT")
    v["vix_log"]=np.log(v.vix_level)
    v["vix_last_log_return"]=v.vix_log.diff()
    v=v.dropna()
    z=z.sort_values("date").copy().reset_index(drop=True)
    z=pd.merge_asof(z,v,left_on="date",right_on="vix_known_date",
         direction="backward",allow_exact_matches=False)
    z=z.dropna(subset=["vix_known_date"]+VIX_FEATURES[:2]).copy()
    if not (z.vix_known_date < z.date).all():raise RuntimeError("VIX_FUTURE_OBSERVED")
    if (z.date-z.vix_known_date).dt.days.gt(7).any():raise RuntimeError("VIX_TOO_STALE")
    z["vix_vs_gvz_log_spread"]=z.vix_log-z.gvz_log
    z=z.dropna(subset=COLS).sort_values(["target","date"]).reset_index(drop=True)
    if require_full_2023_2025 and (len(z[z.year==2023])<380 or len(z[z.year==2024])<390 or len(z[z.year==2025])<380):
        raise RuntimeError("MATCHED_SAMPLE_TOO_THIN")
    if z.duplicated(["target","date"]).any():raise RuntimeError("DUPLICATE_TARGET_DATE")
    return z

def predict_vix(z):
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
                    if model=="VIX_GVZ_LOGIT":
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
    new=predict_vix(z)
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
    summary={"status":"COMPLETED_VIX_GVZ_RISK_DIVERGENCE_TEST",
      "source_id":source.SOURCE,"source_bars":len(q),"source_targets":len(t),
      "source_gvz":"strict previous day","external_source":"Cboe official daily VIX index historical close",
      "vix_date_rule":"Cboe VIX last two observations strict date < origin date; max 7 days old","vix_source_sha256":VIX_SHA,
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
    print("DONE_VIX_GVZ_TEST",json.dumps(summary),flush=True)
    print(m.to_string(index=False),flush=True)
    print("MATCHED_IMPROVEMENTS",pa.to_string(index=False),flush=True)
if __name__=="__main__":
    try:
        main()
    except Exception as exc:
        # Record only sanitized failure category; never write protected price rows,
        # environment variables, full URI, source samples or stack frames to Git.
        safe_codes=["CBOE_VIX_SOURCE_UNAVAILABLE","CBOE_VIX_SCHEMA_NOT_DATE_CLOSE",
            "CBOE_UNEXPECTED_SMALL_PAYLOAD","VIX_HISTORY_INSUFFICIENT",
            "VIX_FUTURE_OBSERVED","VIX_TOO_STALE","MATCHED_SAMPLE_TOO_THIN",
            "RATES_FROZEN_HISTORY_SHORT","FROZEN_HEAD_IDENTITY_MISSING",
            "NOT_IDENTICAL_SAMPLE","NO_FEATURE_ROWS","FROZEN_SOURCE_ID_MISMATCH"]
        message=str(exc)
        code=next((k for k in safe_codes if k in message),"OTHER_CHECK_FAILED")
        err={"status":"EXPERIMENT_EXECUTION_FAILED","class":type(exc).__name__,
             "safe_code":code,"raw_source_or_date_levels_exported":False}
        (AX/(NAME+"_FAIL_STATUS.json")).write_text(json.dumps(err,indent=2)+"\n")
        print("VIX_GVZ_RUN_FAILED",json.dumps(err),flush=True)
        raise
