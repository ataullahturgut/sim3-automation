"""Fully causal Dirichlet-multinomial Bayesian ONLINE CHANGE POINT over 3 first-hit events.
Not a binary logistic/boosting surrogate. First-hit observed 15m BID closes.
"""
from pathlib import Path
import sys,json
import numpy as np,pandas as pd
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_threeway_firstpassage_cbr_20261008 as first
NAME="GOLD_EXECUTION_2026_BAYESIAN_COMPETING_EVENT_BOCPD_20261008"
H=1./63.
ALPHA=np.array([1.,1.,1.])
MAX_RUN=252
METHODS=("BAYES_ONLINE_CHANGEPOINT","TRAILING63_DIRICHLET",
         "LAST_YEAR_CLIMATOLOGY","REGIME_PATH_FIRSTPASSAGE")
def online_predictions(panel,tag):
    z=panel.sort_values("date").copy()
    R=np.array([1.])
    counts=np.zeros((1,3),dtype=float)
    matured=[]
    out=[]
    lastdate=None
    matured_with_dates=[]
    for r in z.itertuples(index=False):
      issue=pd.Timestamp(r.date)
      if lastdate is not None and issue<=lastdate:raise RuntimeError("NOT_STRICTLY_CHRONOLOGICAL")
      # Only preceding fully matured OVN results in state, never current y.
      forecast=(R[:,None]*((counts+ALPHA)/(counts.sum(axis=1,keepdims=True)+3.))).sum(axis=0)
      tail=np.bincount(matured[-63:],minlength=3).astype(float)+ALPHA
      trailing=tail/tail.sum()
      if r.year>=2023:
        previous=[x for d,x in matured_with_dates if pd.Timestamp(d).year==r.year-1]
        if len(previous)<90:raise RuntimeError("LAST_COMPLETE_YEAR_PRIOR_MISSING")
        clim=np.bincount(previous,minlength=3)/len(previous)
        for model,pr in (("BAYES_ONLINE_CHANGEPOINT",forecast),
                         ("TRAILING63_DIRICHLET",trailing),
                         ("LAST_YEAR_CLIMATOLOGY",clim)):
          out.append({"source_test":tag,"date":issue.strftime("%Y-%m-%d"),
             "year":int(r.year),"method":model,"actual":int(r.event),
             "pred":int(np.argmax(pr)),"p_nohit":float(pr[0]),
             "p_upfirst":float(pr[1]),"p_downfirst":float(pr[2]),
             "n_matured_before_issue":len(matured),
             "estimated_current_p_changepoint":float(R[0])})
      # Update happens AFTER target resolves by next 09TR.
      y=int(r.event);n=counts.sum(axis=1)
      py=(counts[:,y]+1)/(n+3)
      growth=R*(1-H)*py
      cp=R.sum()*H/3.
      R=np.r_[cp,growth][:MAX_RUN]
      vec=np.eye(3)[y]
      counts=np.vstack([vec,counts+vec])[:MAX_RUN]
      R=R/R.sum()
      if not np.isfinite(R).all() or not np.isclose(R.sum(),1):
         raise RuntimeError("BOCPD_POSTERIOR_NORMALIZATION")
      matured.append(y)
      matured_with_dates.append((issue,y))
      lastdate=issue
    return pd.DataFrame(out)
