from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

import gold_h3_aim_v1 as aim

OUT = Path(os.environ.get("OUT_DIR", "gold_h3_sentry_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

WINDOW = 63
MIN_MATURED = 42
ENTER_PATH = 3
EXIT_PATH = 0


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


def apply_sentry(ledger):
    g = ledger.sort_values("forecast_issue_date").copy().reset_index(drop=True)
    state = "STRUCTURAL_IRIS"
    rows = []
    switches = []

    for r in g.itertuples():
        cutoff = pd.Timestamp(r.feature_cutoff_date)
        matured = g[
            (g.target_end_date_h3 <= cutoff)
            & (g.forecast_issue_date < r.forecast_issue_date)
        ].copy().tail(WINDOW)

        if len(matured):
            y = matured.y_up.to_numpy(int)
            s = (matured.p_structural.to_numpy(float) >= 0.5).astype(int)
            p = (matured.p_path_global.to_numpy(float) >= 0.5).astype(int)
            s_ok = s == y
            p_ok = p == y
            adv = ((~s_ok) & p_ok).astype(int) - (s_ok & (~p_ok)).astype(int)
            net = int(np.sum(adv))
            rescues = int(np.sum((~s_ok) & p_ok))
            breaks = int(np.sum(s_ok & (~p_ok)))
        else:
            net = rescues = breaks = 0

        old = state
        if len(matured) >= MIN_MATURED:
            if state == "STRUCTURAL_IRIS" and net >= ENTER_PATH:
                state = "PATH_GLOBAL"
            elif state == "PATH_GLOBAL" and net <= EXIT_PATH:
                state = "STRUCTURAL_IRIS"

        if state != old:
            switches.append({
                "forecast_issue_date": str(pd.Timestamp(r.forecast_issue_date).date()),
                "from": old,
                "to": state,
                "matured_n": int(len(matured)),
                "net_rescue_63": net,
                "rescues_63": rescues,
                "breaks_63": breaks,
            })

        ps = float(r.p_structural)
        pp = float(r.p_path_global)
        pout = pp if state == "PATH_GLOBAL" else ps

        rows.append({
            "feature_cutoff_date": r.feature_cutoff_date,
            "forecast_issue_date": r.forecast_issue_date,
            "target_end_date_h3": r.target_end_date_h3,
            "year": int(r.year),
            "month": str(r.month),
            "y_up": int(r.y_up),
            "target_r3": float(r.target_r3),
            "p_structural": ps,
            "p_path_global": pp,
            "active_expert": state,
            "p_sentry": pout,
            "matured_pair_n": int(len(matured)),
            "net_rescue_63": net,
            "rescues_63": rescues,
            "breaks_63": breaks,
        })

    return pd.DataFrame(rows), pd.DataFrame(switches)


def score_periods(g):
    rows = []
    specs = [
        ("2022_H2", g.forecast_issue_date.between("2022-07-01", "2022-12-31")),
        ("2023", g.year == 2023),
        ("2024", g.year == 2024),
        ("2025", g.year == 2025),
        ("2026", g.year == 2026),
        ("2023-2024", g.year.isin([2023, 2024])),
        ("2025-2026", g.year.isin([2025, 2026])),
    ]
    for label, mask in specs:
        z = g[mask].copy()
        if z.empty:
            continue
        rows.append({"model": "STRUCTURAL_IRIS", "period": label, **metrics(z.y_up, z.p_structural)})
        rows.append({"model": "PATH_GLOBAL", "period": label, **metrics(z.y_up, z.p_path_global)})
        rows.append({"model": "SENTRY", "period": label, **metrics(z.y_up, z.p_sentry)})
    return pd.DataFrame(rows)


def path_share(g):
    rows = []
    for yr, z in g[g.year.between(2022, 2026)].groupby("year"):
        rows.append({
            "year": int(yr),
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
            "mean_net_rescue_63": float(z.net_rescue_63.mean()),
            "median_net_rescue_63": float(z.net_rescue_63.median()),
        })
    return pd.DataFrame(rows)


def confirmation(mdf, switches):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == yr)].iloc[0]
        s = mdf[(mdf.model == "SENTRY") & (mdf.period == yr)].iloc[0]
        passed = bool(
            s.accuracy + 0.01 + 1e-12 >= b.accuracy
            and s.brier <= b.brier + 0.003 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "sentry_accuracy": float(s.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "sentry_balanced_accuracy": float(s.balanced_accuracy),
            "base_brier": float(b.brier),
            "sentry_brier": float(s.brier),
        })
        ok = ok and passed

    b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == "2023-2024")].iloc[0]
    s = mdf[(mdf.model == "SENTRY") & (mdf.period == "2023-2024")].iloc[0]
    agg_ok = bool(s.balanced_accuracy + 0.01 + 1e-12 >= b.balanced_accuracy)
    switches_ok = len(switches) > 0
    return bool(ok and agg_ok and switches_ok), checks, agg_ok, switches_ok


def rescue_2026(g):
    z = g[g.year == 2026].copy()
    y = z.y_up.to_numpy(int)
    b = (z.p_structural.to_numpy(float) >= 0.5).astype(int)
    s = (z.p_sentry.to_numpy(float) >= 0.5).astype(int)
    b_ok = b == y
    s_ok = s == y
    return {
        "n": int(len(z)),
        "base_accuracy": float(b_ok.mean()),
        "sentry_accuracy": float(s_ok.mean()),
        "rescued": int(np.sum((~b_ok) & s_ok)),
        "broken": int(np.sum(b_ok & (~s_ok))),
        "net_rescue": int(np.sum((~b_ok) & s_ok) - np.sum(b_ok & (~s_ok))),
        "path_origins": int(np.sum(z.active_expert == "PATH_GLOBAL")),
    }


def monthly_2026(g):
    rows = []
    for mo, z in g[g.year == 2026].groupby("month"):
        for name, col in [
            ("STRUCTURAL_IRIS", "p_structural"),
            ("PATH_GLOBAL", "p_path_global"),
            ("SENTRY", "p_sentry"),
        ]:
            rows.append({"model": name, "month": mo, **metrics(z.y_up, z[col])})
        rows.append({
            "model": "STATE",
            "month": mo,
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
        })
    return pd.DataFrame(rows)


def main():
    panel, bridge, api_calls = aim.load_panel()
    expert = aim.expert_ledger(panel)
    sentry, switches = apply_sentry(expert)
    sentry.to_csv(OUT / "sentry_v1_predictions.csv", index=False)
    switches.to_csv(OUT / "sentry_v1_switches.csv", index=False)

    mdf = score_periods(sentry)
    mdf.to_csv(OUT / "sentry_v1_metrics.csv", index=False)

    shares = path_share(sentry)
    shares.to_csv(OUT / "sentry_v1_path_share.csv", index=False)

    ok, checks, agg_ok, switches_ok = confirmation(mdf, switches)
    status = "MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    resc = rescue_2026(sentry)
    pd.DataFrame([resc]).to_csv(OUT / "sentry_v1_2026_rescue.csv", index=False)

    m26 = monthly_2026(sentry)
    m26.to_csv(OUT / "sentry_v1_2026_monthly.csv", index=False)

    summary = {
        "schema": "SENTRY_H3_V1",
        "status": status,
        "source_bridge": bridge,
        "api_calls": int(api_calls),
        "rule": {
            "window": WINDOW,
            "min_matured": MIN_MATURED,
            "enter_path": ENTER_PATH,
            "exit_path": EXIT_PATH,
        },
        "confirmation_pass": bool(ok),
        "confirmation_checks": checks,
        "aggregate_2023_2024_balanced_guard": bool(agg_ok),
        "switches_present": bool(switches_ok),
        "switches": switches.to_dict(orient="records"),
        "path_share": shares.to_dict(orient="records"),
        "rescue_2026": resc,
        "metrics": mdf.to_dict(orient="records"),
    }
    (OUT / "sentry_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# SENTRY-H3 V1 — CAUSAL EXPERT FAILOVER RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Rule:** last {WINDOW} matured calls; enter PATH at net rescue >= +{ENTER_PATH}; return STRUCTURAL at <= {EXIT_PATH}.  ",
        f"**2023 + 2024 confirmation:** **{ok}**", "",
        "## Period metrics", "",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for model in ["STRUCTURAL_IRIS", "PATH_GLOBAL", "SENTRY"]:
            q = mdf[(mdf.model == model) & (mdf.period == period)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["", "## PATH state share", "",
              "| Year | PATH share | Mean net rescue63 | Median net rescue63 |",
              "|---:|---:|---:|---:|"]
    for r in shares.itertuples():
        lines.append(
            f"| {int(r.year)} | {100*r.path_share:.1f}% | {r.mean_net_rescue_63:+.2f} | {r.median_net_rescue_63:+.1f} |"
        )

    lines += ["", "## State switches", ""]
    if switches.empty:
        lines.append("- none")
    else:
        for r in switches.itertuples():
            lines.append(
                f"- {r.forecast_issue_date}: {r._1 if hasattr(r,'_1') else getattr(r,'from')} -> {r.to}; "
                f"net_rescue63={int(r.net_rescue_63):+d}"
            )

    lines += ["", "## 2026 rescue", "",
              f"- structural accuracy: **{100*resc['base_accuracy']:.2f}%**",
              f"- SENTRY accuracy: **{100*resc['sentry_accuracy']:.2f}%**",
              f"- rescued calls: **{resc['rescued']}**",
              f"- broken calls: **{resc['broken']}**",
              f"- net rescue: **{resc['net_rescue']:+d}**",
              f"- PATH-active origins: **{resc['path_origins']} / {resc['n']}**", "",
              "## Governance", "",
              "The failover rule was fixed before this run and was not optimized on 2023-2026 outcomes. "
              "All switches use only already-matured paired historical H3 correctness."]

    (OUT / "SENTRY_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "SENTRY_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
