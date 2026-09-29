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

FEATURE_NAME = "REAL10_MONTHLY_MEAN_DIFF"
TOTAL_INPUTS = 9
POPULATION = 27


def configure():
    cfg = all6core.configure(TOTAL_INPUTS, POPULATION)
    expected = {
        "inputs": 9,
        "rules": 5,
        "antecedent_parameter_dimension": 90,
        "population": 27,
        "generations": 45,
        "repeats": 3,
    }
    if cfg != expected:
        raise RuntimeError(f"R1_OPTIMIZER_PARITY_FAIL observed={cfg} expected={expected}")
    return cfg


def real10_series(ext: dict):
    return b1.nested_daily(ext, "h15_daily", "DFII10")


def real10_monthly_feature(series: dict, p: str):
    pp = b1.mshift(p, -1)
    lag = b1.LAGS["REAL10"]
    mr, np_, nq = b1.mean_difference(series, p, pp, lag)
    return float(mr), {"p_n": int(np_), "pp_n": int(nq), "lag_calendar_days": int(lag)}


def samples_for_outer(bundle, outer_target: str, series: dict):
    raw = base.all_samples_at_origin(bundle, outer_target, governed=True)
    out = {}
    for t, (x, y) in raw.items():
        p = b1.mshift(t, -1)
        v, _ = real10_monthly_feature(series, p)
        xx = np.concatenate([np.asarray(x, float), np.asarray([v], float)])
        if xx.shape != (TOTAL_INPUTS,) or not np.all(np.isfinite(xx)):
            raise RuntimeError(f"BAD_R1_VECTOR outer={outer_target} t={t} shape={xx.shape}")
        out[t] = (xx, np.asarray(y, float))
    return out


def run_rows(bundle, ext: dict, start: str, end: str):
    cfg = configure()
    series = real10_series(ext)
    rows = []
    for t in base.month_range(start, end):
        samples = samples_for_outer(bundle, t, series)
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
            "variant": "RATES_R1_REAL10_MONTHLY_MEAN_DIFF",
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
        "schema": "GOLD_MONTHLY_F4_RATES_R1_REAL10_MONTHLY_MEAN_DIFF_SHARD_V1_2026-09-29",
        "label": a.label,
        "start": a.start,
        "end": a.end,
        "feature_name": FEATURE_NAME,
        "optimizer": cfg,
        "authority": {
            "selection_period": "2022-04..2024-12",
            "2025_used": False,
            "2026_used": False,
            "random_split": "NONE",
            "target_month_in_training": False,
            "release_lag_calendar_days": int(b1.LAGS["REAL10"]),
            "representation": "MEAN_REAL10[p]-MEAN_REAL10[p-1]",
            "daily_vw_used": False,
            "nominal_rate_used": False,
            "gpr_rate_weighting_used": False,
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
    print("F4_RATES_R1_SHARD_GATE=PASS")
    print(json.dumps({
        "label": a.label,
        "start": a.start,
        "end": a.end,
        "n": len(rows),
        "optimizer": cfg,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
