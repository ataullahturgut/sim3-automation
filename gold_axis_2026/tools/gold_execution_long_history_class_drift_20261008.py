"""Development-only rationale: historic class prior drift causes UP-only collapse.
Two predeclared, algorithmically minimal ablations on LONG 2020+ LIT identities:
class_weight='balanced' and exponential 365d half-life (without balance).
2025 is inspected retrospective evidence and must not tune parameters.
"""
from pathlib import Path
import json,time
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.metrics import confusion_matrix, brier_score_loss
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
import gold_execution_long_history_lit_same_date_20261008 as base

AX=Path(__file__).resolve().parents[1]
OUT=AX/"GOLD_EXECUTION_LONG_HISTORY_CLASS_DRIFT_CHALLENGER_2026-10-08.md"
MET=AX/"GOLD_EXECUTION_LONG_HISTORY_CLASS_DRIFT_METRICS_2026-10-08.csv"
SUM=AX/"GOLD_EXECUTION_LONG_HISTORY_CLASS_DRIFT_SUMMARY_2026-10-08.json"
MODES=("LONG_PLAIN","LONG_CLASS_BALANCED","LONG_HALFLIFE_365")

def metrics(y,probs):
    p=np.asarray(probs); y=np.asarray(y).astype(int)
    yp=(p>=.5).astype(int)
    tn,fp,fn,tp=confusion_matrix(y,yp,labels=[0,1]).ravel()
    return dict(n=len(y),acc=float((yp==y).mean()),
                ba=float((tn/(tn+fp)+tp/(tp+fn))/2) if tn+fp and tp+fn else None,
                up=float(tp/(tp+fn)) if tp+fn else None,
                down=float(tn/(tn+fp)) if tn+fp else None,
                brier=float(brier_score_loss(y,p)),
                up_rate=float(yp.mean()))

def experiments(d):
    out=[]
    for name,(target,feats) in base.FEATURES.items():
        q=d.dropna(subset=feats+["ret_"+target,"y_"+target]).sort_values("date").reset_index(drop=True)
        for year in (2023,2024,2025):
            tst=q[q.year==year]
            fixed=q[(q.date<pd.Timestamp("2025-01-01"))&(q.year>=2020)]
            if target=="OVN":fixed=fixed[fixed.next_date<=pd.Timestamp("2025-01-01")]
            for _,r in tst.iterrows():
                if year!=2025:
                    h=q[(q.date<r.date)&(q.year>=2020)]
                    if target=="OVN":h=h[h.next_date<=r.date]
                else:h=fixed
                if len(h)<80 or h["y_"+target].nunique()!=2:continue
                X=h[feats].to_numpy(float)
                y=h["y_"+target].astype(int).to_numpy()
                row=r[feats].to_numpy(float).reshape(1,-1)
                days=(r.date-h.date).dt.days.to_numpy(float)
                for mode in MODES:
                    weight=np.exp(-np.log(2)*days/365) if mode=="LONG_HALFLIFE_365" else None
                    cw="balanced" if mode=="LONG_CLASS_BALANCED" else None
                    model=make_pipeline(StandardScaler(),
                      LogisticRegression(C=1,max_iter=2000,class_weight=cw))
                    if weight is None:model.fit(X,y)
                    else:model.fit(X,y,logisticregression__sample_weight=weight)
                    p=float(model.predict_proba(row)[0,1])
                    out.append({"model":name,"year":year,"date":r.date,"y":int(r["y_"+target]),
                                "mode":mode,"p":p})
    return pd.DataFrame(out)

def summarise(pred):
    results=[]
    for (model,year),x in pred.groupby(["model","year"]):
        wide=x.pivot(index=["date","y"],columns="mode",values="p").dropna()
        if len(wide)<175:raise RuntimeError("INSUFFICIENT_MATCHED_ORIGINS")
        y=wide.index.get_level_values("y").astype(int).to_numpy()
        plain=metrics(y,wide["LONG_PLAIN"].to_numpy())
        for mode in MODES:
            z=metrics(y,wide[mode].to_numpy())
            pp=(wide["LONG_PLAIN"].to_numpy()>=.5)
            cc=(wide[mode].to_numpy()>=.5)
            res=int(((cc==y)&(pp!=y)).sum())
            brk=int(((cc!=y)&(pp==y)).sum())
            results.append({"model":model,"year":year,"mode":mode,"n":len(y),
                "acc":z["acc"],"ba":z["ba"],"up_recall":z["up"],
                "down_recall":z["down"],"brier":z["brier"],"up_rate":z["up_rate"],
                "delta_ba_pp":100*(z["ba"]-plain["ba"]),
                "delta_brier":z["brier"]-plain["brier"],
                "rescues_vs_long_plain":res,"breaks_vs_long_plain":brk,
                "mcnemar_p":float(binomtest(res,res+brk,.5).pvalue) if res+brk else 1.})
    return pd.DataFrame(results)

def main():
    t=time.time()
    raw=pd.concat([base.private_2020_21(),base.native_2022_25()],ignore_index=True)
    raw[["open","close"]]=raw[["open","close"]].apply(pd.to_numeric,errors="coerce")
    raw=raw.dropna(subset=["open","close","ts"])
    base.check_prices(raw)
    d=base.build(raw)
    labels=base.audit_legacy_labels(d)
    preds=experiments(d)
    metric=summarise(preds)
    metric.to_csv(MET,index=False)
    summary={"status":"ACTUAL_CLASS_DRIFT_AUDIT_COMPLETE",
      "preregistered_comparators":list(MODES),"decay_half_life_days":365,
      "train_source_2020_21":"Twelve Data native M15 private Neon",
      "train_source_2022_25":"frozen project XAU M15 archive",
      "label_exact_match":labels,
      "dev_years":[2023,2024],"retrospective_transport":[2025],
      "target":"Istanbul fixed 09 DAY and 17 OVERNIGHT",
      "scientific_limit":"inspected research 2023-25; cannot promote from 2025; source-transition vintage not yet accepted",
      "elapsed_seconds":round(time.time()-t,2),"models_promoted":False}
    SUM.write_text(json.dumps(summary,indent=2)+"\n")
    lines=["# Long-history class drift remedies — preregistered ablations","",
     "**Research:** SAME base LIT feature models; 2020+ unweighted vs 2020+ balanced class weights vs 2020+ 365-day sample half-life. 2025 never used to select mode. PRAMV V1 NOT rerun.","",
      "| LIT model | Year | Mode | N | BA | UP recall | DOWN recall | Brier | Δ BA vs long plain |",
      "|---|---:|---|---:|---:|---:|---:|---:|---:|"]
    for r in metric.itertuples(index=False):
        lines.append(f"| {r.model} | {r.year} | {r.mode} | {r.n} | {r.ba*100:.2f}% | {r.up_recall*100:.2f}% | {r.down_recall*100:.2f}% | {r.brier:.4f} | {r.delta_ba_pp:+.2f}pp |")
    lines+=["","Interpretation: avoid interpreting improved class balance as positive edge unless BA > 50% in both development years, calibration is sound, and 2025 retrospective transport is consistent. No prospective confirmation or bank P&L.", ""]
    OUT.write_text("\n".join(lines))
    print(OUT.read_text(),flush=True)

if __name__=="__main__": main()
