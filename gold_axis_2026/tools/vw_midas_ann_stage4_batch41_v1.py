from __future__ import annotations

import argparse, json, math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize

RUNS = {
    "BATCH1": "36127630549",
    "BATCH2": "36128225062",
    "BATCH5": "36129458713",
    "BATCH8": "36130538857",
    "STAGE31": "36132219383",
    "STAGE32": "36132859342",
    "STAGE34": "36134549789",
}

COMPONENTS = [
    "VANILLA",
    "MPA",
    "SCA",
    "DE_ABC",
    "ADAPTIVE_TLBO",
    "TLBO_TUNED_PSO",
    "MPA_SCA",
]
MIN_META_HISTORY = 6


def load_json(root: Path, run: str, filename: str):
    p = root / run / filename
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))


def load_components(root: Path):
    out = {}

    r = load_json(root, RUNS["BATCH1"], "vw_midas_shallow_mlp_v1_result.json")
    out["VANILLA"] = {
        "dev": r["dev"]["rows"],
        "transport_2025": r["transport_2025"]["rows"],
        "stress_2026": r["stress_2026"]["rows"],
    }

    r = load_json(root, RUNS["BATCH2"], "vw_midas_ann_meta_batch_2_v1_result.json")
    out["MPA"] = {p: r["models"]["MPA"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r = load_json(root, RUNS["BATCH5"], "vw_midas_ann_meta_batch_5_v1_result.json")
    out["SCA"] = {p: r["models"]["SCA"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r = load_json(root, RUNS["BATCH8"], "vw_midas_ann_meta_batch_8_v1_result.json")
    out["DE_ABC"] = {p: r["models"]["DE_ABC"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r = load_json(root, RUNS["STAGE31"], "vw_midas_ann_stage3_batch31_v1_result.json")
    out["ADAPTIVE_TLBO"] = {p: r["models"]["ADAPTIVE_TLBO"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r = load_json(root, RUNS["STAGE32"], "vw_midas_ann_stage3_batch32_v1_result.json")
    out["TLBO_TUNED_PSO"] = {p: r["models"]["TLBO_TUNED_PSO"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r = load_json(root, RUNS["STAGE34"], "vw_midas_ann_stage3_batch34_v1_result.json")
    out["MPA_SCA"] = {p: r["models"]["MPA_SCA"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    if set(out) != set(COMPONENTS):
        raise RuntimeError("COMPONENT_SET_MISMATCH")
    return out


def aligned_matrix(components, period):
    targets = [r["target"] for r in components[COMPONENTS[0]][period]]
    for name in COMPONENTS:
        if [r["target"] for r in components[name][period]] != targets:
            raise RuntimeError(f"TARGET_ALIGNMENT_FAIL {name} {period}")

    P = np.column_stack([
        [float(r["forecast"]) for r in components[name][period]]
        for name in COMPONENTS
    ])
    rows0 = components[COMPONENTS[0]][period]
    actual = np.array([float(r["actual"]) for r in rows0])
    rw = np.array([float(r["rw"]) for r in rows0])
    return targets, P, actual, rw


def metrics(pred, actual, rw):
    pred=np.asarray(pred,float); actual=np.asarray(actual,float); rw=np.asarray(rw,float)
    ae=np.abs(pred-actual)
    ape=ae/np.maximum(np.abs(actual),1e-12)*100
    return {
        "n": int(len(actual)),
        "mae": float(np.mean(ae)),
        "mape_pct": float(np.mean(ape)),
        "rmse": float(np.sqrt(np.mean((pred-actual)**2))),
        "median_ae": float(np.median(ae)),
        "median_ape_pct": float(np.median(ape)),
        "worst_ape_pct": float(np.max(ape)),
        "direction_accuracy_pct": float(np.mean(np.sign(pred-rw)==np.sign(actual-rw))*100),
        "monthly_win_rate_vs_rw": float(np.mean(ae<np.abs(rw-actual))),
        "relative_mae_vs_rw": float(np.mean(ae)/np.mean(np.abs(rw-actual))),
    }


def equal_weights(m):
    return np.ones(m)/m


def performance_weights(P, actual):
    mae=np.mean(np.abs(P-actual[:,None]),axis=0)
    inv=1/np.maximum(mae,1e-12)
    return inv/inv.sum()


def optimized_weights(P, actual):
    m=P.shape[1]
    u=equal_weights(m)
    def obj(w):
        pred=P@w
        return float(np.mean(np.abs(pred-actual)/np.maximum(np.abs(actual),1e-12))*100)
    res=minimize(
        obj,u,method="SLSQP",
        bounds=[(0.0,1.0)]*m,
        constraints={"type":"eq","fun":lambda w: float(np.sum(w)-1.0)},
        options={"maxiter":1000,"ftol":1e-12},
    )
    if not res.success:
        raise RuntimeError(f"OPTIMIZER_FAIL {res.message}")
    w=np.clip(np.asarray(res.x,float),0,1)
    w=w/w.sum()
    return w,float(res.fun)


def prequential(P,actual,mode):
    m=P.shape[1]
    preds=[]; hist=[]
    for t in range(len(actual)):
        if mode=="EQUAL" or t<MIN_META_HISTORY:
            w=equal_weights(m)
            trained_on=0 if mode=="EQUAL" else t
        elif mode=="PERFORMANCE":
            w=performance_weights(P[:t],actual[:t]); trained_on=t
        elif mode=="OPTIMIZED":
            w,_=optimized_weights(P[:t],actual[:t]); trained_on=t
        else:
            raise ValueError(mode)
        preds.append(float(P[t]@w))
        hist.append({
            "target_index":t,
            "trained_on_prior_dev_origins":int(trained_on),
            "weights":{n:float(x) for n,x in zip(COMPONENTS,w)},
        })
    return np.array(preds),hist


def rows_from_predictions(targets,pred,actual,rw,weight_history=None):
    rows=[]
    for i,t in enumerate(targets):
        row={
            "target":t,
            "forecast":float(pred[i]),
            "actual":float(actual[i]),
            "rw":float(rw[i]),
        }
        if weight_history is not None:
            row["weight_state"]=weight_history[i]
        rows.append(row)
    return rows


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",default="ensemble_artifacts")
    args=ap.parse_args()

    root=Path(args.artifact_root)
    components=load_components(root)

    td,Pd,ad,rwd=aligned_matrix(components,"dev")
    t25,P25,a25,rw25=aligned_matrix(components,"transport_2025")
    t26,P26,a26,rw26=aligned_matrix(components,"stress_2026")

    component_dev={}
    for j,name in enumerate(COMPONENTS):
        component_dev[name]=metrics(Pd[:,j],ad,rwd)

    variants={}

    # 1) fixed simple average benchmark.
    peq,heq=prequential(Pd,ad,"EQUAL")
    weq=equal_weights(len(COMPONENTS))
    variants["SIMPLE_AVERAGE"]={
        "dev":{"metrics":metrics(peq,ad,rwd),"rows":rows_from_predictions(td,peq,ad,rwd,heq)},
        "final_weights":{n:float(x) for n,x in zip(COMPONENTS,weq)},
        "transport_2025":{"metrics":metrics(P25@weq,a25,rw25),
                          "rows":rows_from_predictions(t25,P25@weq,a25,rw25)},
        "stress_2026":{"metrics":metrics(P26@weq,a26,rw26),
                       "rows":rows_from_predictions(t26,P26@weq,a26,rw26)},
    }

    # 2) expanding prior-DEV inverse-MAE weights; freeze all-DEV weights externally.
    pp,hp=prequential(Pd,ad,"PERFORMANCE")
    wp=performance_weights(Pd,ad)
    variants["PERFORMANCE_WEIGHTED"]={
        "dev":{"metrics":metrics(pp,ad,rwd),"rows":rows_from_predictions(td,pp,ad,rwd,hp)},
        "final_weights":{n:float(x) for n,x in zip(COMPONENTS,wp)},
        "transport_2025":{"metrics":metrics(P25@wp,a25,rw25),
                          "rows":rows_from_predictions(t25,P25@wp,a25,rw25)},
        "stress_2026":{"metrics":metrics(P26@wp,a26,rw26),
                       "rows":rows_from_predictions(t26,P26@wp,a26,rw26)},
    }

    # 3) expanding prior-DEV constrained optimized weights; freeze all-DEV optimum externally.
    po,ho=prequential(Pd,ad,"OPTIMIZED")
    wo,insample_obj=optimized_weights(Pd,ad)
    variants["OPTIMIZED_SIMPLEX"]={
        "dev":{"metrics":metrics(po,ad,rwd),"rows":rows_from_predictions(td,po,ad,rwd,ho)},
        "final_weights":{n:float(x) for n,x in zip(COMPONENTS,wo)},
        "full_dev_fit_objective_pct":float(insample_obj),
        "full_dev_fit_metrics_not_selection_evidence":metrics(Pd@wo,ad,rwd),
        "transport_2025":{"metrics":metrics(P25@wo,a25,rw25),
                          "rows":rows_from_predictions(t25,P25@wo,a25,rw25)},
        "stress_2026":{"metrics":metrics(P26@wo,a26,rw26),
                       "rows":rows_from_predictions(t26,P26@wo,a26,rw26)},
    }

    # integrity gates
    for key,v in variants.items():
        w=np.array(list(v["final_weights"].values()))
        if np.any(w < -1e-10) or abs(w.sum()-1)>1e-8:
            raise RuntimeError(f"WEIGHT_CONSTRAINT_FAIL {key}")

    out={
        "batch_id":"VW_MIDAS_ANN_STAGE4_BATCH41_V1",
        "elm_ensemble_recovery":{
            "status":"NOT_FOUND",
            "finding":"Original ELM ledger and current repo contain no verifiable prediction-level ELM ensemble component set, weight vector, or ensemble result. ANN Stage 4 is therefore documented as a new ANN ensemble stage, not exact ELM ensemble parity."
        },
        "component_pool":{
            "names":COMPONENTS,
            "selection_basis":"frozen Stage 2/3 DEV-only role set: baseline, price leader, direction leader, complementarity hybrid benchmark, price refinement, price+direction refinement, balanced/stability hybrid",
            "component_dev_metrics":component_dev,
        },
        "ensemble_protocol":{
            "meta_evaluation":"chronological expanding DEV prequential",
            "minimum_prior_dev_origins_before_learned_weights":MIN_META_HISTORY,
            "early_dev_fallback":"equal weights",
            "performance_weighted":"inverse prior-DEV MAE, normalized non-negative",
            "optimized_simplex":"SLSQP minimize prior-DEV MAPE; weights non-negative and sum to one",
            "external_weights":"fit/freeze using all DEV only, then applied unchanged to 2025 and 2026",
            "2025_used_for_weight_learning":False,
            "2026_used_for_weight_learning":False,
            "random_split":"NONE",
            "database_access":"NONE_ARTIFACT_ONLY",
        },
        "variants":variants,
    }

    Path("vw_midas_ann_stage4_batch41_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        k:{
            "dev":v["dev"]["metrics"],
            "final_weights":v["final_weights"],
            "transport_2025":v["transport_2025"]["metrics"],
            "stress_2026":v["stress_2026"]["metrics"],
        } for k,v in variants.items()
    },sort_keys=True))


if __name__=="__main__":
    main()
