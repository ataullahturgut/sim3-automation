from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_helios_v2_out"))
OUT.mkdir(parents=True, exist_ok=True)

V1 = ROOT / "gold_axis_2026" / "GOLD_H3_HELIOS_V1_PREDICTIONS_2026-10-03.csv"

SEED = 20261003
REPS = 10000
BLOCKS = [5,10]


def metrics(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp),
    }


def build_v2():
    g=pd.read_csv(V1)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        g[c]=pd.to_datetime(g[c],errors="raise")
    g["p_helios_v2"]=g.p_aurora.astype(float)
    route=g.hard_route.astype(bool)
    base_up=g.p_aurora>=.5
    q=g.competence_q.astype(float)

    g.loc[route & base_up,"p_helios_v2"]=1.0-q[route & base_up]
    g.loc[route & (~base_up),"p_helios_v2"]=q[route & (~base_up)]
    return g


def score_periods(g):
    specs=[
        ("2023",g.year==2023),
        ("2024",g.year==2024),
        ("2025",g.year==2025),
        ("2026",g.year==2026),
        ("2023-2024",g.year.isin([2023,2024])),
        ("2025-2026",g.year.isin([2025,2026])),
    ]
    rows=[]
    for label,mask in specs:
        z=g[mask].copy()
        vals={
            "aurora":metrics(z.y_up,z.p_aurora),
            "v1_soft":metrics(z.y_up,z.p_helios_soft),
            "v1_hard":metrics(z.y_up,z.p_helios_hard),
            "v2":metrics(z.y_up,z.p_helios_v2),
            "opal":metrics(z.y_up,z.p_opal_raw),
        }
        rows.append({
            "period":label,
            **{f"{name}_{k}":v for name,m in vals.items() for k,v in m.items()}
        })
    return pd.DataFrame(rows)


def simulate_gate(base,window,enter_wins,exit_wins):
    g=base.copy().sort_values("forecast_issue_date").reset_index(drop=True)
    pending=[]; hist=[]; active=False
    p_out=[]; active_out=[]; switches=[]
    prev=False
    for r in g.itertuples(index=False):
        cutoff=pd.Timestamp(r.feature_cutoff_date)
        keep=[]
        for item in pending:
            if pd.Timestamp(item["end"])<=cutoff:
                hist.append(int(item["success"]))
            else:
                keep.append(item)
        pending=keep

        recent=hist[-window:]
        wins=sum(recent) if len(recent)>=window else 0
        if len(recent)>=window:
            if (not active) and wins>=enter_wins:
                active=True
            elif active and wins<=exit_wins:
                active=False
        if active!=prev:
            switches.append(str(pd.Timestamp(r.forecast_issue_date).date()))
            prev=active

        route=bool(active and r.candidate_reversal)
        q=(wins+1)/(window+2) if len(recent)>=window else .5
        pa=float(r.p_aurora)
        if route:
            p=(1-q) if pa>=.5 else q
        else:
            p=pa
        p_out.append(p); active_out.append(active)

        if bool(r.candidate_reversal):
            pending.append({"end":r.target_end_date_h3,"success":int(r.candidate_success)})

    g["p_sens"]=p_out
    g["gate_active_sens"]=active_out
    return g,switches


def sensitivity(g):
    rows=[]
    configs=[
        ("W6_4_2",6,4,2),
        ("W8_5_3_BINDING",8,5,3),
        ("W10_6_4",10,6,4),
    ]
    for name,w,en,ex in configs:
        s,sw=simulate_gate(g,w,en,ex)
        for label,mask in [
            ("2023-2024",s.year.isin([2023,2024])),
            ("2025",s.year==2025),
            ("2026",s.year==2026),
            ("2025-2026",s.year.isin([2025,2026])),
        ]:
            z=s[mask]
            m=metrics(z.y_up,z.p_sens)
            rows.append({
                "config":name,"period":label,
                "accuracy":m["accuracy"],"balanced_accuracy":m["balanced_accuracy"],
                "brier":m["brier"],"logloss":m["logloss"],
                "active_share":float(z.gate_active_sens.mean()),
                "switches":";".join(sw),
            })
    return pd.DataFrame(rows)


def logloss_row(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    y=np.asarray(y,int)
    return -(y*np.log(p)+(1-y)*np.log(1-p))


def paired_diff(y,cand,base):
    y=np.asarray(y,int); cand=np.asarray(cand,float); base=np.asarray(base,float)
    return {
        "accuracy":((cand>=.5).astype(int)==y).astype(float)-((base>=.5).astype(int)==y).astype(float),
        "brier":(cand-y)**2-(base-y)**2,
        "logloss":logloss_row(y,cand)-logloss_row(y,base),
    }


def circular_boot(diff,block_len,rng):
    diff=np.asarray(diff,float); n=len(diff); nb=int(np.ceil(n/block_len))
    vals=np.empty(REPS,float); offs=np.arange(block_len); batch=500
    for st in range(0,REPS,batch):
        m=min(batch,REPS-st)
        starts=rng.integers(0,n,size=(m,nb))
        idx=(starts[:,:,None]+offs[None,None,:])%n
        idx=idx.reshape(m,-1)[:,:n]
        vals[st:st+m]=diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows=[]; si=0
    comps={
        "AURORA":"p_aurora",
        "HELIOS_V1_SOFT":"p_helios_soft",
        "HELIOS_V1_HARD":"p_helios_hard",
        "OPAL_RAW":"p_opal_raw",
    }
    periods={
        "2023-2024":g.year.isin([2023,2024]),
        "2025-2026":g.year.isin([2025,2026]),
        "2026":g.year==2026,
    }
    for bname,bcol in comps.items():
        for per,mask in periods.items():
            z=g[mask]
            for metric,d in paired_diff(z.y_up,z.p_helios_v2,z[bcol]).items():
                for bl in BLOCKS:
                    si+=1
                    boot=circular_boot(d,bl,np.random.default_rng(SEED+si))
                    lo,hi=np.quantile(boot,[.025,.975])
                    improve=float(np.mean(boot>0)) if metric=="accuracy" else float(np.mean(boot<0))
                    rows.append({
                        "comparison":f"V2_vs_{bname}","period":per,"metric":metric,"block_len":bl,
                        "observed_diff":float(np.mean(d)),
                        "ci95_low":float(lo),"ci95_high":float(hi),
                        "bootstrap_improve_share":improve,"n":int(len(z))
                    })
    return pd.DataFrame(rows)


def main():
    g=build_v2()
    g.to_csv(OUT/"helios_v2_predictions.csv",index=False)

    met=score_periods(g)
    met.to_csv(OUT/"helios_v2_metrics.csv",index=False)

    sens=sensitivity(g)
    sens.to_csv(OUT/"helios_v2_gate_sensitivity.csv",index=False)

    inf=inference(g)
    inf.to_csv(OUT/"helios_v2_inference.csv",index=False)

    summary={
        "schema":"HELIOS_H3_V2",
        "status":"POSTHOC_STRENGTHENING_RESULT",
        "calibration":"posterior competence probability",
        "metrics":met.to_dict(orient="records"),
        "gate_sensitivity":sens.to_dict(orient="records"),
        "inference":inf.to_dict(orient="records"),
    }
    (OUT/"helios_v2_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# HELIOS-H3 V2 — POSTERIOR-CALIBRATED REGIME ROUTER RESULT","",
        "**Status:** **POSTHOC_STRENGTHENING_RESULT**  ",
        "**Binding routing:** identical to HELIOS V1; only routed probability calibration changes.  ","",
        "## Metrics","",
        "| Period | AURORA Acc | V1 Soft | V1 Hard | V2 Acc | Raw OPAL | AURORA Brier | V1 Soft Brier | V1 Hard Brier | V2 Brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in met.itertuples():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.v1_soft_accuracy:.2f}% | "
            f"{100*r.v1_hard_accuracy:.2f}% | {100*r.v2_accuracy:.2f}% | {100*r.opal_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.v1_soft_brier:.4f} | {r.v1_hard_brier:.4f} | {r.v2_brier:.4f} |"
        )

    lines += ["","## Gate sensitivity","",
              "| Config | Period | Acc | BA | Brier | Logloss | Active share | Switches |",
              "|---|---|---:|---:|---:|---:|---:|---|"]
    for r in sens.itertuples():
        lines.append(
            f"| {r.config} | {r.period} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
            f"{r.brier:.4f} | {r.logloss:.4f} | {100*r.active_share:.1f}% | {r.switches} |"
        )

    lines += ["","## Dependence-aware bootstrap",""]
    for r in inf.itertuples():
        scale=100 if r.metric=="accuracy" else 1
        unit=" pp" if r.metric=="accuracy" else ""
        lines.append(
            f"- {r.comparison} / {r.period} / {r.metric} / block{r.block_len}: "
            f"diff={scale*r.observed_diff:+.4f}{unit}; 95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
            f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
        )

    lines += ["","## Governance","",
              "V2 is a post-hoc strengthening study. Historical results cannot replace prospective proof. "
              "The frozen AURORA prospective champion remains unchanged until HELIOS is separately frozen and accumulates future origins."]

    (OUT/"HELIOS_V2_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"HELIOS_V2_RESULT.md").read_text())


if __name__=="__main__":
    main()
