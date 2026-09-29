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
BASE_SIGMAAE=1413.0297794085
BASE_DIRECTION=23

CANDIDATES={
 "BASE":[],
 "FX_BROAD":["broad_usd_ret"],
 "FX_CNY":["cny_usdstrength_ret"],
 "FX_SAFEHAVEN":["safehaven_rotation"],
 "FX_BROAD_CNY":["broad_usd_ret","cny_usdstrength_ret"],
 "FX_BROAD_SAFE":["broad_usd_ret","safehaven_rotation"],
 "FX_BREADTH_DISP":["usd_breadth","fx_dispersion"],
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
    h10={pd.Timestamp(k):v for k,v in d["h10_daily"].items()}
    dates=sorted(h10)
    if not dates or dates[0]>pd.Timestamp("2010-01-15"):
        raise RuntimeError(f"H10_HISTORY_TOO_SHORT first={dates[0] if dates else None}")
    return d,h10,dates

def last_known(h10,dates,month,key,lag=7):
    cut=mend(month)-pd.Timedelta(days=lag)
    for dt in reversed(dates):
        if dt<=cut:
            v=h10[dt].get(key)
            if v is not None: return float(v)
    raise RuntimeError(f"NO_H10 {month} {key}")

def logret(a,b):
    if a<=0 or b<=0: raise RuntimeError(f"NONPOSITIVE_FX {a} {b}")
    return float(math.log(a/b))

def feat_for_origin(h10,dates,p):
    pp=mshift(p,-1)
    cur={k:last_known(h10,dates,p,k) for k in [
      "BROAD_USD_INDEX","EURUSD_QUOTE","GBPUSD_QUOTE","JPY_PER_USD","CHF_PER_USD","CNY_PER_USD"]}
    prv={k:last_known(h10,dates,pp,k) for k in cur}

    broad=logret(cur["BROAD_USD_INDEX"],prv["BROAD_USD_INDEX"])
    eur=-logret(cur["EURUSD_QUOTE"],prv["EURUSD_QUOTE"])
    gbp=-logret(cur["GBPUSD_QUOTE"],prv["GBPUSD_QUOTE"])
    jpy=logret(cur["JPY_PER_USD"],prv["JPY_PER_USD"])
    chf=logret(cur["CHF_PER_USD"],prv["CHF_PER_USD"])
    cny=logret(cur["CNY_PER_USD"],prv["CNY_PER_USD"])
    majors=np.asarray([eur,jpy,gbp,chf,cny],float)
    breadth=float(np.mean(np.sign(majors)))
    dispersion=float(np.std(majors))
    safehaven=float(np.mean([-jpy,-chf])-broad)
    return {
      "broad_usd_ret":broad,
      "cny_usdstrength_ret":cny,
      "safehaven_rotation":safehaven,
      "usd_breadth":breadth,
      "fx_dispersion":dispersion,
    }

def candidate_samples(bundle,outer_target,cols,h10,dates):
    raw=base.all_samples_at_origin(bundle,outer_target,governed=True)
    out={}
    for t,(x,y) in raw.items():
        if not cols:
            out[t]=(np.asarray(x,float).copy(),np.asarray(y,float).copy())
            continue
        p=mshift(t,-1)
        f=feat_for_origin(h10,dates,p)
        ext=np.asarray([f[c] for c in cols],float)
        if not np.all(np.isfinite(ext)): raise RuntimeError(f"NONFINITE_FX_FEATURE {t} {cols} {ext}")
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
    extdoc,h10,dates=load_ext(a.external)
    cols=CANDIDATES[a.candidate]
    configure_dim(8+len(cols))

    rows=[]
    for t in base.month_range(DEV_START,DEV_END):
        s=candidate_samples(b,t,cols,h10,dates)
        p,n,d=anfis.select(s,t,"CHHHO")
        o=mshift(t,-1)
        rows.append({
          "target":t,"origin":o,"candidate":a.candidate,"columns":cols,
          "train_rows":n,"diag":d,"inner_validation_fitness":float(d["meta_check_fitness"]),
          "pred_log_return_gold":float(p[0]),
          "forecast":float(b.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(b.core_gold[t]),"rw":float(b.core_gold[o]),
        })

    m=eb.active_metrics(rows)
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F4_FX_CANDIDATE_V1_2026-09-29",
      "candidate":a.candidate,"columns":cols,
      "authority":{
        "dev":"2022-04..2024-12","training_history":"CANONICAL_UNCHANGED",
        "random_split":"NONE","2025_used":False,"2026_used":False,
        "internal_contract":"CURRENT8_MR1_VW_L1_FROZEN","native_external":True,
        "fx_h10_cutoff_days":7,"neon_reads":0,
        "snapshot_payload_sha256":meta["payload_sha256"],
        "external_payload_sha256":extdoc["payload_sha256"],
      },
      "dev":{"metrics":m,"yearly":eb.yearly(rows),"rows":rows},
    }

    if a.candidate=="BASE":
        diff=abs(m["sum_abs_error"]-BASE_SIGMAAE)
        parity={
          "reference_sum_abs_error":BASE_SIGMAAE,
          "observed_sum_abs_error":m["sum_abs_error"],
          "abs_diff":diff,
          "reference_direction_correct":BASE_DIRECTION,
          "observed_direction_correct":m["direction_correct"],
          "pass":diff<1e-4 and m["direction_correct"]==BASE_DIRECTION,
        }
        out["baseline_parity"]=parity
        if not parity["pass"]: raise RuntimeError(f"F4_FX_BASE_PARITY_FAIL {parity}")

    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_FX_CANDIDATE_GATE=PASS")
    print(json.dumps({
      "candidate":a.candidate,"columns":cols,
      "sum_abs_error":m["sum_abs_error"],"direction_correct":m["direction_correct"],
      "mae":m["mae"],"rmse":m["rmse"],
      "baseline_parity":out.get("baseline_parity"),
    },sort_keys=True))

if __name__=="__main__": main()
