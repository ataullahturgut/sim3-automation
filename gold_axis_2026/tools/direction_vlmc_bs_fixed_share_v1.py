#!/usr/bin/env python3
"""Adaptive Fixed-Share successor for source-faithful VLMC-BS experts.

Identity:
  DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH

The parent expert forecasts are frozen outputs of:
  DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH
"""

from __future__ import annotations
import argparse,csv,json,math
from pathlib import Path

EXPERTS=(26,52)
LOSS_TYPES=("ZERO_ONE","BRIER")
ETAS=(0.25,0.5,1.0,2.0,4.0)
ALPHAS=(0.0,0.01,0.02,0.05,0.10,0.20)

def read_parent(path:Path):
    with path.open(encoding="utf-8",newline="") as fh:
        rows=list(csv.DictReader(fh))
    out=[]
    for r in rows:
        k=int(r["k"])
        if k not in EXPERTS: continue
        out.append({
            "k":k,
            "target_week":r["target_week"],
            "p_up":float(r["p_up"]),
            "actual_up":int(r["actual_up"]),
        })
    return out

def common_rows(rows):
    by={}
    for r in rows:
        by.setdefault(r["target_week"],{})[r["k"]]=r
    out=[]
    for d in sorted(by):
        m=by[d]
        if all(k in m for k in EXPERTS):
            ys={m[k]["actual_up"] for k in EXPERTS}
            if len(ys)!=1: raise RuntimeError(f"ACTUAL_MISMATCH:{d}")
            out.append((d,m))
    return out

def expert_loss(p,y,kind):
    if kind=="ZERO_ONE":
        return 0.0 if (1 if p>=0.5 else 0)==y else 1.0
    if kind=="BRIER":
        return (p-y)**2
    raise ValueError(kind)

def run_sequence(common,loss_type,eta,alpha,weights=None):
    w=[0.5,0.5] if weights is None else [float(weights[0]),float(weights[1])]
    rows=[]
    for d,m in common:
        ps=[m[k]["p_up"] for k in EXPERTS]
        y=m[EXPERTS[0]]["actual_up"]
        p=sum(w[i]*ps[i] for i in range(2))
        rows.append({
            "target_week":d,
            "p_up":p,
            "forecast_up":1 if p>=0.5 else 0,
            "actual_up":y,
            "p26":ps[0],"p52":ps[1],
            "w26_before":w[0],"w52_before":w[1],
        })
        losses=[expert_loss(ps[i],y,loss_type) for i in range(2)]
        u=[w[i]*math.exp(-eta*losses[i]) for i in range(2)]
        z=sum(u)
        if not math.isfinite(z) or z<=0: raise RuntimeError("WEIGHT_NORMALIZATION_FAILURE")
        v=[x/z for x in u]
        w=[(1-alpha)*v[i]+alpha/2.0 for i in range(2)]
        rows[-1]["loss26"]=losses[0]; rows[-1]["loss52"]=losses[1]
        rows[-1]["w26_after"]=w[0]; rows[-1]["w52_after"]=w[1]
    return rows,w

def metrics(rows):
    n=len(rows)
    if not n:return {"n":0}
    au=sum(r["actual_up"] for r in rows); ad=n-au
    tp=sum(r["forecast_up"]==1 and r["actual_up"]==1 for r in rows)
    tn=sum(r["forecast_up"]==0 and r["actual_up"]==0 for r in rows)
    fp=sum(r["forecast_up"]==1 and r["actual_up"]==0 for r in rows)
    fn=sum(r["forecast_up"]==0 and r["actual_up"]==1 for r in rows)
    eps=1e-12
    bs=sum((r["p_up"]-r["actual_up"])**2 for r in rows)/n
    ll=-sum(r["actual_up"]*math.log(min(max(r["p_up"],eps),1-eps))+
            (1-r["actual_up"])*math.log(min(max(1-r["p_up"],eps),1-eps))
            for r in rows)/n
    return {
        "n":n,"accuracy":(tp+tn)/n,
        "balanced_accuracy":((tp/au)+(tn/ad))/2 if au and ad else None,
        "brier":bs,"log_loss":ll,
        "actual_up":au,"actual_down":ad,
        "forecast_up":tp+fp,"forecast_down":tn+fn,
        "up_sensitivity":tp/au if au else None,
        "down_sensitivity":tn/ad if ad else None,
        "tp":tp,"tn":tn,"fp":fp,"fn":fn,
        "always_up_accuracy":au/n,
        "mean_p_up":sum(r["p_up"] for r in rows)/n,
        "min_p_up":min(r["p_up"] for r in rows),
        "max_p_up":max(r["p_up"] for r in rows),
    }

def write_rows(path,rows):
    fields=["target_week","p_up","forecast_up","actual_up","p26","p52",
            "w26_before","w52_before","loss26","loss52","w26_after","w52_after"]
    with path.open("w",encoding="utf-8",newline="") as fh:
        wr=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n")
        wr.writeheader();wr.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--stage",choices=["pre2025","2025"],required=True)
    ap.add_argument("--pre2025-parent",type=Path,required=True)
    ap.add_argument("--parent-2025",type=Path)
    ap.add_argument("--state",type=Path)
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True)

    pre_common=common_rows(read_parent(a.pre2025_parent))
    dev=[x for x in pre_common if x[0].startswith("2023")]
    val=[x for x in pre_common if x[0].startswith("2024")]
    if len(dev)!=43 or len(val)!=53:
        raise RuntimeError(f"EXPECTED_43_53_COMMON_ROWS_GOT_{len(dev)}_{len(val)}")

    if a.stage=="pre2025":
        grid=[]
        for loss in LOSS_TYPES:
            for eta in ETAS:
                for alpha in ALPHAS:
                    rr,_=run_sequence(dev,loss,eta,alpha)
                    mm=metrics(rr)
                    grid.append({"loss_type":loss,"eta":eta,"alpha":alpha,**mm})
        # preregistered lexicographic rule
        grid.sort(key=lambda x:(-x["balanced_accuracy"],-x["accuracy"],x["brier"],x["eta"],x["alpha"],x["loss_type"]))
        best=grid[0]
        if not (best["loss_type"]=="ZERO_ONE" and best["eta"]==1.0 and best["alpha"]==0.05):
            raise RuntimeError(f"PREREG_SELECTION_MISMATCH:{best}")

        dev_rows,w_end23=run_sequence(dev,best["loss_type"],best["eta"],best["alpha"])
        val_rows,w_end24=run_sequence(val,best["loss_type"],best["eta"],best["alpha"],w_end23)

        with (a.outdir/"GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_GRID_2023_2026-09-18.csv").open("w",encoding="utf-8",newline="") as fh:
            fields=list(grid[0].keys());wr=csv.DictWriter(fh,fieldnames=fields,lineterminator="\n");wr.writeheader();wr.writerows(grid)
        write_rows(a.outdir/"GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_PRE2025_FORECASTS_2026-09-18.csv",dev_rows+val_rows)
        state={
            "identity":"DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH",
            "loss_type":best["loss_type"],"eta":best["eta"],"alpha":best["alpha"],
            "experts":list(EXPERTS),
            "end_2023_weights":{"26":w_end23[0],"52":w_end23[1]},
            "end_2024_weights":{"26":w_end24[0],"52":w_end24[1]},
            "development_2023":metrics(dev_rows),
            "validation_2024":metrics(val_rows),
        }
        (a.outdir/"GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_PRE2025_STATE_2026-09-18.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(state,indent=2))

    else:
        if a.parent_2025 is None or a.state is None: raise RuntimeError("2025_REQUIRES_PARENT_AND_STATE")
        state=json.loads(a.state.read_text(encoding="utf-8"))
        if (state["loss_type"],float(state["eta"]),float(state["alpha"])) != ("ZERO_ONE",1.0,0.05):
            raise RuntimeError("FROZEN_STATE_PARAMETER_MISMATCH")
        y25_common=common_rows(read_parent(a.parent_2025))
        if len(y25_common)!=52: raise RuntimeError(f"EXPECTED_52_2025_ROWS_GOT_{len(y25_common)}")
        w0=[state["end_2024_weights"]["26"],state["end_2024_weights"]["52"]]
        rows,w_end=run_sequence(y25_common,state["loss_type"],state["eta"],state["alpha"],w0)
        write_rows(a.outdir/"GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_2025_FORECASTS_2026-09-18.csv",rows)
        result={
            "identity":"DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH",
            "frozen_parameters":{"loss_type":state["loss_type"],"eta":state["eta"],"alpha":state["alpha"]},
            "start_2025_weights":{"26":w0[0],"52":w0[1]},
            "end_2025_weights":{"26":w_end[0],"52":w_end[1]},
            "metrics_2025":metrics(rows),
        }
        (a.outdir/"GOLD_CONTROL_DIRECTION_VLMC_BS_FIXED_SHARE_V1_2025_RESULT_2026-09-18.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
