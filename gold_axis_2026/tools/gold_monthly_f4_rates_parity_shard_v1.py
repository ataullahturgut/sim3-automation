from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

import gold_monthly_dev_snapshot_v1 as snap
import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as anfis
import gold_monthly_f4_b1_transform_parity_v1 as b1
import gold_monthly_f4_all6_compact_candidate_v1 as all6core

RATE_FEATURES = [
    "NOM10_MR_ANALOG",
    "NOM10_VW_ANALOG",
    "REAL10_MR_ANALOG",
    "REAL10_VW_ANALOG",
]
TOTAL_INPUTS = 12
POPULATION = 36
DEV_START, DEV_END = "2022-04", "2024-12"


def build_rate_series(ext: dict):
    return {
        "NOM10": b1.nested_daily(ext, "h15_daily", "DGS10"),
        "REAL10": b1.nested_daily(ext, "h15_daily", "DFII10"),
    }


def rate_features_for_sample(series: dict, p: str, z: float):
    pp = b1.mshift(p, -1)
    out = {}
    obs = {}
    for name in ("NOM10", "REAL10"):
        s = series[name]
        lag = b1.LAGS[name]
        mr, np_, nq = b1.mean_difference(s, p, pp, lag)
        vp, last, _ = b1.eligible_month_values(s, p, lag)
        out[f"{name}_MR_ANALOG"] = mr
        out[f"{name}_VW_ANALOG"] = b1.generic_weighted_increment(vp, z, log_mode=False)
        obs[name] = {"p_n": np_, "pp_n": nq, "p_last": last}
    return out, obs


def rates_samples(bundle, outer_target: str, series: dict):
    origin = b1.mshift(outer_target, -1)
    history = bundle.gpr_vintages[origin]
    raw = base.all_samples_at_origin(bundle, outer_target, governed=True)
    out = {}

    for t, (x, y) in raw.items():
        p = b1.mshift(t, -1)
        pp = b1.mshift(t, -2)
        z = base.gpr_norm(history, pp)
        feat, _ = rate_features_for_sample(series, p, z)
        extx = np.asarray([feat[k] for k in RATE_FEATURES], float)
        if extx.shape != (4,) or not np.all(np.isfinite(extx)):
            raise RuntimeError(f"BAD_RATE_VECTOR outer={outer_target} t={t}")
        xx = np.concatenate([np.asarray(x, float), extx])
        if xx.shape != (TOTAL_INPUTS,) or not np.all(np.isfinite(xx)):
            raise RuntimeError(f"BAD_RATES_DESIGN outer={outer_target} t={t} shape={xx.shape}")
        out[t] = (xx, np.asarray(y, float))
    return out


def configure():
    cfg = all6core.configure(TOTAL_INPUTS, POPULATION)
    expected = {
        "inputs": 12,
        "rules": 5,
        "antecedent_parameter_dimension": 120,
        "population": 36,
        "generations": 45,
        "repeats": 3,
    }
    if cfg != expected:
        raise RuntimeError(f"RATES_OPTIMIZER_PARITY_FAIL observed={cfg} expected={expected}")
    return cfg


def run_rows(bundle, ext: dict, start: str, end: str):
    cfg = configure()
    series = build_rate_series(ext)
    rows = []

    for t in base.month_range(start, end):
        samples = rates_samples(bundle, t, series)
        keys = sorted(k for k in samples if k < t)
        if not keys or keys[0] != "2010-03":
            raise RuntimeError(f"HISTORY_PARITY_FAIL {t} first={keys[0] if keys else None}")
        if any(k >= t for k in keys):
            raise RuntimeError(f"TARGET_LEAKAGE_FAIL {t}")

        p, n, diag = anfis.select(samples, t, "CHHHO")
        o = base.month_shift(t, -1)
        forecast = float(bundle.core_gold[o] * math.exp(float(p[0])))
        actual = float(bundle.core_gold[t])
        if not np.isfinite(forecast):
            raise RuntimeError(f"NONFINITE_FORECAST {t}")

        rows.append({
            "target": t,
            "origin": o,
            "family": "RATES",
            "input_dimension": TOTAL_INPUTS,
            "population": POPULATION,
            "train_rows": n,
            "diag": diag,
            "pred_log_return_gold": float(p[0]),
            "forecast": forecast,
            "actual": actual,
            "rw": float(bundle.core_gold[o]),
            "abs_error": abs(forecast - actual),
            "signed_error": forecast - actual,
        })

    return cfg, rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--external-v2", required=True)
    ap.add_argument("--b2-audit", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--output", required=True)
    a = ap.parse_args()

    bundle, smeta = snap.load_snapshot(a.snapshot)
    ext = json.loads(Path(a.external_v2).read_text())
    b2doc = json.loads(Path(a.b2_audit).read_text())

    if not b2doc.get("gates", {}).get("pass"):
        raise RuntimeError("B2_AUTHORITY_NOT_PASS")
    if ext.get("payload_sha256") != b2doc.get("authority", {}).get("external_v2_payload_sha256"):
        raise RuntimeError("EXTERNAL_V2_PAYLOAD_MISMATCH")

    cfg, rows = run_rows(bundle, ext, a.start, a.end)

    out = {
        "schema": "GOLD_MONTHLY_F4_RATES_PARITY_SHARD_V1_2026-09-29",
        "label": a.label,
        "start": a.start,
        "end": a.end,
        "family": "RATES",
        "feature_names": RATE_FEATURES,
        "optimizer": cfg,
        "authority": {
            "selection_period": "2022-04..2024-12",
            "2025_used": False,
            "2026_used": False,
            "random_split": "NONE",
            "target_month_in_training": False,
            "release_lag_calendar_days": 2,
            "representation": "MONTHLY_MEAN_YIELD_DIFFERENCE_PLUS_GPR_WEIGHTED_DAILY_FIRST_DIFFERENCES",
            "downstream_pipeline": "SHARED_CHRONOLOGICAL_SCALING_ANFIS_LOCAL_REFIT",
            "snapshot_payload_sha256": smeta["payload_sha256"],
            "external_v2_payload_sha256": ext["payload_sha256"],
            "b2_gate_schema": b2doc.get("schema"),
            "parallelization_semantics": "OUTER_ORIGINS_INDEPENDENT__SEED_DEPENDS_ON_TARGET__NO_CROSS_ORIGIN_STATE",
            "neon_reads": 0,
        },
        "rows": rows,
    }
    Path(a.output).write_text(json.dumps(out, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("F4_RATES_SHARD_GATE=PASS")
    print(json.dumps({
        "label": a.label,
        "start": a.start,
        "end": a.end,
        "n": len(rows),
        "optimizer": cfg,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
