from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--challenge-summary", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    d = json.loads(args.challenge_summary.read_text(encoding="utf-8"))
    checks = {
        "challenge_status_is_frozen_rejection": d.get("status") == "REJECT_CHALLENGE_TRANSPORT_FAILURE",
        "support_gate_passed": d.get("support_gate_pass") is True,
        "probability_gate_failed": d.get("probability_gate", {}).get("passed") is False,
        "monitoring_gate_failed": d.get("monitoring", {}).get("gate", {}).get("passed") is False,
        "M2_did_improve_null_both": d.get("probability_gate", {}).get("M2_strictly_improves_M0_brier_and_logloss") is True,
        "M2_failed_minimal_comparator_gate": d.get("probability_gate", {}).get("M2_no_worse_M1_both_and_strictly_improves_at_least_one") is False,
        "dual_recall_improved_or_equal": d.get("monitoring", {}).get("gate", {}).get("dual_recall_at_least_fast") is True,
        "dual_false_burden_within_ceiling": d.get("monitoring", {}).get("gate", {}).get("dual_false_burden_within_ceiling") is True,
        "dual_lead_gate_failed": d.get("monitoring", {}).get("gate", {}).get("dual_lead_strictly_greater_fast") is False,
        "no_challenge_refit": d.get("challenge_refit") is False,
        "no_hyperparameter_search": d.get("hyperparameter_search") is False,
        "no_threshold_search": d.get("threshold_search") is False,
        "no_post_challenge_tuning": d.get("post_challenge_tuning") is False,
        "no_2026_selection": d.get("stress_2026_accessed") is False,
        "no_db_write": d.get("database_write") == "NONE",
        "all_12_accounted": d.get("all_12_governed_identities_accounted_for") is True,
        "path_not_probability_feature": d.get("path_half_or_adverse_fraction_probability_feature") is False,
        "not_production": d.get("production_authority") is False,
        "not_prospective": d.get("prospective_claim") is False,
    }
    if not all(checks.values()):
        failed = [k for k, v in checks.items() if not v]
        raise RuntimeError(f"WP4D_CLOSURE_CHECK_FAIL:{failed}")

    m = d["probability_metrics"]
    fast = d["monitoring"]["FAST_CONFLICT"]
    dual = d["monitoring"]["INTEGRATED_DUAL_LANE_PATH_HALF_OR_FAST_CONFLICT"]
    closure = {
        "audit_id": "GC_BREAK_WP4D_CLOSURE_REVIEW_V1",
        "status": "WP4D_REJECTED_CHALLENGE_TRANSPORT_FAILURE",
        "challenge_status": d["status"],
        "closure_checks": checks,
        "evidence_summary": {
            "challenge_origins": d["challenge_origins"],
            "challenge_break_events": d["challenge_primary_break_events"],
            "predictive_terminal_episodes": d["predictive_episode_audit"]["terminal_predictive_episodes"],
            "predictive_break_conversions": d["predictive_episode_audit"]["break_conversions"],
            "predictive_recoveries": d["predictive_episode_audit"]["recoveries"],
            "M0_brier": m["M0_EPISODE_EMPIRICAL_PRIOR"]["brier_score"],
            "M0_logloss": m["M0_EPISODE_EMPIRICAL_PRIOR"]["log_loss"],
            "M1_brier": m["M1_TACTICAL_DURATION_RIDGE"]["brier_score"],
            "M1_logloss": m["M1_TACTICAL_DURATION_RIDGE"]["log_loss"],
            "M2_brier": m["M2_INTEGRATED_ROLE_CORE_RIDGE"]["brier_score"],
            "M2_logloss": m["M2_INTEGRATED_ROLE_CORE_RIDGE"]["log_loss"],
            "FAST_prebreak_recall": fast["prebreak_event_recall"],
            "FAST_false_per_100": fast["false_episodes_per_100_origins"],
            "FAST_median_lead_obs": fast["median_lead_observations"],
            "DUAL_prebreak_recall": dual["prebreak_event_recall"],
            "DUAL_false_per_100": dual["false_episodes_per_100_origins"],
            "DUAL_median_lead_obs": dual["median_lead_observations"],
            "SLOW_confirmed_before_next_break": d["slow_confirmation_lane"]["confirmed_before_next_break"],
            "SLOW_challenge_break_events": d["slow_confirmation_lane"]["challenge_break_events"],
        },
        "binding_interpretation": [
            "WP4D formation support was real but did not transport under the frozen 2025 challenge gate.",
            "M2 improved the empirical-prior null on both proper scores but was worse than the simpler M1 tactical-duration comparator on both Brier score and log loss in 2025.",
            "The structural-health dual lane increased break-event recall and stayed under the false-warning ceiling, but did not deliver strictly greater median lead observations than FAST, so the frozen monitoring gate failed.",
            "Monthly H1 and Emergency remain role-preserving context only because their formation same-origin incremental gates failed; GVZ remains NOT_TESTABLE for formation PIT support.",
            "No post-challenge rescue tuning is authorized. WP4D is closed as rejected.",
            "A separately named next challenger may investigate explicit state-duration/latent-state structure (e.g. HMM/HSMM) only under a new preregistration and without using 2025 outcomes to tune the rejected WP4D family."
        ],
        "next_gate": "SEPARATELY_PREREGISTERED_HMM_HSMM_CHALLENGER_OR_STOP",
        "database_write": "NONE",
        "production_authority": False,
        "prospective_claim": False,
    }
    out = args.output_dir / "gc_break_wp4d_closure_review_v1.json"
    out.write_text(json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(closure, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
