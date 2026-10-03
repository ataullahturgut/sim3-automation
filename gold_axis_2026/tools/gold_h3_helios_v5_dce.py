from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from gold_h3_helios_v3_gt import (
    BLOCKS, REPS, SEED, circular_boot, metrics, paired_diff,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_helios_v5_dce_out"))
OUT.mkdir(parents=True, exist_ok=True)

V4 = ROOT / "gold_axis_2026" / "GOLD_H3_HELIOS_V4_RGE_PREDICTIONS_2026-10-03.csv"

POSTERIOR_THRESHOLD = 0.50
GT_THRESHOLD = 0.50


def as_bool(s):
    if s.dtype == bool:
        return s
    z = s.astype(str).str.lower().map({"true": True, "false": False})
    if z.isna().any():
        raise RuntimeError("BAD_BOOL")
    return z.astype(bool)


def load_base():
    g = pd.read_csv(V4)
    for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
              "cot_report_date", "cot_available_date"]:
        if c in g.columns:
            g[c] = pd.to_datetime(g[c], errors="raise")
    for c in ["v4_route", "gate_active", "opal_override", "candidate_reversal"]:
        g[c] = as_bool(g[c])
    return g.sort_values("forecast_issue_date").reset_index(drop=True)


def apply_dce(base, posterior_threshold=POSTERIOR_THRESHOLD,
              gt_threshold=GT_THRESHOLD):
    g = base.copy()
    exc = (
        (~g.v4_route)
        & g.gate_active
        & g.opal_override
        & (~g.candidate_reversal)
        & (g.gt_flip_share.astype(float) > float(gt_threshold))
        & (g.active_expert.astype(str) == "PATH_GLOBAL")
        & (g.prob_path_superior.astype(float) > float(posterior_threshold))
    )
    g["dce_exception"] = exc
    g["v5_route"] = g.v4_route | exc
    g["p_helios_v5_dce"] = g.p_helios_v4_rge.astype(float)
    g.loc[exc, "p_helios_v5_dce"] = 1.0 - g.loc[exc, "p_aurora"].astype(float)
    return g


def rescue_counts(z, prob_col):
    y = z.y_up.astype(int)
    a = (z.p_aurora >= .5).astype(int)
    q = (z[prob_col] >= .5).astype(int)
    ch = a != q
    rescue = int((ch & (a != y) & (q == y)).sum())
    broken = int((ch & (a == y) & (q != y)).sum())
    return int(ch.sum()), rescue, broken, rescue - broken


def score_periods(g):
    rows = []
    specs = [
        ("2023", g.year == 2023),
        ("2024", g.year == 2024),
        ("2025", g.year == 2025),
        ("2026", g.year == 2026),
        ("2023-2024", g.year.isin([2023, 2024])),
        ("2025-2026", g.year.isin([2025, 2026])),
    ]
    for label, mask in specs:
        z = g[mask].copy()
        vals = {
            "aurora": metrics(z.y_up, z.p_aurora),
            "v2": metrics(z.y_up, z.p_helios_v2),
            "v3": metrics(z.y_up, z.p_helios_v3_gt),
            "v4": metrics(z.y_up, z.p_helios_v4_rge),
            "v5": metrics(z.y_up, z.p_helios_v5_dce),
            "opal": metrics(z.y_up, z.p_opal_raw),
        }
        routed, rescue, broken, net = rescue_counts(z, "p_helios_v5_dce")
        rows.append({
            "period": label,
            **{f"{name}_{k}": v for name, m in vals.items() for k, v in m.items()},
            "routed_n": routed,
            "rescued": rescue,
            "broken": broken,
            "net_rescue": net,
            "dce_exception_n": int(z.dce_exception.sum()),
        })
    return pd.DataFrame(rows)


def inference(g):
    rows = []
    comparisons = {
        "AURORA": "p_aurora",
        "HELIOS_V2": "p_helios_v2",
        "HELIOS_V3_GT": "p_helios_v3_gt",
        "HELIOS_V4_RGE": "p_helios_v4_rge",
    }
    periods = {
        "2025-2026": g.year.isin([2025, 2026]),
        "2026": g.year == 2026,
    }
    si = 0
    for name, col in comparisons.items():
        for period, mask in periods.items():
            z = g[mask]
            for metric, d in paired_diff(z.y_up, z.p_helios_v5_dce, z[col]).items():
                for bl in BLOCKS:
                    si += 1
                    boot = circular_boot(d, bl, np.random.default_rng(SEED + 30000 + si))
                    lo, hi = np.quantile(boot, [.025, .975])
                    improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                    rows.append({
                        "comparison": f"V5DCE_vs_{name}", "period": period,
                        "metric": metric, "block_len": bl,
                        "observed_diff": float(np.mean(d)),
                        "ci95_low": float(lo), "ci95_high": float(hi),
                        "bootstrap_improve_share": improve, "n": int(len(z)),
                    })
    return pd.DataFrame(rows)


def cluster_inference(g):
    rows = []
    rng = np.random.default_rng(SEED + 39000)
    for label, mask in [
        ("2025-2026", g.year.isin([2025, 2026])),
        ("2026", g.year == 2026),
    ]:
        z = g[mask & g.v5_route].copy()
        z["gain"] = np.where(
            (z.p_aurora >= .5).astype(int) != z.y_up.astype(int),
            1.0, -1.0
        )
        c = z.groupby("cot_report_date").gain.sum().to_numpy(float)
        boots = np.array([rng.choice(c, len(c), replace=True).sum() for _ in range(REPS)])
        lo, hi = np.quantile(boots, [.025, .975])
        rows.append({
            "period": label, "cluster_n": int(len(c)), "routed_n": int(len(z)),
            "net_rescue": float(c.sum()), "ci95_low": float(lo), "ci95_high": float(hi),
            "p_net_positive": float(np.mean(boots > 0)),
        })
    return pd.DataFrame(rows)


def sensitivity(base):
    rows = []
    for pt in [0.40, 0.50, 0.60, 0.70, 0.75, 0.80]:
        s = apply_dce(base, posterior_threshold=pt, gt_threshold=0.50)
        for label, mask in [
            ("2025", s.year == 2025),
            ("2026", s.year == 2026),
            ("2025-2026", s.year.isin([2025, 2026])),
        ]:
            z = s[mask]
            m = metrics(z.y_up, z.p_helios_v5_dce)
            routed, rescue, broken, net = rescue_counts(z, "p_helios_v5_dce")
            rows.append({
                "sensitivity": "path_posterior",
                "threshold": pt, "gt_threshold": 0.50, "period": label,
                "accuracy": m["accuracy"], "balanced_accuracy": m["balanced_accuracy"],
                "brier": m["brier"], "logloss": m["logloss"],
                "routed_n": routed, "rescued": rescue, "broken": broken,
                "net_rescue": net, "exception_n": int(z.dce_exception.sum()),
            })

    for gt in [0.50, 0.60, 0.70, 0.80]:
        s = apply_dce(base, posterior_threshold=0.50, gt_threshold=gt)
        for label, mask in [
            ("2025", s.year == 2025),
            ("2026", s.year == 2026),
            ("2025-2026", s.year.isin([2025, 2026])),
        ]:
            z = s[mask]
            m = metrics(z.y_up, z.p_helios_v5_dce)
            routed, rescue, broken, net = rescue_counts(z, "p_helios_v5_dce")
            rows.append({
                "sensitivity": "gt_share",
                "threshold": 0.50, "gt_threshold": gt, "period": label,
                "accuracy": m["accuracy"], "balanced_accuracy": m["balanced_accuracy"],
                "brier": m["brier"], "logloss": m["logloss"],
                "routed_n": routed, "rescued": rescue, "broken": broken,
                "net_rescue": net, "exception_n": int(z.dce_exception.sum()),
            })
    return pd.DataFrame(rows)


def main():
    base = load_base()
    g = apply_dce(base)
    g.to_csv(OUT / "helios_v5_dce_predictions.csv", index=False)

    met = score_periods(g)
    met.to_csv(OUT / "helios_v5_dce_metrics.csv", index=False)

    inf = inference(g)
    inf.to_csv(OUT / "helios_v5_dce_inference.csv", index=False)

    cinf = cluster_inference(g)
    cinf.to_csv(OUT / "helios_v5_dce_cluster_inference.csv", index=False)

    sens = sensitivity(base)
    sens.to_csv(OUT / "helios_v5_dce_sensitivity.csv", index=False)

    ev = g[g.dce_exception].copy()
    ev["aurora_dir"] = np.where(ev.p_aurora >= .5, "UP", "DOWN")
    ev["v5_dir"] = np.where(ev.p_helios_v5_dce >= .5, "UP", "DOWN")
    ev["actual_dir"] = np.where(ev.y_up == 1, "UP", "DOWN")
    ev["effect"] = np.where(
        (ev.p_aurora >= .5).astype(int) != ev.y_up.astype(int),
        "RESCUED", "BROKEN"
    )
    ev.to_csv(OUT / "helios_v5_dce_exceptions.csv", index=False)

    guard = {
        "same_2023_as_v4": bool(np.allclose(
            g.loc[g.year == 2023, "p_helios_v5_dce"],
            g.loc[g.year == 2023, "p_helios_v4_rge"])),
        "same_2024_as_v4": bool(np.allclose(
            g.loc[g.year == 2024, "p_helios_v5_dce"],
            g.loc[g.year == 2024, "p_helios_v4_rge"])),
    }

    summary = {
        "schema": "HELIOS_H3_V5_DCE",
        "status": "POSTHOC_MECHANISM_RESULT",
        "binding": {
            "posterior_threshold": POSTERIOR_THRESHOLD,
            "gt_threshold": GT_THRESHOLD,
            "active_expert": "PATH_GLOBAL",
            "probability_rule": "mirror AURORA only on DCE exception",
        },
        "guardrails": guard,
        "metrics": met.to_dict(orient="records"),
        "exceptions": ev[[
            "forecast_issue_date", "target_end_date_h3", "year",
            "cot_report_date", "prob_path_superior", "q_path", "gt_flip_share",
            "p_aurora", "p_opal_reversal", "target_r3",
            "aurora_dir", "v5_dir", "actual_dir", "effect"
        ]].to_dict(orient="records"),
        "inference": inf.to_dict(orient="records"),
        "cluster_inference": cinf.to_dict(orient="records"),
        "sensitivity": sens.to_dict(orient="records"),
    }
    (OUT / "helios_v5_dce_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# HELIOS-H3 V5-DCE — DOMINANT-EXPERT CONTRADICTION EXCEPTION RESULT", "",
        "**Status:** **POSTHOC_MECHANISM_RESULT**  ",
        "**Base:** V4-RGE, modified only at DCE exceptions.  ",
        f"**Guardrails:** 2023 unchanged={guard['same_2023_as_v4']}; 2024 unchanged={guard['same_2024_as_v4']}.", "",
        "## Metrics", "",
        "| Period | AURORA | V2 | V3-GT | V4-RGE | V5-DCE | OPAL | V5 BA | V5 Brier | Exceptions | Rescue | Broken | Net |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in met.itertuples():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.v2_accuracy:.2f}% | "
            f"{100*r.v3_accuracy:.2f}% | {100*r.v4_accuracy:.2f}% | {100*r.v5_accuracy:.2f}% | "
            f"{100*r.opal_accuracy:.2f}% | {100*r.v5_balanced_accuracy:.2f}% | {r.v5_brier:.4f} | "
            f"{r.dce_exception_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} |"
        )

    lines += ["", "## DCE exceptions", "",
              "| Issue | Year | PATH posterior | q_path | GT share | AURORA | V5 | Actual | H3 return | Effect |",
              "|---|---:|---:|---:|---:|---|---|---|---:|---|"]
    for r in ev.itertuples():
        lines.append(
            f"| {pd.Timestamp(r.forecast_issue_date).date()} | {r.year} | "
            f"{100*r.prob_path_superior:.1f}% | {100*r.q_path:.1f}% | {100*r.gt_flip_share:.1f}% | "
            f"{r.aurora_dir} | {r.v5_dir} | {r.actual_dir} | {100*r.target_r3:+.2f}% | {r.effect} |"
        )

    lines += ["", "## Dependence-aware inference", ""]
    for r in inf.itertuples():
        scale = 100 if r.metric == "accuracy" else 1
        unit = " pp" if r.metric == "accuracy" else ""
        lines.append(
            f"- {r.comparison} / {r.period} / {r.metric} / block{r.block_len}: "
            f"diff={scale*r.observed_diff:+.4f}{unit}; "
            f"95%=[{scale*r.ci95_low:+.4f},{scale*r.ci95_high:+.4f}]{unit}; "
            f"P(improve)={100*r.bootstrap_improve_share:.1f}%."
        )
    for r in cinf.itertuples():
        lines.append(
            f"- COT-vintage cluster / {r.period}: net={r.net_rescue:+.0f}, "
            f"clusters={r.cluster_n}, 95%=[{r.ci95_low:+.0f},{r.ci95_high:+.0f}], "
            f"P(net>0)={100*r.p_net_positive:.1f}%."
        )

    lines += ["", "## Sensitivity", ""]
    for r in sens[sens.period == "2025-2026"].itertuples():
        lines.append(
            f"- {r.sensitivity}: path>{r.threshold:.2f}, GT>{r.gt_threshold:.2f}: "
            f"Acc {100*r.accuracy:.2f}%, BA {100*r.balanced_accuracy:.2f}%, "
            f"Brier {r.brier:.4f}, exceptions {r.exception_n}, net {r.net_rescue:+d}."
        )

    lines += ["", "## Governance", "",
        "V5-DCE is post-hoc mechanism research. The three historical exceptions were discovered after retrospective error anatomy. "
        "The result is therefore hypothesis-generating/strengthening evidence, not pristine confirmation. "
        "AURORA remains the frozen prospective champion until a separately frozen future-origin challenger accumulates evidence."
    ]
    (OUT / "HELIOS_V5_DCE_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "HELIOS_V5_DCE_RESULT.md").read_text())


if __name__ == "__main__":
    main()
