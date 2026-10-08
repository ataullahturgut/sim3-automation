"""Novel XAU first-passage risk taxonomy forecast (three events, no logit/boosting).
Preregistered 2026-10-08; fixed kernel nearest 41 paths; all labels mature.
"""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from scipy.stats import binomtest
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_full_trajectory_cbr_20261008 as cbr
import gold_execution_2026_firstpassage_barrier_diagnostic_20261008 as passage
NAME="GOLD_EXECUTION_2026_THREE_WAY_FIRSTPASSAGE_CBR_20261008"
CLASSES=("NO_HIT","UP_FIRST","DOWN_FIRST")
MODELS=("PATH_FIRSTPASSAGE","REGIME_PATH_FIRSTPASSAGE","HISTORICAL_THREE_EVENT_PRIOR")
def event_panel(q,t,qs,ts):
    qall=pd.concat([q,qs]).sort_index()
    if qall.index.duplicated().any():raise ValueError("MIXED_BAR_ID")
    tfull=pd.concat([t,ts],ignore_index=True).sort_values("date")
    if tfull.date.duplicated().any():raise ValueError("DUPLICATED_FUTURE_SESSION")
    z=cbr.panel(q,t,qs,ts)
    events=[]
    for r in tfull.itertuples(index=False):
        x=passage.per_night(qall,r)
        if x and x.get("accepted"):
            events.append({"date":pd.Timestamp(x["date"]), "first_hit":x["first_hit"]})
    ev=pd.DataFrame(events)
    if ev.empty or ev.date.duplicated().any():raise ValueError("NO_UNIQUE_FIRST_PASSAGE_TARGETS")
    panel=z[z.target=="OVN"].merge(ev,on="date",how="inner",validate="one_to_one")
    panel["event"]=panel.first_hit.map({name:i for i,name in enumerate(CLASSES)})
    if panel.event.isna().any():raise ValueError("BAD_EVENT_LABEL")
    return panel
def kernel_event(tr,te,regime):
    a=tr[cbr.PATH_COLS].to_numpy(float)
    b=te[cbr.PATH_COLS].to_numpy(float)
    labels=tr.event.to_numpy(int)
    freq=np.bincount(labels,minlength=3)/len(labels)
    d2=((b[:,None,:]-a[None,:,:])**2).sum(axis=2)/8
    if regime:
        keys=["log_pre_rv","gvz_log"]
        z=tr[keys].to_numpy(float);zz=te[keys].to_numpy(float)
        spread=np.maximum(z.std(axis=0),1e-6)
        d2+=.30*(((zz[:,None,:]-z[None,:,:])/spread)**2).sum(axis=2)
    out=[]
    for distances in np.sqrt(np.maximum(d2,0)):
        idx=np.argpartition(distances,40)[:41]
        local=distances[idx]
        w=np.exp(-local/max(1e-5,float(np.median(local))))
        vote=np.bincount(labels[idx],weights=w,minlength=3)
        out.append((vote+5*freq)/(w.sum()+5))
    return np.array(out)

def forecast_events(z,name):
    out=[]
    for period,test in z[z.year>=2023].groupby(z.date.dt.to_period("M")):
        d=period.to_timestamp()
        freeze=d if period.year<=2024 else pd.Timestamp(str(period.year)+"-01-01")
        tr=z[(z.date<freeze)&(z.next_date<=freeze)]
        if len(tr)<280 or tr.event.nunique()<3:continue
        if not(tr.date<test.date.min()).all():raise ValueError("FUTURE_FIRST_PASSAGE_LABEL")
        freq=np.bincount(tr.event.to_numpy(int),minlength=3)/len(tr)
        probs={
          "PATH_FIRSTPASSAGE":kernel_event(tr,test,False),
          "REGIME_PATH_FIRSTPASSAGE":kernel_event(tr,test,True),
          "HISTORICAL_THREE_EVENT_PRIOR":np.tile(freq,(len(test),1))}
        for method,pr in probs.items():
            for i,r in enumerate(test.itertuples(index=False)):
                out.append({"source_test":name,"date":r.date.strftime("%Y-%m-%d"),
                     "year":int(r.year),"month":str(period),"method":method,
                     "actual":int(r.event),"pred":int(np.argmax(pr[i])),
                     "p_nohit":float(pr[i,0]),"p_upfirst":float(pr[i,1]),
                     "p_downfirst":float(pr[i,2]),"fit_before":str(freeze)})
    return pd.DataFrame(out)
def score(p):
    rows=[]
    for (source,year,method),z in p.groupby(["source_test","year","method"]):
        actual=z.actual.to_numpy(int);pred=z.pred.to_numpy(int)
        pr=z[["p_nohit","p_upfirst","p_downfirst"]].to_numpy(float)
        y=np.eye(3)[actual]
        rec=[float(np.mean(pred[actual==cls]==cls)) if (actual==cls).any() else None for cls in range(3)]
        rows.append({"source_test":source,"year":int(year),"method":method,
            "n":len(z),"accuracy":float(np.mean(pred==actual)),
            "macro_recall":float(np.mean([x for x in rec if x is not None])),
            "recall_nohit":rec[0],"recall_upfirst":rec[1],"recall_downfirst":rec[2],
            "brier_multiclass":float(np.mean(np.sum((pr-y)**2,axis=1))),
            "logloss_multiclass":float(np.mean(-np.log(np.maximum(pr[np.arange(len(z)),actual],1e-8)))),
            "base_nohit_fraction":float(np.mean(actual==0)),
            "base_upfirst_fraction":float(np.mean(actual==1)),
            "base_downfirst_fraction":float(np.mean(actual==2))})
    return pd.DataFrame(rows)
