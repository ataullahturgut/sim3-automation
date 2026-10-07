from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_SELECTED_INCREMENTAL_DISAGREEMENT_V1_OUT";OUT.mkdir(exist_ok=True)

BASES=AX/"GOLD_SESSION_INCREMENTAL_DISAGREEMENT_V1_BASES_2026-10-07.csv"

SELECTED_SOURCES=[
    ("SESSION_MODEL03B_A1_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"SELECTED_A1_ARCR":"A1"}),
    ("SESSION_MODEL04B_PATH_GLOBAL_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"SELECTED_PATH_GLOBAL":"PATH"}),
    ("SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"S14_A1_PLUS_1H_SELECTED_BLOCK":"STRUCTURAL"}),
    ("SESSION_MODEL06B_SAGE_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"S15_SESSION_ONLY_SELECTED_BLOCK":"SAGE_SESSION"}),
    ("SESSION_MODEL07B_SAGE_PATH_SESSION_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"SELECTED_PATH_SESSION":"SAGE_PATH"}),
    ("SESSION_MODEL08B_SAGE_A1_SESSION_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"SELECTED_A1_SESSION":"SAGE_A1"}),
    ("SESSION_MODEL09B_SAGE_A1_PATH_SESSION_FEATURE_SELECTION_OUT/dev_predictions.csv",
     {"SELECTED_A1_PATH_SESSION":"SAGE_A1_PATH"}),
]

def metrics(g,pcol):
    y=g.y_up.astype(int).to_numpy()
    p=g[pcol].astype(float).to_numpy()
    d=(p>=.5).astype(int)
    return dict(
        n=int(len(g)),
        accuracy=float(np.mean(d==y)),
        balanced_accuracy=float(balanced_accuracy_score(y,d)),
        brier=float(np.mean((p-y)**2)),
        up_recall=float(recall_score(y,d,pos_label=1,zero_division=0)),
        down_recall=float(recall_score(y,d,pos_label=0,zero_division=0)),
    )

def normalize(q):
    q=q.copy()
    q["start_utc"]=pd.to_datetime(q.start_utc,utc=True)
    if "end_utc" in q.columns:
        q["end_utc"]=pd.to_datetime(q.end_utc,utc=True)
    else:
        q["end_utc"]=pd.NaT
    q["year"]=q.start_utc.dt.year
    return q[q.year.isin([2023,2024])].copy()

def load_base_model(name):
    if name=="CORE3_A0":
        q=pd.read_csv(AX/"GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv")
        p="p_up"
    elif name=="NOVA_A1_ARCR":
        q=pd.read_csv(AX/"GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv")
        p="p_A1_arcr"
    elif name=="PATH_GLOBAL_1H":
        q=pd.read_csv(AX/"GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv")
        p="p_up"
    elif name=="STRUCTURAL_IRIS_1H":
        q=pd.read_csv(AX/"GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_PREDICTIONS_2026-10-07.csv")
        q=q[q.model.eq("S14_A1_PLUS_1H_FULL")].copy();p="p_up"
    elif name.startswith(("S15_","S16_","S17_","S18_")):
        q=pd.read_csv(AX/"GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_PREDICTIONS_2026-10-07.csv")
        q=q[q.model.eq(name)].copy();p="p_up"
    else:
        raise ValueError(name)
    q=normalize(q)
    return q[["partition","window","start_utc","year","y_up",p]].rename(columns={p:"p_base"})

def load_selected():
    parts=[]
    for rel,mapping in SELECTED_SOURCES:
        p=AX/rel
        if not p.exists():
            raise FileNotFoundError(p)
        q=normalize(pd.read_csv(p))
        for m,cluster in mapping.items():
            z=q[q.model.eq(m)].copy()
            if z.empty:
                raise RuntimeError(f"SELECTED_MODEL_MISSING:{m}:{p}")
            z=z[["partition","window","start_utc","year","y_up","p_up"]].copy()
            z["candidate_model"]=m
            z["candidate_cluster"]=cluster
            parts.append(z)
    return pd.concat(parts,ignore_index=True)

def main():
    bases=pd.read_csv(BASES)
    selected=load_selected()
    rows=[]
    for b in bases.itertuples(index=False):
        base=load_base_model(b.base_model)
        base=base[(base.partition.eq(b.partition))&(base.window.eq(b.window))].copy()
        candidates=selected[(selected.partition.eq(b.partition))&(selected.window.eq(b.window))]
        for (cand,cluster),cg in candidates.groupby(["candidate_model","candidate_cluster"],sort=True):
            z=base.merge(
                cg[["partition","window","start_utc","year","y_up","p_up"]],
                on=["partition","window","start_utc","year","y_up"],
                how="inner",validate="one_to_one"
            ).rename(columns={"p_up":"p_cand"})
            if z.empty: continue
            y=z.y_up.astype(int).to_numpy()
            bd=(z.p_base.to_numpy(float)>=.5).astype(int)
            cd=(z.p_cand.to_numpy(float)>=.5).astype(int)
            dis=bd!=cd
            rescue=dis&(bd!=y)&(cd==y)
            broken=dis&(bd==y)&(cd!=y)
            up=y==1;down=y==0
            bm=metrics(z,"p_base");cm=metrics(z,"p_cand")
            corr=float(np.corrcoef(z.p_base,z.p_cand)[0,1]) if len(z)>=2 and np.std(z.p_base)>0 and np.std(z.p_cand)>0 else np.nan
            rows.append({
                "partition":b.partition,"window":b.window,
                "base_model":b.base_model,"base_cluster":b.base_cluster,
                "candidate_model":cand,"candidate_cluster":cluster,
                "same_cluster":bool(b.base_cluster==cluster),
                "common_n":len(z),"disagreement_n":int(dis.sum()),
                "agreement_rate":float((~dis).mean()),
                "candidate_rescues":int(rescue.sum()),
                "candidate_breaks":int(broken.sum()),
                "net_rescue":int(rescue.sum()-broken.sum()),
                "candidate_win_on_disagreement":float(rescue.sum()/dis.sum()) if dis.sum() else np.nan,
                "up_rescues":int((rescue&up).sum()),
                "up_breaks":int((broken&up).sum()),
                "down_rescues":int((rescue&down).sum()),
                "down_breaks":int((broken&down).sum()),
                "base_ba":bm["balanced_accuracy"],"cand_ba":cm["balanced_accuracy"],
                "delta_ba":cm["balanced_accuracy"]-bm["balanced_accuracy"],
                "base_up":bm["up_recall"],"cand_up":cm["up_recall"],
                "delta_up":cm["up_recall"]-bm["up_recall"],
                "base_down":bm["down_recall"],"cand_down":cm["down_recall"],
                "delta_down":cm["down_recall"]-bm["down_recall"],
                "base_brier":bm["brier"],"cand_brier":cm["brier"],
                "delta_brier":cm["brier"]-bm["brier"],
                "probability_corr":corr,
            })
    out=pd.DataFrame(rows)
    out.to_csv(OUT/"selected_pairwise.csv",index=False)
    ranked=out.sort_values(["partition","window","net_rescue","candidate_win_on_disagreement","common_n"],
                           ascending=[True,True,False,False,False])
    ranked.to_csv(OUT/"selected_pairwise_ranked.csv",index=False)

    lines=[
        "# GOLD SESSION — SELECTED-VARIANT INCREMENTAL / DISAGREEMENT AUDIT","",
        "**Scope:** selected 2023–2024 development predictions only; balanced bases are frozen from canonical development audit.","",
        "| Partition | Window | Base | Selected candidate | Common N | Disagree N | Rescue | Break | Net | Win/disagree | ΔUP | ΔDOWN | Agreement | Corr | Same cluster |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for r in ranked.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {r.base_model} | {r.candidate_model} | "
            f"{r.common_n} | {r.disagreement_n} | {r.candidate_rescues} | {r.candidate_breaks} | "
            f"{r.net_rescue:+d} | {100*r.candidate_win_on_disagreement:.2f}% | "
            f"{100*r.delta_up:+.2f} pp | {100*r.delta_down:+.2f} pp | "
            f"{100*r.agreement_rate:.2f}% | {r.probability_corr:.3f} | {r.same_cluster} |"
        )
    lines += ["","No row is automatically admitted to consensus. Positive net rescue is only incremental development evidence; same-cluster candidates require especially strong justification to avoid duplicate voting."]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    summary={
        "status":"SELECTED_INCREMENTAL_DISAGREEMENT_AUDIT_COMPLETE",
        "years":[2023,2024],
        "uses_2025_for_membership":False,
        "pairs":out.to_dict("records"),
        "guardrails":[
            "Selected predictions are regenerated from their original frozen development scripts.",
            "Only dev_predictions.csv is consumed by this audit.",
            "Balanced bases are fixed from the canonical development-only audit.",
            "No final consensus membership is assigned here."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
