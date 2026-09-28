#!/usr/bin/env python3
from __future__ import annotations

import gc
import hashlib
import json
import math
import os
import platform
from pathlib import Path

import numpy as np
import psycopg
import torch

from pypots.forecasting import TimeMixerPP
from pypots.utils.random import set_random_seed

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "GOLD_MONTHLY_TIMEMIXERPP_V1"
PY_POTS_COMMIT = "53b3eac34be9491ac3f28e65ee1993436e9318af"
TRAIN_START = "2010-05"
LOOKBACK = 48
VAL_MONTHS = 12
SEED = 20260928

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
 {"model":"TimesFM-3 Zero-Shot MV V1","sum_abs_error":1850.4112841796875,"direction_correct":19,"approximate":False},
]

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def value(bundle,metal,month):
    if metal=="Gold":
        if month not in bundle.core_gold: raise RuntimeError(f"MISSING_GOLD {month}")
        return float(bundle.core_gold[month])
    M=bundle.monthly_metal[metal]
    if month not in M: raise RuntimeError(f"MISSING_{metal.upper()} {month}")
    return float(M[month])

def matrix_through(bundle,origin):
    months=list(base.month_range(TRAIN_START,origin))
    X=np.asarray([[value(bundle,m,k) for m in METALS] for k in months],dtype=np.float32)
    if X.ndim!=2 or X.shape[1]!=4 or not np.isfinite(X).all() or np.any(X<=0):
        raise RuntimeError(f"SERIES_GATE_FAIL origin={origin} shape={X.shape}")
    return months,X

def make_windows(months,X,target_indices):
    xs=[]; ys=[]; target_months=[]
    for ti in target_indices:
        if ti < LOOKBACK: continue
        xs.append(X[ti-LOOKBACK:ti])
        ys.append(X[ti:ti+1])
        target_months.append(months[ti])
    if not xs:
        raise RuntimeError("EMPTY_WINDOWS")
    return np.stack(xs).astype(np.float32),np.stack(ys).astype(np.float32),target_months

def build_origin_data(bundle,target):
    origin=base.month_shift(target,-1)
    months,X=matrix_through(bundle,origin)
    n=len(months)
    if n < LOOKBACK + VAL_MONTHS + 12:
        raise RuntimeError(f"HISTORY_TOO_SHORT target={target} n={n}")
    val_start_idx=n-VAL_MONTHS
    train_target_idx=range(LOOKBACK,val_start_idx)
    val_target_idx=range(val_start_idx,n)
    Xtr,Ytr,trm=make_windows(months,X,train_target_idx)
    Xv,Yv,vam=make_windows(months,X,val_target_idx)
    Xtest=X[-LOOKBACK:][None,:,:].astype(np.float32)
    if Xv.shape[0]!=VAL_MONTHS:
        raise RuntimeError(f"VAL_COUNT_FAIL target={target} n={Xv.shape[0]}")
    return {
      "origin":origin,"months":months,
      "Xtr":Xtr,"Ytr":Ytr,"Xv":Xv,"Yv":Yv,"Xtest":Xtest,
      "train_target_first":trm[0],"train_target_last":trm[-1],
      "val_target_first":vam[0],"val_target_last":vam[-1],
    }

def fit_predict(bundle,target):
    d=build_origin_data(bundle,target)
    set_random_seed(SEED)
    torch.manual_seed(SEED)
    torch.set_num_threads(1)

    model=TimeMixerPP(
      n_steps=LOOKBACK,
      n_features=4,
      n_pred_steps=1,
      n_pred_features=4,
      term="short",
      n_layers=2,
      top_k=5,
      d_model=32,
      d_ffn=32,
      n_heads=1,
      n_kernels=3,
      downsampling_window=2,
      downsampling_layers=1,
      channel_mixing=True,
      channel_independence=True,
      use_norm=True,
      dropout=0.1,
      batch_size=32,
      epochs=40,
      patience=6,
      num_workers=0,
      device="cpu",
      saving_path=None,
      model_saving_strategy=None,
      verbose=False,
    )
    train_set={"X":d["Xtr"],"X_pred":d["Ytr"]}
    val_set={"X":d["Xv"],"X_pred":d["Yv"]}
    model.fit(train_set,val_set)
    pred=np.asarray(model.predict({"X":d["Xtest"]})["forecasting"],dtype=float)
    if pred.shape!=(1,1,4):
        raise RuntimeError(f"PRED_SHAPE_FAIL target={target} shape={pred.shape}")
    gold_fc=float(pred[0,0,0])
    if not math.isfinite(gold_fc) or gold_fc<=0:
        raise RuntimeError(f"PRED_VALUE_FAIL target={target} pred={gold_fc}")

    actual=float(bundle.core_gold[target])
    rw=float(bundle.core_gold[d["origin"]])
    row={
      "target":target,"origin":d["origin"],
      "lookback_months":LOOKBACK,
      "train_samples":int(d["Xtr"].shape[0]),
      "validation_samples":int(d["Xv"].shape[0]),
      "train_target_first":d["train_target_first"],
      "train_target_last":d["train_target_last"],
      "validation_target_first":d["val_target_first"],
      "validation_target_last":d["val_target_last"],
      "forecast":gold_fc,"actual":actual,"rw":rw,
      "absolute_error":float(abs(gold_fc-actual)),
      "rw_absolute_error":float(abs(rw-actual)),
      "direction_correct":bool(int(np.sign(gold_fc-rw))==int(np.sign(actual-rw))),
      "all_metal_forecast":{METALS[i]:float(pred[0,0,i]) for i in range(4)},
    }
    del model
    gc.collect()
    return row

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows],float)
    f=np.asarray([r["forecast"] for r in rows],float)
    rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a); rwae=np.abs(rw-a)
    dc=np.asarray([r["direction_correct"] for r in rows],bool)
    wi=int(np.argmax(ae))
    return {
      "n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),
      "rmse":float(np.sqrt(np.mean((f-a)**2))),
      "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
      "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
      "median_ae":float(np.median(ae)),"worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
      "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
      "rw_sum_abs_error":float(rwae.sum()),
      "direction_correct":int(dc.sum()),"direction_accuracy_pct":float(dc.mean()*100),
    }

def run_period(bundle,start,end,label):
    rows=[]; ts=list(base.month_range(start,end))
    for i,t in enumerate(ts,1):
        r=fit_predict(bundle,t); rows.append(r)
        print(f"PROGRESS {label} {i}/{len(ts)} target={t} AE={r['absolute_error']:.6f} dir={int(r['direction_correct'])} train_n={r['train_samples']}",flush=True)
    return {"role":label,"metrics":metrics(rows),"rows":rows}

def compare(devm):
    me={"model":"TimeMixer++ V1","sum_abs_error":devm["sum_abs_error"],"direction_correct":devm["direction_correct"],"approximate":False}
    allr=[dict(x) for x in FRONTIER]+[me]
    ranked=sorted(allr,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
    for i,r in enumerate(ranked,1): r["price_error_rank"]=i
    rank=next(r["price_error_rank"] for r in ranked if r["model"]==me["model"])
    dom=[r["model"] for r in allr if r["model"]!=me["model"] and
         r["sum_abs_error"]<=me["sum_abs_error"] and r["direction_correct"]>=me["direction_correct"] and
         (r["sum_abs_error"]<me["sum_abs_error"] or r["direction_correct"]>me["direction_correct"])]
    return {"ranking_by_primary_sumae":ranked,"price_error_rank":rank,"comparison_pool_n":len(ranked),
            "pareto_dominated_by":dom,"pareto_nondominated_within_pool":not dom}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)

    dev=run_period(bundle,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY")
    hold=run_period(bundle,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY")
    stress=run_period(bundle,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")

    after=read_invariants(dsn)
    same=after==bundle.invariants_before
    if not same: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    comp=compare(dev["metrics"])

    payload={"dev":dev["rows"],"hold":hold["rows"],"stress":stress["rows"]}
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
      "model_id":MODEL_ID,"scientific_gate":"PASS",
      "provenance":{"implementation":"PyPOTS TimeMixerPP","pypots_commit":PY_POTS_COMMIT},
      "contract":{
        "target":"H=1 next-calendar-month average XAU/USD",
        "representation":"4-VARIATE RAW MONTHLY PRICE LEVELS",
        "variates":list(METALS),
        "lookback_months":LOOKBACK,
        "horizon":1,
        "validation":"latest 12 matured pre-target target months",
        "epochs_max":40,"patience":6,"seed":SEED,
        "architecture":{"term":"short","n_layers":2,"top_k":5,"d_model":32,"d_ffn":32,"n_heads":1,"n_kernels":3,
                        "downsampling_window":2,"downsampling_layers":1,"channel_mixing":True,
                        "channel_independence":True,"use_norm":True,"dropout":0.1},
        "scaling":"NO_EXTERNAL_SCALER; TIMEMIXERPP use_norm=True",
        "random_split":"NONE","database":"READ_ONLY",
        "2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY",
      },
      "authority_invariants_before":bundle.invariants_before,
      "authority_invariants_after":after,
      "authority_invariants_unchanged":same,
      "software":{"python":platform.python_version(),"numpy":np.__version__,"torch":torch.__version__},
      "dev":dev,"holdout_2025":hold,"stress_2026":stress,
      "cross_family_comparison":comp,"result_payload_sha256":digest,
    }
    Path("gold_monthly_timemixerpp_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("TIMEMIXERPP_V1_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
      "dev_metrics":dev["metrics"],"holdout_2025_metrics":hold["metrics"],"stress_2026_metrics":stress["metrics"],
      "cross_family_rank":comp["price_error_rank"],"cross_family_pool_n":comp["comparison_pool_n"],
      "pareto_dominated_by":comp["pareto_dominated_by"],"authority_invariants_unchanged":same,"sha256":digest,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
