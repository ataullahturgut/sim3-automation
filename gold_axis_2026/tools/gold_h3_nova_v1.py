from __future__ import annotations

import json, os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.covariance import LedoitWolf
from sklearn.linear_model import ElasticNet, LogisticRegression
from sklearn.metrics import confusion_matrix, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_short_horizon_global_xau_stage1_r2 as s1

OUT = Path(os.environ.get("OUT_DIR", "gold_h3_nova_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261002
BLOCK = 5
CORE3 = list(s1.CORE3)

CORE_STATE = [
    "sigma20", "gold_r1", "gold_r5", "gold_r21",
    "silver_r5", "silver_r21", "platinum_r5", "platinum_r21",
]
RATE_EXT = ["DGS10", "DFII10", "BREAKEVEN10_PROXY"]
LOG_EXT = ["BROAD_USD_INDEX", "VIX", "NDX"]
EXT_STATE = [f"{c}_d5" for c in RATE_EXT] + [f"{c}_lr5" for c in LOG_EXT]
BASE_RECENT_WEIGHT = 0.25
RECENT_N = 252
TARGET_ALPHA = 0.20
ACI_WINDOW = 504

MIX_MAX_GRID = [0.35, 0.50, 0.65]
SHRINK_GRID = [0.25, 0.50, 0.75]
NOMINAL_COVERAGES = [0.70, 0.60, 0.50, 0.40, 0.30]
GAMMA_GRID = [0.001, 0.005, 0.010, 0.020]
RHO_GRID = [0.00, 0.10, 0.20, 0.30]


def load_panel():
    df = s1.load_panel().copy()
    for c in RATE_EXT:
        df[f"{c}_d5"] = pd.to_numeric(df[c], errors="coerce").diff(5)
    for c in LOG_EXT:
        x = pd.to_numeric(df[c], errors="coerce")
        df[f"{c}_lr5"] = np.log(x.where(x > 0)).diff(5)
    return df.sort_values("feature_cutoff_date").reset_index(drop=True)


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


def global_logit():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000, random_state=SEED
        )),
    ])


def recent_logit():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0, solver="lbfgs", max_iter=3000,
            class_weight="balanced", random_state=SEED
        )),
    ])


def return_model():
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", ElasticNet(
            alpha=0.0005, l1_ratio=0.5, max_iter=10000, random_state=SEED
        )),
    ])


def empirical_percentile(train_values, test_values):
    a = np.sort(np.asarray(train_values, float))
    b = np.asarray(test_values, float)
    if len(a) == 0:
        return np.full(len(b), 0.5)
    return np.searchsorted(a, b, side="right") / float(len(a))


def novelty_score(tr, te, features):
    Xtr, Xte = fill_xy(tr, te, features)

    med = np.median(Xtr, axis=0)
    mad = np.median(np.abs(Xtr - med), axis=0) * 1.4826
    sd = np.std(Xtr, axis=0)
    scale = np.where(np.isfinite(mad) & (mad > 1e-8), mad,
                     np.where(np.isfinite(sd) & (sd > 1e-8), sd, 1.0))

    Ztr = np.clip((Xtr - med) / scale, -12.0, 12.0)
    Zte = np.clip((Xte - med) / scale, -12.0, 12.0)

    try:
        lw = LedoitWolf().fit(Ztr)
        center = lw.location_
        prec = lw.precision_
        Dtr = Ztr - center
        Dte = Zte - center
        md_tr = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", Dtr, prec, Dtr), 0.0))
        md_te = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", Dte, prec, Dte), 0.0))
        p_md = empirical_percentile(md_tr, md_te)
    except Exception:
        dtr = np.sqrt(np.mean(Ztr ** 2, axis=1))
        dte = np.sqrt(np.mean(Zte ** 2, axis=1))
        p_md = empirical_percentile(dtr, dte)

    sig_tr = pd.to_numeric(tr["sigma20"], errors="coerce")
    sig_te = pd.to_numeric(te["sigma20"], errors="coerce")
    smed = float(sig_tr.median(skipna=True)) if sig_tr.notna().any() else 0.0
    sdev = float(sig_tr.std(ddof=0)) if sig_tr.notna().sum() > 1 else 1.0
    if not np.isfinite(sdev) or sdev <= 1e-12:
        sdev = 1.0
    ztr = np.abs((sig_tr.fillna(smed).to_numpy(float) - smed) / sdev)
    zte = np.abs((sig_te.fillna(smed).to_numpy(float) - smed) / sdev)
    p_sig = empirical_percentile(ztr, zte)

    return np.clip(0.70 * p_md + 0.30 * p_sig, 0.0, 1.0)


def run_base_sequence(df, start_year=2017, end_year=2026):
    test = df[
        df.forecast_issue_date.dt.year.between(start_year, end_year)
        & df.target_r3.notna()
        & df.target_end_date_h3.notna()
    ].copy().reset_index(drop=True)

    rows = []
    for bs in range(0, len(test), BLOCK):
        te = test.iloc[bs:bs + BLOCK].copy()
        cutoff = te.feature_cutoff_date.min()
        tr = df[
            df.target_r3.notna()
            & df.target_end_date_h3.notna()
            & (df.target_end_date_h3 <= cutoff)
        ].copy()
        if len(tr) < 750:
            raise RuntimeError(f"TRAIN_TOO_SMALL n={len(tr)} cutoff={cutoff}")

        Xg, Xte = fill_xy(tr, te, CORE3)
        yg = (tr.target_r3.astype(float) > 0).astype(int).to_numpy()

        mg = global_logit()
        mg.fit(Xg, yg)
        p_global = mg.predict_proba(Xte)[:, 1]

        rr = tr.tail(RECENT_N).copy()
        Xr, Xte_r = fill_xy(rr, te, CORE3)
        yr = (rr.target_r3.astype(float) > 0).astype(int).to_numpy()
        mr = recent_logit()
        mr.fit(Xr, yr)
        p_recent = mr.predict_proba(Xte_r)[:, 1]

        reg = return_model()
        reg.fit(Xg, tr.target_r3.astype(float).to_numpy())
        ret_hat = reg.predict(Xte)

        n_core = novelty_score(tr, te, CORE_STATE)
        n_ext = novelty_score(tr, te, CORE_STATE + EXT_STATE)

        y = (te.target_r3.astype(float) > 0).astype(int).to_numpy()
        for j, r in enumerate(te.itertuples()):
            rows.append({
                "feature_cutoff_date": str(r.feature_cutoff_date.date()),
                "forecast_issue_date": str(r.forecast_issue_date.date()),
                "target_end_date_h3": str(r.target_end_date_h3.date()),
                "year": int(r.forecast_issue_date.year),
                "month": str(r.forecast_issue_date.strftime("%Y-%m")),
                "target_r3": float(r.target_r3),
                "y_up": int(y[j]),
                "p_A0_global": float(p_global[j]),
                "p_recent252": float(p_recent[j]),
                "p_A1_arcr": float(0.75 * p_global[j] + 0.25 * p_recent[j]),
                "novelty_core": float(n_core[j]),
                "novelty_ext": float(n_ext[j]),
                "ret_hat_h3": float(ret_hat[j]),
                "train_n": int(len(tr)),
            })
    out = pd.DataFrame(rows)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
        out[c] = pd.to_datetime(out[c])
    return out.sort_values("forecast_issue_date").reset_index(drop=True)


def full_metrics(y, p):
    y = np.asarray(y, int)
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    up_rec = tp / max(tp + fn, 1)
    down_rec = tn / max(tn + fp, 1)
    return {
        "n": int(len(y)),
        "accuracy": float((pred == y).mean()),
        "balanced_accuracy": float((up_rec + down_rec) / 2.0),
        "up_recall": float(up_rec),
        "down_recall": float(down_rec),
        "false_call_rate": float((pred != y).mean()),
        "brier": float(np.mean((p - y) ** 2)),
        "logloss": float(log_loss(y, p, labels=[0, 1])),
        "prediction_std": float(np.std(p)),
    }


def apply_novelty_mix(df, novelty_col, max_recent_weight, shrink):
    n = np.clip(df[novelty_col].to_numpy(float), 0.0, 1.0)
    pg = df.p_A0_global.to_numpy(float)
    pr = df.p_recent252.to_numpy(float)
    wr = BASE_RECENT_WEIGHT + (float(max_recent_weight) - BASE_RECENT_WEIGHT) * n
    p_mix = (1.0 - wr) * pg + wr * pr
    p = 0.5 + (p_mix - 0.5) * (1.0 - float(shrink) * (n ** 2))
    return np.clip(p, 1e-6, 1 - 1e-6)


def select_novelty_params(sel, novelty_col):
    y = sel.y_up.to_numpy(int)
    base = full_metrics(y, sel.p_A1_arcr.to_numpy(float))
    rows = []
    for mx in MIX_MAX_GRID:
        for sh in SHRINK_GRID:
            p = apply_novelty_mix(sel, novelty_col, mx, sh)
            m = full_metrics(y, p)
            eligible = (
                m["brier"] <= base["brier"] + 0.0015 + 1e-12
                and m["up_recall"] >= base["up_recall"] - 0.05 - 1e-12
            )
            rows.append({
                "novelty_col": novelty_col,
                "max_recent_weight": mx,
                "shrink": sh,
                "eligible": bool(eligible),
                **m,
            })
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, {
            "status": "FALLBACK_A1",
            "max_recent_weight": BASE_RECENT_WEIGHT,
            "shrink": 0.0,
            **base,
        }
    elig = elig.sort_values(
        ["down_recall", "balanced_accuracy", "accuracy", "brier", "logloss"],
        ascending=[False, False, False, True, True],
    )
    best = elig.iloc[0].to_dict()
    best["status"] = "SELECTED"
    return tab, best


def selective_metrics(y, p, mask):
    y = np.asarray(y, int)
    p = np.asarray(p, float)
    mask = np.asarray(mask, bool)
    pred = (p >= 0.5).astype(int)

    n = len(y)
    calls = int(mask.sum())
    actual_up = int((y == 1).sum())
    actual_down = int((y == 0).sum())

    tp = int(np.sum(mask & (pred == 1) & (y == 1)))
    fp = int(np.sum(mask & (pred == 1) & (y == 0)))
    tn = int(np.sum(mask & (pred == 0) & (y == 0)))
    fn = int(np.sum(mask & (pred == 0) & (y == 1)))

    if calls:
        sy = y[mask]
        sp = pred[mask]
        sup = np.sum(sy == 1)
        sdown = np.sum(sy == 0)
        up_rec_sel = np.sum((sp == 1) & (sy == 1)) / max(sup, 1)
        down_rec_sel = np.sum((sp == 0) & (sy == 0)) / max(sdown, 1)
        acc = float(np.mean(sp == sy))
        ba = float((up_rec_sel + down_rec_sel) / 2.0)
    else:
        acc = ba = 0.0

    return {
        "n": int(n),
        "n_calls": calls,
        "coverage": float(calls / max(n, 1)),
        "selective_accuracy": acc,
        "selective_balanced_accuracy": ba,
        "up_precision": float(tp / max(tp + fp, 1)),
        "down_precision": float(tn / max(tn + fn, 1)),
        "up_capture_recall": float(tp / max(actual_up, 1)),
        "down_capture_recall": float(tn / max(actual_down, 1)),
        "false_up_fpr": float(fp / max(actual_down, 1)),
        "false_down_fpr": float(fn / max(actual_up, 1)),
    }


def select_a4_threshold(sel, p_col="p_A3"):
    rel = sel.reliability_A4.to_numpy(float)
    agree = sel.sign_agree_A4.to_numpy(bool)
    y = sel.y_up.to_numpy(int)
    p = sel[p_col].to_numpy(float)
    rows = []
    for nominal in NOMINAL_COVERAGES:
        thr = float(np.quantile(rel, 1.0 - nominal))
        mask = agree & (rel >= thr)
        m = selective_metrics(y, p, mask)
        rows.append({"nominal_coverage": nominal, "threshold": thr, **m})
    tab = pd.DataFrame(rows)
    elig = tab[(tab.coverage >= 0.25) & (tab.n_calls >= 150)].copy()
    if elig.empty:
        elig = tab.sort_values(["coverage"], ascending=False).head(1).copy()
    elig = elig.sort_values(
        ["selective_balanced_accuracy", "selective_accuracy", "coverage"],
        ascending=[False, False, False],
    )
    return tab, elig.iloc[0].to_dict()


def return_metrics(g):
    y = g.target_r3.to_numpy(float)
    p = g.ret_hat_h3.to_numpy(float)
    e = p - y
    return {
        "n": int(len(g)),
        "mae": float(np.mean(np.abs(e))),
        "rmse": float(np.sqrt(np.mean(e ** 2))),
        "direction_accuracy": float(np.mean((p > 0) == (y > 0))),
    }


def apply_aci(base, gamma):
    g = base.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    alpha = TARGET_ALPHA
    residual_scores = []
    pending = []
    rows = []

    for r in g.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)

        still = []
        matured_now = []
        for q in pending:
            if q["target_end_date_h3"] <= cutoff:
                matured_now.append(q)
            else:
                still.append(q)
        pending = still
        matured_now.sort(key=lambda x: x["target_end_date_h3"])

        for q in matured_now:
            residual_scores.append(abs(q["target_r3"] - q["ret_hat_h3"]))
            if np.isfinite(q["lower"]) and np.isfinite(q["upper"]):
                miss = float((q["target_r3"] < q["lower"]) or (q["target_r3"] > q["upper"]))
                alpha = float(np.clip(alpha + float(gamma) * (TARGET_ALPHA - miss), 0.02, 0.40))

        if len(residual_scores) >= 100:
            cal = np.asarray(residual_scores[-ACI_WINDOW:], float)
            level = float(np.clip(1.0 - alpha, 0.60, 0.98))
            half = float(np.quantile(cal, level, method="higher"))
            lower = float(r.ret_hat_h3 - half)
            upper = float(r.ret_hat_h3 + half)
        else:
            half = lower = upper = np.nan

        rows.append({
            "forecast_issue_date": r.forecast_issue_date,
            "aci_alpha": alpha,
            "conformal_half_width": half,
            "conformal_lower": lower,
            "conformal_upper": upper,
        })
        pending.append({
            "target_end_date_h3": pd.Timestamp(r.target_end_date_h3),
            "target_r3": float(r.target_r3),
            "ret_hat_h3": float(r.ret_hat_h3),
            "lower": lower,
            "upper": upper,
        })

    z = pd.DataFrame(rows)
    out = g.merge(z, on="forecast_issue_date", how="left")
    return out


def conformal_metrics(g):
    z = g[np.isfinite(g.conformal_half_width)].copy()
    if z.empty:
        return {"n": 0, "coverage": np.nan, "mean_width": np.nan}
    inside = (z.target_r3 >= z.conformal_lower) & (z.target_r3 <= z.conformal_upper)
    return {
        "n": int(len(z)),
        "coverage": float(inside.mean()),
        "mean_width": float(np.mean(2.0 * z.conformal_half_width)),
    }


def select_gamma(base):
    rows = []
    candidates = {}
    for gm in GAMMA_GRID:
        g = apply_aci(base, gm)
        sel = g[g.year.between(2019, 2021)]
        m = conformal_metrics(sel)
        rows.append({"gamma": gm, **m, "coverage_error": abs(m["coverage"] - 0.80)})
        candidates[gm] = g
    tab = pd.DataFrame(rows).sort_values(["coverage_error", "mean_width"], ascending=[True, True])
    best_gamma = float(tab.iloc[0].gamma)
    return tab, best_gamma, candidates[best_gamma]


def select_rho(sel, p_col="p_A3"):
    y = sel.y_up.to_numpy(int)
    p = sel[p_col].to_numpy(float)
    base_mask = sel.call_A4.to_numpy(bool)
    half = sel.conformal_half_width.to_numpy(float)
    ratio = np.divide(
        np.abs(sel.ret_hat_h3.to_numpy(float)),
        half,
        out=np.zeros(len(sel), float),
        where=np.isfinite(half) & (half > 1e-12),
    )

    rows = []
    for rho in RHO_GRID:
        mask = base_mask & np.isfinite(half) & (ratio >= rho)
        m = selective_metrics(y, p, mask)
        rows.append({"rho": rho, **m})
    tab = pd.DataFrame(rows)
    elig = tab[(tab.coverage >= 0.15) & (tab.n_calls >= 90)].copy()
    if elig.empty:
        elig = tab.sort_values(["coverage"], ascending=False).head(1).copy()
    elig = elig.sort_values(
        ["selective_balanced_accuracy", "selective_accuracy", "coverage"],
        ascending=[False, False, False],
    )
    return tab, elig.iloc[0].to_dict()


def period_rows(df, stage_cols, a4_thr, rho):
    periods = [
        ("SELECT_2019_2021", df.year.between(2019, 2021)),
        ("CONFIRM_2022_2024", df.year.between(2022, 2024)),
        ("2022", df.year == 2022),
        ("2023", df.year == 2023),
        ("2024", df.year == 2024),
        ("2025", df.year == 2025),
        ("2026", df.year == 2026),
    ]
    rows = []
    for label, mask in periods:
        g = df[mask].copy()
        for stage, col in stage_cols:
            rows.append({"period": label, "stage": stage, "mode": "FULL", **full_metrics(g.y_up, g[col])})

        a4mask = g.sign_agree_A4 & (g.reliability_A4 >= a4_thr)
        rows.append({"period": label, "stage": "A4", "mode": "SELECTIVE", **selective_metrics(g.y_up, g.p_A3, a4mask)})

        half = g.conformal_half_width.to_numpy(float)
        ratio = np.divide(
            np.abs(g.ret_hat_h3.to_numpy(float)),
            half,
            out=np.zeros(len(g), float),
            where=np.isfinite(half) & (half > 1e-12),
        )
        a5mask = a4mask.to_numpy(bool) & np.isfinite(half) & (ratio >= rho)
        rows.append({"period": label, "stage": "A5", "mode": "SELECTIVE", **selective_metrics(g.y_up, g.p_A3, a5mask)})

    return pd.DataFrame(rows)


def main():
    df = load_panel()
    led = run_base_sequence(df, 2017, 2026)

    sel = led[led.year.between(2019, 2021)].copy()

    grid_a2, best_a2 = select_novelty_params(sel, "novelty_core")
    grid_a3, best_a3 = select_novelty_params(sel, "novelty_ext")

    led["p_A2"] = apply_novelty_mix(
        led, "novelty_core",
        float(best_a2["max_recent_weight"]), float(best_a2["shrink"])
    )
    led["p_A3"] = apply_novelty_mix(
        led, "novelty_ext",
        float(best_a3["max_recent_weight"]), float(best_a3["shrink"])
    )

    led["sign_agree_A4"] = ((led.p_A3 >= 0.5) == (led.ret_hat_h3 > 0))
    led["reliability_A4"] = (
        2.0 * np.abs(led.p_A3 - 0.5) * (1.0 - np.clip(led.novelty_ext, 0.0, 1.0))
    )

    sel2 = led[led.year.between(2019, 2021)].copy()
    grid_a4, best_a4 = select_a4_threshold(sel2)
    a4_thr = float(best_a4["threshold"])
    led["call_A4"] = led.sign_agree_A4 & (led.reliability_A4 >= a4_thr)

    gamma_grid, gamma, with_aci = select_gamma(led)
    led = with_aci

    sel3 = led[led.year.between(2019, 2021)].copy()
    rho_grid, best_rho = select_rho(sel3)
    rho = float(best_rho["rho"])

    half = led.conformal_half_width.to_numpy(float)
    ratio = np.divide(
        np.abs(led.ret_hat_h3.to_numpy(float)),
        half,
        out=np.zeros(len(led), float),
        where=np.isfinite(half) & (half > 1e-12),
    )
    led["return_uncertainty_ratio"] = ratio
    led["call_A5"] = led.call_A4 & np.isfinite(half) & (ratio >= rho)
    led["signal_A5"] = np.where(
        led.call_A5,
        np.where(led.p_A3 >= 0.5, "UP", "DOWN"),
        "UNCERTAIN",
    )

    grid_a2.to_csv(OUT / "nova_v1_a2_grid.csv", index=False)
    grid_a3.to_csv(OUT / "nova_v1_a3_grid.csv", index=False)
    grid_a4.to_csv(OUT / "nova_v1_a4_reliability_grid.csv", index=False)
    gamma_grid.to_csv(OUT / "nova_v1_aci_gamma_grid.csv", index=False)
    rho_grid.to_csv(OUT / "nova_v1_a5_rho_grid.csv", index=False)

    stage_cols = [
        ("A0", "p_A0_global"),
        ("A1", "p_A1_arcr"),
        ("A2", "p_A2"),
        ("A3", "p_A3"),
    ]
    metrics = period_rows(led, stage_cols, a4_thr, rho)
    metrics.to_csv(OUT / "nova_v1_metrics.csv", index=False)

    ret_rows = []
    conf_rows = []
    for label, mask in [
        ("SELECT_2019_2021", led.year.between(2019, 2021)),
        ("CONFIRM_2022_2024", led.year.between(2022, 2024)),
        ("2025", led.year == 2025),
        ("2026", led.year == 2026),
    ]:
        g = led[mask].copy()
        ret_rows.append({"period": label, **return_metrics(g)})
        conf_rows.append({"period": label, **conformal_metrics(g)})
    pd.DataFrame(ret_rows).to_csv(OUT / "nova_v1_return_metrics.csv", index=False)
    pd.DataFrame(conf_rows).to_csv(OUT / "nova_v1_conformal_metrics.csv", index=False)

    led.to_csv(OUT / "nova_v1_predictions.csv", index=False)

    c = metrics[(metrics.period == "CONFIRM_2022_2024") & (metrics.stage == "A3")].iloc[0]
    a4 = metrics[(metrics.period == "CONFIRM_2022_2024") & (metrics.stage == "A4")].iloc[0]
    a5 = metrics[(metrics.period == "CONFIRM_2022_2024") & (metrics.stage == "A5")].iloc[0]
    y25 = metrics[(metrics.period == "2025") & (metrics.stage == "A5")].iloc[0]
    y26 = metrics[(metrics.period == "2026") & (metrics.stage == "A5")].iloc[0]

    summary = {
        "schema": "NOVA_H3_V1",
        "selection_window": "2019-2021",
        "confirmation_window": "2022-2024",
        "transport_periods": ["2025", "2026"],
        "a2_selected": best_a2,
        "a3_selected": best_a3,
        "a4_selected": best_a4,
        "aci_gamma": gamma,
        "a5_selected": best_rho,
        "confirmation_A3": c.to_dict(),
        "confirmation_A4": a4.to_dict(),
        "confirmation_A5": a5.to_dict(),
        "transport_2025_A5": y25.to_dict(),
        "transport_2026_A5": y26.to_dict(),
    }
    (OUT / "nova_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# NOVA-H3 V1 — RESULT", "",
        "**Identity:** `NOVA_H3_V1_RESEARCH`  ",
        "**Selection:** 2019-2021 only  ",
        "**Confirmation:** 2022-2024  ",
        "**2025/2026:** report-only transport/stress", "",
        "## Frozen selections", "",
        f"- A2 max recent weight: **{float(best_a2['max_recent_weight']):.2f}**; shrink: **{float(best_a2['shrink']):.2f}**; status: **{best_a2['status']}**",
        f"- A3 max recent weight: **{float(best_a3['max_recent_weight']):.2f}**; shrink: **{float(best_a3['shrink']):.2f}**; status: **{best_a3['status']}**",
        f"- A4 reliability threshold: **{a4_thr:.6f}**",
        f"- ACI gamma: **{gamma:.3f}**",
        f"- A5 return/uncertainty rho: **{rho:.2f}**", "",
        "## Full-coverage direction", "",
        "| Period | Stage | Accuracy | Balanced | UP recall | DOWN recall | Brier |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for per in ["SELECT_2019_2021", "CONFIRM_2022_2024", "2025", "2026"]:
        for st in ["A0", "A1", "A2", "A3"]:
            r = metrics[(metrics.period == per) & (metrics.stage == st)].iloc[0]
            lines.append(
                f"| {per} | {st} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.6f} |"
            )

    lines += [
        "", "## Selective UP / DOWN / UNCERTAIN", "",
        "| Period | Stage | Coverage | Sel. accuracy | Sel. balanced | UP capture | DOWN capture | False-UP FPR | False-DOWN FPR |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for per in ["SELECT_2019_2021", "CONFIRM_2022_2024", "2025", "2026"]:
        for st in ["A4", "A5"]:
            r = metrics[(metrics.period == per) & (metrics.stage == st)].iloc[0]
            lines.append(
                f"| {per} | {st} | {100*r.coverage:.2f}% | {100*r.selective_accuracy:.2f}% | "
                f"{100*r.selective_balanced_accuracy:.2f}% | {100*r.up_capture_recall:.2f}% | "
                f"{100*r.down_capture_recall:.2f}% | {100*r.false_up_fpr:.2f}% | {100*r.false_down_fpr:.2f}% |"
            )

    rm = pd.DataFrame(ret_rows)
    cm = pd.DataFrame(conf_rows)
    lines += ["", "## Numerical H3 return head", "",
              "| Period | MAE | RMSE | Sign accuracy |",
              "|---|---:|---:|---:|"]
    for r in rm.itertuples():
        lines.append(f"| {r.period} | {r.mae:.6f} | {r.rmse:.6f} | {100*r.direction_accuracy:.2f}% |")

    lines += ["", "## Adaptive conformal interval", "",
              "| Period | Coverage | Mean width |",
              "|---|---:|---:|"]
    for r in cm.itertuples():
        lines.append(f"| {r.period} | {100*r.coverage:.2f}% | {r.mean_width:.6f} |")

    lines += [
        "", "## Interpretation contract", "",
        "A 2022-2024 improvement is confirmation evidence, not blind proof. "
        "No 2025/2026 result may be used to alter V1 parameters. "
        "If transport fails, repair requires a separately named V2.",
    ]
    (OUT / "NOVA_V1_RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("NOVA_H3_V1_SUMMARY=" + json.dumps(summary, separators=(",", ":"), default=str))
    print((OUT / "NOVA_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
