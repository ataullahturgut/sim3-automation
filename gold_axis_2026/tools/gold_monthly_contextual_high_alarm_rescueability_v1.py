from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

TAU = 0.50

MODELS = [
    "AOA_ELM",
    "BOOST_CATBOOST_ORDERED",
    "BOOST_RANDOM_FOREST_ANCHOR",
    "ChHHO_ANFIS",
    "DE_ABC_RBFNN",
    "FULL7_ANN",
    "LMC2_RBF_M32",
    "PLS1_V1",
    "REDUCED4_ANN",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1",
    "SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1",
    "SVR_CURRENT8",
    "SVR_DAILY_SUMMARY12",
    "SVR_MIXED20",
]


def load(path):
    return json.loads(Path(path).read_text())


def add_rows(dst, name, rows):
    for r in rows:
        dst[name][str(r["target"])] = {
            "forecast": float(r["forecast"]),
            "actual": float(r["actual"]),
            "rw": float(r["rw"]),
            "origin": str(r.get("origin", "")),
        }


def load_models(a):
    fc = {m: {} for m in MODELS}

    ref = load(a.reference_rows)
    for name in ["AOA_ELM", "ChHHO_ANFIS", "FULL7_ANN", "REDUCED4_ANN"]:
        p = ref["models"][name]
        add_rows(fc, name, p["dev"])
        add_rows(fc, name, p["transport_2025"])
        add_rows(fc, name, p["stress_2026"])

    d = load(a.deabc_json)
    add_rows(fc, "DE_ABC_RBFNN", d["dev"]["rows"])
    add_rows(fc, "DE_ABC_RBFNN", d["transport_2025"]["rows"])
    add_rows(fc, "DE_ABC_RBFNN", d["stress_2026"]["rows"])

    d = load(a.gpr_json)
    add_rows(fc, "LMC2_RBF_M32", d["dev"]["rows"])
    add_rows(fc, "LMC2_RBF_M32", d["transport_2025"]["rows"])
    add_rows(fc, "LMC2_RBF_M32", d["stress_2026"]["rows"])

    d = load(a.pls_json)
    add_rows(fc, "PLS1_V1", d["dev"]["rows"])
    add_rows(fc, "PLS1_V1", d["holdout_2025"]["rows"])
    add_rows(fc, "PLS1_V1", d["stress_2026"]["rows"])

    d = load(a.boost_json)
    add_rows(fc, "BOOST_CATBOOST_ORDERED", d["dev_reproduced"]["CATBOOST_ORDERED"])
    add_rows(fc, "BOOST_CATBOOST_ORDERED", d["transport"]["CATBOOST_ORDERED"])
    add_rows(fc, "BOOST_RANDOM_FOREST_ANCHOR", d["dev_reproduced"]["RANDOM_FOREST_ANCHOR"])
    add_rows(fc, "BOOST_RANDOM_FOREST_ANCHOR", d["transport"]["RANDOM_FOREST_ANCHOR"])

    d = load(a.svr_json)
    for rep in ["CURRENT8", "DAILY_SUMMARY12", "MIXED20"]:
        add_rows(fc, f"SVR_{rep}", d["dev_reproduced"][rep])
        add_rows(fc, f"SVR_{rep}", d["transport"][rep])

    seq_args = [
        ("SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB3_V1", a.seq_cnnlstm_lb3),
        ("SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_CNN_LSTM_LB6_V1", a.seq_cnnlstm_lb6),
        ("SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB3_V1", a.seq_lstm_lb3),
        ("SEQ_GOLD_MONTHLY_CNN_LSTM_STAGE1A_LSTM_LB6_V1", a.seq_lstm_lb6),
    ]
    for name, path in seq_args:
        d = load(path)
        add_rows(fc, name, d["dev_reproduced"])
        add_rows(fc, name, d["transport"])

    return fc


def classify(severity, ch_ae, best_gain_pct, n_better, n_material):
    if severity == "NORMAL":
        return "FALSE_ALARM"
    if best_gain_pct < 0.25:
        return "SHARED_HARD_OR_SHALLOW"
    if n_better >= 8 and n_material >= 4:
        return "BROAD_MATERIAL_RESCUE"
    if n_better >= 8:
        return "BROAD_RESCUE"
    return "NARROW_MATERIAL_RESCUE"


def warning_rows(router):
    out = []
    for period in ["DEV_2022_04_2024_12", "OPENED_2025", "OPENED_2026"]:
        for r in router["periods"][period]["rows"]:
            if float(r["p_high"]) >= TAU:
                x = dict(r)
                x["period"] = period
                out.append(x)
    return sorted(out, key=lambda r: r["target"])


def state_map(state):
    out = {}
    for period in ["dev_2022_04_2024_12", "opened_2025_2026"]:
        for r in state["periods"][period]["EXPANDING_REFIT"]["rows"]:
            out[str(r["target"])] = r
    return out


def exact_geometry_map(exact16):
    out = {str(r["target"]): r for r in exact16["transport_features"]}
    for r in exact16["rows"]:
        if r.get("exact16_feature_available"):
            out.setdefault(str(r["target"]), {
                "chhho_direction_agreement": r.get("exact16_direction_agreement"),
                "dispersion_pct": r.get("exact16_dispersion_pct"),
                "prior_disp_median": r.get("exact16_prior_disp_median"),
            })
    return out


def fixed_fallback(rows, fc, include_false):
    use = rows if include_false else [r for r in rows if r["severity"] != "NORMAL"]
    base_sum = float(sum(r["chhho_ae"] for r in use))
    ranked = []
    for m in MODELS:
        if m == "ChHHO_ANFIS":
            continue
        s = 0.0
        wins = 0
        for r in use:
            ae = abs(fc[m][r["target"]]["forecast"] - r["actual"])
            s += ae
            wins += int(ae < r["chhho_ae"])
        ranked.append({
            "model": m,
            "n": len(use),
            "chhho_sum_ae": base_sum,
            "model_sum_ae": float(s),
            "gain_vs_chhho": float(base_sum - s),
            "wins": int(wins),
        })
    ranked.sort(key=lambda z: (-z["gain_vs_chhho"], -z["wins"], z["model"]))
    return ranked


def oracle(rows, fc):
    base = float(sum(r["chhho_ae"] for r in rows))
    best_alt_sum = 0.0
    keep_or_best_sum = 0.0
    for r in rows:
        aes = [abs(fc[m][r["target"]]["forecast"] - r["actual"]) for m in MODELS if m != "ChHHO_ANFIS"]
        b = min(aes)
        best_alt_sum += b
        keep_or_best_sum += min(b, r["chhho_ae"])
    return {
        "chhho_sum_ae": base,
        "best_alternative_every_warning_sum_ae": float(best_alt_sum),
        "best_alternative_every_warning_gain": float(base - best_alt_sum),
        "keep_or_best_alternative_sum_ae": float(keep_or_best_sum),
        "keep_or_best_alternative_gain": float(base - keep_or_best_sum),
    }


def summarize(rows, fc):
    elev = [r for r in rows if r["severity"] != "NORMAL"]
    false = [r for r in rows if r["severity"] == "NORMAL"]
    groups = defaultdict(list)
    for r in elev:
        groups[(r["semantic_label"], r["state_category"])].append(r)
    context = []
    for (reg, cat), vv in sorted(groups.items()):
        context.append({
            "semantic_label": reg,
            "state_category": cat,
            "n": len(vv),
            "pattern_counts": dict(Counter(r["rescue_pattern"] for r in vv)),
            "mean_alternatives_better": float(np.mean([r["alternatives_better"] for r in vv])),
            "mean_best_gain_pct": float(np.mean([r["best_gain_pct"] for r in vv])),
        })
    return {
        "warnings": len(rows),
        "elevated": len(elev),
        "false": len(false),
        "pattern_counts_all": dict(Counter(r["rescue_pattern"] for r in rows)),
        "pattern_counts_elevated": dict(Counter(r["rescue_pattern"] for r in elev)),
        "best_alt_frequency_elevated": dict(Counter(r["best_alt_model"] for r in elev)),
        "fixed_fallback_elevated_only": fixed_fallback(rows, fc, False),
        "fixed_fallback_all_warnings": fixed_fallback(rows, fc, True),
        "oracle_all_warnings": oracle(rows, fc),
        "context_elevated": context,
    }


def write_md(out, path):
    dev = out["periods"]["DEV"]
    op = out["periods"]["OPENED_2025_2026_JUL"]
    md = []
    md.append("# GOLD MONTHLY — Contextual HIGH-Alarm Rescueability Analysis V1 Result")
    md.append("")
    md.append("**Date:** 2026-10-01  ")
    md.append("**Status:** COMPLETE / ANALYSIS ONLY / NO SWITCH AUTHORIZED")
    md.append("")
    md.append("## 1. Main finding")
    md.append("")
    md.append("There is substantial ex-post rescue headroom, but warning months are heterogeneous. A warning can be a false alarm, a broadly rescueable ChHHO miss, a narrow single-model opportunity, or a shared-hard month. Therefore HIGH must not map directly to one fallback model.")
    md.append("")
    md.append("## 2. DEV anatomy")
    md.append("")
    md.append(f"- warnings: **{dev['warnings']}**")
    md.append(f"- realized HIGH/MEDIUM: **{dev['elevated']}**")
    md.append(f"- realized NORMAL false warnings: **{dev['false']}**")
    md.append(f"- elevated rescue patterns: **{dev['pattern_counts_elevated']}**")
    best = dev["fixed_fallback_elevated_only"][0]
    md.append(f"- best fixed challenger on realized elevated warning months: **{best['model']}**, gain **{best['gain_vs_chhho']:.2f} USD**, wins **{best['wins']}/{best['n']}**")
    bestall = dev["fixed_fallback_all_warnings"][0]
    md.append(f"- crucially, on all warning months including false alarms, even the best fixed fallback is **{bestall['model']}** with gain **{bestall['gain_vs_chhho']:.2f} USD**. Negative means worse than KEEP ChHHO.")
    md.append(f"- oracle KEEP-or-best-alternative ceiling on warning months: **{dev['oracle_all_warnings']['keep_or_best_alternative_gain']:.2f} USD**.")
    md.append("")
    md.append("## 3. Opened 2025..2026-07 descriptive transport")
    md.append("")
    md.append(f"- warnings: **{op['warnings']}**")
    md.append(f"- realized HIGH/MEDIUM: **{op['elevated']}**")
    md.append(f"- false warnings: **{op['false']}**")
    md.append(f"- elevated rescue patterns: **{op['pattern_counts_elevated']}**")
    best = op["fixed_fallback_elevated_only"][0]
    md.append(f"- best fixed challenger on realized elevated warning months: **{best['model']}**, gain **{best['gain_vs_chhho']:.2f} USD**, wins **{best['wins']}/{best['n']}**.")
    bestall = op["fixed_fallback_all_warnings"][0]
    md.append(f"- on all opened warning months, the best retrospective fixed fallback is **{bestall['model']}**, gain **{bestall['gain_vs_chhho']:.2f} USD**. This is opened evidence and is not selection authority.")
    md.append("")
    md.append("## 4. Critical rows")
    md.append("")
    md.append("| Target | Severity | Context | ChHHO AE | Best alt | Best alt AE | Alt better | Pattern |")
    md.append("|---|---|---|---:|---|---:|---:|---|")
    critical = {"2025-02","2025-09","2026-01","2026-03","2026-06"}
    for r in out["rows"]:
        if r["target"] in critical:
            md.append(f"| {r['target']} | {r['severity']} | {r['semantic_label']} / {r['state_category']} | {r['chhho_ae']:.2f} | {r['best_alt_model']} | {r['best_alt_ae']:.2f} | {r['alternatives_better']}/15 | {r['rescue_pattern']} |")
    md.append("")
    md.append("## 5. Structural interpretation")
    md.append("")
    md.append("- DEV proves that a fixed HIGH->fallback rule is unsafe: false warnings erase the gains achieved on true elevated-error months.")
    md.append("- Opened transport contains much more rescueable structure, but that period is already opened and cannot choose a production fallback.")
    md.append("- Regime context is informative but not deterministic: even R2/NORMAL contains broad, narrow, and shallow rescue cases.")
    md.append("- Direction consensus / low dispersion is not a safe KEEP signal. 2025-02 had 100% direction agreement and low dispersion, yet 14/15 alternatives beat ChHHO and the month was broadly materially rescueable.")
    md.append("- 2026-03 is the opposite failure mode: the alarm was useful (MEDIUM), but none of 15 alternatives beat ChHHO. This is a genuine KEEP / shared-hard example.")
    md.append("")
    md.append("## 6. Binding decision")
    md.append("")
    md.append("No SWITCH or BLEND rule is promoted. The next scientifically defensible task is an origin-safe **relative-loss / rescue-gain predictor** that distinguishes KEEP from rescue candidates. It must use alarm + market-state + ensemble-geometry context and preserve abstention. 2025/2026 remains descriptive only.")
    Path(path).write_text("\n".join(md) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--router-json", required=True)
    ap.add_argument("--state-json", required=True)
    ap.add_argument("--exact16-json", required=True)
    ap.add_argument("--reference-rows", required=True)
    ap.add_argument("--deabc-json", required=True)
    ap.add_argument("--gpr-json", required=True)
    ap.add_argument("--pls-json", required=True)
    ap.add_argument("--boost-json", required=True)
    ap.add_argument("--svr-json", required=True)
    ap.add_argument("--seq-cnnlstm-lb3", required=True)
    ap.add_argument("--seq-cnnlstm-lb6", required=True)
    ap.add_argument("--seq-lstm-lb3", required=True)
    ap.add_argument("--seq-lstm-lb6", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-md", required=True)
    a = ap.parse_args()

    router = load(a.router_json)
    state = load(a.state_json)
    exact16 = load(a.exact16_json)
    fc = load_models(a)

    if router["selected_candidate"]["params"]["id"] != "HEDGE_eta0.25_tau0.50":
        raise RuntimeError("ROUTER_NOT_FROZEN")
    if len(MODELS) != 16 or exact16["competitive_models"] != MODELS:
        raise RuntimeError("EXACT16_MODEL_POOL_MISMATCH")

    smap = state_map(state)
    gmap = exact_geometry_map(exact16)
    warnings = warning_rows(router)
    rows = []

    for r in warnings:
        t = str(r["target"])
        if t > "2026-07":
            continue
        missing = [m for m in MODELS if t not in fc[m]]
        if missing:
            raise RuntimeError(("MISSING_MODEL_TARGET", t, missing))
        s = smap[t]
        actual = float(s["actual"])
        ch = float(fc["ChHHO_ANFIS"][t]["forecast"])
        ch_ae = abs(ch - actual)
        vals = []
        for m in MODELS:
            f = float(fc[m][t]["forecast"])
            vals.append((m, f, abs(f - actual)))
        alts = sorted([z for z in vals if z[0] != "ChHHO_ANFIS"], key=lambda z: z[2])
        best = alts[0]
        n_better = sum(ae < ch_ae - 1e-9 for _, _, ae in alts)
        n_material = sum(ae <= 0.75 * ch_ae + 1e-9 for _, _, ae in alts) if ch_ae > 0 else 0
        best_gain = ch_ae - best[2]
        best_gain_pct = best_gain / ch_ae if ch_ae else 0.0
        med_alt = float(np.median([ae for _, _, ae in alts]))
        geo = gmap.get(t, {})

        forecasts = np.asarray([fc[m][t]["forecast"] for m in MODELS], float)
        med_fc = float(np.median(forecasts))
        q25, q75 = np.quantile(forecasts, [0.25, 0.75])
        iqr = float(q75 - q25)
        ch_pctile = float((np.sum(forecasts < ch) + 0.5 * np.sum(forecasts == ch)) / len(forecasts))

        rows.append({
            "period": r["period"],
            "origin": r["origin"],
            "target": t,
            "severity": r["severity"],
            "p_high": float(r["p_high"]),
            "active_signals": r["active_signals"],
            "awake_experts": r["awake_experts"],
            "actual": actual,
            "chhho_forecast": ch,
            "chhho_ae": ch_ae,
            "ape_pct": float(s["ape_pct"]),
            "semantic_label": s["semantic_label"],
            "semantic_state": s["semantic_state"],
            "semantic_probability": float(s["semantic_probability"]),
            "origin_regime_state": s["origin_regime_state"],
            "origin_regime_probability": float(s["origin_regime_probability"]),
            "origin_regime_ood": bool(s["origin_regime_ood"]),
            "state_category": s["state_category"],
            "transition_v2_status": s["transition_v2_status"],
            "extreme_status": s["extreme_status"],
            "best_alt_model": best[0],
            "best_alt_forecast": best[1],
            "best_alt_ae": best[2],
            "best_gain_abs": best_gain,
            "best_gain_pct": best_gain_pct,
            "alternatives_better": int(n_better),
            "alternatives_total": 15,
            "materially_better_25pct": int(n_material),
            "median_alt_ae": med_alt,
            "median_gain_abs": float(ch_ae - med_alt),
            "direction_agreement": geo.get("chhho_direction_agreement"),
            "dispersion_pct": geo.get("dispersion_pct"),
            "prior_disp_median": geo.get("prior_disp_median"),
            "chhho_minus_ensemble_median": float(ch - med_fc),
            "chhho_abs_median_gap_pct": float(abs(ch - med_fc) / abs(med_fc) * 100.0) if med_fc else None,
            "chhho_iqr_distance": float(abs(ch - med_fc) / iqr) if iqr > 1e-12 else None,
            "chhho_forecast_percentile": ch_pctile,
            "rescue_pattern": classify(r["severity"], ch_ae, best_gain_pct, n_better, n_material),
            "top5_alternatives": [
                {"model": m, "forecast": f, "ae": ae, "gain_vs_chhho": float(ch_ae - ae)}
                for m, f, ae in alts[:5]
            ],
        })

    dev = [r for r in rows if r["period"] == "DEV_2022_04_2024_12"]
    op = [r for r in rows if r["period"] in ("OPENED_2025", "OPENED_2026")]

    if len(dev) != 20 or len(op) != 12:
        raise RuntimeError(("WARNING_COUNT_MISMATCH", len(dev), len(op)))
    if any(r["target"] == "2026-08" for r in rows):
        raise RuntimeError("AUG_2026_SHOULD_BE_EXCLUDED")

    out = {
        "schema": "GOLD_MONTHLY_CONTEXTUAL_HIGH_ALARM_RESCUEABILITY_V1_2026-10-01",
        "status": "COMPLETE",
        "scientific_gate": "PASS",
        "coverage": {
            "dev": ["2022-04", "2024-12"],
            "opened_exact16": ["2025-01", "2026-07"],
            "2026_08": "EXCLUDED_FULL16_UNAVAILABLE",
        },
        "taxonomy": {
            "material_improvement": "alternative AE <= 0.75 * ChHHO AE",
            "broad": "at least 8 of 15 alternatives beat ChHHO",
            "selection_role": "DESCRIPTIVE_ONLY",
        },
        "models": MODELS,
        "periods": {
            "DEV": summarize(dev, fc),
            "OPENED_2025_2026_JUL": summarize(op, fc),
        },
        "rows": rows,
        "governance": {
            "router_retuned": False,
            "alarm_definitions_changed": False,
            "competitive_pool_changed": False,
            "forecast_modified": False,
            "switch_tested_as_production": False,
            "2025_2026_used_for_selection": False,
            "taxonomy_used_as_decision_threshold": False,
            "production_authorized": False,
        },
    }

    Path(a.output_json).write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")
    write_md(out, a.output_md)

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "dev_patterns": out["periods"]["DEV"]["pattern_counts_elevated"],
        "opened_patterns": out["periods"]["OPENED_2025_2026_JUL"]["pattern_counts_elevated"],
        "dev_best_fixed_all_warnings": out["periods"]["DEV"]["fixed_fallback_all_warnings"][0],
        "opened_best_fixed_all_warnings": out["periods"]["OPENED_2025_2026_JUL"]["fixed_fallback_all_warnings"][0],
        "dev_oracle": out["periods"]["DEV"]["oracle_all_warnings"],
        "opened_oracle": out["periods"]["OPENED_2025_2026_JUL"]["oracle_all_warnings"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
