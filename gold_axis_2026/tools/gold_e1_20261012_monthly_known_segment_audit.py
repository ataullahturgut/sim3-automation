"""E1 2026-10-12: fixed historical forecasts versus origin-known price controls.
Read-only offline replay. No model fitting, no lookahead feature.
Requires numpy for seeded moving-block bootstrap. Run from any cwd.
"""
import csv
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"GOLD_E1_20261012_MONTHLY_KNOWN_SEGMENT_INPUT_ROWS.csv"
OUT=ROOT/"GOLD_E1_20261012_MONTHLY_KNOWN_SEGMENT_RECALC.json"

def sign(z):
    return 1 if z>0 else -1 if z<0 else 0

def err(a,b):
    return abs(a-b)

def main():
    with SOURCE.open(newline="",encoding="utf-8") as f:
        d=list(csv.DictReader(f))
    assert len(d)==52 and len({r["target_month"] for r in d})==52
    dev=[r for r in d if r["cohort"]=="DEV"]
    assert len(dev)==33 and [r["target_month"] for r in dev]==sorted(r["target_month"] for r in dev)
    x=[]
    by_cohort={}
    for name in ("DEV","OPENED2025","OPENED2026"):
        rws=[r for r in d if r["cohort"]==name]
        obs=np.array([float(r["wb_target_avg"]) for r in rws])
        bases={
            "WB_origin_mean":np.array([float(r["origin_wb_avg"]) for r in rws]),
            "STAK_origin_mean":np.array([float(r["origin_stak_avg"]) for r in rws]),
            "STAK_origin_last":np.array([float(r["origin_stak_last"]) for r in rws]),
        }
        if name=="DEV":
            bases["frozen_ChHHO"]=np.array([float(r["frozen_chhho_forecast"]) for r in rws])
        by_cohort[name]={"n":len(rws),
            "sum_absolute_error":{k:float(np.abs(obs-v).sum()) for k,v in bases.items()},
            "mean_absolute_error":{k:float(np.abs(obs-v).mean()) for k,v in bases.items()}}
        if name=="DEV":
            last_abs=np.abs(obs-bases["STAK_origin_last"])
            ch_abs=np.abs(obs-bases["frozen_ChHHO"])
            x=last_abs-ch_abs
            anchor=bases["WB_origin_mean"]
            sc=np.array([sign(v-a) for v,a in zip(bases["frozen_ChHHO"],anchor)])
            sl=np.array([sign(v-a) for v,a in zip(bases["STAK_origin_last"],anchor)])
            sy=np.array([sign(v-a) for v,a in zip(obs,anchor)])
            by_cohort[name]["direction_vs_prev_WB_mean"]={
                "n_nonflat":int((sy!=0).sum()),
                "n_flat":int((sy==0).sum()),
                "ChHHO_correct":int(((sc==sy)&(sy!=0)).sum()),
                "STAK_last_correct":int(((sl==sy)&(sy!=0)).sum())}
            by_cohort[name]["paired_LAST_minus_CHHHO"]={
                "sum_error_reduction":float(x.sum()),
                "mean_error_reduction":float(x.mean()),
                "ChHHO_month_wins":int((x>0).sum()),
                "STAK_last_month_wins":int((x<0).sum())}
    # Moving blocks of three adjacent calendar months. Already-inspected DEV;
    # descriptive uncertainty, not a prospective model-selection p-value.
    rng=np.random.default_rng(20261012)
    n=len(x)
    boot=[]
    for _ in range(20000):
        indices=[]
        while len(indices)<n:
            s=int(rng.integers(0,n-3+1))
            indices.extend(range(s,s+3))
        boot.append(float(x[indices[:n]].mean()))
    ci=np.quantile(boot,[0.025,0.975])
    by_cohort["DEV"]["paired_LAST_minus_CHHHO"]["moving_block3_bootstrap_mean_CI95"]=[float(ci[0]),float(ci[1])]
    by_cohort["DEV"]["paired_LAST_minus_CHHHO"]["moving_block3_bootstrap_Pr_delta_le_zero"]=float((np.array(boot)<=0).mean())
    assert abs(by_cohort["DEV"]["sum_absolute_error"]["frozen_ChHHO"]-1413.0297794084559)<0.000001
    assert abs(by_cohort["DEV"]["sum_absolute_error"]["STAK_origin_mean"]-1767.0457509633763)<0.0001
    summary={"scope":"retrospective archival; historical first-print timing not certified",
        "monthly_target":"CORE5 (WB-derived) monthly average",
        "origin_last_proxy":"StakTrakr retrospective last daily observation in completed month",
        "chhho_frozen_source":"GitHub Actions artifact 11049132605, month_analysis 33 rows",
        "groups":by_cohort,
        "warnings":["Sources WB and StakTrakr differ; last price not a certified tradable month-end or PIT issue quote",
                    "Monthly CORE5 and daily StakTrakr observations were ingested in September 2026, no real-time as-of proof",
                    "No DE-ABC monthly row predictions supplied in this audit; not scored",
                    "2025/2026 are already inspected: price-only baselines; no frozen ChHHO claims for those years"]}
    OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
