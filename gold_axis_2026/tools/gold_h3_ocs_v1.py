from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

IFBC=AX/"GOLD_H3_IFBC_V1_SCORES_2026-10-04.csv"
LLRS=AX/"GOLD_H3_LLRS_V1_ORIGIN_SCORES_2026-10-04.csv"

OUT_GRID=AX/"GOLD_H3_OCS_V1_GRID_2026-10-04.csv"
OUT_BLOCK=AX/"GOLD_H3_OCS_V1_BLOCK_METRICS_2026-10-04.csv"
OUT_EVENTS=AX/"GOLD_H3_OCS_V1_EVENTS_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_OCS_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_OCS_V1_RESULT_2026-10-04.md"
OUT_FREEZE=AX/"GOLD_H3_OCS_V1_PROSPECTIVE_FREEZE_2026-10-04.json"

IQ=[.70,.75,.80]
LQ=[0.00,.10,.25]

def block_name(ts):
    t=pd.Timestamp(ts)
    return f"{t.year}_{'H1' if t.month<=6 else 'H2'}"

def load():
    a=pd.read_csv(IFBC)
    b=pd.read_csv(LLRS)
    for d in [a,b]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in d.columns: d[c]=pd.to_datetime(d[c])
    keepb=["feature_cutoff_date","llrs_pressure","llrs_incremental","llrs_external_opposes"]
    z=a.merge(b[keepb],on="feature_cutoff_date",how="inner",validate="one_to_one")
    z["llrs_external_opposes"]=z.llrs_external_opposes.astype(str).str.lower().isin(["true","1","yes"])
    z["block"]=z.forecast_issue_date.map(block_name)
    return z[z.block.isin(["2025_H2","2026_H1","2026_H2"])].sort_values("forecast_issue_date").reset_index(drop=True)

def cmask(g,iq,lq):
    internal=(g.ifbc_count60>=4)&(g.ifbc_score>=iq)
    external=g.llrs_external_opposes&(g.llrs_incremental>0)&(g.llrs_pressure>=lq)
    return internal&external

def met(g,iq,lq):
    c=cmask(g,iq,lq)
    y=g.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {"ifbc_q":iq,"llrs_q":lq,"eligible_n":len(g),"candidate_n":n,
            "rescued":r,"broken":b,"net":r-b,"precision":r/max(n,1),
            "recall":r/max(int(y.sum()),1),"candidate_rate":n/max(len(g),1)}

def main():
    z=load()
    grids=[]; blocks=[]
    for iq in IQ:
        for lq in LQ:
            a=met(z,iq,lq)
            br=[]
            for name,g in z.groupby("block",sort=False):
                x=met(g,iq,lq); x["block"]=name; br.append(x)
            pos=sum(1 for x in br if x["net"]>0)
            worst=min((x["net"] for x in br),default=0)
            a["positive_blocks"]=pos; a["worst_block_net"]=worst
            a["eligible"]=bool(a["candidate_n"]>=8 and a["net"]>0 and a["precision"]>=.60 and pos>=2 and worst>=-1)
            grids.append(a); blocks.extend(br)

    gdf=pd.DataFrame(grids); bdf=pd.DataFrame(blocks)
    gdf.to_csv(OUT_GRID,index=False); bdf.to_csv(OUT_BLOCK,index=False)

    e=gdf[gdf.eligible].copy()
    selected=None
    if e.empty:
        status="NO_ELIGIBLE_OCS_V1_MECHANISM"
        pd.DataFrame().to_csv(OUT_EVENTS,index=False)
    else:
        e=e.sort_values(["net","precision","rescued","candidate_n","ifbc_q","llrs_q"],
                        ascending=[False,False,False,True,False,False])
        rr=e.iloc[0]
        selected={"ifbc_q":float(rr.ifbc_q),"llrs_q":float(rr.llrs_q)}
        status="OCS_V1_MECHANISM_PASS_PROSPECTIVE_SHADOW"
        c=cmask(z,selected["ifbc_q"],selected["llrs_q"])
        ev=z[c].copy()
        ev["effect"]=np.where(ev.rescue_target==1,"RESCUE","BROKEN")
        ev.to_csv(OUT_EVENTS,index=False)

    freeze={
        "schema":"OCS_H3_V1_PROSPECTIVE_FREEZE",
        "freeze_date":"2026-10-04",
        "first_clean_origin":"2026-10-05",
        "historical_status":"development_only",
        "selected":selected,
        "rules":{
            "ifbc_count60_min":4,
            "ifbc_q_grid":IQ,
            "llrs_external_opposes":True,
            "llrs_incremental_min_strict":0,
            "llrs_q_grid":LQ
        }
    }
    OUT_FREEZE.write_text(json.dumps(freeze,indent=2)+"\n")

    summary={"schema":"OCS_H3_V1","status":status,"matched_rows":len(z),
             "grid":grids,"selected":selected,"prospective_freeze":freeze}
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# OCS-H3 V1 — ORTHOGONAL CONCURRENCE STACK RESULT","",
           f"**Status:** **{status}**  ",
           "**Evidence:** retrospective conjunction of internal flow breakdown and external hourly lead-lag; 2026 is development only.","",
           f"- matched scored origins: **{len(z)}**","",
           "## Frozen 3×3 configuration grid","",
           "| IFBC q | LLRS q | Cand | Rescue | Broken | Net | Precision | Recall | + blocks | Worst | Eligible |",
           "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for x in grids:
        lines.append(f"| {x['ifbc_q']:.2f} | {x['llrs_q']:.2f} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net']:+d} | {100*x['precision']:.2f}% | {100*x['recall']:.2f}% | {x['positive_blocks']} | {x['worst_block_net']:+d} | {x['eligible']} |")

    if selected:
        q=bdf[(np.isclose(bdf.ifbc_q,selected["ifbc_q"]))&(np.isclose(bdf.llrs_q,selected["llrs_q"]))]
        lines += ["",f"## Selected: IFBC {selected['ifbc_q']:.2f} / LLRS {selected['llrs_q']:.2f}","",
                  "| Block | Cand | Rescue | Broken | Net | Precision |",
                  "|---|---:|---:|---:|---:|---:|"]
        for r in q.itertuples():
            lines.append(f"| {r.block} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% |")

    lines += ["","## Governance","",
              "This is development evidence only. The two channels were developed before their conjunction was tested. "
              "A PASS can only justify shadow prospective evaluation, not retrospective promotion."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
