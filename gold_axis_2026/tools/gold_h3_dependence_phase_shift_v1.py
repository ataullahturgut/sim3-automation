from pathlib import Path
import json, math
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
TIMELINE=AX/"GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv"

OUT_MD=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_RESULT_2026-10-05.md"
OUT_JSON=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_SUMMARY_2026-10-05.json"
OUT_CSV=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv"

def num(s): return pd.to_numeric(s,errors="coerce")

def corr_info(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    m=np.isfinite(a)&np.isfinite(b)
    a=a[m];b=b[m]
    if len(a)<40 or np.std(a)<=1e-12 or np.std(b)<=1e-12:
        return np.nan,np.nan,int(len(a))
    r,p=pearsonr(a,b)
    return float(r),float(p),int(len(a))

def topology():
    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)
    rows=[]
    for i,r in d.iterrows():
        h=d.iloc[max(0,i-60):i]
        g=num(h.gold_daily_ret1).to_numpy(float)
        n=num(h.ndx_ret1).to_numpy(float)
        v=num(h.vix_ret1).to_numpy(float)
        rn,pn,nn=corr_info(g,n)
        rv,pv,nv=corr_info(g,v)
        strong=bool(np.isfinite(rn) and np.isfinite(rv) and np.isfinite(pn) and np.isfinite(pv) and rn>0 and rv<0 and min(pn,pv)<.05)
        rows.append({"feature_cutoff_date":r.feature_cutoff_date,"r_gn":rn,"p_gn":pn,"r_gv":rv,"p_gv":pv,
                     "strong_pro_risk":strong,"n_gn":nn,"n_gv":nv})
    z=pd.DataFrame(rows)
    run=[];cur=0
    for x in z.strong_pro_risk:
        cur=cur+1 if x else 0
        run.append(cur)
    z["strong_run"]=run

    # Dependence-vector mean shift.
    shift=np.full(len(z),np.nan)
    vals=z[["r_gn","r_gv"]].to_numpy(float)
    for i in range(len(z)):
        if i<100:continue
        ref=vals[max(0,i-125):i-5]
        rec=vals[max(0,i-4):i+1]
        mref=np.isfinite(ref).all(axis=1);mrec=np.isfinite(rec).all(axis=1)
        ref=ref[mref];rec=rec[mrec]
        if len(ref)<80 or len(rec)<3:continue
        med=np.median(ref,axis=0)
        mad=np.median(np.abs(ref-med),axis=0)*1.4826
        std=np.std(ref,axis=0)
        scale=np.where((np.isfinite(mad))&(mad>1e-9),mad,np.where(std>1e-9,std,1.0))
        delta=(np.mean(rec,axis=0)-med)/scale
        shift[i]=float(np.sqrt(np.sum(delta**2)))
    z["dep_shift"]=shift
    return z

def main():
    z=topology()
    pre=z.feature_cutoff_date<pd.Timestamp("2026-01-01")
    runs=z.loc[pre,"strong_run"].to_numpy(float)
    q95_run=float(np.quantile(runs,.95)); q99_run=float(np.quantile(runs,.99)); max_run=int(np.nanmax(runs))
    shifts=z.loc[pre,"dep_shift"].dropna().to_numpy(float)
    q95_shift=float(np.quantile(shifts,.95))
    z["run_phase95"]=z.strong_run>q95_run
    z["dep_shift95"]=z.dep_shift>=q95_shift
    z["dependence_phase"]=z.strong_pro_risk & (z.run_phase95 | z.dep_shift95)

    tl=pd.read_csv(TIMELINE,parse_dates=["feature_cutoff_date"])
    alarm=tl[tl.period.isin(["2025_FORMATION","2026_STRESS"])][["feature_cutoff_date","period","competence_y"]].copy()
    alarm["competence_y"]=alarm.competence_y.astype(int)
    j=alarm.merge(z,on="feature_cutoff_date",how="left")

    perf={}
    for period in ["2025_FORMATION","2026_STRESS"]:
        q=j[j.period==period]
        inside=q[q.dependence_phase.fillna(False)]
        outside=q[~q.dependence_phase.fillna(False)]
        perf[period]={
          "n":int(len(q)),
          "inside_n":int(len(inside)),
          "inside_rescue":int(inside.competence_y.sum()),
          "inside_precision":float(inside.competence_y.mean()) if len(inside) else None,
          "outside_n":int(len(outside)),
          "outside_rescue":int(outside.competence_y.sum()),
          "outside_precision":float(outside.competence_y.mean()) if len(outside) else None,
        }

    z26=z[(z.feature_cutoff_date>=pd.Timestamp("2026-01-01"))&(z.feature_cutoff_date<=pd.Timestamp("2026-09-30"))]
    def first(col):
        q=z26[z26[col]]
        return None if q.empty else q.iloc[0].feature_cutoff_date.date().isoformat()

    summary={
      "schema":"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1",
      "status":"LABEL_FREE_DEPENDENCE_DIAGNOSTIC",
      "pre2026":{"q95_run":q95_run,"q99_run":q99_run,"max_run":max_run,"q95_dep_shift":q95_shift},
      "first_2026":{
        "strong_pro_risk":first("strong_pro_risk"),
        "run_phase95":first("run_phase95"),
        "dep_shift95":first("dep_shift95"),
        "dependence_phase":first("dependence_phase"),
      },
      "handoff_performance":perf,
      "reference_dates":{"sellr_trigger":"2026-05-21","bocpd_entry":"2026-05-27","offline_cp":"2026-04-30"}
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2)+"\n")
    z.to_csv(OUT_CSV,index=False)

    lines=["# GOLD H3 — Dependence Phase-Shift V1 Result","",
           "**Status:** LABEL_FREE_DEPENDENCE_DIAGNOSTIC","",
           "## Pre-2026 calibration","",
           f"- strong-pro run q95: **{q95_run:.2f}**",
           f"- strong-pro run q99: **{q99_run:.2f}**",
           f"- max pre-2026 run: **{max_run}**",
           f"- dependence-shift q95: **{q95_shift:.3f}**","",
           "## First 2026 dates","",
           f"- first strong-pro-risk origin: **{summary['first_2026']['strong_pro_risk']}**",
           f"- first run-length phase95: **{summary['first_2026']['run_phase95']}**",
           f"- first correlation-vector shift95: **{summary['first_2026']['dep_shift95']}**",
           f"- first combined DEPENDENCE_PHASE: **{summary['first_2026']['dependence_phase']}**","",
           "Reference dates: offline competence CP **2026-04-30**, frozen SELLR trigger **2026-05-21**, BOCPD V4 entry **2026-05-27**.","",
           "## Handoff performance inside/outside dependence phase","",
           "| Period | Inside rescue/N | Inside precision | Outside rescue/N | Outside precision |",
           "|---|---:|---:|---:|---:|"]
    for p in ["2025_FORMATION","2026_STRESS"]:
        r=perf[p]
        pi="NA" if r["inside_precision"] is None else f"{100*r['inside_precision']:.1f}%"
        po="NA" if r["outside_precision"] is None else f"{100*r['outside_precision']:.1f}%"
        lines.append(f"| {p} | {r['inside_rescue']}/{r['inside_n']} | {pi} | {r['outside_rescue']}/{r['outside_n']} | {po} |")
    lines += ["","## Interpretation discipline","",
              "- Thresholds were calibrated without Handoff outcomes or reversal labels.",
              "- This tests dependence/correlation drift, not marginal feature drift.",
              "- A useful result should precede or coincide with the Apr-May competence transition and enrich Handoff precision.",
              "- This diagnostic does not create a trade rule."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
