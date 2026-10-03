from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"

OUT_GRID=AX/"GOLD_H3_RTE_V2_2023_DESIGN_GRID_2026-10-03.csv"
OUT_SUM=AX/"GOLD_H3_RTE_V2_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_RTE_V2_RESULT_2026-10-03.md"

THRESH=[0.70,0.75,0.80]
MODES=["NONE","EITHER"]
PREV_FLOOR=0.60
DP_MAX=0.05

def load():
    p=pd.read_csv(PRED)
    f=pd.read_csv(FEAT)
    for d in [p,f]:
        d["feature_cutoff_date"]=pd.to_datetime(d.feature_cutoff_date)
        d["forecast_issue_date"]=pd.to_datetime(d.forecast_issue_date)
    keep=["feature_cutoff_date","signed_opt_pressure","cf_opt_total_z20_gap"]
    z=p.merge(f[keep],on="feature_cutoff_date",how="left",validate="one_to_one")
    z=z.sort_values("forecast_issue_date").reset_index(drop=True)

    z["prev_p_rte"]=z.p_rte.shift(1)
    z["prev_mom"]=z.momentum_up.shift(1)
    z["prev_date"]=z.feature_cutoff_date.shift(1)
    same=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
    z["seq_valid"]=same.fillna(False)
    z["dp_rte"]=np.where(z.seq_valid,z.p_rte-z.prev_p_rte,np.nan)
    z["persistent"]=(z.seq_valid)&(z.prev_p_rte>=PREV_FLOOR)&(z.dp_rte<=DP_MAX)
    z["options_either"]=(z.signed_opt_pressure>0)|(z.cf_opt_total_z20_gap>0)
    return z

def mask_rule(q,th,mode):
    c=(q.p_rte>=th)&q.persistent
    if mode=="EITHER":
        c=c&q.options_either
    return c

def stats(q,th,mode):
    c=mask_rule(q,th,mode)
    y=q.rescue_target.astype(bool)
    resc=int((c&y).sum()); broken=int((c&~y).sum()); cn=int(c.sum()); n=len(q)
    precision=resc/max(cn,1)
    rate=cn/max(n,1)
    return {
        "threshold":th,"options_mode":mode,"eligible_n":n,"candidate_n":cn,
        "rescued":resc,"broken":broken,"net_rescue":resc-broken,
        "rescue_precision":precision,"candidate_rate":rate,
        "design_eligible":bool(cn>=5 and resc-broken>0 and precision>=.55 and rate<=.25)
    }

def apply_period(q,rule):
    c=mask_rule(q,rule["threshold"],rule["options_mode"])
    y=q.y_up.astype(int).to_numpy()
    v5=q.v5_pred.astype(int).to_numpy()
    assisted=np.where(c.to_numpy(),1-v5,v5)
    resc=int((c.to_numpy()&(v5!=y)&(assisted==y)).sum())
    broken=int((c.to_numpy()&(v5==y)&(assisted!=y)).sum())
    return {
        "eligible_n":len(q),"candidate_n":int(c.sum()),
        "candidate_rate":float(c.mean()) if len(q) else np.nan,
        "rescued":resc,"broken":broken,"net_rescue":resc-broken,
        "rescue_precision":resc/max(resc+broken,1),
        "v5_accuracy":float((v5==y).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((assisted==y).mean()) if len(q) else np.nan,
        "missed_reversal_n":int(q.rescue_target.sum()),
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))&c).sum())
    }

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026].copy()
    pred=(z.p_helios_v5_dce>=.5).astype(int)
    y=z.y_up.astype(int)
    correct=int((pred==y).sum())
    n=len(z)
    return {
        "n":n,"v5_correct":correct,"assisted_correct":correct+net,
        "v5_accuracy":correct/max(n,1),"assisted_accuracy":(correct+net)/max(n,1)
    }

def main():
    z=load()
    y23=z[z.year==2023].copy()
    grid=pd.DataFrame([stats(y23,t,m) for t in THRESH for m in MODES])
    grid.to_csv(OUT_GRID,index=False)

    elig=grid[grid.design_eligible].copy()
    selected=None; y24s=None; y25s=None; y26s=None; whole=None
    confirm24=None; confirm25=None

    if elig.empty:
        status="NO_ELIGIBLE_RTE_V2_DESIGN"
    else:
        elig["mode_pref"]=(elig.options_mode=="EITHER").astype(int)
        elig=elig.sort_values(
            ["net_rescue","rescue_precision","rescued","candidate_rate","threshold","mode_pref"],
            ascending=[False,False,False,True,False,False]
        )
        r=elig.iloc[0]
        selected={"threshold":float(r.threshold),"options_mode":str(r.options_mode)}
        y24s=apply_period(z[z.year==2024].copy(),selected)
        confirm24=bool(
            y24s["net_rescue"]>0
            and y24s["rescue_precision"]>=.55
            and y24s["candidate_rate"]<=.25
        )
        if not confirm24:
            status="RTE_V2_2024_CONFIRM_FAIL"
        else:
            y25s=apply_period(z[z.year==2025].copy(),selected)
            confirm25=bool(
                y25s["net_rescue"]>=2
                and y25s["rescue_precision"]>=.55
                and y25s["candidate_rate"]<=.25
                and y25s["assisted_accuracy"]>y25s["v5_accuracy"]
            )
            if not confirm25:
                status="RTE_V2_2025_CONFIRM_FAIL"
            else:
                status="RTE_V2_CONFIRM_PASS"
                y26s=apply_period(z[z.year==2026].copy(),selected)
                whole=whole2026(y26s["net_rescue"])

    summary={
        "schema":"RTE_SB_H3_V2","status":status,
        "frozen":{"prev_floor":PREV_FLOOR,"dp_max":DP_MAX,"thresholds":THRESH,"modes":MODES},
        "design_2023":grid.to_dict("records"),
        "selected_rule":selected,
        "internal_confirmation_2024":y24s,
        "internal_confirmation_pass":confirm24,
        "confirmation_2025":y25s,
        "confirmation_2025_pass":confirm25,
        "holdout_2026":y26s,
        "whole_2026":whole
    }
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# RTE-H3 V2 — SLOW-BURN TRANSITION RESULT","",
           f"**Status:** **{status}**  ",
           f"**Frozen slow-burn rule family:** prev pRTE >= {PREV_FLOOR:.2f}, ΔpRTE <= {DP_MAX:.2f}.","",
           "## 2023 design grid","",
           "| pRTE | Options | Cand | Rescue | Broken | Net | Precision | Rate | Eligible |",
           "|---:|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(
            f"| {r.threshold:.2f} | {r.options_mode} | {r.candidate_n} | {r.rescued} | {r.broken} | "
            f"{r.net_rescue:+d} | {100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {r.design_eligible} |"
        )

    if selected:
        lines += ["",f"## Selected 2023 rule","",
                  f"- pRTE threshold: **{selected['threshold']:.2f}**",
                  f"- options confirmation: **{selected['options_mode']}**","",
                  "## 2024 internal confirmation","",
                  f"- candidates: **{y24s['candidate_n']} ({100*y24s['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{y24s['rescued']} / {y24s['broken']} / {y24s['net_rescue']:+d}**",
                  f"- precision: **{100*y24s['rescue_precision']:.2f}%**",
                  f"- V5 -> assisted accuracy: **{100*y24s['v5_accuracy']:.2f}% -> {100*y24s['assisted_accuracy']:.2f}%**",
                  f"- 2024 confirmation: **{'PASS' if confirm24 else 'FAIL'}**"]
        if confirm24:
            lines += ["","## 2025 external confirmation","",
                      f"- candidates: **{y25s['candidate_n']} ({100*y25s['candidate_rate']:.2f}%)**",
                      f"- rescue / broken / net: **{y25s['rescued']} / {y25s['broken']} / {y25s['net_rescue']:+d}**",
                      f"- precision: **{100*y25s['rescue_precision']:.2f}%**",
                      f"- V5 -> assisted accuracy: **{100*y25s['v5_accuracy']:.2f}% -> {100*y25s['assisted_accuracy']:.2f}%**",
                      f"- 2025 confirmation: **{'PASS' if confirm25 else 'FAIL'}**"]
        if confirm25:
            lines += ["","## 2026 final holdout","",
                      f"- candidates: **{y26s['candidate_n']} ({100*y26s['candidate_rate']:.2f}%)**",
                      f"- rescue / broken / net: **{y26s['rescued']} / {y26s['broken']} / {y26s['net_rescue']:+d}**",
                      f"- precision: **{100*y26s['rescue_precision']:.2f}%**",
                      f"- V5 eligible -> assisted: **{100*y26s['v5_accuracy']:.2f}% -> {100*y26s['assisted_accuracy']:.2f}%**",
                      f"- V5 missed reversal + OPAL-no-candidate: **{y26s['missed_opal_no_candidate_n']}**",
                      f"- V2 hits in that set: **{y26s['hits_missed_opal_no_candidate']}**",
                      f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                      f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "V2 was invented from V1 DEV behavior. 2023 is design, 2024 internal confirmation, 2025 untouched external confirmation, and 2026 is opened only if both confirmations pass."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
