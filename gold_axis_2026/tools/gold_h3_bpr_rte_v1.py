from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_BPR_RTE_V1_PREDICTIONS_2026-10-04.csv"
OUT_GRID=AX/"GOLD_H3_BPR_RTE_V1_DEV_GRID_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_BPR_RTE_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_BPR_RTE_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_BPR_RTE_V1_RESULT_2026-10-04.md"
OUT_HOLD=AX/"GOLD_H3_BPR_RTE_V1_2026_HOLDOUT_2026-10-04.csv"

WINDOW=60
A=B=5
MIN_MATURED=20
THRESH=[0.40,0.45,0.50,0.55,0.60]

def logit(x):
    x=np.clip(float(x),1e-6,1-1e-6)
    return math.log(x/(1-x))

def logistic(x):
    if x>=0:
        z=math.exp(-x); return 1/(1+z)
    z=math.exp(x); return z/(1+z)

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PRED)
    panel=pd.read_csv(PANEL)
    v=pd.read_csv(V5)
    for d in [p,panel,v]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])

    # Full eligible V5-continuation history for live prior estimation.
    hv=panel[["feature_cutoff_date","forecast_issue_date","target_end_date_h3","y_up","momentum_up"]].merge(
        v[["feature_cutoff_date","p_helios_v5_dce"]],
        on="feature_cutoff_date",how="inner",validate="one_to_one"
    )
    hv["v5_pred"]=(hv.p_helios_v5_dce>=.5).astype(int)
    hv=hv[hv.v5_pred==hv.momentum_up.astype(int)].copy()
    hv["rescue_target"]=(hv.v5_pred!=hv.y_up.astype(int)).astype(int)
    hv=hv.sort_values("target_end_date_h3").reset_index(drop=True)

    p=p.sort_values("forecast_issue_date").reset_index(drop=True)
    p["opal_candidate"]=parse_bool(p.opal_override_check)
    pri=[]; ns=[]
    for r in p.itertuples():
        h=hv[
            (hv.target_end_date_h3<=r.feature_cutoff_date)
            & (hv.forecast_issue_date<r.forecast_issue_date)
        ].tail(WINDOW)
        n=len(h); k=int(h.rescue_target.sum())
        pi=(k+A)/(n+A+B) if n>0 else .5
        pri.append(pi); ns.append(n)
    p["live_reversal_prior"]=pri
    p["prior_matured_n"]=ns
    p["p_bpr"]=[
        logistic(logit(pp)+logit(pi)) if n>=MIN_MATURED else np.nan
        for pp,pi,n in zip(p.p_inst,p.live_reversal_prior,p.prior_matured_n)
    ]
    return p

def stat(q,th):
    q=q[q.p_bpr.notna()].copy()
    c=q.p_bpr>=th; y=q.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "q":th,"eligible_n":len(q),"candidate_n":n,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(n,1),
        "candidate_rate":n/max(len(q),1),
        "prior_median":float(q.live_reversal_prior.median()) if len(q) else np.nan
    }

def period(q,th):
    q=q[q.p_bpr.notna()].copy()
    c=q.p_bpr>=th
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
        "prior_min":float(q.live_reversal_prior.min()) if len(q) else np.nan,
        "prior_median":float(q.live_reversal_prior.median()) if len(q) else np.nan,
        "prior_max":float(q.live_reversal_prior.max()) if len(q) else np.nan,
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&c).sum())
    },q.assign(bpr_candidate=c.to_numpy(),bpr_pred=a,bpr_correct=(a==y))

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    p=load()
    p.to_csv(OUT_PRED,index=False)

    d=p.forecast_issue_date
    masks={
        "2024_H1":(p.year==2024)&(d.dt.month<=6),
        "2024_H2":(p.year==2024)&(d.dt.month>=7),
        "2025_H1":(p.year==2025)&(d.dt.month<=6),
        "2025_H2":(p.year==2025)&(d.dt.month>=7),
    }
    dev=p[p.year.isin([2024,2025])].copy()

    block_rows=[]; grid_rows=[]
    for th in THRESH:
        for name,mask in masks.items():
            s=stat(p[mask].copy(),th)
            block_rows.append({"q":th,"block":name,**s})
        agg=stat(dev,th)
        br=[x for x in block_rows if x["q"]==th]
        pos=sum(1 for x in br if x["net_rescue"]>0)
        mn=min(x["net_rescue"] for x in br)
        robust=bool(
            agg["candidate_n"]>=15
            and agg["net_rescue"]>=5
            and agg["rescue_precision"]>=.58
            and agg["candidate_rate"]<=.25
            and pos>=3
            and mn>=-1
        )
        grid_rows.append({**agg,"positive_blocks":pos,"min_block_net":mn,"robust_eligible":robust})

    blocks=pd.DataFrame(block_rows); grid=pd.DataFrame(grid_rows)
    blocks.to_csv(OUT_BLOCK,index=False); grid.to_csv(OUT_GRID,index=False)

    elig=grid[grid.robust_eligible].copy()
    selected=None; hold=None; whole=None
    if elig.empty:
        status="NO_ROBUST_BPR_RTE_RULE"
    else:
        elig=elig.sort_values(
            ["net_rescue","rescue_precision","rescued","candidate_rate","q"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].q)
        hold,hold_df=period(p[p.year==2026].copy(),selected)
        hold_df.to_csv(OUT_HOLD,index=False)
        whole=whole2026(hold["net_rescue"])
        status="BPR_RTE_ROBUST_PASS_2026_OPENED"

    summary={
        "schema":"BPR_RTE_H3_V1","status":status,
        "window":WINDOW,"beta_prior":[A,B],"min_matured":MIN_MATURED,
        "development_grid":grid.to_dict("records"),
        "block_metrics":blocks.to_dict("records"),
        "selected_q":selected,"holdout_2026":hold,"whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# BPR-RTE-H3 V1 — BAYES PRIOR-SHIFT RESULT","",
           f"**Status:** **{status}**  ",
           f"**Live prior:** last {WINDOW} matured V5-continuation origins with Beta({A},{B}) shrinkage.","",
           "## 2024-2025 development robustness","",
           "| q | Cand | Rescue | Broken | Net | Precision | Rate | Median prior | + blocks | Min block | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(
            f"| {r.q:.2f} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {100*r.prior_median:.2f}% | "
            f"{r.positive_blocks} | {r.min_block_net:+d} | {r.robust_eligible} |"
        )

    lines += ["","## Half-year blocks","",
              "| q | Block | Cand | Rescue | Broken | Net | Precision | Median prior |",
              "|---:|---|---:|---:|---:|---:|---:|---:|"]
    for r in blocks.itertuples():
        lines.append(
            f"| {r.q:.2f} | {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | "
            f"{100*r.rescue_precision:.2f}% | {100*r.prior_median:.2f}% |"
        )

    if selected is not None:
        lines += ["",f"## Selected q: {selected:.2f}","",
                  "## 2026 final holdout","",
                  f"- live reversal prior min / median / max: **{100*hold['prior_min']:.2f}% / {100*hold['prior_median']:.2f}% / {100*hold['prior_max']:.2f}%**",
                  f"- candidates: **{hold['candidate_n']} ({100*hold['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- rescue precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "The prior uses only matured V5-continuation outcomes available at each origin. 2026 is opened only if the full 2024-2025 half-year robustness gate passes."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
