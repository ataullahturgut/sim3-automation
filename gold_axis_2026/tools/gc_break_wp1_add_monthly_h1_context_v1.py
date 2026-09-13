from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
LOCKED = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_43.csv"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    panel = pd.read_csv(args.panel, parse_dates=["date"]).sort_values("date").reset_index(drop=True)
    locked = pd.read_csv(LOCKED)
    required = {"month", "rw", "mom", "vw", "patch_v7"}
    if not required <= set(locked.columns):
        raise RuntimeError("H1_LOCKED_REPLAY_SCHEMA_FAIL")
    locked = locked[["month", "rw", "mom", "vw", "patch_v7"]].copy()
    locked["month"] = locked["month"].astype(str)
    for c in ["rw", "mom", "vw", "patch_v7"]:
        locked[c] = pd.to_numeric(locked[c], errors="raise")
        if (~np.isfinite(locked[c])) .any() or (locked[c] <= 0).any():
            raise RuntimeError(f"H1_INVALID_FORECAST:{c}")

    lookup = locked.set_index("month")
    month = panel["date"].dt.strftime("%Y-%m")
    names = {"rw": "h1_random_walk", "mom": "h1_momentum_3m", "vw": "h1_vw_midas", "patch_v7": "h1_causal_patch"}
    for source, target in names.items():
        panel[target] = month.map(lookup[source].to_dict())
    cols = list(names.values())
    panel["h1_consensus_median"] = panel[cols].median(axis=1, skipna=True)
    panel["h1_dispersion_std"] = panel[cols].std(axis=1, ddof=0, skipna=True)
    panel["h1_dispersion_range"] = panel[cols].max(axis=1, skipna=True) - panel[cols].min(axis=1, skipna=True)
    panel["h1_price_gap_to_consensus"] = panel["close"] / panel["h1_consensus_median"] - 1.0
    support = panel[cols].notna().sum(axis=1)
    panel["h1_expert_support"] = support
    panel["h1_context_status"] = np.where(support.eq(4), "AVAILABLE_FOUR_FROZEN_REPLAY_EXPERTS", "NOT_TESTABLE_HISTORICAL_H1_REPLAY_NOT_AVAILABLE")
    panel["h1_context_role"] = "STRATEGIC_CONTEXT_ONLY_MONTHLY_H1_REMAINS_INDEPENDENT_PRIMARY_OUTPUT"
    panel["h1_context_evidence_class"] = "HISTORICAL_REPLAY_CONTEXT_NOT_PROSPECTIVE"

    panel.to_csv(args.output_dir / "gc_break_wp1_formation_panel_with_monthly_h1_v1.csv", index=False)
    summary = {
        "audit_id": "GC_BREAK_WP1_MONTHLY_H1_CONTEXT_V1",
        "engines": ["RANDOM_WALK", "MOMENTUM_3M", "VW_MIDAS_MSVR_SUCCESSOR_V1", "CAUSAL_PATCH"],
        "role": "STRATEGIC_CONTEXT; monthly H1 forecast remains a separate active output line",
        "origins": int(len(panel)),
        "four_expert_available_origins": int(support.eq(4).sum()),
        "unavailable_origins": int((~support.eq(4)).sum()),
        "imputation": "NONE",
        "production_database_write": "NONE",
        "prospective_claim": False,
        "interpretation_lock": "H1 context may not be promoted to short-term break trigger merely from retrospective score.",
    }
    (args.output_dir / "gc_break_wp1_monthly_h1_context_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
