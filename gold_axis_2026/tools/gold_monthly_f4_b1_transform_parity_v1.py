from __future__ import annotations
import argparse, calendar, json, math
from pathlib import Path
import numpy as np
import pandas as pd

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base

DEV_START,DEV_END="2022-04","2024-12"

FEATURES=[
 "NOM10_MR_ANALOG","NOM10_VW_ANALOG",
 "REAL10_MR_ANALOG","REAL10_VW_ANALOG",
 "BROADUSD_MR1","BROADUSD_VW",
 "VIX_MR1","VIX_VW",
 "NDX_MR1","NDX_VW",
 "WTI_MR1","WTI_VW",
 "BRENT_MR1","BRENT_VW",
]

LAGS={
 "NOM10":2,"REAL10":2,
 "BROADUSD":7,
 "VIX":1,"NDX":1,
 "WTI":7,"BRENT":7,
}

def mshift(m,d):
    y,mo=map(int,m.split("-")); z=y*12+mo-1+d
    return f"{z//12:04d}-{z%12+1:02d}"

def month_bounds(m):
    y,mo=map(int,m.split("-"))
    return pd.Timestamp(y,mo,1),pd.Timestamp(y,mo,calendar.monthrange(y,mo)[1])

def generic_weighted_increment(vals,z,log_mode=True):
    a=np.asarray(vals,float)
    if len(a)<5: raise RuntimeError(f"INSUFFICIENT_DAILY_ROWS {len(a)}")
    if log_mode:
        if np.any(a<=0): raise RuntimeError("NONPOSITIVE_DAILY_LEVEL")
        r=np.diff(np.log(a))
    else:
        r=np.diff(a)
    lam=0.1*math.exp(-10.0*float(np.clip(z,0,1)))
    age=np.arange(len(r)-1,-1,-1,dtype=float)
    w=np.exp(-lam*age); w/=w.sum()
    return float(w@r)

def flat_daily(doc,key):
    return {pd.Timestamp(k):float(v) for k,v in doc[key].items()}

def nested_daily(doc,key,field):
    out={}
    for k,z in doc[key].items():
        if field in z and z[field] is not None:
            out[pd.Timestamp(k)]=float(z[field])
    return out

def eligible_month_values(series,month,lag_days):
    a,b=month_bounds(month)
    cutoff=b-pd.Timedelta(days=lag_days)
    rows=[(d,v) for d,v in series.items() if a<=d<=cutoff]
    rows.sort()
    if len(rows)<5:
        raise RuntimeError(f"THIN_MONTH {month} lag={lag_days} n={len(rows)}")
    return np.asarray([v for _,v in rows],float), rows[-1][0].strftime("%Y-%m-%d"), len(rows)

def mean_positive_ratio(series,p,pp,lag):
    vp,_,np_=eligible_month_values(series,p,lag)
    vq,_,nq=eligible_month_values(series,pp,lag)
    mp=float(np.mean(vp)); mq=float(np.mean(vq))
    if mp<=0 or mq<=0: raise RuntimeError("NONPOSITIVE_MONTH_MEAN")
    return float(math.log(mp/mq)),np_,nq

def mean_difference(series,p,pp,lag):
    vp,_,np_=eligible_month_values(series,p,lag)
    vq,_,nq=eligible_month_values(series,pp,lag)
    return float(np.mean(vp)-np.mean(vq)),np_,nq

def transform_for_sample(series_map,p,z):
    pp=mshift(p,-1)
    out={}; obs={}
    for name in ("NOM10","REAL10"):
        s=series_map[name]; lag=LAGS[name]
        mr,np_,nq=mean_difference(s,p,pp,lag)
        vp,last,nv=eligible_month_values(s,p,lag)
        out[f"{name}_MR_ANALOG"]=mr
        out[f"{name}_VW_ANALOG"]=generic_weighted_increment(vp,z,log_mode=False)
        obs[name]={"p_n":np_,"pp_n":nq,"p_last":last}
    for name,prefix in [
      ("BROADUSD","BROADUSD"),("VIX","VIX"),("NDX","NDX"),("WTI","WTI"),("BRENT","BRENT")]:
        s=series_map[name]; lag=LAGS[name]
        mr,np_,nq=mean_positive_ratio(s,p,pp,lag)
        vp,last,nv=eligible_month_values(s,p,lag)
        out[f"{prefix}_MR1"]=mr
        out[f"{prefix}_VW"]=generic_weighted_increment(vp,z,log_mode=True)
        obs[name]={"p_n":np_,"pp_n":nq,"p_last":last}
    return out,obs

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--external-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    b,meta=snap.load_snapshot(a.snapshot)
    ext=json.loads(Path(a.external_v2).read_text())

    required_ready={
      "rates_daily":"READY_FED_H15",
      "fx_daily":"READY_FED_H10",
      "vix_daily":"READY_CBOE",
      "nasdaq100_daily":"READY_NASDAQ_OFFICIAL",
      "wti_daily":"READY_EIA_OFFICIAL",
      "brent_daily":"READY_EIA_OFFICIAL",
    }
    readiness_checks={k:(ext["readiness"].get(k)==v) for k,v in required_ready.items()}

    series={
      "NOM10":nested_daily(ext,"h15_daily","DGS10"),
      "REAL10":nested_daily(ext,"h15_daily","DFII10"),
      "BROADUSD":nested_daily(ext,"h10_daily","BROAD_USD_INDEX"),
      "VIX":flat_daily(ext,"vix_daily"),
      "NDX":flat_daily(ext,"nasdaq100_daily"),
      "WTI":flat_daily(ext,"wti_daily"),
      "BRENT":flat_daily(ext,"brent_daily"),
    }

    stats={k:[] for k in FEATURES}
    min_obs={k:10**9 for k in series}
    max_vw_parity_diff=0.0
    rows_checked=0
    outer_reports=[]

    for outer in base.month_range(DEV_START,DEV_END):
        origin=mshift(outer,-1)
        history=b.gpr_vintages[origin]
        raw=base.all_samples_at_origin(b,outer,governed=True)
        built_keys=[]
        for t in sorted(raw):
            p=mshift(t,-1); pp=mshift(t,-2)
            z=base.gpr_norm(history,pp)
            feat,obs=transform_for_sample(series,p,z)
            for k in FEATURES:
                v=float(feat[k])
                if not np.isfinite(v): raise RuntimeError(f"NONFINITE {outer} {t} {k}")
                stats[k].append(v)
            for k,zobs in obs.items():
                min_obs[k]=min(min_obs[k],int(zobs["p_n"]),int(zobs["pp_n"]))

            # prove generic VW formula is the same as CURRENT8 using Gold as control
            gold_vals=b.daily_month_values["Gold"].get(p)
            if gold_vals is None: raise RuntimeError(f"GOLD_CONTROL_MISSING {p}")
            v1=generic_weighted_increment(gold_vals,z,log_mode=True)
            v2=base.weighted_daily_return(b,"Gold",p,z)
            max_vw_parity_diff=max(max_vw_parity_diff,abs(v1-v2))
            built_keys.append(t); rows_checked+=1

        if built_keys!=sorted(raw):
            raise RuntimeError(f"HISTORY_SHORTENED {outer}")
        outer_reports.append({
          "outer_target":outer,
          "sample_n":len(built_keys),
          "first_sample":built_keys[0],
          "last_sample":built_keys[-1],
        })

    feature_stats={}
    for k,v in stats.items():
        x=np.asarray(v,float)
        feature_stats[k]={
          "n":int(len(x)),"min":float(x.min()),"max":float(x.max()),
          "mean":float(x.mean()),"std":float(x.std()),
          "p01":float(np.quantile(x,.01)),"p99":float(np.quantile(x,.99)),
        }

    gates={
      "external_v2_readiness":all(readiness_checks.values()),
      "vw_formula_parity":max_vw_parity_diff<1e-12,
      "canonical_history_not_shortened":all(r["first_sample"]=="2010-03" for r in outer_reports),
      "all_external_features_finite":all(np.isfinite(list(s.values())).all() for s in feature_stats.values()),
      "minimum_monthly_observations_ge_5":all(v>=5 for v in min_obs.values()),
      "target_month_external_data":False,
      "2025_selection_use":False,
      "2026_selection_use":False,
    }
    gates["pass"]=all(v for k,v in gates.items() if k!="pass")

    out={
      "schema":"GOLD_MONTHLY_F4_B1_TRANSFORM_PARITY_V1_2026-09-29",
      "authority":{
        "snapshot_payload_sha256":meta["payload_sha256"],
        "external_v2_payload_sha256":ext["payload_sha256"],
        "model_fit":False,"neon_reads":0,"random_split":"NONE",
        "lag_architecture":"L1",
        "gpr_weighting":"EXACT_CURRENT8_FORMULA",
        "release_lags_calendar_days":LAGS,
      },
      "readiness_checks":readiness_checks,
      "gates":gates,
      "max_gold_vw_formula_abs_diff":max_vw_parity_diff,
      "min_monthly_observations":min_obs,
      "feature_stats":feature_stats,
      "rows_checked":rows_checked,
      "outer_reports":outer_reports,
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    if not gates["pass"]:
        raise RuntimeError(f"B1_TRANSFORM_PARITY_FAIL {gates}")
    print("F4_B1_TRANSFORM_PARITY_GATE=PASS")
    print(json.dumps({
      "rows_checked":rows_checked,
      "max_gold_vw_formula_abs_diff":max_vw_parity_diff,
      "min_monthly_observations":min_obs,
      "gates":gates,
      "external_v2_payload_sha256":ext["payload_sha256"],
    },sort_keys=True))

if __name__=="__main__": main()
