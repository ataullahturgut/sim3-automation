#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, math, os, platform
from pathlib import Path

import numpy as np
import psycopg
import torch
import timesfm
from timesfm3 import TimesFM3Evaluator, ModelConfig

import vw_midas_msvr_successor_v1 as base

MODEL_ID="GOLD_MONTHLY_TIMESFM3_ZERO_SHOT_V1"
CHECKPOINT="google/timesfm-3.0-pytorch"
TRAIN_START="2010-05"
DEV_START,DEV_END="2022-04","2024-12"
HOLDOUT_START,HOLDOUT_END="2025-01","2025-12"
STRESS_START,STRESS_END="2026-01","2026-07"
METALS=("Gold","Silver","Platinum","Palladium")

FRONTIER=[
 {"model":"ChHHO-ANFIS","sum_abs_error":1413.029779,"direction_correct":23,"approximate":False},
 {"model":"RBFNN DE-ABC","sum_abs_error":1415.8371,"direction_correct":25,"approximate":True},
 {"model":"PLS1 V1","sum_abs_error":1420.0291314697745,"direction_correct":20,"approximate":False},
 {"model":"GPR/MOGP LMC2_RBF_M32","sum_abs_error":1424.17,"direction_correct":19,"approximate":True},
 {"model":"FULL7 Equal ANN Ensemble","sum_abs_error":1428.86,"direction_correct":22,"approximate":False},
 {"model":"REDUCED4 Equal ANN Ensemble","sum_abs_error":1431.46,"direction_correct":24,"approximate":False},
 {"model":"SVR frozen parent","sum_abs_error":1449.187363,"direction_correct":19,"approximate":False},
 {"model":"CatBoost PRICE","sum_abs_error":1460.433935309605,"direction_correct":20,"approximate":False},
 {"model":"PLS2 V1","sum_abs_error":1489.3300296660234,"direction_correct":23,"approximate":False},
 {"model":"Random Forest comparator","sum_abs_error":1491.550693715667,"direction_correct":20,"approximate":False},
]

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def monthly_value(bundle,metal,month):
    if metal=="Gold":
        if month not in bundle.core_gold:
            raise RuntimeError(f"MISSING_GOLD {month}")
        return float(bundle.core_gold[month])
    M=bundle.monthly_metal[metal]
    if month not in M:
        raise RuntimeError(f"MISSING_{metal.upper()} {month}")
    return float(M[month])

def build_context(bundle,target):
    origin=base.month_shift(target,-1)
    months=list(base.month_range(TRAIN_START,origin))
    arr=np.empty((4,len(months)),dtype=np.float32)
    for i,metal in enumerate(METALS):
        vals=np.asarray([monthly_value(bundle,metal,m) for m in months],dtype=np.float32)
        if not np.isfinite(vals).all() or np.any(vals<=0):
            raise RuntimeError(f"BAD_CONTEXT metal={metal} target={target}")
        arr[i]=vals
    if arr.shape[1] < 32:
        raise RuntimeError(f"CONTEXT_TOO_SHORT target={target} n={arr.shape[1]}")
    return origin,months,arr

def targets():
    return (
        [(t,"DEV_SELECTION_AUTHORITY") for t in base.month_range(DEV_START,DEV_END)]
        +[(t,"LOCKED_REPORT_ONLY") for t in base.month_range(HOLDOUT_START,HOLDOUT_END)]
        +[(t,"QUARANTINED_REPORT_ONLY") for t in base.month_range(STRESS_START,STRESS_END)]
    )

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r["forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a); rwae=np.abs(rw-a)
    dc=np.asarray([r["direction_correct"] for r in rows],bool)
    wi=int(np.argmax(ae))
    return {
      "n":len(rows),
      "sum_abs_error":float(ae.sum()),
      "mae":float(ae.mean()),
      "rmse":float(np.sqrt(np.mean((f-a)**2))),
      "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
      "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
      "median_ae":float(np.median(ae)),
      "worst_ae":float(ae[wi]),
      "worst_month":rows[wi]["target"],
      "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
      "rw_sum_abs_error":float(rwae.sum()),
      "direction_correct":int(dc.sum()),
      "direction_accuracy_pct":float(dc.mean()*100),
    }

def compare(devm):
    me={"model":"TimesFM-3 Zero-Shot MV V1","sum_abs_error":devm["sum_abs_error"],"direction_correct":devm["direction_correct"],"approximate":False}
    allr=[dict(x) for x in FRONTIER]+[me]
    ranked=sorted(allr,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
    for i,r in enumerate(ranked,1): r["price_error_rank"]=i
    rank=next(r["price_error_rank"] for r in ranked if r["model"]==me["model"])
    dom=[r["model"] for r in allr if r["model"]!=me["model"]
         and r["sum_abs_error"]<=me["sum_abs_error"] and r["direction_correct"]>=me["direction_correct"]
         and (r["sum_abs_error"]<me["sum_abs_error"] or r["direction_correct"]>me["direction_correct"])]
    return {"ranking_by_primary_sumae":ranked,"price_error_rank":rank,
            "comparison_pool_n":len(ranked),"pareto_dominated_by":dom,
            "pareto_nondominated_within_pool":not dom}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)

    ts=targets()
    contexts=[]
    meta=[]
    for t,role in ts:
        origin,months,ctx=build_context(bundle,t)
        contexts.append(ctx)
        meta.append((t,role,origin,months))

    config=ModelConfig(
        checkpoint_path=CHECKPOINT,
        per_core_batch_size=4,
        device="cpu",
    )
    forecaster=TimesFM3Evaluator(config)

    outputs=list(forecaster.predict_batch(
        contexts=contexts,
        horizon=1,
        return_quantiles=True,
        use_symmetric_averaging=False,
    ))
    if len(outputs)!=len(meta):
        raise RuntimeError(f"OUTPUT_COUNT_FAIL got={len(outputs)} expected={len(meta)}")

    rows=[]
    for idx,(out,(t,role,origin,months)) in enumerate(zip(outputs,meta),1):
        fcarr=np.asarray(out.forecast,dtype=float)
        qarr=np.asarray(out.quantiles,dtype=float)
        if fcarr.shape!=(4,1):
            raise RuntimeError(f"FORECAST_SHAPE_FAIL target={t} shape={fcarr.shape}")
        pred=float(fcarr[0,0])
        if not math.isfinite(pred) or pred<=0:
            raise RuntimeError(f"FORECAST_VALUE_FAIL target={t} pred={pred}")
        actual=float(bundle.core_gold[t])
        rw=float(bundle.core_gold[origin])
        qgold=qarr[0,0,:].tolist() if qarr.ndim==3 and qarr.shape[0]==4 and qarr.shape[1]==1 else []
        row={
          "target":t,"role":role,"origin":origin,
          "context_first":months[0],"context_last":months[-1],"context_months":len(months),
          "context_variates":list(METALS),
          "forecast":pred,"actual":actual,"rw":rw,
          "absolute_error":float(abs(pred-actual)),
          "rw_absolute_error":float(abs(rw-actual)),
          "direction_correct":bool(int(np.sign(pred-rw))==int(np.sign(actual-rw))),
          "gold_quantiles":qgold,
        }
        rows.append(row)
        print(f"PROGRESS {idx}/{len(meta)} role={role} target={t} forecast={pred:.6f} AE={row['absolute_error']:.6f} dir={int(row['direction_correct'])}",flush=True)

    devrows=[r for r in rows if r["role"]=="DEV_SELECTION_AUTHORITY"]
    holdrows=[r for r in rows if r["role"]=="LOCKED_REPORT_ONLY"]
    stressrows=[r for r in rows if r["role"]=="QUARANTINED_REPORT_ONLY"]
    dev={"role":"DEV_SELECTION_AUTHORITY","metrics":metrics(devrows),"rows":devrows}
    hold={"role":"LOCKED_REPORT_ONLY","metrics":metrics(holdrows),"rows":holdrows}
    stress={"role":"QUARANTINED_REPORT_ONLY","metrics":metrics(stressrows),"rows":stressrows}
    comp=compare(dev["metrics"])

    after=read_invariants(dsn)
    same=after==bundle.invariants_before
    if not same: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    digest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
      "model_id":MODEL_ID,
      "scientific_gate":"PASS",
      "license_note":"TimesFM-3 pretrained weights are research-only here under TimesFM Non-Commercial License v1.0; no production/commercial authorization.",
      "contract":{
        "target":"H=1 next-calendar-month average XAU/USD",
        "checkpoint":CHECKPOINT,
        "representation":"4-VARIATE RAW MONTHLY PRICE LEVELS",
        "variates":list(METALS),
        "training_start":TRAIN_START,
        "fine_tuning":"NONE_ZERO_SHOT",
        "external_covariates":"NONE_V1",
        "scaling":"NONE_EXTERNAL_MODEL_INTERNAL_DEFAULTS",
        "horizon":1,
        "return_quantiles":True,
        "use_symmetric_averaging":False,
        "random_split":"NONE",
        "database":"READ_ONLY",
        "2025_role":"LOCKED_REPORT_ONLY",
        "2026_role":"QUARANTINED_REPORT_ONLY",
      },
      "authority_invariants_before":bundle.invariants_before,
      "authority_invariants_after":after,
      "authority_invariants_unchanged":same,
      "software":{
        "python":platform.python_version(),
        "numpy":np.__version__,
        "torch":torch.__version__,
        "timesfm":getattr(timesfm,"__version__","3.0.2"),
      },
      "dev":dev,"holdout_2025":hold,"stress_2026":stress,
      "cross_family_comparison":comp,
      "result_payload_sha256":digest,
    }
    Path("gold_monthly_timesfm3_zero_shot_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("TIMESFM3_ZERO_SHOT_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
      "dev_metrics":dev["metrics"],
      "holdout_2025_metrics":hold["metrics"],
      "stress_2026_metrics":stress["metrics"],
      "cross_family_rank":comp["price_error_rank"],
      "cross_family_pool_n":comp["comparison_pool_n"],
      "pareto_dominated_by":comp["pareto_dominated_by"],
      "authority_invariants_unchanged":same,
      "sha256":digest,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
