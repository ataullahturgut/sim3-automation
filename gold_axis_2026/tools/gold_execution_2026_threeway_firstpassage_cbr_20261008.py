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
