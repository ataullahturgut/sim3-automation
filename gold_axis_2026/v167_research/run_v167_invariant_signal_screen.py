from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
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
CONTRACT = ROOT / "v167_research/contracts/v167_invariant_signal_screen_freeze_v1.json"
OUT = ROOT / "data_pipeline/audits/v167_research"


def load_contract() -> dict:
    c = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if c["status"] != "FROZEN_BEFORE_ANY_V167_SCORING":
        raise RuntimeError("V167_CONTRACT_NOT_FROZEN")
    if c["governance"]["AUTO_SELECTOR"] != "OFF" or c["governance"]["AUTO_ENSEMBLE"] != "OFF":
        raise RuntimeError("V167_GOVERNANCE_LOCK_FAIL")
    required_forbidden = {
        "FOIL_or_other_deep_invariant_learning",
        "drift_detector",
        "gated_residual_correction",
        "selector_or_CRASE",
        "feature_addition_after_scoring",
        "2025_2026_based_block_selection",
        "production_writes",
    }
    if not required_forbidden.issubset(set(c["forbidden_in_v167"])):
        raise RuntimeError("V167_FORBIDDEN_LOCK_FAIL")
    return c


def artifact_dir() -> Path:
    raw = os.environ.get("V164_ARTIFACT_DIR", "").strip()
    if not raw:
        raise SystemExit("BLOCKED_DATA:V164_ARTIFACT_DIR_REQUIRED")
    p = Path(raw)
    if not (p / "v164_panel.csv").exists():
        raise RuntimeError("V167_SOURCE_PANEL_MISSING")
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


def make_model(features: list[str], contract: dict) -> Pipeline:
    cfg = contract["model_lock"]
    prep = ColumnTransformer(
        [("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]), features)],
        remainder="drop",
    )
    clf = LogisticRegression(
        C=float(cfg["C"]),
        solver=str(cfg["solver"]),
        max_iter=int(cfg["max_iter"]),
        class_weight=cfg["class_weight"],
        random_state=0,
    )
    return Pipeline([("prep", prep), ("clf", clf)])


def causal_frequency(panel: pd.DataFrame, origins: pd.Series, min_support: int = 20) -> np.ndarray:
    # Only targets that have matured strictly before each origin may contribute.
    td = pd.to_datetime(panel["target_date"]).to_numpy(dtype="datetime64[ns]")
    y = panel["y"].to_numpy(dtype=int)
    out = []
    for origin in pd.to_datetime(origins):
        mask = td < np.datetime64(origin.to_datetime64())
        vals = y[mask]
        if len(vals) < min_support:
            out.append(0.5)
        else:
            out.append(float(np.mean(vals)))
    return np.asarray(out, dtype=float)


def metric_bundle(y: np.ndarray, p: np.ndarray, fq: np.ndarray) -> dict:
    y = np.asarray(y, dtype=int)
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    fq = np.clip(np.asarray(fq, dtype=float), 1e-6, 1 - 1e-6)
    pred = (p >= 0.5).astype(int)
    fb = float(brier_score_loss(y, fq))
    b = float(brier_score_loss(y, p))
    fl = float(log_loss(y, fq, labels=[0, 1]))
    ll = float(log_loss(y, p, labels=[0, 1]))
    auc = float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None
    ba = float(balanced_accuracy_score(y, pred)) if len(np.unique(y)) == 2 else None
    mcc = float(matthews_corrcoef(y, pred)) if len(np.unique(y)) == 2 and len(np.unique(pred)) == 2 else 0.0
    return {
        "n": int(len(y)),
        "actual_up": int(y.sum()),
        "actual_down": int((1 - y).sum()),
        "brier": b,
        "frequency_brier": fb,
        "brier_skill_vs_frequency": float(1.0 - b / fb) if fb > 0 else None,
        "log_loss": ll,
        "frequency_log_loss": fl,
        "log_loss_improvement_vs_frequency": float(fl - ll),
        "roc_auc": auc,
        "balanced_accuracy": ba,
        "mcc": mcc,
        "up_predictions": int(pred.sum()),
        "down_predictions": int((1 - pred).sum()),
        "both_predicted_directions": bool(len(np.unique(pred)) == 2),
        "mean_probability": float(np.mean(p)),
        "mean_frequency_probability": float(np.mean(fq)),
    }


def slice_period(panel: pd.DataFrame, start: str, end: str, require_target_inside: bool = True) -> pd.DataFrame:
    a, b = pd.Timestamp(start), pd.Timestamp(end)
    od = pd.to_datetime(panel["origin_date"])
    td = pd.to_datetime(panel["target_date"])
    mask = (od >= a) & (od <= b)
    if require_target_inside:
        mask &= td <= b
    return panel.loc[mask].copy()


def extract_standardized_coefficients(model: Pipeline, features: list[str]) -> np.ndarray:
    return np.asarray(model.named_steps["clf"].coef_[0], dtype=float)


def forward_screen(panel: pd.DataFrame, contract: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    rows: list[dict] = []
    coef_rows: list[dict] = []
    envs = contract["chronological_environment_design"]["forward_tests"]

    for block, features in contract["feature_blocks"].items():
        for env_name, (start, end) in envs.items():
            start_ts = pd.Timestamp(start)
            train = panel[(panel["origin_date"] < start_ts) & (panel["target_date"] < start_ts)].copy()
            test = slice_period(panel, start, end, require_target_inside=True)
            if len(train) < 30 or len(test) < 10:
                raise RuntimeError(f"V167_SUPPORT_TOO_SMALL:{block}:{env_name}:{len(train)}:{len(test)}")
            if train["y"].nunique() < 2 or test["y"].nunique() < 2:
                raise RuntimeError(f"V167_CLASS_SUPPORT_FAIL:{block}:{env_name}")

            model = make_model(features, contract)
            model.fit(train[features], train["y"].to_numpy(dtype=int))
            p = model.predict_proba(test[features])[:, 1]
            fq = causal_frequency(panel, test["origin_date"])
            metrics = metric_bundle(test["y"].to_numpy(dtype=int), p, fq)
            rows.append({"block": block, "environment": env_name, **metrics})

            coefs = extract_standardized_coefficients(model, features)
            for feature, coef in zip(features, coefs):
                coef_rows.append({
                    "block": block,
                    "environment": env_name,
                    "feature": feature,
                    "standardized_coefficient": float(coef),
                    "coefficient_sign": int(np.sign(coef)),
                })

    scores = pd.DataFrame(rows)
    coefs = pd.DataFrame(coef_rows)
    gate = contract["block_eligibility_gate"]
    eligibility: dict[str, dict] = {}
    for block, g in scores.groupby("block", sort=True):
        bss = g["brier_skill_vs_frequency"].astype(float)
        aucs = g["roc_auc"].astype(float)
        eligible = bool(
            int((bss > 0.0).sum()) >= int(gate["positive_brier_skill_environments_min"])
            and float(bss.min()) >= float(gate["worst_environment_brier_skill_min"])
            and float(aucs.median()) >= float(gate["median_auc_min"])
            and float(aucs.min()) >= float(gate["minimum_environment_auc"])
        )
        eligibility[block] = {
            "eligible": eligible,
            "positive_brier_skill_environments": int((bss > 0.0).sum()),
            "worst_environment_brier_skill": float(bss.min()),
            "median_auc": float(aucs.median()),
            "minimum_auc": float(aucs.min()),
        }
    return scores, coefs, eligibility


def choose_eligible_blocks(eligibility: dict) -> tuple[list[str], str | None]:
    eligible = [b for b, d in eligibility.items() if d["eligible"]]
    eligible.sort()
    if not eligible:
        return [], None
    best = sorted(
        eligible,
        key=lambda b: (
            -float(eligibility[b]["worst_environment_brier_skill"]),
            -float(eligibility[b]["median_auc"]),
            b,
        ),
    )[0]
    return eligible, best


def fit_final_block_models(panel: pd.DataFrame, eligible: list[str], contract: dict) -> dict[str, Pipeline]:
    cutoff = pd.Timestamp("2024-09-25")
    train = panel[(panel["origin_date"] <= cutoff) & (panel["target_date"] <= cutoff)].copy()
    models: dict[str, Pipeline] = {}
    for block in eligible:
        features = contract["feature_blocks"][block]
        model = make_model(features, contract)
        model.fit(train[features], train["y"].to_numpy(dtype=int))
        models[block] = model
    return models


def candidate_probs(models: dict[str, Pipeline], panel_slice: pd.DataFrame, contract: dict, best_block: str) -> dict[str, np.ndarray]:
    block_probs = {
        b: m.predict_proba(panel_slice[contract["feature_blocks"][b]])[:, 1]
        for b, m in models.items()
    }
    best = block_probs[best_block]
    avg = np.mean(np.column_stack([block_probs[b] for b in sorted(block_probs)]), axis=1)
    return {"BEST_STABLE_BLOCK": best, "STABLE_EQUAL_AVG": avg, **{f"BLOCK_{b}": p for b, p in block_probs.items()}}


def bridge_pass(metrics: dict, contract: dict) -> bool:
    g = contract["bridge_gate"]["requirements_for_promising_candidate"]
    return bool(
        metrics["brier"] <= metrics["frequency_brier"] + 1e-12
        and metrics["log_loss"] <= metrics["frequency_log_loss"] + 1e-12
        and metrics["roc_auc"] is not None
        and metrics["roc_auc"] >= float(g["roc_auc_min"])
        and metrics["both_predicted_directions"]
    )


def visible_persistence_pass(period_metrics: dict[str, dict], contract: dict) -> bool:
    g = contract["visible_period_success_gate"]
    auc_min = float(g["2025_and_2026_auc_min"])
    for period in ["2025", "2026_available"]:
        m = period_metrics[period]
        if not (
            m["brier"] <= m["frequency_brier"] + 1e-12
            and m["roc_auc"] is not None
            and m["roc_auc"] >= auc_min
            and m["both_predicted_directions"]
        ):
            return False
    return True


def run() -> None:
    c = load_contract()
    art = artifact_dir()
    panel = build_target_panel(pd.read_csv(art / c["source_artifact"]["required_file"]))
    panel["origin_date"] = pd.to_datetime(panel["origin_date"])
    panel["target_date"] = pd.to_datetime(panel["target_date"])

    missing = sorted({f for fs in c["feature_blocks"].values() for f in fs if f not in panel.columns})
    if missing:
        raise RuntimeError(f"V167_FEATURES_MISSING:{missing}")

    scores, coefs, eligibility = forward_screen(panel, c)
    eligible, best_block = choose_eligible_blocks(eligibility)

    OUT.mkdir(parents=True, exist_ok=True)
    scores.to_csv(OUT / "v167_forward_environment_block_scores.csv", index=False)
    coefs.to_csv(OUT / "v167_forward_environment_coefficients.csv", index=False)

    result: dict = {
        "contract_id": c["contract_id"],
        "evidence_class": c["evidence_class"],
        "eligible_blocks": eligible,
        "best_stable_block": best_block,
        "block_eligibility": eligibility,
        "candidate_period_scores": {},
        "bridge_pass": {},
        "visible_persistence_pass": {},
        "decision": None,
    }

    prediction_rows: list[pd.DataFrame] = []
    if not eligible:
        result["decision"] = "NO_ELIGIBLE_STABLE_BLOCK__REJECT_CURRENT_INVARIANT_SIGNAL_HYPOTHESIS"
    else:
        models = fit_final_block_models(panel, eligible, c)
        periods = {
            "2024Q4_bridge": c["chronological_environment_design"]["bridge_2024Q4"],
            **c["chronological_environment_design"]["visible_diagnostic_periods"],
        }
        candidate_period_scores: dict[str, dict[str, dict]] = {}
        for period_name, (start, end) in periods.items():
            d = slice_period(panel, start, end, require_target_inside=True)
            fq = causal_frequency(panel, d["origin_date"])
            cp = candidate_probs(models, d, c, best_block)
            candidate_period_scores[period_name] = {}
            for cand, probs in cp.items():
                m = metric_bundle(d["y"].to_numpy(dtype=int), probs, fq)
                candidate_period_scores[period_name][cand] = m
                prediction_rows.append(pd.DataFrame({
                    "period": period_name,
                    "candidate": cand,
                    "origin_index": d["origin_index"].to_numpy(),
                    "origin_date": d["origin_date"].dt.strftime("%Y-%m-%d").to_numpy(),
                    "target_date": d["target_date"].dt.strftime("%Y-%m-%d").to_numpy(),
                    "y": d["y"].to_numpy(dtype=int),
                    "probability": probs,
                    "causal_frequency": fq,
                }))

        result["candidate_period_scores"] = candidate_period_scores
        for cand in ["BEST_STABLE_BLOCK", "STABLE_EQUAL_AVG"]:
            bp = bridge_pass(candidate_period_scores["2024Q4_bridge"][cand], c)
            result["bridge_pass"][cand] = bp
            visible = {
                "2025": candidate_period_scores["2025"][cand],
                "2026_available": candidate_period_scores["2026_available"][cand],
            }
            result["visible_persistence_pass"][cand] = visible_persistence_pass(visible, c)

        if any(result["bridge_pass"].values()) and any(result["visible_persistence_pass"].values()):
            result["decision"] = "PROMISING_INVARIANT_SIGNAL_CANDIDATE__PROSPECTIVE_SHADOW_REQUIRED"
        elif any(result["bridge_pass"].values()):
            result["decision"] = "BRIDGE_PASS_VISIBLE_PERSISTENCE_FAIL__TEMPORAL_INVARIANCE_INSUFFICIENT"
        else:
            result["decision"] = "ELIGIBLE_FORMATION_BLOCKS_BUT_BRIDGE_FAIL__DO_NOT_ESCALATE_INVARIANT_LEARNER"

    if prediction_rows:
        pd.concat(prediction_rows, ignore_index=True).to_csv(OUT / "v167_candidate_predictions.csv", index=False)

    (OUT / "v167_invariant_signal_screen_results.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
