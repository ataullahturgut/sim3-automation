from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, fisher_exact

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"

DIV = AX / "GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
V2 = AX / "GOLD_H3_RULEFLOW_V2_GATED_SUMMARY_2026-10-04.json"
Q23 = AX / "GOLD_H3_RULEFLOW_V2_Q2Q3_STRESS_EVENTS_2026-10-04.csv"

OUT_MD = AX / "GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.md"
OUT_CSV = AX / "GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv"
OUT_JSON = AX / "GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.json"

ALPHA = 0.05


def as_bool(v):
    if isinstance(v, (bool, np.bool_)):
        return bool(v)
    if pd.isna(v):
        return False
    return str(v).strip().lower() in {"true", "1", "yes"}


def corr_info(h, x, y):
    a = pd.to_numeric(h[x], errors="coerce").to_numpy(float)
    b = pd.to_numeric(h[y], errors="coerce").to_numpy(float)
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    if len(a) < 10 or np.std(a) <= 1e-12 or np.std(b) <= 1e-12:
        return np.nan, np.nan, int(len(a))
    r, p = pearsonr(a, b)
    return float(r), float(p), int(len(a))


def topology(div, date):
    dt = pd.Timestamp(date)
    hit = div.index[div.feature_cutoff_date == dt]
    if len(hit) != 1:
        raise RuntimeError(f"Expected one DIVERGE row for {date}, got {len(hit)}")
    j = int(hit[0])
    out = {}
    for w in (20, 60):
        h = div.iloc[max(0, j - w):j]
        r_ndx, p_ndx, n_ndx = corr_info(h, "gold_daily_ret1", "ndx_ret1")
        r_vix, p_vix, n_vix = corr_info(h, "gold_daily_ret1", "vix_ret1")
        out.update({
            f"ndx_r{w}": r_ndx,
            f"ndx_p{w}": p_ndx,
            f"ndx_n{w}": n_ndx,
            f"vix_r{w}": r_vix,
            f"vix_p{w}": p_vix,
            f"vix_n{w}": n_vix,
        })

    pro60 = out["ndx_r60"] > 0 and out["vix_r60"] < 0
    safe60 = out["ndx_r60"] < 0 and out["vix_r60"] > 0
    sig60 = min(out["ndx_p60"], out["vix_p60"]) < ALPHA
    out["strong_pro_risk"] = bool(pro60 and sig60)

    if pro60 and sig60:
        out["topology60"] = "STRONG_PRO_RISK"
    elif safe60 and sig60:
        out["topology60"] = "STRONG_SAFE_HAVEN"
    elif pro60:
        out["topology60"] = "WEAK_PRO_RISK"
    elif safe60:
        out["topology60"] = "WEAK_SAFE_HAVEN"
    else:
        out["topology60"] = "MIXED"

    safe20 = out["ndx_r20"] < 0 and out["vix_r20"] > 0
    pro20 = out["ndx_r20"] > 0 and out["vix_r20"] < 0
    out["strict_safe_20_60"] = bool(safe20 and safe60)
    out["strict_pro_20_60"] = bool(pro20 and pro60)
    out["safe60_sign_only"] = bool(safe60)
    return out


def build_hotspots(div):
    v2 = json.loads(V2.read_text())
    rows = []

    for period, key in [("2025", "detail_2025"), ("2026Q1", "detail_2026Q1")]:
        for r in v2[key]:
            rows.append({
                "period": period,
                "date": r["date"],
                "v2_gate": bool(r["gate"]),
                "v2_candidate": bool(r["candidate"]),
                "v2_rescue": bool(r["rescue"]),
                "v2_broken": bool(r["broken"]),
            })

    q = pd.read_csv(Q23)
    q = q[(q["available"].map(as_bool)) & (q["hotspot"].map(as_bool))].copy()
    for _, r in q.iterrows():
        rows.append({
            "period": "2026Q2Q3",
            "date": str(r["date"]),
            "v2_gate": as_bool(r["gate"]),
            "v2_candidate": as_bool(r["candidate"]),
            "v2_rescue": as_bool(r["rescue"]),
            "v2_broken": as_bool(r["broken"]),
        })

    z = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    rev_map = div.set_index("feature_cutoff_date")["reversal_target"].to_dict()

    topo_rows = []
    for _, r in z.iterrows():
        d = dict(r)
        dt = pd.Timestamp(r["date"])
        d["reversal"] = bool(int(rev_map[dt]))
        d.update(topology(div, r["date"]))
        topo_rows.append(d)

    z = pd.DataFrame(topo_rows)

    # Binding successor: only a statistically strong 60d pro-risk topology vetoes V2.
    z["v3_candidate"] = z["v2_candidate"] & ~z["strong_pro_risk"]
    z["v3_rescue"] = z["v2_rescue"] & z["v3_candidate"]
    z["v3_broken"] = z["v2_broken"] & z["v3_candidate"]

    # Sensitivity 1: previous hard 20d+60d SAFE-only confirmation.
    z["strict_candidate"] = z["v2_candidate"] & z["strict_safe_20_60"]
    z["strict_rescue"] = z["v2_rescue"] & z["strict_candidate"]
    z["strict_broken"] = z["v2_broken"] & z["strict_candidate"]

    # Sensitivity 2: 60d SAFE sign-only gate.
    z["safe60_candidate"] = z["v2_candidate"] & z["safe60_sign_only"]
    z["safe60_rescue"] = z["v2_rescue"] & z["safe60_candidate"]
    z["safe60_broken"] = z["v2_broken"] & z["safe60_candidate"]

    return z


def perf(df, prefix):
    cand = df[f"{prefix}_candidate"]
    rescue = int(df.loc[cand, f"{prefix}_rescue"].sum())
    broken = int(df.loc[cand, f"{prefix}_broken"].sum())
    actions = int(cand.sum())
    return {
        "actions": actions,
        "rescue": rescue,
        "broken": broken,
        "net": rescue - broken,
        "precision": rescue / actions if actions else np.nan,
    }


def main():
    div = pd.read_csv(DIV, parse_dates=["feature_cutoff_date"]).sort_values("feature_cutoff_date").reset_index(drop=True)
    z = build_hotspots(div)
    z.to_csv(OUT_CSV, index=False)

    periods = ["2025", "2026Q1", "2026Q2Q3"]
    period_rows = []
    for p in periods:
        q = z[z.period == p]
        period_rows.append({
            "period": p,
            "hotspots": len(q),
            **{f"v2_{k}": v for k, v in perf(q, "v2").items()},
            **{f"v3_{k}": v for k, v in perf(q, "v3").items()},
        })

    p2 = perf(z, "v2")
    p3 = perf(z, "v3")
    ps = perf(z, "strict")
    p60 = perf(z, "safe60")

    rescue_retention = p3["rescue"] / p2["rescue"] if p2["rescue"] else np.nan
    broken_suppression = 1 - p3["broken"] / p2["broken"] if p2["broken"] else np.nan

    strong = z[z.strong_pro_risk]
    other = z[~z.strong_pro_risk]
    strong_rev = int(strong.reversal.sum())
    strong_non = len(strong) - strong_rev
    other_rev = int(other.reversal.sum())
    other_non = len(other) - other_rev
    hotspot_fisher = fisher_exact(
        [[strong_rev, strong_non], [other_rev, other_non]], alternative="less"
    )

    action = z[z.v2_candidate].copy()
    action_strong = action[action.strong_pro_risk]
    action_other = action[~action.strong_pro_risk]
    action_fisher = fisher_exact(
        [
            [int(action_strong.v2_rescue.sum()), int(action_strong.v2_broken.sum())],
            [int(action_other.v2_rescue.sum()), int(action_other.v2_broken.sum())],
        ],
        alternative="less",
    )

    summary = {
        "status": "POST_Q2Q3_DIAGNOSTIC_NOT_VALIDATION",
        "binding_v3_rule": {
            "window": 60,
            "pro_risk_signs": {"gold_ndx": ">0", "gold_vix": "<0"},
            "strength_rule": "min(two-sided Pearson p-values) < 0.05",
            "action": "veto RuleFlow V2 FLIP; KEEP V5",
        },
        "combined": {
            "v2": p2,
            "v3_topology_veto": p3,
            "rescue_retention": rescue_retention,
            "broken_suppression": broken_suppression,
        },
        "sensitivities": {
            "hard_20d_60d_safe_confirmation": ps,
            "safe60_sign_only": p60,
        },
        "topology_hotspots": {
            "strong_pro_risk_n": len(strong),
            "strong_pro_risk_reversal": strong_rev,
            "strong_pro_risk_reversal_rate": strong_rev / len(strong),
            "other_n": len(other),
            "other_reversal": other_rev,
            "other_reversal_rate": other_rev / len(other),
            "fisher_one_sided_p": float(hotspot_fisher.pvalue),
        },
        "v2_action_topology": {
            "strong_pro_risk_actions": len(action_strong),
            "strong_pro_risk_rescue": int(action_strong.v2_rescue.sum()),
            "strong_pro_risk_broken": int(action_strong.v2_broken.sum()),
            "other_actions": len(action_other),
            "other_rescue": int(action_other.v2_rescue.sum()),
            "other_broken": int(action_other.v2_broken.sum()),
            "fisher_one_sided_p": float(action_fisher.pvalue),
        },
        "periods": period_rows,
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# GOLD H3 — RULEFLOW V3-TG TOPOLOGY DIAGNOSTIC",
        "",
        "**Date:** 2026-10-04",
        "**Status:** POST-Q2Q3 DIAGNOSTIC — NOT VALIDATION",
        "",
        "## Binding successor tested",
        "",
        "Keep every frozen RuleFlow V2 condition. Add one veto:",
        "",
        "- 60-origin Gold-Nasdaq correlation > 0",
        "- 60-origin Gold-VIX correlation < 0",
        "- at least one of those two correlations has two-sided Pearson p < 0.05",
        "- then VETO the RuleFlow FLIP and KEEP V5.",
        "",
        "The veto is one-sided: pro-risk topology does not create an opposite trade.",
        "",
        "## Main action result",
        "",
        "| Rule | Actions | Rescue | Broken | Net | Precision | Rescue retention | Broken suppression |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| RuleFlow V2 | {p2['actions']} | {p2['rescue']} | {p2['broken']} | {p2['net']:+d} | {100*p2['precision']:.1f}% | — | — |",
        f"| RuleFlow V3-TG | {p3['actions']} | {p3['rescue']} | {p3['broken']} | {p3['net']:+d} | {100*p3['precision']:.1f}% | {100*rescue_retention:.1f}% | {100*broken_suppression:.1f}% |",
        "",
        "Diagnostic delta: net improves from +2 to +6 because all 6 historical rescues survive while all 4 Q2-Q3 broken actions are vetoed.",
        "",
        "## Period split",
        "",
        "| Period | Hotspots | V2 actions | V2 R/B/net | V3 actions | V3 R/B/net |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in period_rows:
        lines.append(
            f"| {r['period']} | {r['hotspots']} | {r['v2_actions']} | "
            f"{r['v2_rescue']}/{r['v2_broken']}/{r['v2_net']:+d} | "
            f"{r['v3_actions']} | {r['v3_rescue']}/{r['v3_broken']}/{r['v3_net']:+d} |"
        )

    lines += [
        "",
        "## Why strength matters",
        "",
        f"- STRONG_PRO_RISK hotspots: {strong_rev}/{len(strong)} reversal = {100*strong_rev/len(strong):.1f}%",
        f"- All other hotspots: {other_rev}/{len(other)} reversal = {100*other_rev/len(other):.1f}%",
        f"- Fisher one-sided p = {hotspot_fisher.pvalue:.5f}",
        "",
        "Among V2 actions:",
        f"- STRONG_PRO_RISK: {int(action_strong.v2_rescue.sum())} rescue / {int(action_strong.v2_broken.sum())} broken",
        f"- Other topology: {int(action_other.v2_rescue.sum())} rescue / {int(action_other.v2_broken.sum())} broken",
        f"- Fisher one-sided p = {action_fisher.pvalue:.5f}",
        "",
        "These p-values are descriptive only because the topology hypothesis was discovered after seeing the Q2-Q3 failures.",
        "",
        "## Sensitivity: the first 20d+60d hard-confirmation idea",
        "",
        "| Variant | Actions | Rescue | Broken | Net | Precision |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Hard SAFE confirmation at both 20d and 60d | {ps['actions']} | {ps['rescue']} | {ps['broken']} | {ps['net']:+d} | {100*ps['precision']:.1f}% |",
        f"| 60d SAFE sign-only | {p60['actions']} | {p60['rescue']} | {p60['broken']} | {p60['net']:+d} | {100*p60['precision']:.1f}% |",
        f"| Binding V3 strong-pro-risk veto | {p3['actions']} | {p3['rescue']} | {p3['broken']} | {p3['net']:+d} | {100*p3['precision']:.1f}% |",
        "",
        "The hard 20d+60d confirmation is rejected as too restrictive: it suppresses valid rescue episodes during topology transition.",
        "",
        "## Action-level topology",
        "",
        "| Date | V2 outcome | NDX r60 | VIX r60 | min p60 | Topology | V3 |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for _, r in action.sort_values("date").iterrows():
        outcome = "RESCUE" if r.v2_rescue else "BROKEN"
        minp = min(r.ndx_p60, r.vix_p60)
        decision = "VETO" if r.strong_pro_risk else "KEEP FLIP"
        lines.append(
            f"| {r.date} | {outcome} | {r.ndx_r60:+.3f} | {r.vix_r60:+.3f} | "
            f"{minp:.4f} | {r.topology60} | {decision} |"
        )

    lines += [
        "",
        "## Scientific decision",
        "",
        "RuleFlow V2 remains closed. RuleFlow V3-TG is a mechanistically stronger successor candidate, but the 2025/Q1/Q2-Q3 replay is consumed diagnostic evidence, not independent validation.",
        "",
        "The V3 topology rule is frozen here for genuinely unseen origins from the clean prospective period beginning 2026-10-05. No threshold or sign change is allowed without opening a new challenger identity.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n")
    print(OUT_MD.read_text())


if __name__ == "__main__":
    main()
