from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, recall_score

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_INCREMENTAL_DISAGREEMENT_V1_OUT"
OUT.mkdir(exist_ok=True)

def metrics(g,pcol="p_up"):
    y=g["y_up"].astype(int).to_numpy()
    p=g[pcol].astype(float).to_numpy()
    d=(p>=0.5).astype(int)
    return dict(
        n=int(len(g)),
        accuracy=float(np.mean(d==y)),
        balanced_accuracy=float(balanced_accuracy_score(y,d)),
        brier=float(np.mean((p-y)**2)),
        up_recall=float(recall_score(y,d,pos_label=1,zero_division=0)),
        down_recall=float(recall_score(y,d,pos_label=0,zero_division=0)),
        up_actual=int((y==1).sum()),
        up_correct=int(((y==1)&(d==1)).sum()),
        down_actual=int((y==0).sum()),
        down_correct=int(((y==0)&(d==0)).sum()),
    )

def normalize(df):
    q=df.copy()
    q["start_utc"]=pd.to_datetime(q["start_utc"],utc=True)
    q["end_utc"]=pd.to_datetime(q["end_utc"],utc=True)
    q["year"]=q["start_utc"].dt.year
    q=q[q["year"].isin([2023,2024])].copy()
    return q

def add_long(parts,name,df,pcol,cluster):
    q=normalize(df)
    q=q[["partition","window","start_utc","end_utc","year","y_up",pcol]].copy()
    q=q.rename(columns={pcol:"p_up"})
    q["model"]=name
    q["cluster"]=cluster
    parts.append(q)

def load_models():
    parts=[]

    a0=pd.read_csv(AX/"GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv")
    add_long(parts,"CORE3_A0",a0,"p_up","CORE3")

    a1=pd.read_csv(AX/"GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv")
    add_long(parts,"NOVA_A1_ARCR",a1,"p_A1_arcr","A1")

    path=pd.read_csv(AX/"GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv")
    add_long(parts,"PATH_GLOBAL_1H",path,"p_up","PATH")

    s14=pd.read_csv(AX/"GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_PREDICTIONS_2026-10-07.csv")
    s14=s14[s14["model"].eq("S14_A1_PLUS_1H_FULL")].copy()
    add_long(parts,"STRUCTURAL_IRIS_1H",s14,"p_up","STRUCTURAL")

    sage=pd.read_csv(AX/"GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_PREDICTIONS_2026-10-07.csv")
    sage_names=[]
    for m in sorted(sage["model"].dropna().unique()):
        if "_MATCHED" in m:
            continue
        if m.startswith(("S15_","S16_","S17_","S18_")):
            z=sage[sage["model"].eq(m)].copy()
            cluster=(
                "SAGE_SESSION" if m.startswith("S15_") else
                "SAGE_PATH" if m.startswith("S16_") else
                "SAGE_A1" if m.startswith("S17_") else
                "SAGE_A1_PATH"
            )
            add_long(parts,m,z,"p_up",cluster)
            sage_names.append(m)

    long=pd.concat(parts,ignore_index=True)
    long=long.drop_duplicates(["model","partition","window","start_utc"],keep="last")
    return long,sage_names

def native_metrics(long):
    rows=[]
    for (model,cluster,part,win),g in long.groupby(["model","cluster","partition","window"],sort=True):
        m=metrics(g)
        rows.append({"model":model,"cluster":cluster,"partition":part,"window":win,**m})
    return pd.DataFrame(rows)

def select_bases(mdf):
    rows=[]
    for (part,win),g in mdf.groupby(["partition","window"],sort=True):
        eligible=g[
            (g["n"]>=80)&
            (g["up_recall"]>=0.30)&
            (g["down_recall"]>=0.30)
        ].copy()
        fallback=False
        if eligible.empty:
            eligible=g[g["n"]>=50].copy()
            fallback=True
        if eligible.empty:
            continue
        eligible=eligible.sort_values(
            ["balanced_accuracy","brier","n"],
            ascending=[False,True,False]
        )
        r=eligible.iloc[0]
        rows.append({
            "partition":part,"window":win,
            "base_model":r.model,"base_cluster":r.cluster,
            "base_native_n":int(r.n),
            "base_native_ba":float(r.balanced_accuracy),
            "base_native_up":float(r.up_recall),
            "base_native_down":float(r.down_recall),
            "base_native_brier":float(r.brier),
            "fallback_no_balanced_base":bool(fallback),
        })
    return pd.DataFrame(rows)

def pairwise(long,bases):
    out=[]
    key=["partition","window","start_utc","end_utc","year","y_up"]
    for b in bases.itertuples(index=False):
        base=long[
            (long.partition.eq(b.partition))&
            (long.window.eq(b.window))&
            (long.model.eq(b.base_model))
        ][key+["p_up","cluster"]].copy()
        base=base.rename(columns={"p_up":"p_base","cluster":"base_cluster_row"})
        candidates=long[
            (long.partition.eq(b.partition))&
            (long.window.eq(b.window))&
            (~long.model.eq(b.base_model))
        ]
        for (cand,ccluster),cg in candidates.groupby(["model","cluster"],sort=True):
            z=base.merge(
                cg[key+["p_up"]].rename(columns={"p_up":"p_cand"}),
                on=key,how="inner",validate="one_to_one"
            )
            if z.empty:
                continue
            y=z.y_up.astype(int).to_numpy()
            bd=(z.p_base.to_numpy(float)>=.5).astype(int)
            cd=(z.p_cand.to_numpy(float)>=.5).astype(int)
            disagree=bd!=cd
            rescue=disagree&(bd!=y)&(cd==y)
            broken=disagree&(bd==y)&(cd!=y)
            up=(y==1);down=(y==0)
            base_m=metrics(z.rename(columns={"p_base":"p_up"}))
            cand_m=metrics(z.rename(columns={"p_cand":"p_up"}))
            if len(z)>=2 and np.std(z.p_base)>0 and np.std(z.p_cand)>0:
                corr=float(np.corrcoef(z.p_base,z.p_cand)[0,1])
            else:
                corr=np.nan
            out.append({
                "partition":b.partition,"window":b.window,
                "base_model":b.base_model,"base_cluster":b.base_cluster,
                "candidate_model":cand,"candidate_cluster":ccluster,
                "same_cluster":bool(b.base_cluster==ccluster),
                "common_n":int(len(z)),
                "agreement_n":int((~disagree).sum()),
                "agreement_rate":float((~disagree).mean()),
                "disagreement_n":int(disagree.sum()),
                "candidate_rescues":int(rescue.sum()),
                "candidate_breaks":int(broken.sum()),
                "net_rescue":int(rescue.sum()-broken.sum()),
                "disagreement_candidate_win_rate":(
                    float(rescue.sum()/disagree.sum()) if disagree.sum() else np.nan
                ),
                "up_rescues":int((rescue&up).sum()),
                "up_breaks":int((broken&up).sum()),
                "down_rescues":int((rescue&down).sum()),
                "down_breaks":int((broken&down).sum()),
                "base_common_ba":base_m["balanced_accuracy"],
                "cand_common_ba":cand_m["balanced_accuracy"],
                "delta_ba":cand_m["balanced_accuracy"]-base_m["balanced_accuracy"],
                "base_common_up":base_m["up_recall"],
                "cand_common_up":cand_m["up_recall"],
                "delta_up_recall":cand_m["up_recall"]-base_m["up_recall"],
                "base_common_down":base_m["down_recall"],
                "cand_common_down":cand_m["down_recall"],
                "delta_down_recall":cand_m["down_recall"]-base_m["down_recall"],
                "base_common_brier":base_m["brier"],
                "cand_common_brier":cand_m["brier"],
                "delta_brier":cand_m["brier"]-base_m["brier"],
                "probability_corr":corr,
            })
    return pd.DataFrame(out)

def main():
    long,sage_names=load_models()
    nm=native_metrics(long)
    bases=select_bases(nm)
    pw=pairwise(long,bases)

    long.to_csv(OUT/"canonical_long_predictions.csv",index=False)
    nm.to_csv(OUT/"canonical_native_metrics.csv",index=False)
    bases.to_csv(OUT/"balanced_base_selection.csv",index=False)
    pw.to_csv(OUT/"pairwise_disagreement.csv",index=False)

    # Rank only as descriptive evidence, not membership selection.
    ranked=pw.sort_values(
        ["partition","window","net_rescue","disagreement_candidate_win_rate","common_n"],
        ascending=[True,True,False,False,False]
    ).copy()
    ranked.to_csv(OUT/"pairwise_ranked.csv",index=False)

    summary={
        "status":"CANONICAL_INCREMENTAL_DISAGREEMENT_AUDIT_COMPLETE",
        "years":[2023,2024],
        "sage_models":sage_names,
        "base_rule":"Within each session, best native development BA among canonical heads with N>=80 and both class recalls>=30%; exact-common rows are then used for every pairwise comparison.",
        "membership_rule":"No consensus membership is assigned by this audit.",
        "base_selection":bases.to_dict("records"),
        "guardrails":[
            "2025 and 2026 are not read.",
            "All rescue/break calculations use exact-common session rows.",
            "Probability threshold remains 0.50.",
            "Same-cluster/nested models are flagged, not double-counted.",
            "Selected-feature variants are not part of this first canonical audit and require a second replay/audit."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# GOLD SESSION — CANONICAL INCREMENTAL / DISAGREEMENT AUDIT",
        "",
        "**Scope:** 2023–2024 development only. No 2025/2026 outcomes read.",
        "",
        "## Balanced base selected per session",
        "",
        "| Partition | Window | Base | N | BA | UP | DOWN | Brier |",
        "|---|---|---|---:|---:|---:|---:|---:|"
    ]
    for r in bases.itertuples(index=False):
        lines.append(
            f"| {r.partition} | {r.window} | {r.base_model} | {r.base_native_n} | "
            f"{100*r.base_native_ba:.2f}% | {100*r.base_native_up:.2f}% | "
            f"{100*r.base_native_down:.2f}% | {r.base_native_brier:.4f} |"
        )

    lines += [
        "",
        "## Highest positive incremental candidates on exact-common rows",
        "",
        "| Partition | Window | Base | Candidate | Common N | Disagree N | Rescue | Break | Net | Cand win on disagreement | ΔUP | ΔDOWN | Agreement | Corr |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for (part,win),g in ranked.groupby(["partition","window"],sort=True):
        pos=g[g.net_rescue>0].head(4)
        if pos.empty:
            pos=g.head(2)
        for r in pos.itertuples(index=False):
            lines.append(
                f"| {part} | {win} | {r.base_model} | {r.candidate_model} | "
                f"{r.common_n} | {r.disagreement_n} | {r.candidate_rescues} | "
                f"{r.candidate_breaks} | {r.net_rescue:+d} | "
                f"{100*r.disagreement_candidate_win_rate:.2f}% | "
                f"{100*r.delta_up_recall:+.2f} pp | {100*r.delta_down_recall:+.2f} pp | "
                f"{100*r.agreement_rate:.2f}% | {r.probability_corr:.3f} |"
            )

    lines += [
        "",
        "## Interpretation guardrail",
        "",
        "Positive net rescue is evidence of incremental directional information on the common development rows, not automatic consensus membership. Selected-feature variants and correction specialists require their own second-stage audit before the role matrix can be fully frozen."
    ]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())

if __name__=="__main__":
    main()
