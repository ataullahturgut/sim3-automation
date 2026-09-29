from __future__ import annotations
import argparse,json,math
from pathlib import Path
import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_elmfis_baseline_v1 as eb

DEV_START,DEV_END="2022-04","2024-12"
METALS=base.METALS
BASE_SIGMAAE=1413.0297794085
BASE_DIRECTION=23

def json_safe(x):
    if isinstance(x,dict): return {k:json_safe(v) for k,v in x.items()}
    if isinstance(x,list): return [json_safe(v) for v in x]
    if isinstance(x,tuple): return [json_safe(v) for v in x]
    if isinstance(x,(float,np.floating)):
        return float(x) if np.isfinite(x) else ("+INF" if x>0 else "-INF")
    if isinstance(x,(int,np.integer)): return int(x)
    return x

VARIANTS={
  "L1":{"mode":"concat","lags":[1]},
  "L1_L2":{"mode":"concat","lags":[1,2]},
  "L1_L2_L3":{"mode":"concat","lags":[1,2,3]},
  "L1_L3_L6":{"mode":"concat","lags":[1,3,6]},
  "DL3_EQUAL":{"mode":"weighted","lags":[1,2,3],"weights":[1/3,1/3,1/3]},
  "DL3_DECAY":{"mode":"weighted","lags":[1,2,3],"weights":[0.6,0.3,0.1]},
  "DL6_BETA13_FIXED":{"mode":"weighted","lags":[1,2,3,4,5,6],"weights":[36/91,25/91,16/91,9/91,4/91,1/91]},
}

def configure_input_dimension(d):
    common=anfis.common
    rules=common.RULES
    n_ant=rules*d
    common.INPUTS=d
    common.N_ANT=n_ant
    common.PARAM_DIM=2*n_ant
    common.LOWER=np.concatenate([np.full(n_ant,common.CENTER_LOW),np.full(n_ant,math.log(common.SPREAD_LOW))])
    common.UPPER=np.concatenate([np.full(n_ant,common.CENTER_HIGH),np.full(n_ant,math.log(common.SPREAD_HIGH))])
    common.LOCAL_SIGMA=np.concatenate([np.full(n_ant,.45),np.full(n_ant,.30)])
    common.REFIT_SIGMA=np.concatenate([np.full(n_ant,.16),np.full(n_ant,.12)])
    anfis.D=common.PARAM_DIM
    anfis.LO=common.LOWER
    anfis.HI=common.UPPER

def merge_prehistory(bundle,path):
    d=json.loads(Path(path).read_text())
    dd={m:{k:list(v) for k,v in bundle.daily_month_values[m].items()} for m in METALS}
    for r in d["daily_2009"]:
        mk=r["date"][:7]
        for m in METALS: dd[m].setdefault(mk,[]).append(float(r[m]))
    bundle.daily_month_values={m:{k:np.asarray(v,float) for k,v in q.items()} for m,q in dd.items()}
    bundle.monthly_metal={m:{k:float(v.mean()) for k,v in bundle.daily_month_values[m].items()} for m in METALS}
    return d

def current8_block(bundle,month,gpr_history):
    prev=base.month_shift(month,-1)
    z=base.gpr_norm(gpr_history,prev)
    x=[]
    for metal in METALS:
        M=bundle.monthly_metal[metal]
        if month not in M or prev not in M:
            raise RuntimeError(f"MONTHLY_METAL_MISSING {metal} {month} {prev}")
        x.extend([
          float(math.log(M[month]/M[prev])),
          float(base.weighted_daily_return(bundle,metal,month,z)),
        ])
    return np.asarray(x,float)

def lagged_sample(bundle,target,gpr_history,spec):
    p=base.month_shift(target,-1)
    blocks=[]
    for lag in spec["lags"]:
        m=base.month_shift(p,-(lag-1))
        blocks.append(current8_block(bundle,m,gpr_history))
    if spec["mode"]=="concat":
        x=np.concatenate(blocks)
    else:
        w=np.asarray(spec["weights"],float)
        w=w/w.sum()
        x=np.sum(np.stack(blocks)*w[:,None],axis=0)
    y=[]
    for metal in METALS:
        M=bundle.monthly_metal[metal]
        if target not in M or p not in M: raise RuntimeError(f"TARGET_MISSING {metal} {target}")
        y.append(math.log(M[target]/M[p]))
    return np.asarray(x,float),np.asarray(y,float)

def samples_at_origin(bundle,outer_target,spec):
    origin=base.month_shift(outer_target,-1)
    gh=bundle.gpr_vintages[origin]
    out={}
    for t in base.month_range("2010-03",outer_target):
        try: out[t]=lagged_sample(bundle,t,gh,spec)
        except RuntimeError: continue
    if outer_target not in out: raise RuntimeError(f"OUTER_TARGET_NOT_BUILDABLE {outer_target}")
    return out

def evaluate(bundle,variant):
    spec=VARIANTS[variant]
    d=8*len(spec["lags"]) if spec["mode"]=="concat" else 8
    configure_input_dimension(d)
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        samples=samples_at_origin(bundle,target,spec)
        p,n,diag=anfis.select(samples,target,"CHHHO")
        o=base.month_shift(target,-1)
        rows.append({
          "target":target,"origin":o,"variant":variant,"spec":spec,
          "input_dimension":d,"train_rows":n,"diag":diag,
          "pred_log_return_gold":float(p[0]),
          "forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[target]),"rw":float(bundle.core_gold[o]),
        })
    return rows,d

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--prehistory",required=True)
    ap.add_argument("--variant",choices=sorted(VARIANTS),required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    b,meta=snap.load_snapshot(a.snapshot)
    pre=merge_prehistory(b,a.prehistory)
    rows,d=evaluate(b,a.variant)
    m=eb.active_metrics(rows)
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F3_LAG_AUDIT_V1_2026-09-29",
      "variant":a.variant,"spec":VARIANTS[a.variant],"input_dimension":d,
      "lag_semantics":"L1=current completed origin month; L2=one month older; etc. Each lag retains MR1+GPR-conditioned VW.",
      "authority":{
        "dev":"2022-04..2024-12","random_split":"NONE","2025_used":False,"2026_used":False,
        "representation":"FROZEN_CURRENT8_MR1_PLUS_VW","external_features_used":False,
        "architecture":"same ChHHO-ANFIS optimizer/rule count/chronological inner validation; input dimension changes only for concatenated lag packs",
        "training_sample_start":"2010-03","neon_reads":0,
        "snapshot_payload_sha256":meta["payload_sha256"],"prehistory_payload_sha256":pre["payload_sha256"],
      },
      "dev":{"metrics":m,"yearly":eb.yearly(rows),"rows":rows},
    }
    if a.variant=="L1":
        diff=abs(m["sum_abs_error"]-BASE_SIGMAAE)
        out["f3_baseline_parity"]={"reference_sum_abs_error":BASE_SIGMAAE,"observed_sum_abs_error":m["sum_abs_error"],
          "abs_diff":diff,"reference_direction_correct":BASE_DIRECTION,"observed_direction_correct":m["direction_correct"],
          "pass":diff<1e-4 and m["direction_correct"]==BASE_DIRECTION}
        if not out["f3_baseline_parity"]["pass"]: raise RuntimeError(f"F3_BASELINE_PARITY_FAIL {out['f3_baseline_parity']}")
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F3_LAG_GATE=PASS")
    print(json.dumps({"variant":a.variant,"input_dimension":d,"sum_abs_error":m["sum_abs_error"],
      "direction_correct":m["direction_correct"],"mae":m["mae"],"rmse":m["rmse"],
      "baseline_parity":out.get("f3_baseline_parity")},sort_keys=True))
if __name__=="__main__":main()
