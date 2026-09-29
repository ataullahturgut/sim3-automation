from __future__ import annotations
import argparse,json,math\nfrom collections import defaultdict
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

# One scientific question per variant: representation changes only.
# Monthly-return family replaces MR while retaining VW.
# Daily-summary family replaces VW while retaining 1M MR.
VARIANTS={
  "CURRENT8":{"mr":"MR1","daily":"VW","scope":"ALL"},
  "MR3_ALL":{"mr":"MR3","daily":"VW","scope":"ALL"},
  "MR6_ALL":{"mr":"MR6","daily":"VW","scope":"ALL"},
  "RV_ALL":{"mr":"MR1","daily":"RV","scope":"ALL"},
  "RANGE_ALL":{"mr":"MR1","daily":"RANGE","scope":"ALL"},
  "ABSRET_ALL":{"mr":"MR1","daily":"ABSRET","scope":"ALL"},
}
for m in METALS:
    VARIANTS[f"{m.upper()}_MR3"]={"mr":"MR3","daily":"VW","scope":m}
    VARIANTS[f"{m.upper()}_MR6"]={"mr":"MR6","daily":"VW","scope":m}
    VARIANTS[f"{m.upper()}_RV"]={"mr":"MR1","daily":"RV","scope":m}
    VARIANTS[f"{m.upper()}_RANGE"]={"mr":"MR1","daily":"RANGE","scope":m}
    VARIANTS[f"{m.upper()}_ABSRET"]={"mr":"MR1","daily":"ABSRET","scope":m}

def daily_summary(bundle,metal,origin,z,kind):
    if kind=="VW":
        return base.weighted_daily_return(bundle,metal,origin,z)
    v=bundle.daily_month_values[metal].get(origin)
    if v is None or len(v)<5:
        raise RuntimeError(f"INSUFFICIENT_DAILY_ROWS {metal} {origin}")
    r=np.diff(np.log(np.asarray(v,float)))
    if kind=="RV":
        return float(np.sqrt(np.sum(r*r)))
    if kind=="RANGE":
        return float(math.log(float(np.max(v))/float(np.min(v))))
    if kind=="ABSRET":
        return float(np.mean(np.abs(r)))
    raise KeyError(kind)

def mr_value(bundle,metal,p,kind):
    M=bundle.monthly_metal[metal]
    if kind=="MR1":
        q=base.month_shift(p,-1)
    elif kind=="MR3":
        q=base.month_shift(p,-3)
    elif kind=="MR6":
        q=base.month_shift(p,-6)
    else:
        raise KeyError(kind)
    if p not in M or q not in M:
        raise RuntimeError(f"MONTHLY_METAL_MISSING {metal} p={p} q={q}")
    return float(math.log(M[p]/M[q]))

def rep_sample(bundle,target,gpr_history,spec):
    p=base.month_shift(target,-1)
    pp=base.month_shift(target,-2)
    z=base.gpr_norm(gpr_history,pp)
    x=[]; y=[]
    for metal in METALS:
        M=bundle.monthly_metal[metal]
        if target not in M or p not in M:
            raise RuntimeError(f"TARGET_ORIGIN_METAL_MISSING {metal} {target}")
        use_mr=spec["mr"] if spec["scope"] in ("ALL",metal) else "MR1"
        use_daily=spec["daily"] if spec["scope"] in ("ALL",metal) else "VW"
        x.extend([
          mr_value(bundle,metal,p,use_mr),
          daily_summary(bundle,metal,p,z,use_daily),
        ])
        y.append(math.log(M[target]/M[p]))
    return np.asarray(x,float),np.asarray(y,float)

def merge_prehistory(bundle,path):\n    d=json.loads(Path(path).read_text())\n    dd={m:{k:list(v) for k,v in bundle.daily_month_values[m].items()} for m in METALS}\n    for r in d["daily_2009"]:\n        mk=r["date"][:7]\n        for m in METALS: dd[m].setdefault(mk,[]).append(float(r[m]))\n    bundle.daily_month_values={m:{k:np.asarray(v,float) for k,v in q.items()} for m,q in dd.items()}\n    bundle.monthly_metal={m:{k:float(v.mean()) for k,v in bundle.daily_month_values[m].items()} for m in METALS}\n    return d\n\ndef samples_at_origin(bundle,outer_target,spec):
    origin=base.month_shift(outer_target,-1)
    gh=bundle.gpr_vintages[origin]
    out={}
    for t in base.month_range("2010-03",outer_target):
        try:
            out[t]=rep_sample(bundle,t,gh,spec)
        except RuntimeError:
            continue
    if outer_target not in out:
        raise RuntimeError(f"OUTER_TARGET_NOT_BUILDABLE {outer_target}")
    return out

def evaluate(bundle,variant):
    spec=VARIANTS[variant]
    rows=[]
    for target in base.month_range(DEV_START,DEV_END):
        samples=samples_at_origin(bundle,target,spec)
        p,n,d=anfis.select(samples,target,"CHHHO")
        o=base.month_shift(target,-1)
        rows.append({
          "target":target,"origin":o,"variant":variant,"spec":spec,
          "train_rows":n,"diag":d,
          "pred_log_return_gold":float(p[0]),
          "forecast":float(bundle.core_gold[o]*math.exp(float(p[0]))),
          "actual":float(bundle.core_gold[target]),
          "rw":float(bundle.core_gold[o]),
        })
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--variant",choices=sorted(VARIANTS),required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    bundle,meta=snap.load_snapshot(a.snapshot)
    rows=evaluate(bundle,a.variant)
    metrics=eb.active_metrics(rows)
    out={
      "schema":"GOLD_MONTHLY_CHHHO_F2_REPRESENTATION_V1_2026-09-29",
      "variant":a.variant,
      "spec":VARIANTS[a.variant],
      "representation_definitions":{
        "MR1":"log(monthly_mean[p]/monthly_mean[p-1])",
        "MR3":"log(monthly_mean[p]/monthly_mean[p-3]); completed-origin cumulative 3M momentum",
        "MR6":"log(monthly_mean[p]/monthly_mean[p-6]); completed-origin cumulative 6M momentum",
        "VW":"existing GPR-conditioned causal weighted daily log-return summary",
        "RV":"sqrt(sum(daily_log_return^2)) within completed origin month",
        "RANGE":"log(max_daily_price/min_daily_price) within completed origin month",
        "ABSRET":"mean(abs(daily_log_return)) within completed origin month",
      },
      "authority":{
        "dev":"2022-04..2024-12","random_split":"NONE",
        "2025_used":False,"2026_used":False,"external_features_used":False,
        "lag_search_used":False,"canonical_training_sample_start":"2010-03",\n        "prehistory_payload_sha256":pre["payload_sha256"],
        "feature_count":8,"feature_families":"same four metals, one monthly + one daily summary each",
        "architecture":"same 8D ChHHO-ANFIS / same optimizer / same rule count / same chronological inner validation",
        "neon_reads":0,"snapshot_payload_sha256":meta["payload_sha256"],
      },
      "dev":{"metrics":metrics,"yearly":eb.yearly(rows),"rows":rows},
    }
    if a.variant=="CURRENT8":
        diff=abs(metrics["sum_abs_error"]-BASE_SIGMAAE)
        out["f2_baseline_parity"]={
          "canonical_training_sample_start":"2010-03",
          "reference_sum_abs_error":BASE_SIGMAAE,
          "observed_sum_abs_error":metrics["sum_abs_error"],
          "abs_diff":diff,
          "reference_direction_correct":BASE_DIRECTION,
          "observed_direction_correct":metrics["direction_correct"],
          "prehistory_should_not_affect_current8":True,
          "pass":diff<1e-4 and metrics["direction_correct"]==BASE_DIRECTION,
        }
        if not out["f2_baseline_parity"]["pass"]:
            raise RuntimeError(f"F2_BASELINE_PARITY_FAIL {out['f2_baseline_parity']}")
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("CHHHO_F2_REPRESENTATION_GATE=PASS")
    print(json.dumps({
      "variant":a.variant,
      "sum_abs_error":metrics["sum_abs_error"],
      "direction_correct":metrics["direction_correct"],
      "mae":metrics["mae"],"rmse":metrics["rmse"],
      "baseline_parity":out.get("f2_baseline_parity"),
    },sort_keys=True))
if __name__=="__main__":main()
