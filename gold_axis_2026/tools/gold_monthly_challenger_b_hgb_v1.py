#!/usr/bin/env python3
from __future__ import annotations

import hashlib, json, math, os, platform
from collections import Counter
from pathlib import Path
import numpy as np, psycopg, sklearn
from sklearn.ensemble import HistGradientBoostingRegressor
import vw_midas_msvr_successor_v1 as base

MODEL_ID="GOLD_MONTHLY_CHALLENGER_B_HGB_V1"
FREEZE_FILE="GOLD_MONTHLY_CHALLENGER_B_HGB_FREEZE_2026-09-28.md"
TRAIN_START="2010-05"; INNER_VAL_MONTHS=12; MIN_INNER_TRAIN=36
DEV_START,DEV_END="2022-04","2024-12"
HOLDOUT_START,HOLDOUT_END="2025-01","2025-12"
STRESS_START,STRESS_END="2026-01","2026-07"

CANDIDATES=(
 {"id":"HGB_A","learning_rate":0.05,"max_iter":250,"max_leaf_nodes":7,"min_samples_leaf":12,"l2_regularization":5.0},
 {"id":"HGB_B","learning_rate":0.10,"max_iter":150,"max_leaf_nodes":7,"min_samples_leaf":15,"l2_regularization":10.0},
)

FRONTIER=[
{"model":"ChHHO-ANFIS","family":"ANFIS","sum_abs_error":1413.029779,"direction_correct":23,"approximate":False},
{"model":"RBFNN DE-ABC","family":"RBFNN","sum_abs_error":1415.8371,"direction_correct":25,"approximate":True},
{"model":"PLS1 V1","family":"Challenger-B","sum_abs_error":1420.0291314697745,"direction_correct":20,"approximate":False},
{"model":"GPR/MOGP LMC2_RBF_M32","family":"GPR/MOGP","sum_abs_error":1424.17,"direction_correct":19,"approximate":True},
{"model":"FULL7 Equal ANN Ensemble","family":"ANN","sum_abs_error":1428.86,"direction_correct":22,"approximate":False},
{"model":"REDUCED4 Equal ANN Ensemble","family":"ANN","sum_abs_error":1431.46,"direction_correct":24,"approximate":False},
{"model":"SVR frozen parent","family":"SVR","sum_abs_error":1449.187363,"direction_correct":19,"approximate":False},
{"model":"CatBoost PRICE","family":"Boosting","sum_abs_error":1460.433935309605,"direction_correct":20,"approximate":False},
{"model":"PLS2 V1","family":"Challenger-B","sum_abs_error":1489.3300296660234,"direction_correct":23,"approximate":False},
{"model":"Random Forest comparator","family":"RF","sum_abs_error":1491.550693715667,"direction_correct":20,"approximate":False},
{"model":"Ridge V1","family":"Challenger-B","sum_abs_error":1520.9926031249222,"direction_correct":21,"approximate":False},
{"model":"Huber V1","family":"Challenger-B","sum_abs_error":1530.1299616481554,"direction_correct":20,"approximate":False},
{"model":"Extra Trees V1","family":"Challenger-B","sum_abs_error":1539.9220718606994,"direction_correct":20,"approximate":False},
{"model":"Elastic Net V1","family":"Challenger-B","sum_abs_error":1590.3570524947138,"direction_correct":16,"approximate":False},
{"model":"GPReg-Matérn V1","family":"Challenger-B","sum_abs_error":1637.916541466211,"direction_correct":19,"approximate":False},
{"model":"GPReg-RBF V1","family":"Challenger-B","sum_abs_error":1696.3365035638303,"direction_correct":16,"approximate":False},
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
    if out.shape!=(8,) or not np.isfinite(out).all(): raise RuntimeError(f"CURRENT8_FAIL {target}")
    return out

def build_origin_data(bundle,target):
    origin=base.month_shift(target,-1)
    if origin not in bundle.gpr_vintages: raise RuntimeError(f"GPR_VINTAGE_MISSING {origin}")
    gh=bundle.gpr_vintages[origin]; samples={}
    for t in base.month_range(TRAIN_START,origin):
        try: samples[t]=base.sample_for_target(bundle,t,gh,True)
        except RuntimeError: continue
    keys=sorted(k for k in samples if TRAIN_START<=k<=origin)
    if len(keys)<INNER_VAL_MONTHS+MIN_INNER_TRAIN: raise RuntimeError(f"TRAIN_TOO_SMALL {target}")
    split=len(keys)-INNER_VAL_MONTHS; tr,va=keys[:split],keys[split:]
    Xtr=np.stack([samples[k][0] for k in tr]); ytr=np.asarray([samples[k][1][0] for k in tr],float)
    Xv=np.stack([samples[k][0] for k in va]); prev=np.asarray([bundle.core_gold[base.month_shift(k,-1)] for k in va],float); act=np.asarray([bundle.core_gold[k] for k in va],float)
    Xall=np.stack([samples[k][0] for k in keys]); yall=np.asarray([samples[k][1][0] for k in keys],float)
    xt=current8_x_only(bundle,target,gh).reshape(1,-1)
    for arr in (Xtr,ytr,Xv,prev,act,Xall,yall,xt):
        if not np.isfinite(arr).all(): raise RuntimeError(f"NONFINITE {target}")
    return {"origin":origin,"keys":keys,"tr":tr,"va":va,"Xtr":Xtr,"ytr":ytr,"Xv":Xv,"prev":prev,"act":act,
            "rw_sae":float(np.abs(prev-act).sum()),"Xall":Xall,"yall":yall,"xt":xt,"anchor":float(bundle.core_gold[origin])}

def fit_model(X,y,c):
    m=HistGradientBoostingRegressor(
        learning_rate=c["learning_rate"], max_iter=c["max_iter"], max_leaf_nodes=c["max_leaf_nodes"],
        min_samples_leaf=c["min_samples_leaf"], l2_regularization=c["l2_regularization"],
        early_stopping=False, random_state=42
    )
    m.fit(X,y)
    return m

def choose_candidate(d):
    den=max(d["rw_sae"],1e-12); scored=[]
    for idx,c in enumerate(CANDIDATES):
        m=fit_model(d["Xtr"],d["ytr"],c)
        pred=np.asarray(m.predict(d["Xv"]),float)
        if not np.isfinite(pred).all() or np.any(np.abs(pred)>=1): raise RuntimeError(f"PATHOLOGICAL_INNER {c['id']}")
        fc=d["prev"]*np.exp(pred); sae=float(np.abs(fc-d["act"]).sum())
        scored.append({"candidate_id":c["id"],"candidate_order":idx,"params":c,
                       "inner_sum_abs_error":sae,"inner_relative_sum_abs_error_vs_rw":float(sae/den)})
    scored.sort(key=lambda r:(r["inner_relative_sum_abs_error_vs_rw"],r["candidate_order"]))
    best=scored[0]
    cand=next(c for c in CANDIDATES if c["id"]==best["candidate_id"])
    return cand,scored

def forecast_one(bundle,target):
    d=build_origin_data(bundle,target); cand,scores=choose_candidate(d)
    m=fit_model(d["Xall"],d["yall"],cand)
    pred=float(np.asarray(m.predict(d["xt"]),float).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1: raise RuntimeError(f"PATHOLOGICAL_OUTER {target}")
    fc=float(d["anchor"]*math.exp(pred)); actual=float(bundle.core_gold[target]); rw=float(d["anchor"])
    return {"target":target,"origin":d["origin"],"train_rows":len(d["keys"]),"train_first":d["keys"][0],"train_last":d["keys"][-1],
            "inner_val_first":d["va"][0],"inner_val_last":d["va"][-1],"selected_candidate":cand["id"],"selected_params":cand,
            "candidate_scores":scores,"pred_log_return_gold":pred,"forecast":fc,"actual":actual,"rw":rw,
            "absolute_error":float(abs(fc-actual)),"rw_absolute_error":float(abs(rw-actual)),
            "direction_correct":bool(int(np.sign(fc-rw))==int(np.sign(actual-rw))),
            "n_iter_fitted":int(getattr(m,"n_iter_",cand["max_iter"]))}

def metrics(rows):
    a=np.asarray([r["actual"] for r in rows]); f=np.asarray([r["forecast"] for r in rows]); rw=np.asarray([r["rw"] for r in rows])
    ae=np.abs(f-a); rwae=np.abs(rw-a); dc=np.asarray([r["direction_correct"] for r in rows],bool); wi=int(np.argmax(ae))
    return {"n":len(rows),"sum_abs_error":float(ae.sum()),"mae":float(ae.mean()),"rmse":float(np.sqrt(np.mean((f-a)**2))),
            "mape_pct":float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100),"wape_pct":float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100),
            "median_ae":float(np.median(ae)),"worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
            "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),"rw_sum_abs_error":float(rwae.sum()),
            "direction_correct":int(dc.sum()),"direction_accuracy_pct":float(dc.mean()*100),
            "mean_n_iter_fitted":float(np.mean([r["n_iter_fitted"] for r in rows]))}

def run_period(bundle,start,end,label):
    rows=[]; targets=list(base.month_range(start,end))
    for i,t in enumerate(targets,1):
        r=forecast_one(bundle,t); rows.append(r)
        print(f"PROGRESS {label} {i}/{len(targets)} {t} cand={r['selected_candidate']} AE={r['absolute_error']:.6f} dir={int(r['direction_correct'])}",flush=True)
    return {"role":label,"metrics":metrics(rows),
            "selected_candidate_counts":dict(sorted(Counter(r["selected_candidate"] for r in rows).items())),"rows":rows}

def comparison(dm):
    me={"model":"HGB V1","family":"Challenger-B","sum_abs_error":float(dm["sum_abs_error"]),"direction_correct":int(dm["direction_correct"]),"approximate":False}
    allr=[dict(x) for x in FRONTIER]+[me]; ranked=sorted(allr,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
    for i,r in enumerate(ranked,1): r["price_error_rank"]=i
    rank=next(r["price_error_rank"] for r in ranked if r["model"]=="HGB V1")
    dom=[r["model"] for r in allr if r["model"]!="HGB V1" and r["sum_abs_error"]<=me["sum_abs_error"] and r["direction_correct"]>=me["direction_correct"] and (r["sum_abs_error"]<me["sum_abs_error"] or r["direction_correct"]>me["direction_correct"])]
    return {"ranking_by_primary_sumae":ranked,"hgb_price_error_rank":rank,"comparison_pool_n":len(ranked),
            "pareto_dominated_by":dom,"pareto_nondominated_within_pool":not dom}

def main():
    dsn=os.environ["NEON_DATABASE_URL"]; bundle=base.load_data(dsn)
    b0={"source_checks":bundle.source_checks,"gate_pass":not bundle.source_checks["missing_required_gpr_origins"] and not bundle.source_checks["late_required_gpr_origins"] and not bundle.source_checks["missing_required_gpr_lag_month"]}
    if not b0["gate_pass"]: raise RuntimeError("B0_FAIL")
    dev=run_period(bundle,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY")
    hold=run_period(bundle,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY")
    stress=run_period(bundle,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY")
    after=read_invariants(dsn); same=after==bundle.invariants_before
    if not same: raise RuntimeError("AUTHORITY_CHANGED")
    comp=comparison(dev["metrics"])
    digest=hashlib.sha256(json.dumps({"dev":dev["rows"],"hold":hold["rows"],"stress":stress["rows"]},sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={"model_id":MODEL_ID,"freeze_file":FREEZE_FILE,"scientific_gate":"PASS",
         "contract":{"target":"H=1 next-calendar-month average XAU/USD","training_target":"Gold next-month log return",
                     "representation":"CURRENT8","training_start":TRAIN_START,"candidate_grid":list(CANDIDATES),
                     "estimator":"sklearn.ensemble.HistGradientBoostingRegressor","scaling":"NONE_TREE_NATIVE",
                     "early_stopping":False,"random_state":42,"random_split":"NONE","database":"READ_ONLY",
                     "2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY","metal_ablation":"NOT_IN_V1"},
         "b0_audit":b0,"authority_invariants_before":bundle.invariants_before,"authority_invariants_after":after,"authority_invariants_unchanged":same,
         "software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},
         "dev":dev,"holdout_2025":hold,"stress_2026":stress,"challenger_a_comparison":comp,"result_payload_sha256":digest}
    Path("gold_monthly_challenger_b_hgb_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("HGB_CHALLENGER_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({"dev_metrics":dev["metrics"],"dev_candidate_counts":dev["selected_candidate_counts"],
                      "rank":comp["hgb_price_error_rank"],"dominated_by":comp["pareto_dominated_by"],
                      "holdout_2025_metrics":hold["metrics"],"stress_2026_metrics":stress["metrics"],
                      "authority_invariants_unchanged":same,"sha256":digest},sort_keys=True),flush=True)

if __name__=="__main__": main()
