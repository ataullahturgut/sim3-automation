from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, log_loss, matthews_corrcoef, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "v170_research/contracts/v170b_free_public_positioning_pilot_freeze_v1.json"
COT_SNAPSHOT = ROOT / "v170_research/data/v170a_cftc_gold_weekly_compact.csv"
OUT = ROOT / "data_pipeline/audits/v170b_research"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V170B_FORECAST_SCORING":
        raise RuntimeError("V170B_CONTRACT_NOT_FROZEN")
    if c["governance"]["AUTO_SELECTOR"] != "OFF" or c["governance"]["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V170B_GOVERNANCE_LOCK_FAIL")
    if sha256_file(COT_SNAPSHOT) != c["new_public_data"]["compact_snapshot_sha256"]:
        raise RuntimeError("V170B_COT_SNAPSHOT_HASH_MISMATCH")
    forbidden = set(c["forbidden_in_v170b"])
    required = {
        "post_score_COT_feature_addition",
        "z_window_search",
        "availability_clock_search",
        "model_family_search",
        "hyperparameter_search",
        "2025_2026_based_candidate_selection",
        "COT_block_combination_after_score",
        "selector_or_CRASE",
        "production_writes",
    }
    if not required.issubset(forbidden):
        raise RuntimeError("V170B_FORBIDDEN_LOCK_FAIL")
    return c


def artifact_dir() -> Path:
    raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
    if not raw:
        raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED")
    p = Path(raw)
    if not (p / "v164_panel.csv").exists():
        raise RuntimeError("V170B_SOURCE_PANEL_MISSING")
    return p


def build_cot_features() -> pd.DataFrame:
    w = pd.read_csv(COT_SNAPSHOT)
    w["report_date"] = pd.to_datetime(w["report_date"])
    w["available_date"] = pd.to_datetime(w["available_date"])
    numeric = [c for c in w.columns if c not in {"report_date", "available_date"}]
    for col in numeric:
        w[col] = pd.to_numeric(w[col], errors="coerce")
    w = w.sort_values("report_date").reset_index(drop=True)

    w["legacy_nc_net_share"] = (w["legacy_nc_long"] - w["legacy_nc_short"]) / w["legacy_oi"]
    w["legacy_comm_net_share"] = (w["legacy_comm_long"] - w["legacy_comm_short"]) / w["legacy_oi"]
    w["legacy_nc_net_change"] = w["legacy_nc_net_share"].diff()
    w["legacy_oi_log_change"] = np.log(w["legacy_oi"] / w["legacy_oi"].shift(1))
    legacy_hist = w["legacy_nc_net_share"].shift(1)
    legacy_mean = legacy_hist.rolling(52, min_periods=26).mean()
    legacy_std = legacy_hist.rolling(52, min_periods=26).std(ddof=0)
    w["legacy_nc_z52"] = (w["legacy_nc_net_share"] - legacy_mean) / legacy_std.replace(0.0, np.nan)

    w["mm_net_share"] = (w["mm_long"] - w["mm_short"]) / w["disagg_oi"]
    w["prodmerc_net_share"] = (w["prodmerc_long"] - w["prodmerc_short"]) / w["disagg_oi"]
    w["mm_net_change"] = w["mm_net_share"].diff()
    w["disagg_oi_log_change"] = np.log(w["disagg_oi"] / w["disagg_oi"].shift(1))
    mm_hist = w["mm_net_share"].shift(1)
    mm_mean = mm_hist.rolling(52, min_periods=26).mean()
    mm_std = mm_hist.rolling(52, min_periods=26).std(ddof=0)
    w["mm_z52"] = (w["mm_net_share"] - mm_mean) / mm_std.replace(0.0, np.nan)

    keep = [
        "report_date", "available_date",
        "legacy_nc_net_share", "legacy_nc_net_change", "legacy_nc_z52", "legacy_comm_net_share", "legacy_oi_log_change",
        "mm_net_share", "mm_net_change", "mm_z52", "prodmerc_net_share", "disagg_oi_log_change",
    ]
    return w[keep].copy()


def attach_cot(panel: pd.DataFrame, cot: pd.DataFrame) -> pd.DataFrame:
    p = panel.copy().reset_index(drop=True)
    p["date"] = pd.to_datetime(p["date"])
    left = p.sort_values("date")
    right = cot.sort_values("available_date")
    out = pd.merge_asof(left, right, left_on="date", right_on="available_date", direction="backward", allow_exact_matches=True)
    if ((out["available_date"].notna()) & (out["available_date"] > out["date"])).any():
        raise RuntimeError("V170B_COT_FUTURE_JOIN_DETECTED")
    return out.sort_values("date").reset_index(drop=True)


def build_target_panel(panel: pd.DataFrame, horizon: int) -> pd.DataFrame:
    h = int(horizon)
    z = panel.copy().reset_index().rename(columns={"index": "origin_index"})
    z["origin_date"] = pd.to_datetime(z["date"])
    z["target_date"] = pd.to_datetime(z["date"].shift(-h))
    origin_close = pd.to_numeric(z["close"], errors="coerce")
    target_close = pd.to_numeric(z["close"].shift(-h), errors="coerce")
    z["future_log_return"] = np.log(target_close / origin_close)
    z["y"] = (z["future_log_return"] > 0.0).astype(float)
    z = z[z["target_date"].notna() & np.isfinite(z["future_log_return"])].copy()
    z["y"] = z["y"].astype(int)
    z["horizon"] = h
    return z.reset_index(drop=True)


def matured_history(panel: pd.DataFrame, origin_date: pd.Timestamp) -> pd.DataFrame:
    return panel[pd.to_datetime(panel["target_date"]) < origin_date].copy()


def clean_numeric(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    return df[features].apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)


def make_model(c: dict) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
        ("model", LogisticRegression(C=float(c["model_lock"]["C"]), solver=str(c["model_lock"]["solver"]), max_iter=5000, random_state=0)),
    ])


def candidate_features(c: dict) -> dict[str, list[str]]:
    base = list(c["base_features"])
    legacy = list(c["positioning_features"]["LEGACY5"].keys())
    disagg = list(c["positioning_features"]["DISAGG5"].keys())
    return {
        "BASE": base,
        "BASE_PLUS_LEGACY": base + legacy,
        "BASE_PLUS_DISAGG": base + disagg,
        "LEGACY_ONLY": legacy,
        "DISAGG_ONLY": disagg,
    }


def causal_frequency(hist: pd.DataFrame) -> float:
    return 0.5 if len(hist) < 20 else float(hist["y"].mean())


def forecast_origin(panel: pd.DataFrame, row_idx: int, features: list[str], c: dict) -> dict:
    current = panel.loc[[row_idx]].copy()
    origin = pd.Timestamp(current.iloc[0]["origin_date"])
    hist = matured_history(panel, origin).sort_values("origin_date")
    freq = causal_frequency(hist)
    min_n = int(c["model_lock"]["minimum_mature_training_rows"])
    if len(hist) < min_n or hist["y"].nunique() < 2:
        return {"probability": freq, "frequency_probability": freq, "training_n": int(len(hist)), "fallback": True}
    model = make_model(c)
    model.fit(clean_numeric(hist, features), hist["y"].to_numpy(dtype=int))
    p = float(model.predict_proba(clean_numeric(current, features))[:, 1][0])
    return {"probability": p, "frequency_probability": freq, "training_n": int(len(hist)), "fallback": False}


def period_indices(panel: pd.DataFrame, start: str, end: str) -> list[int]:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od = pd.to_datetime(panel["origin_date"])
    td = pd.to_datetime(panel["target_date"])
    return panel.index[(od >= a) & (od <= b) & (td <= b)].tolist()


def generate_predictions(panel: pd.DataFrame, indices: list[int], candidate: str, features: list[str], c: dict, period: str) -> pd.DataFrame:
    rows = []
    for i in indices:
        fc = forecast_origin(panel, i, features, c)
        r = panel.loc[i]
        rows.append({
            "period": period,
            "horizon": int(r["horizon"]),
            "candidate": candidate,
            "origin_index": int(r["origin_index"]),
            "origin_date": pd.Timestamp(r["origin_date"]).strftime("%Y-%m-%d"),
            "target_date": pd.Timestamp(r["target_date"]).strftime("%Y-%m-%d"),
            "cot_report_date": pd.Timestamp(r["report_date"]).strftime("%Y-%m-%d") if pd.notna(r.get("report_date")) else None,
            "cot_available_date": pd.Timestamp(r["available_date"]).strftime("%Y-%m-%d") if pd.notna(r.get("available_date")) else None,
            "y": int(r["y"]),
            "future_log_return": float(r["future_log_return"]),
            **fc,
        })
    return pd.DataFrame(rows)


def metrics(df: pd.DataFrame) -> dict:
    y = df["y"].to_numpy(dtype=int)
    p = np.clip(df["probability"].to_numpy(dtype=float), 1e-6, 1 - 1e-6)
    fq = np.clip(df["frequency_probability"].to_numpy(dtype=float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    brier = float(brier_score_loss(y, p))
    fq_brier = float(brier_score_loss(y, fq))
    ll = float(log_loss(y, p, labels=[0, 1]))
    fq_ll = float(log_loss(y, fq, labels=[0, 1]))
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    ba = float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None
    mcc = float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0
    return {
        "n": int(len(df)),
        "brier": brier,
        "frequency_brier": fq_brier,
        "brier_skill_vs_frequency": float(1.0 - brier / fq_brier) if fq_brier > 0 else None,
        "log_loss": ll,
        "frequency_log_loss": fq_ll,
        "roc_auc": auc,
        "balanced_accuracy": ba,
        "mcc": mcc,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "both_predicted_directions": bool(len(np.unique(pred)) == 2),
        "fallback_rows": int(df["fallback"].sum()),
    }


def candidate_increment(candidate_metrics: dict, base_metrics: dict) -> dict:
    return {
        "absolute_brier_improvement_vs_BASE": float(base_metrics["brier"] - candidate_metrics["brier"]),
        "log_loss_improvement_vs_BASE": float(base_metrics["log_loss"] - candidate_metrics["log_loss"]),
        "roc_auc_difference_vs_BASE": None if candidate_metrics["roc_auc"] is None or base_metrics["roc_auc"] is None else float(candidate_metrics["roc_auc"] - base_metrics["roc_auc"]),
    }


def classify_candidate(candidate: str, horizon_metrics: dict, c: dict) -> dict:
    fcfg = c["incremental_hope_gate"]["formation"]
    bcfg = c["incremental_hope_gate"]["bridge"]
    formation_envs = list(c["temporal_design"]["formation"].keys())
    increments = []
    aucs = []
    for env in formation_envs:
        cm = horizon_metrics[env][candidate]
        bm = horizon_metrics[env]["BASE"]
        increments.append(bm["brier"] - cm["brier"])
        if cm["roc_auc"] is not None:
            aucs.append(cm["roc_auc"])
    formation_pass = bool(
        sum(x > 0.0 for x in increments) >= int(fcfg["positive_absolute_brier_improvement_vs_BASE_environments_min"])
        and float(np.median(increments)) >= float(fcfg["median_absolute_brier_improvement_vs_BASE_min"])
        and len(aucs) == len(formation_envs)
        and float(np.median(aucs)) >= float(fcfg["median_roc_auc_min"])
    )

    cm = horizon_metrics["BRIDGE_2024Q4"][candidate]
    bm = horizon_metrics["BRIDGE_2024Q4"]["BASE"]
    bridge_improvement = bm["brier"] - cm["brier"]
    bridge_pass = bool(
        bridge_improvement >= float(bcfg["absolute_brier_improvement_vs_BASE_min"])
        and cm["brier"] <= cm["frequency_brier"] + 1e-12
        and cm["log_loss"] <= bm["log_loss"] + 1e-12
        and cm["log_loss"] <= cm["frequency_log_loss"] + 1e-12
        and cm["roc_auc"] is not None and cm["roc_auc"] >= float(bcfg["roc_auc_min"])
        and cm["both_predicted_directions"]
    )

    visible = {}
    positive_count = 0
    for period in ["VISIBLE_2025", "VISIBLE_2026_AVAILABLE"]:
        cmv = horizon_metrics[period][candidate]
        bmv = horizon_metrics[period]["BASE"]
        delta = bmv["brier"] - cmv["brier"]
        visible[period] = float(delta)
        positive_count += int(delta > 0.0)

    if formation_pass and bridge_pass and positive_count == 2:
        classification = "ROBUST_HOPE"
    elif formation_pass and bridge_pass and positive_count == 1:
        classification = "WEAK_HOPE"
    else:
        classification = "NO_HOPE"
    return {
        "classification": classification,
        "formation_pass": formation_pass,
        "formation_environment_brier_improvements": [float(x) for x in increments],
        "formation_median_brier_improvement": float(np.median(increments)),
        "formation_median_auc": float(np.median(aucs)) if aucs else None,
        "bridge_pass": bridge_pass,
        "bridge_brier_improvement_vs_BASE": float(bridge_improvement),
        "visible_brier_improvements_vs_BASE": visible,
    }


def main() -> None:
    c = load_contract()
    raw_panel = pd.read_csv(artifact_dir() / "v164_panel.csv")
    required = set(c["base_features"])
    missing = sorted(required - set(raw_panel.columns))
    if missing:
        raise RuntimeError(f"V170B_BASE_FEATURES_MISSING:{missing}")
    cot = build_cot_features()
    panel = attach_cot(raw_panel, cot)
    features = candidate_features(c)
    OUT.mkdir(parents=True, exist_ok=True)

    period_specs = {}
    for name, bounds in c["temporal_design"]["formation"].items():
        period_specs[name] = bounds
    period_specs["BRIDGE_2024Q4"] = c["temporal_design"]["bridge_2024Q4"]
    period_specs["VISIBLE_2025"] = c["temporal_design"]["visible_diagnostics"]["2025"]
    period_specs["VISIBLE_2026_AVAILABLE"] = c["temporal_design"]["visible_diagnostics"]["2026_available"]

    all_predictions = []
    results = {
        "contract_id": c["contract_id"],
        "status": "SUCCESS_RETROSPECTIVE_DIAGNOSTIC_NOT_FRESH_OOS",
        "source_snapshot_sha256": sha256_file(COT_SNAPSHOT),
        "pit_join_violations": 0,
        "horizons": {},
        "governance": c["governance"],
    }

    for h in c["horizons"]:
        tp = build_target_panel(panel, int(h))
        hmetrics = {}
        for period, (start, end) in period_specs.items():
            idx = period_indices(tp, start, end)
            if not idx:
                raise RuntimeError(f"V170B_EMPTY_PERIOD:H{h}:{period}")
            hmetrics[period] = {}
            for candidate, feats in features.items():
                pred = generate_predictions(tp, idx, candidate, feats, c, period)
                all_predictions.append(pred)
                hmetrics[period][candidate] = metrics(pred)
            for candidate in ["BASE_PLUS_LEGACY", "BASE_PLUS_DISAGG", "LEGACY_ONLY", "DISAGG_ONLY"]:
                hmetrics[period][candidate]["incremental_vs_BASE"] = candidate_increment(hmetrics[period][candidate], hmetrics[period]["BASE"])

        classifications = {}
        for candidate in c["incremental_hope_gate"]["eligible_candidates"]:
            classifications[candidate] = classify_candidate(candidate, hmetrics, c)
        results["horizons"][str(h)] = {"period_metrics": hmetrics, "candidate_classification": classifications}

    pred_all = pd.concat(all_predictions, ignore_index=True)
    pd.to_datetime(pred_all["cot_available_date"], errors="coerce")
    violations = pred_all["cot_available_date"].notna() & (pd.to_datetime(pred_all["cot_available_date"]) > pd.to_datetime(pred_all["origin_date"]))
    results["pit_join_violations"] = int(violations.sum())
    if results["pit_join_violations"] != 0:
        raise RuntimeError("V170B_PIT_JOIN_VIOLATION")

    classes_3d = [x["classification"] for x in results["horizons"]["3"]["candidate_classification"].values()]
    classes_1d = [x["classification"] for x in results["horizons"]["1"]["candidate_classification"].values()]
    if "ROBUST_HOPE" in classes_3d:
        overall = "ROBUST_HOPE_PRIMARY_3D"
    elif "WEAK_HOPE" in classes_3d:
        overall = "WEAK_HOPE_PRIMARY_3D"
    elif "ROBUST_HOPE" in classes_1d:
        overall = "ROBUST_HOPE_SECONDARY_1D_ONLY"
    elif "WEAK_HOPE" in classes_1d:
        overall = "WEAK_HOPE_SECONDARY_1D_ONLY"
    else:
        overall = "NO_HOPE_FROM_FREE_COT_POSITIONING_UNDER_FROZEN_GATE"
    results["overall_research_classification"] = overall

    pred_all.to_csv(OUT / "v170b_free_public_positioning_predictions.csv", index=False)
    (OUT / "v170b_free_public_positioning_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
