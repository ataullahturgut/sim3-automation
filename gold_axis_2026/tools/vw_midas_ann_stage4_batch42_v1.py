from __future__ import annotations

import argparse, json
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

FULL_POOL = ["VANILLA","MPA","SCA","DE_ABC","ADAPTIVE_TLBO","TLBO_TUNED_PSO","MPA_SCA"]
REDUCED_POOL = ["VANILLA","MPA","SCA","DE_ABC"]
LAMBDAS = [0.1,0.3,1.0,3.0,10.0,30.0,100.0]
MIN_META_HISTORY = 6

def load_json(root,run,filename):
    p=Path(root)/run/filename
    if not p.exists(): raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding="utf-8"))

def load_components(root):
    out={}
    r=load_json(root,RUNS["BATCH1"],"vw_midas_shallow_mlp_v1_result.json")
    out["VANILLA"]={p:r[p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r=load_json(root,RUNS["BATCH2"],"vw_midas_ann_meta_batch_2_v1_result.json")
    out["MPA"]={p:r["models"]["MPA"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r=load_json(root,RUNS["BATCH5"],"vw_midas_ann_meta_batch_5_v1_result.json")
    out["SCA"]={p:r["models"]["SCA"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r=load_json(root,RUNS["BATCH8"],"vw_midas_ann_meta_batch_8_v1_result.json")
    out["DE_ABC"]={p:r["models"]["DE_ABC"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r=load_json(root,RUNS["STAGE31"],"vw_midas_ann_stage3_batch31_v1_result.json")
    out["ADAPTIVE_TLBO"]={p:r["models"]["ADAPTIVE_TLBO"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r=load_json(root,RUNS["STAGE32"],"vw_midas_ann_stage3_batch32_v1_result.json")
    out["TLBO_TUNED_PSO"]={p:r["models"]["TLBO_TUNED_PSO"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}

    r=load_json(root,RUNS["STAGE34"],"vw_midas_ann_stage3_batch34_v1_result.json")
    out["MPA_SCA"]={p:r["models"]["MPA_SCA"][p]["rows"] for p in ("dev","transport_2025","stress_2026")}
    return out

def aligned(components,names,period):
    targets=[r["target"] for r in components[names[0]][period]]
    for n in names:
        if [r["target"] for r in components[n][period]]!=targets:
            raise RuntimeError(f"ALIGN_FAIL {n} {period}")
    P=np.column_stack([[float(r["forecast"]) for r in components[n][period]] for n in names])
    rows=components[names[0]][period]
    actual=np.array([float(r["actual"]) for r in rows])
    rw=np.array([float(r["rw"]) for r in rows])
    return targets,P,actual,rw

def metrics(pred,actual,rw):
    pred=np.asarray(pred,float); actual=np.asarray(actual,float); rw=np.asarray(rw,float)
    ae=np.abs(pred-actual); ape=ae/np.maximum(np.abs(actual),1e-12)*100
    return {
        "n":int(len(actual)),
        "mae":float(np.mean(ae)),
        "mape_pct":float(np.mean(ape)),
        "rmse":float(np.sqrt(np.mean((pred-actual)**2))),
        "median_ae":float(np.median(ae)),
        "median_ape_pct":float(np.median(ape)),
        "worst_ape_pct":float(np.max(ape)),
        "direction_accuracy_pct":float(np.mean(np.sign(pred-rw)==np.sign(actual-rw))*100),
        "monthly_win_rate_vs_rw":float(np.mean(ae<np.abs(rw-actual))),
        "relative_mae_vs_rw":float(np.mean(ae)/np.mean(np.abs(rw-actual))),
    }

def equal_w(m): return np.ones(m)/m

def fit_shrunk(P,y,lam):
    m=P.shape[1]; u=equal_w(m)
    scale=np.maximum(np.abs(y),1e-12)
    def obj(w):
        mape=float(np.mean(np.abs(P@w-y)/scale)*100)
        penalty=float(lam*np.mean((w-u)**2))
        return mape+penalty
    res=minimize(obj,u,method="SLSQP",
                 bounds=[(0,1)]*m,
                 constraints={"type":"eq","fun":lambda w:float(np.sum(w)-1)},
                 options={"maxiter":1000,"ftol":1e-12})
    if not res.success:
        raise RuntimeError(f"OPT_FAIL lam={lam} {res.message}")
    w=np.clip(np.asarray(res.x,float),0,1); w=w/w.sum()
    return w,float(res.fun)

def prequential_fixed_lambda(P,y,lam):
    m=P.shape[1]; preds=[]; hist=[]
    for t in range(len(y)):
        if t<MIN_META_HISTORY:
            w=equal_w(m); trained=0
        else:
            w,_=fit_shrunk(P[:t],y[:t],lam); trained=t
        preds.append(float(P[t]@w))
        hist.append({"index":t,"trained_on_prior_dev_origins":trained,
                     "lambda":lam,"weights":[float(x) for x in w]})
    return np.array(preds),hist

def rows(targets,pred,actual,rw,hist=None):
    out=[]
    for i,t in enumerate(targets):
        z={"target":t,"forecast":float(pred[i]),"actual":float(actual[i]),"rw":float(rw[i])}
        if hist is not None: z["weight_state"]=hist[i]
        out.append(z)
    return out

def evaluate_pool(components,names):
    td,Pd,ad,rwd=aligned(components,names,"dev")
    t25,P25,a25,rw25=aligned(components,names,"transport_2025")
    t26,P26,a26,rw26=aligned(components,names,"stress_2026")

    variants={}
    honest={}
    for lam in LAMBDAS:
        pred,hist=prequential_fixed_lambda(Pd,ad,lam)
        met=metrics(pred,ad,rwd)
        honest[str(lam)]={"metrics":met,"rows":rows(td,pred,ad,rwd,hist)}

    # DEV-only development selection of lambda; external weights are then fit on all DEV.
    chosen=min(LAMBDAS,key=lambda l: honest[str(l)]["metrics"]["mape_pct"])
    w,_=fit_shrunk(Pd,ad,chosen)

    pred_dev=np.array([r["forecast"] for r in honest[str(chosen)]["rows"]],float)
    variants["SHRUNK_SIMPLEX"]={
        "chosen_lambda_dev_only":float(chosen),
        "lambda_grid":LAMBDAS,
        "dev":honest[str(chosen)],
        "all_lambda_dev_metrics":{k:v["metrics"] for k,v in honest.items()},
        "final_weights":{n:float(x) for n,x in zip(names,w)},
        "full_dev_fit_metrics_not_honest_dev_evidence":metrics(Pd@w,ad,rwd),
        "transport_2025":{"metrics":metrics(P25@w,a25,rw25),"rows":rows(t25,P25@w,a25,rw25)},
        "stress_2026":{"metrics":metrics(P26@w,a26,rw26),"rows":rows(t26,P26@w,a26,rw26)},
    }

    # Equal benchmark for the exact same pool.
    u=equal_w(len(names))
    variants["SIMPLE_AVERAGE"]={
        "dev":{"metrics":metrics(Pd@u,ad,rwd),"rows":rows(td,Pd@u,ad,rwd)},
        "final_weights":{n:float(x) for n,x in zip(names,u)},
        "transport_2025":{"metrics":metrics(P25@u,a25,rw25),"rows":rows(t25,P25@u,a25,rw25)},
        "stress_2026":{"metrics":metrics(P26@u,a26,rw26),"rows":rows(t26,P26@u,a26,rw26)},
    }
    return variants

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",default="ensemble_artifacts")
    args=ap.parse_args()
    comp=load_components(args.artifact_root)

    full=evaluate_pool(comp,FULL_POOL)
    reduced=evaluate_pool(comp,REDUCED_POOL)

    # integrity
    for pool in (full,reduced):
        for k,v in pool.items():
            w=np.array(list(v["final_weights"].values()),float)
            assert np.min(w)>=-1e-10 and abs(float(w.sum())-1)<1e-8

    out={
        "batch_id":"VW_MIDAS_ANN_STAGE4_BATCH42_V1",
        "protocol":{
            "regularizer":"lambda * mean((w - equal_weight)^2)",
            "lambda_grid":LAMBDAS,
            "lambda_selection":"DEV-only among fixed predeclared lambdas using expanding prequential DEV MAPE",
            "minimum_prior_dev_origins":MIN_META_HISTORY,
            "weights":"non-negative, sum to one",
            "2025_used_for_selection":False,
            "2026_used_for_selection":False,
            "random_split":"NONE",
            "database_access":"NONE_ARTIFACT_ONLY",
            "subset_search":"NONE",
        },
        "pools":{
            "FULL7":{"components":FULL_POOL,"variants":full},
            "REDUCED4":{"components":REDUCED_POOL,
                        "selection_basis":"single predeclared role-diverse pool: baseline + price + direction + complementarity",
                        "variants":reduced},
        },
    }

    Path("vw_midas_ann_stage4_batch42_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        pool:{
            k:{
                "chosen_lambda":v.get("chosen_lambda_dev_only"),
                "dev":v["dev"]["metrics"],
                "final_weights":v["final_weights"],
                "transport_2025":v["transport_2025"]["metrics"],
                "stress_2026":v["stress_2026"]["metrics"],
            }
            for k,v in z["variants"].items()
        }
        for pool,z in out["pools"].items()
    },sort_keys=True))

if __name__=="__main__":
    main()
