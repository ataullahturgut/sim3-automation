from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np

RUNS = {
    "BATCH1": "36127630549",
    "BATCH2": "36128225062",
    "BATCH5": "36129458713",
    "BATCH8": "36130538857",
    "STAGE31": "36132219383",
    "STAGE32": "36132859342",
    "STAGE34": "36134549789",
}

FULL7 = ["VANILLA","MPA","SCA","DE_ABC","ADAPTIVE_TLBO","TLBO_TUNED_PSO","MPA_SCA"]
REDUCED4 = ["VANILLA","MPA","SCA","DE_ABC"]

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

def aligned(comp,names,period="dev"):
    targets=[r["target"] for r in comp[names[0]][period]]
    for n in names:
        if [r["target"] for r in comp[n][period]] != targets:
            raise RuntimeError(f"ALIGN_FAIL {n} {period}")
    P=np.column_stack([[float(r["forecast"]) for r in comp[n][period]] for n in names])
    rows=comp[names[0]][period]
    actual=np.array([float(r["actual"]) for r in rows],float)
    rw=np.array([float(r["rw"]) for r in rows],float)
    return targets,P,actual,rw

def met(pred,actual,rw):
    pred=np.asarray(pred,float); actual=np.asarray(actual,float); rw=np.asarray(rw,float)
    ae=np.abs(pred-actual); ape=ae/np.maximum(np.abs(actual),1e-12)*100
    return {
        "n":int(len(actual)),
        "mae":float(np.mean(ae)),
        "mape_pct":float(np.mean(ape)),
        "rmse":float(np.sqrt(np.mean((pred-actual)**2))),
        "median_ape_pct":float(np.median(ape)),
        "worst_ape_pct":float(np.max(ape)),
        "direction_accuracy_pct":float(np.mean(np.sign(pred-rw)==np.sign(actual-rw))*100),
        "monthly_win_rate_vs_rw":float(np.mean(ae<np.abs(rw-actual))),
        "relative_mae_vs_rw":float(np.mean(ae)/np.mean(np.abs(rw-actual))),
    }

def eq_pred(P): return np.mean(P,axis=1)

def yearly(targets,pred,actual,rw):
    out={}
    years=sorted(set(t[:4] for t in targets))
    for y in years:
        idx=np.array([t.startswith(y) for t in targets])
        out[y]=met(pred[idx],actual[idx],rw[idx])
    return out

def leave_one_origin(targets,pred,actual,rw):
    vals=[]
    n=len(targets)
    for i,t in enumerate(targets):
        keep=np.ones(n,dtype=bool); keep[i]=False
        m=met(pred[keep],actual[keep],rw[keep])
        vals.append({"left_out":t,"mape_pct":m["mape_pct"],"direction_accuracy_pct":m["direction_accuracy_pct"]})
    mape=np.array([x["mape_pct"] for x in vals])
    dire=np.array([x["direction_accuracy_pct"] for x in vals])
    return {
        "min_mape_pct":float(mape.min()),
        "max_mape_pct":float(mape.max()),
        "range_mape_pct":float(mape.max()-mape.min()),
        "mean_mape_pct":float(mape.mean()),
        "min_direction_pct":float(dire.min()),
        "max_direction_pct":float(dire.max()),
        "rows":vals,
    }

def paired_vs(pred,ref,actual):
    ape=np.abs(pred-actual)/np.maximum(np.abs(actual),1e-12)*100
    rpe=np.abs(ref-actual)/np.maximum(np.abs(actual),1e-12)*100
    delta=ape-rpe
    return {
        "ensemble_better_origins":int(np.sum(delta<0)),
        "tie_origins":int(np.sum(np.isclose(delta,0,atol=1e-12))),
        "ensemble_worse_origins":int(np.sum(delta>0)),
        "mean_delta_ape_pct_points":float(np.mean(delta)),
        "median_delta_ape_pct_points":float(np.median(delta)),
        "max_improvement_pct_points":float(-np.min(delta)),
        "max_deterioration_pct_points":float(np.max(delta)),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact-root",default="ensemble_artifacts")
    args=ap.parse_args()
    comp=load_components(args.artifact_root)

    td,P7,a,rw=aligned(comp,FULL7,"dev")
    _,P4,a4,rw4=aligned(comp,REDUCED4,"dev")
    assert np.allclose(a,a4) and np.allclose(rw,rw4)

    p7=eq_pred(P7)
    p4=eq_pred(P4)

    # references
    p_van=np.array([float(r["forecast"]) for r in comp["VANILLA"]["dev"]])
    p_mpa=np.array([float(r["forecast"]) for r in comp["MPA"]["dev"]])

    # deterministic leave-one-component-out audit of FULL7.
    loco={}
    base_m=met(p7,a,rw)
    for j,name in enumerate(FULL7):
        keep=[k for k in range(len(FULL7)) if k!=j]
        p=np.mean(P7[:,keep],axis=1)
        mm=met(p,a,rw)
        loco[name]={
            "dev_metrics":mm,
            "delta_mape_vs_full7_pct_points":float(mm["mape_pct"]-base_m["mape_pct"]),
            "delta_direction_vs_full7_pct_points":float(mm["direction_accuracy_pct"]-base_m["direction_accuracy_pct"]),
        }

    # external reporting only, same frozen equal-weight rules.
    t25,P7_25,a25,rw25=aligned(comp,FULL7,"transport_2025")
    _,P4_25,_,_=aligned(comp,REDUCED4,"transport_2025")
    t26,P7_26,a26,rw26=aligned(comp,FULL7,"stress_2026")
    _,P4_26,_,_=aligned(comp,REDUCED4,"stress_2026")

    out={
        "batch_id":"VW_MIDAS_ANN_STAGE4_FREEZE_AUDIT_V1",
        "authority":{
            "purpose":"robustness_and_freeze_only_not_new_model_search",
            "selection_period":"DEV_2022-04_to_2024-12",
            "2025_used_for_selection":False,
            "2026_used_for_selection":False,
            "random_split":"NONE",
            "database_access":"NONE_ARTIFACT_ONLY",
            "component_removal_policy":"diagnostic_only_not_subset_selection",
        },
        "full7":{
            "components":FULL7,
            "dev_metrics":base_m,
            "yearly_dev":yearly(td,p7,a,rw),
            "leave_one_origin":leave_one_origin(td,p7,a,rw),
            "paired_vs_vanilla":paired_vs(p7,p_van,a),
            "paired_vs_mpa":paired_vs(p7,p_mpa,a),
            "leave_one_component_out_diagnostic":loco,
            "transport_2025_reporting_only":met(eq_pred(P7_25),a25,rw25),
            "stress_2026_reporting_only":met(eq_pred(P7_26),a26,rw26),
        },
        "reduced4":{
            "components":REDUCED4,
            "dev_metrics":met(p4,a,rw),
            "yearly_dev":yearly(td,p4,a,rw),
            "leave_one_origin":leave_one_origin(td,p4,a,rw),
            "paired_vs_vanilla":paired_vs(p4,p_van,a),
            "paired_vs_mpa":paired_vs(p4,p_mpa,a),
            "transport_2025_reporting_only":met(eq_pred(P4_25),a25,rw25),
            "stress_2026_reporting_only":met(eq_pred(P4_26),a26,rw26),
        },
    }

    Path("vw_midas_ann_stage4_freeze_audit_v1_result.json").write_text(
        json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "FULL7":{
            "dev":out["full7"]["dev_metrics"],
            "yearly_dev":out["full7"]["yearly_dev"],
            "leave_one_origin":{k:v for k,v in out["full7"]["leave_one_origin"].items() if k!="rows"},
            "paired_vs_vanilla":out["full7"]["paired_vs_vanilla"],
            "paired_vs_mpa":out["full7"]["paired_vs_mpa"],
            "leave_one_component_out":loco,
        },
        "REDUCED4":{
            "dev":out["reduced4"]["dev_metrics"],
            "yearly_dev":out["reduced4"]["yearly_dev"],
            "leave_one_origin":{k:v for k,v in out["reduced4"]["leave_one_origin"].items() if k!="rows"},
            "paired_vs_vanilla":out["reduced4"]["paired_vs_vanilla"],
            "paired_vs_mpa":out["reduced4"]["paired_vs_mpa"],
        }
    },sort_keys=True))

if __name__=="__main__":
    main()
