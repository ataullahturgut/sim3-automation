from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

FORMATION_START = pd.Timestamp("2022-01-01")
FORMATION_END = pd.Timestamp("2024-12-31")
PREHISTORY_START = pd.Timestamp("2021-09-01")
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}
REQUIRED_LINEAGE = {"source_bar_datetime", "retrieved_at", "payload_sha256", "evidence_class"}


def read_panel(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    if "date" not in d:
        raise RuntimeError(f"PANEL_DATE_MISSING:{path}")
    d["date"] = pd.to_datetime(d["date"]).dt.normalize()
    if d["date"].duplicated().any():
        raise RuntimeError(f"PANEL_DUPLICATE_DATE:{path}")
    return d.sort_values("date").reset_index(drop=True)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--exact-csv", type=Path, required=True)
    p.add_argument("--base-panel", type=Path, required=True)
    p.add_argument("--bocpd-panel", type=Path, required=True)
    p.add_argument("--h1-panel", type=Path, required=True)
    p.add_argument("--event-panel", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args(); a.output_dir.mkdir(parents=True, exist_ok=True)

    x = pd.read_csv(a.exact_csv, dtype=str, keep_default_na=False)
    if not {"trade_date", "acquisition_status"} <= set(x.columns):
        raise RuntimeError("EXACT_SCHEMA_FAIL")
    x["trade_date"] = pd.to_datetime(x["trade_date"]).dt.normalize()
    if x["trade_date"].duplicated().any():
        raise RuntimeError("EXACT_DUPLICATE_TRADE_DATE")
    expected = pd.date_range(PREHISTORY_START, FORMATION_END, freq="D")
    if set(x["trade_date"]) != set(expected):
        raise RuntimeError(f"EXACT_CALENDAR_COVERAGE_FAIL:got={len(x)}:expected={len(expected)}")
    unresolved = x.loc[~x["acquisition_status"].isin(FINAL_STATUSES)]
    if len(unresolved):
        raise RuntimeError(f"EXACT_UNRESOLVED_ROWS:{len(unresolved)}")

    valid = x[x["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    if valid.empty:
        raise RuntimeError("EXACT_NO_VALID_ROWS")
    if not REQUIRED_LINEAGE <= set(valid.columns):
        raise RuntimeError(f"EXACT_LINEAGE_COLUMNS_MISSING:{sorted(REQUIRED_LINEAGE-set(valid.columns))}")
    for c in REQUIRED_LINEAGE:
        if valid[c].astype(str).str.strip().eq("").any():
            raise RuntimeError(f"EXACT_LINEAGE_VALUE_MISSING:{c}")
    if "prospective_claim" in valid and valid["prospective_claim"].astype(str).str.lower().ne("false").any():
        raise RuntimeError("EXACT_PROSPECTIVE_CLAIM_FAIL")
    for c, expected_value in {
        "provider": "Twelve Data", "symbol": "XAU/USD", "interval": "1min",
        "timezone": "America/New_York", "accepted_source_time": "16:59:00",
    }.items():
        if c not in valid or set(valid[c].astype(str)) != {expected_value}:
            raise RuntimeError(f"EXACT_BINDING_FAIL:{c}")

    base = read_panel(a.base_panel)
    bocpd = read_panel(a.bocpd_panel)
    h1 = read_panel(a.h1_panel)
    event = read_panel(a.event_panel)
    formation_valid = valid[(valid["trade_date"] >= FORMATION_START) & (valid["trade_date"] <= FORMATION_END)]["trade_date"]
    if set(base["date"]) != set(formation_valid):
        raise RuntimeError(f"BASE_PANEL_VALID_DATE_MISMATCH:panel={len(base)}:valid={len(formation_valid)}")
    for name, d in (("bocpd", bocpd), ("h1", h1), ("event", event)):
        if list(d["date"]) != list(base["date"]):
            raise RuntimeError(f"AUGMENTED_PANEL_DATE_MISMATCH:{name}")
    required_final_cols = {
        "fast_state", "slow_state", "fast_state_age", "slow_state_age",
        "bocpd_state", "bocpd_context_age_origins",
        "h1_random_walk", "h1_momentum_3m", "h1_vw_midas", "h1_causal_patch",
        "macro_strong_event_count", "market_shock_event_count",
    }
    if not required_final_cols <= set(event.columns):
        raise RuntimeError(f"FINAL_CONTEXT_COLUMNS_MISSING:{sorted(required_final_cols-set(event.columns))}")
    if "prospective_claim" in event and event["prospective_claim"].astype(str).str.lower().ne("false").any():
        raise RuntimeError("FINAL_PANEL_PROSPECTIVE_CLAIM_FAIL")

    summary = {
        "audit_id": "GC_BREAK_WP1_MANIFEST_CLOSURE_AUDIT_V1",
        "status": "PASS",
        "manifest_wp": "WP1 — PIT-safe formation panel",
        "prehistory_calendar_start": PREHISTORY_START.date().isoformat(),
        "formation_start": FORMATION_START.date().isoformat(),
        "formation_end": FORMATION_END.date().isoformat(),
        "exact_calendar_rows": int(len(x)),
        "valid_exact_rows_total": int(len(valid)),
        "provider_no_bar_rows_total": int((x["acquisition_status"] == "PROVIDER_NO_BAR").sum()),
        "unresolved_rows": 0,
        "formation_origins": int(len(base)),
        "final_context_origins": int(len(event)),
        "exact_source_semantic": "Twelve Data XAU/USD 1min exact 16:59:00 America/New_York -> 17:00 ET",
        "fallback": "NONE",
        "interpolation": "FORBIDDEN",
        "forward_fill": "FORBIDDEN",
        "production_database_write": "NONE",
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "prospective_claim": False,
        "closure_interpretation": "WP1 closure candidate only; WP2 may start only after this PASS artifact is inspected under the current manifest.",
    }
    (a.output_dir / "gc_break_wp1_manifest_closure_audit_v1.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
