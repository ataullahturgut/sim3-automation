from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    matthews_corrcoef,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v169_research/contracts/v169_target_forecastability_audit_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v169_research"


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V169_SCORING":
        raise RuntimeError("V169_CONTRACT_NOT_FROZEN")
    if c["governance"]["AUTO_SELECTOR"] != "OFF" or c["governance"]["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V169_GOVERNANCE_LOCK_FAIL")
    required = {
        "model_family_search",
        "hyperparameter_search",
        "deadband_or_material_move_threshold_tuning",
        "abstention_threshold_tuning",
        "2025_2026_based_feature_or_horizon_selection",
        "selector_or_CRASE",
        "production_writes",
    }
    if not required.issubset(set(c["forbidden_in_v169"])):
        raise RuntimeError("V169_FORBIDDEN_LOCK_FAIL")
    return c


def artifact_dir() -> Path:
    raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
    if not raw:
        raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED")
    p = Path(raw)
    if not (p / "v164_panel.csv").exists():
        raise RuntimeError("V169_SOURCE_PANEL_MISSING")
    return p


def build_target_panel(panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    h = int(horizon)
    z = panel.copy().reset_index().rename(columns={"index": "origin_index"})
    z["origin_date"] = pd.to_datetime(z["date"])
    z["target_date"] = pd.to_datetime(z["date"].shift(-h))
    origin_close = pd.to_numeric(z["close"], errors="coerce")
    target_close = pd.to_numeric(z["close"].shift(-h), errors="coerce")
    z["continuous_return"] = np.log(target_close / origin_close)
    z["y"] = (z["continuous_return"] > 0.0).astype(float)
    z = z[z["target_date"].notna() & np.isfinite(z["continuous_return"])].copy()
    z["y"] = z["y"].astype(int)
    z["horizon"] = h
    return z


def matured_history(panel: pd.DataFrame, origin_date: pd.Timestamp) -> pd.DataFrame:
    return panel[pd.to_datetime(panel["target_date"]) < origin_date].copy()


def clean_numeric(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    out = df[features].apply(pd.to_numeric, errors="coerce").copy()
    return out.replace([np.inf, -np.inf], np.nan)


def make_logistic(c: dict) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
        ("model", LogisticRegression(C=float(c["model_lock"]["logistic_C"]), solver="lbfgs", max_iter=5000, random_state=0)),
    ])


def make_ridge(c: dict) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
        ("model", Ridge(alpha=float(c["model_lock"]["ridge_alpha"]))),
    ])


def causal_baselines(hist: pd.DataFrame) -> tuple[float, float, float]:
    if len(hist) < 20:
        return 0.5, 0.0, 0.0
    return float(hist["y"].mean()), float(hist["continuous_return"].median()), float(hist["continuous_return"].mean())


def forecast_origin(panel: pd.DataFrame, row_idx: int, features: list[str], c: dict) -> dict:
    current = panel.loc[[row_idx]].copy()
    origin = pd.Timestamp(current.iloc[0]["origin_date"])
    hist = matured_history(panel, origin).sort_values("origin_date").copy()
    freq, med_ret, mean_ret = causal_baselines(hist)
    if len(hist) < 30:
        return {
            "binary_probability": freq,
            "continuous_prediction": mean_ret,
            "frequency_probability": freq,
            "causal_median_return": med_ret,
            "causal_mean_return": mean_ret,
            "training_n": int(len(hist)),
            "fallback": True,
        }

    x_train = clean_numeric(hist, features)
    x_current = clean_numeric(current, features)
    y_bin = hist["y"].to_numpy(dtype=int)
    y_cont = hist["continuous_return"].to_numpy(dtype=float)

    if len(np.unique(y_bin)) >= 2:
        logit = make_logistic(c)
        logit.fit(x_train, y_bin)
        p = float(logit.predict_proba(x_current)[:, 1][0])
    else:
        p = freq

    ridge = make_ridge(c)
    ridge.fit(x_train, y_cont)
    rhat = float(ridge.predict(x_current)[0])
    return {
        "binary_probability": p,
        "continuous_prediction": rhat,
        "frequency_probability": freq,
        "causal_median_return": med_ret,
        "causal_mean_return": mean_ret,
        "training_n": int(len(hist)),
        "fallback": False,
    }


def period_indices(panel: pd.DataFrame, start: str, end: str) -> list[int]:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od = pd.to_datetime(panel["origin_date"])
    td = pd.to_datetime(panel["target_date"])
    return panel.index[(od >= a) & (od <= b) & (td <= b)].tolist()


def generate_predictions(panel: pd.DataFrame, indices: list[int], block: str, features: list[str], c: dict, period: str) -> pd.DataFrame:
    rows = []
    for i in indices:
        fc = forecast_origin(panel, i, features, c)
        r = panel.loc[i]
        rows.append({
            "period": period,
            "horizon": int(r["horizon"]),
            "block": block,
            "origin_index": int(r["origin_index"]),
            "origin_date": pd.Timestamp(r["origin_date"]).strftime("%Y-%m-%d"),
            "target_date": pd.Timestamp(r["target_date"]).strftime("%Y-%m-%d"),
            "continuous_return": float(r["continuous_return"]),
            "y": int(r["y"]),
            **fc,
        })
    return pd.DataFrame(rows)


def safe_corr(a: np.ndarray, b: np.ndarray, kind: str) -> float | None:
    if len(a) < 3 or np.nanstd(a) < 1e-12 or np.nanstd(b) < 1e-12:
        return None
    try:
        res = spearmanr(a, b) if kind == "spearman" else pearsonr(a, b)
        value = float(res.statistic)
        return value if np.isfinite(value) else None
    except Exception:
        return None


def metric_bundle(df: pd.DataFrame) -> dict:
    y = df["y"].to_numpy(dtype=int)
    r = df["continuous_return"].to_numpy(dtype=float)
    p = np.clip(df["binary_probability"].to_numpy(dtype=float), 1e-6, 1 - 1e-6)
    fq = np.clip(df["frequency_probability"].to_numpy(dtype=float), 1e-6, 1 - 1e-6)
    rhat = df["continuous_prediction"].to_numpy(dtype=float)
    med = df["causal_median_return"].to_numpy(dtype=float)
    mean = df["causal_mean_return"].to_numpy(dtype=float)

    direct_pred = (p >= 0.5).astype(int)
    ridge_pred = (rhat > 0.0).astype(int)
    brier = float(brier_score_loss(y, p))
    fq_brier = float(brier_score_loss(y, fq))
    ll = float(log_loss(y, p, labels=[0, 1]))
    fq_ll = float(log_loss(y, fq, labels=[0, 1]))
    mae = float(mean_absolute_error(r, rhat))
    med_mae = float(mean_absolute_error(r, med))
    mse = float(mean_squared_error(r, rhat))
    mean_mse = float(mean_squared_error(r, mean))
    auc_direct = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    auc_ridge = float(roc_auc_score(y, rhat)) if len(np.unique(y)) == 2 else None
    ba_direct = float(balanced_accuracy_score(y, direct_pred)) if len(np.unique(y)) == 2 else None
    ba_ridge = float(balanced_accuracy_score(y, ridge_pred)) if len(np.unique(y)) == 2 else None
    mcc_direct = float(matthews_corrcoef(y, direct_pred)) if len(np.unique(y)) == 2 and len(np.unique(direct_pred)) == 2 else 0.0
    mcc_ridge = float(matthews_corrcoef(y, ridge_pred)) if len(np.unique(y)) == 2 and len(np.unique(ridge_pred)) == 2 else 0.0

    return {
        "n": int(len(df)),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
        "binary": {
            "brier": brier,
            "frequency_brier": fq_brier,
            "brier_skill_vs_frequency": float(1.0 - brier / fq_brier) if fq_brier > 0 else None,
            "log_loss": ll,
            "frequency_log_loss": fq_ll,
            "log_loss_improvement_vs_frequency": float(fq_ll - ll),
            "roc_auc": auc_direct,
            "balanced_accuracy": ba_direct,
            "mcc": mcc_direct,
            "up_predictions": int(direct_pred.sum()),
            "down_predictions": int((1 - direct_pred).sum()),
            "both_predicted_directions": bool(len(np.unique(direct_pred)) == 2),
        },
        "continuous": {
            "mae": mae,
            "causal_median_mae": med_mae,
            "mae_skill_vs_causal_median": float(1.0 - mae / med_mae) if med_mae > 0 else None,
            "mse": mse,
            "causal_mean_mse": mean_mse,
            "mse_skill_vs_causal_mean": float(1.0 - mse / mean_mse) if mean_mse > 0 else None,
            "pearson_r": safe_corr(r, rhat, "pearson"),
            "spearman_r": safe_corr(r, rhat, "spearman"),
            "direction_roc_auc_from_predicted_return": auc_ridge,
            "direction_balanced_accuracy_from_sign": ba_ridge,
            "direction_mcc_from_sign": mcc_ridge,
            "up_predictions_from_sign": int(ridge_pred.sum()),
            "down_predictions_from_sign": int((1 - ridge_pred).sum()),
            "both_predicted_directions": bool(len(np.unique(ridge_pred)) == 2),
        },
    }


def formation_gates(env_metrics: dict[str, dict], c: dict) -> tuple[bool, bool]:
    cont_cfg = c["formation_diagnostics"]["continuous_signal_gate"]
    bin_cfg = c["formation_diagnostics"]["binary_signal_gate"]
    envs = sorted(env_metrics)
    cont_mae = [env_metrics[e]["continuous"]["mae_skill_vs_causal_median"] for e in envs]
    cont_spear = [env_metrics[e]["continuous"]["spearman_r"] for e in envs]
    cont_auc = [env_metrics[e]["continuous"]["direction_roc_auc_from_predicted_return"] for e in envs]
    bin_bss = [env_metrics[e]["binary"]["brier_skill_vs_frequency"] for e in envs]
    bin_auc = [env_metrics[e]["binary"]["roc_auc"] for e in envs]

    cont_ok = bool(
        sum(v is not None and v > 0.0 for v in cont_mae) >= int(cont_cfg["positive_mae_skill_environments_min"])
        and all(v is not None for v in cont_spear)
        and float(np.median(cont_spear)) >= float(cont_cfg["median_spearman_min"])
        and float(np.min(cont_spear)) >= float(cont_cfg["minimum_spearman_min"])
        and all(v is not None for v in cont_auc)
        and float(np.median(cont_auc)) >= float(cont_cfg["median_direction_auc_min"])
    )
    bin_ok = bool(
        sum(v is not None and v > 0.0 for v in bin_bss) >= int(bin_cfg["positive_brier_skill_environments_min"])
        and all(v is not None for v in bin_auc)
        and float(np.median(bin_auc)) >= float(bin_cfg["median_direction_auc_min"])
        and float(np.min(bin_auc)) >= float(bin_cfg["minimum_direction_auc_min"])
    )
    return cont_ok, bin_ok


def bridge_gates(m: dict, c: dict) -> tuple[bool, bool]:
    ccfg = c["bridge_gate"]["continuous"]
    bcfg = c["bridge_gate"]["binary"]
    cont = m["continuous"]
    binary = m["binary"]
    cont_ok = bool(
        cont["mae"] <= cont["causal_median_mae"] + 1e-12
        and cont["mse"] <= cont["causal_mean_mse"] + 1e-12
        and cont["spearman_r"] is not None and cont["spearman_r"] > 0.0
        and cont["direction_roc_auc_from_predicted_return"] is not None
        and cont["direction_roc_auc_from_predicted_return"] >= float(ccfg["direction_auc_min"])
        and cont["both_predicted_directions"]
    )
    bin_ok = bool(
        binary["brier"] <= binary["frequency_brier"] + 1e-12
        and binary["log_loss"] <= binary["frequency_log_loss"] + 1e-12
        and binary["roc_auc"] is not None and binary["roc_auc"] >= float(bcfg["direction_auc_min"])
        and binary["both_predicted_directions"]
    )
    return cont_ok, bin_ok


def magnitude_thresholds(panel: pd.DataFrame) -> tuple[float, float]:
    cutoff = pd.Timestamp("2024-09-25")
    vals = panel.loc[pd.to_datetime(panel["target_date"]) <= cutoff, "continuous_return"].abs().to_numpy(dtype=float)
    vals = vals[np.isfinite(vals)]
    if len(vals) < 20:
        raise RuntimeError("V169_MAGNITUDE_SUPPORT_TOO_SMALL")
    return float(np.quantile(vals, 0.33)), float(np.quantile(vals, 0.67))


def magnitude_diagnostics(pred: pd.DataFrame, q33: float, q67: float) -> list[dict]:
    z = pred.copy()
    a = z["continuous_return"].abs()
    z["magnitude_band"] = np.where(a <= q33, "SMALL", np.where(a <= q67, "MEDIUM", "LARGE"))
    rows = []
    for band in ["SMALL", "MEDIUM", "LARGE"]:
        g = z[z["magnitude_band"] == band]
        if len(g) == 0:
            continue
        y = g["y"].to_numpy(dtype=int)
        p = g["binary_probability"].to_numpy(dtype=float)
        rhat = g["continuous_prediction"].to_numpy(dtype=float)
        direct = (p >= 0.5).astype(int)
        ridge = (rhat > 0.0).astype(int)
        rows.append({
            "period": str(g.iloc[0]["period"]),
            "horizon": int(g.iloc[0]["horizon"]),
            "block": str(g.iloc[0]["block"]),
            "magnitude_band": band,
            "n": int(len(g)),
            "mean_abs_return": float(g["continuous_return"].abs().mean()),
            "direct_accuracy": float(accuracy_score(y, direct)),
            "continuous_sign_accuracy": float(accuracy_score(y, ridge)),
            "direct_auc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
            "continuous_score_auc": float(roc_auc_score(y, rhat)) if len(np.unique(y)) == 2 else None,
        })
    return rows


def run() -> None:
    c = load_contract()
    raw_panel = pd.read_csv(artifact_dir() / c["source_artifact"]["required_file"])
    missing = sorted({f for fs in c["feature_blocks"].values() for f in fs if f not in raw_panel.columns})
    if missing:
        raise RuntimeError(f"V169_FEATURES_MISSING:{missing}")

    OUT.mkdir(parents=True, exist_ok=True)
    all_predictions = []
    all_magnitude_rows = []
    result: dict = {
        "contract_id": c["contract_id"],
        "evidence_class": c["evidence_class"],
        "by_horizon": {},
        "decision_by_horizon": {},
    }

    for h in c["horizons"]:
        panel = build_target_panel(raw_panel, int(h))
        panel["origin_date"] = pd.to_datetime(panel["origin_date"])
        panel["target_date"] = pd.to_datetime(panel["target_date"])
        q33, q67 = magnitude_thresholds(panel)
        hres = {"magnitude_thresholds_abs_log_return": {"q33": q33, "q67": q67}, "blocks": {}}

        for block, features in c["feature_blocks"].items():
            bres = {"formation": {}, "bridge": None, "visible": {}}
            block_preds = []
            for period, (start, end) in c["temporal_design"]["forward_tests"].items():
                idx = period_indices(panel, start, end)
                pred = generate_predictions(panel, idx, block, features, c, period)
                block_preds.append(pred)
                bres["formation"][period] = metric_bundle(pred)

            formation_cont, formation_bin = formation_gates(bres["formation"], c)
            bres["formation_continuous_gate"] = formation_cont
            bres["formation_binary_gate"] = formation_bin

            start, end = c["temporal_design"]["bridge_2024Q4"]
            bridge_pred = generate_predictions(panel, period_indices(panel, start, end), block, features, c, "bridge_2024Q4")
            block_preds.append(bridge_pred)
            bridge_metrics = metric_bundle(bridge_pred)
            bridge_cont, bridge_bin = bridge_gates(bridge_metrics, c)
            bres["bridge"] = bridge_metrics
            bres["bridge_continuous_gate"] = bridge_cont
            bres["bridge_binary_gate"] = bridge_bin
            bres["continuous_candidate_pass"] = bool(formation_cont and bridge_cont)
            bres["binary_candidate_pass"] = bool(formation_bin and bridge_bin)

            for period, (start, end) in c["temporal_design"]["visible_diagnostics"].items():
                pred = generate_predictions(panel, period_indices(panel, start, end), block, features, c, period)
                block_preds.append(pred)
                bres["visible"][period] = metric_bundle(pred)

            combined = pd.concat(block_preds, ignore_index=True)
            all_predictions.append(combined)
            for period_name in ["bridge_2024Q4", "2025", "2026_available"]:
                g = combined[combined["period"] == period_name]
                all_magnitude_rows.extend(magnitude_diagnostics(g, q33, q67))
            hres["blocks"][block] = bres

        cont_pass = [b for b, d in hres["blocks"].items() if d["continuous_candidate_pass"]]
        bin_pass = [b for b, d in hres["blocks"].items() if d["binary_candidate_pass"]]
        if cont_pass and not bin_pass:
            decision = "CONTINUOUS_TARGET_SIGNAL_ONLY__SUPPORT_TARGET_REPRESENTATION_REDESIGN"
        elif cont_pass and bin_pass:
            decision = "BOTH_TARGET_REPRESENTATIONS_SHOW_SIGNAL__SEPARATE_STABILITY_COMPARISON_REQUIRED"
        elif bin_pass and not cont_pass:
            decision = "BINARY_TARGET_SIGNAL_ONLY__DO_NOT_SWITCH_TO_CONTINUOUS_ON_V169"
        else:
            decision = "NO_TRANSPORTABLE_SIGNAL_UNDER_EITHER_TARGET_REPRESENTATION__INFORMATION_OR_HORIZON_REDESIGN"
        hres["continuous_candidate_blocks"] = cont_pass
        hres["binary_candidate_blocks"] = bin_pass
        result["by_horizon"][str(h)] = hres
        result["decision_by_horizon"][str(h)] = decision

    pd.concat(all_predictions, ignore_index=True).to_csv(OUT / "v169_target_representation_predictions.csv", index=False)
    pd.DataFrame(all_magnitude_rows).to_csv(OUT / "v169_magnitude_conditioned_diagnostics.csv", index=False)
    (OUT / "v169_target_forecastability_audit_results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
