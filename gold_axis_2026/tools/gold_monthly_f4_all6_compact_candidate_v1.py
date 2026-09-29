from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_elmfis_baseline_v1 as eb
import gold_monthly_f4_b1_transform_parity_v1 as b1

DEV_START, DEV_END = "2022-04", "2024-12"
BASE_SIGMAAE = 1413.0297794085
BASE_DIRECTION = 23
RULES = 5
BASE_POP = 24
BASE_INPUTS = 8

VARIANTS = {
    "BASE": {"inputs": 8, "population": 24},
    "ALL6": {"inputs": 22, "population": 66},
}


def configure(inputs: int, population: int) -> dict:
    c = anfis.common
    if c.RULES != RULES:
        raise RuntimeError(f"RULE_COUNT_CHANGED {c.RULES}")
    n_ant = RULES * inputs
    param_dim = 2 * n_ant
    expected_population = int(math.ceil(BASE_POP * param_dim / (2 * RULES * BASE_INPUTS)))
    if population != expected_population:
        raise RuntimeError(
            f"POPULATION_DENSITY_FAIL inputs={inputs} observed={population} expected={expected_population}"
        )

    c.INPUTS = inputs
    c.N_ANT = n_ant
    c.PARAM_DIM = param_dim
    c.LOWER = np.concatenate([
        np.full(n_ant, c.CENTER_LOW),
        np.full(n_ant, math.log(c.SPREAD_LOW)),
    ])
    c.UPPER = np.concatenate([
        np.full(n_ant, c.CENTER_HIGH),
        np.full(n_ant, math.log(c.SPREAD_HIGH)),
    ])
    c.LOCAL_SIGMA = np.concatenate([
        np.full(n_ant, .45),
        np.full(n_ant, .30),
    ])
    c.REFIT_SIGMA = np.concatenate([
        np.full(n_ant, .16),
        np.full(n_ant, .12),
    ])
    c.POP_SIZE = population

    anfis.POP = population
    anfis.D = param_dim
    anfis.LO = c.LOWER
    anfis.HI = c.UPPER

    return {
        "inputs": inputs,
        "rules": RULES,
        "antecedent_parameter_dimension": param_dim,
        "population": population,
        "generations": int(anfis.GENS),
        "repeats": int(anfis.REPEATS),
    }


def build_series(ext: dict):
    return {
        "NOM10": b1.nested_daily(ext, "h15_daily", "DGS10"),
        "REAL10": b1.nested_daily(ext, "h15_daily", "DFII10"),
        "BROADUSD": b1.nested_daily(ext, "h10_daily", "BROAD_USD_INDEX"),
        "VIX": b1.flat_daily(ext, "vix_daily"),
        "NDX": b1.flat_daily(ext, "nasdaq100_daily"),
        "WTI": b1.flat_daily(ext, "wti_daily"),
        "BRENT": b1.flat_daily(ext, "brent_daily"),
    }


def all6_samples(bundle, outer_target: str, series: dict):
    origin = b1.mshift(outer_target, -1)
    history = bundle.gpr_vintages[origin]
    raw = base.all_samples_at_origin(bundle, outer_target, governed=True)
    out = {}

    for t, (x, y) in raw.items():
        p = b1.mshift(t, -1)
        pp = b1.mshift(t, -2)
        z = base.gpr_norm(history, pp)
        feat, _ = b1.transform_for_sample(series, p, z)
        extx = np.asarray([feat[k] for k in b1.FEATURES], float)
        if extx.shape != (14,) or not np.all(np.isfinite(extx)):
            raise RuntimeError(f"BAD_EXTERNAL_VECTOR outer={outer_target} t={t}")
        xx = np.concatenate([np.asarray(x, float), extx])
        if xx.shape != (22,) or not np.all(np.isfinite(xx)):
            raise RuntimeError(f"BAD_ALL6_VECTOR outer={outer_target} t={t} shape={xx.shape}")
        out[t] = (xx, np.asarray(y, float))
    return out


def evaluate(bundle, variant: str, ext: dict | None):
    cfg = configure(**VARIANTS[variant])
    series = build_series(ext) if variant == "ALL6" else None
    rows = []

    for t in base.month_range(DEV_START, DEV_END):
        samples = (
            base.all_samples_at_origin(bundle, t, governed=True)
            if variant == "BASE"
            else all6_samples(bundle, t, series)
        )
        keys = sorted(k for k in samples if k < t)
        if not keys or keys[0] != "2010-03":
            raise RuntimeError(f"HISTORY_PARITY_FAIL {variant} {t} first={keys[0] if keys else None}")
        if any(k >= t for k in keys):
            raise RuntimeError(f"TARGET_LEAKAGE_FAIL {variant} {t}")

        p, n, diag = anfis.select(samples, t, "CHHHO")
        o = base.month_shift(t, -1)
        forecast = float(bundle.core_gold[o] * math.exp(float(p[0])))
        actual = float(bundle.core_gold[t])
        if not np.isfinite(forecast):
            raise RuntimeError(f"NONFINITE_FORECAST {variant} {t}")

        rows.append({
            "target": t,
            "origin": o,
            "variant": variant,
            "input_dimension": cfg["inputs"],
            "population": cfg["population"],
            "train_rows": n,
            "diag": diag,
            "pred_log_return_gold": float(p[0]),
            "forecast": forecast,
            "actual": actual,
            "rw": float(bundle.core_gold[o]),
            "abs_error": abs(forecast - actual),
            "signed_error": forecast - actual,
        })

    metrics = eb.active_metrics(rows)
    return cfg, rows, metrics


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--external-v2")
    ap.add_argument("--b2-audit", required=True)
    ap.add_argument("--variant", choices=sorted(VARIANTS), required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    bundle, smeta = snap.load_snapshot(args.snapshot)
    b2doc = json.loads(Path(args.b2_audit).read_text())
    if not b2doc.get("gates", {}).get("pass"):
        raise RuntimeError("B2_AUTHORITY_NOT_PASS")

    ext = None
    if args.variant == "ALL6":
        if not args.external_v2:
            raise RuntimeError("ALL6_REQUIRES_EXTERNAL_V2")
        ext = json.loads(Path(args.external_v2).read_text())
        if (
            ext.get("payload_sha256")
            != b2doc.get("authority", {}).get("external_v2_payload_sha256")
        ):
            raise RuntimeError("EXTERNAL_V2_PAYLOAD_MISMATCH")

    cfg, rows, metrics = evaluate(bundle, args.variant, ext)

    out = {
        "schema": "GOLD_MONTHLY_F4_ALL6_COMPACT_CANDIDATE_V1_2026-09-29",
        "variant": args.variant,
        "authority": {
            "dev": "2022-04..2024-12",
            "selection_period": "2022-04..2024-12",
            "random_split": "NONE",
            "2025_used": False,
            "2026_used": False,
            "target_month_in_training": False,
            "lag_architecture": "L1_ONLY",
            "internal_contract": "CURRENT8_MR1_PLUS_GPR_VW",
            "external_contract": (
                "NONE"
                if args.variant == "BASE"
                else "14_F4_DAILY_EXTERNAL_MR_VW_ANALOGUES"
            ),
            "downstream_pipeline": "SHARED_CHRONOLOGICAL_SCALING_ANFIS_LOCAL_REFIT",
            "snapshot_payload_sha256": smeta["payload_sha256"],
            "external_v2_payload_sha256": (
                None if ext is None else ext["payload_sha256"]
            ),
            "b2_gate_schema": b2doc.get("schema"),
            "neon_reads": 0,
        },
        "optimizer": cfg,
        "feature_names": (
            list(base.FEATURES)
            if args.variant == "BASE"
            else list(base.FEATURES) + list(b1.FEATURES)
        ),
        "dev": {
            "metrics": metrics,
            "yearly": eb.yearly(rows),
            "rows": rows,
        },
    }

    if args.variant == "BASE":
        parity = {
            "reference_sum_abs_error": BASE_SIGMAAE,
            "observed_sum_abs_error": float(metrics["sum_abs_error"]),
            "abs_diff": abs(float(metrics["sum_abs_error"]) - BASE_SIGMAAE),
            "reference_direction_correct": BASE_DIRECTION,
            "observed_direction_correct": int(metrics["direction_correct"]),
        }
        parity["pass"] = (
            parity["abs_diff"] < 1e-4
            and parity["observed_direction_correct"] == BASE_DIRECTION
        )
        out["baseline_parity"] = parity
        if not parity["pass"]:
            raise RuntimeError(f"ALL6_BASE_PARITY_FAIL {parity}")

    Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print("F4_ALL6_CANDIDATE_GATE=PASS")
    print(json.dumps({
        "variant": args.variant,
        "sum_abs_error": metrics["sum_abs_error"],
        "direction_correct": metrics["direction_correct"],
        "mae": metrics["mae"],
        "rmse": metrics["rmse"],
        "optimizer": cfg,
        "baseline_parity": out.get("baseline_parity"),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
