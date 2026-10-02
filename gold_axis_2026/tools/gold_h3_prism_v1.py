from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pywt
from scipy.optimize import minimize
from scipy.special import expit

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_prism_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

AURORA = ROOT / "gold_axis_2026" / "GOLD_H3_AURORA_V1_PREDICTIONS_2026-10-02.csv"

LAMBDA_GRID = [1.0, 10.0, 50.0]
LATENT_COLS = [f"wv_{i:02d}" for i in range(16)] + ["log_rv48", "jump48"]
SEED = 20261002


def metrics(y, p):
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
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def paa4(x):
    x = np.asarray(x, float)
    if len(x) != 48:
        raise ValueError(len(x))
    return x.reshape(4, 12).mean(axis=1)


def load_hourly():
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError(f"PRISM_SOURCE_BRIDGE_FAIL {bridge}")
    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    h = pd.concat([hist, ext], ignore_index=True)
    h = h.sort_values("ts").drop_duplicates("ts", keep="last").reset_index(drop=True)
    h["ts_ny"] = h.ts.dt.tz_convert(iris.TZ)
    h["local_date"] = pd.to_datetime(h.ts_ny.dt.date)
    h["local_hour"] = h.ts_ny.dt.hour
    h["local_minute"] = h.ts_ny.dt.minute
    h["logp"] = np.log(h.value.astype(float))
    return h, bridge, api_calls


def wavelet_latent(rets):
    r = np.asarray(rets, float)
    if len(r) != 48 or not np.isfinite(r).all():
        raise ValueError("bad 48h returns")
    rv = float(np.sqrt(np.sum(r * r)))
    rn = r / (rv + 1e-12)

    coeffs = pywt.swt(rn, "db2", level=3, trim_approx=False, norm=True)
    highest_approx = coeffs[0][0]
    details = [pair[1] for pair in coeffs]
    arrays = [highest_approx] + details

    latent = []
    for arr in arrays:
        latent.extend(paa4(arr).tolist())

    jump = float(np.max(np.abs(r)) / (rv + 1e-12))
    latent.extend([math.log(rv + 1e-12), jump])
    return np.asarray(latent, float)


def build_panel():
    base = pd.read_csv(AURORA)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        base[c] = pd.to_datetime(base[c], errors="raise")
    base = base.sort_values("forecast_issue_date").reset_index(drop=True)

    h, bridge, api_calls = load_hourly()
    q = h[(h.local_minute == 0)].copy().sort_values("ts").reset_index(drop=True)

    anchor_idx = {}
    for i, r in q.iterrows():
        if int(r.local_hour) == 16:
            anchor_idx[pd.Timestamp(r.local_date)] = i

    rows = []
    missing = []
    for r in base.itertuples():
        d = pd.Timestamp(r.feature_cutoff_date)
        i = anchor_idx.get(d)
        if i is None or i < 48:
            missing.append(str(d.date()))
            continue
        vals = q.iloc[i-48:i+1].logp.to_numpy(float)
        rets = np.diff(vals)
        if len(rets) != 48 or not np.isfinite(rets).all():
            missing.append(str(d.date()))
            continue
        z = wavelet_latent(rets)
        row = {
            "feature_cutoff_date": d,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_aurora": float(r.p_aurora),
        }
        for j, v in enumerate(z):
            row[LATENT_COLS[j]] = float(v)
        rows.append(row)

    panel = pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)
    if len(panel) != len(base):
        raise RuntimeError(f"PRISM_EMBEDDING_MATCH_FAIL base={len(base)} panel={len(panel)} missing={missing[:20]}")
    return panel, bridge, api_calls


def standardize(tr, te):
    X = tr[LATENT_COLS].to_numpy(float)
    T = te[LATENT_COLS].to_numpy(float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd = np.where(sd > 1e-8, sd, 1.0)
    return (X - mu) / sd, (T - mu) / sd, mu, sd


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    return np.log(p / (1.0 - p))


def fit_offset_logistic(X, y, offset, lam):
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    offset = np.asarray(offset, float)

    def fg(beta):
        eta = offset + X @ beta
        loss = np.sum(np.logaddexp(0.0, eta) - y * eta) + 0.5 * lam * np.dot(beta, beta)
        pr = expit(eta)
        grad = X.T @ (pr - y) + lam * beta
        return float(loss), grad

    init = np.zeros(X.shape[1], float)
    res = minimize(
        lambda b: fg(b)[0],
        init,
        jac=lambda b: fg(b)[1],
        method="L-BFGS-B",
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    if not res.success:
        raise RuntimeError(f"PRISM_OPT_FAIL {res.message}")
    return res.x


def walk_forward(panel, lam):
    test = panel[
        (panel.forecast_issue_date >= pd.Timestamp("2022-07-01"))
        & (panel.forecast_issue_date.dt.year <= 2026)
    ].copy()

    rows = []
    for mo in sorted(test.month.unique()):
        te = test[test.month == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        first_issue = te.forecast_issue_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < first_issue)
        ].copy()
        if len(tr) < 80:
            continue

        X, T, _, _ = standardize(tr, te)
        y = tr.y_up.astype(int).to_numpy()
        off_tr = logit(tr.p_aurora.to_numpy(float))
        beta = fit_offset_logistic(X, y, off_tr, lam)

        eta = logit(te.p_aurora.to_numpy(float)) + T @ beta
        pp = expit(eta)

        for r, p in zip(te.itertuples(), pp):
            rows.append({
                "lambda": float(lam),
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "target_r3": float(r.target_r3),
                "p_aurora": float(r.p_aurora),
                "p_prism": float(p),
                "train_n": int(len(tr)),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)


def score_periods(led):
    rows = []
    specs = [
        ("SELECT_2022_H2", led.forecast_issue_date.between("2022-07-01", "2022-12-31")),
        ("2023", led.year == 2023),
        ("2024", led.year == 2024),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
        ("2023-2024", led.year.isin([2023, 2024])),
        ("2025-2026", led.year.isin([2025, 2026])),
    ]
    for label, mask in specs:
        z = led[mask].copy()
        if z.empty:
            continue
        ma = metrics(z.y_up, z.p_aurora)
        mp = metrics(z.y_up, z.p_prism)

        ad = (z.p_aurora >= 0.5).astype(int)
        pd_ = (z.p_prism >= 0.5).astype(int)
        yy = z.y_up.astype(int)
        changed = ad != pd_
        rescued = int((changed & (ad != yy) & (pd_ == yy)).sum())
        broken = int((changed & (ad == yy) & (pd_ != yy)).sum())

        rows.append({
            "period": label,
            "changed_calls": int(changed.sum()),
            "rescued": rescued,
            "broken": broken,
            "net_rescue": rescued - broken,
            **{f"aurora_{k}": v for k, v in ma.items()},
            **{f"prism_{k}": v for k, v in mp.items()},
        })
    return pd.DataFrame(rows)


def select_model(preds):
    rows = []
    for lam, led in preds.items():
        mdf = score_periods(led)
        r = mdf[mdf.period == "SELECT_2022_H2"].iloc[0]
        eligible = bool(
            r.prism_balanced_accuracy + 1e-12 >= r.aurora_balanced_accuracy
            and r.prism_accuracy + 0.005 + 1e-12 >= r.aurora_accuracy
            and r.prism_brier <= r.aurora_brier + 0.0025 + 1e-12
            and r.prism_prediction_std >= 0.02
        )
        rows.append({
            "lambda": float(lam),
            "eligible": eligible,
            "delta_accuracy": float(r.prism_accuracy - r.aurora_accuracy),
            "delta_balanced_accuracy": float(r.prism_balanced_accuracy - r.aurora_balanced_accuracy),
            "delta_brier": float(r.prism_brier - r.aurora_brier),
            "delta_logloss": float(r.prism_logloss - r.aurora_logloss),
            "changed_calls": int(r.changed_calls),
            "rescued": int(r.rescued),
            "broken": int(r.broken),
            "net_rescue": int(r.net_rescue),
            "prism_accuracy": float(r.prism_accuracy),
            "prism_balanced_accuracy": float(r.prism_balanced_accuracy),
            "prism_brier": float(r.prism_brier),
            "prism_logloss": float(r.prism_logloss),
        })
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(
        ["prism_balanced_accuracy", "prism_accuracy", "prism_brier", "prism_logloss"],
        ascending=[False, False, True, True],
    )
    return tab, float(elig.iloc[0]["lambda"])


def confirmation(mdf):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        r = mdf[mdf.period == yr].iloc[0]
        passed = bool(
            r.prism_accuracy + 0.01 + 1e-12 >= r.aurora_accuracy
            and r.prism_brier <= r.aurora_brier + 0.003 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "aurora_accuracy": float(r.aurora_accuracy),
            "prism_accuracy": float(r.prism_accuracy),
            "aurora_balanced_accuracy": float(r.aurora_balanced_accuracy),
            "prism_balanced_accuracy": float(r.prism_balanced_accuracy),
            "aurora_brier": float(r.aurora_brier),
            "prism_brier": float(r.prism_brier),
        })
        ok = ok and passed
    agg = mdf[mdf.period == "2023-2024"].iloc[0]
    agg_ok = bool(agg.prism_balanced_accuracy + 1e-12 >= agg.aurora_balanced_accuracy)
    return bool(ok and agg_ok), checks, agg_ok


def frozen_coefficients(panel, lam):
    tr = panel[
        (panel.target_end_date_h3 <= pd.Timestamp("2022-12-31"))
        & (panel.forecast_issue_date <= pd.Timestamp("2022-12-31"))
    ].copy()
    X = tr[LATENT_COLS].to_numpy(float)
    mu = X.mean(axis=0)
    sd = X.std(axis=0, ddof=0)
    sd = np.where(sd > 1e-8, sd, 1.0)
    Z = (X - mu) / sd
    beta = fit_offset_logistic(
        Z,
        tr.y_up.astype(int).to_numpy(),
        logit(tr.p_aurora.to_numpy(float)),
        lam,
    )
    return pd.DataFrame({
        "feature": LATENT_COLS,
        "coef_std": beta,
        "abs_coef": np.abs(beta),
    }).sort_values("abs_coef", ascending=False)


def main():
    panel, bridge, api_calls = build_panel()
    panel.to_csv(OUT / "prism_v1_latent_panel.csv", index=False)

    preds = {}
    for lam in LAMBDA_GRID:
        led = walk_forward(panel, lam)
        preds[lam] = led
        led.to_csv(OUT / f"prism_v1_predictions_lambda_{int(lam)}.csv", index=False)

    grid, selected = select_model(preds)
    grid.to_csv(OUT / "prism_v1_selection_grid.csv", index=False)

    if selected is None:
        summary = {
            "schema": "PRISM_H3_V1",
            "status": "FAIL_CLOSED_NO_ELIGIBLE_LAMBDA",
            "source_bridge": bridge,
            "api_calls": int(api_calls),
            "selection_grid": grid.to_dict(orient="records"),
        }
        (OUT / "prism_v1_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
        (OUT / "PRISM_V1_RESULT.md").write_text(
            "# PRISM-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2022-H2 regularization.\n"
        )
        print((OUT / "PRISM_V1_RESULT.md").read_text())
        return

    led = preds[selected].copy()
    mdf = score_periods(led)
    mdf.to_csv(OUT / "prism_v1_metrics.csv", index=False)

    passed, checks, agg_ok = confirmation(mdf)
    status = "MECHANISM_PASS" if passed else "NOT_PROMOTED_CONFIRM_FAIL"

    led.to_csv(OUT / "prism_v1_selected_predictions.csv", index=False)

    coef = frozen_coefficients(panel, selected)
    coef.to_csv(OUT / "prism_v1_coefficients.csv", index=False)

    z = led[led.year == 2026].copy()
    z["aurora_dir"] = np.where(z.p_aurora >= 0.5, "UP", "DOWN")
    z["prism_dir"] = np.where(z.p_prism >= 0.5, "UP", "DOWN")
    z["actual_dir"] = np.where(z.y_up == 1, "UP", "DOWN")
    z["changed"] = z.aurora_dir != z.prism_dir
    z["aurora_correct"] = z.aurora_dir == z.actual_dir
    z["prism_correct"] = z.prism_dir == z.actual_dir
    detail = z[z.changed].copy()
    detail.to_csv(OUT / "prism_v1_2026_changed_calls.csv", index=False)

    summary = {
        "schema": "PRISM_H3_V1",
        "status": status,
        "selected_lambda": selected,
        "source_bridge": bridge,
        "api_calls": int(api_calls),
        "confirmation_pass": bool(passed),
        "confirmation_checks": checks,
        "aggregate_balanced_guard": bool(agg_ok),
        "selection_grid": grid.to_dict(orient="records"),
        "metrics": mdf.to_dict(orient="records"),
        "changed_2026": int(detail.shape[0]),
        "rescued_2026": int(((~detail.aurora_correct) & detail.prism_correct).sum()) if len(detail) else 0,
        "broken_2026": int((detail.aurora_correct & (~detail.prism_correct)).sum()) if len(detail) else 0,
    }
    (OUT / "prism_v1_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")

    lines = [
        "# PRISM-H3 V1 — PHASE-RESOLVED INTRADAY SPECTRAL RESIDUAL RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Selected lambda (2022-H2 only):** **{selected:g}**  ",
        f"**2023 + 2024 frozen confirmation:** **{passed}**", "",
        "## Selection grid — 2022 H2", "",
        "| Lambda | Eligible | Δ accuracy | Δ balanced | Δ Brier | Changed | Rescued | Broken |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {r.lambda_ if hasattr(r,'lambda_') else getattr(r,'_1',r[0])} | {r.eligible} | "
            f"{100*r.delta_accuracy:+.2f} pp | {100*r.delta_balanced_accuracy:+.2f} pp | "
            f"{r.delta_brier:+.4f} | {int(r.changed_calls)} | {int(r.rescued)} | {int(r.broken)} |"
        )

    lines += ["", "## Period metrics", "",
              "| Period | AURORA Acc | PRISM Acc | AURORA BA | PRISM BA | AURORA Brier | PRISM Brier | Changed | Rescued | Broken |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for period in ["SELECT_2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        q = mdf[mdf.period == period]
        if q.empty:
            continue
        r = q.iloc[0]
        lines.append(
            f"| {period} | {100*r.aurora_accuracy:.2f}% | {100*r.prism_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.prism_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.prism_brier:.4f} | "
            f"{int(r.changed_calls)} | {int(r.rescued)} | {int(r.broken)} |"
        )

    lines += ["", "## Largest frozen standardized residual coefficients", "",
              "| Feature | Coefficient |",
              "|---|---:|"]
    for r in coef.head(10).itertuples():
        lines.append(f"| {r.feature} | {r.coef_std:+.4f} |")

    lines += ["", "## 2026 changed decisions", ""]
    if detail.empty:
        lines.append("- none")
    else:
        lines += [
            "| Issue | H3 end | AURORA | PRISM | Actual | H3 return | AURORA pUP | PRISM pUP | Effect |",
            "|---|---|---|---|---|---:|---:|---:|---|",
        ]
        for r in detail.itertuples():
            effect = "RESCUED" if ((not r.aurora_correct) and r.prism_correct) else "BROKEN"
            lines.append(
                f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
                f"{r.aurora_dir} | {r.prism_dir} | {r.actual_dir} | {100*r.target_r3:+.2f}% | "
                f"{100*r.p_aurora:.1f}% | {100*r.p_prism:.1f}% | {effect} |"
            )

    lines += ["", "## Governance", "",
              "Only lambda was selected on Jul-Dec 2022. The wavelet family, level, latent dimension and residual architecture were frozen before the run. "
              "2025/2026 did not alter V1. The existing AURORA prospective champion remains unchanged."]

    (OUT / "PRISM_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "PRISM_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
