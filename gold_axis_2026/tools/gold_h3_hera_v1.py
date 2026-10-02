from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_hera_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"
OPAL = ROOT / "gold_axis_2026" / "GOLD_H3_OPAL_V1_PREDICTIONS_2026-10-03.csv"

SEED = 20261003
REPS = 10000
BLOCKS = [5, 10]


def metrics(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,pred,labels=[0,1]).ravel()
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "up_recall":float(recall_score(y,pred,pos_label=1,zero_division=0)),
        "down_recall":float(recall_score(y,pred,pos_label=0,zero_division=0)),
        "prediction_std":float(np.std(p)),
        "tn":int(tn),"fp":int(fp),"fn":int(fn),"tp":int(tp),
    }


def load():
    a=pd.read_csv(AURORA)
    o=pd.read_csv(OPAL)
    for x in [a,o]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            x[c]=pd.to_datetime(x[c],errors="raise")
    keep=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "year","month","y_up","target_r3","p_aurora","active_expert"
    ]
    a=a[keep].copy()
    a=a[a.forecast_issue_date>=pd.Timestamp("2022-07-01")].copy()
    o=o[["forecast_issue_date","p_opal","override","p_reversal"]].copy()
    g=a.merge(o,on="forecast_issue_date",how="inner",validate="one_to_one")
    if len(g)!=len(a):
        missing=sorted(set(a.forecast_issue_date)-set(g.forecast_issue_date))
        raise RuntimeError(f"HERA_MATCH_FAIL aurora_eval={len(a)} matched={len(g)} missing={missing[:10]}")
    g["hera_uses_opal"]=g.active_expert.eq("PATH_GLOBAL")
    g["p_hera"]=np.where(g.hera_uses_opal,g.p_opal,g.p_aurora)
    return g.sort_values("forecast_issue_date").reset_index(drop=True)


def score(g):
    specs=[
        ("2022_H2",g.forecast_issue_date.between("2022-07-01","2022-12-31")),
        ("2023",g.year==2023),("2024",g.year==2024),
        ("2025",g.year==2025),("2026",g.year==2026),
        ("2023-2024",g.year.isin([2023,2024])),
        ("2025-2026",g.year.isin([2025,2026])),
    ]
    rows=[]
    for period,mask in specs:
        z=g[mask].copy()
        if z.empty: continue
        for model,col in [("AURORA","p_aurora"),("OPAL","p_opal"),("HERA","p_hera")]:
            rows.append({
                "model":model,"period":period,
                "path_share":float(z.hera_uses_opal.mean()),
                **metrics(z.y_up,z[col])
            })
    return pd.DataFrame(rows)


def confirmation(mdf,g):
    checks=[]; ok=True
    for yr in ["2023","2024"]:
        a=mdf[(mdf.model=="AURORA")&(mdf.period==yr)].iloc[0]
        h=mdf[(mdf.model=="HERA")&(mdf.period==yr)].iloc[0]
        passed=bool(
            h.accuracy+.01+1e-12>=a.accuracy
            and h.brier<=a.brier+.003+1e-12
        )
        checks.append({"period":yr,"pass":passed})
        ok=ok and passed
    a=mdf[(mdf.model=="AURORA")&(mdf.period=="2023-2024")].iloc[0]
    h=mdf[(mdf.model=="HERA")&(mdf.period=="2023-2024")].iloc[0]
    agg_ok=bool(h.balanced_accuracy+.01+1e-12>=a.balanced_accuracy)
    differs=bool(np.any(
        (g[g.forecast_issue_date>=pd.Timestamp("2025-01-01")].p_hera>=.5).astype(int).to_numpy()
        !=
        (g[g.forecast_issue_date>=pd.Timestamp("2025-01-01")].p_aurora>=.5).astype(int).to_numpy()
    ))
    return bool(ok and agg_ok and differs),checks,agg_ok,differs


def changed_calls(g,year=None):
    z=g.copy() if year is None else g[g.year==year].copy()
    z["aurora_dir"]=np.where(z.p_aurora>=.5,"UP","DOWN")
    z["opal_dir"]=np.where(z.p_opal>=.5,"UP","DOWN")
    z["hera_dir"]=np.where(z.p_hera>=.5,"UP","DOWN")
    z["actual_dir"]=np.where(z.y_up==1,"UP","DOWN")
    z["aurora_correct"]=z.aurora_dir.eq(z.actual_dir)
    z["hera_correct"]=z.hera_dir.eq(z.actual_dir)
    q=z[z.hera_dir.ne(z.aurora_dir)].copy()
    q["effect"]=np.where(
        (~q.aurora_correct)&q.hera_correct,"RESCUED",
        np.where(q.aurora_correct&(~q.hera_correct),"BROKEN","NO_NET")
    )
    return q


def logloss_row(y,p):
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    y=np.asarray(y,int)
    return -(y*np.log(p)+(1-y)*np.log(1-p))


def diff_arrays(y,cand,base):
    y=np.asarray(y,int); cand=np.asarray(cand,float); base=np.asarray(base,float)
    return {
        "accuracy":((cand>=.5).astype(int)==y).astype(float)-((base>=.5).astype(int)==y).astype(float),
        "brier":(cand-y)**2-(base-y)**2,
        "logloss":logloss_row(y,cand)-logloss_row(y,base),
    }


def circular_boot(diff,block_len,rng):
    diff=np.asarray(diff,float)
    n=len(diff); nb=int(np.ceil(n/block_len)); offs=np.arange(block_len)
    vals=np.empty(REPS,float); batch=500
    for st in range(0,REPS,batch):
        m=min(batch,REPS-st)
        starts=rng.integers(0,n,size=(m,nb))
        idx=(starts[:,:,None]+offs[None,None,:])%n
        idx=idx.reshape(m,-1)[:,:n]
        vals[st:st+m]=diff[idx].mean(axis=1)
    return vals


def inference(g):
    rows=[]; si=0
    periods={
        "2025":g.year==2025,
        "2026":g.year==2026,
        "2025-2026":g.year.isin([2025,2026]),
    }
    comparisons={
        "HERA_vs_AURORA":("p_hera","p_aurora"),
        "HERA_vs_OPAL":("p_hera","p_opal"),
    }
    for period,mask in periods.items():
        z=g[mask].copy()
        for comp,(cand,base) in comparisons.items():
            for metric,d in diff_arrays(z.y_up,z[cand],z[base]).items():
                for b in BLOCKS:
                    si+=1
                    boot=circular_boot(d,b,np.random.default_rng(SEED+si))
                    lo,hi=np.quantile(boot,[.025,.975])
                    improve=float(np.mean(boot>0)) if metric=="accuracy" else float(np.mean(boot<0))
                    rows.append({
                        "period":period,"comparison":comp,"metric":metric,"block_len":b,
                        "n":int(len(z)),"observed_diff":float(np.mean(d)),
                        "ci95_low":float(lo),"ci95_high":float(hi),
                        "bootstrap_improve_share":improve,
                    })
    return pd.DataFrame(rows)


def main():
    g=load()
    g.to_csv(OUT/"hera_v1_predictions.csv",index=False)

    mdf=score(g)
    mdf.to_csv(OUT/"hera_v1_metrics.csv",index=False)

    passed,checks,agg_ok,differs=confirmation(mdf,g)
    status="MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    c25=changed_calls(g,2025)
    c26=changed_calls(g,2026)
    c25.to_csv(OUT/"hera_v1_2025_changed.csv",index=False)
    c26.to_csv(OUT/"hera_v1_2026_changed.csv",index=False)

    inf=inference(g) if passed else pd.DataFrame()
    if passed: inf.to_csv(OUT/"hera_v1_inference.csv",index=False)

    summary={
        "schema":"HERA_H3_V1",
        "status":status,
        "evidence_class":"RETROSPECTIVE_MECHANISM_VALIDATION_POST_HOC_ARCHITECTURE",
        "rule":"Use OPAL iff AURORA active_expert == PATH_GLOBAL; otherwise use AURORA.",
        "confirmation_pass":bool(passed),
        "confirmation_checks":checks,
        "aggregate_guard":bool(agg_ok),
        "post2024_differs":bool(differs),
        "metrics":mdf.to_dict(orient="records"),
        "2025_changed":int(len(c25)),
        "2025_rescued":int((c25.effect=="RESCUED").sum()),
        "2025_broken":int((c25.effect=="BROKEN").sum()),
        "2026_changed":int(len(c26)),
        "2026_rescued":int((c26.effect=="RESCUED").sum()),
        "2026_broken":int((c26.effect=="BROKEN").sum()),
        "inference":inf.to_dict(orient="records") if passed else [],
    }
    (OUT/"hera_v1_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# HERA-H3 V1 — HIERARCHICAL EXHAUSTION-REVERSAL ADAPTER RESULT","",
        f"**Status:** **{status}**  ",
        "**Evidence class:** retrospective mechanism validation; architecture was motivated after historical OPAL regime dependence was observed.  ",
        "**Rule:** AURORA STRUCTURAL_IRIS -> AURORA; AURORA PATH_GLOBAL -> OPAL.","",
        "## Period metrics","",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall | PATH share |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2022_H2","2023","2024","2025","2026","2025-2026"]:
        for model in ["AURORA","OPAL","HERA"]:
            q=mdf[(mdf.model==model)&(mdf.period==period)]
            if q.empty: continue
            r=q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {100*r.path_share:.1f}% |"
            )

    lines += ["","## Changed calls","",
              f"- 2025: {len(c25)} changed; {(c25.effect=='RESCUED').sum()} rescued / {(c25.effect=='BROKEN').sum()} broken.",
              f"- 2026: {len(c26)} changed; {(c26.effect=='RESCUED').sum()} rescued / {(c26.effect=='BROKEN').sum()} broken."]

    if passed:
        lines += ["","## Dependence-aware bootstrap",""]
        for r in inf.itertuples():
            scale=100 if r.metric=="accuracy" else 1
            unit=" pp" if r.metric=="accuracy" else ""
            lines.append(
                f"- {r.period} {r.comparison} {r.metric} block{r.block_len}: "
                f"diff={scale*r.observed_diff:+.4f}{unit}; "
                f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
                f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
            )

    lines += ["","## Governance","",
              "HERA introduces no new numerical threshold or fitted parameter. It composes two frozen parent mechanisms using AURORA's already-causal active-expert state. "
              "Because HERA was conceived after observing OPAL's historical regime dependence, 2022-2026 results remain retrospective mechanism evidence. "
              "Existing AURORA prospective validation is unchanged."]

    (OUT/"HERA_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"HERA_V1_RESULT.md").read_text())


if __name__=="__main__":
    main()
