from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    matthews_corrcoef,
)

from gold_axis_2026.v149_thesis.run_rich_short_horizon import (
    B0,
    BLOCKS,
    CONFIGS,
    load_panel,
    raw_paths,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v162_research/contracts/v162_context_aware_meta_forecast_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v162_research"

EXPERTS = [c[0] for c in CONFIGS]
BASE_COLS = B0 + BLOCKS["B6"]
STATE_NUMERIC = ["gold_mom5", "gold_mom20", "gold_rv20"]
STATE_ENCODED = [
    "monthly_direction_3m_encoded",
    "fast_state_encoded",
    "slow_state_encoded",
    "emergency_level_encoded",
    "emergency_reversal_encoded",
    "legacy_state_available",
]
STATE_COLS = STATE_NUMERIC + STATE_ENCODED

ENCODING = {
    "monthly_direction_3m": {"UP": 1.0, "DOWN": -1.0, "NEUTRAL": 0.0},
    "fast_state": {"ROBUST_UP": 1.0, "ROBUST_DOWN": -1.0, "MIXED": 0.0, "NOT_YET_ROBUST": 0.0},
    "slow_state": {"ROBUST_UP": 1.0, "ROBUST_DOWN": -1.0, "MIXED": 0.0, "NOT_YET_ROBUST": 0.0},
    "emergency_level": {"UP": 1.0, "DOWN": -1.0, "NEUTRAL": 0.0},
    "emergency_reversal": {"OFF": 0.0, "ON": 1.0},
}


def prepare_state(d: pd.DataFrame) -> pd.DataFrame:
    z = d.copy()
    available_cols = [c for c in ENCODING if c in z.columns]
    if available_cols:
        z["legacy_state_available"] = z[available_cols].notna().any(axis=1).astype(float)
    else:
        z["legacy_state_available"] = 0.0
    for col, mapping in ENCODING.items():
        if col in z.columns:
            z[f"{col}_encoded"] = z[col].map(mapping).fillna(0.0).astype(float)
        else:
            z[f"{col}_encoded"] = 0.0
    return z


def _matured_indices(paths: dict[str, dict[int, float]], y: pd.Series, t: int, h: int) -> list[int]:
    common = set.intersection(*(set(paths[e]) for e in EXPERTS))
    return sorted(j for j in common if j < t and j + h <= t and pd.notna(y.iloc[j]))


def _expert_matrix(paths: dict[str, dict[int, float]], idx: list[int]) -> np.ndarray:
    return np.asarray([[paths[e][j] for e in EXPERTS] for j in idx], dtype=float)


def _softmax_losses(loss: np.ndarray, eta: float) -> np.ndarray:
    a = -eta * np.asarray(loss, dtype=float)
    a -= np.max(a)
    w = np.exp(a)
    return w / w.sum()


def _entropy_confidence(w: np.ndarray) -> float:
    w = np.asarray(w, dtype=float)
    h = -np.sum(np.where(w > 0, w * np.log(w), 0.0))
    return float(1.0 - h / math.log(len(w)))


def _weighted_effective_n(w: np.ndarray) -> float:
    s = float(np.sum(w))
    q = float(np.sum(np.square(w)))
    return 0.0 if q <= 0 else s * s / q


def recent_weights(paths, y, idx, t, half_life=60.0, eta=12.0):
    p = _expert_matrix(paths, idx)
    yy = y.iloc[idx].to_numpy(dtype=float)[:, None]
    age = np.asarray([t - j for j in idx], dtype=float)
    rw = np.power(0.5, age / half_life)
    losses = np.sum(rw[:, None] * np.square(p - yy), axis=0) / np.sum(rw)
    return _softmax_losses(losses, eta), losses


def local_weights(d, paths, y, idx, t, half_life=120.0, eta=12.0, penalty_lambda=0.0):
    hist = d.loc[idx, STATE_COLS].astype(float).copy()
    cur = d.loc[[t], STATE_COLS].astype(float).copy()

    # All scaling/filling is prior-only. Legacy states have explicit availability indicator.
    med = hist.median(axis=0, skipna=True).fillna(0.0)
    hist = hist.fillna(med)
    cur = cur.fillna(med)
    mean = hist.mean(axis=0)
    sd = hist.std(axis=0, ddof=0).replace(0.0, 1.0).fillna(1.0)
    hs = (hist - mean) / sd
    cs = (cur - mean) / sd
    dist = np.sqrt(np.square(hs.to_numpy() - cs.to_numpy()[0]).sum(axis=1))
    positive = dist[dist > 0]
    bandwidth = float(np.median(positive)) if len(positive) else 1.0
    if not np.isfinite(bandwidth) or bandwidth <= 0:
        bandwidth = 1.0
    kernel = np.exp(-0.5 * np.square(dist / bandwidth))
    age = np.asarray([t - j for j in idx], dtype=float)
    recency = np.power(0.5, age / half_life)
    sw = kernel * recency
    eff_n = _weighted_effective_n(sw)
    if sw.sum() <= 0:
        return np.repeat(1 / len(EXPERTS), len(EXPERTS)), np.repeat(np.nan, len(EXPERTS)), eff_n, bandwidth

    p = _expert_matrix(paths, idx)
    yy = y.iloc[idx].to_numpy(dtype=float)[:, None]
    loss = np.sum(sw[:, None] * np.square(p - yy), axis=0) / sw.sum()

    if penalty_lambda > 0:
        predicted_up = (p >= 0.5).astype(float)
        frac_up = np.sum(sw[:, None] * predicted_up, axis=0) / sw.sum()
        degeneracy = np.abs(2.0 * frac_up - 1.0)
        score = loss + penalty_lambda * degeneracy
    else:
        score = loss
    return _softmax_losses(score, eta), score, eff_n, bandwidth


def build_meta_predictions(d: pd.DataFrame, h: int) -> pd.DataFrame:
    paths, y, ret = raw_paths(d, h, BASE_COLS)
    rows = []
    for t in range(len(d) - h):
        if not all(t in paths[e] for e in EXPERTS):
            continue
        idx = _matured_indices(paths, y, t, h)
        if len(idx) < 60:
            continue

        current = np.asarray([paths[e][t] for e in EXPERTS], dtype=float)
        hist_p = _expert_matrix(paths, idx)
        hist_y = y.iloc[idx].to_numpy(dtype=float)[:, None]
        cum_loss = np.mean(np.square(hist_p - hist_y), axis=0)
        best = int(np.argmin(cum_loss))
        freq = float((y.iloc[idx].sum() + 0.5) / (len(idx) + 1.0))

        rw, _ = recent_weights(paths, y, idx, t)
        lw, _, local_neff, bandwidth = local_weights(d, paths, y, idx, t)
        cw, _, cra_neff, _ = local_weights(d, paths, y, idx, t, penalty_lambda=0.05)

        p_equal = float(current.mean())
        p_recent = float(np.dot(rw, current))
        p_local = float(np.dot(lw, current))
        p_crase_raw = float(np.dot(cw, current))
        weight_conf = _entropy_confidence(cw)
        crase_signal = bool(cra_neff >= 25 and weight_conf >= 0.10 and abs(p_crase_raw - 0.5) >= 0.03)

        row = {
            "origin_index": t,
            "origin_date": d.date.iloc[t],
            "target_date": d.date.iloc[t + h],
            "horizon": h,
            "y": int(y.iloc[t]),
            "return": float(ret.iloc[t]),
            "P50": 0.5,
            "FREQ": freq,
            "BEST_SINGLE_PRIOR": float(current[best]),
            "BEST_SINGLE_ID": EXPERTS[best],
            "EQUAL_MEAN": p_equal,
            "RECENT_EXP": p_recent,
            "LOCAL_SOFT": p_local,
            "CRASE_V0_RAW": p_crase_raw,
            "CRASE_V0": p_crase_raw if crase_signal else np.nan,
            "CRASE_SIGNAL": int(crase_signal),
            "CRASE_WEIGHT_CONFIDENCE": weight_conf,
            "CRASE_LOCAL_EFFECTIVE_N": cra_neff,
            "LOCAL_EFFECTIVE_N": local_neff,
            "LOCAL_BANDWIDTH": bandwidth,
            "MATURED_META_N": len(idx),
        }
        for i, e in enumerate(EXPERTS):
            row[f"P_{e}"] = float(current[i])
            row[f"W_RECENT_{e}"] = float(rw[i])
            row[f"W_LOCAL_{e}"] = float(lw[i])
            row[f"W_CRASE_{e}"] = float(cw[i])
        rows.append(row)
    return pd.DataFrame(rows)


def metric_block(f: pd.DataFrame, col: str) -> dict:
    z = f[["y", col]].dropna()
    if z.empty:
        return {"n": 0, "status": "NO_SIGNAL"}
    y = z.y.to_numpy(dtype=int)
    p = z[col].to_numpy(dtype=float)
    pred = (p >= 0.5).astype(int)
    both_actual = len(np.unique(y)) == 2
    both_pred = len(np.unique(pred)) == 2
    return {
        "n": int(len(z)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, np.clip(p, 1e-9, 1 - 1e-9), labels=[0, 1])),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if both_actual else None,
        "mcc": float(matthews_corrcoef(y, pred)) if both_actual and both_pred else 0.0,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
    }


def summarize(f: pd.DataFrame) -> dict:
    methods = ["P50", "FREQ", "BEST_SINGLE_PRIOR", "EQUAL_MEAN", "RECENT_EXP", "LOCAL_SOFT", "CRASE_V0"]
    out = {}
    periods = {
        "ALL_AVAILABLE": pd.Series(True, index=f.index),
        "2025": pd.to_datetime(f.origin_date).dt.year.eq(2025),
        "2026": pd.to_datetime(f.origin_date).dt.year.eq(2026),
    }
    for period, mask in periods.items():
        g = f.loc[mask].copy()
        out[period] = {m: metric_block(g, m) for m in methods}
        denom = len(g)
        sig = int(g.CRASE_V0.notna().sum()) if denom else 0
        out[period]["CRASE_V0"]["coverage"] = float(sig / denom) if denom else 0.0
    return out


def main():
    freeze = json.loads(CONTRACT.read_text())
    assert freeze["status"] == "FROZEN_BEFORE_ANY_V162_SCORING"
    assert freeze["auto_selector"] == "OFF" and freeze["auto_ensemble"] == "OFF"
    OUT.mkdir(parents=True, exist_ok=True)

    with psycopg.connect(os.environ["NEON_DATABASE_URL"]) as conn:
        d = prepare_state(load_panel(conn))

    result = {
        "contract_id": freeze["contract_id"],
        "evidence_class": freeze["evidence_class"],
        "origin_rows": int(len(d)),
        "base_forecast_features": BASE_COLS,
        "state_features": STATE_COLS,
        "experts": EXPERTS,
        "horizons": {},
        "auto_selector": "OFF",
        "auto_ensemble": "OFF",
        "production_authority": False,
        "production_writes": "NONE",
    }

    for h in [1, 3]:
        f = build_meta_predictions(d, h)
        f.to_csv(OUT / f"v162_{h}d_meta_predictions.csv", index=False)
        result["horizons"][f"{h}D"] = {
            "prediction_rows": int(len(f)),
            "metrics": summarize(f),
        }

    (OUT / "v162_context_aware_meta_forecast_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
