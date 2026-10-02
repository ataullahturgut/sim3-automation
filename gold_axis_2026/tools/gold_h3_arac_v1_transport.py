from __future__ import annotations
import json, os
from pathlib import Path
import pandas as pd

import gold_h3_arac_v1 as arac

OUT=Path(os.environ.get("OUT_DIR","gold_h3_arac_v1_transport_out"))
OUT.mkdir(parents=True,exist_ok=True)
THRESH=0.03337519281868787

def main():
    df=arac.load_panel()
    all_oos=arac.run_sequence(df,2019,2026)

    transport=all_oos[all_oos.year.isin([2025,2026])].copy()
    if transport.empty:
        raise RuntimeError("NO_2025_2026_TRANSPORT_ROWS")

    summary=[]
    for label,g in [
        ("2025",transport[transport.year==2025]),
        ("2026",transport[transport.year==2026]),
        ("2025_2026",transport),
    ]:
        summary+=arac.summarize_period(g,label,THRESH)

    sdf=pd.DataFrame(summary)
    sdf.to_csv(OUT/"arac_v1_transport_metrics.csv",index=False)
    transport.to_csv(OUT/"arac_v1_transport_predictions.csv",index=False)

    # Annual expert weights.
    weight_cols=["year","w_GLOBAL_EN","w_RECENT504_BAL_LOGIT","w_LOCAL_ANALOG","w_REGIME_PRIOR"]
    wdf=transport[weight_cols].groupby("year",as_index=False).mean()
    wdf.to_csv(OUT/"arac_v1_transport_weights.csv",index=False)

    # 2026 monthly full/selective diagnostics.
    y26=transport[transport.year==2026].copy()
    y26["month"]=pd.to_datetime(y26.forecast_issue_date).dt.to_period("M").astype(str)
    monthly=[]
    for mo,g in y26.groupby("month"):
        full=arac.basic_metrics(g.y_up,g.p_ARAC)
        sel=arac.selective_metrics(g,THRESH)
        monthly.append({"month":mo,"scope":"FULL","model":"ARAC",**full})
        monthly.append({"month":mo,"scope":"SELECTIVE","model":"ARAC",**sel})
    mdf=pd.DataFrame(monthly)
    mdf.to_csv(OUT/"arac_v1_transport_2026_monthly.csv",index=False)

    # selective call ledger for direct inspection
    transport["selective_call"]=transport.reliability_score>=THRESH
    transport["pred_direction"]=transport.p_ARAC.map(lambda x:"UP" if x>=0.5 else "DOWN")
    transport["actual_direction"]=transport.y_up.map(lambda x:"UP" if int(x)==1 else "DOWN")
    transport["correct"]=(transport.pred_direction==transport.actual_direction)
    transport[transport.selective_call].to_csv(OUT/"arac_v1_transport_selective_calls.csv",index=False)

    result={
        "schema":"GOLD_H3_ARAC_V1_TRANSPORT",
        "threshold":THRESH,
        "last_forecast_issue_date":str(pd.to_datetime(transport.forecast_issue_date).max().date()),
        "last_target_end_date_h3":str(pd.to_datetime(transport.target_end_date_h3).max().date()),
        "metrics":sdf.to_dict(orient="records"),
        "mean_weights":wdf.to_dict(orient="records"),
        "monthly_2026":mdf.to_dict(orient="records"),
    }
    (OUT/"arac_v1_transport_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD H3 — ARAC-H3-v1 2025/2026 TRANSPORT","",
        f"Frozen reliability threshold: **{THRESH:.15f}**.",
        f"Last evaluated forecast issue: **{result['last_forecast_issue_date']}**.","",
        "## Full coverage","",
        "| Period | Model | N | Accuracy | Balanced acc | False calls | Brier | Log loss | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for per in ["2025","2026","2025_2026"]:
        for model in ["EXPANDING_PRIOR","CORE3_LOGIT_L2","CORE3_LOGIT_EN","ARAC"]:
            r=sdf[(sdf.period==per)&(sdf.scope=="FULL")&(sdf.model==model)].iloc[0]
            lines.append(
                f"| {per} | {model} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {100*r.false_call_rate:.2f}% | "
                f"{r.brier:.4f} | {r.logloss:.4f} | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["","## Frozen selective ARAC","",
              "| Period | Calls | Coverage | Accuracy | Balanced acc | False calls | UP recall | DOWN recall |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for per in ["2025","2026","2025_2026"]:
        r=sdf[(sdf.period==per)&(sdf.scope=="SELECTIVE")&(sdf.model=="ARAC")].iloc[0]
        lines.append(
            f"| {per} | {int(r.n_calls)} | {100*r.coverage:.2f}% | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {100*r.false_call_rate:.2f}% | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )

    lines += ["","## 2026 monthly ARAC","",
              "| Month | Scope | N/Calls | Coverage | Accuracy | Balanced acc | False calls |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for mo in sorted(mdf.month.unique()):
        for scope in ["FULL","SELECTIVE"]:
            r=mdf[(mdf.month==mo)&(mdf.scope==scope)].iloc[0]
            n=int(r.n if scope=="FULL" else r.n_calls)
            cov=1.0 if scope=="FULL" else r.coverage
            lines.append(
                f"| {mo} | {scope} | {n} | {100*cov:.2f}% | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {100*r.false_call_rate:.2f}% |"
            )
    lines += ["","No transport result was used to change ARAC-H3-v1."]
    (OUT/"ARAC_V1_TRANSPORT_RESULT.md").write_text("\n".join(lines)+"\n")
    print((OUT/"ARAC_V1_TRANSPORT_RESULT.md").read_text())

if __name__=="__main__":
    main()
