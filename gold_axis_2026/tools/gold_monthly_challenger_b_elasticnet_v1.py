#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, math, os, platform
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg
import sklearn
from sklearn.linear_model import ElasticNet
from sklearn.preprocessing import StandardScaler

import vw_midas_msvr_successor_v1 as base

MODEL_ID = "GOLD_MONTHLY_CHALLENGER_B_ELASTICNET_V1"
FREEZE_FILE = "GOLD_MONTHLY_CHALLENGER_B_ELASTICNET_FREEZE_2026-09-28.md"

TRAIN_START = "2010-05"
INNER_VAL_MONTHS = 12
MIN_INNER_TRAIN = 36
ALPHAS = (0.0001, 0.001, 0.01, 0.1, 1.0)
L1_RATIOS = (0.10, 0.25, 0.50, 0.75, 0.90, 0.95)

DEV_START, DEV_END = "2022-04", "2024-12"
HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

FEATURE_NAMES = (
    "Gold_MR","Gold_VW","Silver_MR","Silver_VW",
    "Platinum_MR","Platinum_VW","Palladium_MR","Palladium_VW",
)

def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def current8_x_only(bundle, target, gpr_history):
    p, pp = base.month_shift(target,-1), base.month_shift(target,-2)
    z = base.gpr_norm(gpr_history, pp)
    x=[]
    for metal in base.METALS:
        M=bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"MONTHLY_METAL_FEATURE_MISSING metal={metal} target={target}")
        x.extend((math.log(float(M[p])/float(M[pp])),
                  base.weighted_daily_return(bundle,metal,p,z)))
    out=np.asarray(x,float)
    if out.shape!=(8,) or not np.isfinite(out).all():
        raise RuntimeError(f"CURRENT8_FEATURE_GATE_FAIL target={target}")
    return out

def build_origin_data(bundle,target):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_ORIGIN_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin]
    samples={}
    for t in base.month_range(TRAIN_START,origin):
        try:
            samples[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError:
            continue
    keys=sorted(k for k in samples if TRAIN_START<=k<=origin)
    if len(keys)<INNER_VAL_MONTHS+MIN_INNER_TRAIN:
        raise RuntimeError(f"TRAIN_HISTORY_TOO_SMALL target={target} n={len(keys)}")
    split=len(keys)-INNER_VAL_MONTHS
    tr,va=keys[:split],keys[split:]
    Xtr=np.stack([samples[k][0] for k in tr]); ytr=np.asarray([samples[k][1][0] for k in tr],float)
    Xv=np.stack([samples[k][0] for k in va])
    prev_v=np.asarray([bundle.core_gold[base.month_shift(k,-1)] for k in va],float)
    actual_v=np.asarray([bundle.core_gold[k] for k in va],float)
    Xall=np.stack([samples[k][0] for k in keys]); yall=np.asarray([samples[k][1][0] for k in keys],float)
    xt=current8_x_only(bundle,target,gh).reshape(1,-1)
    for n,a in {"Xtr":Xtr,"ytr":ytr,"Xv":Xv,"prev_v":prev_v,"actual_v":actual_v,"Xall":Xall,"yall":yall,"xt":xt}.items():
        if not np.isfinite(a).all(): raise RuntimeError(f"NONFINITE_DATA target={target} field={n}")
    return {
        "origin":origin,"keys":keys,"inner_train_keys":tr,"inner_val_keys":va,
        "Xtr":Xtr,"ytr":ytr,"Xv":Xv,"prev_v":prev_v,"actual_v":actual_v,
        "inner_rw_sum_ae":float(np.abs(prev_v-actual_v).sum()),
        "Xall":Xall,"yall":yall,"xt":xt,"anchor_prev":float(bundle.core_gold[origin]),
    }

def fit_model(X,y,alpha,l1_ratio):
    scaler=StandardScaler()
    Xs=scaler.fit_transform(X)
    model=ElasticNet(
        alpha=float(alpha), l1_ratio=float(l1_ratio), fit_intercept=True,
        max_iter=200000, tol=1e-10, selection="cyclic"
    )
    model.fit(Xs,y)
    return scaler,model

def predict_return(X,y,Xtest,alpha,l1_ratio):
    scaler,model=fit_model(X,y,alpha,l1_ratio)
    pred=np.asarray(model.predict(scaler.transform(Xtest)),float).reshape(-1)
    if not np.isfinite(pred).all() or np.any(np.abs(pred)>=1.0):
        raise RuntimeError(f"PATHOLOGICAL_ELASTICNET_PRED alpha={alpha} l1={l1_ratio}")
    return pred,model

def choose_params(data):
    denom=max(data["inner_rw_sum_ae"],1e-12)
    scored=[]
    for alpha in ALPHAS:
        for l1 in L1_RATIOS:
            pred,_=predict_return(data["Xtr"],data["ytr"],data["Xv"],alpha,l1)
            fc=data["prev_v"]*np.exp(pred)
            sae=float(np.abs(fc-data["actual_v"]).sum())
            scored.append({
                "alpha":float(alpha),"l1_ratio":float(l1),
                "inner_sum_abs_error":sae,
                "inner_relative_sum_abs_error_vs_rw":float(sae/denom),
            })
    scored.sort(key=lambda r:(r["inner_relative_sum_abs_error_vs_rw"],r["alpha"],r["l1_ratio"]))
    b=scored[0]
    return float(b["alpha"]),float(b["l1_ratio"]),scored

def forecast_one(bundle,target):
    d=build_origin_data(bundle,target)
    alpha,l1,scores=choose_params(d)
    scaler,model=fit_model(d["Xall"],d["yall"],alpha,l1)
    pred=float(np.asarray(model.predict(scaler.transform(d["xt"]))).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0: raise RuntimeError("PATHOLOGICAL_OUTER_PRED")
    fc=float(d["anchor_prev"]*math.exp(pred))
    if target not in bundle.core_gold: raise RuntimeError(f"SCORING_ACTUAL_MISSING {target}")
    actual=float(bundle.core_gold[target]); rw=float(d["anchor_prev"])
    coef=np.asarray(model.coef_,float).reshape(-1)
    near_zero=np.abs(coef)<1e-10
    return {
        "target":target,"origin":d["origin"],"representation":"CURRENT8","feature_dim":8,
        "train_first":d["keys"][0],"train_last":d["keys"][-1],"train_rows":len(d["keys"]),
        "inner_train_n":len(d["inner_train_keys"]),"inner_val_n":len(d["inner_val_keys"]),
        "inner_val_first":d["inner_val_keys"][0],"inner_val_last":d["inner_val_keys"][-1],
        "selected_alpha":alpha,"selected_l1_ratio":l1,"param_scores":scores,
        "pred_log_return_gold":pred,"forecast":fc,"actual":actual,"rw":rw,
        "absolute_error":float(abs(fc-actual)),"rw_absolute_error":float(abs(rw-actual)),
        "direction_correct":bool(int(np.sign(fc-rw))==int(np.sign(actual-rw))),
        "coefficients_standardized_X":{FEATURE_NAMES[i]:float(coef[i]) for i in range(8)},
        "zero_coefficient_count":int(near_zero.sum()),
        "nonzero_feature_names":[FEATURE_NAMES[i] for i in range(8) if not near_zero[i]],
    }

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows],float); f=np.asarray([r["forecast"] for r in rows],float); rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a); rwae=np.abs(rw-a); dc=np.asarray([r["direction_correct"] for r in rows],bool); wi=int(np.argmax(ae))
    return {
        "n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),
        "rmse":float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
        "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
        "median_ae":float(np.median(ae)),"worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
        "rw_sum_abs_error":float(rwae.sum()),"direction_correct":int(dc.sum()),
        "direction_accuracy_pct":float(dc.mean()*100),
        "mean_zero_coefficients":float(np.mean([r["zero_coefficient_count"] for r in rows])),
    }

def yearly(rows):
    return {y:metrics([r for r in rows if r["target"].startswith(y)]) for y in sorted({r["target"][:4] for r in rows})}

def run_period(bundle,start,end,label):
    rows=[]
    targets=list(base.month_range(start,end))
    for i,t in enumerate(targets,1):
        r=forecast_one(bundle,t); rows.append(r)
        print(f"PROGRESS period={label} target={i}/{len(targets)} month={t} alpha={r['selected_alpha']:.4g} l1={r['selected_l1_ratio']:.2f} AE={r['absolute_error']:.6f} dir={int(r['direction_correct'])} zeros={r['zero_coefficient_count']}",flush=True)
    return {
        "role":label,"metrics":metrics(rows),"yearly":yearly(rows),
        "selected_alpha_counts":dict(sorted(Counter(str(r["selected_alpha"]) for r in rows).items())),
        "selected_l1_ratio_counts":dict(sorted(Counter(str(r["selected_l1_ratio"]) for r in rows).items())),
        "zero_coefficient_count_distribution":dict(sorted(Counter(str(r["zero_coefficient_count"]) for r in rows).items())),
        "rows":rows,
    }

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    b0={
        "source_checks":bundle.source_checks,
        "current8_feature_contract":{
            "metals":list(base.METALS),"features":list(FEATURE_NAMES),"feature_dim":8,
            "gpr_source":base.GPR_PIT,"outer_feature_builder":"X_ONLY_NO_TARGET_MONTH_METAL_DEREFERENCE",
        },
        "gate_pass":not bundle.source_checks["missing_required_gpr_origins"] and not bundle.source_checks["late_required_gpr_origins"] and not bundle.source_checks["missing_required_gpr_lag_month"],
    }
    if not b0["gate_pass"]: raise RuntimeError(f"B0_SOURCE_GATE_FAIL {b0}")

    dev=run_period(bundle,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY")
    if dev["metrics"]["n"]!=33: raise RuntimeError("DEV_N_FAIL")
    hold=run_period(bundle,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY")
    stress=run_period(bundle,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")

    after=read_invariants(dsn); same=after==bundle.invariants_before
    if not same: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    digest=hashlib.sha256(json.dumps({"dev":dev["rows"],"hold":hold["rows"],"stress":stress["rows"]},sort_keys=True,separators=(",",":")).encode()).hexdigest()

    out={
        "model_id":MODEL_ID,"freeze_file":FREEZE_FILE,"scientific_gate":"PASS",
        "contract":{
            "target":"H=1 next-calendar-month average XAU/USD","training_target":"Gold next-month log return",
            "representation":"CURRENT8","training_start":TRAIN_START,"inner_validation_months":INNER_VAL_MONTHS,
            "alpha_grid":list(ALPHAS),"l1_ratio_grid":list(L1_RATIOS),
            "parameter_selection":"per-origin last-12 pre-target months; min relative cumulative price AE vs RW",
            "tie_break":"lower objective, lower alpha, lower l1_ratio",
            "scaling":"StandardScaler fit on training fold only","estimator":"sklearn.linear_model.ElasticNet",
            "max_iter":200000,"tol":1e-10,"selection":"cyclic","random_split":"NONE","database":"READ_ONLY",
            "primary_metric":"DEV_PRICE_SUM_ABS_ERROR","2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY",
            "metal_ablation":"NOT_IN_V1","outer_target_metal_feature_access":"NONE",
        },
        "b0_audit":b0,"authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,
        "authority_invariants_unchanged":same,
        "software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},
        "dev":dev,"holdout_2025":hold,"stress_2026":stress,"result_payload_sha256":digest,
        "context_only_comparators":{
            "catboost_price_dev_sumae":1460.433935309605,"catboost_price_dev_direction_correct":20,
            "catboost_balanced_dev_sumae":1481.261937710369,"catboost_balanced_dev_direction_correct":22,
            "random_forest_dev_sumae":1491.550693715667,"random_forest_dev_direction_correct":20,
            "ridge_v1_dev_sumae":1520.9926031249222,"ridge_v1_dev_direction_correct":21,
            "note":"Existing frozen results only; not used to tune Elastic Net."
        }
    }
    Path("gold_monthly_challenger_b_elasticnet_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("ELASTICNET_CHALLENGER_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "b0_gate_pass":b0["gate_pass"],"dev_metrics":dev["metrics"],
        "dev_alpha_counts":dev["selected_alpha_counts"],"dev_l1_counts":dev["selected_l1_ratio_counts"],
        "dev_zero_coef_dist":dev["zero_coefficient_count_distribution"],
        "holdout_2025_metrics":hold["metrics"],"stress_2026_metrics":stress["metrics"],
        "authority_invariants_unchanged":same,"result_payload_sha256":digest
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
