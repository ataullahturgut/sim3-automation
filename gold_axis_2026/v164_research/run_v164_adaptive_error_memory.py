from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef

from gold_axis_2026.v163_research import run_v163_heterogeneous_forecasters as v163

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v164_research/contracts/v164_adaptive_error_memory_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v164_research"

VARIANTS = ["STATIC", "FORGET", "ERRMEM", "LOCAL_ERRMEM"]


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V164_SCORING":
        raise RuntimeError("V164_CONTRACT_NOT_FROZEN")
    g = c["governance"]
    if g["AUTO_SELECTOR"] != "OFF" or g["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V164_GOVERNANCE_LOCK_FAIL")
    if c["evaluation"]["selector_scoring_in_v164"] != "FORBIDDEN":
        raise RuntimeError("V164_SELECTOR_MUST_REMAIN_FORBIDDEN")
    if c["evaluation"]["abstention_tuning_in_v164"] != "FORBIDDEN":
        raise RuntimeError("V164_ABSTENTION_MUST_REMAIN_FORBIDDEN")
    return c


def _fit_model(kind: str, X: pd.DataFrame, y: pd.Series, sample_weight: np.ndarray | None = None):
    m = v163.make_model(kind)
    if sample_weight is None:
        m.fit(X, y)
    elif kind == "ridge":
        m.fit(X, y, logisticregression__sample_weight=np.asarray(sample_weight, dtype=float))
    elif kind == "hgb":
        m.fit(X, y, histgradientboostingclassifier__sample_weight=np.asarray(sample_weight, dtype=float))
    else:
        raise ValueError(kind)
    return m


def _effective_n(w: np.ndarray) -> float:
    w = np.asarray(w, dtype=float)
    s = float(np.sum(w))
    q = float(np.sum(np.square(w)))
    return 0.0 if q <= 0 else s * s / q


def _state_local_weights(
    d: pd.DataFrame,
    hist_origins: list[int],
    current_t: int,
    ages: np.ndarray,
    half_life: float,
    state_features: list[str],
) -> tuple[np.ndarray, float, float]:
    hist = d.loc[hist_origins, state_features].astype(float).copy()
    cur = d.loc[[current_t], state_features].astype(float).copy()

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
    recency = np.power(0.5, ages / float(half_life))
    w = kernel * recency
    return w, _effective_n(w), bandwidth


def _residual_correction(
    residuals: np.ndarray,
    weights: np.ndarray,
    rho: float,
    shrink_kappa: float,
) -> tuple[float, float]:
    weights = np.asarray(weights, dtype=float)
    residuals = np.asarray(residuals, dtype=float)
    if len(weights) == 0 or float(weights.sum()) <= 0:
        return 0.0, 0.0
    neff = _effective_n(weights)
    mu = float(np.sum(weights * residuals) / np.sum(weights))
    shrink = neff / (neff + float(shrink_kappa)) if neff > 0 else 0.0
    return float(rho * shrink * mu), neff


def sequential_parent(
    d: pd.DataFrame,
    h: int,
    parent: str,
    kind: str,
    features: list[str],
    contract: dict,
) -> pd.DataFrame:
    y, ret, target_date = v163.target_series(d, h)
    missing = [c for c in features if c not in d.columns]
    if missing:
        raise RuntimeError(f"V164_PARENT_FEATURES_MISSING:{parent}:{missing}")

    state_features = list(contract["state_local"]["state_features"])
    missing_state = [c for c in state_features if c not in d.columns]
    if missing_state:
        raise RuntimeError(f"V164_STATE_FEATURES_MISSING:{missing_state}")

    cap = int(contract["training"]["rolling_window"])
    min_n = int(contract["training"]["minimum_mature_targets"])
    train_half = float(contract["training"]["forgetting_half_life_origins"])
    mem_half = float(contract["training"]["residual_memory_half_life_origins"])
    mem_min = int(contract["training"]["minimum_error_memory_points"])
    shrink_kappa = float(contract["training"]["error_memory_shrink_kappa"])
    rho = float(contract["training"]["error_correction_rho"])
    p_lo, p_hi = [float(x) for x in contract["training"]["probability_clip"]]
    min_local_neff = float(contract["state_local"]["minimum_local_effective_n"])
    start = pd.Timestamp(contract["windows"]["formation_start"])

    rows: list[dict] = []
    history: list[dict] = []

    for t in range(len(d) - h):
        if pd.Timestamp(d.loc[t, "date"]) < start:
            continue

        idx = v163.matured_indices(y, t, h, cap)
        if len(idx) < min_n:
            continue
        yy = y.iloc[idx].astype(int)
        if yy.nunique() < 2:
            continue

        X_train = d.loc[idx, features]
        X_now = d.loc[[t], features]

        static_model = _fit_model(kind, X_train, yy)
        p_static = float(static_model.predict_proba(X_now)[0, 1])

        age_train = np.asarray([t - j for j in idx], dtype=float)
        w_train = np.power(0.5, age_train / train_half)
        forget_model = _fit_model(kind, X_train, yy, sample_weight=w_train)
        p_forget = float(forget_model.predict_proba(X_now)[0, 1])

        mature_hist = [r for r in history if int(r["origin_index"]) + h <= t]
        global_corr = 0.0
        global_neff = 0.0
        local_corr = 0.0
        local_neff = 0.0
        local_bandwidth = math.nan
        memory_n = len(mature_hist)

        if memory_n >= mem_min:
            hist_origins = [int(r["origin_index"]) for r in mature_hist]
            residuals = np.asarray([float(r["y"]) - float(r["p_forget"]) for r in mature_hist], dtype=float)
            ages = np.asarray([t - j for j in hist_origins], dtype=float)
            global_w = np.power(0.5, ages / mem_half)
            global_corr, global_neff = _residual_correction(residuals, global_w, rho, shrink_kappa)

            local_w, local_neff, local_bandwidth = _state_local_weights(
                d, hist_origins, t, ages, mem_half, state_features
            )
            if local_neff >= min_local_neff:
                local_corr, _ = _residual_correction(residuals, local_w, rho, shrink_kappa)

        p_static = float(np.clip(p_static, p_lo, p_hi))
        p_forget = float(np.clip(p_forget, p_lo, p_hi))
        p_errmem = float(np.clip(p_forget + global_corr, p_lo, p_hi))
        p_local = float(np.clip(p_forget + local_corr, p_lo, p_hi))

        freq_idx = [j for j in range(t) if j + h <= t and pd.notna(y.iloc[j])]
        freq = float((y.iloc[freq_idx].sum() + 0.5) / (len(freq_idx) + 1.0))

        row = {
            "parent": parent,
            "origin_index": int(t),
            "origin_date": d.loc[t, "date"],
            "target_date": target_date.iloc[t],
            "horizon": int(h),
            "y": int(y.iloc[t]),
            "return": float(ret.iloc[t]),
            "P50": 0.5,
            "FREQ": freq,
            "STATIC": p_static,
            "FORGET": p_forget,
            "ERRMEM": p_errmem,
            "LOCAL_ERRMEM": p_local,
            "train_n": int(len(idx)),
            "memory_n": int(memory_n),
            "global_error_correction": float(global_corr),
            "global_error_effective_n": float(global_neff),
            "local_error_correction": float(local_corr),
            "local_error_effective_n": float(local_neff),
            "local_bandwidth": float(local_bandwidth) if np.isfinite(local_bandwidth) else np.nan,
            "feature_missing_fraction": float(d.loc[t, features].isna().mean()),
        }
        rows.append(row)
        history.append({
            "origin_index": int(t),
            "y": int(y.iloc[t]),
            "p_forget": p_forget,
        })

    return pd.DataFrame(rows)


def metric_block(f: pd.DataFrame, col: str) -> dict:
    z = f[["y", col]].dropna()
    if z.empty:
        return {"n": 0, "status": "EMPTY"}
    y = z["y"].to_numpy(dtype=int)
    p = np.clip(z[col].to_numpy(dtype=float), 1e-9, 1 - 1e-9)
    pred = (p >= 0.5).astype(int)
    both_actual = len(np.unique(y)) == 2
    both_pred = len(np.unique(pred)) == 2
    return {
        "n": int(len(z)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)) if both_actual else None,
        "mcc": float(matthews_corrcoef(y, pred)) if both_actual and both_pred else 0.0,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
    }


def period_slice(f: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od = pd.to_datetime(f["origin_date"])
    td = pd.to_datetime(f["target_date"])
    return f[(od >= a) & (od <= b) & (td <= b)].copy()


def period_metrics(f: pd.DataFrame, contract: dict) -> dict:
    w = contract["windows"]
    periods = {
        "FORMATION_2024": period_slice(f, w["formation_start"], w["formation_end"]),
        "VALIDATION_2025": period_slice(f, w["validation_start"], w["validation_end"]),
        "TEST_2026_AVAILABLE": period_slice(f, w["test_start"], w["test_end"]),
    }
    out = {}
    for name, g in periods.items():
        out[name] = {"P50": metric_block(g, "P50"), "FREQ": metric_block(g, "FREQ")}
        for v in VARIANTS:
            out[name][v] = metric_block(g, v)
    return out


def success_gate(periods: dict, contract: dict) -> dict:
    cfg = contract["evaluation"]["primary_success_gate_each_variant"]
    out = {}
    for v in ["FORGET", "ERRMEM", "LOCAL_ERRMEM"]:
        checks: dict[str, dict] = {}
        for p in ["VALIDATION_2025", "TEST_2026_AVAILABLE"]:
            m = periods[p][v]
            s = periods[p]["STATIC"]
            fq = periods[p]["FREQ"]
            checks[p] = {
                "brier_vs_frequency_pass": m["brier"] <= fq["brier"],
                "brier_vs_static_pass": m["brier"] < s["brier"],
                "brier_improvement_vs_static": float(s["brier"] - m["brier"]),
                "log_loss_vs_static_pass": m["log_loss"] <= s["log_loss"],
                "balanced_pass": (m.get("balanced_accuracy") or 0.0) >= float(cfg["validation_and_test_balanced_accuracy_min"]),
                "mcc_pass": (m.get("mcc") or 0.0) > 0.0,
                "both_directions_pass": m.get("up_predictions", 0) > 0 and m.get("down_predictions", 0) > 0,
            }
            checks[p]["pass"] = bool(all(value for key, value in checks[p].items() if key.endswith("_pass")))

        test_improvement = checks["TEST_2026_AVAILABLE"]["brier_improvement_vs_static"]
        test_min_pass = test_improvement >= float(cfg["test_brier_improvement_vs_static_parent_min"])
        out[v] = {
            "periods": checks,
            "test_brier_minimum_improvement_pass": bool(test_min_pass),
            "pass": bool(all(checks[p]["pass"] for p in checks) and test_min_pass),
        }
    return out


def memory_diagnostics(f: pd.DataFrame) -> dict:
    if f.empty:
        return {"rows": 0}
    return {
        "rows": int(len(f)),
        "memory_n_median": float(f["memory_n"].median()),
        "global_effective_n_median": float(f["global_error_effective_n"].median()),
        "local_effective_n_median": float(f["local_error_effective_n"].median()),
        "mean_abs_global_correction": float(f["global_error_correction"].abs().mean()),
        "mean_abs_local_correction": float(f["local_error_correction"].abs().mean()),
        "local_correction_nonzero_share": float((f["local_error_correction"].abs() > 0).mean()),
    }


def main() -> int:
    contract = load_contract()
    database_url = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("BLOCKED_DATA:NEON_DATABASE_URL_REQUIRED")

    OUT.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(database_url, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("set transaction isolation level repeatable read, read only")
        panel, source_evidence = v163.build_panel(conn, contract)

    result = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "source_evidence": source_evidence,
        "origin_rows": int(len(panel)),
        "horizons": {},
        "governance": {
            "AUTO_SELECTOR": "OFF",
            "AUTO_ENSEMBLE": "OFF",
            "production_authority": False,
            "production_writes": "NONE",
        },
    }

    any_pass = False
    for h in [int(x) for x in contract["horizons"]]:
        hres = {"parents": {}}
        for parent, (kind, features) in v163.EXPERTS.items():
            pred = sequential_parent(panel, h, parent, kind, list(features), contract)
            if pred.empty:
                raise RuntimeError(f"V164_EMPTY_PREDICTIONS:{h}:{parent}")
            pred.to_csv(OUT / f"v164_{h}d_{parent.lower()}_predictions.csv", index=False)
            periods = period_metrics(pred, contract)
            gate = success_gate(periods, contract)
            any_pass = any_pass or any(x["pass"] for x in gate.values())
            hres["parents"][parent] = {
                "prediction_rows": int(len(pred)),
                "period_metrics": periods,
                "success_gate": gate,
                "memory_diagnostics": memory_diagnostics(pred),
            }
        hres["any_variant_pass"] = bool(any(
            v["pass"]
            for parent_data in hres["parents"].values()
            for v in parent_data["success_gate"].values()
        ))
        result["horizons"][f"{h}D"] = hres

    result["overall_any_variant_pass"] = bool(any_pass)
    result["scientific_interpretation_lock"] = {
        "selector_scoring_performed": False,
        "abstention_tuning_performed": False,
        "post_score_parameter_search_performed": False,
        "2025_2026_are_researcher_visible": True,
        "prospective_claim": False,
    }

    (OUT / "v164_adaptive_error_memory_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    panel.to_csv(OUT / "v164_panel.csv", index=False)
    print(json.dumps(result, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
