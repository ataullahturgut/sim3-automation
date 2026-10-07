from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PSF=AX/"GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv"
RFR=AX/"GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv"
PAIR=AX/"GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"

OUTC=AX/"GOLD_EXECUTION_PRAMV_GATE_ROWS_2026-10-07.csv"
OUTJ=AX/"GOLD_EXECUTION_PRAMV_GATE_SUMMARY_2026-10-07.json"
OUTR=AX/"GOLD_EXECUTION_PRAMV_GATE_RESULT_2026-10-07.md"

def metric(g,pcol):
    y=g.y.astype(int).to_numpy();p=g[pcol].astype(int).to_numpy()
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    return {"n":len(g),"accuracy":float(accuracy_score(y,p)),"ba":float(balanced_accuracy_score(y,p)),
            "up_recall":float(recall_score(y,p,pos_label=1,zero_division=0)),
            "down_recall":float(recall_score(y,p,pos_label=0,zero_division=0)),
            "tn":tn,"fp":fp,"fn":fn,"tp":tp}

def summarize(g):
    gm=metric(g,"gate_pred");bp=metric(g,"pair_pred")
    gc=g.gate_pred.astype(int).eq(g.y.astype(int));bc=g.pair_pred.astype(int).eq(g.y.astype(int))
    rescue=int((gc&~bc).sum());brk=int((~gc&bc).sum())
    return {"gate":gm,"pair_same_rows":bp,"rescue":rescue,"break":brk,"net_rescue":rescue-brk,
            "binom_p_vs_50_one_sided":float(binomtest(int(gc.sum()),len(g),.5,alternative="greater").pvalue),
            "mcnemar_exact_p_vs_pair":float(binomtest(rescue,rescue+brk,.5).pvalue) if rescue+brk else 1.0}

def main():
    p=pd.read_csv(PSF,parse_dates=["date"])
    p=p[p.family.eq("M4_SIG_FPCA_MACRO")][["date","year","y","pred","p_up"]].rename(columns={"pred":"m4_pred"})
    r=pd.read_csv(RFR,parse_dates=["date"])
    r=r[r.eligible_nomacro.astype(str).str.lower().eq("true")][["date","rule_pred","eligible_nomacro"]]
    b=pd.read_csv(PAIR,parse_dates=["date"])
    b=b[b.policy.eq("PAIR_ALL")][["date","pred"]].drop_duplicates("date").rename(columns={"pred":"pair_pred"})
    q=p.merge(r,on="date",how="inner",validate="one_to_one").merge(b,on="date",how="inner",validate="one_to_one")
    q["agree"]=q.m4_pred.astype(int).eq(q.rule_pred.astype(int))
    q=q[q.agree].copy()
    q["gate_pred"]=q.m4_pred.astype(int)
    q["gate_correct"]=q.gate_pred.eq(q.y.astype(int))
    q["pair_correct"]=q.pair_pred.astype(int).eq(q.y.astype(int))
    q["half"]=np.where(q.date.dt.month<=6,"H1","H2")

    result={}
    denominators={2023:256,2024:259,2025:254}
    for y in [2023,2024,2025]:
        g=q[q.year.eq(y)]
        z=summarize(g);z["coverage"]=len(g)/denominators[y];result[str(y)]=z
        for half in ["H1","H2"]:
            h=g[g.half.eq(half)]
            result[f"{y}_{half}"]=summarize(h) if len(h) else None
    dev=q[q.year.isin([2023,2024])]
    result["DEV_2023_2024"]=summarize(dev)
    result["DEV_2023_2024"]["coverage"]=len(dev)/(denominators[2023]+denominators[2024])

    summary={
      "status":"COMPLETE",
      "identity":"PRAMV_V1",
      "target":"17:00 -> next eligible 09:00 Europe/Istanbul",
      "rule":[
        "same-day paired macro surprise released by 17:00 => ABSTAIN",
        "16:00-16:30 and 16:30-17:00 must have opposite signs (RFR active), otherwise ABSTAIN",
        "M4_SIG_FPCA_MACRO direction must equal RFR first-impulse direction, otherwise ABSTAIN",
        "if all conditions hold, issue the common direction"
      ],
      "scientific_roles":{
        "M4":"direct path-shape predictor using scalar + lead-lag signature + FPCA + origin-known macro state",
        "RFR":"mechanistic reversal-first-impulse specialist",
        "macro_veto":"known information-arrival regime filter"
      },
      "posthoc_warning":"The exact PRAMV synthesis was identified after the 2025 retrospective archive was already accessible. 2025 is corroborative retrospective transport, not untouched prospective validation. A future/2026+ locked test is required for production proof.",
      "results":result
    }
    q.to_csv(OUTC,index=False);OUTJ.write_text(json.dumps(summary,indent=2)+"\n")
    def pct(v):return f"{100*float(v):.2f}%"
    lines=["# GOLD EXECUTION PRAMV V1 RESULT — 2026-10-07","",
           "**Status:** COMPLETE / MECHANISTIC SELECTIVE OVERNIGHT CANDIDATE","",
           "**PRAMV = Path-Reversal Agreement + Macro Veto**","",
           "Rule: abstain on same-day macro-release state; require a pre-17:00 half-hour reversal; require the path-signature/FPCA M4 direction to agree with the independent RFR first-impulse direction; otherwise abstain.","",
           "| Period | N | Coverage | PRAMV Acc | PRAMV BA | UP recall | DOWN recall | PAIR Acc same rows | PAIR BA | Rescue | Break | Net |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for y in ["2023","2024","2025"]:
        z=result[y]
        lines.append(f"| {y} | {z['gate']['n']} | {pct(z['coverage'])} | {pct(z['gate']['accuracy'])} | {pct(z['gate']['ba'])} | {pct(z['gate']['up_recall'])} | {pct(z['gate']['down_recall'])} | {pct(z['pair_same_rows']['accuracy'])} | {pct(z['pair_same_rows']['ba'])} | {z['rescue']} | {z['break']} | {z['net_rescue']:+d} |")
    d=result["DEV_2023_2024"]
    lines += ["",f"Development pooled: N **{d['gate']['n']}**, coverage **{pct(d['coverage'])}**, accuracy **{pct(d['gate']['accuracy'])}**, BA **{pct(d['gate']['ba'])}**.",
              f"Chance test: one-sided binomial p = **{d['binom_p_vs_50_one_sided']:.4f}**.",
              f"Against PAIR on exact same rows: rescue/break/net **{d['rescue']}/{d['break']}/{d['net_rescue']:+d}**, exact McNemar/binomial p = **{d['mcnemar_exact_p_vs_pair']:.4f}**.","",
              "Half-year stability:",
              f"- 2023 H1: N {result['2023_H1']['gate']['n']}, BA {pct(result['2023_H1']['gate']['ba'])}; H2: N {result['2023_H2']['gate']['n']}, BA {pct(result['2023_H2']['gate']['ba'])}.",
              f"- 2024 H1: N {result['2024_H1']['gate']['n']}, BA {pct(result['2024_H1']['gate']['ba'])}; H2: N {result['2024_H2']['gate']['n']}, BA {pct(result['2024_H2']['gate']['ba'])}.",
              f"- 2025 H1: N {result['2025_H1']['gate']['n']}, BA {pct(result['2025_H1']['gate']['ba'])}; H2: N {result['2025_H2']['gate']['n']}, BA {pct(result['2025_H2']['gate']['ba'])}.","",
              "Governance warning: PRAMV was synthesized after the 2025 archive was already visible in the project. Therefore 2025 supports robustness but is not untouched prospective OOS proof. Lock PRAMV V1 unchanged before any 2026+ test."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text());print(json.dumps(summary,indent=2))

if __name__=="__main__":main()
