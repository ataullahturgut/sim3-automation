from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.linear_model import ElasticNet, HuberRegressor, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_iris_return_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

FEATURES = ["base_logit"] + list(iris.PATH)
TARGET_COVERAGE = 0.80
RESID_WINDOW = 252
MIN_RESIDS = 80
SEED = 20261002

MODEL_NAMES = ["RIDGE_1", "RIDGE_10", "ELASTIC_0001", "ELASTIC_0005", "HUBER"]


def load_panel():
    ledger = iris.load_ledger()
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("IRIS_SOURCE_BRIDGE_FAIL")

    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)

    anchors = iris.build_anchor_features(hourly)
    panel = iris.prepare_panel(ledger, anchors)
    panel = panel.dropna(subset=FEATURES + ["target_r3"]).copy()
    panel["year"] = panel.forecast_issue_date.dt.year.astype(int)
    panel["month"] = panel.forecast_issue_date.dt.to_period("M").astype(str)
    return panel.sort_values("forecast_issue_date").reset_index(drop=True), bridge, api_calls


def make_model(name):
    if name == "RIDGE_1":
        reg = Ridge(alpha=1.0)
    elif name == "RIDGE_10":
        reg = Ridge(alpha=10.0)
    elif name == "ELASTIC_0001":
        reg = ElasticNet(alpha=0.0001, l1_ratio=0.5, max_iter=20000, random_state=SEED)
    elif name == "ELASTIC_0005":
        reg = ElasticNet(alpha=0.0005, l1_ratio=0.5, max_iter=20000, random_state=SEED)
    elif name == "HUBER":
        reg = HuberRegressor(epsilon=1.35, alpha=0.0001, max_iter=500)
    else:
        raise KeyError(name)
    return Pipeline([("scale", StandardScaler()), ("model", reg)])


def fill_xy(tr, te):
    a = tr[FEATURES].copy()
    b = te[FEATURES].copy()
    for c in FEATURES:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


def walk_forward(panel, model_name):
    test = panel[
        (panel.forecast_issue_date >= pd.Timestamp("2022-06-01"))
        & (panel.forecast_issue_date.dt.year <= 2026)
    ].copy()
    rows = []
    for mo in sorted(test.month.unique()):
        te = test[test.month == mo].copy()
        cutoff = te.feature_cutoff_date.min()
        tr = panel[
            (panel.target_end_date_h3 <= cutoff)
            & (panel.forecast_issue_date < te.forecast_issue_date.min())
        ].copy()
        if len(tr) < 80:
            continue
        Xtr, Xte = fill_xy(tr, te)
        ytr = tr.target_r3.astype(float).to_numpy()
        m = make_model(model_name)
        m.fit(Xtr, ytr)
        pred = m.predict(Xte)
        for r, pp in zip(te.itertuples(), pred):
            rows.append({
                "model": model_name,
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "target_r3": float(r.target_r3),
                "ret_hat_h3": float(pp),
                "p_up_iris": float(r.p_A1_arcr),
                "train_n": int(len(tr)),
            })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)


def point_metrics(g):
    y = g.target_r3.to_numpy(float)
    p = g.ret_hat_h3.to_numpy(float)
    err = p - y
    try:
        corr = float(np.corrcoef(y, p)[0, 1]) if len(g) > 2 and np.std(y) > 0 and np.std(p) > 0 else np.nan
    except Exception:
        corr = np.nan
    return {
        "n": int(len(g)),
        "mae": float(np.mean(np.abs(err))),
        "rmse": float(np.sqrt(np.mean(err ** 2))),
        "bias": float(np.mean(err)),
        "corr": corr,
        "sign_accuracy": float(np.mean((p > 0) == (y > 0))),
        "mean_predicted_return": float(np.mean(p)),
        "mean_actual_return": float(np.mean(y)),
    }


def zero_metrics(g):
    z = g.copy()
    z["ret_hat_h3"] = 0.0
    return point_metrics(z)


def selection_table(preds):
    rows = []
    for name, led in preds.items():
        g = led[led.year == 2023].copy()
        if g.empty:
            continue
        m = point_metrics(g)
        z = zero_metrics(g)
        eligible = bool(
            m["mae"] <= z["mae"] + 1e-12
            and m["rmse"] <= z["rmse"] + 0.001 + 1e-12
        )
        rows.append({
            "model": name,
            "eligible": eligible,
            "zero_mae": z["mae"],
            "zero_rmse": z["rmse"],
            "delta_mae_vs_zero": m["mae"] - z["mae"],
            "delta_rmse_vs_zero": m["rmse"] - z["rmse"],
            **m,
        })
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None
    elig = elig.sort_values(["mae", "rmse", "sign_accuracy"], ascending=[True, True, False])
    return tab, elig.iloc[0].to_dict()


def add_causal_conformal(led):
    g = led.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    pending = []
    residuals = []
    out = []

    for r in g.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)

        matured = []
        future = []
        for q in pending:
            if q["target_end_date_h3"] <= cutoff:
                matured.append(q)
            else:
                future.append(q)
        pending = future
        matured.sort(key=lambda x: x["target_end_date_h3"])

        for q in matured:
            residuals.append(abs(q["target_r3"] - q["ret_hat_h3"]))

        if len(residuals) >= MIN_RESIDS:
            cal = np.asarray(residuals[-RESID_WINDOW:], float)
            half = float(np.quantile(cal, TARGET_COVERAGE, method="higher"))
            lower = float(r.ret_hat_h3 - half)
            upper = float(r.ret_hat_h3 + half)
        else:
            half = lower = upper = np.nan

        out.append({
            "forecast_issue_date": r.forecast_issue_date,
            "conformal_half_width": half,
            "lower80_h3": lower,
            "upper80_h3": upper,
            "residual_bank_n": int(len(residuals)),
        })

        pending.append({
            "target_end_date_h3": pd.Timestamp(r.target_end_date_h3),
            "target_r3": float(r.target_r3),
            "ret_hat_h3": float(r.ret_hat_h3),
        })

    z = pd.DataFrame(out)
    return g.merge(z, on="forecast_issue_date", how="left")


def interval_metrics(g):
    z = g[np.isfinite(g.conformal_half_width)].copy()
    if z.empty:
        return {"interval_n": 0, "coverage80": np.nan, "mean_width80": np.nan, "median_width80": np.nan}
    inside = (z.target_r3 >= z.lower80_h3) & (z.target_r3 <= z.upper80_h3)
    width = z.upper80_h3 - z.lower80_h3
    return {
        "interval_n": int(len(z)),
        "coverage80": float(inside.mean()),
        "mean_width80": float(width.mean()),
        "median_width80": float(width.median()),
    }


def period_table(led):
    rows = []
    periods = [
        ("2023", led.year == 2023),
        ("2024", led.year == 2024),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
        ("2023-2024", led.year.isin([2023, 2024])),
        ("2025-2026", led.year.isin([2025, 2026])),
    ]
    for label, mask in periods:
        g = led[mask].copy()
        if g.empty:
            continue
        rows.append({
            "period": label,
            **point_metrics(g),
            **interval_metrics(g),
        })
    return pd.DataFrame(rows)


def monthly_2026(led):
    rows = []
    g0 = led[led.year == 2026].copy()
    for mo, g in g0.groupby("month"):
        rows.append({
            "month": mo,
            **point_metrics(g),
            **interval_metrics(g),
        })
    return pd.DataFrame(rows)


def latest_rows(led, n=15):
    cols = [
        "forecast_issue_date", "target_end_date_h3", "target_r3", "ret_hat_h3",
        "lower80_h3", "upper80_h3",
    ]
    z = led[led.year == 2026].copy().sort_values("forecast_issue_date").tail(n)
    return z[cols].copy()


def main():
    panel, bridge, api_calls = load_panel()

    preds = {}
    for name in MODEL_NAMES:
        led = walk_forward(panel, name)
        preds[name] = led
        led.to_csv(OUT / f"iris_return_v1_predictions_{name.lower()}.csv", index=False)

    sel_grid, selected = selection_table(preds)
    sel_grid.to_csv(OUT / "iris_return_v1_selection_grid_2023.csv", index=False)

    if selected is None:
        summary = {
            "schema": "IRIS_H3_RETURN_V1",
            "status": "FAIL_CLOSED_NO_ELIGIBLE_NUMERICAL_HEAD",
            "bridge": bridge,
        }
        (OUT / "iris_return_v1_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
        (OUT / "IRIS_RETURN_V1_RESULT.md").write_text(
            "# IRIS-H3 RETURN V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2023 numerical head.\n"
        )
        print((OUT / "IRIS_RETURN_V1_RESULT.md").read_text())
        return

    selected_name = str(selected["model"])
    led = add_causal_conformal(preds[selected_name])
    led["sign_hat"] = np.where(led.ret_hat_h3 > 0, "UP", "DOWN")
    led["actual_sign"] = np.where(led.target_r3 > 0, "UP", "DOWN")
    led.to_csv(OUT / "iris_return_v1_selected_predictions.csv", index=False)

    ptab = period_table(led)
    ptab.to_csv(OUT / "iris_return_v1_period_metrics.csv", index=False)

    m26 = monthly_2026(led)
    m26.to_csv(OUT / "iris_return_v1_2026_monthly.csv", index=False)

    last = latest_rows(led, 15)
    last.to_csv(OUT / "iris_return_v1_2026_latest15.csv", index=False)

    # Frozen 2024 confirmation criterion: numerical head must beat zero MAE and not
    # materially worsen RMSE.
    g24 = led[led.year == 2024].copy()
    m24 = point_metrics(g24)
    z24 = zero_metrics(g24)
    confirm_pass = bool(
        m24["mae"] < z24["mae"]
        and m24["rmse"] <= z24["rmse"] + 0.001
    )

    summary = {
        "schema": "IRIS_H3_RETURN_V1",
        "status": "MECHANISM_PASS" if confirm_pass else "NOT_PROMOTED_2024_CONFIRM_FAIL",
        "selected_model": selected_name,
        "selection_2023": selected,
        "confirmation_2024": m24,
        "zero_2024": z24,
        "confirmation_pass": confirm_pass,
        "source_bridge": bridge,
        "api_calls": int(api_calls),
        "period_metrics": ptab.to_dict(orient="records"),
        "monthly_2026": m26.to_dict(orient="records"),
    }
    (OUT / "iris_return_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# IRIS-H3 RETURN V1 — NUMERICAL 3-DAY RETURN RESULT", "",
        f"**Status:** **{summary['status']}**  ",
        f"**Selected numerical head (2023 only):** **{selected_name}**  ",
        f"**Frozen 2024 confirmation:** **{confirm_pass}**", "",
        "## Period metrics", "",
        "| Period | N | MAE | RMSE | Bias | Corr | Sign acc | Mean predicted | Mean actual | 80% cov | Mean width |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in ptab.itertuples():
        cov = "NA" if pd.isna(r.coverage80) else f"{100*r.coverage80:.1f}%"
        wid = "NA" if pd.isna(r.mean_width80) else f"{100*r.mean_width80:.2f}%"
        lines.append(
            f"| {r.period} | {int(r.n)} | {100*r.mae:.2f}% | {100*r.rmse:.2f}% | "
            f"{100*r.bias:+.2f}% | {r.corr:.3f} | {100*r.sign_accuracy:.2f}% | "
            f"{100*r.mean_predicted_return:+.2f}% | {100*r.mean_actual_return:+.2f}% | {cov} | {wid} |"
        )

    lines += ["", "## 2026 month-by-month", "",
              "| Month | N | Mean pred | Mean actual | MAE | Sign acc | 80% cov | Mean width |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in m26.itertuples():
        cov = "NA" if pd.isna(r.coverage80) else f"{100*r.coverage80:.1f}%"
        wid = "NA" if pd.isna(r.mean_width80) else f"{100*r.mean_width80:.2f}%"
        lines.append(
            f"| {r.month} | {int(r.n)} | {100*r.mean_predicted_return:+.2f}% | "
            f"{100*r.mean_actual_return:+.2f}% | {100*r.mae:.2f}% | "
            f"{100*r.sign_accuracy:.1f}% | {cov} | {wid} |"
        )

    lines += ["", "## Latest 15 matured 2026 H3 origins", "",
              "| Issue | Target end | Pred | Actual | Lower80 | Upper80 |",
              "|---|---|---:|---:|---:|---:|"]
    for r in last.itertuples():
        lo = "NA" if pd.isna(r.lower80_h3) else f"{100*r.lower80_h3:+.2f}%"
        hi = "NA" if pd.isna(r.upper80_h3) else f"{100*r.upper80_h3:+.2f}%"
        lines.append(
            f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.target_end_date_h3).date()} | "
            f"{100*r.ret_hat_h3:+.2f}% | {100*r.target_r3:+.2f}% | {lo} | {hi} |"
        )

    lines += ["", "## Governance", "",
              "2023 selected the numerical head. 2024 did not alter it. "
              "2025/2026 are frozen transport/stress. Intervals use only prior matured OOS residuals. "
              "This numerical head supplements, but does not replace, frozen IRIS-H3 direction V1."]

    (OUT / "IRIS_RETURN_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "IRIS_RETURN_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
