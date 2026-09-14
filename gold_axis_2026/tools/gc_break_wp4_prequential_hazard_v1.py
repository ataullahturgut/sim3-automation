from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "gc_break_v0" / "gc_break_wp4_hazard_prereg_v1.json").exists():
            return parent
    raise RuntimeError("PROJECT_ROOT_NOT_FOUND")


def as_bool(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    bad = ~s.isin(["true", "false"])
    if bad.any():
        raise RuntimeError(f"BOOLEAN_PARSE_FAIL:{series.name}:{sorted(s[bad].unique())[:10]}")
    return s.eq("true")


def same_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_UP")) | ((regime == "DOWN") & (state == "ROBUST_DOWN"))


def opposite_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_DOWN")) | ((regime == "DOWN") & (state == "ROBUST_UP"))


def metric_block(y: np.ndarray, prob: np.ndarray) -> dict:
    if len(y) == 0:
        raise RuntimeError("EMPTY_EVALUATION_SET")
    if not np.isfinite(prob).all() or ((prob <= 0) | (prob >= 1)).any():
        raise RuntimeError("INVALID_PROBABILITY")
    y_int = y.astype(int)
    return {
        "evaluation_origins": int(len(y_int)),
        "break_events": int(y_int.sum()),
        "brier_score": float(brier_score_loss(y_int, prob)),
        "log_loss": float(log_loss(y_int, prob, labels=[0, 1])),
        "average_precision": float(average_precision_score(y_int, prob)) if y_int.sum() else None,
        "roc_auc": float(roc_auc_score(y_int, prob)) if len(np.unique(y_int)) == 2 else None,
        "mean_predicted_hazard": float(np.mean(prob)),
        "observed_break_rate": float(np.mean(y_int)),
    }


def make_pipeline(model_contract: dict) -> Pipeline:
    if model_contract.get("estimator") != "L2 logistic regression":
        raise RuntimeError(f"ESTIMATOR_CONTRACT_FAIL:{model_contract.get('id')}")
    if model_contract.get("solver") != "liblinear" or float(model_contract.get("C")) != 1.0:
        raise RuntimeError(f"HYPERPARAMETER_CONTRACT_FAIL:{model_contract.get('id')}")
    if model_contract.get("class_weight") is not None:
        raise RuntimeError(f"CLASS_WEIGHT_CONTRACT_FAIL:{model_contract.get('id')}")
    return Pipeline([
        ("scale", StandardScaler()),
        ("logit", LogisticRegression(
            penalty="l2",
            C=1.0,
            solver="liblinear",
            class_weight=None,
            max_iter=1000,
            random_state=0,
        )),
    ])


def build_risk_intervals(panel: pd.DataFrame) -> pd.DataFrame:
    required = {
        "date", "regime_post", "wp2_break_flag", "fast_state", "slow_state",
        "fast_state_age", "slow_state_age", "adverse_fraction",
    }
    if not required <= set(panel.columns):
        raise RuntimeError(f"PANEL_COLUMNS_MISSING:{sorted(required-set(panel.columns))}")

    p = panel.copy()
    p["date"] = pd.to_datetime(p["date"]).dt.normalize()
    p = p.sort_values("date").reset_index(drop=True)
    if p["date"].duplicated().any():
        raise RuntimeError("DUPLICATE_PANEL_DATE")
    if p["date"].min() < pd.Timestamp("2022-01-01") or p["date"].max() > pd.Timestamp("2024-12-31"):
        raise RuntimeError("FORMATION_BOUNDARY_FAIL")
    if len(p) != 351:
        raise RuntimeError(f"FORMATION_ORIGIN_COUNT_FAIL:{len(p)}")

    p["break_now"] = as_bool(p["wp2_break_flag"])
    if int(p["break_now"].sum()) != 21:
        raise RuntimeError(f"FORMATION_BREAK_COUNT_FAIL:{int(p['break_now'].sum())}")
    if not p["regime_post"].isin(["UP", "DOWN"]).all():
        raise RuntimeError("REGIME_POST_INVALID")

    for col in ["fast_state_age", "slow_state_age"]:
        p[col] = pd.to_numeric(p[col], errors="raise")
        if p[col].isna().any() or (p[col] < 0).any():
            raise RuntimeError(f"STATE_AGE_INVALID:{col}")

    p["fast_conflict_post"] = ~same_robust(p["fast_state"], p["regime_post"])
    p["fast_opposite_post"] = opposite_robust(p["fast_state"], p["regime_post"])
    p["slow_conflict_post"] = ~same_robust(p["slow_state"], p["regime_post"])
    p["log1p_fast_state_age"] = np.log1p(p["fast_state_age"].astype(float))
    p["log1p_slow_state_age"] = np.log1p(p["slow_state_age"].astype(float))

    raw_adv = pd.to_numeric(p["adverse_fraction"], errors="coerce")
    non_break = ~p["break_now"]
    if raw_adv[non_break].isna().any():
        raise RuntimeError("ADVERSE_FRACTION_MISSING_NONBREAK")
    if (raw_adv[non_break] < -1e-10).any() or (raw_adv[non_break] >= 1.0 + 1e-8).any():
        bad = p.loc[non_break & ((raw_adv < -1e-10) | (raw_adv >= 1.0 + 1e-8)), ["date", "adverse_fraction"]]
        raise RuntimeError(f"ADVERSE_FRACTION_NONBREAK_RANGE_FAIL:{bad.head().to_dict(orient='records')}")
    p["adverse_fraction_post"] = raw_adv.clip(lower=0.0, upper=1.0)
    p.loc[p["break_now"], "adverse_fraction_post"] = 0.0

    first_break_i = int(np.flatnonzero(p["break_now"].to_numpy())[0])
    ages = np.full(len(p), np.nan)
    age = None
    for i in range(first_break_i, len(p)):
        if bool(p.at[i, "break_now"]):
            age = 0
        elif age is not None:
            age += 1
        ages[i] = age if age is not None else np.nan
    p["sojourn_age"] = ages
    p["log1p_sojourn_age"] = np.log1p(p["sojourn_age"])

    # A risk row at origin t predicts whether the next governed origin t+1 is a break.
    p["interval_end_date"] = p["date"].shift(-1)
    p["y_next_break"] = p["break_now"].shift(-1)
    risk = p.iloc[first_break_i:-1].copy().reset_index(drop=True)
    if risk["sojourn_age"].isna().any() or risk["y_next_break"].isna().any():
        raise RuntimeError("RISK_SET_CAUSAL_AGE_OR_TARGET_MISSING")
    risk["y_next_break"] = risk["y_next_break"].astype(bool).astype(int)
    risk["origin_position_in_formation"] = np.arange(first_break_i, len(p)-1)
    risk["risk_interval_calendar_days"] = (risk["interval_end_date"] - risk["date"]).dt.days
    # This gap is retained for audit only and is explicitly forbidden as a model feature.
    if (risk["risk_interval_calendar_days"] <= 0).any():
        raise RuntimeError("NONPOSITIVE_INTERVAL_GAP")
    return risk


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wp3-panel", type=Path, required=True)
    ap.add_argument("--wp3-summary", type=Path, required=True)
    ap.add_argument("--wp3-closure", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)

    root = project_root()
    contract = json.loads((root / "gc_break_v0" / "gc_break_wp4_hazard_prereg_v1.json").read_text(encoding="utf-8"))
    if contract.get("contract_id") != "GC_BREAK_WP4_HAZARD_PREREG_V1" or contract.get("status") != "FROZEN_BEFORE_WP4_FORMATION_SCORING":
        raise RuntimeError("WP4_CONTRACT_NOT_FROZEN")
    gov = contract.get("governance", {})
    required_true = [
        "no_random_split", "no_hindsight_threshold_tuning", "no_2025_challenge_access",
        "no_2026_stress_access", "no_database_writes", "no_position_mapping",
        "no_production_promotion", "retain_wp2_data_density_warning",
    ]
    if not all(gov.get(k) is True for k in required_true):
        raise RuntimeError("WP4_GOVERNANCE_GUARD_FAIL")
    if gov.get("auto_selector") != "OFF" or gov.get("auto_ensemble") != "OFF":
        raise RuntimeError("WP4_AUTO_GUARD_FAIL")
    protocol = contract["prequential_protocol"]
    if protocol.get("random_split") is not False or protocol.get("hyperparameter_search") is not False or protocol.get("threshold_search") is not False:
        raise RuntimeError("WP4_PREQUENTIAL_PROTOCOL_GUARD_FAIL")

    wp3 = json.loads(a.wp3_summary.read_text(encoding="utf-8"))
    closure = json.loads(a.wp3_closure.read_text(encoding="utf-8"))
    if wp3.get("audit_id") != "GC_BREAK_WP3_CURRENT_FORMATION_BASELINES_V1":
        raise RuntimeError("WP3_SUMMARY_ID_FAIL")
    if closure.get("audit_id") != "GC_BREAK_WP3_CLOSURE_REVIEW_V1" or closure.get("status") != "COMPLETE_WITH_LIMITATIONS_READY_FOR_WP4":
        raise RuntimeError("WP3_CLOSURE_GATE_FAIL")
    if closure.get("wp4_entry_guard") != "BEGIN_SIMPLE_ROLE_PRESERVING_SEQUENTIAL_HAZARD_OR_STATE_TRANSITION_ONLY":
        raise RuntimeError("WP3_WP4_ENTRY_GUARD_FAIL")
    if closure.get("no_threshold_retuning") is not True or closure.get("no_2025_2026_selection") is not True:
        raise RuntimeError("WP3_CONTAMINATION_GUARD_FAIL")

    panel = pd.read_csv(a.wp3_panel)
    risk = build_risk_intervals(panel)

    models = {m["id"]: m for m in contract["models"]}
    expected_models = ["M0_EMPIRICAL_HAZARD", "M1_FAST_DURATION_RIDGE", "M2_ROLE_CORE_RIDGE", "M3_PATH_AUGMENTED_SENSITIVITY"]
    if list(models) != expected_models:
        raise RuntimeError(f"WP4_MODEL_SET_MISMATCH:{list(models)}")
    for mid in expected_models[1:]:
        if "risk_interval_calendar_days" in models[mid]["features"]:
            raise RuntimeError("FUTURE_GAP_FEATURE_FORBIDDEN")
        missing = set(models[mid]["features"]) - set(risk.columns)
        if missing:
            raise RuntimeError(f"MODEL_FEATURES_MISSING:{mid}:{sorted(missing)}")
        x = risk[models[mid]["features"]].apply(pd.to_numeric, errors="raise")
        if x.isna().any().any() or not np.isfinite(x.to_numpy(float)).all():
            raise RuntimeError(f"MODEL_FEATURE_NONFINITE:{mid}")

    min_n = int(protocol["minimum_past_intervals"])
    min_e = int(protocol["minimum_past_break_events"])
    records = []
    coef_records = []
    for i in range(len(risk)):
        train = risk.iloc[:i]
        if len(train) < min_n or int(train["y_next_break"].sum()) < min_e:
            continue
        current = risk.iloc[[i]]
        y_train = train["y_next_break"].to_numpy(int)
        if len(np.unique(y_train)) != 2:
            raise RuntimeError("TRAINING_CLASS_DEGENERACY_AFTER_GATE")

        rec = {
            "origin_date": current.iloc[0]["date"],
            "interval_end_date": current.iloc[0]["interval_end_date"],
            "origin_position_in_formation": int(current.iloc[0]["origin_position_in_formation"]),
            "training_intervals": int(len(train)),
            "training_break_events": int(y_train.sum()),
            "y_next_break": int(current.iloc[0]["y_next_break"]),
            "risk_interval_calendar_days_audit_only": int(current.iloc[0]["risk_interval_calendar_days"]),
        }
        p0 = float((y_train.sum() + 0.5) / (len(y_train) + 1.0))
        if not 0 < p0 < 1:
            raise RuntimeError("M0_PROBABILITY_FAIL")
        rec["p_M0_EMPIRICAL_HAZARD"] = p0

        for mid in expected_models[1:]:
            feats = models[mid]["features"]
            pipe = make_pipeline(models[mid])
            x_train = train[feats].astype(float)
            x_now = current[feats].astype(float)
            pipe.fit(x_train, y_train)
            prob = float(pipe.predict_proba(x_now)[0, 1])
            if not 0 < prob < 1:
                raise RuntimeError(f"MODEL_PROBABILITY_FAIL:{mid}:{prob}")
            rec[f"p_{mid}"] = prob
            coef = pipe.named_steps["logit"].coef_[0]
            coef_records.append({
                "origin_date": current.iloc[0]["date"],
                "model_id": mid,
                "training_intervals": len(train),
                "training_break_events": int(y_train.sum()),
                "intercept_standardized": float(pipe.named_steps["logit"].intercept_[0]),
                **{f"coef_{f}": float(c) for f, c in zip(feats, coef)},
            })
        records.append(rec)

    pred = pd.DataFrame(records)
    if pred.empty:
        raise RuntimeError("NO_PREQUENTIAL_EVALUATION_ORIGINS")
    prob_cols = [f"p_{m}" for m in expected_models]
    if pred[prob_cols].isna().any().any():
        raise RuntimeError("MODEL_EVALUATION_ORIGIN_MISMATCH")
    if pred["origin_date"].min() < pd.Timestamp("2022-01-01") or pred["interval_end_date"].max() > pd.Timestamp("2024-12-31"):
        raise RuntimeError("EVALUATION_LEFT_FORMATION_WINDOW")

    y = pred["y_next_break"].to_numpy(int)
    metrics = []
    for mid in expected_models:
        mb = metric_block(y, pred[f"p_{mid}"].to_numpy(float))
        mb["model_id"] = mid
        mb["role"] = models[mid]["role"]
        mb["primary_promotion_evidence"] = bool(models[mid].get("primary_promotion_evidence", mid != "M3_PATH_AUGMENTED_SENSITIVITY"))
        metrics.append(mb)
    metrics_df = pd.DataFrame(metrics)
    by_id = metrics_df.set_index("model_id")
    m0 = by_id.loc["M0_EMPIRICAL_HAZARD"]
    decision_detail = {}
    for mid in expected_models[1:]:
        r = by_id.loc[mid]
        decision_detail[mid] = {
            "delta_brier_vs_M0": float(r["brier_score"] - m0["brier_score"]),
            "delta_log_loss_vs_M0": float(r["log_loss"] - m0["log_loss"]),
            "improves_brier_vs_M0": bool(r["brier_score"] < m0["brier_score"]),
            "improves_log_loss_vs_M0": bool(r["log_loss"] < m0["log_loss"]),
        }
    m2_positive = decision_detail["M2_ROLE_CORE_RIDGE"]["improves_brier_vs_M0"] and decision_detail["M2_ROLE_CORE_RIDGE"]["improves_log_loss_vs_M0"]
    m1_positive = decision_detail["M1_FAST_DURATION_RIDGE"]["improves_brier_vs_M0"] and decision_detail["M1_FAST_DURATION_RIDGE"]["improves_log_loss_vs_M0"]
    if m2_positive:
        phase_status = "M2_POSITIVE_PROBABILITY_SIGNAL"
    elif m1_positive:
        phase_status = "M1_ONLY_POSITIVE_PROBABILITY_SIGNAL"
    else:
        phase_status = "REJECT_LEARNED_HAZARD"

    metrics_df.to_csv(a.output_dir / "gc_break_wp4_prequential_hazard_metrics_v1.csv", index=False)
    pred.to_csv(a.output_dir / "gc_break_wp4_prequential_hazard_predictions_v1.csv", index=False)
    pd.DataFrame(coef_records).to_csv(a.output_dir / "gc_break_wp4_prequential_hazard_coefficients_v1.csv", index=False)
    risk.to_csv(a.output_dir / "gc_break_wp4_prequential_hazard_risk_set_v1.csv", index=False)

    summary = {
        "audit_id": "GC_BREAK_WP4_PREQUENTIAL_HAZARD_PHASE_A_V1",
        "status": "EVIDENCE_GENERATED_NOT_YET_CLOSED",
        "phase_a_status": phase_status,
        "contract_id": contract["contract_id"],
        "contract_status": contract["status"],
        "formation_interpretation": "FORMATION_DEVELOPMENT_PREQUENTIAL_NOT_CHALLENGE",
        "risk_interval_unit": contract["risk_interval"]["unit"],
        "calendar_day_horizon_claim": False,
        "formation_origins": int(len(panel)),
        "formation_break_events": 21,
        "risk_set_intervals_after_left_censor_guard": int(len(risk)),
        "evaluation_origins": int(len(pred)),
        "evaluation_break_events": int(y.sum()),
        "first_evaluation_origin": pd.Timestamp(pred["origin_date"].min()).date().isoformat(),
        "last_evaluation_origin": pd.Timestamp(pred["origin_date"].max()).date().isoformat(),
        "metrics": metrics_df.replace({np.nan: None}).set_index("model_id").to_dict(orient="index"),
        "decision_detail": decision_detail,
        "decision_rule_applied_without_threshold_search": True,
        "state_threshold_mapping_performed": False,
        "hyperparameter_search_performed": False,
        "random_split_used": False,
        "challenge_2025_accessed": False,
        "stress_2026_accessed": False,
        "database_write": "NONE",
        "production_authority": False,
        "prospective_claim": False,
        "wp2_data_density_warning_retained": True,
        "data_density_note": "Predictions are per governed-origin interval. Calendar gaps are audit-only and are not model features.",
        "next_gate": "Inspect Phase A evidence under manifest v1.51 and frozen preregistration. Do not create WEAKENING/BREAK_ALERT probability thresholds before this review."
    }
    (a.output_dir / "gc_break_wp4_prequential_hazard_phase_a_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
