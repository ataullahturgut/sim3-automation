from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_GRID=AX/"GOLD_H3_RTE_V3_DEV_GRID_2026-10-03.csv"
OUT_BLOCKS=AX/"GOLD_H3_RTE_V3_BLOCK_METRICS_2026-10-03.csv"
OUT_SUM=AX/"GOLD_H3_RTE_V3_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_RTE_V3_RESULT_2026-10-03.md"

QS=[0.60,0.65,0.70]

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    for d in [p,f]:
        d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
        d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
    z=p.merge(f[["feature_cutoff_date","signed_opt_pressure"]],
              on="feature_cutoff_date",how="left",validate="one_to_one")
    return z.sort_values("forecast_issue_date").reset_index(drop=True)

def cand(q,th):
    return (q.p_rte>=th)&(q.p_inst>=0.50)&(q.signed_opt_pressure>0)

def stat(q,th):
    c=cand(q,th)
    y=q.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "q":th,"eligible_n":len(q),"candidate_n":n,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(n,1),"candidate_rate":n/max(len(q),1)
    }

def period(q,th):
    c=cand(q,th)
    y=q.y_up.astype(int).to_numpy()
    v=q.v5_pred.astype(int).to_numpy()
    a=np.where(c.to_numpy(),1-v,v)
    r=int((c.to_numpy()&(v!=y)&(a==y)).sum())
    b=int((c.to_numpy()&(v==y)&(a!=y)).sum())
    return {
        "eligible_n":len(q),"candidate_n":int(c.sum()),
        "candidate_rate":float(c.mean()) if len(q) else np.nan,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(r+b,1),
        "v5_accuracy":float((v==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((a==y).mean()) if len(q) else np.nan,
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))&c).sum())
    }

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def block_masks(z):
    d=z.forecast_issue_date
    return {
        "2024_H1":(z.year==2024)&(d.dt.month<=6),
        "2024_H2":(z.year==2024)&(d.dt.month>=7),
        "2025_H1":(z.year==2025)&(d.dt.month<=6),
        "2025_H2":(z.year==2025)&(d.dt.month>=7),
    }

def main():
    z=load()
    dev=z[z.year.isin([2024,2025])].copy()
    masks=block_masks(z)

    block_rows=[]
    grid_rows=[]
    for th in QS:
        for name,mask in masks.items():
            s=stat(z[mask].copy(),th)
            block_rows.append({"q":th,"block":name,**s})

        agg=stat(dev,th)
        br=[r for r in block_rows if r["q"]==th]
        positive=sum(1 for r in br if r["net_rescue"]>0)
        min_net=min(r["net_rescue"] for r in br)
        eligible=bool(
            agg["candidate_n"]>=15
            and agg["net_rescue"]>=5
            and agg["rescue_precision"]>=.55
            and agg["candidate_rate"]<=.25
            and min_net>=-1
            and positive>=3
        )
        grid_rows.append({**agg,"positive_blocks":positive,"min_block_net":min_net,"robust_eligible":eligible})

    blocks=pd.DataFrame(block_rows)
    grid=pd.DataFrame(grid_rows)
    blocks.to_csv(OUT_BLOCKS,index=False)
    grid.to_csv(OUT_GRID,index=False)

    elig=grid[grid.robust_eligible].copy()
    selected=None; h=None; whole=None
    if elig.empty:
        status="NO_ROBUST_RTE_V3_RULE"
    else:
        elig=elig.sort_values(
            ["net_rescue","rescue_precision","rescued","candidate_rate","q"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].q)
        h=period(z[z.year==2026].copy(),selected)
        whole=whole2026(h["net_rescue"])
        status="RTE_V3_HOLDOUT_SCORED"

    summary={
        "schema":"RTE_OPT_H3_V3","status":status,
        "development_grid":grid.to_dict("records"),
        "block_metrics":blocks.to_dict("records"),
        "selected_q":selected,
        "holdout_2026":h,
        "whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# RTE-H3 V3 — OPTION-CONFIRMED TRANSITION CASCADE RESULT","",
           f"**Status:** **{status}**  ",
           "**Candidate:** pRTE >= q AND pInst >= 0.50 AND signed Gold options pressure > 0.","",
           "## 2024-2025 development robustness","",
           "| q | Cand | Rescue | Broken | Net | Precision | Rate | Positive blocks | Min block net | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(f"| {r.q:.2f} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {r.positive_blocks} | {r.min_block_net:+d} | {r.robust_eligible} |")

    lines += ["","## Half-year blocks","",
              "| q | Block | Cand | Rescue | Broken | Net | Precision |",
              "|---:|---|---:|---:|---:|---:|---:|"]
    for r in blocks.itertuples():
        lines.append(f"| {r.q:.2f} | {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% |")

    if selected is not None:
        lines += ["",f"## Selected q: {selected:.2f}","",
                  "## 2026 final holdout","",
                  f"- candidates: **{h['candidate_n']} ({100*h['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{h['rescued']} / {h['broken']} / {h['net_rescue']:+d}**",
                  f"- rescue precision: **{100*h['rescue_precision']:.2f}%**",
                  f"- V5 eligible -> assisted: **{100*h['v5_accuracy']:.2f}% -> {100*h['assisted_accuracy']:.2f}%**",
                  f"- V5 missed reversal + OPAL-no-candidate: **{h['missed_opal_no_candidate_n']}**",
                  f"- V3 hits inside that set: **{h['hits_missed_opal_no_candidate']}**",
                  f"- whole clean 2026 correct: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "2024-2025 was the complete V3 development set. 2026 was opened only if a rule passed the preregistered block-robustness gate. No 2026 outcome was used for rule selection."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
