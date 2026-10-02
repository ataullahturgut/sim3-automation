from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, confusion_matrix, log_loss, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(os.environ.get("OUT_DIR", "gold_h3_helios_v3_gt_out"))
OUT.mkdir(parents=True, exist_ok=True)

H1 = ROOT / "gold_axis_2026" / "GOLD_H3_HELIOS_V1_PREDICTIONS_2026-10-03.csv"
H2 = ROOT / "gold_axis_2026" / "GOLD_H3_HELIOS_V2_PREDICTIONS_2026-10-03.csv"
OPAL = ROOT / "gold_axis_2026" / "GOLD_H3_OPAL_V1_PREDICTIONS_2026-10-03.csv"

BINDING_WINDOW = 8
BINDING_BROKEN_COST = 1.0
BINDING_THRESHOLD = 0.50
SEED = 20261003
REPS = 10000
BLOCKS = [5, 10]

POLICIES = [
    "KEEP",
    "HELIOS_CONSENSUS",
    "COT_FRESH",
    "FRESH_OR_CONSENSUS",
    "OPAL_ALL",
]


def as_bool(s: pd.Series) -> pd.Series:
    if s.dtype == bool:
        return s
    z = s.astype(str).str.lower().map({"true": True, "false": False})
    if z.isna().any():
        raise RuntimeError("BAD_BOOLEAN_COLUMN")
    return z.astype(bool)


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
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def load_base():
    h = pd.read_csv(H1)
    h2 = pd.read_csv(H2, usecols=["forecast_issue_date", "p_helios_v2"])
    o = pd.read_csv(
        OPAL,
        usecols=[
            "forecast_issue_date", "cot_report_date", "cot_available_date",
            "override", "p_reversal"
        ],
    )

    for df in [h, h2, o]:
        for c in ["feature_cutoff_date", "forecast_issue_date", "target_end_date_h3",
                  "cot_report_date", "cot_available_date"]:
            if c in df.columns:
                df[c] = pd.to_datetime(df[c], errors="raise")

    h = h.merge(h2, on="forecast_issue_date", how="left", validate="one_to_one")
    o = o.rename(columns={
        "override": "opal_override_check",
        "p_reversal": "p_opal_reversal_check",
    })
    h = h.merge(o, on="forecast_issue_date", how="left", validate="one_to_one")

    for c in ["opal_override", "candidate_reversal", "gate_active",
              "rift_override", "turn_override", "vega_override"]:
        h[c] = as_bool(h[c])
    h["opal_override_check"] = as_bool(h["opal_override_check"])

    if not (h.opal_override == h.opal_override_check).all():
        raise RuntimeError("OPAL_OVERRIDE_LINEAGE_MISMATCH")
    if not np.allclose(h.p_opal_reversal, h.p_opal_reversal_check, equal_nan=True):
        raise RuntimeError("OPAL_PROBABILITY_LINEAGE_MISMATCH")
    if (h.cot_available_date > h.forecast_issue_date).any():
        raise RuntimeError("FUTURE_COT_AVAILABILITY")

    h = h.sort_values("forecast_issue_date").reset_index(drop=True)

    seen = {}
    vintage_pos = []
    for r in h.itertuples(index=False):
        if bool(r.opal_override):
            key = str(pd.Timestamp(r.cot_report_date).date())
            seen[key] = seen.get(key, 0) + 1
            vintage_pos.append(seen[key])
        else:
            vintage_pos.append(0)
    h["cot_vintage_opal_position"] = vintage_pos
    h["cot_fresh"] = h.cot_vintage_opal_position.eq(1)

    h["aurora_pred"] = (h.p_aurora >= 0.5).astype(int)
    h["opal_rescue_success"] = np.where(
        h.opal_override,
        (h.aurora_pred != h.y_up.astype(int)).astype(float),
        np.nan,
    )
    return h


def policy_votes(row):
    consensus = bool(row.candidate_reversal)
    fresh = bool(row.cot_fresh)
    return {
        "KEEP": 0,
        "HELIOS_CONSENSUS": int(consensus),
        "COT_FRESH": int(fresh),
        "FRESH_OR_CONSENSUS": int(fresh or consensus),
        "OPAL_ALL": 1,
    }


def simulate_market(base, window=BINDING_WINDOW, broken_cost=BINDING_BROKEN_COST,
                    policy_names=None, threshold=BINDING_THRESHOLD):
    policy_names = list(policy_names or POLICIES)
    g = base.copy().sort_values("forecast_issue_date").reset_index(drop=True)

    history = []
    pending = []
    rows = []

    eta = math.sqrt(8.0 * math.log(len(policy_names)) / float(window))

    for r in g.itertuples(index=False):
        cutoff = pd.Timestamp(r.feature_cutoff_date)
        keep = []
        for item in pending:
            if pd.Timestamp(item["target_end_date_h3"]) <= cutoff:
                history.append(item)
            else:
                keep.append(item)
        pending = keep

        recent = history[-window:]
        votes = policy_votes(r)

        utilities = {}
        raw_logw = {}
        for name in policy_names:
            u = 0.0
            for e in recent:
                if e["votes"][name]:
                    u += 1.0 if e["success"] else -float(broken_cost)
            utilities[name] = u
            raw_logw[name] = eta * u

        mx = max(raw_logw.values())
        weights = {k: math.exp(v - mx) for k, v in raw_logw.items()}
        den = sum(weights.values())
        norm = {k: weights[k] / den for k in policy_names}
        share = float(sum(norm[k] * votes[k] for k in policy_names))

        route = bool(r.gate_active and r.opal_override and share > threshold)
        pa = float(r.p_aurora)
        p_gt = float(1.0 - pa) if route else pa

        rec = r._asdict()
        rec.update({
            "gt_window": int(window),
            "gt_broken_cost": float(broken_cost),
            "gt_eta": float(eta),
            "gt_matured_opal_n": int(len(history)),
            "gt_recent_opal_n": int(len(recent)),
            "gt_flip_share": share,
            "gt_route": route,
            "p_helios_v3_gt": p_gt,
            "gt_top_policy": max(norm, key=norm.get),
            "gt_policy_weights_json": json.dumps(norm, sort_keys=True),
            "gt_policy_utilities_json": json.dumps(utilities, sort_keys=True),
        })
        rows.append(rec)

        if bool(r.opal_override):
            pending.append({
                "target_end_date_h3": r.target_end_date_h3,
                "success": bool(r.opal_rescue_success),
                "votes": votes,
                "cot_report_date": r.cot_report_date,
            })

    return pd.DataFrame(rows)


def rescue_counts(z, prob_col):
    y = z.y_up.astype(int)
    a = (z.p_aurora >= 0.5).astype(int)
    q = (z[prob_col] >= 0.5).astype(int)
    changed = a != q
    rescue = int((changed & (a != y) & (q == y)).sum())
    broken = int((changed & (a == y) & (q != y)).sum())
    return {
        "routed_n": int(changed.sum()),
        "rescued": rescue,
        "broken": broken,
        "net_rescue": rescue - broken,
    }


def score_periods(g):
    specs = [
        ("2023", g.year == 2023),
        ("2024", g.year == 2024),
        ("2025", g.year == 2025),
        ("2026", g.year == 2026),
        ("2023-2024", g.year.isin([2023, 2024])),
        ("2025-2026", g.year.isin([2025, 2026])),
    ]
    rows = []
    for label, mask in specs:
        z = g[mask].copy()
        a = metrics(z.y_up, z.p_aurora)
        v2 = metrics(z.y_up, z.p_helios_v2)
        gt = metrics(z.y_up, z.p_helios_v3_gt)
        op = metrics(z.y_up, z.p_opal_raw)
        rc = rescue_counts(z, "p_helios_v3_gt")
        routed = z[z.gt_route]
        rows.append({
            "period": label,
            **{f"aurora_{k}": v for k, v in a.items()},
            **{f"v2_{k}": v for k, v in v2.items()},
            **{f"gt_{k}": v for k, v in gt.items()},
            **{f"opal_{k}": v for k, v in op.items()},
            **rc,
            "unique_cot_vintages_routed": int(routed.cot_report_date.nunique()),
        })
    return pd.DataFrame(rows)


def logloss_row(y, p):
    p = np.clip(np.asarray(p, float), 1e-6, 1 - 1e-6)
    y = np.asarray(y, int)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def paired_diff(y, cand, base):
    y = np.asarray(y, int)
    cand = np.asarray(cand, float)
    base = np.asarray(base, float)
    return {
        "accuracy": ((cand >= .5).astype(int) == y).astype(float)
                  - ((base >= .5).astype(int) == y).astype(float),
        "brier": (cand - y) ** 2 - (base - y) ** 2,
        "logloss": logloss_row(y, cand) - logloss_row(y, base),
    }


def circular_boot(diff, block_len, rng):
    diff = np.asarray(diff, float)
    n = len(diff)
    nb = int(np.ceil(n / block_len))
    vals = np.empty(REPS, float)
    offs = np.arange(block_len)
    batch = 500
    for st in range(0, REPS, batch):
        m = min(batch, REPS - st)
        starts = rng.integers(0, n, size=(m, nb))
        idx = (starts[:, :, None] + offs[None, None, :]) % n
        idx = idx.reshape(m, -1)[:, :n]
        vals[st:st + m] = diff[idx].mean(axis=1)
    return vals


def block_inference(g):
    rows = []
    si = 0
    comparisons = {
        "AURORA": "p_aurora",
        "HELIOS_V2": "p_helios_v2",
        "OPAL_RAW": "p_opal_raw",
    }
    periods = {
        "2023-2024": g.year.isin([2023, 2024]),
        "2025-2026": g.year.isin([2025, 2026]),
        "2026": g.year == 2026,
    }
    for base_name, base_col in comparisons.items():
        for period, mask in periods.items():
            z = g[mask].copy()
            for metric, d in paired_diff(z.y_up, z.p_helios_v3_gt, z[base_col]).items():
                for bl in BLOCKS:
                    si += 1
                    boot = circular_boot(d, bl, np.random.default_rng(SEED + si))
                    lo, hi = np.quantile(boot, [.025, .975])
                    improve = float(np.mean(boot > 0)) if metric == "accuracy" else float(np.mean(boot < 0))
                    rows.append({
                        "comparison": f"V3GT_vs_{base_name}",
                        "period": period,
                        "metric": metric,
                        "block_len": int(bl),
                        "observed_diff": float(np.mean(d)),
                        "ci95_low": float(lo),
                        "ci95_high": float(hi),
                        "bootstrap_improve_share": improve,
                        "n": int(len(z)),
                    })
    return pd.DataFrame(rows)


def vintage_cluster_inference(g):
    rows = []
    rng = np.random.default_rng(SEED + 9000)
    for label, mask in [
        ("2025-2026", g.year.isin([2025, 2026])),
        ("2026", g.year == 2026),
    ]:
        z = g[mask & g.gt_route].copy()
        if z.empty:
            continue
        z["event_gain"] = np.where(z.aurora_pred != z.y_up.astype(int), 1.0, -1.0)
        c = z.groupby("cot_report_date", as_index=False).event_gain.sum()
        vals = c.event_gain.to_numpy(float)
        boots = np.empty(REPS)
        for i in range(REPS):
            boots[i] = rng.choice(vals, size=len(vals), replace=True).sum()
        lo, hi = np.quantile(boots, [.025, .975])
        rows.append({
            "comparison": "V3GT_NET_RESCUE_CLUSTERED_BY_COT_VINTAGE",
            "period": label,
            "metric": "net_rescue",
            "cluster_n": int(len(vals)),
            "observed_diff": float(vals.sum()),
            "ci95_low": float(lo),
            "ci95_high": float(hi),
            "bootstrap_improve_share": float(np.mean(boots > 0)),
            "n": int(len(z)),
        })
    return pd.DataFrame(rows)


def robustness(base):
    rows = []

    def add(config_type, config, sim, periods=("2024", "2025", "2026", "2025-2026")):
        period_map = {
            "2024": sim.year == 2024,
            "2025": sim.year == 2025,
            "2026": sim.year == 2026,
            "2025-2026": sim.year.isin([2025, 2026]),
        }
        for p in periods:
            z = sim[period_map[p]].copy()
            m = metrics(z.y_up, z.p_helios_v3_gt)
            rc = rescue_counts(z, "p_helios_v3_gt")
            rows.append({
                "config_type": config_type,
                "config": config,
                "period": p,
                "accuracy": m["accuracy"],
                "balanced_accuracy": m["balanced_accuracy"],
                "brier": m["brier"],
                "logloss": m["logloss"],
                **rc,
            })

    for w in [6, 8, 10, 12]:
        add("window", f"W{w}_C1.00", simulate_market(base, window=w, broken_cost=1.0))

    for cost in [1.25, 1.50]:
        add("broken_cost", f"W8_C{cost:.2f}", simulate_market(base, window=8, broken_cost=cost))

    sets = {
        "NO_UNION": ["KEEP", "HELIOS_CONSENSUS", "COT_FRESH", "OPAL_ALL"],
        "NO_FRESH": ["KEEP", "HELIOS_CONSENSUS", "FRESH_OR_CONSENSUS", "OPAL_ALL"],
        "NO_OPAL_ALL": ["KEEP", "HELIOS_CONSENSUS", "COT_FRESH", "FRESH_OR_CONSENSUS"],
        "CORE3": ["KEEP", "HELIOS_CONSENSUS", "OPAL_ALL"],
    }
    for name, policies in sets.items():
        add("policy_ablation", name, simulate_market(base, policy_names=policies), periods=("2025-2026", "2026"))

    return pd.DataFrame(rows)


def event_ledger(g):
    z = g[g.opal_override].copy()
    z["aurora_dir"] = np.where(z.p_aurora >= .5, "UP", "DOWN")
    z["gt_dir"] = np.where(z.p_helios_v3_gt >= .5, "UP", "DOWN")
    z["actual_dir"] = np.where(z.y_up == 1, "UP", "DOWN")
    z["effect"] = "KEEP"
    routed = z.gt_route
    z.loc[routed & (z.aurora_pred != z.y_up.astype(int)), "effect"] = "RESCUED"
    z.loc[routed & (z.aurora_pred == z.y_up.astype(int)), "effect"] = "BROKEN"
    cols = [
        "feature_cutoff_date", "forecast_issue_date", "target_end_date_h3", "year",
        "cot_report_date", "cot_available_date", "cot_vintage_opal_position",
        "cot_fresh", "p_aurora", "p_opal_reversal", "corroborator_n",
        "candidate_reversal", "gate_active", "gt_matured_opal_n", "gt_recent_opal_n",
        "gt_flip_share", "gt_route", "gt_top_policy", "aurora_dir", "gt_dir",
        "actual_dir", "target_r3", "effect", "gt_policy_weights_json",
        "gt_policy_utilities_json",
    ]
    return z[cols]


def main():
    base = load_base()
    gt = simulate_market(base)
    gt.to_csv(OUT / "helios_v3_gt_predictions.csv", index=False)

    met = score_periods(gt)
    met.to_csv(OUT / "helios_v3_gt_metrics.csv", index=False)

    ev = event_ledger(gt)
    ev.to_csv(OUT / "helios_v3_gt_event_ledger.csv", index=False)

    rob = robustness(base)
    rob.to_csv(OUT / "helios_v3_gt_robustness.csv", index=False)

    inf = block_inference(gt)
    cinf = vintage_cluster_inference(gt)
    inf.to_csv(OUT / "helios_v3_gt_inference.csv", index=False)
    cinf.to_csv(OUT / "helios_v3_gt_vintage_cluster_inference.csv", index=False)

    opal_events = gt[gt.opal_override].copy()
    policy_cols = [
        "forecast_issue_date", "target_end_date_h3", "year", "cot_report_date",
        "cot_vintage_opal_position", "gate_active", "candidate_reversal",
        "opal_rescue_success", "gt_matured_opal_n", "gt_recent_opal_n",
        "gt_flip_share", "gt_route", "gt_top_policy", "gt_policy_weights_json",
        "gt_policy_utilities_json",
    ]
    opal_events[policy_cols].to_csv(OUT / "helios_v3_gt_policy_state.csv", index=False)

    summary = {
        "schema": "HELIOS_H3_V3_GT",
        "status": "POSTHOC_STRENGTHENING_RESULT",
        "binding": {
            "window": BINDING_WINDOW,
            "broken_cost": BINDING_BROKEN_COST,
            "decision_threshold": BINDING_THRESHOLD,
            "policies": POLICIES,
            "probability_rule": "mirror AURORA probability only when GT routes",
        },
        "metrics": met.to_dict(orient="records"),
        "robustness": rob.to_dict(orient="records"),
        "block_inference": inf.to_dict(orient="records"),
        "vintage_cluster_inference": cinf.to_dict(orient="records"),
    }
    (OUT / "helios_v3_gt_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n"
    )

    lines = [
        "# HELIOS-H3 V3-GT — GAME-THEORETIC REVERSAL ARBITER RESULT", "",
        "**Status:** **POSTHOC_STRENGTHENING_RESULT**  ",
        "**Binding design:** W8, rescue +1 / broken -1, five-policy Hedge market, threshold >0.50.  ",
        "**Probability:** mirror frozen AURORA probability only on routed events.  ", "",
        "## Period metrics", "",
        "| Period | AURORA Acc | HELIOS V2 Acc | V3-GT Acc | Raw OPAL Acc | AURORA BA | V3-GT BA | AURORA Brier | V2 Brier | V3-GT Brier | Routed | Rescue | Broken | Net |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in met.itertuples():
        lines.append(
            f"| {r.period} | {100*r.aurora_accuracy:.2f}% | {100*r.v2_accuracy:.2f}% | "
            f"{100*r.gt_accuracy:.2f}% | {100*r.opal_accuracy:.2f}% | "
            f"{100*r.aurora_balanced_accuracy:.2f}% | {100*r.gt_balanced_accuracy:.2f}% | "
            f"{r.aurora_brier:.4f} | {r.v2_brier:.4f} | {r.gt_brier:.4f} | "
            f"{r.routed_n} | {r.rescued} | {r.broken} | {r.net_rescue:+d} |"
        )

    lines += ["", "## 2026 routed events", "",
              "| Issue | COT vintage | Pos | Market share | AURORA | V3-GT | Actual | H3 return | Effect |",
              "|---|---|---:|---:|---|---|---|---:|---|"]
    for r in ev[(ev.year == 2026) & ev.gt_route].itertuples():
        lines.append(
            f"| {pd.Timestamp(r.forecast_issue_date).date()} | {pd.Timestamp(r.cot_report_date).date()} | "
            f"{r.cot_vintage_opal_position} | {100*r.gt_flip_share:.1f}% | {r.aurora_dir} | "
            f"{r.gt_dir} | {r.actual_dir} | {100*r.target_r3:+.2f}% | {r.effect} |"
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
            f"- {r.comparison} / {r.period}: net={r.observed_diff:+.0f}; "
            f"COT-vintage clusters={r.cluster_n}; 95%=[{r.ci95_low:+.0f},{r.ci95_high:+.0f}]; "
            f"P(net>0)={100*r.bootstrap_improve_share:.1f}%."
        )

    lines += ["", "## Robustness summary", ""]
    for r in rob[(rob.period == "2025-2026")].itertuples():
        lines.append(
            f"- {r.config_type} / {r.config}: Acc {100*r.accuracy:.2f}%, "
            f"routed {r.routed_n}, rescue/broken {r.rescued}/{r.broken}, net {r.net_rescue:+d}, "
            f"Brier {r.brier:.4f}."
        )

    lines += ["", "## Governance", "",
              "V3-GT is retrospective strengthening research. Its architecture was developed after historical error anatomy and therefore cannot be called prospective confirmation. "
              "The frozen AURORA prospective champion remains unchanged. Any operational promotion requires a separate future-origin V3-GT freeze with no retrospective retuning."]

    (OUT / "HELIOS_V3_GT_RESULT.md").write_text("\n".join(lines) + "\n")
    print((OUT / "HELIOS_V3_GT_RESULT.md").read_text())


if __name__ == "__main__":
    main()
