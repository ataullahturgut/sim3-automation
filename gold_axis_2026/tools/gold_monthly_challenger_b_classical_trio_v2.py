#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import warnings
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import sklearn
import statsmodels
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "GOLD_MONTHLY_CHALLENGER_B_CLASSICAL_TRIO_V2"
FREEZE_FILE = "GOLD_MONTHLY_CHALLENGER_B_CLASSICAL_TRIO_FREEZE_2026-09-28.md"

TRAIN_START = "2010-05"
INNER_VAL_MONTHS = 12
DEV_START, DEV_END = "2022-04", "2024-12"
HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

ARIMA_CANDIDATES = (
    {"id":"ARIMA_A","order":(1,0,0),"trend":"c"},
    {"id":"ARIMA_B","order":(1,1,1),"trend":"t"},
    {"id":"ARIMA_C","order":(0,1,1),"trend":"t"},
)
SARIMA_CANDIDATES = (
    {"id":"SARIMA_A","order":(1,0,0),"seasonal_order":(1,0,0,12),"trend":"n"},
    {"id":"SARIMA_B","order":(0,1,1),"seasonal_order":(0,1,1,12),"trend":"n"},
)
PROPHET_CANDIDATES = (
    {"id":"PROPHET_A","changepoint_prior_scale":0.01,"seasonality_prior_scale":1.0,"seasonality_mode":"additive"},
    {"id":"PROPHET_B","changepoint_prior_scale":0.1,"seasonality_prior_scale":1.0,"seasonality_mode":"multiplicative"},
)

def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def month_dt(m):
    return pd.Period(m, freq="M").to_timestamp(how="start")

def gold_series(bundle, through_month):
    keys = [k for k in sorted(bundle.core_gold) if TRAIN_START <= k <= through_month]
    vals = np.asarray([float(bundle.core_gold[k]) for k in keys], dtype=float)
    if len(keys) < 36 or not np.isfinite(vals).all() or np.any(vals <= 0):
        raise RuntimeError(f"GOLD_SERIES_GATE_FAIL through={through_month} n={len(keys)}")
    return keys, vals

def arima_forecast(y, steps, c):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = ARIMA(
            y,
            order=tuple(c["order"]),
            trend=c["trend"],
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit()
        pred = np.asarray(fit.forecast(steps=steps), dtype=float).reshape(-1)
    return pred

def sarima_forecast(y, steps, c):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fit = SARIMAX(
            y,
            order=tuple(c["order"]),
            seasonal_order=tuple(c["seasonal_order"]),
            trend=c["trend"],
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)
        pred = np.asarray(fit.forecast(steps=steps), dtype=float).reshape(-1)
    return pred

def prophet_forecast(keys, y, future_keys, c):
    df = pd.DataFrame({"ds":[month_dt(k) for k in keys], "y":np.asarray(y,dtype=float)})
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = Prophet(
            changepoint_prior_scale=float(c["changepoint_prior_scale"]),
            seasonality_prior_scale=float(c["seasonality_prior_scale"]),
            seasonality_mode=c["seasonality_mode"],
            yearly_seasonality="auto",
            weekly_seasonality="auto",
            daily_seasonality="auto",
            uncertainty_samples=0,
        )
        m.fit(df)
        future = pd.DataFrame({"ds":[month_dt(k) for k in future_keys]})
        fc = m.predict(future)
    pred = np.asarray(fc["yhat"], dtype=float).reshape(-1)
    return pred

def candidate_inner_score(bundle, target, family, c):
    origin = base.month_shift(target, -1)
    val_end = origin
    val_start = base.month_shift(val_end, -(INNER_VAL_MONTHS-1))
    train_end = base.month_shift(val_start, -1)

    train_keys, y = gold_series(bundle, train_end)
    val_keys = list(base.month_range(val_start, val_end))
    actual = np.asarray([float(bundle.core_gold[k]) for k in val_keys], dtype=float)

    try:
        if family == "ARIMA":
            pred = arima_forecast(y, INNER_VAL_MONTHS, c)
        elif family == "SARIMA":
            pred = sarima_forecast(y, INNER_VAL_MONTHS, c)
        elif family == "PROPHET":
            pred = prophet_forecast(train_keys, y, val_keys, c)
        else:
            raise RuntimeError(f"UNKNOWN_FAMILY {family}")
        if pred.shape != (INNER_VAL_MONTHS,) or not np.isfinite(pred).all():
            raise RuntimeError("INNER_PRED_NONFINITE_OR_SHAPE")
        sae = float(np.abs(pred-actual).sum())
        rw = np.asarray([float(bundle.core_gold[base.month_shift(k,-1)]) for k in val_keys], dtype=float)
        rw_sae = float(np.abs(rw-actual).sum())
        rel = float(sae/max(rw_sae,1e-12))
        return {
            "candidate_id":c["id"],
            "params":c,
            "inner_train_first":train_keys[0],
            "inner_train_last":train_keys[-1],
            "inner_val_first":val_keys[0],
            "inner_val_last":val_keys[-1],
            "inner_sum_abs_error":sae,
            "inner_rw_sum_abs_error":rw_sae,
            "inner_relative_sum_abs_error_vs_rw":rel,
            "status":"OK",
        }
    except Exception as e:
        return {
            "candidate_id":c["id"],
            "params":c,
            "inner_train_first":train_keys[0],
            "inner_train_last":train_keys[-1],
            "inner_val_first":val_keys[0],
            "inner_val_last":val_keys[-1],
            "inner_sum_abs_error":float("inf"),
            "inner_rw_sum_abs_error":float(np.abs(
                np.asarray([float(bundle.core_gold[base.month_shift(k,-1)]) for k in val_keys])-actual
            ).sum()),
            "inner_relative_sum_abs_error_vs_rw":float("inf"),
            "status":"FAILED",
            "error":repr(e),
        }

def candidates_for(family):
    if family=="ARIMA": return ARIMA_CANDIDATES
    if family=="SARIMA": return SARIMA_CANDIDATES
    if family=="PROPHET": return PROPHET_CANDIDATES
    raise RuntimeError(f"UNKNOWN_FAMILY {family}")

def choose_candidate(bundle,target,family):
    scored=[]
    for idx,c in enumerate(candidates_for(family)):
        r=candidate_inner_score(bundle,target,family,c)
        r["candidate_order"]=idx
        scored.append(r)
    valid=[r for r in scored if r["status"]=="OK" and math.isfinite(r["inner_sum_abs_error"])]
    if not valid:
        raise RuntimeError(f"ALL_CANDIDATES_FAILED family={family} target={target} scored={scored}")
    valid.sort(key=lambda r:(r["inner_sum_abs_error"],r["candidate_order"]))
    best=valid[0]
    c=next(x for x in candidates_for(family) if x["id"]==best["candidate_id"])
    return c,scored

def outer_forecast(bundle,target,family,c):
    origin=base.month_shift(target,-1)
    keys,y=gold_series(bundle,origin)
    if family=="ARIMA":
        pred=float(arima_forecast(y,1,c)[0])
    elif family=="SARIMA":
        pred=float(sarima_forecast(y,1,c)[0])
    elif family=="PROPHET":
        pred=float(prophet_forecast(keys,y,[target],c)[0])
    else:
        raise RuntimeError(f"UNKNOWN_FAMILY {family}")
    if not math.isfinite(pred) or pred<=0:
        raise RuntimeError(f"OUTER_PRED_FAIL family={family} target={target} pred={pred}")
    return pred,keys

def forecast_one(bundle,target,family):
    c,scores=choose_candidate(bundle,target,family)
    pred,keys=outer_forecast(bundle,target,family,c)
    actual=float(bundle.core_gold[target])
    rw=float(bundle.core_gold[base.month_shift(target,-1)])
    return {
        "family":family,"target":target,"origin":base.month_shift(target,-1),
        "input_type":"RAW_MONTHLY_GOLD_AVERAGE_LEVEL",
        "train_first":keys[0],"train_last":keys[-1],"train_rows":len(keys),
        "selected_candidate":c["id"],"selected_params":c,"candidate_scores":scores,
        "forecast":pred,"actual":actual,"rw":rw,
        "absolute_error":float(abs(pred-actual)),
        "rw_absolute_error":float(abs(rw-actual)),
        "direction_correct":bool(int(np.sign(pred-rw))==int(np.sign(actual-rw))),
    }

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
        "median_ae":float(np.median(ae)),
        "worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
        "rw_sum_abs_error":float(rwae.sum()),
        "direction_correct":int(dc.sum()),
        "direction_accuracy_pct":float(dc.mean()*100),
    }

def yearly(rows):
    return {y:metrics([r for r in rows if r["target"].startswith(y)])
            for y in sorted({r["target"][:4] for r in rows})}

def run_period(bundle,family,start,end,label):
    rows=[]; ts=list(base.month_range(start,end))
    for i,t in enumerate(ts,1):
        r=forecast_one(bundle,t,family); rows.append(r)
        print(
            f"PROGRESS family={family} period={label} {i}/{len(ts)} target={t} "
            f"candidate={r['selected_candidate']} AE={r['absolute_error']:.6f} "
            f"dir={int(r['direction_correct'])}",
            flush=True
        )
    return {
        "role":label,
        "metrics":metrics(rows),
        "yearly":yearly(rows),
        "selected_candidate_counts":dict(sorted(Counter(r["selected_candidate"] for r in rows).items())),
        "rows":rows,
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    before=bundle.invariants_before

    models={}
    for family in ("ARIMA","SARIMA","PROPHET"):
        print(f"FAMILY_START {family}",flush=True)
        dev=run_period(bundle,family,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY")
        hold=run_period(bundle,family,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY")
        stress=run_period(bundle,family,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")
        models[family]={
            "dev":dev,"holdout_2025":hold,"stress_2026":stress,
            "candidate_grid":list(candidates_for(family)),
        }

    after=read_invariants(dsn)
    same=after==before
    if not same: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    digest=hashlib.sha256(json.dumps(models,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
        "model_id":MODEL_ID,
        "freeze_file":FREEZE_FILE,
        "scientific_gate":"PASS",
        "contract":{
            "target":"H=1 next-calendar-month average XAU/USD",
            "input":"authoritative completed monthly Gold average price level",
            "representation":"UNIVARIATE_RAW_MONTHLY_LEVEL",
            "training_start":TRAIN_START,
            "inner_validation_months":INNER_VAL_MONTHS,
            "inner_design":"fit through month before 12-month validation block; forecast full 12-month block; select by cumulative AE",
            "outer_design":"refit selected candidate through current origin; one-step H=1 forecast",
            "scaling":"NONE",
            "random_split":"NONE",
            "database":"READ_ONLY",
            "2025_role":"LOCKED_REPORT_ONLY",
            "2026_role":"QUARANTINED_REPORT_ONLY",
        },
        "authority_invariants_before":before,
        "authority_invariants_after":after,
        "authority_invariants_unchanged":same,
        "software":{
            "python":platform.python_version(),
            "numpy":np.__version__,
            "pandas":pd.__version__,
            "scikit_learn":sklearn.__version__,
            "statsmodels":statsmodels.__version__,
        },
        "models":models,
        "result_payload_sha256":digest,
    }

    Path("gold_monthly_challenger_b_classical_trio_v2_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("CLASSICAL_TRIO_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "ARIMA_DEV":models["ARIMA"]["dev"]["metrics"],
        "SARIMA_DEV":models["SARIMA"]["dev"]["metrics"],
        "PROPHET_DEV":models["PROPHET"]["dev"]["metrics"],
        "ARIMA_COUNTS":models["ARIMA"]["dev"]["selected_candidate_counts"],
        "SARIMA_COUNTS":models["SARIMA"]["dev"]["selected_candidate_counts"],
        "PROPHET_COUNTS":models["PROPHET"]["dev"]["selected_candidate_counts"],
        "ARIMA_2025":models["ARIMA"]["holdout_2025"]["metrics"],
        "SARIMA_2025":models["SARIMA"]["holdout_2025"]["metrics"],
        "PROPHET_2025":models["PROPHET"]["holdout_2025"]["metrics"],
        "ARIMA_2026":models["ARIMA"]["stress_2026"]["metrics"],
        "SARIMA_2026":models["SARIMA"]["stress_2026"]["metrics"],
        "PROPHET_2026":models["PROPHET"]["stress_2026"]["metrics"],
        "authority_invariants_unchanged":same,
        "sha256":digest,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
