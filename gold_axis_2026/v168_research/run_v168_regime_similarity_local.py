from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    matthews_corrcoef,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v168_research/contracts/v168_regime_similarity_local_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v168_research"


@dataclass
class OriginForecast:
    global_p: float
    recent_p: float
    similar_p: float
    frequency_p: float
    similar_n: int
    recent_n: int
    mean_similar_distance: float | None
    local_fallback: bool


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V168_SCORING":
        raise RuntimeError("V168_CONTRACT_NOT_FROZEN")
    if c["governance"]["AUTO_SELECTOR"] != "OFF" or c["governance"]["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V168_GOVERNANCE_LOCK_FAIL")
    required = {
        "2024Q4_2025_2026_based_K_selection",
        "state_vector_changes_after_scoring",
        "kernel_shape_search",
        "selector_or_CRASE",
        "forecast_combination_between_blocks",
        "production_writes",
    }
    if not required.issubset(set(c["forbidden_in_v168"])):
        raise RuntimeError("V168_FORBIDDEN_LOCK_FAIL")
    return c


def artifact_dir() -> Path:
    raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
    if not raw:
        raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED")
    p = Path(raw)
    if not (p / "v164_panel.csv").exists():
        raise RuntimeError("V168_SOURCE_PANEL_MISSING")
    return p


def build_target_panel(panel: pd.DataFrame) -> pd.DataFrame:
    z = panel.copy().reset_index().rename(columns={"index": "origin_index"})
    z["origin_date"] = pd.to_datetime(z["date"])
    z["target_date"] = pd.to_datetime(z["date"].shift(-3))
    z["target_close"] = pd.to_numeric(z["close"].shift(-3), errors="coerce")
    z["origin_close"] = pd.to_numeric(z["close"], errors="coerce")
    z["y"] = (z["target_close"] > z["origin_close"]).astype(float)
    z = z[z["target_date"].notna() & z["target_close"].notna()].copy()
    z["y"] = z["y"].astype(int)
    return z


def make_model(contract: dict) -> Pipeline:
    cfg = contract["model_lock"]
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(
            C=float(cfg["C"]),
            solver=str(cfg["solver"]),
            max_iter=int(cfg["max_iter"]),
            class_weight=cfg["class_weight"],
            random_state=0,
        )),
    ])


def fit_probability(train: pd.DataFrame, current: pd.DataFrame, features: list[str], contract: dict) -> float:
    y = train["y"].to_numpy(dtype=int)
    if len(train) < int(contract["model_lock"]["minimum_training_rows"]) or len(np.unique(y)) < 2:
        return 0.5
    model = make_model(contract)
    model.fit(train[features], y)
    return float(model.predict_proba(current[features])[:, 1][0])


def matured_history(panel: pd.DataFrame, origin_date: pd.Timestamp) -> pd.DataFrame:
    return panel[pd.to_datetime(panel["target_date"]) < origin_date].copy()


def causal_frequency(history: pd.DataFrame, min_support: int = 20) -> float:
    if len(history) < min_support:
        return 0.5
    return float(history["y"].mean())


def similarity_indices(history: pd.DataFrame, current: pd.DataFrame, state_features: list[str], k: int) -> tuple[np.ndarray, float | None]:
    hist = history[state_features].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
    cur = current[state_features].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)[0]

    valid_dims = []
    medians = []
    means = []
    scales = []
    for j in range(hist.shape[1]):
        col = hist[:, j]
        finite = np.isfinite(col)
        if int(finite.sum()) < 2:
            continue
        med = float(np.median(col[finite]))
        filled = np.where(finite, col, med)
        mean = float(np.mean(filled))
        sd = float(np.std(filled, ddof=0))
        if not np.isfinite(sd) or sd < 1e-12:
            sd = 1.0
        valid_dims.append(j)
        medians.append(med)
        means.append(mean)
        scales.append(sd)

    if not valid_dims:
        n = min(int(k), len(history))
        idx = np.arange(max(0, len(history) - n), len(history), dtype=int)
        return idx, None

    h = hist[:, valid_dims].copy()
    c = cur[valid_dims].copy()
    med = np.asarray(medians, dtype=float)
    mu = np.asarray(means, dtype=float)
    sd = np.asarray(scales, dtype=float)

    for j in range(h.shape[1]):
        h[~np.isfinite(h[:, j]), j] = med[j]
        if not np.isfinite(c[j]):
            c[j] = med[j]
    hz = (h - mu) / sd
    cz = (c - mu) / sd
    dist = np.sqrt(np.sum(np.square(hz - cz), axis=1))
    n = min(int(k), len(history))
    order = np.argsort(dist, kind="mergesort")[:n]
    return order.astype(int), float(np.mean(dist[order])) if len(order) else None


def forecast_origin(panel: pd.DataFrame, row_index: int, block_features: list[str], k: int, contract: dict) -> OriginForecast:
    current = panel.iloc[[row_index]].copy()
    origin_date = pd.Timestamp(current.iloc[0]["origin_date"])
    hist = matured_history(panel, origin_date).sort_values("origin_date").copy()
    min_train = int(contract["model_lock"]["minimum_training_rows"])
    if len(hist) < min_train:
        return OriginForecast(0.5, 0.5, 0.5, causal_frequency(hist), 0, 0, None, True)

    global_p = fit_probability(hist, current, block_features, contract)
    recent_n = min(int(k), len(hist))
    recent = hist.tail(recent_n).copy()
    recent_p = fit_probability(recent, current, block_features, contract)
    if recent["y"].nunique() < 2:
        recent_p = global_p

    sim_idx, mean_dist = similarity_indices(hist, current, contract["state_vector"], int(k))
    similar = hist.iloc[sim_idx].copy()
    similar_p = fit_probability(similar, current, block_features, contract)
    local_fallback = False
    if similar["y"].nunique() < 2:
        similar_p = global_p
        local_fallback = True

    return OriginForecast(
        global_p=global_p,
        recent_p=recent_p,
        similar_p=similar_p,
        frequency_p=causal_frequency(hist),
        similar_n=int(len(similar)),
        recent_n=int(len(recent)),
        mean_similar_distance=mean_dist,
        local_fallback=local_fallback,
    )


def metric_bundle(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y, dtype=int)
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    ba = float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None
    mcc = float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0
    return {
        "n": int(len(y)),
        "brier": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
        "roc_auc": auc,
        "balanced_accuracy": ba,
        "mcc": mcc,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "both_predicted_directions": bool(len(np.unique(pred)) == 2),
        "mean_probability": float(np.mean(p)),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
    }


def period_indices(panel: pd.DataFrame, start: str, end: str) -> list[int]:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od = pd.to_datetime(panel["origin_date"])
    td = pd.to_datetime(panel["target_date"])
    return panel.index[(od >= a) & (od <= b) & (td <= b)].tolist()


def generate_predictions(panel: pd.DataFrame, indices: list[int], block: str, features: list[str], k: int, contract: dict, period: str) -> pd.DataFrame:
    rows = []
    for i in indices:
        fc = forecast_origin(panel, i, features, k, contract)
        r = panel.loc[i]
        rows.append({
            "period": period,
            "block": block,
            "k": int(k),
            "origin_index": int(r["origin_index"]),
            "origin_date": pd.Timestamp(r["origin_date"]).strftime("%Y-%m-%d"),
            "target_date": pd.Timestamp(r["target_date"]).strftime("%Y-%m-%d"),
            "y": int(r["y"]),
            "GLOBAL": fc.global_p,
            "RECENT_K": fc.recent_p,
            "SIMILAR_K": fc.similar_p,
            "CAUSAL_FREQUENCY": fc.frequency_p,
            "similar_n": fc.similar_n,
            "recent_n": fc.recent_n,
            "mean_similar_distance": fc.mean_similar_distance,
            "local_fallback": fc.local_fallback,
        })
    return pd.DataFrame(rows)


def select_k(panel: pd.DataFrame, contract: dict) -> tuple[int, pd.DataFrame, pd.DataFrame]:
    detail_parts = []
    for k in contract["k_selection"]["grid"]:
        for period, (start, end) in contract["k_selection"]["selection_periods"].items():
            idx = period_indices(panel, start, end)
            for block, features in contract["candidate_predictor_blocks"].items():
                detail_parts.append(generate_predictions(panel, idx, block, features, int(k), contract, period))
    detail = pd.concat(detail_parts, ignore_index=True)

    summary_rows = []
    for k, g in detail.groupby("k", sort=True):
        y = g["y"].to_numpy(dtype=int)
        p = g["SIMILAR_K"].to_numpy(dtype=float)
        summary_rows.append({
            "k": int(k),
            "n_predictions": int(len(g)),
            "similar_brier": float(brier_score_loss(y, p)),
            "similar_log_loss": float(log_loss(y, np.clip(p, 1e-6, 1 - 1e-6), labels=[0, 1])),
            "recent_brier": float(brier_score_loss(y, g["RECENT_K"].to_numpy(dtype=float))),
            "global_brier": float(brier_score_loss(y, g["GLOBAL"].to_numpy(dtype=float))),
            "frequency_brier": float(brier_score_loss(y, g["CAUSAL_FREQUENCY"].to_numpy(dtype=float))),
            "local_fallback_rate": float(g["local_fallback"].mean()),
        })
    summary = pd.DataFrame(summary_rows)
    best = summary.sort_values(["similar_brier", "similar_log_loss", "k"], ascending=[True, True, False]).iloc[0]
    return int(best["k"]), summary, detail


def evaluate_period_predictions(pred: pd.DataFrame) -> dict:
    out = {}
    y = pred["y"].to_numpy(dtype=int)
    for model in ["CAUSAL_FREQUENCY", "GLOBAL", "RECENT_K", "SIMILAR_K"]:
        out[model] = metric_bundle(y, pred[model].to_numpy(dtype=float))
    out["similar_minus_global_brier"] = float(out["SIMILAR_K"]["brier"] - out["GLOBAL"]["brier"])
    out["similar_minus_recent_brier"] = float(out["SIMILAR_K"]["brier"] - out["RECENT_K"]["brier"])
    out["similar_minus_frequency_brier"] = float(out["SIMILAR_K"]["brier"] - out["CAUSAL_FREQUENCY"]["brier"])
    out["local_fallback_rate"] = float(pred["local_fallback"].mean())
    out["mean_similar_distance"] = float(pred["mean_similar_distance"].dropna().mean()) if pred["mean_similar_distance"].notna().any() else None
    return out


def bridge_pass(metrics: dict, contract: dict) -> bool:
    sim = metrics["SIMILAR_K"]
    glob = metrics["GLOBAL"]
    rec = metrics["RECENT_K"]
    fq = metrics["CAUSAL_FREQUENCY"]
    auc_min = float(contract["bridge_success_gate_per_block"]["SIMILAR_K_roc_auc_min"])
    return bool(
        sim["brier"] <= glob["brier"] + 1e-12
        and sim["brier"] <= rec["brier"] + 1e-12
        and sim["brier"] <= fq["brier"] + 1e-12
        and sim["log_loss"] <= glob["log_loss"] + 1e-12
        and sim["roc_auc"] is not None
        and sim["roc_auc"] >= auc_min
        and sim["both_predicted_directions"]
    )


def visible_persistence_pass(periods: dict[str, dict], contract: dict) -> bool:
    auc_min = float(contract["visible_persistence_gate_per_block"]["2025_and_2026_SIMILAR_K_auc_min"])
    for name in ["diagnostic_2025", "diagnostic_2026_available"]:
        m = periods[name]
        sim, glob, fq = m["SIMILAR_K"], m["GLOBAL"], m["CAUSAL_FREQUENCY"]
        if not (
            sim["brier"] <= glob["brier"] + 1e-12
            and sim["brier"] <= fq["brier"] + 1e-12
            and sim["roc_auc"] is not None
            and sim["roc_auc"] >= auc_min
            and sim["both_predicted_directions"]
        ):
            return False
    return True


def run() -> None:
    c = load_contract()
    panel = build_target_panel(pd.read_csv(artifact_dir() / c["source_artifact"]["required_file"]))
    panel["origin_date"] = pd.to_datetime(panel["origin_date"])
    panel["target_date"] = pd.to_datetime(panel["target_date"])

    required_features = set(c["state_vector"])
    for fs in c["candidate_predictor_blocks"].values():
        required_features.update(fs)
    missing = sorted(f for f in required_features if f not in panel.columns)
    if missing:
        raise RuntimeError(f"V168_FEATURES_MISSING:{missing}")

    chosen_k, k_summary, selection_detail = select_k(panel, c)
    OUT.mkdir(parents=True, exist_ok=True)
    k_summary.to_csv(OUT / "v168_k_selection_summary.csv", index=False)
    selection_detail.to_csv(OUT / "v168_k_selection_predictions.csv", index=False)

    all_eval = []
    period_metrics: dict[str, dict[str, dict]] = {}
    for period, (start, end) in c["evaluation_periods"].items():
        idx = period_indices(panel, start, end)
        period_metrics[period] = {}
        for block, features in c["candidate_predictor_blocks"].items():
            pred = generate_predictions(panel, idx, block, features, chosen_k, c, period)
            all_eval.append(pred)
            period_metrics[period][block] = evaluate_period_predictions(pred)

    eval_df = pd.concat(all_eval, ignore_index=True)
    eval_df.to_csv(OUT / "v168_evaluation_predictions.csv", index=False)

    bridge = {block: bridge_pass(period_metrics["bridge_2024Q4"][block], c) for block in c["candidate_predictor_blocks"]}
    visible = {
        block: visible_persistence_pass({
            "diagnostic_2025": period_metrics["diagnostic_2025"][block],
            "diagnostic_2026_available": period_metrics["diagnostic_2026_available"][block],
        }, c)
        for block in c["candidate_predictor_blocks"]
    }

    if any(bridge[b] and visible[b] for b in bridge):
        decision = "PROMISING_REGIME_SIMILARITY_CANDIDATE__PROSPECTIVE_SHADOW_REQUIRED"
    elif any(bridge.values()):
        decision = "BRIDGE_PASS_VISIBLE_PERSISTENCE_FAIL__RETURN_TO_INFORMATION_OR_HORIZON_REDESIGN"
    else:
        decision = "BRIDGE_FAIL__REJECT_REGIME_SIMILARITY_ESCALATION_FOR_CURRENT_INFORMATION_SET"

    result = {
        "contract_id": c["contract_id"],
        "evidence_class": c["evidence_class"],
        "chosen_k_pre2025": int(chosen_k),
        "k_selection_summary": k_summary.to_dict(orient="records"),
        "period_metrics": period_metrics,
        "bridge_pass_by_block": bridge,
        "visible_persistence_pass_by_block": visible,
        "decision": decision,
    }
    (OUT / "v168_regime_similarity_local_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
