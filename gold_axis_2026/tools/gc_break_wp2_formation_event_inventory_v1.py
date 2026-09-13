from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def summarize(events: pd.DataFrame, origins: pd.DataFrame) -> dict:
    if events.empty:
        return {"events": 0, "by_new_regime": {}, "by_year": {}, "median_extreme_to_break_calendar_days": None}
    e = events.copy()
    e["break_date"] = pd.to_datetime(e["break_date"])
    e["extreme_date"] = pd.to_datetime(e["extreme_date"])
    e["year"] = e["break_date"].dt.year
    lead = (e["break_date"] - e["extreme_date"]).dt.days
    return {
        "events": int(len(e)),
        "by_new_regime": {str(k): int(v) for k, v in e["new_regime"].value_counts().to_dict().items()},
        "by_year": {str(k): int(v) for k, v in e["year"].value_counts().sort_index().to_dict().items()},
        "median_extreme_to_break_calendar_days": float(np.median(lead)) if len(lead) else None,
        "p25_extreme_to_break_calendar_days": float(np.percentile(lead, 25)) if len(lead) else None,
        "p75_extreme_to_break_calendar_days": float(np.percentile(lead, 75)) if len(lead) else None,
        "origin_rows": int(len(origins)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status") != "FROZEN_BEFORE_GC_BREAK_V0_DIAGNOSTIC_SCORING":
        raise RuntimeError("EVENT_CONTRACT_NOT_FROZEN")
    if float(contract["primary_event_rule"]["k_sigma"]) != 3.0:
        raise RuntimeError("PRIMARY_K_SIGMA_CHANGED")
    if contract["governance"]["no_database_writes"] is not True:
        raise RuntimeError("NO_WRITE_GUARD_FAIL")

    panel = pd.read_csv(args.panel, parse_dates=["date"])
    required = {"date", "close"}
    if not required <= set(panel.columns):
        raise RuntimeError("FORMATION_PANEL_SCHEMA_FAIL")
    panel = panel.sort_values("date").reset_index(drop=True)
    if panel["date"].duplicated().any():
        raise RuntimeError("FORMATION_PANEL_DUPLICATE_DATE")

    diag = load_module(ROOT / "tools" / "gc_break_v0_governed_diagnostic_v1.py", "gc_break_wp2_diag")
    primary_events, primary_origins = diag.build_break_inventory(panel[["date", "close"]], contract)

    sensitivity_contract = copy.deepcopy(contract)
    sensitivity_contract["primary_event_rule"]["k_sigma"] = 2.5
    sens_events, sens_origins = diag.build_break_inventory(panel[["date", "close"]], sensitivity_contract)

    primary_events.to_csv(args.output_dir / "gc_break_wp2_primary_k3_events.csv", index=False)
    primary_origins.to_csv(args.output_dir / "gc_break_wp2_primary_k3_origin_rule.csv", index=False)
    sens_events.to_csv(args.output_dir / "gc_break_wp2_sensitivity_k2_5_events.csv", index=False)
    sens_origins.to_csv(args.output_dir / "gc_break_wp2_sensitivity_k2_5_origin_rule.csv", index=False)

    summary = {
        "audit_id": "GC_BREAK_WP2_FORMATION_EVENT_INVENTORY_V1",
        "event_contract_id": contract["contract_id"],
        "event_contract_status": contract["status"],
        "formation_start": panel["date"].min().date().isoformat(),
        "formation_end": panel["date"].max().date().isoformat(),
        "primary_k3": summarize(primary_events, primary_origins),
        "sensitivity_k2_5": summarize(sens_events, sens_origins),
        "engine_inputs_used_for_label": [],
        "model_performance_consumed": False,
        "split_selection_performed": False,
        "production_database_write": "NONE",
        "prospective_claim": False,
        "interpretation_lock": "WP2 label-quality/event-support inventory only; k=2.5 cannot replace frozen primary k=3.0 because of downstream model score.",
    }
    (args.output_dir / "gc_break_wp2_formation_event_inventory_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
