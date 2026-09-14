from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd


def root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "gc_break_v0" / "gc_break_wp3_baseline_contract_v1.json").exists():
            return p
    raise RuntimeError("PROJECT_ROOT_NOT_FOUND")


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--wp3-panel", type=Path, required=True)
    ap.add_argument("--wp3-summary", type=Path, required=True)
    ap.add_argument("--wp3-metrics", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)

    r = root()
    contract = json.loads((r / "gc_break_v0" / "gc_break_wp3_baseline_contract_v1.json").read_text())
    if contract.get("status") != "FROZEN_BEFORE_FORMATION_BASELINE_SCORING":
        raise RuntimeError("WP3_CONTRACT_NOT_FROZEN")
    s = json.loads(a.wp3_summary.read_text())
    if s.get("audit_id") != "GC_BREAK_WP3_CURRENT_FORMATION_BASELINES_V1" or s.get("status") != "EVIDENCE_GENERATED_NOT_YET_CLOSED":
        raise RuntimeError("WP3_EVIDENCE_GATE_FAIL")
    if any([s.get("model_learning_performed"), s.get("threshold_tuning_performed"), s.get("random_split_used"),
            s.get("challenge_2025_accessed"), s.get("stress_2026_accessed"), s.get("prospective_claim")]):
        raise RuntimeError("WP3_GOVERNANCE_CONTAMINATION")
    if s.get("database_write") != "NONE":
        raise RuntimeError("WP3_DATABASE_WRITE_DETECTED")

    p = pd.read_csv(a.wp3_panel, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    m = pd.read_csv(a.wp3_metrics)
    if len(p) != 351 or int(p["event_id"].notna().sum()) != 21:
        raise RuntimeError("WP3_PANEL_COUNT_FAIL")
    support = p[p["emergency_supported"].astype(str).str.lower().eq("true")].copy().reset_index(drop=True)
    if len(support) != 213 or int(support["event_id"].notna().sum()) != 13:
        raise RuntimeError("EMERGENCY_SUPPORT_COUNT_FAIL")

    events = support.loc[support["event_id"].notna(), ["event_id", "date", "regime_post"]].copy()
    events["event_id"] = events["event_id"].astype(int)
    events = events.rename(columns={"date": "break_date", "regime_post": "new_regime"}).reset_index(drop=True)
    diag = load_module(r / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_wp3_closure_diag")
    fast_same, fast_eps = diag.evaluate_signal(support, events, "fast_conflict")

    def row(bid: str) -> dict:
        z = m[m["baseline_id"].eq(bid)]
        if len(z) != 1: raise RuntimeError(f"METRIC_ROW_FAIL:{bid}")
        return z.iloc[0].to_dict()

    core = row("CORE_WEAKENING_NATIVE")
    emergency = row("EMERGENCY_REVERSAL_OPPOSITE")
    slow = s["slow_confirmation"]

    same_event_detection = int(fast_same["converted_episodes"]) == int(core["converted_episodes"])
    same_prebreak_recall = abs(float(fast_same["prebreak_event_recall"]) - float(core["prebreak_event_recall"])) < 1e-12
    same_at_or_before = abs(float(fast_same["at_or_before_event_recall"]) - float(core["at_or_before_event_recall"])) < 1e-12
    emergency_incremental_early_warning = not (same_event_detection and same_prebreak_recall and same_at_or_before)
    core_false_alarm_delta = float(core["false_episodes_per_100_origins"]) - float(fast_same["false_episodes_per_100_origins"])

    same_origin = {
        "support_origins": len(support),
        "eligible_break_events": len(events),
        "fast_conflict": fast_same,
        "core_weakening_native": {
            "converted_episodes": int(core["converted_episodes"]),
            "prebreak_event_recall": float(core["prebreak_event_recall"]),
            "at_or_before_event_recall": float(core["at_or_before_event_recall"]),
            "false_episodes_per_100_origins": float(core["false_episodes_per_100_origins"]),
            "episode_conversion_rate": float(core["episode_conversion_rate"]),
            "median_lead_observations": float(core["median_lead_observations"]),
            "median_lead_calendar_days": float(core["median_lead_calendar_days"]),
        },
        "emergency_reversal_opposite": {
            "prebreak_event_recall": float(emergency["prebreak_event_recall"]),
            "at_or_before_event_recall": float(emergency["at_or_before_event_recall"]),
            "false_episodes_per_100_origins": float(emergency["false_episodes_per_100_origins"]),
        },
        "emergency_incremental_early_warning_detected": emergency_incremental_early_warning,
        "core_minus_fast_false_alarm_episodes_per_100_origins": core_false_alarm_delta,
        "interpretation": "On Emergency-eligible origins, CORE adds no detected-break or recall gain over FAST_CONFLICT and increases false-warning burden." if not emergency_incremental_early_warning else "Incremental change detected; requires separate preregistered follow-up before promotion."
    }

    closure = {
        "audit_id": "GC_BREAK_WP3_CLOSURE_REVIEW_V1",
        "status": "COMPLETE_WITH_LIMITATIONS_READY_FOR_WP4",
        "wp3_contract_id": contract["contract_id"],
        "formation_origins": len(p),
        "break_events": int(p["event_id"].notna().sum()),
        "same_origin_optional_block_check": same_origin,
        "slow_confirmation": slow,
        "data_density_warning_retained": s.get("wp2_data_density_warning_inherited"),
        "scientific_interpretation": {
            "path_half": "ANATOMY_ONLY_NOT_INDEPENDENT_PREDICTIVE_EVIDENCE",
            "fast": "TACTICAL_WEAKENING_BASELINE_HAS_SIGNAL_BUT_LEAD_RECALL_TRADEOFF_REMAINS",
            "slow": "CONFIRMATION_ROLE_SUPPORTED",
            "emergency": "SELECTIVE_CONFIRMATION_CONTEXT; NO_INCREMENTAL_EARLY_WARNING_GAIN_ON_SAME_ELIGIBLE_ORIGINS",
            "bocpd_prereg": "SUPPLEMENTARY_SLOW_CONTEXT_ONLY; NOT_PROMOTED_AS_DAILY_TRIGGER"
        },
        "adequate_support_interpretation": "21 formation break events are adequate to begin a simple low-dimensional time-ordered WP4 challenger, but not to justify high-capacity models or broad interaction search.",
        "wp4_entry_guard": "BEGIN_SIMPLE_ROLE_PRESERVING_SEQUENTIAL_HAZARD_OR_STATE_TRANSITION_ONLY",
        "no_baseline_promoted_to_production": True,
        "no_threshold_retuning": True,
        "no_2025_2026_selection": True,
        "production_authority": False,
        "prospective_claim": False
    }
    (a.output_dir / "gc_break_wp3_same_origin_fast_vs_core_v1.json").write_text(json.dumps(same_origin, indent=2, sort_keys=True)+"\n")
    (a.output_dir / "gc_break_wp3_closure_review_v1.json").write_text(json.dumps(closure, indent=2, sort_keys=True)+"\n")
    fast_eps.to_csv(a.output_dir / "gc_break_wp3_same_origin_fast_episodes_v1.csv", index=False)
    print(json.dumps(closure, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
