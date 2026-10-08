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

def evaluate(p):
    out=[]
    for (source,year),g in p.groupby(["source_test","year"]):
        a=g.actual_abs.to_numpy(float);raw=g.risk_pred.to_numpy(float)
        cal=g.corrected.to_numpy(float);naive=g.naive.to_numpy(float)
        x=g[g.eligible_alarm]
        alarm=x.alarm.to_numpy(bool)
        large=x.large_event.to_numpy(bool);down=x.down_tail.to_numpy(bool)
        def capture(e):
            return float(np.sum(alarm&e)/sum(e)) if sum(e) else None
        def enrichment(e):
            return float(np.mean(e[alarm])/np.mean(e)) if sum(alarm) and sum(e) else None
        wins=int(np.sum(abs(cal-a)<abs(raw-a)))
        losses=int(np.sum(abs(cal-a)>abs(raw-a)))
        out.append({"source_test":source,"year":int(year),"n":len(g),
          "mae_naive_bps":float(np.mean(abs(naive-a))*1e4),
          "mae_frozen_bps":float(np.mean(abs(raw-a))*1e4),
          "mae_dynamic_bps":float(np.mean(abs(cal-a))*1e4),
          "dynamic_vs_frozen_MAE_gain":float(1-np.mean(abs(cal-a))/np.mean(abs(raw-a))),
          "dynamic_vs_naive_MAE_gain":float(1-np.mean(abs(cal-a))/np.mean(abs(naive-a))),
          "correction_wins":wins,"correction_losses":losses,
          "paired_sign_p_descriptive":float(binomtest(wins,wins+losses,.5).pvalue) if wins+losses else 1,
          "alarm_eligible":len(x),"alarm_fraction":float(np.mean(alarm)) if len(x) else None,
          "large_event_rate":float(np.mean(large)) if len(x) else None,
          "large_event_capture":capture(large),"large_event_precision_lift":enrichment(large),
          "down_tail_rate":float(np.mean(down)) if len(x) else None,
          "down_tail_capture":capture(down),"down_tail_precision_lift":enrichment(down)})
    return pd.DataFrame(out)
