from __future__ import annotations
"""
Pre-registered isolated GPR weighting ablation for ChHHO-ANFIS.
Same four metals, 8 features, canonical targets, training origins, optimizer,
seed formula, inner chronology, and output anchor in all arms.
No Neon/database reads; immutable 2022-2024 DEV snapshot only.
Does not change/publish a new primary model.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_elmfis_baseline_v1 as eb

START, END = "2022-04", "2024-12"
ARMS = ("GPR_PIT_CURRENT8", "NO_GPR_EQUAL", "NO_GPR_FIXED_RECENCY")
FIXED_LAMBDA = 0.05  # pre-registered, exponential recency; not tuned on DEV
REFERENCE_AE = 1413.0297794085
REFERENCE_DIR = 23
METALS = base.METALS


def daily_feature(bundle, metal: str, origin: str, arm: str, z: float | None) -> float:
    v = bundle.daily_month_values[metal].get(origin)
    if v is None or len(v) < 5:
        raise RuntimeError(f"INSUFFICIENT_DAILY_ROWS {metal} {origin}")
    values = np.asarray(v, float)
    if np.any(~np.isfinite(values)) or np.any(values <= 0):
        raise RuntimeError(f"BAD_METAL_PRICE {metal} {origin}")
    dr = np.diff(np.log(values))
    if arm == "GPR_PIT_CURRENT8":
        if z is None:
            raise RuntimeError("PIT_GPR_REQUIRED")
        return base.weighted_daily_return(bundle, metal, origin, z)
    if arm == "NO_GPR_EQUAL":
        return float(np.mean(dr))
    if arm == "NO_GPR_FIXED_RECENCY":
        age = np.arange(len(dr) - 1, -1, -1, dtype=float)
        w = np.exp(-FIXED_LAMBDA * age)
        w /= w.sum()
        return float(w @ dr)
    raise ValueError(arm)


def make_sample(bundle, target: str, arm: str, gpr_history: dict) -> tuple[np.ndarray, np.ndarray]:
    p, pp = base.month_shift(target, -1), base.month_shift(target, -2)
    z = base.gpr_norm(gpr_history, pp) if arm == "GPR_PIT_CURRENT8" else None
    x, y = [], []
    for metal in METALS:
        M = bundle.monthly_metal[metal]
        if target not in M or p not in M or pp not in M:
            raise RuntimeError(f"MONTHLY_METAL_MISSING {metal} {target}")
        x.extend([math.log(M[p] / M[pp]), daily_feature(bundle, metal, p, arm, z)])
        y.append(math.log(M[target] / M[p]))
    return np.asarray(x, float), np.asarray(y, float)


def samples_for_outer_origin(bundle, target: str, arm: str) -> dict:
    """Completed historical (X,Y), future outer target (X,None).

    The GPR control retains bit-for-bit comparison with the canonical
    label-free target source; no future target-month price is necessary.
    """
    origin = base.month_shift(target, -1)
    history = bundle.gpr_vintages[origin] if arm == "GPR_PIT_CURRENT8" else {}
    result = {}
    for t in base.month_range("2010-03", origin):
        try:
            result[t] = make_sample(bundle, t, arm, history)
        except RuntimeError:
            continue
    if arm == "GPR_PIT_CURRENT8":
        target_x = base.feature_for_target(bundle, target, history, True)
    else:
        p, pp = base.month_shift(target, -1), base.month_shift(target, -2)
        if any(p not in bundle.monthly_metal[m] or pp not in bundle.monthly_metal[m] for m in METALS):
            raise RuntimeError(f"OUTER_TARGET_ORIGIN_FEATURE_MISSING {target}")
        target_x = np.asarray([
            z for metal in METALS for z in (
                math.log(bundle.monthly_metal[metal][p] / bundle.monthly_metal[metal][pp]),
                daily_feature(bundle, metal, p, arm, None))
        ], float)
    result[target] = (target_x, None)
    if arm == "GPR_PIT_CURRENT8":
        canonical = base.all_samples_at_origin(bundle, target, governed=True)
        if set(result) != set(canonical):
            raise RuntimeError("CANONICAL_SAMPLE_SET_DIFFERENCE")
        if any(not np.array_equal(result[k][0], canonical[k][0]) or
               not np.array_equal(result[k][1], canonical[k][1]) for k in canonical):
            raise RuntimeError("CANONICAL_FEATURE_PARITY_FAIL")
    return result


def evaluate(bundle, arm: str) -> list[dict]:
    rows = []
    for target in base.month_range(START, END):
        samples = samples_for_outer_origin(bundle, target, arm)
        pred, training_rows, diag = anfis.select(samples, target, "CHHHO")
        origin = base.month_shift(target, -1)
        if target in samples and target in [k for k in samples if k < target]:
            raise RuntimeError("TARGET_LEAKAGE")
        rows.append({
            "target": target, "origin": origin, "arm": arm,
            "train_rows": training_rows, "diag": diag,
            "pred_log_return_gold": float(pred[0]),
            "forecast": float(bundle.core_gold[origin] * math.exp(float(pred[0]))),
            "actual": float(bundle.core_gold[target]),
            "rw": float(bundle.core_gold[origin]),
        })
        print(f"DEV_PROGRESS {arm} {target} {len(rows)}/33", flush=True)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--arm", choices=ARMS, required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    bundle, snapshot_meta = snap.load_snapshot(args.snapshot)
    rows = evaluate(bundle, args.arm)
    metrics = eb.active_metrics(rows)
    assert len(rows) == 33
    assert len({r["target"] for r in rows}) == 33
    assert rows[0]["target"] == START and rows[-1]["target"] == END
    assert all(r["origin"] == base.month_shift(r["target"], -1) for r in rows)
    assert all(0 < r["rw"] and 0 < r["actual"] and 0 < r["forecast"] for r in rows)

    out = {
        "schema": "GOLD_MONTHLY_CHHHO_GPR_WEIGHT_ABLATION_V1",
        "arm": args.arm,
        "experimental_status": "DEV_ONLY_NEITHER_MODEL_SELECTION_NOR_AUTOMATIC_PROMOTION",
        "features": ["Gold_MR", "Gold_VW", "Silver_MR", "Silver_VW",
                     "Platinum_MR", "Platinum_VW", "Palladium_MR", "Palladium_VW"],
        "daily_feature": {
            "GPR_PIT_CURRENT8": "canonical PIT GPR(z[p-1])-controlled exp[-0.1exp(-10z)*age]",
            "NO_GPR_EQUAL": "mean(daily_log_returns_in_completed_origin_month)",
            "NO_GPR_FIXED_RECENCY": "exp(-0.05*age)/sum(exp(-0.05*age)), no GPR",
        }[args.arm],
        "fixed_recency_lambda": FIXED_LAMBDA,
        "data_authority": {
            "snapshot_payload_sha256": snapshot_meta["payload_sha256"],
            "dev": "2022-04..2024-12", "n": 33,
            "pit_gpr_origin_vintages": 33,
            "model": "CHHHO_ANFIS_UNCHANGED",
            "feature_dimension": 8, "metal_universe": METALS,
            "random_split": False, "target_leakage": False,
            "optimizer_changed": False, "inner_validation_changed": False,
            "2025_used_for_selection": False, "2026_used_for_selection": False,
            "NEON_DATABASE_URL": "DISABLED", "db_reads": 0,
        },
        "dev": {"metrics": metrics, "yearly": eb.yearly(rows), "rows": rows},
    }
    if args.arm == "GPR_PIT_CURRENT8":
        mae = float(metrics["sum_abs_error"])
        hit = int(metrics["direction_correct"])
        out["canonical_parity"] = {
            "observed_error": mae, "reference_error": REFERENCE_AE,
            "observed_direction": hit, "reference_direction": REFERENCE_DIR,
            "pass": abs(mae - REFERENCE_AE) < 1e-4 and hit == REFERENCE_DIR,
        }
        if not out["canonical_parity"]["pass"]:
            raise RuntimeError(f"CANONICAL_GPR_BASELINE_PARITY_FAIL {out['canonical_parity']}")
    Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print("GPR_WEIGHT_ABLATION_GATE=PASS")
    print(json.dumps({
        "arm": args.arm, "sum_abs_error": metrics["sum_abs_error"],
        "direction_correct": metrics["direction_correct"],
        "n": len(rows),
        "canonical_parity": out.get("canonical_parity"),
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
