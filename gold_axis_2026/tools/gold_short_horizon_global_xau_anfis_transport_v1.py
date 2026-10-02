from __future__ import annotations
import json, os
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import log_loss, balanced_accuracy_score, precision_score, recall_score

import gold_short_horizon_global_xau_anfis_vanilla_v1 as van
import gold_short_horizon_global_xau_anfis_chhho_v1 as ch

OUT=Path(os.environ.get("OUT_DIR","global_xau_anfis_transport_out"))
OUT.mkdir(parents=True,exist_ok=True)

def metrics(y,p):
    y=np.asarray(y,int)
    p=np.clip(np.asarray(p,float),1e-6,1-1e-6)
    pred=(p>=.5).astype(int)
    return {
        "n":int(len(y)),
        "brier":float(np.mean((p-y)**2)),
        "logloss":float(log_loss(y,p,labels=[0,1])),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "up_precision":float(precision_score(y,pred,zero_division=0)),
        "up_recall":float(recall_score(y,pred,zero_division=0)),
        "down_recall":float(recall_score(1-y,1-pred,zero_division=0)),
        "mean_p_up":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
        "actual_up_rate":float(np.mean(y)),
    }

def attach_rows(test,pv,pc,pl):
    rows=[]
    for r,a,b,l in zip(test.itertuples(),pv,pc,pl):
        y=int(r.target_r3>0)
        for model,p in [("VANILLA_ANFIS",a),("CHHHO_ANFIS",b),("LOGIT_L2",l)]:
            pred=int(p>=.5)
            rows.append({
                "model":model,
                "feature_cutoff_date":str(r.feature_cutoff_date.date()),
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "target_end_date_h3":str(r.target_end_date_h3.date()),
                "actual_h3_return":float(r.target_r3),
                "actual_direction":"UP" if y else "DOWN",
                "p_up":float(p),
                "predicted_direction":"UP" if pred else "DOWN",
                "correct":bool(pred==y),
                "year":int(r.forecast_issue_date.year),
                "month":str(r.forecast_issue_date.strftime("%Y-%m")),
            })
    return pd.DataFrame(rows)

def period_metrics(ledger):
    rows=[]
    for model,g0 in ledger.groupby("model"):
        for yr,g in g0.groupby("year"):
            mm=metrics((g.actual_direction=="UP").astype(int),g.p_up)
            rows.append({"model":model,"period":str(int(yr)),**mm})
        g26=g0[g0.year==2026]
        for mo,g in g26.groupby("month"):
            mm=metrics((g.actual_direction=="UP").astype(int),g.p_up)
            rows.append({"model":model,"period":str(mo),**mm})
    return pd.DataFrame(rows)

def main():
    df=van.read_panel()
    eligible=df[df.target_r3.notna() & df.target_end_date_h3.notna()].copy()
    train=eligible[eligible.target_end_date_h3<=pd.Timestamp("2024-12-31")].copy()
    test=eligible[
        eligible.forecast_issue_date.dt.year.isin([2025,2026]) &
        (eligible.target_end_date_h3<=pd.Timestamp("2026-09-30"))
    ].copy()

    pv,dv=van.fit_predict_anfis(train,test)
    pc,dc=ch.fit_predict_hybrid(train,test,block_id=0)
    pl=van.fit_predict_logit(train,test)

    ledger=attach_rows(test,pv,pc,pl)
    ledger.to_csv(OUT/"anfis_transport_predictions.csv",index=False)
    pm=period_metrics(ledger)
    pm.to_csv(OUT/"anfis_transport_metrics.csv",index=False)

    summary={
        "schema":"GLOBAL_XAU_DAILY_H3_ANFIS_TRANSPORT_V1",
        "mode":"STRICT_FROZEN_FIT",
        "train_n":int(len(train)),
        "train_last_target_end":str(train.target_end_date_h3.max().date()),
        "test_n":int(len(test)),
        "last_scored_issue":str(test.forecast_issue_date.max().date()),
        "last_scored_target_end":str(test.target_end_date_h3.max().date()),
        "vanilla_fit_diag":dv,
        "chhho_fit_diag":dc,
        "metrics":pm.to_dict(orient="records"),
        "governance":{
            "opened_outcomes_used_for_fit":False,
            "opened_outcomes_used_for_model_selection":False,
            "threshold":0.5,
            "features":"CORE3",
            "target":"H3_DIRECTION",
        }
    }
    (OUT/"anfis_transport_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str)+"\n")

    lines=[
        "# GLOBAL XAU DAILY H3 — ANFIS 2025/2026 Frozen Transport","",
        f"Training rows: **{len(train)}**; last pre-2025 target maturity: **{train.target_end_date_h3.max().date()}**.",
        f"Opened scoring through issue **{test.forecast_issue_date.max().date()}**, target end **{test.target_end_date_h3.max().date()}**.","",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | Log loss | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"
    ]
    want={"2025","2026","2026-08","2026-09"}
    for r in pm.itertuples():
        if r.period in want:
            lines.append(
                f"| {r.model} | {r.period} | {int(r.n)} | {100*r.accuracy:.1f}% | "
                f"{100*r.balanced_accuracy:.1f}% | {r.brier:.4f} | {r.logloss:.4f} | "
                f"{100*r.up_recall:.1f}% | {100*r.down_recall:.1f}% |"
            )
    lines += ["",
              "All three rows use one pre-2025 frozen fit. No 2025/2026 label updates the models."]
    (OUT/"ANFIS_TRANSPORT_RESULT.md").write_text("\n".join(lines)+"\n")
    print("ANFIS_TRANSPORT_SUMMARY="+json.dumps(summary,separators=(",",":"),default=str))
    print((OUT/"ANFIS_TRANSPORT_RESULT.md").read_text())

if __name__=="__main__":
    main()
