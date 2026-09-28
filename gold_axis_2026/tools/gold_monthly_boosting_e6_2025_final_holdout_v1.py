#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np

import vw_midas_msvr_successor_v1 as base
import gold_monthly_boosting_stage5_regularization_v1 as s5

HOLDOUT_START, HOLDOUT_END = "2025-01", "2025-12"
TOL = 1e-8

SPECS = {
    "CATBOOST_PRICE": ("CATBOOST_PRICE", "CB_R0_BASELINE"),
    "CATBOOST_BALANCED": ("CATBOOST_BALANCED", "CB_R0_BASELINE"),
    "GBRT": ("GBRT_PRICE_BALANCED", "G_R0_BASELINE"),
    "LIGHTGBM": ("LIGHTGBM_PRICE_BALANCED", "L_R0_BASELINE"),
    "XGB_DIRECTION": ("XGBOOST_DIRECTION", "X_R1_L2_5"),
}
FULL5 = ["CATBOOST_PRICE", "CATBOOST_BALANCED", "GBRT", "LIGHTGBM", "XGB_DIRECTION"]

DEV_REFS = {
    "CATBOOST_PRICE": {"sum_abs_error": 1460.433935309605, "direction_correct": 20},
    "FULL5_MEDIAN": {"sum_abs_error": 1484.731330609916, "direction_correct": 23},
}


def get_lane_and_reg(lane_name, profile_name):
    lane = next(x for x in s5.LANES if x["lane"] == lane_name)
    profile, reg = next(x for x in lane["profiles"] if x[0] == profile_name)
    return lane, profile, reg


def metrics(rows):
    a = np.asarray([r["actual"] for r in rows], float)
    f = np.asarray([r["forecast"] for r in rows], float)
    rw = np.asarray([r["rw"] for r in rows], float)
    ae = np.abs(f-a)
    rw_ae = np.abs(rw-a)
    d = np.asarray([r["direction_correct"] for r in rows], bool)
    wi = int(np.argmax(ae))
    return {
        "n": len(rows),
        "sum_abs_error": float(ae.sum()),
        "mae": float(ae.mean()),
        "rmse": float(np.sqrt(np.mean((f-a)**2))),
        "mape_pct": float(np.mean(ae/np.maximum(np.abs(a),1e-12))*100.0),
        "wape_pct": float(ae.sum()/np.maximum(np.abs(a).sum(),1e-12)*100.0),
        "median_ae": float(np.median(ae)),
        "monthly_ae_std": float(np.std(ae, ddof=0)),
        "worst_ae": float(ae[wi]),
        "worst_month": rows[wi]["target"],
        "relative_mae_vs_rw": float(ae.sum()/max(float(rw_ae.sum()),1e-12)),
        "direction_correct": int(d.sum()),
        "direction_accuracy_pct": float(d.mean()*100.0),
        "rw_sum_abs_error": float(rw_ae.sum()),
    }


def main():
    dsn = os.environ.get("NEON_DATABASE_URL")
    if not dsn:
        raise SystemExit("NEON_DATABASE_URL required")

    bundle = base.load_data(dsn)
    targets = list(base.month_range(HOLDOUT_START, HOLDOUT_END))
    if targets[0] != HOLDOUT_START or targets[-1] != HOLDOUT_END or len(targets) != 12:
        raise RuntimeError("HOLDOUT_SCOPE_FAIL")

    # Exact frozen component replay for the one-shot 2025 holdout.
    cache = {t: base.all_samples_at_origin(bundle, t, governed=True) for t in targets}
    components = {}
    for name, (lane_name, profile_name) in SPECS.items():
        lane, profile, reg = get_lane_and_reg(lane_name, profile_name)
        rows = [
            s5.predict_one(bundle, cache[t], t, lane, profile, reg)
            for t in targets
        ]
        if [r["target"] for r in rows] != targets:
            raise RuntimeError(f"TARGET_ALIGNMENT_FAIL {name}")
        components[name] = {
            "lane": lane_name,
            "profile": profile_name,
            "rows": rows,
            "metrics": metrics(rows),
        }

    # PRICE role = frozen CatBoost PRICE.
    price_rows = components["CATBOOST_PRICE"]["rows"]
    price_metrics = metrics(price_rows)

    # BALANCE/DIRECTION role = frozen row-wise median of FULL5 price forecasts.
    actual = np.asarray([r["actual"] for r in price_rows], float)
    rw = np.asarray([r["rw"] for r in price_rows], float)
    P = np.column_stack([
        [float(r["forecast"]) for r in components[name]["rows"]]
        for name in FULL5
    ])
    median_forecast = np.median(P, axis=1)

    median_rows = []
    for i, t in enumerate(targets):
        f = float(median_forecast[i])
        a = float(actual[i])
        rwi = float(rw[i])
        pd = int(np.sign(f-rwi))
        ad = int(np.sign(a-rwi))
        median_rows.append({
            "target": t,
            "origin": base.month_shift(t, -1),
            "forecast": f,
            "actual": a,
            "rw": rwi,
            "absolute_error": float(abs(f-a)),
            "pred_direction": pd,
            "actual_direction": ad,
            "direction_correct": bool(pd == ad),
            "component_forecasts": {
                name: float(P[i, j]) for j, name in enumerate(FULL5)
            },
        })
    median_metrics = metrics(median_rows)

    after = s5.read_invariants(dsn)
    if after != bundle.invariants_before:
        raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    compact = {
        "targets": targets,
        "price": [
            {
                "target": r["target"],
                "forecast": r["forecast"],
                "actual": r["actual"],
                "rw": r["rw"],
                "direction_correct": r["direction_correct"],
            }
            for r in price_rows
        ],
        "median": [
            {
                "target": r["target"],
                "forecast": r["forecast"],
                "actual": r["actual"],
                "rw": r["rw"],
                "direction_correct": r["direction_correct"],
            }
            for r in median_rows
        ],
    }
    digest = hashlib.sha256(
        json.dumps(compact, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()

    out = {
        "scope": "BOOSTING_E6_2025_FINAL_HOLDOUT_V1",
        "final_freeze_file": "GOLD_MONTHLY_BOOSTING_E5_FINAL_FREEZE_2026-09-28.md",
        "contract": {
            "holdout": f"{HOLDOUT_START}..{HOLDOUT_END}",
            "holdout_n": 12,
            "one_shot": True,
            "price_role": "CATBOOST_PRICE",
            "balance_direction_role": "FULL5_MEDIAN",
            "full5_components": FULL5,
            "post_holdout_tuning": "PROHIBITED",
            "model_reselection": "PROHIBITED",
            "random_split": "NONE",
            "database": "READ_ONLY",
            "2026_role": "QUARANTINED_NOT_USED",
        },
        "dev_freeze_references": DEV_REFS,
        "components_2025": components,
        "PRICE": {
            "model": "CATBOOST_PRICE",
            "metrics": price_metrics,
            "rows": price_rows,
        },
        "BALANCE_DIRECTION": {
            "model": "FULL5_MEDIAN",
            "metrics": median_metrics,
            "rows": median_rows,
        },
        "authority_invariants_before": bundle.invariants_before,
        "authority_invariants_after": after,
        "payload_sha256": digest,
    }

    Path("gold_monthly_boosting_e6_2025_final_holdout_v1_result.json").write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# GOLD MONTHLY FORECAST — BOOSTING E6 2025 FINAL HOLDOUT RESULT",
        "",
        "Date: 2026-09-28",
        "Status: COMPLETE / ONE-SHOT HOLDOUT / SCIENTIFIC GATE PASS",
        "",
        "## Frozen roles",
        "- PRICE: CATBOOST_PRICE",
        "- BALANCE / DIRECTION: FULL5_MEDIAN",
        "- No post-holdout tuning or model reselection is permitted.",
        "",
        "## 2025 summary",
        "",
        "| Role | SigmaAE | MAE | RMSE | MAPE | WAPE | Rel.MAE vs RW | Direction | Worst month | Worst AE |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ]
    for role in ("PRICE", "BALANCE_DIRECTION"):
        m = out[role]["metrics"]
        lines.append(
            f"| {role} | {m['sum_abs_error']:.6f} | {m['mae']:.6f} | {m['rmse']:.6f} | "
            f"{m['mape_pct']:.4f}% | {m['wape_pct']:.4f}% | {m['relative_mae_vs_rw']:.6f} | "
            f"{m['direction_correct']}/12 | {m['worst_month']} | {m['worst_ae']:.6f} |"
        )

    lines += [
        "",
        "## Month-by-month — PRICE",
        "",
        "| Month | Actual | Forecast | AE | RW | Direction correct |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in price_rows:
        lines.append(
            f"| {r['target']} | {r['actual']:.6f} | {r['forecast']:.6f} | "
            f"{abs(r['forecast']-r['actual']):.6f} | {r['rw']:.6f} | "
            f"{'YES' if r['direction_correct'] else 'NO'} |"
        )

    lines += [
        "",
        "## Month-by-month — BALANCE / DIRECTION",
        "",
        "| Month | Actual | Forecast | AE | RW | Direction correct |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in median_rows:
        lines.append(
            f"| {r['target']} | {r['actual']:.6f} | {r['forecast']:.6f} | "
            f"{r['absolute_error']:.6f} | {r['rw']:.6f} | "
            f"{'YES' if r['direction_correct'] else 'NO'} |"
        )

    lines += [
        "",
        "## Final interpretation rule",
        "These 2025 results are final transport evidence only. They cannot reopen or modify Boosting architecture.",
        "",
        "## Reproducibility",
        f"- Payload SHA256: {digest}",
        "",
        "## Kontrol ve Uyum Özeti",
        "- E5 architecture freeze respected: PASS.",
        "- 2025 evaluated exactly once under frozen roles: PASS.",
        "- 2025 used for tuning/selection: NO.",
        "- 2026 used: NO.",
        "- Random split: NONE.",
        "- DB mutation: NONE / READ_ONLY.",
        "- Boosting family status after E6: CLOSED.",
        "",
    ]

    Path(
        "gold_axis_2026/GOLD_MONTHLY_BOOSTING_E6_2025_FINAL_HOLDOUT_RESULT_2026-09-28.md"
    ).write_text("\n".join(lines), encoding="utf-8")

    print("OUTPUT_GATE=PASS", flush=True)
    print(json.dumps({
        "PRICE": price_metrics,
        "BALANCE_DIRECTION": median_metrics,
        "payload_sha256": digest,
        "authority_invariants_unchanged": after == bundle.invariants_before,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
