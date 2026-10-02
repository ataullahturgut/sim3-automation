from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

from gold_h3_helios_v3_gt import (
    BLOCKS, POLICIES, REPS, SEED, circular_boot, load_base, logloss_row,
    metrics, paired_diff, policy_votes,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_helios_v4_rge_out"))
OUT.mkdir(parents=True, exist_ok=True)

V3 = ROOT / "gold_axis_2026" / "GOLD_H3_HELIOS_V3_GT_PREDICTIONS_2026-10-03.csv"

MARKET_WINDOW = 8
EXPANSION_WINDOW = 10
ENTER_REGRET = 2
EXIT_REGRET = -2
THRESHOLD = 0.50


def as_bool(s):
    if s.dtype == bool:
        return s
    z = s.astype(str).str.lower().map({"true": True, "false": False})
    if z.isna().any():
        raise RuntimeError("BAD_BOOL")
    return z.astype(bool)


def attach_v3(base):
    v3 = pd.read_csv(V3, usecols=["forecast_issue_date", "p_helios_v3_gt"])
    v3["forecast_issue_date"] = pd.to_datetime(v3.forecast_issue_date, errors="raise")
    return base.merge(v3, on="forecast_issue_date", how="left", validate="one_to_one")


def simulate_rge(base, expansion_window=EXPANSION_WINDOW,
                 enter_regret=ENTER_REGRET, exit_regret=EXIT_REGRET):
    g = base.copy().sort_values("forecast_issue_date").reset_index(drop=True)

    eta = math.sqrt(8.0 * math.log(len(POLICIES)) / float(MARKET_WINDOW))
    all_hist, all_pending = [], []
    ext_hist, ext_pending = [], []
    active = False
    rows, switches = [], []

    for r in g.itertuples(index=False):
        cutoff = pd.Timestamp(r.feature_cutoff_date)

        keep = []
        for item in all_pending:
            if pd.Timestamp(item["target_end_date_h3"]) <= cutoff:
                all_hist.append(item)
            else:
                keep.append(item)
        all_pending = keep

        keep = []
        for item in ext_pending:
            if pd.Timestamp(item["target_end_date_h3"]) <= cutoff:
                ext_hist.append(item)
            else:
                keep.append(item)
        ext_pending = keep

        recent_ext = ext_hist[-expansion_window:]
        regret = int(sum(1 if e["success"] else -1 for e in recent_ext))
        wins = int(sum(1 for e in recent_ext if e["success"]))
        losses = int(len(recent_ext) - wins)
        prior = active

        if len(recent_ext) >= expansion_window:
            if (not active) and regret >= enter_regret:
                active = True
            elif active and regret <= exit_regret:
                active = False

        if active != prior:
            switches.append({
                "forecast_issue_date": str(pd.Timestamp(r.forecast_issue_date).date()),
                "new_state": "ACTIVE" if active else "INACTIVE",
                "matured_nonconsensus_n": int(len(ext_hist)),
                "recent_n": int(len(recent_ext)),
                "recent_wins": wins,
                "recent_losses": losses,
                "recent_regret": regret,
                "recent_sequence": "".join("1" if e["success"] else "0" for e in recent_ext),
            })

        recent = all_hist[-MARKET_WINDOW:]
        votes = policy_votes(r)
        raw_logw, utilities = {}, {}
        for name in POLICIES:
            u = 0.0
            for e in recent:
                if e["votes"][name]:
                    u += 1.0 if e["success"] else -1.0
            utilities[name] = u
            raw_logw[name] = eta * u
        mx = max(raw_logw.values())
        weights = {k: math.exp(v - mx) for k, v in raw_logw.items()}
        den = sum(weights.values())
        norm = {k: weights[k] / den for k in POLICIES}
        share = float(sum(norm[k] * votes[k] for k in POLICIES))

        base_route = bool(r.hard_route)
        expansion_candidate = bool(
            r.gate_active and r.opal_override and (not r.candidate_reversal)
        )
        expansion_route = bool(expansion_candidate and active and share > THRESHOLD)
        route = bool(base_route or expansion_route)

        pa = float(r.p_aurora)
        p_v4 = float(1.0 - pa) if expansion_route else float(r.p_helios_v2)

        rec = r._asdict()
        rec.update({
            "rge_active": bool(active),
            "rge_matured_nonconsensus_n": int(len(ext_hist)),
            "rge_recent_n": int(len(recent_ext)),
            "rge_recent_wins": wins,
            "rge_recent_losses": losses,
            "rge_recent_regret": regret,
            "gt_flip_share": share,
            "v2_base_route": base_route,
            "rge_expansion_candidate": expansion_candidate,
            "rge_expansion_route": expansion_route,
            "v4_route": route,
            "p_helios_v4_rge": p_v4,
            "gt_policy_weights_json": json.dumps(norm, sort_keys=True),
            "gt_policy_utilities_json": json.dumps(utilities, sort_keys=True),
        })
        rows.append(rec)

        if bool(r.opal_override):
            success = bool(r.aurora_pred != r.y_up)
            item = {
                "target_end_date_h3": r.target_end_date_h3,
                "success": success,
                "votes": votes,
            }
            all_pending.append(item)
            if not bool(r.candidate_reversal):
                ext_pending.append({
                    "target_end_date_h3": r.target_end_date_h3,
                    "success": success,
                })

    return pd.DataFrame(rows), pd.DataFrame(switches)


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
            "opal": metrics(z.y_up, z.p_opal_raw),
        }
        routed, rescue, broken, net = rescue_counts(z, "p_helios_v4_rge")
        rows.append({
            "period": label,
            **{f"{name}_{k}": v for name, m in vals.items() for k, v in m.items()},
            "routed_n": routed,
            "rescued": rescue,
            "broken": broken,
            "net_rescue": net,
            "v2_base_routes": int(z.v2_base_route.sum()),
            "expansion_routes": int(z.rge_expansion_route.sum()),
            "rge_active_share": float(z.rge_active.mean()),
        })
    return pd.DataFrame(rows)


def inference(g):
    rows = []
    comparisons = {
        "AURORA": "p_aurora",
        "HELIOS_V2": "p_helios_v2",
        "HELIOS_V3_GT": "p_helios_v3_gt",
        "OPAL_RAW": "p_opal_raw",
    }
    periods = {
        "2023-2024": g.year.isin([2023, 2024]),
        "2025-2026": g.year.isin([2025, 2026]),
        "2026": g.year == 2026,
    }
    si = 0
    for name, col in comparisons.items():
        for period, mask in periods.items():
            z = g[mask]
            for metric, d in paired_diff(z.y_up, z.p_helios_v4_rge, z[col]).items():
                for bl in BLOCKS:
                    si += 1
                    boot = circular_boot(d, bl, np.random.default_rng(SEED + 20000 + si))
                    lo, hi = np.quantile(boot, [.025, .975])
                    improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                    rows.append({
                        "comparison": f"V4RGE_vs_{name}", "period": period,
                        "metric": metric, "block_len": bl,
                        "observed_diff": float(np.mean(d)),
                        "ci95_low": float(lo), "ci95_high": float(hi),
                        "bootstrap_improve_share": improve, "n": int(len(z)),
                    })
    return pd.DataFrame(rows)


def cluster_inference(g):
    rows = []
    rng = np.random.default_rng(SEED + 29000)
    for label, mask in [
        ("2025-2026", g.year.isin([2025, 2026])),
        ("2026", g.year == 2026),
    ]:
        z = g[mask & g.v4_route].copy()
        z["gain"] = np.where(z.aurora_pred != z.y_up.astype(int), 1.0, -1.0)
        c = z.groupby("cot_report_date").gain.sum().to_numpy(float)
        boots = np.array([rng.choice(c, len(c), replace=True).sum() for _ in range(REPS)])
        lo, hi = np.quantile(boots, [.025, .975])
        rows.append({
            "period": label, "cluster_n": int(len(c)), "routed_n": int(len(z)),
            "net_rescue": float(c.sum()), "ci95_low": float(lo), "ci95_high": float(hi),
            "p_net_positive": float(np.mean(boots > 0)),
        })
    return pd.DataFrame(rows)


def robustness(base):
    rows = []
    for w, en, ex in [(8, 2, -2), (10, 2, -2), (12, 2, -2)]:
        s, sw = simulate_rge(base, expansion_window=w, enter_regret=en, exit_regret=ex)
        for label, mask in [
            ("2025", s.year == 2025),
            ("2026", s.year == 2026),
            ("2025-2026", s.year.isin([2025, 2026])),
        ]:
            z = s[mask]
            m = metrics(z.y_up, z.p_helios_v4_rge)
            routed, rescue, broken, net = rescue_counts(z, "p_helios_v4_rge")
            rows.append({
                "config": f"W{w}_REGRET+2_-2", "period": label,
                "accuracy": m["accuracy"], "balanced_accuracy": m["balanced_accuracy"],
                "brier": m["brier"], "logloss": m["logloss"],
                "routed_n": routed, "rescued": rescue, "broken": broken,
                "net_rescue": net,
                "switches": ";".join(sw.forecast_issue_date.astype(str).tolist()) if not sw.empty else "",
            })
    return pd.DataFrame(rows)


def main():
    base = attach_v3(load_base())
    g, switches = simulate_rge(base)
    g.to_csv(OUT / "helios_v4_rge_predictions.csv", index=False)
    switches.to_csv(OUT / "helios_v4_rge_switches.csv", index=False)

    met = score_periods(g)
    met.to_csv(OUT / "helios_v4_rge_metrics.csv", index=False)

    inf = inference(g)
    inf.to_csv(OUT / "helios_v4_rge_inference.csv", index=False)

    cinf = cluster_inference(g)
    cinf.to_csv(OUT / "helios_v4_rge_cluster_inference.csv", index=False)

    rob = robustness(base)
    rob.to_csv(OUT / "helios_v4_rge_robustness.csv", index=False)

    ev = g[g.v4_route].copy()
    ev["aurora_dir"] = np.where(ev.p_aurora >= .5, "UP", "DOWN")
    ev["v4_dir"] = np.where(ev.p_helios_v4_rge >= .5, "UP", "DOWN")
    ev["actual_dir"] = np.where(ev.y_up == 1, "UP", "DOWN")
    ev["effect"] = np.where(ev.aurora_pred != ev.y_up.astype(int), "RESCUED", "BROKEN")
    ev.to_csv(OUT / "helios_v4_rge_event_ledger.csv", index=False)

    summary = {
        "schema": "HELIOS_H3_V4_RGE",
        "status": "POSTHOC_STRENGTHENING_RESULT",
        "binding": {
            "market_window": MARKET_WINDOW,
            "expansion_window": EXPANSION_WINDOW,
            "enter_regret": ENTER_REGRET,
            "exit_regret": EXIT_REGRET,
            "threshold": THRESHOLD,
        },
        "switches": switches.to_dict(orient="records"),
        "metrics": met.to_dict(orient="records"),
        "inference": inf.to_dict(orient="records"),
        "cluster_inference": cinf.to_dict(orient="records"),
        "robustness": rob.to_dict(orient="records"),
    }
    (OUT / "helios_v4_rge_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# HELIOS-H3 V4-RGE — REGRET-GATED EXPANSION RESULT", "",
        "**Status:** **POSTHOC_STRENGTHENING_RESULT**  ",
        "**Base:** HELIOS V2 preserved; broader OPAL only after positive non-consensus regret.  ", "",
        "## Expansion switches", "",
    ]
    if switches.empty:
        lines.append("- none")
    else:
        for r in switches.itertuples():
            lines.append(
                f"- **{r.forecast_issue_date} -> {r.new_state}**; "
                f"recent {r.recent_n}: {r.recent_sequence}, "
                f"{r.recent_wins}W/{r.recent_losses}L, regret {r.recent_regret:+d}."
            )

    lines += ["", "## Metrics", "",
        "| Period | AURORA | V2 | V3-GT | V4-RGE | OPAL | V4 BA | V4 Brier | Base routes | Expansion | Rescue | Broken | Net |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in met.itertuples():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.v2_accuracy:.2f}% | "
            f"{100*r.v3_accuracy:.2f}% | {100*r.v4_accuracy:.2f}% | {100*r.opal_accuracy:.2f}% | "
            f"{100*r.v4_balanced_accuracy:.2f}% | {r.v4_brier:.4f} | {r.v2_base_routes} | "
            f"{r.expansion_routes} | {r.rescued} | {r.broken} | {r.net_rescue:+d} |"
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

    lines += ["", "## Robustness", ""]
    for r in rob[rob.period == "2025-2026"].itertuples():
        lines.append(
            f"- {r.config}: Acc {100*r.accuracy:.2f}%, BA {100*r.balanced_accuracy:.2f}%, "
            f"Brier {r.brier:.4f}, rescue/broken {r.rescued}/{r.broken}, net {r.net_rescue:+d}, "
            f"switches {r.switches or 'none'}."
        )

    lines += ["", "## Governance", "",
        "V4-RGE is second-order post-hoc strengthening research. It preserves the frozen AURORA champion governance. "
        "No historical result may be treated as prospective confirmation; any operational use requires a separate future-origin freeze."
    ]
    (OUT / "HELIOS_V4_RGE_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "HELIOS_V4_RGE_RESULT.md").read_text())


if __name__ == "__main__":
    main()
