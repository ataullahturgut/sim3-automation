"""Source-timestamp-safe overnight signed-tail probability research.

Two disjoint event heads:
  NEG: completed t overnight log return <= -0.0100;
  POS: completed t overnight log return >= +0.0100.
Each head is estimated independently. Their probabilities are NOT an
overnight full-sign UP/DOWN classifier.

Input risk_score is built only from 5/20/60 PREVIOUS MATURED overnight returns.
GVZ D-1 is joined from Cboe date strictly earlier than the issue date.
2023-2024: expanding 120-row warm-up on matured outcomes.
2025: frozen trained sample = 2023-2024 risk-ready 455 rows.
2025 was examined during exploratory hypothesis selection => NOT untouched OOS.
"""
from pathlib import Path
import numpy as np
import pandas as pd

AX = Path(__file__).resolve().parents[1]
RISK = AX / "GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv"
GVZ = AX / "GOLD_GVZCLS_RAW_2021_2025.csv"
RATES = AX / "GOLD_DGS2_RAW_2022_2025.csv"
OUT = AX / "GOLD_EXECUTION_GVZ_SIGNED_TAIL_PREDICTIONS_2026-10-08.csv"
METRICS = AX / "GOLD_EXECUTION_GVZ_SIGNED_TAIL_METRICS_2026-10-08.csv"
MIN_HISTORY = 120
RIDGE = 5.0

def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -25., 25.)))

def regularized_logit_prediction(history, current, target, features):
    x = history[features].to_numpy(float)
    y = history[target].to_numpy(int)
    mu = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0] = 1.
    xx = np.c_[np.ones(len(x)), (x - mu) / scale]
    prior = (1 + y.sum()) / (2 + len(y))
    beta = np.r_[np.log(prior / (1. - prior)), np.zeros(len(features))]
    for _ in range(40):
        p = sigmoid(xx @ beta)
        err = y - p
        w = p * (1-p)
        grad = xx.T @ err
        grad[1:] -= RIDGE * beta[1:]
        hess = xx.T @ (xx * w[:,None])
        hess[1:,1:] += RIDGE * np.eye(len(features))
        hess[0,0] += 1e-5
        step = np.linalg.solve(hess, grad)
        beta += step
        if step @ step < 1e-10:
            break
    row = current[features].to_numpy(float)
    test = np.r_[1., (row-mu)/scale]
    return float(sigmoid(test @ beta))

def load():
    a = pd.read_csv(RISK).sort_values("date").reset_index(drop=True)
    assert a.groupby("year").size().to_dict() == {2023:196,2024:259,2025:254}
    a["date"] = pd.to_datetime(a.date)
    gvz = pd.read_csv(GVZ).rename(columns={"date":"gvz_date","value":"gvz_last"})
    gvz["gvz_date"] = pd.to_datetime(gvz.gvz_date)
    rates = pd.read_csv(RATES).rename(columns={"date":"rate_date","value":"rate_last"})
    rates["rate_date"] = pd.to_datetime(rates.rate_date)
    gvz = gvz.sort_values("gvz_date")
    rates = rates.sort_values("rate_date")
    a = pd.merge_asof(a.sort_values("date"),gvz,left_on="date",right_on="gvz_date",
                      direction="backward",allow_exact_matches=False)
    a = pd.merge_asof(a.sort_values("date"),rates,left_on="date",right_on="rate_date",
                      direction="backward",allow_exact_matches=False)
    assert a.gvz_last.notna().all() and a.rate_last.notna().all()
    assert a.gvz_date.lt(a.date).all() and a.rate_date.lt(a.date).all()
    a["logscore"] = np.log(a.risk_score)
    a["loggvz"] = np.log(a.gvz_last)
    a["target_down"] = (a.target_log_return <= -.01).astype(int)
    a["target_up"] = (a.target_log_return >= .01).astype(int)
    assert ((a.target_down+a.target_up)<=1).all()
    return a

def main():
    a = load()
    frozen = a[a.year <= 2024]
    assert len(frozen)==455
    output = []
    models = {"SCORE":["logscore"],
              "GVZ":["loggvz"],
              "SCORE_GVZ":["logscore","loggvz"]}
    for i, row in a.iterrows():
        hist = frozen if row.year == 2025 else a.iloc[:i]
        if len(hist) < MIN_HISTORY:
            continue
        assert hist.date.max() < row.date
        item = {"date":row.date.strftime("%Y-%m-%d"),
                "year":int(row.year), "n_train":len(hist),
                "gvz_date":row.gvz_date.strftime("%Y-%m-%d"),
                "gvz_D1":float(row.gvz_last),
                "score":float(row.risk_score),
                "ret_target":float(row.target_log_return),
                "target_down":int(row.target_down),
                "target_up":int(row.target_up)}
        for label in ("down","up"):
            t = "target_"+label
            item["p_"+label+"_BASE"] = (1 + hist[t].sum())/(2+len(hist))
            for name, feat in models.items():
                item["p_"+label+"_"+name] = regularized_logit_prediction(hist,row,t,feat)
        output.append(item)
    out = pd.DataFrame(output)
    assert out.groupby("year").size().to_dict()=={2023:76,2024:259,2025:254}
    assert len(out)==589 and out.date.is_unique
    out.to_csv(OUT,index=False)
    results=[]
    for year,g in out.groupby("year"):
        for sign in ("down","up"):
            y=g["target_"+sign].to_numpy(int)
            from sklearn.metrics import roc_auc_score
            for method in ("BASE","SCORE","GVZ","SCORE_GVZ"):
                p=g["p_"+sign+"_"+method].to_numpy(float)
                results.append({"year":year,"tail":sign,"method":method,"n":len(g),
                                "events":int(y.sum()),
                                "brier":float(np.mean((p-y)**2)),
                                "roc_auc":float(roc_auc_score(y,p)),
                                "mean_p":float(p.mean())})
    m=pd.DataFrame(results)
    # Exact independently calculated point-in-time benchmark guards.
    checks = [
        (2025,"down","SCORE_GVZ",0.057340),
        (2025,"down","SCORE",0.059657),
        (2025,"down","GVZ",0.057604),
        (2024,"down","SCORE_GVZ",0.050988),
        (2025,"up","SCORE_GVZ",0.094873)
    ]
    for year,tail,method,expected in checks:
        r=m[(m.year==year)&(m.tail==tail)&(m.method==method)].iloc[0]
        assert abs(float(r.brier)-expected)<.000005,(year,tail,method,float(r.brier))
    m.to_csv(METRICS,index=False)
    print(m.to_string(index=False))
    print("Saved",OUT,METRICS)

if __name__=="__main__":
    main()
