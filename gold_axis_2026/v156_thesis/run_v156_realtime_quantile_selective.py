from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, matthews_corrcoef
from sklearn.pipeline import make_pipeline

from gold_axis_2026.v155_thesis.run_v155_dynamic_crossmarket_direction import build_panel

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v156_thesis/contracts/v156_realtime_quantile_selective_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v156_thesis"


def add_target(d: pd.DataFrame, h: int) -> pd.DataFrame:
    z = d.copy().sort_values("date").reset_index(drop=True)
    z["target_close"] = z["close"].shift(-h)
    z["target_date"] = z["date"].shift(-h)
    z["target_return"] = np.log(z["target_close"] / z["close"])
    z["y"] = np.where(z["target_return"].notna(), (z["target_return"] > 0).astype(int), np.nan)
    z["origin_index"] = np.arange(len(z), dtype=int)
    return z


def _regressor(cfg: dict, q: float):
    return make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
        HistGradientBoostingRegressor(
            loss="quantile",
            quantile=float(q),
            max_depth=int(cfg["max_depth"]),
            max_iter=int(cfg["max_iter"]),
            learning_rate=float(cfg["learning_rate"]),
            l2_regularization=float(cfg["l2_regularization"]),
            random_state=int(cfg["random_state"]),
        ),
    )


def sequential_quantiles(z: pd.DataFrame, features: list[str], model_id: str, cfg: dict, h: int, prediction_start: str) -> pd.DataFrame:
    start = pd.Timestamp(prediction_start)
    qs = [float(x) for x in cfg["quantiles"]]
    min_train = int(cfg["minimum_mature_targets"])
    rows = []
    for t in range(len(z) - h):
        if pd.Timestamp(z.loc[t, "date"]) < start:
            continue
        mature = [j for j in range(t) if j + h <= t and pd.notna(z.loc[j, "target_return"])]
        if len(mature) < min_train:
            continue
        weights = None
        if cfg["training_mode"] == "ROLLING":
            mature = mature[-int(cfg["window"]):]
        elif cfg["training_mode"] == "EXP_WEIGHTED":
            ages = np.arange(len(mature) - 1, -1, -1, dtype=float)
            weights = np.exp(-math.log(2.0) * ages / float(cfg["half_life"]))
        else:
            raise KeyError(cfg["training_mode"])
        X = z.loc[mature, features]
        y = z.loc[mature, "target_return"].astype(float)
        preds = []
        for q in qs:
            model = _regressor(cfg, q)
            fit_kwargs = {} if weights is None else {"histgradientboostingregressor__sample_weight": weights}
            model.fit(X, y, **fit_kwargs)
            preds.append(float(model.predict(z.loc[[t], features])[0]))
        # Monotone rearrangement was frozen before scoring.
        q25, q50, q75 = sorted(preds)
        rows.append(
            {
                "origin_index": int(t),
                "origin_date": z.loc[t, "date"],
                "target_date": z.loc[t, "target_date"],
                "target_return": float(z.loc[t, "target_return"]),
                "y": int(z.loc[t, "y"]),
                "model_id": model_id,
                "q25": q25,
                "q50": q50,
                "q75": q75,
                "train_n": int(len(mature)),
            }
        )
    return pd.DataFrame(rows)


def _period(f: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    return f[(f["origin_date"] >= a) & (f["origin_date"] <= b) & (f["target_date"] <= b)].copy()


def median_metrics(f: pd.DataFrame) -> dict:
    if f.empty:
        return {"n": 0, "status": "BLOCKED_EMPTY"}
    y = f["y"].astype(int).to_numpy()
    pred = (f["q50"].to_numpy(float) > 0).astype(int)
    return {
        "n": int(len(f)),
        "accuracy": float(accuracy_score(y, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "actual_up_rate": float(np.mean(y)),
        "predicted_up_rate": float(np.mean(pred)),
        "median_predicted_return": float(np.median(f["q50"].to_numpy(float))),
        "median_realized_return": float(np.median(f["target_return"].to_numpy(float))),
    }


def selective_metrics(f: pd.DataFrame) -> dict:
    if f.empty:
        return {"n": 0, "coverage": 0.0, "status": "BLOCKED_EMPTY"}
    up = f["q25"].to_numpy(float) > 0
    down = f["q75"].to_numpy(float) < 0
    take = up | down
    if not take.any():
        return {"n": 0, "coverage": 0.0, "status": "NO_SIGNAL"}
    z = f.loc[take].copy()
    pred = np.where(z["q25"].to_numpy(float) > 0, 1, 0)
    y = z["y"].astype(int).to_numpy()
    return {
        "n": int(len(z)),
        "coverage": float(len(z) / len(f)),
        "selective_accuracy": float(accuracy_score(y, pred)),
        "selective_balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "up_signals": int((pred == 1).sum()),
        "down_signals": int((pred == 0).sum()),
        "median_signed_realized_return": float(np.median(np.where(pred == 1, 1.0, -1.0) * z["target_return"].to_numpy(float))),
    }


def _median_gate(v: dict, t: dict, lane: str, contract: dict) -> dict:
    g = contract["evaluation"]["research_interest_gates"][lane]
    checks = {
        "validation_accuracy": v.get("accuracy", 0.0) >= float(g["accuracy_each_period_min"]),
        "validation_balanced": v.get("balanced_accuracy", 0.0) >= float(g["balanced_accuracy_each_period_min"]),
        "test_accuracy": t.get("accuracy", 0.0) >= float(g["accuracy_each_period_min"]),
        "test_balanced": t.get("balanced_accuracy", 0.0) >= float(g["balanced_accuracy_each_period_min"]),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def _selective_gate(v: dict, t: dict, lane: str, contract: dict) -> dict:
    g = contract["evaluation"]["research_interest_gates"][lane]
    checks = {
        "validation_accuracy": v.get("selective_accuracy", 0.0) >= float(g["selective_accuracy_each_period_min"]),
        "validation_coverage": v.get("coverage", 0.0) >= float(g["coverage_each_period_min"]),
        "test_accuracy": t.get("selective_accuracy", 0.0) >= float(g["selective_accuracy_each_period_min"]),
        "test_coverage": t.get("coverage", 0.0) >= float(g["coverage_each_period_min"]),
    }
    return {"pass": bool(all(checks.values())), "checks": checks}


def run_horizon(panel: pd.DataFrame, features: list[str], h: int, lane: str, contract: dict) -> tuple[dict, pd.DataFrame]:
    z = add_target(panel, h)
    w = contract["windows"]
    periods = {
        "FORMATION_2024": (w["formation_score_start"], w["formation_score_end"]),
        "VALIDATION_2025": (w["validation_start"], w["validation_end"]),
        "TEST_2026_AVAILABLE": (w["test_start"], w["test_end"]),
    }
    out = {"models": {}}
    all_rows = []
    for mid, cfg in contract["models"].items():
        f = sequential_quantiles(z, features, mid, cfg, h, w["formation_score_start"])
        block = {}
        for plabel, (a, b) in periods.items():
            g = _period(f, a, b)
            block[plabel] = {"median_direction": median_metrics(g), "iqr_excludes_zero": selective_metrics(g)}
            gg = g.copy()
            gg["period"] = plabel
            gg["lane"] = lane
            all_rows.append(gg)
        vg = block["VALIDATION_2025"]
        tg = block["TEST_2026_AVAILABLE"]
        med_lane = "TACTICAL_H1_MEDIAN" if h == 1 else "STRATEGIC_H20_MEDIAN"
        sel_lane = "TACTICAL_H1_SELECTIVE" if h == 1 else "STRATEGIC_H20_SELECTIVE"
        block["median_research_interest_gate"] = _median_gate(vg["median_direction"], tg["median_direction"], med_lane, contract)
        block["selective_research_interest_gate"] = _selective_gate(vg["iqr_excludes_zero"], tg["iqr_excludes_zero"], sel_lane, contract)
        out["models"][mid] = block
    return out, pd.concat(all_rows, ignore_index=True) if all_rows else pd.DataFrame()


def main() -> None:
    contract = json.loads(CONTRACT.read_text())
    if contract["status"] != "FROZEN_BEFORE_V156_2025_2026_SCORING":
        raise RuntimeError("CONTRACT_NOT_FROZEN")
    if contract["governance"]["production_authority"]:
        raise RuntimeError("PRODUCTION_AUTHORITY_MUST_BE_FALSE")
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    # build_panel needs only the V1.55-compatible source/window keys supplied here.
    inherited = {
        "windows": contract["windows"],
    }
    with psycopg.connect(db) as conn:
        panel, _, full_features = build_panel(conn, inherited)
    results = {}
    preds = []
    for lane, h in contract["horizons"].items():
        block, p = run_horizon(panel, full_features, int(h), lane, contract)
        results[lane] = block
        if not p.empty:
            preds.append(p)
    report = {
        "contract_id": contract["contract_id"],
        "evidence_class": contract["evidence_class"],
        "panel_n": int(len(panel)),
        "panel_first": panel["date"].min().date().isoformat(),
        "panel_last": panel["date"].max().date().isoformat(),
        "feature_count": int(len(full_features)),
        "features": full_features,
        "results": results,
        "governance": contract["governance"],
        "notes": [
            "Each fit uses only returns whose target is mature at the current origin.",
            "The IQR-excludes-zero direction rule was frozen before scoring and emits NO_SIGNAL when the interquartile predictive interval crosses zero.",
            "2025/2026 are retrospective successor diagnostics, not fresh blind confirmation.",
            "No threshold/model change is permitted inside V1.56 after reading this output."
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT / "v156_quantile_panel.csv", index=False)
    if preds:
        pd.concat(preds, ignore_index=True).to_csv(OUT / "v156_quantile_predictions.csv", index=False)
    (OUT / "v156_quantile_results.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
