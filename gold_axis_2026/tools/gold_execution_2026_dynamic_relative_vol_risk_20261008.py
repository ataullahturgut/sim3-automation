"""Lag-safe volatility recalibration and relative-risk alarm; registered before run."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import binomtest,spearmanr
import gold_execution_2026_absolute_move_risk_20261008 as risk
AX=Path(__file__).resolve().parents[1]
BASE="GOLD_EXECUTION_2026_CAUSAL_RELATIVE_VOL_RISK_20261008"
def asof_calibration(g):
    g=g.sort_values("date").reset_index(drop=True)
    prior=[]
    out=[]
    for row in g.itertuples(index=False):
        prev=prior[-63:]
        n=len(prev)
        if n:
            residuals=[np.log((x["actual_abs"]+1e-5)/(x["risk_pred"]+1e-5)) for x in prev]
            correction=np.clip((n/(n+32))*np.median(residuals),-np.log(2),np.log(2))
        else:correction=0.
        estimate=float(row.risk_pred)*float(np.exp(correction))
        reference=[x["corrected"] for x in prev]
        eligible=n>=20
        warning=bool(estimate>=np.quantile(reference,.75)) if eligible else False
        record={"source_test":row.source_test,"date":row.date,"year":int(row.year),
          "actual_abs":float(row.actual_abs),"risk_pred":float(row.risk_pred),
          "naive":float(row.naive),"corrected":estimate,
          "large_event":bool(row.large_event),"down_tail":bool(row.down_tail),
          "alarm":warning,"eligible_alarm":eligible,"past_matured":n}
        out.append(record)
        prior.append(record)
    return pd.DataFrame(out)
