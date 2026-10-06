from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
BASE_PATH=AX/"tools"/"gold_session_nova_a0_core3_raw_replay_v1_20261006.py"
OUT=AX/"SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_OUT"; OUT.mkdir(exist_ok=True)

spec=importlib.util.spec_from_file_location("nova_a0_raw",BASE_PATH)
base=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(base)

CORE3=list(base.CORE3)
BLOCK=5
RECENT_N=252
SEED=20261006

def global_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))
    ])

def recent_model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,class_weight="balanced",random_state=SEED))
    ])

def metrics(y,p):
    y=np.asarray(y,int); p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
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
        "prediction_std":float(np.std(p))
    }

def replay_window(g):
    g=g.sort_values("start_utc").reset_index(drop=True)
    test=g[g["start_utc"].dt.year.isin([2023,2024])].copy()
    rows=[]
    for bs in range(0,len(test),BLOCK):
        te=test.iloc[bs:bs+BLOCK].copy()
        if te.empty: continue
        first_start=te["start_utc"].min()
        tr=g[
            (g["end_utc"]<=first_start)
            & (g["start_utc"]<first_start)
            & (g["start_utc"].dt.year.isin([2023,2024]))
        ].copy()
        if len(tr)<RECENT_N:
            continue

        Xg=tr[CORE3].astype(float)
        Xte=te[CORE3].astype(float)
        yg=tr["y_up"].to_numpy(int)

        mg=global_model(); mg.fit(Xg,yg)
        p0=mg.predict_proba(Xte)[:,1]

        rr=tr.tail(RECENT_N).copy()
        mr=recent_model(); mr.fit(rr[CORE3].astype(float),rr["y_up"].to_numpy(int))
        pr=mr.predict_proba(Xte)[:,1]

        p1=.75*p0+.25*pr

        for r,pp0,ppr,pp1 in zip(te.itertuples(index=False),p0,pr,p1):
            rows.append({
                "label_date":r.label_date,
                "partition":r.partition,
                "window":r.window,
                "start_utc":r.start_utc.isoformat(),
                "end_utc":r.end_utc.isoformat(),
                "feature_obs_date":pd.Timestamp(r.obs_date).date().isoformat(),
                "daily_age_days":int(r.daily_age_days),
                "year":int(r.start_utc.year),
                "y_up":int(r.y_up),
                "direction":r.direction,
                "p_A0_global":float(pp0),
                "p_recent252":float(ppr),
                "p_A1_arcr":float(pp1),
                "pred_A0":"UP" if pp0>=.5 else "DOWN",
                "pred_A1":"UP" if pp1>=.5 else "DOWN",
                "train_n":int(len(tr))
            })
    return pd.DataFrame(rows)

def main():
    metals,annual_hashes=base.load_raw_metals()
    targets=base.verify_v5_targets()
    targets=targets[pd.to_datetime(targets["label_date"]).dt.year.isin([2023,2024])].copy()
    panel=base.align_daily_features(targets,metals)
    panel=panel.dropna(subset=CORE3+["direction","obs_date"]).copy()

    preds=[]
    for (part,win),g in panel.groupby(["partition","window"],sort=True):
        z=replay_window(g)
        if not z.empty: preds.append(z)
    pred=pd.concat(preds,ignore_index=True) if preds else pd.DataFrame()

    rows=[]
    for (part,win,yr),g in pred.groupby(["partition","window","year"],sort=True):
        m0=metrics(g["y_up"],g["p_A0_global"]); m1=metrics(g["y_up"],g["p_A1_arcr"])
        rows.append({
            "partition":part,"window":win,"period":str(yr),
            **{f"A0_{k}":v for k,v in m0.items()},
            **{f"A1_{k}":v for k,v in m1.items()},
            "delta_accuracy":m1["accuracy"]-m0["accuracy"],
            "delta_balanced_accuracy":m1["balanced_accuracy"]-m0["balanced_accuracy"],
            "delta_brier":m1["brier"]-m0["brier"],
        })
    for (part,win),g in pred.groupby(["partition","window"],sort=True):
        m0=metrics(g["y_up"],g["p_A0_global"]); m1=metrics(g["y_up"],g["p_A1_arcr"])
        rows.append({
            "partition":part,"window":win,"period":"2023-2024_SCORED",
            **{f"A0_{k}":v for k,v in m0.items()},
            **{f"A1_{k}":v for k,v in m1.items()},
            "delta_accuracy":m1["accuracy"]-m0["accuracy"],
            "delta_balanced_accuracy":m1["balanced_accuracy"]-m0["balanced_accuracy"],
            "delta_brier":m1["brier"]-m0["brier"],
        })
    mdf=pd.DataFrame(rows)

    pred.to_csv(OUT/"nova_a1_arcr_raw_predictions_2023_2024.csv",index=False)
    mdf.to_csv(OUT/"nova_a1_arcr_raw_metrics_2023_2024.csv",index=False)

    summary={
        "status":"NOVA_A1_ARCR_RAW_SESSION_REPLAY_V1_COMPLETE",
        "model_role":"STAGE1_PRIMARY_DIRECTION_ENGINE",
        "model":"NOVA A1 / ARCR = 0.75 global CORE3 + 0.25 recent252 balanced CORE3",
        "raw_daily_source":{
            "repo":base.STAK_REPO,"ref":base.STAK_REF,
            "annual_payload_sha256":annual_hashes,
            "feature_rows":int(len(metals))
        },
        "daily_source_ready_rule":"Strictly earlier America/New_York calendar-date observation only; same-day daily metal labels prohibited.",
        "target_reproduction":"PASS",
        "development_scope":"2023-2024 only; 2025 unopened",
        "training":{"block":BLOCK,"recent_n":RECENT_N,"features":CORE3},
        "metrics":mdf.to_dict("records"),
        "guardrails":[
            "No A0 prediction file used as A1 input; A0 comparator regenerated in the same raw replay.",
            "No readiness feature panel used.",
            "Only matured same-window targets used.",
            "2025 and 2026 unopened."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# NOVA A1 / ARCR — RAW SESSION REPLAY V1","",
        "**Status:** completed from raw daily metals + raw 15m targets.","",
        "- A1 = 0.75 global CORE3 + 0.25 recent252 balanced CORE3",
        "- A0 comparator regenerated on identical A1-scored rows",
        "- 2023–2024 only; 2025 unopened","",
        "## Matched metrics","",
        "| Partition | Window | Period | N | A0 Acc | A1 Acc | A0 Bal | A1 Bal | ΔAcc | ΔBal | A0 Brier | A1 Brier |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for r in mdf.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {r.period} | {int(r.A1_n)} | "
            f"{100*r.A0_accuracy:.2f}% | {100*r.A1_accuracy:.2f}% | "
            f"{100*r.A0_balanced_accuracy:.2f}% | {100*r.A1_balanced_accuracy:.2f}% | "
            f"{100*r.delta_accuracy:+.2f} pp | {100*r.delta_balanced_accuracy:+.2f} pp | "
            f"{r.A0_brier:.4f} | {r.A1_brier:.4f} |"
        )
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":
    main()
