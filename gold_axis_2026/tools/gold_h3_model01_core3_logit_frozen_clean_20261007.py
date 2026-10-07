from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_clean_core_rebuild_v1 as clean
import gold_h3_nova_v1 as nova

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"
OUT = AX / "H3_MODEL01_CORE3_LOGIT_FROZEN_CLEAN_OUT"
OUT.mkdir(exist_ok=True)

BLOCK = 5
SEED = 20261001
FEATURES = list(nova.CORE3)


def model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def fill(train, test):
    a = train[FEATURES].copy()
    b = test[FEATURES].copy()
    for c in FEATURES:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a, b


def metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-9, 1-1e-9)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0,1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p-y)**2)),
        "logloss": float(log_loss(y, p, labels=[0,1])),
        "up_recall": float(tp/max(tp+fn,1)),
        "down_recall": float(tn/max(tn+fp,1)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def dev_replay(df):
    dev = df[
        (df["role"] == "DEV")
        & df["target_r3"].notna()
        & df["target_end_date_h3"].notna()
    ].copy().sort_values("feature_cutoff_date").reset_index(drop=True)

    rows = []
    for block_id in range(0, len(dev), BLOCK):
        te = dev.iloc[block_id:block_id+BLOCK].copy()
        start = te["feature_cutoff_date"].min()

        tr = df[
            df["target_r3"].notna()
            & df["target_end_date_h3"].notna()
            & (df["target_end_date_h3"] <= start)
            & (df["forecast_issue_date"] < pd.Timestamp("2025-01-01"))
        ].copy()

        if len(tr) < 252:
            raise RuntimeError(f"DEV_TRAIN_TOO_SMALL n={len(tr)} start={start}")

        Xtr, Xte = fill(tr, te)
        ytr = (tr.target_r3.astype(float) > 0).astype(int)
        m = model()
        m.fit(Xtr, ytr)
        pp = m.predict_proba(Xte)[:,1]

        for r, p in zip(te.itertuples(index=False), pp):
            y = int(float(r.target_r3) > 0)
            rows.append({
                "evaluation": "DEV_CAUSAL_BLOCK5",
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.forecast_issue_date.year),
                "target_r3": float(r.target_r3),
                "y_up": y,
                "p_up": float(p),
                "pred_direction": "UP" if p >= .5 else "DOWN",
                "actual_direction": "UP" if y else "DOWN",
                "correct": bool((p >= .5) == bool(y)),
                "train_n": int(len(tr)),
            })
    return pd.DataFrame(rows)


def frozen_transport(df):
    eligible = df[df.target_r3.notna() & df.target_end_date_h3.notna()].copy()
    tr = eligible[eligible.target_end_date_h3 <= pd.Timestamp("2024-12-31")].copy()
    te = eligible[
        eligible.forecast_issue_date.dt.year.isin([2025, 2026])
        & (eligible.target_end_date_h3 <= pd.Timestamp("2026-09-30"))
    ].copy().sort_values("forecast_issue_date")

    Xtr, Xte = fill(tr, te)
    ytr = (tr.target_r3 > 0).astype(int)
    m = model()
    m.fit(Xtr, ytr)
    pp = m.predict_proba(Xte)[:,1]

    rows = []
    for r, p in zip(te.itertuples(index=False), pp):
        y = int(float(r.target_r3) > 0)
        rows.append({
            "evaluation": "FROZEN_PRE2025_FIT",
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.forecast_issue_date.year),
            "target_r3": float(r.target_r3),
            "y_up": y,
            "p_up": float(p),
            "pred_direction": "UP" if p >= .5 else "DOWN",
            "actual_direction": "UP" if y else "DOWN",
            "correct": bool((p >= .5) == bool(y)),
            "train_n": int(len(tr)),
        })
    return pd.DataFrame(rows), int(len(tr)), str(tr.target_end_date_h3.max().date())


def main():
    df, audit = clean.patched_readiness()

    required = ["role","feature_cutoff_date","forecast_issue_date","target_end_date_h3","target_r3"] + FEATURES
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise RuntimeError(f"MISSING {missing}")

    dev = dev_replay(df)
    trn, train_n, train_last = frozen_transport(df)
    pred = pd.concat([dev, trn], ignore_index=True)
    pred.to_csv(OUT/"predictions.csv", index=False)

    rows = []
    specs = [
        ("DEV_2022_2024", dev.year.between(2022, 2024), dev),
        ("2022", dev.year == 2022, dev),
        ("2023", dev.year == 2023, dev),
        ("2024", dev.year == 2024, dev),
        ("FROZEN_2025", trn.year == 2025, trn),
        ("FROZEN_2026", trn.year == 2026, trn),
        ("FROZEN_2025_2026", trn.year.isin([2025, 2026]), trn),
    ]
    for label, mask, src in specs:
        z = src[mask].copy()
        if len(z):
            rows.append({"period": label, **metrics(z.y_up, z.p_up)})
    mdf = pd.DataFrame(rows)
    mdf.to_csv(OUT/"metrics.csv", index=False)

    summary = {
        "status": "H3_MODEL01_CORE3_LOGIT_FROZEN_CLEAN_COMPLETE",
        "model": "CLASSICAL_CORE3_LOGISTIC_L2",
        "target": "H3 direction = sign(log(P[t+3]/P[t]))",
        "horizon_semantics": "third retained Gold observation; not 3 calendar days",
        "features": FEATURES,
        "dev_contract": "2022-2024 chronological block-5; train only on H3 outcomes matured by block start",
        "transport_contract": "single model fit on all H3 rows matured by 2024-12-31; unchanged through 2025 and 2026",
        "frozen_train_n": train_n,
        "frozen_train_last_target_end": train_last,
        "threshold": 0.5,
        "integrity_patch": audit,
        "metrics": mdf.to_dict("records"),
        "supersedes_for_model01": "GOLD_H3_MODEL01_CORE3_LOGIT_* first 2026-10-07 run used NOVA A0 expanding refit and is not the classical frozen transport contract",
    }
    (OUT/"summary.json").write_text(json.dumps(summary, indent=2, default=str)+"\n")

    lines = [
        "# H3 MODEL 01 — CLASSICAL CORE3 LOGISTIC — CORRECT FROZEN CONTRACT",
        "",
        "**Status:** COMPLETE / MODEL-01 AUTHORITY",
        "",
        "**Target:** H3 direction = sign(log(P[t+3]/P[t]))",
        "",
        "- t+3 = third retained Gold observation; not 3 calendar days.",
        "- Features = Gold/Silver/Platinum CORE3.",
        "- Model = StandardScaler + LogisticRegression(L2, C=1.0).",
        "- DEV 2022-2024 = causal block-5 replay using only already-matured H3 outcomes.",
        f"- Frozen transport fit = {train_n} rows; last train target end = {train_last}.",
        "- 2025/2026 are scored with that unchanged pre-2025 fit.",
        "- Clean chain includes the confirmed 2026-02-27 integrity correction.",
        "",
        "| Period | N | Accuracy | BA | Brier | UP recall | DOWN recall |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in mdf.itertuples(index=False):
        lines.append(
            f"| {r.period} | {r.n} | {100*r.accuracy:.2f}% | "
            f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
            f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
        )
    lines += [
        "",
        "The earlier 2026-10-07 Model-01 trial based on NOVA A0 expanding refits is superseded for the classical CORE3 frozen-transport question."
    ]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print((OUT/"result.md").read_text())


if __name__ == "__main__":
    main()
