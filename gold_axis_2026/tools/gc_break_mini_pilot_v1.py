from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import gc_break_wp1_build_formation_panel_v1 as wp1  # noqa: E402

CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_mini_pilot_contract_v1.json"
EVENT_CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def same_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_UP")) | ((regime == "DOWN") & (state == "ROBUST_DOWN"))


def opposite_robust(state: pd.Series, regime: pd.Series) -> pd.Series:
    return ((regime == "UP") & (state == "ROBUST_DOWN")) | ((regime == "DOWN") & (state == "ROBUST_UP"))


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status") != "FROZEN_BEFORE_MINI_PILOT_SCORING":
        raise RuntimeError("MINI_PILOT_CONTRACT_NOT_FROZEN")
    if float(contract["event_rule"]["k_sigma"]) != 3.0:
        raise RuntimeError("MINI_PILOT_K_SIGMA_CHANGED")
    if contract["governance"]["no_post_score_threshold_tuning"] is not True:
        raise RuntimeError("MINI_PILOT_POST_SCORE_TUNING_GUARD_FAIL")
    if contract["governance"]["no_database_writes"] is not True:
        raise RuntimeError("MINI_PILOT_NO_WRITE_GUARD_FAIL")

    prehistory_start = pd.Timestamp(contract["data_window"]["prehistory_start"])
    state_start = pd.Timestamp(contract["state_window"]["start"])
    state_end = pd.Timestamp(contract["state_window"]["end"])
    score_start = pd.Timestamp(contract["score_window"]["start"])
    score_end = pd.Timestamp(contract["score_window"]["end"])

    ny, all_probe = wp1.load_exact_rows([args.probe_csv])
    all_probe = all_probe[(all_probe["trade_date"] >= prehistory_start) & (all_probe["trade_date"] <= state_end)].copy()
    unresolved = sorted(set(all_probe["acquisition_status"]) - wp1.FINAL_STATUSES)
    if unresolved:
        raise RuntimeError(f"MINI_PILOT_UNRESOLVED_PROBE_STATUS:{unresolved}")

    ny = ny[(ny["date"] >= prehistory_start) & (ny["date"] <= state_end)].copy().reset_index(drop=True)
    if ny.empty:
        raise RuntimeError("MINI_PILOT_NO_VALID_EXACT_ROWS")

    # Guard sufficient native prehistory before state scoring begins.
    pre = ny[ny["date"] < state_start]
    if len(pre) < 40:
        raise RuntimeError(f"MINI_PILOT_INSUFFICIENT_DAILY_PREHISTORY:{len(pre)}")
    pre_months = pre.set_index("date")["close"].resample("MS").last().dropna()
    required_months = {"2024-01", "2024-02", "2024-03"}
    got_months = set(pre_months.index.to_period("M").astype(str))
    if not required_months <= got_months:
        raise RuntimeError(f"MINI_PILOT_MONTHLY_PREHISTORY_MISSING:{sorted(required_months-got_months)}")

    # Reuse the frozen R4 implementation exactly; only the pilot date boundaries differ.
    wp1.FORMATION_START = state_start
    wp1.FORMATION_END = state_end
    wp1.REQUIRED_PREHISTORY_START = ny["date"].min()
    refs = wp1.load_emergency_refs()
    panel = wp1.build_panel(ny, refs)

    if panel["date"].min() > state_start or panel["date"].max() < score_end:
        raise RuntimeError("MINI_PILOT_STATE_WINDOW_COVERAGE_FAIL")

    event_contract = json.loads(EVENT_CONTRACT_PATH.read_text(encoding="utf-8"))
    if event_contract.get("status") != "FROZEN_BEFORE_GC_BREAK_V0_DIAGNOSTIC_SCORING":
        raise RuntimeError("EVENT_CONTRACT_NOT_FROZEN")
    if float(event_contract["primary_event_rule"]["k_sigma"]) != 3.0:
        raise RuntimeError("EVENT_CONTRACT_PRIMARY_K_CHANGED")

    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_mini_pilot_diag")
    events_all, origins_all = diag.build_break_inventory(panel[["date", "close"]], event_contract)

    origins_all["date"] = pd.to_datetime(origins_all["date"])
    events_all["break_date"] = pd.to_datetime(events_all["break_date"])
    origins = origins_all[(origins_all["date"] >= score_start) & (origins_all["date"] <= score_end)].copy()
    events = events_all[(events_all["break_date"] >= score_start) & (events_all["break_date"] <= score_end)].copy()
    score_panel = panel[(panel["date"] >= score_start) & (panel["date"] <= score_end)].copy()

    missing_origin_dates = sorted(set(score_panel["date"]) - set(origins["date"]))
    if missing_origin_dates:
        raise RuntimeError(f"MINI_PILOT_ANATOMY_COVERAGE_GAP:{[d.date().isoformat() for d in missing_origin_dates[:10]]}")

    p = score_panel.merge(origins, on="date", how="inner", validate="one_to_one").sort_values("date").reset_index(drop=True)
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
        metrics.append(m)
        if not e.empty:
            e = e.copy()
            e["baseline_id"] = baseline_id
            episodes.append(e)

    metrics_df = pd.DataFrame(metrics)
    episodes_df = pd.concat(episodes, ignore_index=True) if episodes else pd.DataFrame()
    conf = diag.confirmation_delays(p, events)
    conf_valid = conf.dropna(subset=["delay_observations"]) if not conf.empty else conf

    panel.to_csv(args.output_dir / "mini_wp1_state_panel_2024_apr_aug.csv", index=False)
    origins.to_csv(args.output_dir / "mini_wp2_score_origin_rule_2024_jun_aug.csv", index=False)
    events.to_csv(args.output_dir / "mini_wp2_break_events_2024_jun_aug.csv", index=False)
    p.to_csv(args.output_dir / "mini_wp3_baseline_panel_2024_jun_aug.csv", index=False)
    metrics_df.to_csv(args.output_dir / "mini_wp3_baseline_metrics_2024_jun_aug.csv", index=False)
    episodes_df.to_csv(args.output_dir / "mini_wp3_baseline_episodes_2024_jun_aug.csv", index=False)
    conf.to_csv(args.output_dir / "mini_wp3_slow_confirmation_2024_jun_aug.csv", index=False)

    summary = {
        "audit_id": "GC_BREAK_MINI_PILOT_V1",
        "contract_id": contract["contract_id"],
        "contract_status": contract["status"],
        "source_semantic": contract["data_window"]["source_semantic"],
        "valid_exact_rows_total": int(len(ny)),
        "state_window": {"start": state_start.date().isoformat(), "end": state_end.date().isoformat(), "origins": int(len(panel))},
        "score_window": {"start": score_start.date().isoformat(), "end": score_end.date().isoformat(), "origins": int(len(p))},
        "break_events": int(len(events)),
        "break_direction_counts": events["new_regime"].value_counts().to_dict() if not events.empty else {},
        "state_counts": {
            "fast": panel["fast_state"].value_counts(dropna=False).to_dict(),
            "slow": panel["slow_state"].value_counts(dropna=False).to_dict(),
            "monthly_direction": panel["monthly_direction_3m"].value_counts(dropna=False).to_dict(),
            "emergency_reversal": panel["emergency_reversal"].value_counts(dropna=False).to_dict(),
        },
        "metrics": metrics_df.replace({np.nan: None}).set_index("baseline_id").to_dict(orient="index"),
        "slow_confirmation": {
            "events": int(len(conf)),
            "confirmed_before_next_break": int(len(conf_valid)),
            "rate": float(len(conf_valid) / len(conf)) if len(conf) else None,
            "median_delay_observations": float(conf_valid["delay_observations"].median()) if len(conf_valid) else None,
        },
        "model_learning_performed": False,
        "post_score_tuning_performed": False,
        "production_database_write": "NONE",
        "prospective_claim": False,
        "interpretation_lock": "MINI PILOT ONLY. These results test signal coherence and pipeline viability; they do not replace the full formation/challenge design.",
    }
    (args.output_dir / "gc_break_mini_pilot_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False, default=str) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
