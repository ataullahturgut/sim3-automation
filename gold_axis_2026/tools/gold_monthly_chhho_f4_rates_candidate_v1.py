from __future__ import annotations
import argparse, calendar, json, math
from pathlib import Path
import numpy as np
import pandas as pd

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_elmfis_baseline_v1 as eb

DEV_START,DEV_END="2022-04","2024-12"
COMMON_START="2010-04"
CANDIDATES={
 "BASE":[],
 "R_NOM10":["nom10_chg"],
 "R_REAL10":["real10_chg"],
 "R_BE10":["be10_chg"],
 "R_NOM_REAL":["nom10_chg","real10_chg"],
 "R_REAL_BE":["real10_chg","be10_chg"],
 "R_REAL_FF":["real10_chg","ff_lagged_chg"],
}

def configure_dim(d):
    c=anfis.common; rules=c.RULES; n=rules*d
    c.INPUTS=d;c.N_ANT=n;c.PARAM_DIM=2*n
    c.LOWER=np.concatenate([np.full(n,c.CENTER_LOW),np.full(n,math.log(c.SPREAD_LOW))])
    c.UPPER=np.concatenate([np.full(n,c.CENTER_HIGH),np.full(n,math.log(c.SPREAD_HIGH))])
    c.LOCAL_SIGMA=np.concatenate([np.full(n,.45),np.full(n,.30)])
    c.REFIT_SIGMA=np.concatenate([np.full(n,.16),np.full(n,.12)])
    anfis.D=c.PARAM_DIM;anfis.LO=c.LOWER;anfis.HI=c.UPPER

def mshift(m,d):
    y,mo=map(int,m.split("-"));z=y*12+mo-1+d
    return f"{z//12:04d}-{z%12+1:02d}"
def mend(m):
    y,mo=map(int,m.split("-")); return pd.Timestamp(y,mo,calendar.monthrange(y,mo)[1])

def load_ext(path):
    d=json.loads(Path(path).read_text())
    h15={pd.Timestamp(k):v for k,v in d["h15_daily"].items()}
    dates=sorted(h15)
    core=d["core5_monthly"]
    return d,h15,dates,core

def last_known(h15,dates,month,key,lag=2):
    cut=mend(month)-pd.Timedelta(days=lag)
    for dt in reversed(dates):
        if dt<=cut:
            v=h15[dt].get(key)
            if v is not None: return float(v)
    raise RuntimeError(f"NO_H15 {month} {key}")

def feat_for_origin(h15,dates,core,p):
    pp=mshift(p,-1)
    nom=last_known(h15,dates,p,"DGS10"); pnom=last_known(h15,dates,pp,"DGS10")
    real=last_known(h15,dates,p,"DFII10"); preal=last_known(h15,dates,pp,"DFII10")
    be=last_known(h15,dates,p,"BREAKEVEN10_PROXY"); pbe=last_known(h15,dates,pp,"BREAKEVEN10_PROXY")
    p1=mshift(p,-1);p2=mshift(p,-2)
    if p1 not in core or p2 not in core: raise RuntimeError(f"NO_FF {p}")
    ff=float(core[p1]["FEDFUNDS_MONTHLY"])-float(core[p2]["FEDFUNDS_MONTHLY"])
    return {"nom10_chg":nom-pnom,"real10_chg":real-preal,"be10_chg":be-pbe,"ff_lagged_chg":ff}

def candidate_samples(bundle,outer_target,cols,h15,dates,core):
    raw=base.all_samples_at_origin(bundle,outer_target,governed=True)
    out={}
    for t,(x,y) in raw.items():
        if t<COMMON_START: continue
        p=mshift(t,-1)
        f=feat_for_origin(h15,dates,core,p)
        ext=np.asarray([f[c] for c in cols],float)
        out[t]=(np.concatenate([np.asarray(x,float),ext]),np.asarray(y,float))
    if outer_target not in out: raise RuntimeError(f"OUTER_TARGET_MISSING {outer_target}")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--external",required=True)
    ap.add_argument("--candidate",choices=sorted(CANDIDATES),required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    b,meta=snap.load_snapshot(a.snapshot)
    extdoc,h15,dates,core=load_ext(a.external)
    cols=CANDIDATES[a.candidate]
    configure_dim(8+len(cols))
    rows=[]
    for t in base.month_range(DEV_START,DEV_END):
        s=candidate_samples(b,t,cols,h15,dates,core)
        p,n,d=anfis.select(s,t,"CHHHO")
        o=mshift(t,-1)
        rows.append({"target":t,"origin":o,"candidate":a.candidate,"columns":cols,
          "train_rows":n,"diag":d,"inner_validation_fitness":float(d["meta_check_fitness"]),
          "pred_log_return_gold":float(p[0]),"forecast":float(b.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(b.core_gold[t]),"rw":float(b.core_gold[o])})
    m=eb.active_metrics(rows)
    out={"schema":"GOLD_MONTHLY_CHHHO_F4_RATES_CANDIDATE_V1_2026-09-29",
      "candidate":a.candidate,"columns":cols,
      "authority":{"dev":"2022-04..2024-12","common_training_start":COMMON_START,
        "random_split":"NONE","2025_used":False,"2026_used":False,
        "internal_contract":"CURRENT8_MR1_VW_L1_FROZEN","native_external":True,
        "rates_h15_cutoff_days":2,"fedfunds_rule":"p-1 minus p-2 monthly",
        "neon_reads":0,"snapshot_payload_sha256":meta["payload_sha256"],
        "external_payload_sha256":extdoc["payload_sha256"]},
      "dev":{"metrics":m,"yearly":eb.yearly(rows),"rows":rows}}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_RATES_CANDIDATE_GATE=PASS")
    print(json.dumps({"candidate":a.candidate,"columns":cols,"sum_abs_error":m["sum_abs_error"],
      "direction_correct":m["direction_correct"],"mae":m["mae"],"rmse":m["rmse"]},sort_keys=True))
if __name__=="__main__":main()
