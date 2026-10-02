from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_iris_v1_robust_out"))
OUT.mkdir(parents=True, exist_ok=True)
PARENT_METRICS = ROOT / "gold_axis_2026" / "GOLD_H3_IRIS_V1_METRICS_2026-10-02.csv"

SEED = 20261002
PATH = list(iris.PATH)


def build_path_anchors(hourly, anchor_hour: int):
    q = hourly.copy().sort_values("ts").reset_index(drop=True)
    q["ts_ny"] = q.ts.dt.tz_convert(iris.TZ)
    q["local_date"] = q.ts_ny.dt.date
    q["local_hour"] = q.ts_ny.dt.hour
    q["local_minute"] = q.ts_ny.dt.minute
    q["logp"] = np.log(q.value.astype(float))
    q["hr"] = q.logp.diff()

    for h in [1, 3, 6, 12, 24, 48]:
        q[f"h_ret_{h}"] = q.logp - q.logp.shift(h)
    q["h_lag2"] = q.hr.shift(2)

    first_log = q.groupby("local_date")["logp"].transform("first")
    q["h_session_ret"] = q.logp - first_log

    a = q[(q.local_hour == anchor_hour) & (q.local_minute == 0)].copy()
    a = a.sort_values("ts").drop_duplicates("local_date", keep="last")
    a = a.dropna(subset=PATH).copy()
    return a[["local_date", "ts"] + PATH].reset_index(drop=True)


def panel_for(ledger, anchors):
    p = ledger.merge(
        anchors,
        left_on="feature_date",
        right_on="local_date",
        how="inner",
        validate="many_to_one",
    )
    p = p.dropna(subset=["y_up", "target_r3", "p_A1_arcr", "base_logit"] + PATH).copy()
    p["year"] = p.forecast_issue_date.dt.year.astype(int)
    p["month"] = p.forecast_issue_date.dt.to_period("M").astype(str)
    return p.sort_values("forecast_issue_date").reset_index(drop=True)


def make_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def fill_xy(tr, te, features):
    a = tr[features].copy()
    b = te[features].copy()
    for c in features:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


def metric(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y)),
        "accuracy": float(np.mean(pred == y)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "up_recall": float(recall_score(y, pred, pos_label=1, zero_division=0)),
        "down_recall": float(recall_score(y, pred, pos_label=0, zero_division=0)),
        "false_call_rate": float(np.mean(pred != y)),
    }


def run(panel, tag, features):
    test = panel[panel.year.between(2023, 2026)].copy()
    rows = []
    for mo in sorted(test.month.unique()):
        te = test[test.month == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < te.forecast_issue_date.min())
        ].copy()
        if len(tr) < 180:
            raise RuntimeError(f"TRAIN_TOO_SMALL {tag} {mo} {len(tr)}")
        Xtr, Xte = fill_xy(tr, te, features)
        ytr = tr.y_up.astype(int).to_numpy()
        m = make_model()
        m.fit(Xtr, ytr)
        pp = m.predict_proba(Xte)[:, 1]
        for r, p in zip(te.itertuples(), pp):
            rows.append({
                "tag": tag,
                "forecast_issue_date": r.forecast_issue_date,
                "feature_cutoff_date": r.feature_cutoff_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "p_up": float(p),
                "p_base_a1": float(r.p_A1_arcr),
            })
    return pd.DataFrame(rows)


def score(led):
    out = []
    for tag, g0 in led.groupby("tag"):
        for label, mask in [
            ("2023", g0.year == 2023),
            ("2024", g0.year == 2024),
            ("2025", g0.year == 2025),
            ("2026", g0.year == 2026),
            ("2023-2024", g0.year.isin([2023, 2024])),
            ("2025-2026", g0.year.isin([2025, 2026])),
        ]:
            g = g0[mask]
            if not g.empty:
                out.append({"tag": tag, "period": label, **metric(g.y_up, g.p_up)})
    return pd.DataFrame(out)


def monthly_stability(g):
    rows = []
    for mo, z in g.groupby("month"):
        rows.append({"month": mo, **metric(z.y_up, z.p_up)})
    m = pd.DataFrame(rows)
    if m.empty:
        return {}, m
    summary = {
        "months": int(len(m)),
        "months_accuracy_gt_50": int((m.accuracy > 0.50).sum()),
        "share_accuracy_gt_50": float((m.accuracy > 0.50).mean()),
        "months_balanced_gt_50": int((m.balanced_accuracy > 0.50).sum()),
        "share_balanced_gt_50": float((m.balanced_accuracy > 0.50).mean()),
        "median_monthly_accuracy": float(m.accuracy.median()),
        "worst_month_accuracy": float(m.accuracy.min()),
        "best_month_accuracy": float(m.accuracy.max()),
    }
    return summary, m


def main():
    ledger = iris.load_ledger()
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("IRIS_PARENT_SOURCE_BRIDGE_NOT_PASS")

    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)

    a16 = build_path_anchors(hourly, 16)
    a15 = build_path_anchors(hourly, 15)

    prev16 = a16.copy().sort_values("ts").reset_index(drop=True)
    for c in PATH:
        prev16[c] = prev16[c].shift(1)
    prev16 = prev16.dropna(subset=PATH).copy()

    p16 = panel_for(ledger, a16)
    p15 = panel_for(ledger, a15)
    ppv = panel_for(ledger, prev16)

    ledgers = []

    # Exact parent recomputation
    ledgers.append(run(p16, "A1_PATH_16", ["base_logit"] + PATH))
    ledgers.append(run(p15, "A1_PATH_15", ["base_logit"] + PATH))
    ledgers.append(run(ppv, "A1_PATH_PREV16", ["base_logit"] + PATH))
    ledgers.append(run(p16, "PATH_ONLY_16", PATH))
    ledgers.append(run(p16, "A1_RET12_16", ["base_logit", "h_ret_12"]))

    # Same-row A1 baseline for reference
    z = p16[p16.year.between(2023, 2026)].copy()
    ledgers.append(pd.DataFrame({
        "tag": "BASE_A1",
        "forecast_issue_date": z.forecast_issue_date,
        "feature_cutoff_date": z.feature_cutoff_date,
        "target_end_date_h3": z.target_end_date_h3,
        "year": z.year.astype(int),
        "month": z.month.astype(str),
        "y_up": z.y_up.astype(int),
        "p_up": z.p_A1_arcr.astype(float),
        "p_base_a1": z.p_A1_arcr.astype(float),
    }))

    led = pd.concat(ledgers, ignore_index=True)
    led.to_csv(OUT / "iris_v1_robustness_predictions.csv", index=False)

    mdf = score(led)
    mdf.to_csv(OUT / "iris_v1_robustness_metrics.csv", index=False)

    # Parent reproduction check.
    parent = pd.read_csv(PARENT_METRICS)
    checks = []
    for yr in ["2023", "2024", "2025", "2026"]:
        a = mdf[(mdf.tag == "A1_PATH_16") & (mdf.period == yr)].iloc[0]
        b = parent[(parent.model == "A1_PLUS_PATH") & (parent.period.astype(str) == yr)].iloc[0]
        checks.append({
            "period": yr,
            "delta_accuracy": float(a.accuracy - b.accuracy),
            "delta_balanced_accuracy": float(a.balanced_accuracy - b.balanced_accuracy),
            "delta_brier": float(a.brier - b.brier),
        })
    cdf = pd.DataFrame(checks)
    cdf.to_csv(OUT / "iris_v1_parent_reproduction_check.csv", index=False)

    monthly_summaries = []
    monthly_ledgers = []
    for yr in [2023, 2024, 2025, 2026]:
        g = led[(led.tag == "A1_PATH_16") & (led.year == yr)].copy()
        summ, mon = monthly_stability(g)
        monthly_summaries.append({"year": yr, **summ})
        if not mon.empty:
            mon["year"] = yr
            monthly_ledgers.append(mon)
    ms = pd.DataFrame(monthly_summaries)
    ms.to_csv(OUT / "iris_v1_monthly_stability_summary.csv", index=False)
    if monthly_ledgers:
        pd.concat(monthly_ledgers, ignore_index=True).to_csv(
            OUT / "iris_v1_monthly_stability_detail.csv", index=False
        )

    def rr(tag, period):
        q = mdf[(mdf.tag == tag) & (mdf.period == period)]
        return None if q.empty else q.iloc[0]

    summary = {
        "schema": "IRIS_H3_V1_ROBUSTNESS_AUDIT",
        "bridge": bridge,
        "api_calls": int(api_calls),
        "parent_reproduction_max_abs_delta_accuracy": float(cdf.delta_accuracy.abs().max()),
        "metrics": mdf.to_dict(orient="records"),
        "monthly_stability": ms.to_dict(orient="records"),
    }
    (OUT / "iris_v1_robustness_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# IRIS-H3 V1 — ROBUSTNESS / TIMING AUDIT", "",
        f"Parent reproduction max |Δ accuracy|: **{cdf.delta_accuracy.abs().max():.12f}**.", "",
        "## Timing / ablation comparison", "",
        "| Variant | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2023", "2024", "2025", "2026", "2023-2024", "2025-2026"]:
        for tag in ["BASE_A1", "A1_PATH_16", "A1_PATH_15", "A1_PATH_PREV16", "PATH_ONLY_16", "A1_RET12_16"]:
            r = rr(tag, period)
            if r is None:
                continue
            lines.append(
                f"| {tag} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["", "## Monthly stability of frozen parent", "",
              "| Year | Months | Acc >50 | Share | BA >50 | Share | Median acc | Worst acc | Best acc |",
              "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in ms.itertuples():
        lines.append(
            f"| {int(r.year)} | {int(r.months)} | {int(r.months_accuracy_gt_50)} | "
            f"{100*r.share_accuracy_gt_50:.1f}% | {int(r.months_balanced_gt_50)} | "
            f"{100*r.share_balanced_gt_50:.1f}% | {100*r.median_monthly_accuracy:.1f}% | "
            f"{100*r.worst_month_accuracy:.1f}% | {100*r.best_month_accuracy:.1f}% |"
        )

    # Fixed interpretation based on diagnostics, not model reselection.
    lines += ["", "## Interpretation rule", "",
              "This audit cannot replace the frozen A1_PATH_16 parent. "
              "The key checks are whether 15:00 retains signal, previous-anchor placebo weakens, "
              "PATH-only remains informative, and RET12-only does not fully explain the parent result."]

    (OUT / "IRIS_V1_ROBUSTNESS_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "IRIS_V1_ROBUSTNESS_RESULT.md").read_text())


if __name__ == "__main__":
    main()
