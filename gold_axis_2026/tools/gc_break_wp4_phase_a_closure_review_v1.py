from __future__ import annotations

import argparse
import json
from pathlib import Path


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "gc_break_v0" / "gc_break_wp4_hazard_prereg_v1.json").exists():
            return parent
    raise RuntimeError("PROJECT_ROOT_NOT_FOUND")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase-a-summary", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)

    root = project_root()
    contract = json.loads((root / "gc_break_v0" / "gc_break_wp4_hazard_prereg_v1.json").read_text(encoding="utf-8"))
    s = json.loads(a.phase_a_summary.read_text(encoding="utf-8"))
    if contract.get("status") != "FROZEN_BEFORE_WP4_FORMATION_SCORING":
        raise RuntimeError("WP4_CONTRACT_STATUS_FAIL")
    if s.get("audit_id") != "GC_BREAK_WP4_PREQUENTIAL_HAZARD_PHASE_A_V1" or s.get("status") != "EVIDENCE_GENERATED_NOT_YET_CLOSED":
        raise RuntimeError("WP4_PHASE_A_EVIDENCE_GATE_FAIL")
    if s.get("contract_id") != contract.get("contract_id"):
        raise RuntimeError("WP4_CONTRACT_ID_MISMATCH")
    forbidden = ["state_threshold_mapping_performed", "hyperparameter_search_performed", "random_split_used", "challenge_2025_accessed", "stress_2026_accessed", "prospective_claim"]
    if any(bool(s.get(k)) for k in forbidden):
        raise RuntimeError("WP4_GOVERNANCE_CONTAMINATION")
    if s.get("database_write") != "NONE" or s.get("production_authority") is not False:
        raise RuntimeError("WP4_AUTHORITY_FAIL")

    d = s["decision_detail"]
    m1 = d["M1_FAST_DURATION_RIDGE"]
    m2 = d["M2_ROLE_CORE_RIDGE"]
    m3 = d["M3_PATH_AUGMENTED_SENSITIVITY"]
    m1_both = bool(m1["improves_brier_vs_M0"] and m1["improves_log_loss_vs_M0"])
    m2_both = bool(m2["improves_brier_vs_M0"] and m2["improves_log_loss_vs_M0"])
    m3_both = bool(m3["improves_brier_vs_M0"] and m3["improves_log_loss_vs_M0"])
    expected = "M2_POSITIVE_PROBABILITY_SIGNAL" if m2_both else ("M1_ONLY_POSITIVE_PROBABILITY_SIGNAL" if m1_both else "REJECT_LEARNED_HAZARD")
    if s.get("phase_a_status") != expected:
        raise RuntimeError(f"WP4_DECISION_RULE_MISMATCH:{s.get('phase_a_status')}:{expected}")
    if expected != "REJECT_LEARNED_HAZARD":
        raise RuntimeError("THIS_CLOSURE_VERSION_EXPECTS_REJECTION;CREATE_NEW_VERSION_IF_EVIDENCE_DIFFERS")
    if not m3_both:
        raise RuntimeError("M3_SENSITIVITY_EXPECTATION_MISMATCH")

    closure = {
        "audit_id": "GC_BREAK_WP4_PHASE_A_CLOSURE_REVIEW_V1",
        "status": "WP4_PHASE_A_REJECTED_NO_PHASE_B",
        "contract_id": contract["contract_id"],
        "frozen_decision_rule_result": expected,
        "evaluation_origins": int(s["evaluation_origins"]),
        "evaluation_break_events": int(s["evaluation_break_events"]),
        "primary_evidence": {
            "M1_FAST_DURATION_RIDGE": m1,
            "M2_ROLE_CORE_RIDGE": m2,
        },
        "sensitivity_only": {
            "M3_PATH_AUGMENTED_SENSITIVITY": m3,
            "both_primary_probability_scores_improved": m3_both,
            "promotion_permitted": False,
            "reason": "M3 uses adverse_fraction_post derived from the same price path as the frozen event label; the preregistration forbids sensitivity-only promotion."
        },
        "interpretation": "The independent learned hazard challengers M1/M2 improved log loss but failed the preregistered joint Brier+log-loss criterion versus M0. Learned-hazard escalation is rejected. The positive M3 path sensitivity is not independent predictive evidence and cannot rescue the primary family.",
        "phase_b_probability_thresholds_authorized": False,
        "high_capacity_escalation_authorized": False,
        "next_research_gate": "RESEARCH_REDIRECTION_REQUIRED; any alternative simple role-preserving architecture must receive a separately named preregistration before scoring. Do not tune M1/M2/M3 after these results.",
        "challenge_2025_remains_locked": True,
        "stress_2026_remains_nonselection": True,
        "production_authority": False,
        "prospective_claim": False
    }
    out = a.output_dir / "gc_break_wp4_phase_a_closure_review_v1.json"
    out.write_text(json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(closure, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
