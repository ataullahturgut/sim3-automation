from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_GRID=AX/"GOLD_H3_OAR_RTE_V1_DEV_GRID_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_OAR_RTE_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_OAR_RTE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_OAR_RTE_V1_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_OAR_RTE_V1_2026_HOLDOUT_2026-10-04.csv"

QS=[0.60,0.65,0.70]

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    for d in [p,f]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    z=p.merge(
        f[["feature_cutoff_date","signed_opt_pressure","signed_d_opt_pressure"]],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    )
    z["opal_candidate"]=parse_bool(z.opal_override_check)
    return z.sort_values("forecast_issue_date").reset_index(drop=True)

def cand(q,th):
    return (
        (q.p_rte>=th)
        &(q.p_inst>=.50)
        &(q.signed_opt_pressure>0)
        &(q.signed_d_opt_pressure>0)
    )

def stat(q,th):
    c=cand(q,th); y=q.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "q":th,"eligible_n":len(q),"candidate_n":n,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(n,1),"candidate_rate":n/max(len(q),1)
    }

def period(q,th):
    c=cand(q,th)
    v=q.v5_pred.astype(int).to_numpy(); y=q.y_up.astype(int).to_numpy()
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
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&c).sum())
    },q.assign(oar_candidate=c.to_numpy(),oar_pred=a,oar_correct=(a==y))

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    z=load()
    d=z.forecast_issue_date
    masks={
        "2024_H1":(z.year==2024)&(d.dt.month<=6),
        "2024_H2":(z.year==2024)&(d.dt.month>=7),
        "2025_H1":(z.year==2025)&(d.dt.month<=6),
        "2025_H2":(z.year==2025)&(d.dt.month>=7),
    }
    dev=z[z.year.isin([2024,2025])].copy()

    blocks=[]; grids=[]
    for th in QS:
        for name,mask in masks.items():
            s=stat(z[mask].copy(),th)
            blocks.append({"q":th,"block":name,**s})
        agg=stat(dev,th)
        br=[x for x in blocks if x["q"]==th]
        nonneg=sum(1 for x in br if x["net_rescue"]>=0)
        mn=min(x["net_rescue"] for x in br)
        ok=bool(
            agg["candidate_n"]>=10
            and agg["net_rescue"]>=4
            and agg["rescue_precision"]>=.60
            and agg["candidate_rate"]<=.15
            and nonneg>=3
            and mn>=-1
        )
        grids.append({**agg,"nonnegative_blocks":nonneg,"min_block_net":mn,"robust_eligible":ok})

    bdf=pd.DataFrame(blocks); gdf=pd.DataFrame(grids)
    bdf.to_csv(OUT_BLOCK,index=False); gdf.to_csv(OUT_GRID,index=False)

    elig=gdf[gdf.robust_eligible].copy()
    selected=None; hold=None; whole=None
    if elig.empty:
        status="NO_ROBUST_OAR_RTE_RULE"
    else:
        elig=elig.sort_values(
            ["net_rescue","rescue_precision","rescued","candidate_rate","q"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].q)
        hold,hold_df=period(z[z.year==2026].copy(),selected)
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
        status="OAR_RTE_ROBUST_PASS_2026_OPENED"

    summary={
        "schema":"OAR_RTE_H3_V1","status":status,
        "development_grid":gdf.to_dict("records"),
        "block_metrics":bdf.to_dict("records"),
        "selected_q":selected,"holdout_2026":hold,"whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# OAR-RTE-H3 V1 — OPTIONS AGAINST-AND-RISING RESULT","",
           f"**Status:** **{status}**  ",
           "**Candidate:** pRTE>=q AND pInst>=0.50 AND signed option pressure>0 AND signed option-pressure change>0.","",
           "## 2024-2025 development robustness","",
           "| q | Cand | Rescue | Broken | Net | Precision | Rate | Nonnegative blocks | Min block | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in gdf.itertuples():
        lines.append(
            f"| {r.q:.2f} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {r.nonnegative_blocks}/4 | {r.min_block_net:+d} | {r.robust_eligible} |"
        )

    lines += ["","## Half-year blocks","",
              "| q | Block | Cand | Rescue | Broken | Net | Precision |",
              "|---:|---|---:|---:|---:|---:|---:|"]
    for r in bdf.itertuples():
        lines.append(f"| {r.q:.2f} | {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% |")

    if selected is not None:
        lines += ["",f"## Selected q: {selected:.2f}","",
                  "## 2026 final holdout","",
                  f"- candidates: **{hold['candidate_n']} ({100*hold['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- rescue precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "2026 is opened only after the dual options-pressure mechanism passes the frozen 2024-2025 robustness gate. No holdout-driven tuning is allowed."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
