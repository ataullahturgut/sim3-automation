"""Gold nonparametric 16-bar trajectory analogy, preregistered, never logistic."""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2020_2025_all_existing_model_replay_20261008 as src
import gold_execution_origin_safe_shape_gvz_ml_challenge_20261008 as shape
import gold_execution_2020_2025_training_start_sensitivity_20261008 as frozen
import gold_execution_2026_direct_dukascopy_frozen_history_holdout_20261008 as targets
import gold_execution_2026_dukascopy_node_mirror_locked_models_20261008 as mirror
import gold_execution_2026_primary_native_restricted_diagnostic_20261008 as direct
NAME="GOLD_EXECUTION_2026_FULL_TRAJECTORY_CBR_20261008"
def source_sets():
    q,t=src.source_load()
    if len(q)!=141890 or len(t)!=1549:raise ValueError("HISTORY_CONTRACT_CHANGED")
    z,proof=mirror.load_approved()
    qm=z.set_index("bar_start_utc")[["bid_open","bid_close"]]
    qm=qm.rename(columns={"bid_open":"open","bid_close":"close"})
    tm,_=targets.candidate_targets(t,qm)
    qhist,thist,qd,td,quality=direct.load()
    if len(qhist)!=len(q):raise ValueError("HISTORICAL_CONTRACT_DIFF")
    return q,t,[("SAME_UPSTREAM_MIRROR_JAN_AUG20",qm,tm),
                ("DIRECT_DUKASCOPY_NATIVE_THROUGH_OCT07",qd,td)]
def panel(q,t,qs,ts):
    qfull=pd.concat([q,qs]).sort_index()
    if qfull.index.duplicated().any():raise ValueError("OVERLAPPING_QUOTE_TIMESTAMPS")
    tfull=pd.concat([t,ts],ignore_index=True).sort_values("date")
    if tfull.date.duplicated().any():raise ValueError("OVERLAPPING_ORIGIN_DATES")
    z=shape.features(qfull,tfull,min_year=2020,max_year=2026,gvz_csv=frozen.GVZ_FULL)
    path=[]
    for r in z.itertuples(index=False):
        origin=pd.Timestamp(r.date.date(),tz="Europe/Istanbul")+pd.Timedelta(hours=shape.ORIGIN[r.target])
        grid=pd.date_range(origin.tz_convert("UTC")-pd.Timedelta(hours=4),periods=16,freq="15min")
        bars=qfull.reindex(grid)
        if bars[["open","close"]].isna().any().any():raise ValueError("HIDDEN_PREORIGIN_PRICE_GAP")
        increments=np.log(bars.close.to_numpy(float)/bars.open.to_numpy(float))
        cum=np.cumsum(increments.reshape(8,2).sum(axis=1))
        path.append(cum/(np.sqrt(np.square(increments).sum())+1e-10))
    paths=np.array(path)
    for i in range(8):z["path_"+str(i)]=paths[:,i]
    z["log_pre_rv"]=np.log(z.pre4h_rv)
    if z.duplicated(["date","target"]).any():raise ValueError("DUPLICATE_MATURITY")
    return z

PATH_COLS=["path_"+str(i) for i in range(8)]
METHODS=("CBR_PATH","CBR_REGIME_PATH","HGB_FROZEN_2021","EMPIRICAL_PRIOR")
def analogue(tr,te,regime):
    a=tr[PATH_COLS].to_numpy(float)
    x=te[PATH_COLS].to_numpy(float)
    y=tr.y.to_numpy(int)
    base=float(np.mean(y))
    if len(y)<100 or len(np.unique(y))<2:raise ValueError("TRAIN_ANALOGUE_HISTORY_FAIL")
    d2=((x[:,None,:]-a[None,:,:])**2).sum(axis=2)/8
    if regime:
        keys=["log_pre_rv","gvz_log"]
        z=tr[keys].to_numpy(float)
        zx=te[keys].to_numpy(float)
        scale=np.maximum(z.std(axis=0),1e-6)
        diff=(zx[:,None,:]-z[None,:,:])/scale[None,None,:]
        d2+=.30*(diff**2).sum(axis=2)
    d=np.sqrt(np.maximum(0,d2))
    p=[]
    for row in d:
        idx=np.argpartition(row,41)[:41]
        distances=row[idx]
        temperature=max(1e-5,float(np.median(distances)))
        w=np.exp(-distances/temperature)
        p.append(float((np.dot(w,y[idx])+5*base)/(np.sum(w)+5)))
    return np.clip(np.array(p),1e-6,1-1e-6)
def forecast(z,source_name):
    results=[]
    for target in ("DAY","OVN"):
      k=z[z.target==target].sort_values("date").copy()
      for period,test in k[k.year>=2023].groupby(k.date.dt.to_period("M")):
        dt=period.to_timestamp()
        cutoff=dt if period.year<=2024 else pd.Timestamp(str(period.year)+"-01-01")
        training=k[(k.date<cutoff)&(k.year>=2021)]
        if target=="OVN":training=training[training.next_date<=cutoff]
        if len(training)<280:continue
        if not (training.date<test.date.min()).all():raise ValueError("TARGET_ORIGIN_LEAK")
        cols=frozen.COLUMNS["SHAPE_GVZ_HGB"]
        benchmark=frozen.method_fit(training[cols].to_numpy(float),
                              training.y.to_numpy(int),"SHAPE_GVZ_HGB")
        probs={
          "CBR_PATH":analogue(training,test,False),
          "CBR_REGIME_PATH":analogue(training,test,True),
          "HGB_FROZEN_2021":benchmark.predict_proba(test[cols].to_numpy(float))[:,1],
          "EMPIRICAL_PRIOR":np.full(len(test),float(training.y.mean()))}
        for name,p in probs.items():
          for i,r in enumerate(test.itertuples(index=False)):
            results.append({"source_test":source_name,"target":target,
              "date":r.date.strftime("%Y-%m-%d"),"year":int(r.year),
              "month":str(period),"method":name,"y":int(r.y),"p_up":float(p[i]),
              "pred":int(p[i]>=.5),"n_historical_paths":len(training),
              "training_cutoff":str(cutoff)})
    return pd.DataFrame(results)

def measures(p):
    rows=[]
    for (src,target,year,method),g in p.groupby(["source_test","target","year","method"]):
        y=g.y.to_numpy(int);q=g.pred.to_numpy(int);probs=g.p_up.to_numpy(float)
        tn=int(np.sum((y==0)&(q==0)));fp=int(np.sum((y==0)&(q==1)))
        fn=int(np.sum((y==1)&(q==0)));tp=int(np.sum((y==1)&(q==1)))
        dn=tn/(tn+fp) if tn+fp else None
        up=tp/(tp+fn) if tp+fn else None
        rows.append({"source_test":src,"target":target,"year":int(year),
            "method":method,"n":len(g),"BA":(dn+up)*.5 if dn is not None and up is not None else None,
            "DOWN_recall":dn,"UP_recall":up,"accuracy":float(np.mean(q==y)),
            "Brier":float(np.mean((probs-y)**2)),
            "tn":tn,"fp":fp,"fn":fn,"tp":tp})
    return pd.DataFrame(rows)
def paired(p):
    rows=[]
    for (src,target,year),g in p.groupby(["source_test","target","year"]):
        ref=g[g.method=="HGB_FROZEN_2021"].set_index("date").sort_index()
        for name in ("CBR_PATH","CBR_REGIME_PATH"):
            alt=g[g.method==name].set_index("date").sort_index()
            if not ref.index.equals(alt.index) or not (ref.y==alt.y).all():
                raise ValueError("UNPAIRED_ANALOG_CASES")
            y=ref.y.to_numpy(int);q=alt.pred.to_numpy(int);r=ref.pred.to_numpy(int)
            saved=int(np.sum((q==y)&(r!=y)))
            broken=int(np.sum((q!=y)&(r==y)))
            rows.append({"source_test":src,"target":target,"year":int(year),
               "model":name,"n":len(y),"rescues":saved,"breaks":broken,
               "net":saved-broken,
               "mcnemar_p":float(binomtest(saved,saved+broken,.5).pvalue) if saved+broken else 1.})
    return pd.DataFrame(rows)

def main():
    q,t,sources=source_sets()
    preds=[]
    for source_name,px,ts in sources:
        z=panel(q,t,px,ts)
        pp=forecast(z,source_name)
        if pp.empty:raise ValueError("EMPTY_TRAJECTORY_FORECAST")
        if pp.duplicated(["target","date","method"]).any():raise ValueError("DUPLICATE_CASES")
        preds.append(pp)
        print("CBR_POPULATION",source_name,
              z.groupby(["target","year"]).size().to_dict(),flush=True)
    p=pd.concat(preds,ignore_index=True)
    m=measures(p);pairs=paired(p)
    counts={str(k):int(v) for k,v in
       p.groupby(["source_test","target","year","method"]).size().groupby(level=[0,1,2]).first().items()}
    report={"status":"NOVEL_MULTISCALE_PATH_ANALOG_ACTUALLY_SCORED",
      "methods":["CBR_PATH","CBR_REGIME_PATH","HGB_FROZEN_2021","EMPIRICAL_PRIOR"],
      "history":"2020-25 EV Dukascopy BID, trained from 2021",
      "forecast":"past16 M15 whole path + preorigin RV/GVZ; no 2026 labels in model fit",
      "year2023_24":"monthly fit with mature past only",
      "year2025":"fixed before 2025; retrospective",
      "year2026":"fixed before 2026; already-inspected retrospective",
      "test_sources":["2026 same-upstream mirror price gated","2026 native direct"],
      "samples":counts,"no_banking_PnL":True,"no_untouched_holdout":True}
    stem=AX/NAME
    Path(str(stem)+"_SUMMARY.json").write_text(json.dumps(report,indent=2)+"\n")
    m.to_csv(str(stem)+"_YEAR_METRICS.csv",index=False)
    pairs.to_csv(str(stem)+"_PAIRED.csv",index=False)
    p.to_csv(str(stem)+"_DATED_PRIVATE.csv",index=False)
    print("MULTISCALE_TRAJECTORY_RESULTS",m.to_string(index=False),flush=True)
    print("MULTISCALE_TRAJECTORY_PAIRED",pairs.to_string(index=False),flush=True)
    print("CBR_RUN_STATUS",json.dumps(report),flush=True)
if __name__=="__main__":main()
