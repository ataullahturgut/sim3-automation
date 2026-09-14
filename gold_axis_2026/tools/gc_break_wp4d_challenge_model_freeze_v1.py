from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "gc_break_v0" / "gc_break_wp4d_integrated_role_transition_prereg_v1.json"
CHALLENGE_PROTOCOL = ROOT / "gc_break_v0" / "gc_break_wp4d_2025_challenge_protocol_v1.json"

M1_FEATURES = [
    "log1p_regime_sojourn_age",
    "fast_opposite_at_episode_start",
]
M2_FEATURES = [
    "log1p_regime_sojourn_age",
    "fast_opposite_at_episode_start",
    "monthly_direction_conflict_at_episode_start",
    "bocpd_downside_adverse_context_at_episode_start",
    "macro_break_pressure_at_episode_start",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_contracts() -> tuple[dict, dict]:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    challenge = json.loads(CHALLENGE_PROTOCOL.read_text(encoding="utf-8"))
    if prereg.get("status") != "FROZEN_BEFORE_WP4D_FORMATION_SCORING":
        raise RuntimeError("WP4D_PREREG_NOT_FROZEN")
    if challenge.get("status") != "FROZEN_BEFORE_2025_CHALLENGE_SCORING":
        raise RuntimeError("WP4D_CHALLENGE_PROTOCOL_NOT_FROZEN")
    if challenge.get("architecture_contract") != prereg.get("contract_id"):
        raise RuntimeError("WP4D_CHALLENGE_PROTOCOL_ARCH_MISMATCH")
    return prereg, challenge


def fit_fixed_logit(d: pd.DataFrame, features: list[str], c_value: float) -> dict:
    X = d[features].astype(float).to_numpy()
    y = d["outcome_break"].astype(int).to_numpy()
    if len(np.unique(y)) != 2:
        raise RuntimeError("WP4D_FINAL_FIT_SINGLE_CLASS")
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = LogisticRegression(
        penalty="l2",
        C=c_value,
        solver="liblinear",
        class_weight=None,
        fit_intercept=True,
        max_iter=1000,
        random_state=0,
    )
    model.fit(Xs, y)
    return {
        "features": features,
        "standardizer_mean": [float(v) for v in scaler.mean_],
        "standardizer_scale": [float(v) for v in scaler.scale_],
        "coef_standardized": [float(v) for v in model.coef_[0]],
        "intercept": float(model.intercept_[0]),
        "C": float(c_value),
        "solver": "liblinear",
        "class_weight": None,
        "fit_intercept": True,
        "max_iter": 1000,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--formation-summary", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    prereg, protocol = load_contracts()
    summary = json.loads(args.formation_summary.read_text(encoding="utf-8"))
    if summary.get("status") != "FORMATION_SUPPORT_CHALLENGE_REQUIRED":
        raise RuntimeError(f"WP4D_FORMATION_NOT_PASSED:{summary.get('status')}")
    if summary.get("challenge_2025_accessed") is not False or summary.get("stress_2026_accessed") is not False:
        raise RuntimeError("WP4D_FORMATION_CONTAMINATION_GUARD_FAIL")
    if summary.get("post_score_tuning") is not False:
        raise RuntimeError("WP4D_POST_SCORE_TUNING_GUARD_FAIL")

    d = pd.read_csv(args.episodes)
    required = {"outcome_break", "core_eligible", *M2_FEATURES}
    missing = sorted(required - set(d.columns))
    if missing:
        raise RuntimeError(f"WP4D_FREEZE_EPISODE_SCHEMA_MISSING:{missing}")
    core = d[d["core_eligible"].astype(str).str.lower().eq("true")].copy()
    if len(core) != 35:
        raise RuntimeError(f"WP4D_FINAL_FIT_EPISODE_COUNT_FAIL:{len(core)}")
    breaks = int(core["outcome_break"].astype(int).sum())
    recoveries = int(len(core) - breaks)
    if (breaks, recoveries) != (13, 22):
        raise RuntimeError(f"WP4D_FINAL_FIT_CLASS_COUNTS_FAIL:{breaks}:{recoveries}")
    if core[M2_FEATURES].isna().any().any():
        raise RuntimeError("WP4D_FINAL_FIT_MISSING_CORE_FEATURE")

    c_value = float(protocol["frozen_final_fit"]["C"])
    m0 = float((breaks + 0.5) / (len(core) + 1.0))
    if abs(m0 - 0.375) > 1e-12:
        raise RuntimeError(f"WP4D_M0_PRIOR_UNEXPECTED:{m0}")
    m1 = fit_fixed_logit(core, M1_FEATURES, c_value)
    m2 = fit_fixed_logit(core, M2_FEATURES, c_value)

    freeze = {
        "freeze_id": "GC_BREAK_WP4D_CHALLENGE_MODEL_FREEZE_V1",
        "status": "FROZEN_BEFORE_2025_CHALLENGE_SCORING",
        "architecture_contract": prereg["contract_id"],
        "challenge_protocol": protocol["protocol_id"],
        "formation_only": True,
        "formation_window": prereg["formation_window"],
        "fit_support": {
            "terminal_core_eligible_episodes": int(len(core)),
            "break_conversions": breaks,
            "recoveries": recoveries,
        },
        "M0_EPISODE_EMPIRICAL_PRIOR": {
            "probability": m0,
            "formula": "(break_conversions+0.5)/(completed_episodes+1.0)",
        },
        "M1_TACTICAL_DURATION_RIDGE": m1,
        "M2_INTEGRATED_ROLE_CORE_RIDGE": m2,
        "extension_locks": {
            "E1_MONTHLY_H1_STRATEGIC_CONTEXT": "EXCLUDED_FROM_CHALLENGE_PROBABILITY_AFTER_FAILED_FORMATION_INCREMENTAL_GATE",
            "E2_EMERGENCY_CONTEXT": "EXCLUDED_FROM_CHALLENGE_PROBABILITY_AFTER_FAILED_FORMATION_INCREMENTAL_GATE",
            "E3_GVZ_RISK": "NOT_TESTABLE_FORMATION_PIT_NOT_PROVEN",
            "SLOW": "POST_BREAK_CONFIRMATION_NEW_REGIME_ONLY",
        },
        "structural_health_probability_feature": False,
        "path_half_or_adverse_fraction_probability_feature": False,
        "hyperparameter_search": False,
        "threshold_search": False,
        "challenge_data_accessed": False,
        "stress_2026_accessed": False,
        "database_write": "NONE",
        "production_authority": False,
        "prospective_claim": False,
        "formation_episode_file_sha256": sha256_file(args.episodes),
        "formation_summary_file_sha256": sha256_file(args.formation_summary),
    }
    out = args.output_dir / "gc_break_wp4d_challenge_model_freeze_v1.json"
    out.write_text(json.dumps(freeze, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(freeze, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
