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

def month_block_intervals(p):
    rng=np.random.default_rng(20261008)
    rows=[]
    for (source,year),g in p.groupby(["source_test","year"]):
        groups=[q for _,q in g.groupby(g.date.str.slice(0,7))]
        block_count=len(groups)
        if block_count<4:continue
        samples=[]
        for _ in range(1500):
            idx=rng.integers(0,block_count,size=block_count)
            chosen=pd.concat([groups[int(j)] for j in idx],ignore_index=True)
            a=chosen.actual_abs.to_numpy(float)
            calibrated=chosen.corrected.to_numpy(float)
            naive=chosen.naive.to_numpy(float)
            samples.append(1-np.mean(abs(calibrated-a))/np.mean(abs(naive-a)))
        rows.append({"source_test":source,"year":int(year),
          "n":len(g),"months_as_blocks":block_count,"iterations":1500,
          "lower_95":float(np.quantile(samples,.025)),
          "upper_95":float(np.quantile(samples,.975)),
          "bootstrap_positive_fraction":float(np.mean(np.array(samples)>0)),
          "retrospective_descriptive_not_out_of_sample":True})
    return pd.DataFrame(rows)

def main():
    q,t=risk.src.source_load()
    m,source_proof=risk.mirror.load_approved()
    qm=m.set_index("bar_start_utc")[["bid_open","bid_close"]]
    qm=qm.rename(columns={"bid_open":"open","bid_close":"close"})
    tm,_=risk.direct.candidate_targets(t,qm)
    qold,told,qn,tn,qc=risk.primary.load()
    if len(qold)!=len(q):raise RuntimeError("HISTORICAL_IDENTITY_CHANGED")
    records=[]
    for label,px,targets in (("MIRROR_SAME_UPSTREAM_JAN_AUG20",qm,tm),
                             ("DIRECT_PRIMARY_NATIVE_THROUGH_OCT07",qn,tn)):
        features=risk.panel(q,t,px,targets)
        original=risk.produce_predictions(features,label)
        records.append(asof_calibration(original))
    p=pd.concat(records,ignore_index=True)
    if p.duplicated(["source_test","date"]).any():raise RuntimeError("DUPLICATE_ORIGIN")
    metrics=evaluate(p)
    intervals=month_block_intervals(p)
    intervals.to_csv(AX/(BASE+"_MONTH_BLOCK_UNCERTAINTY.csv"),index=False)
    print("MONTH_BLOCK_DESCRIPTIVE_INTERVALS",intervals.to_string(index=False),flush=True)
    state={"status":"CAUSAL_RELATIVE_RISK_RECALIBRATION_ACTUALLY_EXECUTED",
      "source_years":"2025 historical EV BIDASK, 2026 mirror versus direct primary separately",
      "regression":"previous prereg fixed 2025 or 2026 absolute-move ridge",
      "calibration":"63 earlier-matured absolute-return ratios with n/(n+32) shrink; cap [0.5,2]",
      "alert":"past 63 corrected forecasts 75th quantile, minimum 20 matured forecasts",
      "2026_past_matured_labels_allowed":True,"2026_future_label_leakage":False,
      "no_2026_unseen_claim":True,"bank_PnL_not_evaluated":True}
    (AX/(BASE+"_SUMMARY.json")).write_text(json.dumps(state,indent=2)+"\n")
    metrics.to_csv(AX/(BASE+"_METRICS.csv"),index=False)
    p.to_csv(AX/(BASE+"_PRIVATE_DATED.csv"),index=False)
    print("REAL_RELATIVE_RISK_EVIDENCE",metrics.to_string(index=False),flush=True)
    print("RELATIVE_RISK_QC",json.dumps(state),flush=True)
if __name__=="__main__":main()
