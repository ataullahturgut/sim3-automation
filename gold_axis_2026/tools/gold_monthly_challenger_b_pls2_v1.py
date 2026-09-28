#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, math, os, platform, warnings
from collections import Counter
from pathlib import Path

import numpy as np
import psycopg
import sklearn
from sklearn.cross_decomposition import PLSRegression

import vw_midas_msvr_successor_v1 as base

MODEL_ID="GOLD_MONTHLY_CHALLENGER_B_PLS2_V1"
FREEZE_FILE="GOLD_MONTHLY_CHALLENGER_B_PLS2_FREEZE_2026-09-28.md"
TRAIN_START="2010-05"; INNER_VAL_MONTHS=12; MIN_INNER_TRAIN=36
COMPONENTS=tuple(range(1,9))
DEV_START,DEV_END="2022-04","2024-12"
HOLDOUT_START,HOLDOUT_END="2025-01","2025-12"
STRESS_START,STRESS_END="2026-01","2026-07"
METAL_NAMES=("Gold","Silver","Platinum","Palladium")

FRONTIER=[
 {"model":"ChHHO-ANFIS","family":"ANFIS","sum_abs_error":1413.029779,"direction_correct":23,"approximate":False},
 {"model":"RBFNN DE-ABC","family":"RBFNN","sum_abs_error":1415.8371,"direction_correct":25,"approximate":True},
 {"model":"PLS1 V1","family":"Challenger-B","sum_abs_error":1420.0291314697745,"direction_correct":20,"approximate":False},
 {"model":"GPR/MOGP LMC2_RBF_M32","family":"GPR/MOGP","sum_abs_error":1424.17,"direction_correct":19,"approximate":True},
 {"model":"FULL7 Equal ANN Ensemble","family":"ANN","sum_abs_error":1428.86,"direction_correct":22,"approximate":False},
 {"model":"REDUCED4 Equal ANN Ensemble","family":"ANN","sum_abs_error":1431.46,"direction_correct":24,"approximate":False},
 {"model":"SVR frozen parent","family":"SVR","sum_abs_error":1449.187363,"direction_correct":19,"approximate":False},
 {"model":"CatBoost PRICE","family":"Boosting","sum_abs_error":1460.433935309605,"direction_correct":20,"approximate":False},
 {"model":"Random Forest comparator","family":"RF","sum_abs_error":1491.550693715667,"direction_correct":20,"approximate":False},
 {"model":"Ridge V1","family":"Challenger-B","sum_abs_error":1520.9926031249222,"direction_correct":21,"approximate":False},
 {"model":"Huber V1","family":"Challenger-B","sum_abs_error":1530.1299616481554,"direction_correct":20,"approximate":False},
 {"model":"Elastic Net V1","family":"Challenger-B","sum_abs_error":1590.3570524947138,"direction_correct":16,"approximate":False},
]

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def current8_x_only(bundle,target,gh):
    p=base.month_shift(target,-1); pp=base.month_shift(target,-2)
    z=base.gpr_norm(gh,pp); x=[]
    for metal in base.METALS:
        M=bundle.monthly_metal[metal]
        if p not in M or pp not in M: raise RuntimeError(f"FEATURE_MISSING {metal} {target}")
        x.extend((math.log(float(M[p])/float(M[pp])),base.weighted_daily_return(bundle,metal,p,z)))
    out=np.asarray(x,float)
    if out.shape!=(8,) or not np.isfinite(out).all(): raise RuntimeError("CURRENT8_FAIL")
    return out

def build_origin_data(bundle,target):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages: raise RuntimeError(f"GPR_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin]
    samples={}
    for t in base.month_range(TRAIN_START,origin):
        try: samples[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError: continue
    keys=sorted(k for k in samples if TRAIN_START<=k<=origin)
    if len(keys)<INNER_VAL_MONTHS+MIN_INNER_TRAIN: raise RuntimeError("TRAIN_TOO_SMALL")
    split=len(keys)-INNER_VAL_MONTHS; tr,va=keys[:split],keys[split:]
    Xtr=np.stack([samples[k][0] for k in tr])
    Ytr=np.stack([np.asarray(samples[k][1],float).reshape(-1)[:4] for k in tr])
    Xv=np.stack([samples[k][0] for k in va])
    prev=np.asarray([bundle.core_gold[base.month_shift(k,-1)] for k in va],float)
    act=np.asarray([bundle.core_gold[k] for k in va],float)
    Xall=np.stack([samples[k][0] for k in keys])
    Yall=np.stack([np.asarray(samples[k][1],float).reshape(-1)[:4] for k in keys])
    xt=current8_x_only(bundle,target,gh).reshape(1,-1)
    for n,a in {"Xtr":Xtr,"Ytr":Ytr,"Xv":Xv,"prev":prev,"act":act,"Xall":Xall,"Yall":Yall,"xt":xt}.items():
        if not np.isfinite(a).all(): raise RuntimeError(f"NONFINITE {n}")
    if Ytr.shape[1]!=4 or Yall.shape[1]!=4: raise RuntimeError("PLS2_TARGET_DIM_FAIL")
    return {"origin":origin,"keys":keys,"tr":tr,"va":va,"Xtr":Xtr,"Ytr":Ytr,"Xv":Xv,
            "prev":prev,"act":act,"rw_sae":float(np.abs(prev-act).sum()),
            "Xall":Xall,"Yall":Yall,"xt":xt,"anchor":float(bundle.core_gold[origin])}

def fit_model(X,Y,ncomp):
    if ncomp>min(X.shape[0],X.shape[1]): raise RuntimeError("COMPONENT_INVALID")
    model=PLSRegression(n_components=int(ncomp),scale=True,max_iter=2000,tol=1e-8,copy=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always"); model.fit(X,Y)
    return model,len(caught),[str(w.message) for w in caught]

def predict(X,Y,Xtest,ncomp):
    model,wc,wm=fit_model(X,Y,ncomp)
    pred=np.asarray(model.predict(Xtest),float)
    if pred.ndim!=2 or pred.shape[1]!=4 or not np.isfinite(pred).all() or np.any(np.abs(pred)>=1.0):
        raise RuntimeError(f"PLS2_PRED_FAIL ncomp={ncomp} shape={pred.shape}")
    return pred,model,wc,wm

def choose_components(d):
    denom=max(d["rw_sae"],1e-12); scored=[]
    for ncomp in COMPONENTS:
        pred,_,wc,wm=predict(d["Xtr"],d["Ytr"],d["Xv"],ncomp)
        gold_ret=pred[:,0]
        fc=d["prev"]*np.exp(gold_ret)
        sae=float(np.abs(fc-d["act"]).sum())
        scored.append({"n_components":ncomp,"inner_sum_abs_error":sae,
                       "inner_relative_sum_abs_error_vs_rw":float(sae/denom),
                       "warning_count":wc,"warning_messages":wm})
    scored.sort(key=lambda r:(r["inner_relative_sum_abs_error_vs_rw"],r["n_components"]))
    return int(scored[0]["n_components"]),scored

def forecast_one(bundle,target):
    d=build_origin_data(bundle,target); ncomp,scores=choose_components(d)
    model,wc,wm=fit_model(d["Xall"],d["Yall"],ncomp)
    predvec=np.asarray(model.predict(d["xt"]),float).reshape(-1)
    if predvec.shape!=(4,) or not np.isfinite(predvec).all() or np.any(np.abs(predvec)>=1.0):
        raise RuntimeError("OUTER_PRED_FAIL")
    gold_ret=float(predvec[0]); fc=float(d["anchor"]*math.exp(gold_ret))
    if target not in bundle.core_gold: raise RuntimeError("ACTUAL_MISSING")
    actual=float(bundle.core_gold[target]); rw=float(d["anchor"])
    return {"target":target,"origin":d["origin"],"train_first":d["keys"][0],"train_last":d["keys"][-1],
            "train_rows":len(d["keys"]),"inner_train_n":len(d["tr"]),"inner_val_n":len(d["va"]),
            "inner_val_first":d["va"][0],"inner_val_last":d["va"][-1],
            "selected_n_components":ncomp,"component_scores":scores,
            "predicted_returns":{METAL_NAMES[i]:float(predvec[i]) for i in range(4)},
            "pred_log_return_gold":gold_ret,"forecast":fc,"actual":actual,"rw":rw,
            "absolute_error":float(abs(fc-actual)),"rw_absolute_error":float(abs(rw-actual)),
            "direction_correct":bool(int(np.sign(fc-rw))==int(np.sign(actual-rw))),
            "coef_l2_norm":float(np.linalg.norm(np.asarray(model.coef_,float))),
            "n_iter_per_component":[int(v) for v in getattr(model,"n_iter_",[])],
            "warning_count_outer":wc,"warning_messages_outer":wm}

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows],float); f=np.asarray([r["forecast"] for r in rows],float); rw=np.asarray([r["rw"] for r in rows],float)
    ae=np.abs(f-a); rwae=np.abs(rw-a); dc=np.asarray([r["direction_correct"] for r in rows],bool); wi=int(np.argmax(ae))
    return {"n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),
            "rmse":float(np.sqrt(np.mean((f-a)**2))),
            "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),
            "wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
            "median_ae":float(np.median(ae)),"worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
            "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
            "rw_sum_abs_error":float(rwae.sum()),"direction_correct":int(dc.sum()),
            "direction_accuracy_pct":float(dc.mean()*100),
            "mean_coef_l2_norm":float(np.mean([r["coef_l2_norm"] for r in rows])),
            "outer_warning_count":int(sum(r["warning_count_outer"] for r in rows))}

def yearly(rows):
    return {y:metrics([r for r in rows if r["target"].startswith(y)]) for y in sorted({r["target"][:4] for r in rows})}

def run_period(bundle,start,end,label):
    rows=[]; targets=list(base.month_range(start,end))
    for i,t in enumerate(targets,1):
        r=forecast_one(bundle,t); rows.append(r)
        print(f"PROGRESS period={label} target={i}/{len(targets)} month={t} ncomp={r['selected_n_components']} AE={r['absolute_error']:.6f} dir={int(r['direction_correct'])}",flush=True)
    return {"role":label,"metrics":metrics(rows),"yearly":yearly(rows),
            "selected_component_counts":dict(sorted(Counter(str(r["selected_n_components"]) for r in rows).items())),
            "rows":rows}

def comparison(devm):
    pls={"model":"PLS2 V1","family":"Challenger-B","sum_abs_error":float(devm["sum_abs_error"]),
         "direction_correct":int(devm["direction_correct"]),"approximate":False}
    allrows=[dict(x) for x in FRONTIER]+[pls]
    ranked=sorted(allrows,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
    for i,r in enumerate(ranked,1): r["price_error_rank"]=i
    rank=next(r["price_error_rank"] for r in ranked if r["model"]=="PLS2 V1")
    dominators=[r["model"] for r in allrows if r["model"]!="PLS2 V1"
                and r["sum_abs_error"]<=pls["sum_abs_error"] and r["direction_correct"]>=pls["direction_correct"]
                and (r["sum_abs_error"]<pls["sum_abs_error"] or r["direction_correct"]>pls["direction_correct"])]
    return {"ranking_by_primary_sumae":ranked,"pls2_price_error_rank":rank,
            "comparison_pool_n":len(ranked),"pareto_dominated_by":dominators,
            "pareto_nondominated_within_pool":len(dominators)==0}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    b0={"source_checks":bundle.source_checks,
        "current8_feature_contract":{"metals":list(base.METALS),"feature_dim":8,"training_outputs":list(METAL_NAMES),
                                     "gpr_source":base.GPR_PIT,"outer_feature_builder":"X_ONLY_NO_TARGET_MONTH_METAL_DEREFERENCE"},
        "gate_pass":not bundle.source_checks["missing_required_gpr_origins"] and not bundle.source_checks["late_required_gpr_origins"] and not bundle.source_checks["missing_required_gpr_lag_month"]}
    if not b0["gate_pass"]: raise RuntimeError("B0_FAIL")
    dev=run_period(bundle,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY")
    if dev["metrics"]["n"]!=33: raise RuntimeError("DEV_N_FAIL")
    hold=run_period(bundle,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY")
    stress=run_period(bundle,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")
    after=read_invariants(dsn); same=after==bundle.invariants_before
    if not same: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")
    comp=comparison(dev["metrics"])
    digest=hashlib.sha256(json.dumps({"dev":dev["rows"],"hold":hold["rows"],"stress":stress["rows"]},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={"model_id":MODEL_ID,"freeze_file":FREEZE_FILE,"scientific_gate":"PASS",
         "contract":{"target":"H=1 next-calendar-month average XAU/USD","training_target":"4-metal next-month log returns (PLS2)",
                     "training_outputs":4,"evaluation_target":"Gold only","representation":"CURRENT8","training_start":TRAIN_START,
                     "inner_validation_months":INNER_VAL_MONTHS,"n_components_grid":list(COMPONENTS),
                     "component_selection":"per-origin last-12 pre-target months; Gold price relative cumulative AE vs RW",
                     "tie_break":"lower objective, fewer components",
                     "scaling":"PLSRegression(scale=True), internal X/Y training-fold scaling; no external scaler",
                     "estimator":"sklearn.cross_decomposition.PLSRegression","max_iter":2000,"tol":1e-8,
                     "random_split":"NONE","database":"READ_ONLY","primary_metric":"DEV_GOLD_PRICE_SUM_ABS_ERROR",
                     "2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY",
                     "metal_ablation":"NOT_IN_V1","outer_target_metal_feature_access":"NONE"},
         "b0_audit":b0,"authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,
         "authority_invariants_unchanged":same,
         "software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},
         "dev":dev,"holdout_2025":hold,"stress_2026":stress,"challenger_a_comparison":comp,"result_payload_sha256":digest}
    Path("gold_monthly_challenger_b_pls2_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PLS2_CHALLENGER_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"b0_gate_pass":b0["gate_pass"],"dev_metrics":dev["metrics"],
                      "dev_component_counts":dev["selected_component_counts"],
                      "pls2_price_error_rank":comp["pls2_price_error_rank"],"comparison_pool_n":comp["comparison_pool_n"],
                      "pareto_dominated_by":comp["pareto_dominated_by"],
                      "holdout_2025_metrics":hold["metrics"],"stress_2026_metrics":stress["metrics"],
                      "authority_invariants_unchanged":same,"result_payload_sha256":digest},sort_keys=True),flush=True)

if __name__=="__main__": main()
