from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
ORIGIN=AX/"GOLD_H3_VAST_V1_ORIGIN_FEATURES_2026-10-04.csv"

OUT_SCORE=AX/"GOLD_H3_IFBC_V1_SCORES_2026-10-04.csv"
OUT_GRID=AX/"GOLD_H3_IFBC_V1_THRESHOLD_GRID_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_IFBC_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_IFBC_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_IFBC_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_IFBC_V1_PROSPECTIVE_FREEZE_2026-10-04.json"

QGRID=[.65,.70,.75,.80]
CAL_N=120
MIN_CAL=60

def block_name(ts):
    t=pd.Timestamp(ts)
    return f"{t.year}_{'H1' if t.month<=6 else 'H2'}"

def rank_val(hist,v):
    a=np.asarray(hist,float)
    a=a[np.isfinite(a)]
    if len(a)<MIN_CAL or not np.isfinite(v):
        return np.nan
    return float((1+np.sum(a<=v))/(len(a)+1))

def build_scores():
    z=pd.read_csv(ORIGIN)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        z[c]=pd.to_datetime(z[c])
    z=z.sort_values("feature_cutoff_date").reset_index(drop=True)

    z["x1"]=z.gc_opp_vol_share_12
    z["x2"]=-z.gc_flow_12
    z["x3"]=-z.si_flow_12
    z["x4"]=z.joint_opposition_share12
    z["x5"]=z.gc_si_flow_gap12
    z["x6"]=1.0-z.gc_efficiency_12

    rows=[]
    for i,r in z.iterrows():
        hist=z[z.feature_cutoff_date<r.feature_cutoff_date].tail(CAL_N)
        ranks=[rank_val(hist[f"x{k}"],r[f"x{k}"]) for k in range(1,7)]
        if any(not np.isfinite(x) for x in ranks):
            continue
        d=r.to_dict()
        for k,v in enumerate(ranks,1):
            d[f"rank_{k}"]=v
        d["ifbc_score"]=float(np.median(ranks))
        d["ifbc_count60"]=int(sum(v>=.60 for v in ranks))
        rows.append(d)
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def cand(g,q):
    return (g.ifbc_count60>=4)&(g.ifbc_score>=q)

def metrics(g,q):
    c=cand(g,q)
    y=g.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "q":q,"eligible_n":len(g),"candidate_n":n,
        "rescued":r,"broken":b,"net":r-b,
        "precision":r/max(n,1),
        "recall":r/max(int(y.sum()),1),
        "candidate_rate":n/max(len(g),1)
    }

def main():
    z=build_scores()
    z.to_csv(OUT_SCORE,index=False)
    z["block"]=z.forecast_issue_date.map(block_name)
    scored=z[z.block.isin(["2025_H2","2026_H1","2026_H2"])].copy()

    grid=[]; blocks=[]
    for q in QGRID:
        a=metrics(scored,q)
        br=[]
        for name,g in scored.groupby("block",sort=False):
            x=metrics(g,q); x["block"]=name; br.append(x)
        pos=sum(1 for x in br if x["net"]>0)
        worst=min((x["net"] for x in br),default=0)
        a["positive_blocks"]=pos; a["worst_block_net"]=worst
        a["eligible"]=bool(
            a["candidate_n"]>=10 and a["net"]>0 and a["precision"]>=.55
            and pos>=2 and worst>=-2
        )
        grid.append(a); blocks.extend(br)

    gdf=pd.DataFrame(grid); bdf=pd.DataFrame(blocks)
    gdf.to_csv(OUT_GRID,index=False); bdf.to_csv(OUT_BLOCK,index=False)

    elig=gdf[gdf.eligible].copy()
    selected=None
    if elig.empty:
        status="NO_ELIGIBLE_IFBC_V1_MECHANISM"
    else:
        elig=elig.sort_values(["net","precision","rescued","candidate_n","q"],
                              ascending=[False,False,False,True,False])
        selected=float(elig.iloc[0].q)
        status="IFBC_V1_MECHANISM_PASS_PROSPECTIVE_SHADOW"

    # Diagnostics for score calibration.
    diag=[]
    for name,g in scored.groupby("block",sort=False):
        r=g[g.rescue_target==1]; c=g[g.rescue_target==0]
        diag.append({
            "block":name,"n":len(g),"reversal_n":int(g.rescue_target.sum()),
            "reversal_score_median":float(r.ifbc_score.median()) if len(r) else np.nan,
            "continuation_score_median":float(c.ifbc_score.median()) if len(c) else np.nan,
            "reversal_count60_median":float(r.ifbc_count60.median()) if len(r) else np.nan,
            "continuation_count60_median":float(c.ifbc_count60.median()) if len(c) else np.nan,
        })

    freeze={
        "schema":"IFBC_H3_V1_PROSPECTIVE_FREEZE",
        "freeze_date":"2026-10-04",
        "first_clean_origin":"2026-10-05",
        "historical_status":"development_only",
        "selected_q":selected,
        "calibration_origins":CAL_N,
        "min_calibration":MIN_CAL,
        "consensus_count60_min":4,
        "feature_signs":{
            "x1":"gc_opp_vol_share_12",
            "x2":"-gc_flow_12",
            "x3":"-si_flow_12",
            "x4":"joint_opposition_share12",
            "x5":"gc_si_flow_gap12",
            "x6":"1-gc_efficiency_12"
        }
    }
    OUT_FREEZE.write_text(json.dumps(freeze,indent=2)+"\n")

    summary={
        "schema":"IFBC_H3_V1","status":status,
        "score_rows":len(z),"selected_q":selected,
        "threshold_grid":grid,"block_diagnostic":diag,
        "prospective_freeze":freeze
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# IFBC-H3 V1 — INTRADAY FLOW BREAKDOWN CONSENSUS RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence:** retrospective rank-based development; 2026 is development only.","",
        f"- scored origins with sufficient trailing calibration: **{len(z)}**","",
        "## Frozen threshold grid","",
        "| q | Cand | Rescue | Broken | Net | Precision | Recall | Rate | + blocks | Worst | Eligible |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for x in grid:
        lines.append(
            f"| {x['q']:.2f} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net']:+d} | "
            f"{100*x['precision']:.2f}% | {100*x['recall']:.2f}% | {100*x['candidate_rate']:.2f}% | "
            f"{x['positive_blocks']} | {x['worst_block_net']:+d} | {x['eligible']} |"
        )

    lines += ["","## Score anatomy","",
              "| Block | n | Rev | Rev score med | Cont score med | Rev count60 med | Cont count60 med |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for x in diag:
        lines.append(
            f"| {x['block']} | {x['n']} | {x['reversal_n']} | {x['reversal_score_median']:.3f} | "
            f"{x['continuation_score_median']:.3f} | {x['reversal_count60_median']:.1f} | "
            f"{x['continuation_count60_median']:.1f} |"
        )

    if selected is not None:
        q=bdf[np.isclose(bdf.q,selected)]
        lines += ["",f"## Selected q: {selected:.2f}","",
                  "| Block | Cand | Rescue | Broken | Net | Precision | Recall |",
                  "|---|---:|---:|---:|---:|---:|---:|"]
        for r in q.itertuples():
            lines.append(f"| {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% | {100*r.recall:.2f}% |")

    lines += ["","## Governance","",
              "The feature signs were frozen from VAST block-consistency diagnostics before this run. "
              "Historical results are development only; any new clean evidence must be prospective."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
