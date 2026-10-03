from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
OUT_MD=AX/"GOLD_H3_RTE_V1_DEV_DIAGNOSTIC_2026-10-03.md"
OUT_JSON=AX/"GOLD_H3_RTE_V1_DEV_DIAGNOSTIC_2026-10-03.json"

THS=[0.70,0.75,0.80]
FEATURES=[
"v5_confidence","trend_strength","opposite_semivar_share","deceleration_6h",
"path_consistency","trend_close_location","opposite_extreme_recency","adverse_excursion",
"gc_dlog_volume_1","gc_volume_z20","gc_volume_accel_5",
"signed_opt_pressure","signed_d_opt_pressure","opt_total_z20",
"cf_deceleration_6h_gap","cf_opposite_semivar_share_gap","cf_adverse_excursion_gap",
"cf_signed_opt_pressure_gap","cf_signed_d_opt_pressure_gap","cf_gc_dlog_volume_1_gap",
"cf_opt_total_z20_gap"
]

def smd(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    if len(a)<2 or len(b)<2: return np.nan
    s=np.sqrt((np.nanvar(a,ddof=1)+np.nanvar(b,ddof=1))/2)
    return np.nan if s==0 else float((np.nanmean(a)-np.nanmean(b))/s)

def main():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    for d in [p,f]:
        d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
        d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
    keep=["feature_cutoff_date"]+FEATURES
    z=p.merge(f[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z[z.year.isin([2023,2024])].sort_values("forecast_issue_date").reset_index(drop=True)

    # sequential derivatives computed only within chronological DEV predictions
    z["prev_p_rte"]=z.p_rte.shift(1)
    z["prev_p_inst"]=z.p_inst.shift(1)
    z["prev_mom"]=z.momentum_up.shift(1)
    same=(z.momentum_up==z.prev_mom)
    z["dp_rte"]=np.where(same,z.p_rte-z.prev_p_rte,np.nan)
    z["dp_inst"]=np.where(same,z.p_inst-z.prev_p_inst,np.nan)
    z["tension_velocity"]=z.rte_tension-z.rte_tension.shift(1)
    z.loc[~same,"tension_velocity"]=np.nan
    z["opt_against_and_rising"]=(z.signed_opt_pressure>0)&(z.signed_d_opt_pressure>0)
    z["cf_opt_joint"]=(z.cf_signed_opt_pressure_gap>0)&(z.cf_signed_d_opt_pressure_gap>0)
    z["path_fracture_joint"]=(z.deceleration_6h>0)&(z.adverse_excursion>0.25)&(z.path_consistency<0.75)

    out={"thresholds":{}}
    lines=["# RTE-H3 V1 — DEV FALSE-POSITIVE DIAGNOSTIC","",
           "**Scope:** 2023-2024 DEV only. 2025/2026 outcomes are not opened.",""]

    for th in THS:
        q=z[z.p_rte>=th].copy()
        q["effect"]=np.where(q.rescue_target==1,"RESCUED","BROKEN")
        r=q[q.effect=="RESCUED"]; b=q[q.effect=="BROKEN"]
        info={"n":len(q),"rescued":len(r),"broken":len(b),"features":[]}
        for c in FEATURES+["p_inst","p_rte","rte_tension","dp_rte","dp_inst","tension_velocity"]:
            info["features"].append({
                "feature":c,
                "rescued_mean":float(r[c].mean()) if len(r) else np.nan,
                "broken_mean":float(b[c].mean()) if len(b) else np.nan,
                "rescued_median":float(r[c].median()) if len(r) else np.nan,
                "broken_median":float(b[c].median()) if len(b) else np.nan,
                "smd_rescued_minus_broken":smd(r[c].dropna(),b[c].dropna())
            })
        bools={}
        for c in ["opt_against_and_rising","cf_opt_joint","path_fracture_joint"]:
            rr=float(r[c].mean()) if len(r) else np.nan
            bb=float(b[c].mean()) if len(b) else np.nan
            bools[c]={"rescued_rate":rr,"broken_rate":bb,"diff":rr-bb if np.isfinite(rr) and np.isfinite(bb) else np.nan}
        info["boolean_mechanisms"]=bools
        out["thresholds"][str(th)]=info

        lines += [f"## Threshold {th:.2f}","",
                  f"- candidates: **{len(q)}**",
                  f"- rescued / broken: **{len(r)} / {len(b)}**","",
                  "### Largest standardized separations (rescued - broken)","",
                  "| Feature | SMD | Rescue median | Broken median |",
                  "|---|---:|---:|---:|"]
        fs=sorted(info["features"],key=lambda x: abs(x["smd_rescued_minus_broken"]) if np.isfinite(x["smd_rescued_minus_broken"]) else -1,reverse=True)
        for x in fs[:10]:
            lines.append(f"| {x['feature']} | {x['smd_rescued_minus_broken']:+.3f} | {x['rescued_median']:.4f} | {x['broken_median']:.4f} |")
        lines += ["","### Mechanism flags",""]
        for c,x in bools.items():
            lines.append(f"- {c}: rescued **{100*x['rescued_rate']:.1f}%**, broken **{100*x['broken_rate']:.1f}%**, diff **{100*x['diff']:+.1f} pp**")
        lines.append("")

    # inspect whether memory harms by comparing p_inst-only thresholds on DEV
    inst_grid=[]
    for th in [0.55,0.60,0.65,0.70,0.75,0.80]:
        c=z.p_inst>=th; y=z.rescue_target.astype(bool)
        rr=int((c&y).sum()); bb=int((c&~y).sum())
        inst_grid.append({"threshold":th,"candidate_n":int(c.sum()),"rescued":rr,"broken":bb,
                          "net":rr-bb,"precision":rr/max(int(c.sum()),1),"rate":float(c.mean())})
    out["instant_grid"]=inst_grid
    lines += ["## Instant probability control","",
              "| Th | Cand | Rescue | Broken | Net | Precision | Rate |",
              "|---:|---:|---:|---:|---:|---:|---:|"]
    for x in inst_grid:
        lines.append(f"| {x['threshold']:.2f} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net']:+d} | {100*x['precision']:.2f}% | {100*x['rate']:.2f}% |")

    OUT_JSON.write_text(json.dumps(out,indent=2,default=str)+"\n")
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: diagnostic-ready
