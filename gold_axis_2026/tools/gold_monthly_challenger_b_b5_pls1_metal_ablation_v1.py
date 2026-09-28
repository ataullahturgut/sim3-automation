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

MODEL_ID = "GOLD_MONTHLY_CHALLENGER_B_B5_PLS1_METAL_ABLATION_V1"
FREEZE_FILE = "GOLD_MONTHLY_CHALLENGER_B_B5_PLS1_METAL_ABLATION_FREEZE_2026-09-28.md"

TRAIN_START = "2010-05"
INNER_VAL_MONTHS = 12
MIN_INNER_TRAIN = 36

DEV_START, DEV_END = "2022-04", "2024-12"
HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
STRESS_START, STRESS_END = "2026-01", "2026-07"

FEATURE_NAMES = (
    "Gold_MR","Gold_VW","Silver_MR","Silver_VW",
    "Platinum_MR","Platinum_VW","Palladium_MR","Palladium_VW",
)

VARIANTS = (
    {"id":"M0_GOLD_ONLY","metals":["Gold"],"indices":[0,1]},
    {"id":"M1_GOLD_SILVER","metals":["Gold","Silver"],"indices":[0,1,2,3]},
    {"id":"M2_ALL4_REFERENCE","metals":["Gold","Silver","Platinum","Palladium"],"indices":[0,1,2,3,4,5,6,7]},
    {"id":"M3_NO_SILVER","metals":["Gold","Platinum","Palladium"],"indices":[0,1,4,5,6,7]},
    {"id":"M4_NO_PLATINUM","metals":["Gold","Silver","Palladium"],"indices":[0,1,2,3,6,7]},
    {"id":"M5_NO_PALLADIUM","metals":["Gold","Silver","Platinum"],"indices":[0,1,2,3,4,5]},
)

REFERENCE_DEV_SUMAE = 1420.0291314697745
REFERENCE_DEV_DIRECTION = 20
REPRO_TOL = 1e-9

FRONTIER = [
    {"model":"ChHHO-ANFIS","family":"ANFIS","sum_abs_error":1413.029779,"direction_correct":23,"approximate":False},
    {"model":"RBFNN DE-ABC","family":"RBFNN","sum_abs_error":1415.8371,"direction_correct":25,"approximate":True},
    {"model":"PLS1 V1 All-4","family":"Challenger-B","sum_abs_error":1420.0291314697745,"direction_correct":20,"approximate":False},
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
    {"model":"GPReg-Matern V1","family":"Challenger-B","sum_abs_error":1637.916541466211,"direction_correct":19,"approximate":False},
    {"model":"GPReg-RBF V1","family":"Challenger-B","sum_abs_error":1696.3365035638303,"direction_correct":16,"approximate":False},
    {"model":"HGB V1","family":"Challenger-B","sum_abs_error":1840.2678387980486,"direction_correct":20,"approximate":False},
]

def read_invariants(dsn):
    with psycopg.connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def current8_x_only(bundle, target, gh):
    p = base.month_shift(target, -1)
    pp = base.month_shift(target, -2)
    z = base.gpr_norm(gh, pp)
    x = []
    for metal in base.METALS:
        M = bundle.monthly_metal[metal]
        if p not in M or pp not in M:
            raise RuntimeError(f"FEATURE_MISSING metal={metal} target={target}")
        x.extend((
            math.log(float(M[p]) / float(M[pp])),
            base.weighted_daily_return(bundle, metal, p, z),
        ))
    out = np.asarray(x, dtype=float)
    if out.shape != (8,) or not np.isfinite(out).all():
        raise RuntimeError(f"CURRENT8_FAIL target={target}")
    return out

def build_full_origin_data(bundle, target):
    origin = base.month_shift(target, -1)
    if origin not in bundle.gpr_vintages:
        raise RuntimeError(f"GPR_VINTAGE_MISSING {origin}")
    gh = bundle.gpr_vintages[origin]

    samples = {}
    for t in base.month_range(TRAIN_START, origin):
        try:
            samples[t] = base.sample_for_target(bundle, t, gh, True)
        except RuntimeError:
            continue

    keys = sorted(k for k in samples if TRAIN_START <= k <= origin)
    if len(keys) < INNER_VAL_MONTHS + MIN_INNER_TRAIN:
        raise RuntimeError(f"TRAIN_TOO_SMALL target={target} n={len(keys)}")

    split = len(keys) - INNER_VAL_MONTHS
    tr, va = keys[:split], keys[split:]

    Xtr8 = np.stack([samples[k][0] for k in tr])
    ytr = np.asarray([float(samples[k][1][0]) for k in tr], dtype=float)
    Xv8 = np.stack([samples[k][0] for k in va])
    prev = np.asarray([float(bundle.core_gold[base.month_shift(k, -1)]) for k in va], dtype=float)
    act = np.asarray([float(bundle.core_gold[k]) for k in va], dtype=float)

    Xall8 = np.stack([samples[k][0] for k in keys])
    yall = np.asarray([float(samples[k][1][0]) for k in keys], dtype=float)
    xt8 = current8_x_only(bundle, target, gh).reshape(1, -1)

    for name, arr in {
        "Xtr8":Xtr8,"ytr":ytr,"Xv8":Xv8,"prev":prev,"act":act,
        "Xall8":Xall8,"yall":yall,"xt8":xt8
    }.items():
        if not np.isfinite(arr).all():
            raise RuntimeError(f"NONFINITE target={target} field={name}")

    return {
        "origin":origin,"keys":keys,"tr":tr,"va":va,
        "Xtr8":Xtr8,"ytr":ytr,"Xv8":Xv8,"prev":prev,"act":act,
        "rw_sae":float(np.abs(prev-act).sum()),
        "Xall8":Xall8,"yall":yall,"xt8":xt8,
        "anchor":float(bundle.core_gold[origin]),
    }

def subset(data, variant):
    idx = np.asarray(variant["indices"], dtype=int)
    return {
        **data,
        "Xtr":data["Xtr8"][:,idx],
        "Xv":data["Xv8"][:,idx],
        "Xall":data["Xall8"][:,idx],
        "xt":data["xt8"][:,idx],
        "feature_names":[FEATURE_NAMES[i] for i in idx],
    }

def fit_model(X, y, ncomp):
    if ncomp < 1 or ncomp > min(X.shape[0], X.shape[1]):
        raise RuntimeError(f"PLS_COMPONENT_INVALID n={ncomp} shape={X.shape}")
    m = PLSRegression(n_components=int(ncomp), scale=True, max_iter=2000, tol=1e-8, copy=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        m.fit(X, y.reshape(-1,1))
    return m, len(caught), [str(w.message) for w in caught]

def choose_components(d):
    max_comp = d["Xtr"].shape[1]
    den = max(float(d["rw_sae"]),1e-12)
    scored = []
    for ncomp in range(1, max_comp+1):
        m,wc,wm = fit_model(d["Xtr"], d["ytr"], ncomp)
        pred = np.asarray(m.predict(d["Xv"]), dtype=float).reshape(-1)
        if not np.isfinite(pred).all() or np.any(np.abs(pred)>=1.0):
            raise RuntimeError(f"INNER_PRED_FAIL ncomp={ncomp}")
        fc = d["prev"] * np.exp(pred)
        sae = float(np.abs(fc-d["act"]).sum())
        scored.append({
            "n_components":int(ncomp),
            "inner_sum_abs_error":sae,
            "inner_relative_sum_abs_error_vs_rw":float(sae/den),
            "warning_count":int(wc),
            "warning_messages":wm,
        })
    scored.sort(key=lambda r:(r["inner_relative_sum_abs_error_vs_rw"], r["n_components"]))
    return int(scored[0]["n_components"]), scored

def forecast_one(full_data, bundle, target, variant):
    d = subset(full_data, variant)
    ncomp, scores = choose_components(d)
    m,wc,wm = fit_model(d["Xall"], d["yall"], ncomp)
    pred = float(np.asarray(m.predict(d["xt"]), dtype=float).reshape(-1)[0])
    if not math.isfinite(pred) or abs(pred)>=1.0:
        raise RuntimeError(f"OUTER_PRED_FAIL target={target} variant={variant['id']}")
    fc = float(d["anchor"] * math.exp(pred))
    actual = float(bundle.core_gold[target])
    rw = float(d["anchor"])
    return {
        "variant_id":variant["id"],
        "metals":variant["metals"],
        "feature_names":d["feature_names"],
        "feature_dim":len(d["feature_names"]),
        "target":target,"origin":d["origin"],
        "train_rows":len(d["keys"]),"train_first":d["keys"][0],"train_last":d["keys"][-1],
        "inner_val_first":d["va"][0],"inner_val_last":d["va"][-1],
        "selected_n_components":ncomp,"component_scores":scores,
        "forecast":fc,"actual":actual,"rw":rw,"pred_log_return_gold":pred,
        "absolute_error":float(abs(fc-actual)),"rw_absolute_error":float(abs(rw-actual)),
        "direction_correct":bool(int(np.sign(fc-rw))==int(np.sign(actual-rw))),
        "warning_count_outer":int(wc),"warning_messages_outer":wm,
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
        "median_ae":float(np.median(ae)),"worst_ae":float(ae[wi]),"worst_month":rows[wi]["target"],
        "relative_mae_vs_rw":float(ae.sum()/max(float(rwae.sum()),1e-12)),
        "rw_sum_abs_error":float(rwae.sum()),"direction_correct":int(dc.sum()),
        "direction_accuracy_pct":float(dc.mean()*100),
        "outer_warning_count":int(sum(r["warning_count_outer"] for r in rows)),
    }

def run_variant_period(bundle, variant, start, end, label, cache):
    rows=[]
    targets=list(base.month_range(start,end))
    for i,t in enumerate(targets,1):
        if t not in cache:
            cache[t]=build_full_origin_data(bundle,t)
        row=forecast_one(cache[t],bundle,t,variant)
        rows.append(row)
        print(
            f"PROGRESS variant={variant['id']} period={label} {i}/{len(targets)} "
            f"month={t} p={row['feature_dim']} ncomp={row['selected_n_components']} "
            f"AE={row['absolute_error']:.6f} dir={int(row['direction_correct'])}",
            flush=True
        )
    return {
        "role":label,
        "metrics":metrics(rows),
        "selected_component_counts":dict(sorted(Counter(str(r["selected_n_components"]) for r in rows).items())),
        "rows":rows,
    }

def pareto_variant_ids(dev_summaries):
    out=[]
    for a in dev_summaries:
        dominated=False
        for b in dev_summaries:
            if a["variant_id"]==b["variant_id"]: continue
            if (b["sum_abs_error"] <= a["sum_abs_error"]
                and b["direction_correct"] >= a["direction_correct"]
                and (b["sum_abs_error"] < a["sum_abs_error"] or b["direction_correct"] > a["direction_correct"])):
                dominated=True; break
        if not dominated: out.append(a["variant_id"])
    return out

def cross_family(best):
    # Remove the old All-4 PLS1 row only if the best ablation is the exact same M2 reference.
    rows=[dict(x) for x in FRONTIER]
    model_name=f"PLS1 B5 {best['variant_id']}"
    if best["variant_id"]=="M2_ALL4_REFERENCE":
        rows=[r for r in rows if r["model"]!="PLS1 V1 All-4"]
    me={"model":model_name,"family":"Challenger-B B5","sum_abs_error":best["sum_abs_error"],
        "direction_correct":best["direction_correct"],"approximate":False}
    allr=rows+[me]
    ranked=sorted(allr,key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["model"]))
    for i,r in enumerate(ranked,1): r["price_error_rank"]=i
    rank=next(r["price_error_rank"] for r in ranked if r["model"]==model_name)
    dom=[r["model"] for r in allr if r["model"]!=model_name
         and r["sum_abs_error"]<=me["sum_abs_error"] and r["direction_correct"]>=me["direction_correct"]
         and (r["sum_abs_error"]<me["sum_abs_error"] or r["direction_correct"]>me["direction_correct"])]
    return {"model_name":model_name,"ranking_by_primary_sumae":ranked,"price_error_rank":rank,
            "comparison_pool_n":len(ranked),"pareto_dominated_by":dom,"pareto_nondominated_within_pool":not dom}

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    b0={"source_checks":bundle.source_checks,
        "gate_pass":not bundle.source_checks["missing_required_gpr_origins"]
                    and not bundle.source_checks["late_required_gpr_origins"]
                    and not bundle.source_checks["missing_required_gpr_lag_month"]}
    if not b0["gate_pass"]: raise RuntimeError("B0_SOURCE_GATE_FAIL")

    cache={}
    results={}
    for v in VARIANTS:
        print(f"VARIANT_START {v['id']} metals={','.join(v['metals'])}",flush=True)
        dev=run_variant_period(bundle,v,DEV_START,DEV_END,"DEV_SELECTION_AUTHORITY",cache)
        hold=run_variant_period(bundle,v,HOLDOUT_START,HOLDOUT_END,"LOCKED_REPORT_ONLY",cache)
        stress=run_variant_period(bundle,v,STRESS_START,STRESS_END,"QUARANTINED_REPORT_ONLY",cache)
        results[v["id"]]={"definition":v,"dev":dev,"holdout_2025":hold,"stress_2026":stress}

    m2=results["M2_ALL4_REFERENCE"]["dev"]["metrics"]
    repro_pass=(abs(float(m2["sum_abs_error"])-REFERENCE_DEV_SUMAE)<=REPRO_TOL
                and int(m2["direction_correct"])==REFERENCE_DEV_DIRECTION)
    reproduction_gate={
        "expected_sumae":REFERENCE_DEV_SUMAE,
        "observed_sumae":m2["sum_abs_error"],
        "absolute_difference":abs(float(m2["sum_abs_error"])-REFERENCE_DEV_SUMAE),
        "tolerance":REPRO_TOL,
        "expected_direction":REFERENCE_DEV_DIRECTION,
        "observed_direction":m2["direction_correct"],
        "pass":bool(repro_pass),
    }
    if not repro_pass: raise RuntimeError(f"M2_REFERENCE_REPRODUCTION_FAIL {reproduction_gate}")

    m2_sae=float(m2["sum_abs_error"]); m2_dir=int(m2["direction_correct"])
    dev_summary=[]
    for v in VARIANTS:
        met=results[v["id"]]["dev"]["metrics"]
        dev_summary.append({
            "variant_id":v["id"],"metals":v["metals"],"feature_dim":len(v["indices"]),
            "sum_abs_error":float(met["sum_abs_error"]),"direction_correct":int(met["direction_correct"]),
            "direction_accuracy_pct":float(met["direction_accuracy_pct"]),
            "relative_mae_vs_rw":float(met["relative_mae_vs_rw"]),
            "delta_sumae_vs_all4":float(met["sum_abs_error"]-m2_sae),
            "delta_direction_vs_all4":int(met["direction_correct"]-m2_dir),
        })
    dev_summary.sort(key=lambda r:(r["sum_abs_error"],-r["direction_correct"],r["variant_id"]))
    for i,r in enumerate(dev_summary,1): r["dev_price_error_rank"]=i
    pareto=pareto_variant_ids(dev_summary)
    best=dev_summary[0]
    comp=cross_family(best)

    after=read_invariants(dsn); same=after==bundle.invariants_before
    if not same: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    digest=hashlib.sha256(json.dumps(results,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    out={
        "model_id":MODEL_ID,"freeze_file":FREEZE_FILE,"scientific_gate":"PASS",
        "contract":{
            "target":"H=1 next-calendar-month average XAU/USD",
            "training_target":"Gold next-month log return (PLS1)",
            "representation":"CURRENT8_SUBSET_ABLATION",
            "training_start":TRAIN_START,
            "variants":[v["id"] for v in VARIANTS],
            "variant_selection_authority":"DEV_ONLY",
            "inner_validation_months":INNER_VAL_MONTHS,
            "n_components_grid_rule":"1..feature_dim for each variant",
            "component_selection":"per-origin last-12 pre-target months; min relative cumulative price AE vs RW",
            "scaling":"PLSRegression(scale=True), training-fold internal scaling",
            "random_split":"NONE","database":"READ_ONLY",
            "2025_role":"LOCKED_REPORT_ONLY","2026_role":"QUARANTINED_REPORT_ONLY",
        },
        "b0_audit":b0,"reproduction_gate":reproduction_gate,
        "dev_variant_ranking":dev_summary,"dev_pareto_variant_ids":pareto,
        "best_dev_variant":best,"best_variant_cross_family_comparison":comp,
        "variants":results,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "authority_invariants_unchanged":same,
        "software":{"python":platform.python_version(),"numpy":np.__version__,"scikit_learn":sklearn.__version__},
        "result_payload_sha256":digest,
    }
    Path("gold_monthly_challenger_b_b5_pls1_metal_ablation_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("B5_PLS1_METAL_ABLATION_OUTPUT_GATE=PASS",flush=True)
    print(json.dumps({
        "reproduction_gate":reproduction_gate,
        "dev_variant_ranking":dev_summary,
        "dev_pareto_variant_ids":pareto,
        "best_dev_variant":best,
        "cross_family_rank":comp["price_error_rank"],
        "cross_family_pool_n":comp["comparison_pool_n"],
        "cross_family_dominated_by":comp["pareto_dominated_by"],
        "report_only_2025":{
            k:results[k]["holdout_2025"]["metrics"] for k in results
        },
        "report_only_2026":{
            k:results[k]["stress_2026"]["metrics"] for k in results
        },
        "authority_invariants_unchanged":same,
        "sha256":digest,
    },sort_keys=True),flush=True)

if __name__=="__main__":
    main()
