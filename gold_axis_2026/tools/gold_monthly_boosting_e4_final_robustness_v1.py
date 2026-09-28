#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_ensemble_e1_baselines_v1 as e1

DEV_START, DEV_END = "2022-04", "2024-12"
TOL = 1e-8

FULL5 = ["CATBOOST_PRICE", "CATBOOST_BALANCED", "GBRT", "LIGHTGBM", "XGB_DIRECTION"]

REFS = {
    "CATBOOST_PRICE": {
        "sum_abs_error": 1460.433935309605,
        "direction_correct": 20,
    },
    "FULL5_MEDIAN": {
        "sum_abs_error": 1484.731330609916,
        "direction_correct": 23,
    },
}


def winner(a, b, a_name, b_name, tol=TOL):
    if a < b - tol:
        return a_name
    if b < a - tol:
        return b_name
    return "TIE"


def stability(metrics):
    yearly_mae = {
        y: float(metrics["yearly"][y]["mae"])
        for y in ("2022", "2023", "2024")
    }
    vals = np.array(list(yearly_mae.values()), dtype=float)
    return {
        "monthly_ae_std": float(metrics["monthly_ae_std"]),
        "median_ae": float(metrics["median_ae"]),
        "worst_ae": float(metrics["worst_ae"]),
        "worst_month": metrics["worst_month"],
        "yearly_mae": yearly_mae,
        "yearly_mae_range": float(vals.max() - vals.min()),
        "yearly_mae_std_population": float(np.std(vals, ddof=0)),
    }


def render_report(payload):
    p = payload["principal"]
    pair = payload["pairwise"]
    dr = payload["direction_rescue_loss"]
    loo = payload["leave_one_origin"]
    comp = payload["leave_one_component_out"]

    lines = [
        "# GOLD MONTHLY FORECAST — BOOSTING E4 FINAL ROBUSTNESS RESULT",
        "",
        "Date: 2026-09-28",
        "Status: COMPLETE / SCIENTIFIC GATE PASS",
        "",
        "## Principal candidates",
        "",
        "| Role | Candidate | SigmaAE | Direction | MAE | Worst month | Worst AE |",
        "|---|---|---:|---:|---:|---|---:|",
        (
            f"| PRICE | CATBOOST_PRICE | {p['CATBOOST_PRICE']['metrics']['sum_abs_error']:.6f} | "
            f"{p['CATBOOST_PRICE']['metrics']['direction_correct']}/33 | "
            f"{p['CATBOOST_PRICE']['metrics']['mae']:.6f} | "
            f"{p['CATBOOST_PRICE']['metrics']['worst_month']} | "
            f"{p['CATBOOST_PRICE']['metrics']['worst_ae']:.6f} |"
        ),
        (
            f"| BALANCE / DIRECTION | FULL5_MEDIAN | {p['FULL5_MEDIAN']['metrics']['sum_abs_error']:.6f} | "
            f"{p['FULL5_MEDIAN']['metrics']['direction_correct']}/33 | "
            f"{p['FULL5_MEDIAN']['metrics']['mae']:.6f} | "
            f"{p['FULL5_MEDIAN']['metrics']['worst_month']} | "
            f"{p['FULL5_MEDIAN']['metrics']['worst_ae']:.6f} |"
        ),
        "",
        "## Year-by-year",
        "",
    ]

    for name in ("CATBOOST_PRICE", "FULL5_MEDIAN"):
        lines += [f"### {name}", "", "| Year | SigmaAE | MAE | Direction |", "|---|---:|---:|---:|"]
        for y in ("2022", "2023", "2024"):
            m = p[name]["metrics"]["yearly"][y]
            lines.append(
                f"| {y} | {m['sum_abs_error']:.6f} | {m['mae']:.6f} | {m['direction_correct']}/{m['n']} |"
            )
        lines.append("")

    lines += [
        "## Pairwise monthly AE",
        f"- CATBOOST_PRICE wins: **{pair['CATBOOST_PRICE_wins']}**",
        f"- FULL5_MEDIAN wins: **{pair['FULL5_MEDIAN_wins']}**",
        f"- Ties: **{pair['ties']}**",
        "",
        "## Direction rescue / loss relative to CATBOOST_PRICE",
        f"- Median rescues: **{dr['rescue']}**",
        f"- Median losses: **{dr['loss']}**",
        f"- Both correct: **{dr['both_correct']}**",
        f"- Both wrong: **{dr['both_wrong']}**",
        "",
        "## Worst-month sensitivity",
        "",
    ]

    for name in ("CATBOOST_PRICE", "FULL5_MEDIAN"):
        w = payload["worst_month_sensitivity"][name]
        lines += [
            f"### {name}",
            f"- Removed month: **{w['removed_month']}**",
            f"- Removed AE: **{w['removed_ae']:.6f}**",
            f"- Remaining n=32 SigmaAE: **{w['remaining_sum_abs_error']:.6f}**",
            f"- Remaining n=32 MAE: **{w['remaining_mae']:.6f}**",
            "",
        ]

    lines += [
        "## Common leave-one-origin sensitivity",
        f"- CATBOOST_PRICE preferred: **{loo['CATBOOST_PRICE_wins']} / 33 omissions**",
        f"- FULL5_MEDIAN preferred: **{loo['FULL5_MEDIAN_wins']} / 33 omissions**",
        f"- Ties: **{loo['ties']}**",
        "",
        "## FULL5 leave-one-component-out diagnostic only",
        "",
        "| Omitted component | SigmaAE | Direction | Delta vs FULL5 Median |",
        "|---|---:|---:|---:|",
    ]
    for name, r in comp.items():
        lines.append(
            f"| {name} | {r['metrics']['sum_abs_error']:.6f} | "
            f"{r['metrics']['direction_correct']}/33 | {r['delta_sigma_ae_vs_full5_median']:+.6f} |"
        )

    lines += [
        "",
        "## Stability summary",
        "",
        "| Candidate | Monthly AE std | Median AE | Yearly MAE range | Yearly MAE std |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in ("CATBOOST_PRICE", "FULL5_MEDIAN"):
        s = payload["stability"][name]
        lines.append(
            f"| {name} | {s['monthly_ae_std']:.6f} | {s['median_ae']:.6f} | "
            f"{s['yearly_mae_range']:.6f} | {s['yearly_mae_std_population']:.6f} |"
        )

    lines += [
        "",
        "## E4 decision",
        "Robustness is diagnostic only and does not perform post-hoc model reselection.",
        "",
        "- E4 scientific/integrity gate: **PASS**",
        "- Proceed to E5 final Boosting freeze.",
        "- PRICE role remains **CATBOOST_PRICE**.",
        "- BALANCE / DIRECTION role remains **FULL5_MEDIAN**.",
        "",
        "## Reproducibility",
        f"- Payload SHA256: {payload['payload_sha256']}",
        "",
        "## Kontrol ve Uyum Özeti",
        "- Frozen predictions exact reconciliation: PASS.",
        "- DEV scope 2022-04..2024-12, n=33: PASS.",
        "- Robustness-only diagnostics: PASS.",
        "- Leave-one-component-out used for reselection: NO.",
        "- 2025 opened: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        "",
    ]
    return "\n".join(lines)


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    targets, components = e1.read_components(bundle)
    if targets[0] != DEV_START or targets[-1] != DEV_END or len(targets) != 33:
        raise RuntimeError("DEV_SCOPE_FAIL")

    cat_rows = components["CATBOOST_PRICE"]["rows"]
    cat_pred = np.array([float(r["forecast"]) for r in cat_rows], dtype=float)
    actual = np.array([float(r["actual"]) for r in cat_rows], dtype=float)
    rw = np.array([float(r["rw"]) for r in cat_rows], dtype=float)

    t2, P, actual2, rw2 = e1.matrix(components, FULL5)
    if t2 != targets or not np.allclose(actual, actual2) or not np.allclose(rw, rw2):
        raise RuntimeError("FULL5_ALIGNMENT_FAIL")

    med_pred = np.median(P, axis=1)

    cat_metrics = e1.metrics(cat_pred, actual, rw, targets)
    med_metrics = e1.metrics(med_pred, actual, rw, targets)

    if abs(cat_metrics["sum_abs_error"] - REFS["CATBOOST_PRICE"]["sum_abs_error"]) > TOL:
        raise RuntimeError("CATBOOST_PRICE_AE_REPRO_FAIL")
    if cat_metrics["direction_correct"] != REFS["CATBOOST_PRICE"]["direction_correct"]:
        raise RuntimeError("CATBOOST_PRICE_DIR_REPRO_FAIL")
    if abs(med_metrics["sum_abs_error"] - REFS["FULL5_MEDIAN"]["sum_abs_error"]) > TOL:
        raise RuntimeError("FULL5_MEDIAN_AE_REPRO_FAIL")
    if med_metrics["direction_correct"] != REFS["FULL5_MEDIAN"]["direction_correct"]:
        raise RuntimeError("FULL5_MEDIAN_DIR_REPRO_FAIL")

    cat_ae = np.abs(cat_pred - actual)
    med_ae = np.abs(med_pred - actual)
    cat_dc = np.sign(cat_pred - rw) == np.sign(actual - rw)
    med_dc = np.sign(med_pred - rw) == np.sign(actual - rw)

    month_rows = []
    cat_wins = med_wins = ties = 0
    rescue = loss = both_correct = both_wrong = 0

    for i, target in enumerate(targets):
        w = winner(cat_ae[i], med_ae[i], "CATBOOST_PRICE", "FULL5_MEDIAN")
        if w == "CATBOOST_PRICE":
            cat_wins += 1
        elif w == "FULL5_MEDIAN":
            med_wins += 1
        else:
            ties += 1

        if (not cat_dc[i]) and med_dc[i]:
            dclass = "RESCUE"
            rescue += 1
        elif cat_dc[i] and (not med_dc[i]):
            dclass = "LOSS"
            loss += 1
        elif cat_dc[i] and med_dc[i]:
            dclass = "BOTH_CORRECT"
            both_correct += 1
        else:
            dclass = "BOTH_WRONG"
            both_wrong += 1

        month_rows.append(
            {
                "target": target,
                "actual": float(actual[i]),
                "rw": float(rw[i]),
                "catboost_price_forecast": float(cat_pred[i]),
                "catboost_price_ae": float(cat_ae[i]),
                "catboost_price_direction_correct": bool(cat_dc[i]),
                "full5_median_forecast": float(med_pred[i]),
                "full5_median_ae": float(med_ae[i]),
                "full5_median_direction_correct": bool(med_dc[i]),
                "ae_winner": w,
                "direction_relation": dclass,
            }
        )

    worst = {}
    for name, ae in (("CATBOOST_PRICE", cat_ae), ("FULL5_MEDIAN", med_ae)):
        i = int(np.argmax(ae))
        remaining_sum = float(ae.sum() - ae[i])
        worst[name] = {
            "removed_month": targets[i],
            "removed_ae": float(ae[i]),
            "remaining_n": 32,
            "remaining_sum_abs_error": remaining_sum,
            "remaining_mae": float(remaining_sum / 32.0),
        }

    loo_rows = []
    loo_cat = loo_med = loo_tie = 0
    for i, target in enumerate(targets):
        c = float(cat_ae.sum() - cat_ae[i])
        m = float(med_ae.sum() - med_ae[i])
        w = winner(c, m, "CATBOOST_PRICE", "FULL5_MEDIAN")
        if w == "CATBOOST_PRICE":
            loo_cat += 1
        elif w == "FULL5_MEDIAN":
            loo_med += 1
        else:
            loo_tie += 1
        loo_rows.append(
            {
                "removed_target": target,
                "catboost_price_sum_abs_error_n32": c,
                "full5_median_sum_abs_error_n32": m,
                "winner": w,
            }
        )

    loco = {}
    for j, omitted in enumerate(FULL5):
        keep = [k for k in range(len(FULL5)) if k != j]
        pred = np.median(P[:, keep], axis=1)
        m = e1.metrics(pred, actual, rw, targets)
        loco[omitted] = {
            "metrics": m,
            "delta_sigma_ae_vs_full5_median": float(
                m["sum_abs_error"] - med_metrics["sum_abs_error"]
            ),
            "selection_evidence": False,
        }

    after = e1.s5.read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    payload = {
        "scope": "BOOSTING_E4_FINAL_ROBUSTNESS_V1",
        "freeze_file": "GOLD_MONTHLY_BOOSTING_E4_FINAL_ROBUSTNESS_FREEZE_2026-09-28.md",
        "contract": {
            "dev": f"{DEV_START}..{DEV_END}",
            "dev_n": 33,
            "principal_candidates": ["CATBOOST_PRICE", "FULL5_MEDIAN"],
            "robustness_role": "DIAGNOSTIC_ONLY_NO_POSTHOC_RESELECTION",
            "leave_one_component_out_role": "DIAGNOSTIC_ONLY",
            "random_split": "NONE",
            "database": "READ_ONLY",
            "2025_role": "NOT_OPENED_NOT_EVALUATED",
            "2026_role": "QUARANTINED_NOT_USED",
        },
        "principal": {
            "CATBOOST_PRICE": {"role": "PRICE", "metrics": cat_metrics},
            "FULL5_MEDIAN": {"role": "BALANCE_DIRECTION", "metrics": med_metrics},
        },
        "pairwise": {
            "CATBOOST_PRICE_wins": cat_wins,
            "FULL5_MEDIAN_wins": med_wins,
            "ties": ties,
            "rows": month_rows,
        },
        "direction_rescue_loss": {
            "rescue": rescue,
            "loss": loss,
            "both_correct": both_correct,
            "both_wrong": both_wrong,
        },
        "worst_month_sensitivity": worst,
        "leave_one_origin": {
            "CATBOOST_PRICE_wins": loo_cat,
            "FULL5_MEDIAN_wins": loo_med,
            "ties": loo_tie,
            "rows": loo_rows,
            "selection_evidence": False,
        },
        "leave_one_component_out": loco,
        "stability": {
            "CATBOOST_PRICE": stability(cat_metrics),
            "FULL5_MEDIAN": stability(med_metrics),
        },
        "e4_gate": "PASS",
        "e5_roles": {
            "PRICE": "CATBOOST_PRICE",
            "BALANCE_DIRECTION": "FULL5_MEDIAN",
        },
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
    }

    compact = {
        "cat_forecasts": cat_pred.tolist(),
        "median_forecasts": med_pred.tolist(),
        "pairwise_counts": [cat_wins, med_wins, ties],
        "direction_counts": [rescue, loss, both_correct, both_wrong],
        "loo_counts": [loo_cat, loo_med, loo_tie],
        "loco": {
            k: {
                "sum_abs_error": v["metrics"]["sum_abs_error"],
                "direction_correct": v["metrics"]["direction_correct"],
            }
            for k, v in loco.items()
        },
    }
    digest = hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    payload["payload_sha256"] = digest

    Path("gold_monthly_boosting_e4_final_robustness_v1_result.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    Path(
        "gold_axis_2026/GOLD_MONTHLY_BOOSTING_E4_FINAL_ROBUSTNESS_RESULT_2026-09-28.md"
    ).write_text(render_report(payload), encoding="utf-8")

    print("OUTPUT_GATE=PASS", flush=True)
    print(
        json.dumps(
            {
                "principal": {
                    k: v["metrics"] for k, v in payload["principal"].items()
                },
                "pairwise": {
                    "CATBOOST_PRICE_wins": cat_wins,
                    "FULL5_MEDIAN_wins": med_wins,
                    "ties": ties,
                },
                "direction_rescue_loss": payload["direction_rescue_loss"],
                "leave_one_origin": {
                    "CATBOOST_PRICE_wins": loo_cat,
                    "FULL5_MEDIAN_wins": loo_med,
                    "ties": loo_tie,
                },
                "leave_one_component_out": {
                    k: {
                        "sum_abs_error": v["metrics"]["sum_abs_error"],
                        "direction_correct": v["metrics"]["direction_correct"],
                        "delta": v["delta_sigma_ae_vs_full5_median"],
                    }
                    for k, v in loco.items()
                },
                "payload_sha256": digest,
                "authority_invariants_unchanged": after == bundle.invariants_before,
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
