from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import gold_h3_iris_v1 as iris

OUT = Path(os.environ.get("OUT_DIR", "gold_h3_aim_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20261002
PATH = list(iris.PATH)
E1_FEATURES = ["base_logit"] + PATH
E2_FEATURES = PATH
RECENT_N = 126
HALF_LIFE_GRID = [21, 63, 126]
ETA_GRID = [10, 20, 40]


def model_balanced(balanced=False):
    return Pipeline([
        ("scale", StandardScaler()),
        ("model", LogisticRegression(
            C=1.0,
            solver="lbfgs",
            max_iter=3000,
            class_weight="balanced" if balanced else None,
            random_state=SEED,
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
        "false_call_rate": float(np.mean(pred != y)),
        "prediction_std": float(np.std(p)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def load_panel():
    ledger = iris.load_ledger()
    hist = iris.load_neon_hourly()
    succ, api_calls = iris.fetch_extension()
    _, bridge = iris.bridge_metrics(hist, succ)
    if not bridge["pass"]:
        raise RuntimeError("AIM_SOURCE_BRIDGE_FAIL")

    ext = succ[succ.ts >= pd.Timestamp("2025-01-01", tz="UTC")].copy()
    hourly = pd.concat([hist, ext], ignore_index=True)
    hourly = hourly.sort_values("ts").drop_duplicates("ts", keep="first").reset_index(drop=True)

    anchors = iris.build_anchor_features(hourly)
    panel = iris.prepare_panel(ledger, anchors)
    panel = panel.dropna(subset=["target_r3", "y_up", "base_logit"] + PATH).copy()
    panel["year"] = panel.forecast_issue_date.dt.year.astype(int)
    panel["month"] = panel.forecast_issue_date.dt.to_period("M").astype(str)
    return panel.sort_values("forecast_issue_date").reset_index(drop=True), bridge, api_calls


def expert_ledger(panel):
    test = panel[
        (panel.forecast_issue_date >= pd.Timestamp("2022-04-01"))
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

        ytr = tr.y_up.astype(int).to_numpy()

        X1, T1 = fill_xy(tr, te, E1_FEATURES)
        m1 = model_balanced(False)
        m1.fit(X1, ytr)
        p1 = m1.predict_proba(T1)[:, 1]

        X2, T2 = fill_xy(tr, te, E2_FEATURES)
        m2 = model_balanced(False)
        m2.fit(X2, ytr)
        p2 = m2.predict_proba(T2)[:, 1]

        rr = tr.tail(RECENT_N).copy()
        X3, T3 = fill_xy(rr, te, E2_FEATURES)
        y3 = rr.y_up.astype(int).to_numpy()
        m3 = model_balanced(True)
        m3.fit(X3, y3)
        p3 = m3.predict_proba(T3)[:, 1]

        for r, a, b, c in zip(te.itertuples(), p1, p2, p3):
            rows.append({
                "feature_cutoff_date": r.feature_cutoff_date,
                "forecast_issue_date": r.forecast_issue_date,
                "target_end_date_h3": r.target_end_date_h3,
                "year": int(r.year),
                "month": str(r.month),
                "y_up": int(r.y_up),
                "target_r3": float(r.target_r3),
                "p_structural": float(a),
                "p_path_global": float(b),
                "p_path_recent126": float(c),
                "train_n": int(len(tr)),
                "recent_train_n": int(len(rr)),
            })
    out = pd.DataFrame(rows)
    return out.sort_values("forecast_issue_date").reset_index(drop=True)


def decayed_brier(matured, pcol, half_life):
    if matured.empty:
        return 0.25
    y = matured.y_up.to_numpy(float)
    p = matured[pcol].to_numpy(float)
    loss = (p - y) ** 2
    n = len(loss)
    age = np.arange(n - 1, -1, -1, dtype=float)
    w = 0.5 ** (age / float(half_life))
    return float(np.sum(w * loss) / np.sum(w))


def softmax_weights(losses, eta):
    a = -float(eta) * np.asarray(losses, float)
    a -= np.max(a)
    e = np.exp(a)
    return e / np.sum(e)


def apply_mixture(ledger, half_life, eta):
    g = ledger.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    rows = []
    pcols = ["p_structural", "p_path_global", "p_path_recent126"]

    for r in g.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)
        matured = g[
            (g.target_end_date_h3 <= cutoff)
            & (g.forecast_issue_date < r.forecast_issue_date)
        ].copy()

        if len(matured) < 30:
            losses = [0.25, 0.25, 0.25]
            w = np.array([1/3, 1/3, 1/3], float)
        else:
            losses = [decayed_brier(matured, c, half_life) for c in pcols]
            w = softmax_weights(losses, eta)

        pvec = np.array([
            float(r.p_structural),
            float(r.p_path_global),
            float(r.p_path_recent126),
        ])
        pmix = float(np.dot(w, pvec))

        rows.append({
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_structural": float(r.p_structural),
            "p_path_global": float(r.p_path_global),
            "p_path_recent126": float(r.p_path_recent126),
            "loss_structural": float(losses[0]),
            "loss_path_global": float(losses[1]),
            "loss_path_recent126": float(losses[2]),
            "w_structural": float(w[0]),
            "w_path_global": float(w[1]),
            "w_path_recent126": float(w[2]),
            "p_aim": pmix,
            "matured_ledger_n": int(len(matured)),
            "half_life": int(half_life),
            "eta": int(eta),
        })
    return pd.DataFrame(rows)


def period_metric_row(g, pcol):
    return metrics(g.y_up, g[pcol])


def selection_grid(ledger):
    sel_mask = ledger.forecast_issue_date.between("2022-07-01", "2022-12-31")
    base = metrics(
        ledger.loc[sel_mask, "y_up"],
        ledger.loc[sel_mask, "p_structural"],
    )
    rows = []
    candidates = {}
    for h in HALF_LIFE_GRID:
        for eta in ETA_GRID:
            mix = apply_mixture(ledger, h, eta)
            g = mix[mix.forecast_issue_date.between("2022-07-01", "2022-12-31")].copy()
            m = metrics(g.y_up, g.p_aim)
            eligible = bool(
                m["balanced_accuracy"] + 1e-12 >= base["balanced_accuracy"]
                and m["accuracy"] + 0.005 + 1e-12 >= base["accuracy"]
                and m["brier"] <= base["brier"] + 1e-12
                and m["logloss"] <= base["logloss"] + 0.005 + 1e-12
            )
            rows.append({
                "half_life": h,
                "eta": eta,
                "eligible": eligible,
                "delta_accuracy": m["accuracy"] - base["accuracy"],
                "delta_balanced_accuracy": m["balanced_accuracy"] - base["balanced_accuracy"],
                "delta_brier": m["brier"] - base["brier"],
                "delta_logloss": m["logloss"] - base["logloss"],
                **m,
            })
            candidates[(h, eta)] = mix
    tab = pd.DataFrame(rows)
    elig = tab[tab.eligible].copy()
    if elig.empty:
        return tab, None, None
    elig = elig.sort_values(
        ["balanced_accuracy", "accuracy", "brier", "logloss"],
        ascending=[False, False, True, True],
    )
    best = elig.iloc[0].to_dict()
    key = (int(best["half_life"]), int(best["eta"]))
    return tab, best, candidates[key]


def score_periods(mix):
    rows = []
    specs = [
        ("SELECT_2022_H2", mix.forecast_issue_date.between("2022-07-01", "2022-12-31")),
        ("2023", mix.year == 2023),
        ("2024", mix.year == 2024),
        ("2025", mix.year == 2025),
        ("2026", mix.year == 2026),
        ("2023-2024", mix.year.isin([2023, 2024])),
        ("2025-2026", mix.year.isin([2025, 2026])),
    ]
    for label, mask in specs:
        g = mix[mask].copy()
        if g.empty:
            continue
        rows.append({"model": "STRUCTURAL_IRIS", "period": label, **metrics(g.y_up, g.p_structural)})
        rows.append({"model": "PATH_GLOBAL", "period": label, **metrics(g.y_up, g.p_path_global)})
        rows.append({"model": "PATH_RECENT126", "period": label, **metrics(g.y_up, g.p_path_recent126)})
        rows.append({"model": "AIM", "period": label, **metrics(g.y_up, g.p_aim)})
    return pd.DataFrame(rows)


def confirmation(mdf):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == yr)].iloc[0]
        a = mdf[(mdf.model == "AIM") & (mdf.period == yr)].iloc[0]
        passed = bool(
            a.balanced_accuracy + 1e-12 >= b.balanced_accuracy
            and a.accuracy + 0.01 + 1e-12 >= b.accuracy
            and a.brier <= b.brier + 0.0025 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "aim_accuracy": float(a.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "aim_balanced_accuracy": float(a.balanced_accuracy),
            "base_brier": float(b.brier),
            "aim_brier": float(a.brier),
        })
        ok = ok and passed
    return ok, checks


def weight_summary(mix):
    rows = []
    for yr, g in mix[mix.year.between(2022, 2026)].groupby("year"):
        rows.append({
            "year": int(yr),
            "n": int(len(g)),
            "w_structural_mean": float(g.w_structural.mean()),
            "w_path_global_mean": float(g.w_path_global.mean()),
            "w_path_recent126_mean": float(g.w_path_recent126.mean()),
            "loss_structural_mean": float(g.loss_structural.mean()),
            "loss_path_global_mean": float(g.loss_path_global.mean()),
            "loss_path_recent126_mean": float(g.loss_path_recent126.mean()),
        })
    return pd.DataFrame(rows)


def monthly_2026(mix):
    rows = []
    z = mix[mix.year == 2026].copy()
    for mo, g in z.groupby("month"):
        for name, col in [
            ("STRUCTURAL_IRIS", "p_structural"),
            ("PATH_GLOBAL", "p_path_global"),
            ("PATH_RECENT126", "p_path_recent126"),
            ("AIM", "p_aim"),
        ]:
            rows.append({"model": name, "month": mo, **metrics(g.y_up, g[col])})
    return pd.DataFrame(rows)


def rescue_2026(mix):
    g = mix[mix.year == 2026].copy()
    y = g.y_up.to_numpy(int)
    b = (g.p_structural.to_numpy(float) >= 0.5).astype(int)
    a = (g.p_aim.to_numpy(float) >= 0.5).astype(int)
    base_correct = b == y
    aim_correct = a == y
    return {
        "n": int(len(g)),
        "base_accuracy": float(base_correct.mean()),
        "aim_accuracy": float(aim_correct.mean()),
        "rescued": int(np.sum((~base_correct) & aim_correct)),
        "broken": int(np.sum(base_correct & (~aim_correct))),
        "net_rescue": int(np.sum((~base_correct) & aim_correct) - np.sum(base_correct & (~aim_correct))),
    }


def main():
    panel, bridge, api_calls = load_panel()
    led = expert_ledger(panel)
    led.to_csv(OUT / "aim_v1_expert_ledger.csv", index=False)

    grid, best, mix = selection_grid(led)
    grid.to_csv(OUT / "aim_v1_selection_grid.csv", index=False)

    if best is None or mix is None:
        summary = {
            "schema": "AIM_H3_V1",
            "status": "FAIL_CLOSED_NO_ELIGIBLE_ADAPTIVE_MIX",
            "source_bridge": bridge,
        }
        (OUT / "aim_v1_summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n")
        (OUT / "AIM_V1_RESULT.md").write_text(
            "# AIM-H3 V1 — RESULT\n\n**Status:** FAIL CLOSED — no eligible 2022-H2 adaptive mixture.\n"
        )
        print((OUT / "AIM_V1_RESULT.md").read_text())
        return

    mix.to_csv(OUT / "aim_v1_selected_predictions.csv", index=False)
    mdf = score_periods(mix)
    mdf.to_csv(OUT / "aim_v1_metrics.csv", index=False)

    ok, checks = confirmation(mdf)
    status = "MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    ws = weight_summary(mix)
    ws.to_csv(OUT / "aim_v1_weight_summary.csv", index=False)

    m26 = monthly_2026(mix)
    m26.to_csv(OUT / "aim_v1_2026_monthly.csv", index=False)

    rescue = rescue_2026(mix)
    pd.DataFrame([rescue]).to_csv(OUT / "aim_v1_2026_rescue.csv", index=False)

    summary = {
        "schema": "AIM_H3_V1",
        "status": status,
        "source_bridge": bridge,
        "api_calls": int(api_calls),
        "selected": best,
        "confirmation_pass": bool(ok),
        "confirmation_checks": checks,
        "weight_summary": ws.to_dict(orient="records"),
        "rescue_2026": rescue,
        "metrics": mdf.to_dict(orient="records"),
    }
    (OUT / "aim_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# AIM-H3 V1 — ADAPTIVE INTRADAY MIXTURE RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Selected half-life:** **{int(best['half_life'])}** matured forecasts  ",
        f"**Selected eta:** **{int(best['eta'])}**  ",
        f"**2023 + 2024 frozen confirmation:** **{ok}**", "",
        "## Selection grid — 2022 H2", "",
        "| Half-life | Eta | Eligible | Δ accuracy | Δ balanced | Δ Brier |",
        "|---:|---:|---|---:|---:|---:|",
    ]
    for r in grid.itertuples():
        lines.append(
            f"| {int(r.half_life)} | {int(r.eta)} | {r.eligible} | "
            f"{100*r.delta_accuracy:+.2f} pp | {100*r.delta_balanced_accuracy:+.2f} pp | "
            f"{r.delta_brier:+.4f} |"
        )

    lines += ["", "## Period metrics", "",
              "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
              "|---|---|---:|---:|---:|---:|---:|---:|"]
    for period in ["SELECT_2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for model in ["STRUCTURAL_IRIS", "PATH_GLOBAL", "PATH_RECENT126", "AIM"]:
            q = mdf[(mdf.model == model) & (mdf.period == period)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["", "## Mean adaptive weights", "",
              "| Year | Structural | Path global | Path recent126 |",
              "|---:|---:|---:|---:|"]
    for r in ws.itertuples():
        lines.append(
            f"| {int(r.year)} | {100*r.w_structural_mean:.1f}% | "
            f"{100*r.w_path_global_mean:.1f}% | {100*r.w_path_recent126_mean:.1f}% |"
        )

    lines += ["", "## 2026 rescue", "",
              f"- structural accuracy: **{100*rescue['base_accuracy']:.2f}%**",
              f"- AIM accuracy: **{100*rescue['aim_accuracy']:.2f}%**",
              f"- rescued calls: **{rescue['rescued']}**",
              f"- broken calls: **{rescue['broken']}**",
              f"- net rescue: **{rescue['net_rescue']:+d}**", "",
              "## Governance", "",
              "AIM half-life and eta were selected only on Jul-Dec 2022. "
              "2023 and 2024 were frozen confirmations; 2025/2026 were transport/stress. "
              "Weights at each origin used only already-matured earlier expert losses."]

    (OUT / "AIM_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "AIM_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
