from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

START = pd.Timestamp("2021-09-01")
END = pd.Timestamp("2024-12-31")
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--probe-csv", action="append", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    a = p.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    for path in a.probe_csv:
        d = pd.read_csv(path, dtype=str, keep_default_na=False)
        if not {"trade_date", "acquisition_status"} <= set(d.columns):
            raise RuntimeError(f"SCHEMA_MISMATCH:{path}")
        d["source_input"] = str(path)
        frames.append(d)
    src = pd.concat(frames, ignore_index=True)
    src["trade_date"] = pd.to_datetime(src["trade_date"]).dt.normalize()
    src = src[(src["trade_date"] >= START) & (src["trade_date"] <= END)].copy()
    if src["trade_date"].duplicated().any():
        dup = src.loc[src["trade_date"].duplicated(False), "trade_date"].dt.strftime("%Y-%m-%d").tolist()
        raise RuntimeError(f"DUPLICATE_TRADE_DATE:{dup[:20]}")

    expected = pd.date_range(START, END, freq="D")
    missing = expected.difference(pd.DatetimeIndex(src["trade_date"]))
    seed = pd.DataFrame({"trade_date": missing.strftime("%Y-%m-%d")})
    seed["acquisition_status"] = "UNRESOLVED_EXACT_DATE_PROBE_REQUIRED"
    seed["provider_code"] = ""
    seed["provider_message"] = "formation date not present in prior immutable probe artifacts"
    seed["source_bar_datetime"] = ""
    for c in ("open", "high", "low", "close", "retrieved_at", "payload_sha256"):
        seed[c] = ""
    seed["provider"] = "Twelve Data"
    seed["symbol"] = "XAU/USD"
    seed["interval"] = "1min"
    seed["timezone"] = "America/New_York"
    seed["accepted_source_time"] = "16:59:00"
    seed["stored_semantic"] = "17:00 ET"
    seed["evidence_class"] = "HISTORICAL_REPLAY_RECONSTRUCTION"
    seed["prospective_claim"] = "False"
    seed["source_input"] = "WP1_FULL_FORMATION_SEED_MISSING_DATE"

    src["trade_date"] = src["trade_date"].dt.strftime("%Y-%m-%d")
    all_cols = list(dict.fromkeys(list(src.columns) + list(seed.columns)))
    out = pd.concat([src.reindex(columns=all_cols), seed.reindex(columns=all_cols)], ignore_index=True)
    out = out.sort_values("trade_date").reset_index(drop=True)
    if len(out) != len(expected) or out["trade_date"].iloc[0] != START.date().isoformat() or out["trade_date"].iloc[-1] != END.date().isoformat():
        raise RuntimeError("FULL_FORMATION_CALENDAR_COVERAGE_FAIL")
    if out["trade_date"].duplicated().any():
        raise RuntimeError("FULL_FORMATION_DUPLICATE_AFTER_SEED")

    counts = out["acquisition_status"].value_counts().to_dict()
    summary = {
        "audit_id": "GC_BREAK_WP1_FULL_FORMATION_SEED_V1",
        "calendar_start": START.date().isoformat(),
        "calendar_end": END.date().isoformat(),
        "calendar_rows": int(len(out)),
        "prior_artifact_rows": int(len(src)),
        "new_unresolved_seed_rows": int(len(seed)),
        "new_unresolved_seed_min": None if seed.empty else str(seed["trade_date"].min()),
        "new_unresolved_seed_max": None if seed.empty else str(seed["trade_date"].max()),
        "status_counts": {str(k): int(v) for k, v in counts.items()},
        "final_status_rows": int(out["acquisition_status"].isin(FINAL_STATUSES).sum()),
        "unresolved_rows": int((~out["acquisition_status"].isin(FINAL_STATUSES)).sum()),
        "source_semantic": "Twelve Data XAU/USD 1min exact 16:59:00 America/New_York; no fallback/interpolation",
        "production_database_write": "NONE",
        "performance_scoring": False,
        "prospective_claim": False,
    }
    out.to_csv(a.output_dir / "gc_break_wp1_full_formation_seed_v1.csv", index=False)
    (a.output_dir / "gc_break_wp1_full_formation_seed_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
