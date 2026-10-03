from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PRED=AX/"GOLD_H3_RTE_V1_PREDICTIONS_2026-10-03.csv"
FEAT=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
OUT_GRID=AX/"GOLD_H3_RTE_V2B_DEV_GRID_2026-10-03.csv"
OUT_SUM=AX/"GOLD_H3_RTE_V2B_SUMMARY_2026-10-03.json"
OUT_MD=AX/"GOLD_H3_RTE_V2B_RESULT_2026-10-03.md"

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
    z=p.merge(
        f[["feature_cutoff_date","signed_opt_pressure","cf_opt_total_z20_gap"]],
        on="feature_cutoff_date",how="left",validate="one_to_one"
    ).sort_values("forecast_issue_date").reset_index(drop=True)

    z["prev_p_rte"]=z.p_rte.shift(1)
    z["prev_mom"]=z.momentum_up.shift(1)
    z["prev_date"]=z.feature_cutoff_date.shift(1)
    same=(z.momentum_up==z.prev_mom)&((z.feature_cutoff_date-z.prev_date).dt.days<=5)
    z["seq_valid"]=same.fillna(False)
    z["dp_rte"]=np.where(z.seq_valid,z.p_rte-z.prev_p_rte,np.nan)
    z["persistent"]=z.seq_valid&(z.prev_p_rte>=PREV_FLOOR)&(z.dp_rte<=DP_MAX)
    z["options_either"]=(z.signed_opt_pressure>0)|(z.cf_opt_total_z20_gap>0)
    return z

def cand_mask(q,th,mode):
    c=(q.p_rte>=th)&q.persistent
    if mode=="EITHER":
        c=c&q.options_either
    return c

def rule_stats(q,th,mode):
    c=cand_mask(q,th,mode); y=q.rescue_target.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "threshold":th,"options_mode":mode,"eligible_n":len(q),"candidate_n":n,
        "rescued":r,"broken":b,"net_rescue":r-b,
        "rescue_precision":r/max(n,1),"candidate_rate":n/max(len(q),1),
        "design_eligible":bool(n>=10 and r-b>0 and r/max(n,1)>=.55 and n/max(len(q),1)<=.25)
    }

def period(q,rule):
    c=cand_mask(q,rule["threshold"],rule["options_mode"])
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
        "missed_opal_no_candidate_n":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))).sum()),
        "hits_missed_opal_no_candidate":int(((q.rescue_target==1)&(~q.opal_override_check.astype(bool))&c).sum())
    }

def whole2026(net):
    v=pd.read_csv(V5)
    z=v[v.year==2026]
    pred=(z.p_helios_v5_dce>=.5).astype(int); y=z.y_up.astype(int)
    base=int((pred==y).sum()); n=len(z)
    return {"n":n,"v5_correct":base,"assisted_correct":base+net,
            "v5_accuracy":base/max(n,1),"assisted_accuracy":(base+net)/max(n,1)}

def main():
    z=load()
    dev=z[z.year.isin([2023,2024])].copy()
    grid=pd.DataFrame([rule_stats(dev,t,m) for t in THRESH for m in MODES])
    grid.to_csv(OUT_GRID,index=False)

    elig=grid[grid.design_eligible].copy()
    selected=None; c25=None; c26=None; whole=None; pass25=None

    if elig.empty:
        status="NO_ELIGIBLE_RTE_V2B_RULE"
    else:
        elig["mode_pref"]=(elig.options_mode=="EITHER").astype(int)
        elig=elig.sort_values(
            ["net_rescue","rescue_precision","rescued","candidate_rate","threshold","mode_pref"],
            ascending=[False,False,False,True,False,False]
        )
        r=elig.iloc[0]
        selected={"threshold":float(r.threshold),"options_mode":str(r.options_mode)}
        c25=period(z[z.year==2025].copy(),selected)
        pass25=bool(
            c25["net_rescue"]>=2 and c25["rescue_precision"]>=.55
            and c25["candidate_rate"]<=.25
            and c25["assisted_accuracy"]>c25["v5_accuracy"]
        )
        if not pass25:
            status="RTE_V2B_2025_CONFIRM_FAIL"
        else:
            status="RTE_V2B_CONFIRM_PASS"
            c26=period(z[z.year==2026].copy(),selected)
            whole=whole2026(c26["net_rescue"])

    summary={"schema":"RTE_SB_H3_V2B","status":status,
             "frozen":{"prev_floor":PREV_FLOOR,"dp_max":DP_MAX,"thresholds":THRESH,"modes":MODES},
             "development_2023_2024":grid.to_dict("records"),
             "selected_rule":selected,"confirmation_2025":c25,
             "confirmation_2025_pass":pass25,"holdout_2026":c26,"whole_2026":whole}
    OUT_SUM.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# RTE-H3 V2B — SLOW-BURN TRANSITION RESULT","",
           f"**Status:** **{status}**  ",
           f"**Frozen state:** previous pRTE >= {PREV_FLOOR:.2f}, ΔpRTE <= {DP_MAX:.2f}.","",
           "## 2023-2024 development grid","",
           "| pRTE | Options | Cand | Rescue | Broken | Net | Precision | Rate | Eligible |",
           "|---:|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.itertuples():
        lines.append(f"| {r.threshold:.2f} | {r.options_mode} | {r.candidate_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} | {100*r.rescue_precision:.2f}% | {100*r.candidate_rate:.2f}% | {r.design_eligible} |")

    if selected:
        lines += ["","## Selected DEV rule","",
                  f"- pRTE threshold: **{selected['threshold']:.2f}**",
                  f"- options mode: **{selected['options_mode']}**","",
                  "## 2025 untouched confirmation","",
                  f"- candidates: **{c25['candidate_n']} ({100*c25['candidate_rate']:.2f}%)**",
                  f"- rescue / broken / net: **{c25['rescued']} / {c25['broken']} / {c25['net_rescue']:+d}**",
                  f"- precision: **{100*c25['rescue_precision']:.2f}%**",
                  f"- V5 -> assisted accuracy: **{100*c25['v5_accuracy']:.2f}% -> {100*c25['assisted_accuracy']:.2f}%**",
                  f"- confirmation: **{'PASS' if pass25 else 'FAIL'}**"]
        if pass25:
            lines += ["","## 2026 final holdout","",
                      f"- candidates: **{c26['candidate_n']} ({100*c26['candidate_rate']:.2f}%)**",
                      f"- rescue / broken / net: **{c26['rescued']} / {c26['broken']} / {c26['net_rescue']:+d}**",
                      f"- precision: **{100*c26['rescue_precision']:.2f}%**",
                      f"- V5 eligible -> assisted: **{100*c26['v5_accuracy']:.2f}% -> {100*c26['assisted_accuracy']:.2f}%**",
                      f"- V5 missed reversal + OPAL-no-candidate: **{c26['missed_opal_no_candidate_n']}**",
                      f"- V2B hits in that set: **{c26['hits_missed_opal_no_candidate']}**",
                      f"- whole clean 2026: **{whole['v5_correct']} -> {whole['assisted_correct']} / {whole['n']}**",
                      f"- whole clean 2026 accuracy: **{100*whole['v5_accuracy']:.2f}% -> {100*whole['assisted_accuracy']:.2f}%**"]

    lines += ["","## Governance","",
              "The slow-burn rule family was fixed before this run. 2023-2024 is development, 2025 is the first untouched confirmation, and 2026 is opened only after a 2025 pass."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
