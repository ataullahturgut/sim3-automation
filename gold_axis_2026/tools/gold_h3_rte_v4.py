from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PANEL=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_PRED=AX/"GOLD_H3_RTE_V4_PREDICTIONS_2026-10-03.csv"
OUT_GRID=AX/"GOLD_H3_RTE_V4_DEV_GRID_2026-10-03.csv"
OUT_BLOCKS=AX/"GOLD_H3_RTE_V4_BLOCK_METRICS_2026-10-03.csv"
OUT_SUM=AX/"GOLD_H3_RTE_V4_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_RTE_V4_RESULT_2026-10-03.md"

SEED=20261003
MIN_TRAIN=100
THRESH=[0.50,0.55,0.60,0.65,0.70]
MAG_FLOOR=0.01

FEATURES=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","trend_close_location","opposite_extreme_recency","adverse_excursion",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20",
"cf_deceleration_6h_gap","cf_opposite_semivar_share_gap","cf_adverse_excursion_gap",
"cf_signed_opt_pressure_gap","cf_signed_d_opt_pressure_gap","cf_gc_dlog_volume_1_gap",
"cf_opt_total_z20_gap"
]

def parse_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def load():
    p=pd.read_csv(PANEL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","cme_trade_date"]:
        if c in p.columns: p[c]=pd.to_datetime(p[c])
    p=p[p.eligible_v5_continuation.astype(bool)].copy()
    p["material_reversal_target"]=(
        (p.rescue_target.astype(int)==1)&(p.target_r3.abs()>=MAG_FLOOR)
    ).astype(int)
    p["opal_candidate"]=parse_bool(p.opal_override_check)
    p["month_key"]=p.forecast_issue_date.dt.to_period("M").astype(str)
    return p.sort_values("forecast_issue_date").reset_index(drop=True)

def model():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=.25,solver="lbfgs",max_iter=3000,class_weight="balanced",random_state=SEED
        ))
    ])

def walk(p):
    out=[]
    test=p[p.forecast_issue_date>=pd.Timestamp("2024-01-01")].copy()
    for mo in sorted(test.month_key.unique()):
        te=test[test.month_key==mo].dropna(subset=FEATURES).copy()
        if te.empty: continue
        cutoff=te.feature_cutoff_date.min()
        first=te.forecast_issue_date.min()
        tr=p[(p.target_end_date_h3<=cutoff)&(p.forecast_issue_date<first)].dropna(
            subset=FEATURES+["material_reversal_target"]
        ).copy()
        if len(tr)<MIN_TRAIN or tr.material_reversal_target.nunique()<2: continue
        m=model()
        m.fit(tr[FEATURES].to_numpy(float),tr.material_reversal_target.astype(int).to_numpy())
        pr=m.predict_proba(te[FEATURES].to_numpy(float))[:,1]
        for r,pp in zip(te.itertuples(),pr):
            out.append({
                "feature_cutoff_date":r.feature_cutoff_date,
                "forecast_issue_date":r.forecast_issue_date,
                "target_end_date_h3":r.target_end_date_h3,
                "year":int(r.year),"month":str(r.month),
                "y_up":int(r.y_up),"target_r3":float(r.target_r3),
                "v5_pred":int(r.v5_pred),"rescue_target":int(r.rescue_target),
                "material_reversal_target":int(r.material_reversal_target),
                "opal_candidate":bool(r.opal_candidate),
                "p_material":float(pp),"train_n":len(tr)
            })
    return pd.DataFrame(out).sort_values("forecast_issue_date").reset_index(drop=True)

def cand(q,th):
    return q.p_material>=th

def stats(q,th):
    c=cand(q,th)
    y=q.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "q":th,"eligible_n":len(q),"candidate_n":n,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(n,1),"candidate_rate":n/max(len(q),1),
        "material_true_n":int(q.material_reversal_target.sum()),
        "material_hit_n":int((c&q.material_reversal_target.astype(bool)).sum())
    }

def period(q,th):
    c=cand(q,th)
    v=q.v5_pred.astype(int).to_numpy(); y=q.y_up.astype(int).to_numpy()
    a=np.where(c.to_numpy(),1-v,v)
    r=int((c.to_numpy()&(v!=y)&(a==y)).sum())
    b=int((c.to_numpy()&(v==y)&(a!=y)).sum())
    mat=q.material_reversal_target.astype(bool)
    return {
        "eligible_n":len(q),"candidate_n":int(c.sum()),
        "candidate_rate":float(c.mean()) if len(q) else np.nan,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(r+b,1),
        "v5_accuracy":float((v==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((a==y).mean()) if len(q) else np.nan,
        "material_reversal_n":int(mat.sum()),
        "material_reversal_hit_n":int((c&mat).sum()),
        "material_reversal_recall":float((c&mat).sum()/max(int(mat.sum()),1)),
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_candidate)).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_candidate)&c).sum())
    }

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    p=load()
    pred=walk(p)
    pred.to_csv(OUT_PRED,index=False)

    d=pred.forecast_issue_date
    masks={
        "2024_H1":(pred.year==2024)&(d.dt.month<=6),
        "2024_H2":(pred.year==2024)&(d.dt.month>=7),
        "2025_H1":(pred.year==2025)&(d.dt.month<=6),
        "2025_H2":(pred.year==2025)&(d.dt.month>=7),
    }
    dev=pred[pred.year.isin([2024,2025])].copy()

    block_rows=[]; grid_rows=[]
    for th in THRESH:
        for name,mask in masks.items():
            s=stats(pred[mask].copy(),th)
            block_rows.append({"q":th,"block":name,**s})
        agg=stats(dev,th)
        br=[x for x in block_rows if x["q"]==th]
        pos=sum(1 for x in br if x["net_rescue"]>0)
        mn=min(x["net_rescue"] for x in br)
        ok=bool(
            agg["candidate_n"]>=10
            and agg["net_rescue"]>=5
            and agg["rescue_precision"]>=.60
            and agg["candidate_rate"]<=.20
            and pos>=3 and mn>=-1
        )
        grid_rows.append({**agg,"positive_blocks":pos,"min_block_net":mn,"robust_eligible":ok})

    blocks=pd.DataFrame(block_rows); grid=pd.DataFrame(grid_rows)
    blocks.to_csv(OUT_BLOCKS,index=False); grid.to_csv(OUT_GRID,index=False)

    elig=grid[grid.robust_eligible].copy()
    selected=None; hold=None; whole=None
    if elig.empty:
        status="NO_ROBUST_RTE_V4_RULE"
    else:
        elig=elig.sort_values(
            ["net_rescue","rescue_precision","rescued","candidate_rate","q"],
            ascending=[False,False,False,True,False]
        )
        selected=float(elig.iloc[0].q)
        hold=period(pred[pred.year==2026].copy(),selected)
        whole=whole2026(hold["net_rescue"])
        status="RTE_V4_HOLDOUT_SCORED"

    summary={
        "schema":"RTE_MATERIAL_H3_V4","status":status,"magnitude_floor":MAG_FLOOR,
        "development_grid":grid.to_dict("records"),"block_metrics":blocks.to_dict("records"),
        "selected_q":selected,"holdout_2026":hold,"whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# RTE-H3 V4 — MATERIAL REVERSAL TARGET RESULT","",
           f"**Status:** **{status}**  ",
           f"**Target:** V5 missed reversal AND |H3 return| >= {100*MAG_FLOOR:.1f}%.","",
           "## 2024-2025 development robustness","",
           "| q | Cand | Rescue | Broken | Net | Precision | Rate | Material hit/true | + blocks | Min block | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(f"| {r.q:.2f} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {r.material_hit_n}/{r.material_true_n} | {r.positive_blocks} | {r.min_block_net:+d} | {r.robust_eligible} |")

    lines += ["","## Half-year blocks","",
              "| q | Block | Cand | Rescue | Broken | Net | Precision |",
              "|---:|---|---:|---:|---:|---:|---:|"]
    for r in blocks.itertuples():
        lines.append(f"| {r.q:.2f} | {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% |")

    if selected is not None:
        lines += ["",f"## Selected q: {selected:.2f}","",
                  "## 2026 final holdout","",
                  f"- candidates: **{hold['candidate_n']} ({100*hold['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{hold['rescued']} / {hold['broken']} / {hold['net_rescue']:+d}**",
                  f"- precision: **{100*hold['rescue_precision']:.2f}%**",
                  f"- material reversal recall: **{hold['material_reversal_hit_n']}/{hold['material_reversal_n']} = {100*hold['material_reversal_recall']:.2f}%**",
                  f"- eligible V5 -> assisted: **{100*hold['v5_accuracy']:.2f}% -> {100*hold['assisted_accuracy']:.2f}%**",
                  f"- OPAL-no-candidate missed reversals hit: **{hold['hits_missed_opal_no_candidate']}/{hold['missed_opal_no_candidate_n']}**",
                  f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                  f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "2026 was opened only if the material-reversal rule passed the preregistered 2024-2025 half-year robustness gate. No holdout-driven tuning is permitted."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
