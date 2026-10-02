from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_aurora_v1_out"))
OUT.mkdir(parents=True, exist_ok=True)

SENTRY = ROOT / "gold_axis_2026" / "GOLD_H3_SENTRY_V1_PREDICTIONS_2026-10-02.csv"
DART = ROOT / "gold_axis_2026" / "GOLD_H3_DART_V1_PREDICTIONS_2026-10-02.csv"

MIN_MATURED_PAIR = 42
ENTER_NET_RESCUE = 3
MIN_DISAGREEMENTS = 8
EXIT_PROB = 0.10
EXIT_Q = 0.40

SEED = 20261002
REPS = 10000
BLOCKS = [5, 10]


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


def load_ledger():
    s = pd.read_csv(SENTRY)
    d = pd.read_csv(DART)
    for x in [s, d]:
        for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3"]:
            x[c] = pd.to_datetime(x[c], errors="raise")

    s_keep = [
        "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
        "year", "month", "y_up", "target_r3",
        "p_structural", "p_path_global", "p_sentry",
        "matured_pair_n", "net_rescue_63", "rescues_63", "breaks_63",
    ]
    d_keep = [
        "forecast_issue_date", "p_dart",
        "matured_disagreements", "q_path", "prob_path_superior",
        "expected_run_length", "changepoint_mass",
    ]
    x = s[s_keep].merge(
        d[d_keep], on="forecast_issue_date", how="left", validate="one_to_one"
    )
    if x[d_keep[1:]].isna().any().any():
        raise RuntimeError("AURORA_DART_LEDGER_MATCH_FAIL")
    return x.sort_values("forecast_issue_date").reset_index(drop=True)


def apply_aurora(x):
    state = "STRUCTURAL_IRIS"
    rows = []
    switches = []

    for r in x.itertuples():
        old = state

        if state == "STRUCTURAL_IRIS":
            if int(r.matured_pair_n) >= MIN_MATURED_PAIR and int(r.net_rescue_63) >= ENTER_NET_RESCUE:
                state = "PATH_GLOBAL"
        else:
            if (
                int(r.matured_disagreements) >= MIN_DISAGREEMENTS
                and float(r.prob_path_superior) <= EXIT_PROB
                and float(r.q_path) <= EXIT_Q
            ):
                state = "STRUCTURAL_IRIS"

        if state != old:
            switches.append({
                "forecast_issue_date": str(pd.Timestamp(r.forecast_issue_date).date()),
                "from": old,
                "to": state,
                "matured_pair_n": int(r.matured_pair_n),
                "net_rescue_63": int(r.net_rescue_63),
                "matured_disagreements": int(r.matured_disagreements),
                "q_path": float(r.q_path),
                "prob_path_superior": float(r.prob_path_superior),
            })

        p = float(r.p_path_global) if state == "PATH_GLOBAL" else float(r.p_structural)

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
            "p_sentry": float(r.p_sentry),
            "p_dart": float(r.p_dart),
            "p_aurora": p,
            "active_expert": state,
            "matured_pair_n": int(r.matured_pair_n),
            "net_rescue_63": int(r.net_rescue_63),
            "matured_disagreements": int(r.matured_disagreements),
            "q_path": float(r.q_path),
            "prob_path_superior": float(r.prob_path_superior),
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
    models = [
        ("STRUCTURAL_IRIS", "p_structural"),
        ("PATH_GLOBAL", "p_path_global"),
        ("SENTRY", "p_sentry"),
        ("DART", "p_dart"),
        ("AURORA", "p_aurora"),
    ]
    for label, mask in specs:
        z = g[mask].copy()
        if z.empty:
            continue
        for model, col in models:
            rows.append({"model": model, "period": label, **metrics(z.y_up, z[col])})
    return pd.DataFrame(rows)


def confirmation(mdf, switches):
    checks = []
    ok = True
    for yr in ["2023", "2024"]:
        b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == yr)].iloc[0]
        a = mdf[(mdf.model == "AURORA") & (mdf.period == yr)].iloc[0]
        passed = bool(
            a.accuracy + 0.01 + 1e-12 >= b.accuracy
            and a.brier <= b.brier + 0.003 + 1e-12
        )
        checks.append({
            "period": yr,
            "pass": passed,
            "base_accuracy": float(b.accuracy),
            "aurora_accuracy": float(a.accuracy),
            "base_balanced_accuracy": float(b.balanced_accuracy),
            "aurora_balanced_accuracy": float(a.balanced_accuracy),
            "base_brier": float(b.brier),
            "aurora_brier": float(a.brier),
        })
        ok = ok and passed

    b = mdf[(mdf.model == "STRUCTURAL_IRIS") & (mdf.period == "2023-2024")].iloc[0]
    a = mdf[(mdf.model == "AURORA") & (mdf.period == "2023-2024")].iloc[0]
    agg_ok = bool(a.balanced_accuracy + 0.01 + 1e-12 >= b.balanced_accuracy)
    switches_ok = len(switches) > 0
    return bool(ok and agg_ok and switches_ok), checks, agg_ok, switches_ok


def state_summary(g):
    rows = []
    for yr, z in g[g.year.between(2022, 2026)].groupby("year"):
        rows.append({
            "year": int(yr),
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
            "mean_net_rescue_63": float(z.net_rescue_63.mean()),
            "mean_q_path": float(z.q_path.mean()),
            "mean_prob_path_superior": float(z.prob_path_superior.mean()),
        })
    return pd.DataFrame(rows)


def rescue_2026(g):
    z = g[g.year == 2026].copy()
    y = z.y_up.to_numpy(int)
    b = (z.p_structural.to_numpy(float) >= 0.5).astype(int)
    a = (z.p_aurora.to_numpy(float) >= 0.5).astype(int)
    b_ok = b == y
    a_ok = a == y
    return {
        "n": int(len(z)),
        "base_accuracy": float(b_ok.mean()),
        "aurora_accuracy": float(a_ok.mean()),
        "rescued": int(np.sum((~b_ok) & a_ok)),
        "broken": int(np.sum(b_ok & (~a_ok))),
        "net_rescue": int(np.sum((~b_ok) & a_ok) - np.sum(b_ok & (~a_ok))),
        "path_origins": int(np.sum(z.active_expert == "PATH_GLOBAL")),
    }


def monthly_2026(g):
    rows = []
    for mo, z in g[g.year == 2026].groupby("month"):
        for name, col in [
            ("STRUCTURAL_IRIS", "p_structural"),
            ("SENTRY", "p_sentry"),
            ("DART", "p_dart"),
            ("AURORA", "p_aurora"),
        ]:
            rows.append({"model": name, "month": mo, **metrics(z.y_up, z[col])})
        rows.append({
            "model": "STATE",
            "month": mo,
            "n": int(len(z)),
            "path_share": float((z.active_expert == "PATH_GLOBAL").mean()),
        })
    return pd.DataFrame(rows)


def logloss_row(y, p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, int)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def diff_arrays(y, cand, base):
    y = np.asarray(y, int)
    cand = np.asarray(cand, float)
    base = np.asarray(base, float)
    return {
        "accuracy": ((cand >= 0.5).astype(int) == y).astype(float)
                    - ((base >= 0.5).astype(int) == y).astype(float),
        "brier": (cand - y) ** 2 - (base - y) ** 2,
        "logloss": logloss_row(y, cand) - logloss_row(y, base),
    }


def circular_boot(diff, block_len, rng):
    diff = np.asarray(diff, float)
    n = len(diff)
    nblocks = int(np.ceil(n / block_len))
    vals = np.empty(REPS, float)
    offsets = np.arange(block_len, dtype=int)
    batch = 500
    for st in range(0, REPS, batch):
        m = min(batch, REPS - st)
        starts = rng.integers(0, n, size=(m, nblocks))
        idx = (starts[:, :, None] + offsets[None, None, :]) % n
        idx = idx.reshape(m, -1)[:, :n]
        vals[st:st + m] = diff[idx].mean(axis=1)
    return vals


def inference(g):
    comparisons = {
        "AURORA_vs_DART": ("p_aurora", "p_dart"),
        "AURORA_vs_SENTRY": ("p_aurora", "p_sentry"),
        "AURORA_vs_STRUCTURAL": ("p_aurora", "p_structural"),
    }
    periods = {
        "2026": g.year == 2026,
        "2025-2026": g.year.isin([2025, 2026]),
    }

    rows = []
    seed_i = 0
    for period, mask in periods.items():
        z = g[mask].copy()
        y = z.y_up.to_numpy(int)
        for comp, (cand_col, base_col) in comparisons.items():
            diffs = diff_arrays(y, z[cand_col], z[base_col])
            for metric, diff in diffs.items():
                for block_len in BLOCKS:
                    seed_i += 1
                    rng = np.random.default_rng(SEED + seed_i)
                    boot = circular_boot(diff, block_len, rng)
                    lo, hi = np.quantile(boot, [0.025, 0.975])
                    improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                    rows.append({
                        "period": period,
                        "comparison": comp,
                        "metric": metric,
                        "block_len": int(block_len),
                        "n": int(len(z)),
                        "observed_diff": float(np.mean(diff)),
                        "ci95_low": float(lo),
                        "ci95_high": float(hi),
                        "bootstrap_improve_share": improve,
                    })
    return pd.DataFrame(rows)


def main():
    x = load_ledger()
    aurora, switches = apply_aurora(x)
    aurora.to_csv(OUT / "aurora_v1_predictions.csv", index=False)
    switches.to_csv(OUT / "aurora_v1_switches.csv", index=False)

    mdf = score_periods(aurora)
    mdf.to_csv(OUT / "aurora_v1_metrics.csv", index=False)

    st = state_summary(aurora)
    st.to_csv(OUT / "aurora_v1_state_summary.csv", index=False)

    ok, checks, agg_ok, switches_ok = confirmation(mdf, switches)
    status = "MECHANISM_PASS" if ok else "NOT_PROMOTED_CONFIRM_FAIL"

    resc = rescue_2026(aurora)
    pd.DataFrame([resc]).to_csv(OUT / "aurora_v1_2026_rescue.csv", index=False)

    m26 = monthly_2026(aurora)
    m26.to_csv(OUT / "aurora_v1_2026_monthly.csv", index=False)

    inf = inference(aurora)
    inf.to_csv(OUT / "aurora_v1_inference.csv", index=False)

    summary = {
        "schema": "AURORA_H3_V1",
        "status": status,
        "rule": {
            "fast_entry": {
                "min_matured_pair": MIN_MATURED_PAIR,
                "net_rescue_threshold": ENTER_NET_RESCUE,
            },
            "slow_exit": {
                "min_disagreements": MIN_DISAGREEMENTS,
                "prob_path_superior_max": EXIT_PROB,
                "q_path_max": EXIT_Q,
            },
        },
        "confirmation_pass": bool(ok),
        "confirmation_checks": checks,
        "aggregate_2023_2024_balanced_guard": bool(agg_ok),
        "switches_present": bool(switches_ok),
        "switches": switches.to_dict(orient="records"),
        "state_summary": st.to_dict(orient="records"),
        "rescue_2026": resc,
        "metrics": mdf.to_dict(orient="records"),
        "inference": inf.to_dict(orient="records"),
    }
    (OUT / "aurora_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# AURORA-H3 V1 — ASYMMETRIC UNIFIED REGIME ONLINE ROUTING RESULT", "",
        f"**Status:** **{status}**  ",
        f"**Entry:** SENTRY fast evidence (net rescue63 >= +3)  ",
        f"**Exit:** DART slow Bayesian reversal evidence  ",
        f"**2023 + 2024 confirmation:** **{ok}**", "",
        "## Period metrics", "",
        "| Model | Period | N | Accuracy | Balanced acc | Brier | UP recall | DOWN recall |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for period in ["2022_H2", "2023", "2024", "2025", "2026", "2025-2026"]:
        for model in ["STRUCTURAL_IRIS", "SENTRY", "DART", "AURORA"]:
            q = mdf[(mdf.model == model) & (mdf.period == period)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f"| {model} | {period} | {int(r.n)} | {100*r.accuracy:.2f}% | "
                f"{100*r.balanced_accuracy:.2f}% | {r.brier:.4f} | "
                f"{100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% |"
            )

    lines += ["", "## Annual state", "",
              "| Year | PATH share | Mean net rescue63 | Mean q_path | Mean Pr(PATH superior) |",
              "|---:|---:|---:|---:|---:|"]
    for r in st.itertuples():
        lines.append(
            f"| {int(r.year)} | {100*r.path_share:.1f}% | {r.mean_net_rescue_63:+.2f} | "
            f"{r.mean_q_path:.3f} | {r.mean_prob_path_superior:.3f} |"
        )

    lines += ["", "## State switches", ""]
    if switches.empty:
        lines.append("- none")
    else:
        for _, r in switches.iterrows():
            lines.append(
                f"- {r['forecast_issue_date']}: {r['from']} -> {r['to']}; "
                f"net_rescue63={int(r['net_rescue_63']):+d}; "
                f"q_path={r['q_path']:.3f}; Pr(PATH superior)={r['prob_path_superior']:.3f}"
            )

    lines += ["", "## 2026 rescue", "",
              f"- Structural accuracy: **{100*resc['base_accuracy']:.2f}%**",
              f"- AURORA accuracy: **{100*resc['aurora_accuracy']:.2f}%**",
              f"- rescued: **{resc['rescued']}**",
              f"- broken: **{resc['broken']}**",
              f"- net rescue: **{resc['net_rescue']:+d}**",
              f"- PATH origins: **{resc['path_origins']} / {resc['n']}**", "",
              "## Dependence-aware bootstrap highlights", ""]

    for period in ["2026", "2025-2026"]:
        for comp in ["AURORA_vs_DART", "AURORA_vs_SENTRY", "AURORA_vs_STRUCTURAL"]:
            for metric in ["accuracy", "brier"]:
                q = inf[
                    (inf.period == period)
                    & (inf.comparison == comp)
                    & (inf.metric == metric)
                    & (inf.block_len == 10)
                ]
                if q.empty:
                    continue
                r = q.iloc[0]
                scale = 100.0 if metric == "accuracy" else 1.0
                suffix = " pp" if metric == "accuracy" else ""
                lines.append(
                    f"- {period} {comp} {metric} (block10): "
                    f"diff={scale*r.observed_diff:+.4f}{suffix}; "
                    f"95%=[{scale*r.ci95_low:+.4f}, {scale*r.ci95_high:+.4f}]{suffix}; "
                    f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
                )

    lines += ["", "## Governance", "",
              "AURORA introduces no new fitted threshold. Entry is the frozen SENTRY rule; exit is the frozen DART reversal rule. "
              "All evidence fields are causal and based only on matured prior H3 outcomes."]

    (OUT / "AURORA_V1_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "AURORA_V1_RESULT.md").read_text())


if __name__ == "__main__":
    main()
