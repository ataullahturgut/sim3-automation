from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    panel = pd.read_csv(args.panel, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    bocpd = load_module(ROOT / "tools" / "bocpd_return_successor_v1.py", "gc_break_wp1_bocpd")
    replay = bocpd.build_replay().rows.reset_index()
    replay["month"] = pd.to_datetime(replay["month"]).dt.to_period("M")
    lookup = replay.set_index("month")[["state", "reset_fraction", "p_run0", "run_length_entropy", "evidence_class", "direction_vote_permitted"]]

    current_month = panel["date"].dt.to_period("M")
    prior_month = current_month - 1
    panel["bocpd_source_month"] = prior_month.astype(str)
    for col in lookup.columns:
        panel[f"bocpd_{col}"] = prior_month.map(lookup[col].to_dict())
    panel["bocpd_native_clock"] = "COMPLETED_MONTH_ONLY"
    panel["bocpd_available_rule"] = "PRIOR_COMPLETED_MONTH_CARRIED_FORWARD_WITHIN_CURRENT_MONTH"
    panel["bocpd_missing_reason"] = panel["bocpd_state"].isna().map(lambda x: "NATIVE_REPLAY_MONTH_NOT_AVAILABLE" if x else None)

    age = []
    prev = None
    n = 0
    for m in current_month.astype(str):
        if m == prev:
            n += 1
        else:
            prev = m; n = 1
        age.append(n)
    panel["bocpd_context_age_origins"] = age

    panel.to_csv(args.output_dir / "gc_break_wp1_formation_panel_with_bocpd_v1.csv", index=False)
    summary = {
        "audit_id": "GC_BREAK_WP1_BOCPD_NATIVE_CONTEXT_V1",
        "engine_id": "BOCPD_RETURN_SUCCESSOR_V1",
        "role": "REGIME_BREAK_CONTEXT",
        "native_clock": "COMPLETED_MONTH_ONLY",
        "direction_vote_permitted": False,
        "origins": int(len(panel)),
        "state_available_origins": int(panel["bocpd_state"].notna().sum()),
        "state_missing_origins": int(panel["bocpd_state"].isna().sum()),
        "future_information_violations_by_join_rule": 0,
        "production_database_write": "NONE",
        "prospective_claim": False,
        "interpretation_lock": "Existing frozen monthly BOCPD identity is preserved; no daily BOCPD mutation is performed.",
    }
    (args.output_dir / "gc_break_wp1_bocpd_native_context_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
