from __future__ import annotations

import argparse
import inspect
import json
import math
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import vw_midas_anfis_meta_screen_v6 as av6
import vw_midas_elmfis_baseline_v1 as eb
import gold_monthly_f4_b1_transform_parity_v1 as b1

DEV_START, DEV_END = "2022-04", "2024-12"
BASE_SIGMAAE = 1413.0297794085
BASE_DIRECTION = 23
BASE_INPUTS = 8
ALL6_INPUTS = 22
RULES = 5
BASE_POP = 24
GENS = 45
REPEATS = 3
EXPECTED_B1_EXTERNAL_SHA = "fb779f1f1a3f5689f9f631aadc7e6e6e0c8cf5e50ec7730a233b80e8789438bc"


def population_for_inputs(k: int) -> int:
    d = 2 * RULES * k
    return int(math.ceil(BASE_POP * d / (2 * RULES * BASE_INPUTS)))


def configure(k: int, pop: int) -> dict:
    c = anfis.common
    if c.RULES != RULES:
        raise RuntimeError(f"RULE_COUNT_CHANGED {c.RULES}")

    n_ant = RULES * k
    param_dim = 2 * n_ant
    expected_pop = population_for_inputs(k)
    if pop != expected_pop:
        raise RuntimeError(f"POP_DENSITY_MISMATCH k={k} observed={pop} expected={expected_pop}")

    c.INPUTS = k
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
    c.POP_SIZE = pop

    anfis.POP = pop
    anfis.D = param_dim
    anfis.LO = c.LOWER
    anfis.HI = c.UPPER

    return {
        "inputs": k,
        "rules": RULES,
        "antecedent_parameter_dimension": param_dim,
        "population": pop,
        "generations": anfis.GENS,
        "repeats": anfis.REPEATS,
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
            raise RuntimeError(f"BAD_EXTERNAL_VECTOR {outer_target} {t} {extx.shape}")
        xi = np.concatenate([np.asarray(x, float), extx])
        if xi.shape != (ALL6_INPUTS,):
            raise RuntimeError(f"BAD_ALL6_VECTOR {outer_target} {t} {xi.shape}")
        out[t] = (xi, np.asarray(y, float))
    return out


def pipeline_source_contract():
    src_select = inspect.getsource(anfis.select).replace(" ", "")
    src_raw = inspect.getsource(av6.raw_arrays).replace(" ", "")

    required_select = [
        "Xtrr,Ytrr=Xr[:split],Yr[:split]",
        "xm,xs,ym,ys=av6.scale_fit(Xtrr,Ytrr)",
        "X=(Xtrr-xm)/xs",
        "Xv=(Xr[split:]-xm)/xs",
        "xfm,xfs,yfm,yfs=av6.scale_fit(Xr,Yr)",
        "(txr-xfm)/xfs",
        "av6.local_refit(theta,Xf,Yf,epochs)",
    ]
    required_raw = [
        "keys=sorted(kforkinsamplesifk<target)",
        "tx=samples[target][0][None,:]",
    ]
    checks = {
        f"select::{token}": token in src_select for token in required_select
    }
    checks.update({
        f"raw_arrays::{token}": token in src_raw for token in required_raw
    })
    return checks


def audit_processing(bundle, ext):
    series = build_series(ext)
    source_checks = pipeline_source_contract()
    if not all(source_checks.values()):
        raise RuntimeError(f"PIPELINE_SOURCE_CONTRACT_CHANGED {source_checks}")

    per_origin = []
    for outer in base.month_range(DEV_START, DEV_END):
        samples = all6_samples(bundle, outer, series)
        keys, Xr, Yr, txr, split = av6.raw_arrays(samples, outer)
        if Xr.ndim != 2 or Xr.shape[1] != ALL6_INPUTS or txr.shape != (1, ALL6_INPUTS):
            raise RuntimeError(f"ALL6_MATRIX_DIM_FAIL {outer} X={Xr.shape} tx={txr.shape}")
        if keys[0] != "2010-03":
            raise RuntimeError(f"HISTORY_SHORTENED {outer} first={keys[0]}")
        if not all(k < outer for k in keys):
            raise RuntimeError(f"TARGET_OR_FUTURE_IN_TRAIN {outer}")
        Xtrr, Ytrr = Xr[:split], Yr[:split]
        xm, xs, ym, ys = av6.scale_fit(Xtrr, Ytrr)
        if xm.shape != (ALL6_INPUTS,) or xs.shape != (ALL6_INPUTS,):
            raise RuntimeError(f"SCALER_DIM_FAIL {outer} {xm.shape} {xs.shape}")
        if not (np.all(np.isfinite(xm)) and np.all(np.isfinite(xs)) and np.all(xs > 0)):
            raise RuntimeError(f"BAD_SCALER {outer}")

        Xtr = (Xtrr - xm) / xs
        Xv = (Xr[split:] - xm) / xs
        if not (np.all(np.isfinite(Xtr)) and np.all(np.isfinite(Xv))):
            raise RuntimeError(f"NONFINITE_STANDARDIZED {outer}")

        # The exact same vectorized scaler spans CURRENT8 columns 0:8 and
        # external columns 8:22. No family-specific scaler is permitted.
        train_means = np.mean(Xtr, axis=0)
        if float(np.max(np.abs(train_means))) > 1e-10:
            raise RuntimeError(f"TRAIN_STANDARDIZATION_MEAN_FAIL {outer}")

        # Full refit scaler is fitted on pre-target Xr only; target vector is
        # transformed afterward with that same scaler.
        xfm, xfs, yfm, yfs = av6.scale_fit(Xr, Yr)
        tx_scaled = (txr - xfm) / xfs
        if tx_scaled.shape != (1, ALL6_INPUTS) or not np.all(np.isfinite(tx_scaled)):
            raise RuntimeError(f"TARGET_SCALE_FAIL {outer}")

        per_origin.append({
            "outer_target": outer,
            "train_n": int(split),
            "validation_n": int(len(Xr) - split),
            "input_columns": int(Xr.shape[1]),
            "first_training_sample": keys[0],
            "last_pre_target_sample": keys[-1],
            "max_abs_scaled_train_mean": float(np.max(np.abs(train_means))),
            "current8_scaler_columns": 8,
            "external_scaler_columns": 14,
        })

    return {
        "source_contract_checks": source_checks,
        "origins_checked": len(per_origin),
        "all6_input_columns": ALL6_INPUTS,
        "same_vectorized_scaler_for_current8_and_external": True,
        "inner_scaler_fit_on_training_prefix_only": True,
        "validation_uses_inner_train_scaler": True,
        "full_refit_scaler_fit_on_pre_target_history_only": True,
        "target_uses_full_history_scaler_without_entering_fit": True,
        "same_anfis_select_and_local_refit_path": True,
        "history_not_shortened": all(r["first_training_sample"] == "2010-03" for r in per_origin),
        "per_origin": per_origin,
    }


def audit_optimizer_shape(bundle, ext):
    cfg = configure(ALL6_INPUTS, population_for_inputs(ALL6_INPUTS))
    series = build_series(ext)
    samples = all6_samples(bundle, DEV_END, series)
    keys, Xr, Yr, txr, split = av6.raw_arrays(samples, DEV_END)
    Xtrr, Ytrr = Xr[:split], Yr[:split]
    xm, xs, ym, ys = av6.scale_fit(Xtrr, Ytrr)
    X = (Xtrr - xm) / xs
    anchor = anfis.common.initial_theta(X)
    if anchor.shape != (220,):
        raise RuntimeError(f"ANCHOR_DIM_FAIL {anchor.shape}")
    pop = anfis.init_chaotic(anchor, 771100)
    if pop.shape != (66, 220):
        raise RuntimeError(f"POP_SHAPE_FAIL {pop.shape}")
    c, s = anfis.common.decode(anchor)
    if c.shape != (RULES, ALL6_INPUTS) or s.shape != (RULES, ALL6_INPUTS):
        raise RuntimeError(f"DECODE_SHAPE_FAIL centers={c.shape} spreads={s.shape}")

    density_base = BASE_POP / (2 * RULES * BASE_INPUTS)
    density_all6 = cfg["population"] / cfg["antecedent_parameter_dimension"]
    return {
        **cfg,
        "expected_population_formula": "ceil(24 * (10*k) / 80)",
        "population_shape": list(pop.shape),
        "anchor_shape": list(anchor.shape),
        "decoded_centers_shape": list(c.shape),
        "decoded_spreads_shape": list(s.shape),
        "base_population_per_parameter": density_base,
        "all6_population_per_parameter": density_all6,
        "density_not_below_base": density_all6 + 1e-15 >= density_base,
    }


def evaluate_base(bundle):
    cfg = configure(BASE_INPUTS, BASE_POP)
    if cfg["generations"] != GENS or cfg["repeats"] != REPEATS:
        raise RuntimeError(f"OPTIMIZER_SCHEDULE_CHANGED {cfg}")
    rows = []
    for t in base.month_range(DEV_START, DEV_END):
        samples = base.all_samples_at_origin(bundle, t, governed=True)
        p, n, diag = anfis.select(samples, t, "CHHHO")
        o = base.month_shift(t, -1)
        rows.append({
            "target": t,
            "origin": o,
            "train_rows": n,
            "diag": diag,
            "pred_log_return_gold": float(p[0]),
            "forecast": float(bundle.core_gold[o] * math.exp(float(p[0]))),
            "actual": float(bundle.core_gold[t]),
            "rw": float(bundle.core_gold[o]),
        })
    metrics = eb.active_metrics(rows)
    diff = abs(float(metrics["sum_abs_error"]) - BASE_SIGMAAE)
    passed = diff < 1e-4 and int(metrics["direction_correct"]) == BASE_DIRECTION
    return {
        "config": cfg,
        "reference_sum_abs_error": BASE_SIGMAAE,
        "observed_sum_abs_error": float(metrics["sum_abs_error"]),
        "abs_diff": diff,
        "reference_direction_correct": BASE_DIRECTION,
        "observed_direction_correct": int(metrics["direction_correct"]),
        "pass": passed,
        "metrics": metrics,
        "rows": rows,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--external-v2", required=True)
    ap.add_argument("--b1-audit", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    bundle, snapshot_meta = snap.load_snapshot(args.snapshot)
    ext = json.loads(Path(args.external_v2).read_text())
    b1doc = json.loads(Path(args.b1_audit).read_text())

    b1_revalidation = {
        "schema": b1doc.get("schema"),
        "gate_pass": bool(b1doc.get("gates", {}).get("pass")),
        "external_v2_payload_matches": (
            b1doc.get("authority", {}).get("external_v2_payload_sha256")
            == ext.get("payload_sha256")
            == EXPECTED_B1_EXTERNAL_SHA
        ),
        "snapshot_payload_matches": (
            b1doc.get("authority", {}).get("snapshot_payload_sha256")
            == snapshot_meta.get("payload_sha256")
        ),
        "rows_checked": b1doc.get("rows_checked"),
        "vw_formula_max_abs_diff": b1doc.get("max_gold_vw_formula_abs_diff"),
    }
    b1_revalidation["pass"] = (
        b1_revalidation["gate_pass"]
        and b1_revalidation["external_v2_payload_matches"]
        and b1_revalidation["snapshot_payload_matches"]
    )
    if not b1_revalidation["pass"]:
        raise RuntimeError(f"B1_REVALIDATION_FAIL {b1_revalidation}")

    processing = audit_processing(bundle, ext)
    b2a_pass = (
        processing["origins_checked"] == 33
        and processing["all6_input_columns"] == 22
        and processing["same_vectorized_scaler_for_current8_and_external"]
        and processing["inner_scaler_fit_on_training_prefix_only"]
        and processing["validation_uses_inner_train_scaler"]
        and processing["full_refit_scaler_fit_on_pre_target_history_only"]
        and processing["target_uses_full_history_scaler_without_entering_fit"]
        and processing["same_anfis_select_and_local_refit_path"]
        and processing["history_not_shortened"]
        and all(processing["source_contract_checks"].values())
    )
    if not b2a_pass:
        raise RuntimeError("B2A_PROCESSING_PARITY_FAIL")

    base_parity = evaluate_base(bundle)
    if not base_parity["pass"]:
        raise RuntimeError(f"B2B_BASE_PARITY_FAIL {base_parity}")

    optimizer = audit_optimizer_shape(bundle, ext)
    b2b_pass = (
        optimizer["inputs"] == 22
        and optimizer["rules"] == 5
        and optimizer["antecedent_parameter_dimension"] == 220
        and optimizer["population"] == 66
        and optimizer["generations"] == 45
        and optimizer["repeats"] == 3
        and optimizer["population_shape"] == [66, 220]
        and optimizer["density_not_below_base"]
        and base_parity["pass"]
    )
    if not b2b_pass:
        raise RuntimeError(f"B2B_OPTIMIZER_PARITY_FAIL {optimizer}")

    out = {
        "schema": "GOLD_MONTHLY_F4_B2_PROCESSING_OPTIMIZER_PARITY_V1_2026-09-29",
        "authority": {
            "dev": "2022-04..2024-12",
            "random_split": "NONE",
            "2025_used": False,
            "2026_used": False,
            "all6_model_scored": False,
            "neon_reads": 0,
            "snapshot_payload_sha256": snapshot_meta["payload_sha256"],
            "external_v2_payload_sha256": ext["payload_sha256"],
            "b1_audit_schema": b1doc.get("schema"),
        },
        "b1_revalidation": b1_revalidation,
        "b2a_processing_parity": {
            "pass": b2a_pass,
            **processing,
        },
        "b2b_optimizer_parity": {
            "pass": b2b_pass,
            "base_parity": base_parity,
            "all6_optimizer": optimizer,
        },
        "gates": {
            "b1_revalidated": b1_revalidation["pass"],
            "b2a_processing_parity": b2a_pass,
            "b2b_optimizer_and_base_parity": b2b_pass,
            "pass": b1_revalidation["pass"] and b2a_pass and b2b_pass,
        },
    }

    Path(args.output).write_text(
        json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n"
    )
    print("F4_B2_PROCESSING_OPTIMIZER_PARITY_GATE=PASS")
    print(json.dumps({
        "gates": out["gates"],
        "base_sum_abs_error": base_parity["observed_sum_abs_error"],
        "base_direction_correct": base_parity["observed_direction_correct"],
        "all6_dimension": optimizer["antecedent_parameter_dimension"],
        "all6_population": optimizer["population"],
        "generations": optimizer["generations"],
        "repeats": optimizer["repeats"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
