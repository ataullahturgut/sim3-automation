from __future__ import annotations

import json, math, os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "gold_axis_2026" / "GOLD_H3_NOVA_V1_PREDICTIONS_2026-10-02.csv"
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_ferg_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261002
BLOCK = 5

META_FEATURES = [
    "a1_confidence",
    "a0_confidence",
    "a3_confidence",
    "global_recent_gap",
    "a1_a3_gap",
    "novelty_core",
    "novelty_ext",
    "novelty_gap",
    "ret_abs",
    "ret_sign_agree_a3",
    "conformal_half_width",
    "return_uncertainty_ratio",
    "aci_alpha",
    "base_pred_up",
    "hist_acc20",
    "hist_acc60",
    "hist_acc126",
    "hist_up_precision60",
    "hist_down_precision60",
    "hist_ret_vol20",
    "hist_ret_vol60",
    "hist_actual_up60",
]

MODEL_NAMES = ["META_LOGIT_L2", "META_HGB_SHALLOW"]
NOMINAL_COVERAGES = [0.70, 0.60, 0.50, 0.40, 0.30, 0.20]


def load_ledger():
    df = pd.read_csv(LEDGER)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        df[c] = pd.to_datetime(df[c], errors="raise")
    df = df.sort_values("forecast_issue_date").reset_index(drop=True)
    df["base_pred_up"] = (df["p_A1_arcr"].astype(float) >= 0.5).astype(int)
    df["base_correct"] = (df["base_pred_up"] == df["y_up"].astype(int)).astype(int)
    df["error_label"] = 1 - df["base_correct"]
    return df


def safe_precision(y, pred, label):
    y = np.asarray(y, int)
    pred = np.asarray(pred, int)
    m = pred == label
    if not np.any(m):
        return 0.5
    return float(np.mean(y[m] == label))


def hist_features(past):
    if past.empty:
        return {
            "hist_acc20": 0.5, "hist_acc60": 0.5, "hist_acc126": 0.5,
            "hist_up_precision60": 0.5, "hist_down_precision60": 0.5,
            "hist_ret_vol20": 0.0, "hist_ret_vol60": 0.0,
            "hist_actual_up60": 0.5,
        }

    def acc(n):
        z = past.tail(n)
        return float(z.base_correct.mean()) if len(z) else 0.5

    z60 = past.tail(60)
    pred60 = z60.base_pred_up.to_numpy(int)
    y60 = z60.y_up.to_numpy(int)

    r20 = past.tail(20).target_r3.to_numpy(float)
    r60 = past.tail(60).target_r3.to_numpy(float)

    return {
        "hist_acc20": acc(20),
        "hist_acc60": acc(60),
        "hist_acc126": acc(126),
        "hist_up_precision60": safe_precision(y60, pred60, 1),
        "hist_down_precision60": safe_precision(y60, pred60, 0),
        "hist_ret_vol20": float(np.std(r20, ddof=0)) if len(r20) > 1 else 0.0,
        "hist_ret_vol60": float(np.std(r60, ddof=0)) if len(r60) > 1 else 0.0,
        "hist_actual_up60": float(np.mean(y60)) if len(y60) else 0.5,
    }


def build_causal_meta_frame(df):
    rows = []
    for r in df.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)
        past = df[df.target_end_date_h3 <= cutoff].copy()
        # Exact current/future row exclusion is guaranteed by target maturity.
        h = hist_features(past)

        chw = float(r.conformal_half_width) if pd.notna(r.conformal_half_width) else np.nan
        rur = float(r.return_uncertainty_ratio) if pd.notna(r.return_uncertainty_ratio) else np.nan
        alpha = float(r.aci_alpha) if pd.notna(r.aci_alpha) else 0.20

        rows.append({
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_A1_arcr": float(r.p_A1_arcr),
            "base_pred_up": int(r.base_pred_up),
            "base_correct": int(r.base_correct),
            "error_label": int(r.error_label),
            "a1_confidence": float(abs(r.p_A1_arcr - 0.5) * 2.0),
            "a0_confidence": float(abs(r.p_A0_global - 0.5) * 2.0),
            "a3_confidence": float(abs(r.p_A3 - 0.5) * 2.0),
            "global_recent_gap": float(abs(r.p_A0_global - r.p_recent252)),
            "a1_a3_gap": float(abs(r.p_A1_arcr - r.p_A3)),
            "novelty_core": float(r.novelty_core),
            "novelty_ext": float(r.novelty_ext),
            "novelty_gap": float(abs(r.novelty_ext - r.novelty_core)),
            "ret_abs": float(abs(r.ret_hat_h3)),
            "ret_sign_agree_a3": float((r.ret_hat_h3 > 0) == (r.p_A3 >= 0.5)),
            "conformal_half_width": chw,
            "return_uncertainty_ratio": rur,
            "aci_alpha": alpha,
            **h,
        })
    return pd.DataFrame(rows)


def make_model(name):
    if name == "META_LOGIT_L2":
        return Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(
                C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED
            )),
        ])
    if name == "META_HGB_SHALLOW":
        return HistGradientBoostingClassifier(
            learning_rate=0.05,
            max_iter=80,
            max_depth=2,
            min_samples_leaf=40,
            l2_regularization=1.0,
            random_state=SEED,
        )
    raise KeyError(name)


def fill_train_test(tr, te):
    a = tr[META_FEATURES].copy()
    b = te[META_FEATURES].copy()
    for c in META_FEATURES:
        a[c] = pd.to_numeric(a[c], errors="coerce")
        b[c] = pd.to_numeric(b[c], errors="coerce")
        med = a[c].median(skipna=True)
        v = float(med) if pd.notna(med) else 0.0
        a[c] = a[c].fillna(v)
        b[c] = b[c].fillna(v)
    return a.to_numpy(float), b.to_numpy(float)


def chronological_meta_predictions(meta, model_name, start_year=2019, end_year=2026):
    test = meta[
        meta.forecast_issue_date.dt.year.between(start_year, end_year)
    ].copy().reset_index(drop=True)

    rows = []
    for bs in range(0, len(test), BLOCK):
        te = test.iloc[bs:bs + BLOCK].copy()
        cutoff = te.feature_cutoff_date.min()
        tr = meta[
            (meta.target_end_date_h3 <= cutoff)
            & (meta.forecast_issue_date < te.forecast_issue_date.min())
        ].copy()

        if len(tr) < 350:
            raise RuntimeError(f"META_TRAIN_TOO_SMALL {len(tr)} at {cutoff}")

        ytr = tr.error_label.to_numpy(int)
        if len(np.unique(ytr)) < 2:
            raise RuntimeError("META_SINGLE_CLASS")

        Xtr, Xte = fill_train_test(tr, te)
        m = make_model(model_name)
        m.fit(Xtr, ytr)
        p_err = m.predict_proba(Xte)[:, 1]

        for r, pe in zip(te.itertuples(), p_err):
            rows.append({
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "target_r3": float(r.target_r3),
                "p_up_base": float(r.p_A1_arcr),
                "base_pred_up": int(r.base_pred_up),
                "base_correct": int(r.base_correct),
                "error_label": int(r.error_label),
                "p_error": float(pe),
                "forecastability": float(1.0 - pe),
                "meta_train_n": int(len(tr)),
                "model": model_name,
            })
    return pd.DataFrame(rows)


def meta_metrics(g):
    y = g.error_label.to_numpy(int)
    p = np.clip(g.p_error.to_numpy(float), 1e-6, 1 - 1e-6)
    try:
        auc = float(roc_auc_score(y, p))
    except Exception:
        auc = np.nan
    return {
        "n": int(len(g)),
        "error_rate": float(y.mean()),
        "brier_error": float(np.mean((p - y) ** 2)),
        "logloss_error": float(log_loss(y, p, labels=[0, 1])),
        "roc_auc_error": auc,
        "mean_p_error_correct": float(g.loc[g.error_label == 0, "p_error"].mean()),
        "mean_p_error_wrong": float(g.loc[g.error_label == 1, "p_error"].mean()),
    }


def gate_metrics(g, threshold):
    accept = g.p_error.to_numpy(float) <= float(threshold)
    y = g.y_up.to_numpy(int)
    pred = g.base_pred_up.to_numpy(int)

    full_acc = float(np.mean(pred == y))
    n = len(g)
    calls = int(accept.sum())

    if calls:
        ya = y[accept]
        pa = pred[accept]
        tn, fp, fn, tp = confusion_matrix(ya, pa, labels=[0, 1]).ravel()
        up_rec_sel = tp / max(tp + fn, 1)
        down_rec_sel = tn / max(tn + fp, 1)
        sel_acc = float(np.mean(pa == ya))
        sel_ba = float((up_rec_sel + down_rec_sel) / 2.0)
    else:
        tn = fp = fn = tp = 0
        sel_acc = sel_ba = 0.0

    reject = ~accept
    rejected_acc = float(np.mean(pred[reject] == y[reject])) if np.any(reject) else np.nan

    actual_up = int(np.sum(y == 1))
    actual_down = int(np.sum(y == 0))
    tp_all = int(np.sum(accept & (pred == 1) & (y == 1)))
    fp_all = int(np.sum(accept & (pred == 1) & (y == 0)))
    tn_all = int(np.sum(accept & (pred == 0) & (y == 0)))
    fn_all = int(np.sum(accept & (pred == 0) & (y == 1)))

    up_precision = tp_all / max(tp_all + fp_all, 1)
    down_precision = tn_all / max(tn_all + fn_all, 1)

    return {
        "n": int(n),
        "threshold": float(threshold),
        "n_calls": calls,
        "coverage": float(calls / max(n, 1)),
        "full_base_accuracy": full_acc,
        "selective_accuracy": sel_acc,
        "selective_balanced_accuracy": sel_ba,
        "accepted_vs_full_gain": float(sel_acc - full_acc),
        "rejected_accuracy": rejected_acc,
        "accepted_vs_rejected_gap": float(sel_acc - rejected_acc) if np.isfinite(rejected_acc) else np.nan,
        "up_precision": float(up_precision),
        "down_precision": float(down_precision),
        "up_capture_recall": float(tp_all / max(actual_up, 1)),
        "down_capture_recall": float(tn_all / max(actual_down, 1)),
        "false_up_fpr": float(fp_all / max(actual_down, 1)),
        "false_down_fpr": float(fn_all / max(actual_up, 1)),
    }


def select_gate(preds_by_model):
    rows = []
    for model_name, led in preds_by_model.items():
        sel = led[led.year.between(2019, 2021)].copy()
        mm = meta_metrics(sel)
        vals = sel.p_error.to_numpy(float)
        for nominal in NOMINAL_COVERAGES:
            th = float(np.quantile(vals, nominal))
            gm = gate_metrics(sel, th)
            eligible = (
                gm["coverage"] >= 0.20
                and gm["n_calls"] >= 100
                and gm["selective_accuracy"] >= gm["full_base_accuracy"] + 0.02 - 1e-12
                and np.isfinite(gm["rejected_accuracy"])
            )
            rows.append({
                "model": model_name,
                "nominal_coverage": nominal,
                "eligible": bool(eligible),
                **mm,
                **gm,
            })

    grid = pd.DataFrame(rows)
    elig = grid[grid.eligible].copy()
    if elig.empty:
        return grid, None

    elig = elig.sort_values(
        [
            "selective_balanced_accuracy",
            "selective_accuracy",
            "accepted_vs_rejected_gap",
            "coverage",
            "brier_error",
        ],
        ascending=[False, False, False, False, True],
    )
    return grid, elig.iloc[0].to_dict()


def period_report(led, threshold):
    periods = [
        ("SELECT_2019_2021", led.year.between(2019, 2021)),
        ("CONFIRM_2022_2024", led.year.between(2022, 2024)),
        ("2022", led.year == 2022),
        ("2023", led.year == 2023),
        ("2024", led.year == 2024),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
    ]
    rows = []
    for label, mask in periods:
        g = led[mask].copy()
        rows.append({"period": label, **meta_metrics(g), **gate_metrics(g, threshold)})
    return pd.DataFrame(rows)


def feature_coefs(meta, led, selected_model):
    # Descriptive fit on the selection period only. Not used to change the gate.
    if selected_model != "META_LOGIT_L2":
        return pd.DataFrame()
    sel_dates = led[led.year.between(2019, 2021)].forecast_issue_date
    cutoff = sel_dates.min()
    tr = meta[meta.target_end_date_h3 < cutoff].copy()
    # Include matured selection history causally up to end-2021 for one retrospective descriptive coefficient fit.
    end = pd.Timestamp("2021-12-31")
    tr = meta[(meta.forecast_issue_date <= end) & (meta.target_end_date_h3 <= end)].copy()
    X, _ = fill_train_test(tr, tr.iloc[:1])
    y = tr.error_label.to_numpy(int)
    m = make_model("META_LOGIT_L2")
    m.fit(X, y)
    co = m.named_steps["model"].coef_[0]
    return pd.DataFrame({"feature": META_FEATURES, "coef_std": co}).sort_values("coef_std", ascending=False)


def main():
    raw = load_ledger()
    meta = build_causal_meta_frame(raw)
    meta.to_csv(OUT / "ferg_v1_meta_features.csv", index=False)

    preds = {}
    for name in MODEL_NAMES:
        led = chronological_meta_predictions(meta, name, 2019, 2026)
        preds[name] = led
        led.to_csv(OUT / f"ferg_v1_predictions_{name.lower()}.csv", index=False)

    grid, best = select_gate(preds)
    grid.to_csv(OUT / "ferg_v1_selection_grid.csv", index=False)

    if best is None:
        summary = {
            "schema": "FERG_H3_V1",
            "status": "FAIL_CLOSED_NO_ELIGIBLE_GATE",
            "selection_window": "2019-2021",
        }
        (OUT / "ferg_v1_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        (OUT / "FERG_V1_RESULT.md").write_text(
            "# FERG-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible pre-2022 error-risk gate.\n"
        )
        print((OUT / "FERG_V1_RESULT.md").read_text())
        return

    model_name = str(best["model"])
    threshold = float(best["threshold"])
    led = preds[model_name].copy()
    led["accepted"] = led.p_error <= threshold
    led["signal"] = np.where(
        led.accepted,
        np.where(led.base_pred_up == 1, "UP", "DOWN"),
        "UNCERTAIN",
    )
    led.to_csv(OUT / "ferg_v1_selected_predictions.csv", index=False)

    periods = period_report(led, threshold)
    periods.to_csv(OUT / "ferg_v1_metrics.csv", index=False)

    coefs = feature_coefs(meta, led, model_name)
    if not coefs.empty:
        coefs.to_csv(OUT / "ferg_v1_logit_coefficients_descriptive.csv", index=False)

    c = periods[periods.period == "CONFIRM_2022_2024"].iloc[0]
    y25 = periods[periods.period == "2025"].iloc[0]
    y26 = periods[periods.period == "2026"].iloc[0]

    mechanism_pass = bool(
        c.coverage >= 0.20
        and c.selective_accuracy > c.full_base_accuracy
        and c.accepted_vs_rejected_gap > 0
    )

    summary = {
        "schema": "FERG_H3_V1",
        "status": "MECHANISM_PASS" if mechanism_pass else "NOT_PROMOTED",
        "selection_window": "2019-2021",
        "confirmation_window": "2022-2024",
        "selected_model": model_name,
        "selected_threshold": threshold,
        "selection": best,
        "confirmation_2022_2024": c.to_dict(),
        "transport_2025": y25.to_dict(),
        "transport_2026": y26.to_dict(),
    }
    (OUT / "ferg_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# FERG-H3 V1 — RESULT", "",
        f"**Status:** **{summary['status']}**  ",
        f"**Selected meta-model:** **{model_name}**  ",
        f"**Frozen P(ERROR) acceptance threshold:** **{threshold:.6f}**  ",
        "**Selection:** 2019-2021 only  ",
        "**Confirmation:** 2022-2024  ",
        "**2025/2026:** report-only transport/stress", "",
        "## Error-risk + gate metrics", "",
        "| Period | Coverage | Full A1 acc | Accepted acc | Accepted BA | Rejected acc | Gap | Error AUC | Error Brier |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for per in ["SELECT_2019_2021", "CONFIRM_2022_2024", "2022", "2023", "2024", "2025", "2026"]:
        r = periods[periods.period == per].iloc[0]
        lines.append(
            f"| {per} | {100*r.coverage:.2f}% | {100*r.full_base_accuracy:.2f}% | "
            f"{100*r.selective_accuracy:.2f}% | {100*r.selective_balanced_accuracy:.2f}% | "
            f"{100*r.rejected_accuracy:.2f}% | {100*r.accepted_vs_rejected_gap:.2f} pp | "
            f"{r.roc_auc_error:.3f} | {r.brier_error:.4f} |"
        )

    lines += ["", "## Directional capture of accepted calls", "",
              "| Period | UP precision | DOWN precision | UP capture | DOWN capture | False-UP FPR | False-DOWN FPR |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for per in ["SELECT_2019_2021", "CONFIRM_2022_2024", "2025", "2026"]:
        r = periods[periods.period == per].iloc[0]
        lines.append(
            f"| {per} | {100*r.up_precision:.2f}% | {100*r.down_precision:.2f}% | "
            f"{100*r.up_capture_recall:.2f}% | {100*r.down_capture_recall:.2f}% | "
            f"{100*r.false_up_fpr:.2f}% | {100*r.false_down_fpr:.2f}% |"
        )

    lines += ["", "## Error-risk separation", ""]
    for per in ["SELECT_2019_2021", "CONFIRM_2022_2024", "2025", "2026"]:
        r = periods[periods.period == per].iloc[0]
        lines.append(
            f"- {per}: mean P(error) on correct calls **{r.mean_p_error_correct:.3f}**; "
            f"on wrong calls **{r.mean_p_error_wrong:.3f}**."
        )

    lines += ["", "## Governance", "",
              "No 2025/2026 outcome was used to select the model family or threshold. "
              "The selected meta-model is refit online only from already-matured prior H3 errors. "
              "A failed transport cannot modify FERG V1; any repair requires V2."]

    (OUT / "FERG_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print("FERG_H3_V1_SUMMARY=" + json.dumps(summary, separators=(",", ":"), default=str))
    print((OUT / "FERG_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
