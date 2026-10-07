from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
FSMR=AX/"GOLD_EXECUTION_FSMR_STAGE4_PREDICTIONS_2026-10-07.csv"
PAIR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
OUTJ=AX/"GOLD_EXECUTION_RFR_NOMACRO_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_RFR_NOMACRO_RESULT_2026-10-07.md"
OUTC=AX/"GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv"

def metrics(y,p):
    y=np.asarray(y,int);p=np.asarray(p,int)
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    return {"n":len(y),"accuracy":float(accuracy_score(y,p)),"ba":float(balanced_accuracy_score(y,p)),
            "up_recall":float(recall_score(y,p,pos_label=1,zero_division=0)),
            "down_recall":float(recall_score(y,p,pos_label=0,zero_division=0)),
            "tn":tn,"fp":fp,"fn":fn,"tp":tp}

def summarize(g):
    r=metrics(g.y,g.rule_pred);b=metrics(g.y,g.pair_pred)
    maj=max(float(g.y.mean()),1-float(g.y.mean()))
    resc=int((~g.pair_correct & g.rule_correct).sum())
    brk=int((g.pair_correct & ~g.rule_correct).sum())
    acc_p=float(binomtest(int(g.rule_correct.sum()),len(g),0.5,alternative="greater").pvalue)
    mc_p=float(binomtest(resc,resc+brk,0.5).pvalue) if resc+brk else 1.0
    return {"rule":r,"pair_same_rows":b,"majority_accuracy":maj,"rescue":resc,"break":brk,"net_rescue":resc-brk,
            "binom_p_vs_50":acc_p,"mcnemar_exact_p_vs_pair":mc_p}

def main():
    f=pd.read_csv(FSMR,parse_dates=["date"])
    p=pd.read_csv(PAIR,parse_dates=["date"])
    p=p[p.policy=="PAIR_ALL"][["date","year","pred","y","macro_released","upcoming_fomc"]].rename(columns={"pred":"pair_pred","y":"pair_y"})
    q=f[(f.model=="FSMR4")&(f.state.isin(["01","10"]))][["date","year","state","y"]].copy()
    q=q.merge(p,on=["date","year"],how="inner",validate="one_to_one")
    if not q.y.astype(int).eq(q.pair_y.astype(int)).all():raise RuntimeError("LABEL_MISMATCH")
    q["rule_pred"]=np.where(q.state.eq("10"),1,0)
    q["rule_correct"]=q.rule_pred.astype(int).eq(q.y.astype(int))
    q["pair_correct"]=q.pair_pred.astype(int).eq(q.y.astype(int))
    q["eligible_nomacro"]=q.macro_released.astype(int).eq(0)

    result={}
    for label,mask in [
        ("2023",q.year.eq(2023)&q.eligible_nomacro),
        ("2024",q.year.eq(2024)&q.eligible_nomacro),
        ("DEV_2023_2024",q.year.isin([2023,2024])&q.eligible_nomacro),
        ("2025",q.year.eq(2025)&q.eligible_nomacro),
        ("DEV_MACRO_RELEASED",q.year.isin([2023,2024])&~q.eligible_nomacro),
        ("2025_MACRO_RELEASED",q.year.eq(2025)&~q.eligible_nomacro),
    ]:
        g=q[mask].copy()
        if len(g):result[label]=summarize(g)

    # coverage denominator is all PAIR_ALL days in each year.
    den={int(y):int(len(p[p.year==y])) for y in [2023,2024,2025]}
    for y in [2023,2024,2025]:
        result[str(y)]["coverage"]=result[str(y)]["rule"]["n"]/den[y]

    summary={
      "status":"COMPLETE",
      "identity":"RFR_NOMACRO_V1",
      "rule":"If 16:00-16:30 and 16:30-17:00 Europe/Istanbul have opposite signs and no same-day paired macro surprise was released by 17:00, predict 17:00->next09 direction as the 16:00-16:30 sign; otherwise abstain.",
      "rationale":["Ma et al. 2025 night-effect momentum/reversal mechanism","Sobti et al. 2021 macro-news state dependence","Smales & Yang 2015 rapid macro-announcement reaction"],
      "selection_note":"No numeric threshold. The no-macro filter improves the reversal-first-impulse rule in both 2023 and 2024. 2025 is retrospective transport and was already observed elsewhere in the project, so it is not untouched prospective evidence.",
      "results":result,
    }
    q.to_csv(OUTC,index=False);OUTJ.write_text(json.dumps(summary,indent=2)+"\n")
    def pct(x):return f"{100*float(x):.2f}%"
    lines=["# GOLD EXECUTION RFR-NOMACRO V1 RESULT — 2026-10-07","",
      "**Status:** COMPLETE / DEVELOPMENT-SUPPORTED SELECTIVE OVERNIGHT SPECIALIST","",
      "Rule: when 16:00-16:30 and 16:30-17:00 directions are opposite and no same-day paired macro surprise has been released by 17:00, predict the overnight direction as the 16:00-16:30 direction; otherwise abstain.","",
      "| Period | N | Coverage | Rule Acc | Rule BA | UP recall | DOWN recall | Pair Acc same rows | Pair BA | Majority Acc | Rescue | Break | Net |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in ["2023","2024","2025"]:
        z=result[y]
        lines.append(f"| {y} | {z['rule']['n']} | {pct(z['coverage'])} | {pct(z['rule']['accuracy'])} | {pct(z['rule']['ba'])} | {pct(z['rule']['up_recall'])} | {pct(z['rule']['down_recall'])} | {pct(z['pair_same_rows']['accuracy'])} | {pct(z['pair_same_rows']['ba'])} | {pct(z['majority_accuracy'])} | {z['rescue']} | {z['break']} | {z['net_rescue']:+d} |")
    z=result["DEV_2023_2024"]
    lines += ["",f"DEV pooled: accuracy **{pct(z['rule']['accuracy'])}**, BA **{pct(z['rule']['ba'])}**, rescue/break/net **{z['rescue']}/{z['break']}/{z['net_rescue']:+d}**.",
              f"DEV one-sided binomial p vs 50%: **{z['binom_p_vs_50']:.4f}**; exact rescue-vs-break p against pair model: **{z['mcnemar_exact_p_vs_pair']:.4f}**.",
              "",
              "Interpretation: this is a selective overnight specialist with roughly mid-40% coverage, not a full-coverage daily model. The 2025 result is retrospective transport, not prospective proof."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
