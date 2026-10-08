"""PIT-ordered, low-capacity overnight magnitude probability calibration.

Research execution: 2025 archive has been examined, NOT untouched OOS.
The input is a frozen file of previous-matured overnight lag scores; this
script NEVER imports 17:00 news or next-day outcomes as features.

At date t: log-score from previous completed 5/20/60 nights.
Target: |overnight log return of t| >= 0.01.
Train: growing matured preceding targets for 2023-2024; freeze 2025
fit to the entire <=2024 eligible panel. First 120 scored rows warm up.
Compare probabilistic model to Laplace-smoothed historical event rate.

Exact 2D Newton L2 logistic fit, 5-unit slope penalty; intercept unpenalized.
This is a challenger, not promotion to execution or revised PRAMV.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, log_loss

AX = Path(__file__).resolve().parents[1]
INPUT = AX / "GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv"
OUT = AX / "GOLD_EXECUTION_TAIL1_PROBABILITY_PREDICTIONS_2026-10-08.csv"
METRICS = AX / "GOLD_EXECUTION_TAIL1_PROBABILITY_METRICS_2026-10-08.csv"
MIN_TRAIN = 120
L2_SLOPE = 5.0

def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -25, 25)))

def logit(p):
    p = float(np.clip(p, 1e-8, 1 - 1e-8))
    return np.log(p / (1 - p))

def fit_predict(history, row):
    x = np.log(history.risk_score.to_numpy(dtype=float))
    y = history.tail1.to_numpy(dtype=float)
    mean = float(x.mean())
    stdev = float(np.sqrt(np.mean((x - mean)**2)))
    assert stdev > 0.0
    xx = (x - mean) / stdev
    pbar = (1.0 + float(y.sum())) / (2.0 + len(y))
    intercept = logit(pbar)
    slope = 0.0
    for _ in range(40):
        pp = sigmoid(intercept + slope * xx)
        resid = y - pp
        ww = pp * (1.0 - pp)
        g0 = float(resid.sum())
        g1 = float((resid * xx).sum() - L2_SLOPE * slope)
        h00 = float(ww.sum() + 1e-5)
        h01 = float((ww * xx).sum())
        h11 = float((ww * xx * xx).sum() + L2_SLOPE)
        det = h00 * h11 - h01 * h01
        assert det > 0.0
        delta0 = (g0 * h11 - g1 * h01) / det
        delta1 = (g1 * h00 - g0 * h01) / det
        intercept += delta0
        slope += delta1
        if delta0*delta0 + delta1*delta1 < 1e-10:
            break
    pred = float(sigmoid(intercept + slope *
                         (np.log(float(row.risk_score)) - mean) / stdev))
    return pred, pbar, slope

def main():
    q = pd.read_csv(INPUT).sort_values("date").reset_index(drop=True)
    assert len(q) == 709
    assert q.groupby("year").size().to_dict() == {2023:196, 2024:259, 2025:254}
    assert q.date.is_unique
    assert np.isfinite(q.risk_score).all()
    # The 2025 records are used for evaluation ONLY.
    train_frozen = q[q.year <= 2024].copy()
    assert len(train_frozen) == 455
    records = []
    for i, row in q.iterrows():
        history = train_frozen if int(row.year) == 2025 else q.iloc[:i]
        if len(history) < MIN_TRAIN:
            continue
        assert (history.date < row.date).all()
        pred, baseline, slope = fit_predict(history, row)
        records.append({
            "date":row.date, "year":int(row.year), "train_n":len(history),
            "score":float(row.risk_score), "tail1":int(row.tail1),
            "target_return":float(row.target_log_return),
            "prob_tail1_calibrated":pred, "prob_tail1_historical_rate":baseline,
            "fitted_slope":slope})
    preds = pd.DataFrame(records)
    assert preds.groupby("year").size().to_dict() == {2023:76,2024:259,2025:254}
    assert np.isfinite(preds.prob_tail1_calibrated).all()
    preds.to_csv(OUT, index=False)

    stats = []
    for year, g in preds.groupby("year"):
        y = g.tail1.to_numpy(int)
        p = g.prob_tail1_calibrated.to_numpy(float)
        base = g.prob_tail1_historical_rate.to_numpy(float)
        stats.append({
            "year":int(year), "n":len(g), "events":int(y.sum()),
            "brier":float(brier_score_loss(y,p)),
            "historical_rate_brier":float(brier_score_loss(y,base)),
            "brier_skill_improvement":float(brier_score_loss(y,base) - brier_score_loss(y,p)),
            "log_loss":float(log_loss(y,p)),
            "historical_rate_log_loss":float(log_loss(y,base)),
            "roc_auc":float(roc_auc_score(y,p)),
            "average_precision":float(average_precision_score(y,p)),
            "avg_probability":float(p.mean()),
            "avg_historical_rate":float(base.mean())})
    metrics = pd.DataFrame(stats)
    # Guards from independently reproduced 2026-10-08 research replay.
    assert abs(float(metrics.loc[metrics.year.eq(2025),"brier"].iloc[0]) - 0.1392909699917062) < 1e-8
    assert abs(float(metrics.loc[metrics.year.eq(2025),"historical_rate_brier"].iloc[0]) - 0.14731713071678942) < 1e-8
    metrics.to_csv(METRICS, index=False)
    print(metrics.to_string(index=False))
    print("Saved", OUT, METRICS)

if __name__ == "__main__":
    main()
