from __future__ import annotations

import argparse
import json
from pathlib import Path


def project_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "gc_break_v0" / "gc_break_wp4b_authority_guided_state_machine_prereg_v1.json").exists():
            return parent
    raise RuntimeError("PROJECT_ROOT_NOT_FOUND")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)
    c = json.loads((project_root()/"gc_break_v0"/"gc_break_wp4b_authority_guided_state_machine_prereg_v1.json").read_text())
    s = json.loads(a.summary.read_text())
    if c.get("status") != "FROZEN_BEFORE_FORMATION_SCORING": raise RuntimeError("PREREG_NOT_FROZEN")
    if s.get("contract_id") != c.get("contract_id"): raise RuntimeError("CONTRACT_MISMATCH")
    if s.get("status") != "NO_INCREMENTAL_VALUE": raise RuntimeError(f"UNEXPECTED_PRIMARY_STATUS:{s.get('status')}")
    for k in ["challenge_2025_accessed", "stress_2026_accessed", "prospective_claim", "post_score_tuning_performed"]:
        if bool(s.get(k)): raise RuntimeError(f"GOVERNANCE_CONTAMINATION:{k}")
    if s.get("database_write") != "NONE" or s.get("production_authority") is not False:
        raise RuntimeError("AUTHORITY_CONTAMINATION")
    m=s["models"]
    ids=["WP4B_ROLE_FSM_NO_CUSUM","WP4B_RP_CUSUM_FSM_H5","WP4B_RP_CUSUM_FSM_H4_SENSITIVITY"]
    w=[m[i]["weakening"] for i in ids]
    signature=lambda x:(x["episodes"],x["converted_episodes"],x["false_episodes"],x["prebreak_event_recall"],x["median_lead_observations"],x["false_episodes_per_100_origins"])
    if len({signature(x) for x in w}) != 1:
        raise RuntimeError("CUSUM_VARIANTS_CHANGED_WARNING_METRICS_UNEXPECTED_FOR_CLOSURE_V1")
    p=m["WP4B_RP_CUSUM_FSM_H5"]
    closure={
        "audit_id":"GC_BREAK_WP4B_CLOSURE_REVIEW_V1",
        "status":"WP4B_REJECTED_NO_INCREMENTAL_VALUE",
        "contract_id":c["contract_id"],
        "run_id":34833180741,
        "formation_origins":s["formation_origins"],
        "formation_break_events":s["formation_break_events"],
        "primary_h5_weakening":p["weakening"],
        "primary_h5_break_alert":p["break_alert"],
        "confirmation":p["confirmation"],
        "cusum_incremental_state_value":"NONE_AT_FROZEN_H4_H5",
        "interpretation":"The authority-guided FSM is operationally selective and recovers cleanly, but its pre-break coverage is below the frozen FAST_CONFLICT comparator. Classical CUSUM at preregistered h=5 and h=4 sensitivity changed no state metrics. Lowering h or rewriting transitions after observing this result is forbidden.",
        "phase_result":"NO_INCREMENTAL_VALUE",
        "next_research_gate":"REDIRECT_TO_EPISODE_CONDITIONED_COMPETING_TRANSITION_PROBLEM; separately preregister before scoring",
        "challenge_2025_remains_locked":True,
        "stress_2026_remains_nonselection":True,
        "production_authority":False,
        "prospective_claim":False
    }
    out=a.output_dir/"gc_break_wp4b_closure_review_v1.json"
    out.write_text(json.dumps(closure,indent=2,sort_keys=True)+"\n")
    print(json.dumps(closure,indent=2,sort_keys=True))
    return 0

if __name__ == "__main__": raise SystemExit(main())
