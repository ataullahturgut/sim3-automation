from __future__ import annotations

import argparse, json, math
from pathlib import Path
import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import gold_monthly_f4_b1_transform_parity_v1 as b1
import gold_monthly_f4_all6_compact_candidate_v1 as all6core

FEATURES=["BROADUSD_MR1","BROADUSD_MIDAS_DIRECTIONAL"]
TOTAL_INPUTS=10
POPULATION=30

# Frozen before outcome. u=0 newest daily return, u=1 oldest.
THETA_CANDIDATES=[
    (0.0,0.0),
    (-1.0,0.0),(-2.0,0.0),(-4.0,0.0),(-8.0,0.0),
    (1.0,-2.0),(2.0,-4.0),(4.0,-8.0),
    (2.0,-2.0),(4.0,-4.0),
]
ANFIS_VAL_FRAC=0.20
ANFIS_MIN_VAL=12
MIDAS_VAL_FRAC=0.20
MIDAS_MIN_VAL=12


def configure():
    cfg=all6core.configure(TOTAL_INPUTS,POPULATION)
    expected={"inputs":10,"rules":5,"antecedent_parameter_dimension":100,
              "population":30,"generations":45,"repeats":3}
    if cfg!=expected:
        raise RuntimeError(f"FX3_OPTIMIZER_PARITY_FAIL observed={cfg} expected={expected}")
    return cfg


def usd_series(ext):
    return b1.nested_daily(ext,"h10_daily","BROAD_USD_INDEX")


def daily_log_returns(series,p):
    vals,_,_=b1.eligible_month_values(series,p,b1.LAGS["BROADUSD"])
    if np.any(vals<=0):
        raise RuntimeError(f"NONPOSITIVE_BROADUSD {p}")
    r=np.diff(np.log(vals))
    if len(r)<4:
        raise RuntimeError(f"THIN_DAILY_RETURNS {p} n={len(r)}")
    return np.asarray(r,float)


def almon_scalar(r,theta1,theta2):
    n=len(r)
    # r oldest->newest. age u: newest=0, oldest=1.
    u=np.linspace(1.0,0.0,n)
    z=theta1*u+theta2*u*u
    z=z-z.max()
    w=np.exp(z); w=w/w.sum()
    return float(np.dot(w,r))


def monthly_mr(series,p):
    pp=b1.mshift(p,-1)
    mr,_,_=b1.mean_positive_ratio(series,p,pp,b1.LAGS["BROADUSD"])
    return float(mr)


def candidate_scalar(series,t,theta):
    p=b1.mshift(t,-1)
    return almon_scalar(daily_log_returns(series,p),theta[0],theta[1])


def select_theta(raw,series,outer_target):
    keys=sorted(k for k in raw if k<outer_target)
    n=len(keys)
    anv=max(ANFIS_MIN_VAL,int(round(ANFIS_VAL_FRAC*n)))
    asplit=n-anv
    if asplit<30:
        raise RuntimeError(f"ANFIS_INNER_TRAIN_TOO_SMALL {outer_target} split={asplit}")

    # MIDAS parameter selection uses ONLY the ANFIS inner-train pool.
    pool=keys[:asplit]
    mn=len(pool)
    mnv=max(MIDAS_MIN_VAL,int(round(MIDAS_VAL_FRAC*mn)))
    msplit=mn-mnv
    if msplit<30:
        raise RuntimeError(f"MIDAS_SUBTRAIN_TOO_SMALL {outer_target} split={msplit}")

    tr=pool[:msplit]; va=pool[msplit:]
    ytr=np.asarray([float(np.asarray(raw[k][1],float)[0]) for k in tr])
    yva=np.asarray([float(np.asarray(raw[k][1],float)[0]) for k in va])

    scored=[]
    for th in THETA_CANDIDATES:
        xtr=np.asarray([candidate_scalar(series,k,th) for k in tr])
        xva=np.asarray([candidate_scalar(series,k,th) for k in va])
        X=np.c_[np.ones(len(xtr)),xtr]
        beta=np.linalg.lstsq(X,ytr,rcond=1e-8)[0]
        pred=np.c_[np.ones(len(xva)),xva]@beta
        mae=float(np.mean(np.abs(pred-yva)))
        scored.append((mae,abs(th[0])+abs(th[1]),th))

    scored.sort(key=lambda x:(x[0],x[1],x[2]))
    best=scored[0]
    return best[2],{
        "selection_rule":"nested_pre_ANFIS_validation_univariate_gold_return_MAE",
        "anfis_pretarget_rows":n,
        "anfis_inner_train_rows":asplit,
        "anfis_validation_rows":anv,
        "midas_pool_rows":mn,
        "midas_subtrain_rows":msplit,
        "midas_subvalidation_rows":mnv,
        "selected_theta1":best[2][0],
        "selected_theta2":best[2][1],
        "selected_subvalidation_mae":best[0],
        "candidate_count":len(THETA_CANDIDATES),
    }


def samples_for_outer(bundle,outer_target,series):
    raw=base.all_samples_at_origin(bundle,outer_target,governed=True)
    theta,mdiag=select_theta(raw,series,outer_target)
    out={}
    for t,(x,y) in raw.items():
        p=b1.mshift(t,-1)
        mr=monthly_mr(series,p)
        ds=almon_scalar(daily_log_returns(series,p),theta[0],theta[1])
        xx=np.concatenate([np.asarray(x,float),np.asarray([mr,ds],float)])
        if xx.shape!=(TOTAL_INPUTS,) or not np.all(np.isfinite(xx)):
            raise RuntimeError(f"BAD_FX3_VECTOR outer={outer_target} t={t}")
        out[t]=(xx,np.asarray(y,float))
    return out,theta,mdiag


def run_rows(bundle,ext,start,end):
    cfg=configure(); series=usd_series(ext); rows=[]
    for t in base.month_range(start,end):
        samples,theta,mdiag=samples_for_outer(bundle,t,series)
        keys=sorted(k for k in samples if k<t)
        if not keys or keys[0]!="2010-03":
            raise RuntimeError(f"HISTORY_PARITY_FAIL {t}")
        p,n,diag=anfis.select(samples,t,"CHHHO")
        o=base.month_shift(t,-1)
        forecast=float(bundle.core_gold[o]*math.exp(float(p[0])))
        actual=float(bundle.core_gold[t])
        if not np.isfinite(forecast): raise RuntimeError(f"NONFINITE_FORECAST {t}")
        rows.append({
          "target":t,"origin":o,"variant":"FX3_BROADUSD_MR1_PLUS_DIRECTIONAL_ALMON_MIDAS",
          "input_dimension":TOTAL_INPUTS,"population":POPULATION,"train_rows":n,
          "midas_theta1":theta[0],"midas_theta2":theta[1],"midas_diag":mdiag,"diag":diag,
          "pred_log_return_gold":float(p[0]),"forecast":forecast,"actual":actual,
          "rw":float(bundle.core_gold[o]),"abs_error":abs(forecast-actual),
          "signed_error":forecast-actual,
        })
    return cfg,rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True); ap.add_argument("--external-v2",required=True)
    ap.add_argument("--b2-audit",required=True); ap.add_argument("--start",required=True)
    ap.add_argument("--end",required=True); ap.add_argument("--label",required=True)
    ap.add_argument("--output",required=True); a=ap.parse_args()

    bundle,smeta=snap.load_snapshot(a.snapshot)
    ext=json.loads(Path(a.external_v2).read_text())
    b2doc=json.loads(Path(a.b2_audit).read_text())
    if not b2doc.get("gates",{}).get("pass"): raise RuntimeError("B2_AUTHORITY_NOT_PASS")
    if ext.get("payload_sha256")!=b2doc.get("authority",{}).get("external_v2_payload_sha256"):
        raise RuntimeError("EXTERNAL_V2_PAYLOAD_MISMATCH")

    cfg,rows=run_rows(bundle,ext,a.start,a.end)
    out={
      "schema":"GOLD_MONTHLY_F4_FX3_DIRECTIONAL_ALMON_MIDAS_SHARD_V1_2026-09-29",
      "label":a.label,"start":a.start,"end":a.end,"feature_names":FEATURES,
      "optimizer":cfg,
      "midas_contract":{
        "family":"EXPONENTIAL_ALMON",
        "age_normalization":"u=0 newest, u=1 oldest",
        "candidate_thetas":THETA_CANDIDATES,
        "selection":"nested within ANFIS inner-train; ANFIS validation untouched",
        "selection_objective":"univariate Gold log-return MAE on nested chronological subvalidation",
      },
      "authority":{
        "selection_period":"2022-04..2024-12","2025_used":False,"2026_used":False,
        "random_split":"NONE","target_month_in_training":False,
        "release_lag_calendar_days":int(b1.LAGS["BROADUSD"]),
        "monthly_representation":"log(mean(BROADUSD[p])/mean(BROADUSD[p-1]))",
        "daily_path_representation":"training-only selected exponential-Almon weighted daily log returns",
        "gpr_fx_weighting_used":False,
        "downstream_pipeline":"SHARED_CHRONOLOGICAL_SCALING_ANFIS_LOCAL_REFIT",
        "snapshot_payload_sha256":smeta["payload_sha256"],
        "external_v2_payload_sha256":ext["payload_sha256"],
        "b2_gate_schema":b2doc.get("schema"),"neon_reads":0,
      },"rows":rows
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("F4_FX3_SHARD_GATE=PASS")
    print(json.dumps({"label":a.label,"n":len(rows),"optimizer":cfg},sort_keys=True))


if __name__=="__main__":
    main()
