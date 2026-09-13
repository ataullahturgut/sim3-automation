from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_wp3_baseline_contract_v1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def opposite_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_DOWN")) | ((regime == "DOWN") & (state == "ROBUST_UP"))


def same_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_UP")) | ((regime == "DOWN") & (state == "ROBUST_DOWN"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--origin-rule", type=Path, required=True)
    parser.add_argument("--events", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status") != "FROZEN_BEFORE_FORMATION_BASELINE_SCORING":
        raise RuntimeError("WP3_BASELINE_CONTRACT_NOT_FROZEN")
    if contract["governance"]["no_post_score_threshold_tuning"] is not True:
        raise RuntimeError("NO_POST_SCORE_TUNING_GUARD_FAIL")

    panel = pd.read_csv(args.panel, parse_dates=["date"])
    anatomy = pd.read_csv(args.origin_rule, parse_dates=["date"])
    events = pd.read_csv(args.events, parse_dates=["break_date"])
    p = panel.merge(anatomy, on="date", how="inner", validate="one_to_one").sort_values("date").reset_index(drop=True)
    if len(p) != len(panel):
        raise RuntimeError(f"PANEL_ANATOMY_JOIN_LOSS:{len(panel)}:{len(p)}")

    valid_regime = p["regime_pre"].isin(["UP", "DOWN"])
    fast_same = same_robust(p["fast_state"], p["regime_pre"])
    p["no_warning"] = False
    p["path_half"] = valid_regime & p["adverse_fraction"].ge(0.50)
    p["fast_conflict"] = valid_regime & ~fast_same
    p["fast_opposite"] = valid_regime & opposite_robust(p["fast_state"], p["regime_pre"])
    p["slow_conflict"] = valid_regime & ~same_robust(p["slow_state"], p["regime_pre"])
    p["slow_opposite"] = valid_regime & opposite_robust(p["slow_state"], p["regime_pre"])
    p["emergency_reversal_opposite"] = (
        ((p["regime_pre"] == "UP") & (p["emergency_reversal"] == "DOWN_ALERT"))
        | ((p["regime_pre"] == "DOWN") & (p["emergency_reversal"] == "UP_ALERT"))
    )
    p["core_weakening_native"] = p["fast_conflict"] | p["emergency_reversal_opposite"]

    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_wp3_diag")
    signal_map = {
        "NO_WARNING": "no_warning",
        "PATH_HALF": "path_half",
        "FAST_CONFLICT": "fast_conflict",
        "FAST_OPPOSITE": "fast_opposite",
        "SLOW_CONFLICT": "slow_conflict",
        "EMERGENCY_REVERSAL_OPPOSITE": "emergency_reversal_opposite",
        "CORE_WEAKENING_NATIVE": "core_weakening_native",
    }
    metrics = []
    episodes = []
    for baseline_id, col in signal_map.items():
        m, e = diag.evaluate_signal(p, events, col)
        m["baseline_id"] = baseline_id
        m["available_origins"] = int(p[col].notna().sum())
        if baseline_id == "EMERGENCY_REVERSAL_OPPOSITE":
            m["native_reference_available_origins"] = int(p["emergency_status"].eq("AVAILABLE_FROZEN_REFERENCE").sum())
        metrics.append(m)
        if not e.empty:
            e = e.copy(); e["baseline_id"] = baseline_id; episodes.append(e)

    metrics_df = pd.DataFrame(metrics)
    episodes_df = pd.concat(episodes, ignore_index=True) if episodes else pd.DataFrame()
    conf = diag.confirmation_delays(p, events)
    conf_valid = conf.dropna(subset=["delay_observations"])

    p.to_csv(args.output_dir / "gc_break_wp3_formation_baseline_panel.csv", index=False)
    metrics_df.to_csv(args.output_dir / "gc_break_wp3_formation_baseline_metrics.csv", index=False)
    episodes_df.to_csv(args.output_dir / "gc_break_wp3_formation_baseline_episodes.csv", index=False)
    conf.to_csv(args.output_dir / "gc_break_wp3_slow_confirmation.csv", index=False)

    summary = {
        "audit_id": "GC_BREAK_WP3_FORMATION_BASELINES_V1",
        "contract_id": contract["contract_id"],
        "contract_status": contract["status"],
        "formation_origins": int(len(p)),
        "events": int(len(events)),
        "metrics": metrics_df.replace({np.nan: None}).set_index("baseline_id").to_dict(orient="index"),
        "slow_confirmation": {
            "events": int(len(conf)),
            "confirmed_before_next_break": int(len(conf_valid)),
            "rate": float(len(conf_valid) / len(conf)) if len(conf) else None,
            "median_delay_observations": float(conf_valid["delay_observations"].median()) if len(conf_valid) else None,
            "median_delay_calendar_days": float(conf_valid["delay_calendar_days"].median()) if len(conf_valid) else None
        },
        "emergency_2022_imputation": "NONE",
        "model_learning_performed": False,
        "production_database_write": "NONE",
        "prospective_claim": False,
        "interpretation_lock": "FORMATION BASELINES ONLY; WP4 integration may be designed only after these frozen baseline results are inspected.",
    }
    (args.output_dir / "gc_break_wp3_formation_baselines_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
