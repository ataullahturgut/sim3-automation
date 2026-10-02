from __future__ import annotations

import json, os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_short_horizon_global_xau_stage1_r2 as s1

OUT=Path(os.environ.get("OUT_DIR","gold_h3_arcr_v1_out"))
OUT.mkdir(parents=True,exist_ok=True)

SEED=20261001
BLOCK=5
RECENT_N=252
WEIGHTS=[1.00,0.75,0.50,0.25,0.00]  # global weight; recent = 1-w
THRESHOLDS=[0.50,0.52,0.54,0.56,0.58,0.60,0.62]
UP_RECALL_TOL=0.05
BRIER_TOL=0.005
CORE3=s1.CORE3

def make_global():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(C=1.0,solver="lbfgs",max_iter=3000,random_state=SEED))
    ])

def make_recent():
    return Pipeline([
        ("scale",StandardScaler()),
        ("model",LogisticRegression(
            C=1.0,solver="lbfgs",max_iter=3000,
            class_weight="balanced",random_state=SEED
        ))
    ])

def load_panel():
    return s1.load_panel()

def predict_sequence(df,start_year=2019,end_year=2026):
    test=df[
        df.forecast_issue_date.dt.year.between(start_year,end_year) &
        df.target_r3.notna() &
        df.target_end_date_h3.notna()
    ].copy().reset_index(drop=True)

    rows=[]
    for bs in range(0,len(test),BLOCK):
        te=test.iloc[bs:bs+BLOCK].copy()
        cutoff=te.feature_cutoff_date.min()

        tr=df[
            df.target_r3.notna() &
            df.target_end_date_h3.notna() &
            (df.target_end_date_h3<=cutoff)
        ].copy()
        if len(tr)<750:
            raise RuntimeError(f"TRAIN_TOO_SMALL n={len(tr)} cutoff={cutoff}")

        Xg,Xte=s1.fill_train_test(tr,te,CORE3)
        yg=(tr.target_r3.astype(float)>0).astype(int).to_numpy()
        mg=make_global(); mg.fit(Xg,yg)
        pg=mg.predict_proba(Xte)[:,1]

        rr=tr.tail(RECENT_N).copy()
        Xr,Xte2=s1.fill_train_test(rr,te,CORE3)
        yr=(rr.target_r3.astype(float)>0).astype(int).to_numpy()
        mr=make_recent(); mr.fit(Xr,yr)
        pr=mr.predict_proba(Xte2)[:,1]

        yte=(te.target_r3.astype(float)>0).astype(int).to_numpy()
        for r,y,a,b in zip(te.itertuples(),yte,pg,pr):
            rows.append({
                "forecast_issue_date":str(r.forecast_issue_date.date()),
                "target_end_date_h3":str(r.target_end_date_h3.date()),
                "year":int(r.forecast_issue_date.year),
                "month":str(r.forecast_issue_date.strftime("%Y-%m")),
                "y_up":int(y),
                "p_global":float(a),
                "p_recent252":float(b),
                "train_n":int(len(tr)),
                "recent_train_n":int(len(rr)),
            })
    return pd.DataFrame(rows)

def score(y,p,threshold):
    y=np.asarray(y,int)
    p=np.asarray(p,float)
    pred=(p>=threshold).astype(int)
    up=float(recall_score(y,pred,pos_label=1,zero_division=0))
    down=float(recall_score(y,pred,pos_label=0,zero_division=0))
    return {
        "n":int(len(y)),
        "accuracy":float(np.mean(pred==y)),
        "balanced_accuracy":float(balanced_accuracy_score(y,pred)),
        "false_call_rate":float(np.mean(pred!=y)),
        "up_recall":up,
        "down_recall":down,
        "min_side_recall":float(min(up,down)),
        "brier":float(np.mean((np.clip(p,1e-6,1-1e-6)-y)**2)),
        "logloss":float(log_loss(y,np.clip(p,1e-6,1-1e-6),labels=[0,1])),
        "mean_p_up":float(np.mean(p)),
        "prediction_std":float(np.std(p)),
        "predicted_up_rate":float(np.mean(pred)),
    }

def select_candidate(dev):
    y=dev.y_up.to_numpy(int)
    base=score(y,dev.p_global.to_numpy(float),0.50)
    rows=[]
    for wg in WEIGHTS:
        p=wg*dev.p_global.to_numpy(float)+(1-wg)*dev.p_recent252.to_numpy(float)
        for th in THRESHOLDS:
            m=score(y,p,th)
            elig=(
                m["up_recall"]+1e-12 >= base["up_recall"]-UP_RECALL_TOL and
                m["brier"] <= base["brier"]+BRIER_TOL+1e-12
            )
            rows.append({
                "global_weight":wg,
                "recent_weight":1-wg,
                "threshold":th,
                "eligible":bool(elig),
                **m
            })
    tab=pd.DataFrame(rows)
    elig=tab[tab.eligible].copy()
    if elig.empty:
        raise RuntimeError("NO_ELIGIBLE_ARCR_CANDIDATE")
    elig["threshold_distance"]=(elig.threshold-0.50).abs()
    elig=elig.sort_values(
        ["down_recall","balanced_accuracy","accuracy","brier","global_weight","threshold_distance"],
        ascending=[False,False,False,True,False,True]
    )
    best=elig.iloc[0].to_dict()
    return base,tab,best

def eval_period(g,wg,th,label):
    p=wg*g.p_global.to_numpy(float)+(1-wg)*g.p_recent252.to_numpy(float)
    return {"period":label,**score(g.y_up.to_numpy(int),p,th)}

def eval_baseline(g,label):
    return {"period":label,**score(g.y_up.to_numpy(int),g.p_global.to_numpy(float),0.50)}

def main():
    df=load_panel()
    led=predict_sequence(df,2019,2026)

    sel=led[led.year.between(2019,2021)].copy()
    base_sel,grid,best=select_candidate(sel)
    wg=float(best["global_weight"]); th=float(best["threshold"])

    grid.to_csv(OUT/"arcr_v1_selection_grid_2019_2021.csv",index=False)

    metrics=[]
    base_metrics=[]
    periods=[
        ("SELECT_2019_2021",led[led.year.between(2019,2021)]),
        ("CONFIRM_2022_2024",led[led.year.between(2022,2024)]),
        ("2022",led[led.year==2022]),
        ("2023",led[led.year==2023]),
        ("2024",led[led.year==2024]),
        ("2025",led[led.year==2025]),
        ("2026",led[led.year==2026]),
    ]
    for label,g in periods:
        metrics.append(eval_period(g,wg,th,label))
        base_metrics.append(eval_baseline(g,label))
    mdf=pd.DataFrame(metrics)
    bdf=pd.DataFrame(base_metrics)
    mdf.to_csv(OUT/"arcr_v1_metrics.csv",index=False)
    bdf.to_csv(OUT/"arcr_v1_baseline_metrics.csv",index=False)

    led["p_arcr"]=wg*led.p_global+(1-wg)*led.p_recent252
    led["arcr_pred_up"]=(led.p_arcr>=th).astype(int)
    led["global_pred_up"]=(led.p_global>=.5).astype(int)
    led["arcr_correct"]=(led.arcr_pred_up==led.y_up)
    led["global_correct"]=(led.global_pred_up==led.y_up)
    led.to_csv(OUT/"arcr_v1_predictions.csv",index=False)

    y26=led[led.year==2026].copy()
    monthly=[]
    for mo,g in y26.groupby("month"):
        monthly.append(eval_period(g,wg,th,mo))
        monthly[-1]["scope"]="ARCR"
        z=eval_baseline(g,mo); z["scope"]="GLOBAL_L2"; monthly.append(z)
    mon=pd.DataFrame(monthly)
    mon.to_csv(OUT/"arcr_v1_2026_monthly.csv",index=False)

    result={
        "schema":"GOLD_H3_ARCR_V1",
        "selection_window":"2019-2021",
        "confirmation_window":"2022-2024",
        "selected":{
            "global_weight":wg,
            "recent_weight":1-wg,
            "threshold":th,
            "selection_metrics":{k:v for k,v in best.items() if k not in ["threshold_distance"]},
        },
        "selection_baseline":base_sel,
        "metrics":mdf.to_dict(orient="records"),
        "baseline_metrics":bdf.to_dict(orient="records"),
    }
    (OUT/"arcr_v1_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=[
        "# GOLD H3 — ARCR-H3-v1 RESULT","",
        f"Selected on 2019-2021: global weight **{wg:.2f}**, recent252 weight **{1-wg:.2f}**, UP threshold **{th:.2f}**.","",
        "## Confirmation 2022-2024","",
        "| Model | Accuracy | Balanced acc | UP recall | DOWN recall | Min-side recall | Brier | False calls |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    c=mdf[mdf.period=="CONFIRM_2022_2024"].iloc[0]
    b=bdf[bdf.period=="CONFIRM_2022_2024"].iloc[0]
    lines.append(f"| GLOBAL L2 baseline | {100*b.accuracy:.2f}% | {100*b.balanced_accuracy:.2f}% | {100*b.up_recall:.2f}% | {100*b.down_recall:.2f}% | {100*b.min_side_recall:.2f}% | {b.brier:.4f} | {100*b.false_call_rate:.2f}% |")
    lines.append(f"| ARCR-H3-v1 | {100*c.accuracy:.2f}% | {100*c.balanced_accuracy:.2f}% | {100*c.up_recall:.2f}% | {100*c.down_recall:.2f}% | {100*c.min_side_recall:.2f}% | {c.brier:.4f} | {100*c.false_call_rate:.2f}% |")

    lines += ["","## Annual / transport diagnostics","",
              "| Period | Model | Accuracy | Balanced acc | UP recall | DOWN recall | Brier |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for per in ["2022","2023","2024","2025","2026"]:
        r=mdf[mdf.period==per].iloc[0]; q=bdf[bdf.period==per].iloc[0]
        lines.append(f"| {per} | GLOBAL L2 | {100*q.accuracy:.2f}% | {100*q.balanced_accuracy:.2f}% | {100*q.up_recall:.2f}% | {100*q.down_recall:.2f}% | {q.brier:.4f} |")
        lines.append(f"| {per} | ARCR | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
    lines += ["","2019-2021 alone selected the blend and threshold. Later periods did not modify V1."]
    (OUT/"ARCR_V1_RESULT.md").write_text("\n".join(lines)+"\n")
    print("ARCR_V1_RESULT="+json.dumps(result,separators=(",",":")))
    print((OUT/"ARCR_V1_RESULT.md").read_text())

if __name__=="__main__":
    main()
