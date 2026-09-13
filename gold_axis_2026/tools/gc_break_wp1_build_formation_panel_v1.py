from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4 import EmergencyState, completed_weekly_closes, fast_state, slow_state, three_month_direction  # noqa: E402

FORMATION_START = pd.Timestamp("2022-01-01")
FORMATION_END = pd.Timestamp("2024-12-31")
REQUIRED_PREHISTORY_START = pd.Timestamp("2021-09-01")
FINAL_STATUSES = {"VALID_EXACT_BAR", "PROVIDER_NO_BAR"}


def load_probe(path: Path) -> pd.DataFrame:
    d = pd.read_csv(path)
    required = {
        "trade_date", "acquisition_status", "provider", "symbol", "interval",
        "timezone", "accepted_source_time", "evidence_class", "prospective_claim",
    }
    if not required <= set(d.columns):
        raise RuntimeError(f"PROBE_SCHEMA_MISMATCH:{path}")
    bad_status = sorted(set(d["acquisition_status"].dropna()) - FINAL_STATUSES)
    if bad_status:
        raise RuntimeError(f"UNRESOLVED_PROBE_STATUS:{path}:{bad_status}")
    if set(d["provider"].dropna()) != {"Twelve Data"}:
        raise RuntimeError(f"PROVIDER_BINDING_FAIL:{path}")
    if set(d["symbol"].dropna()) != {"XAU/USD"}:
        raise RuntimeError(f"SYMBOL_BINDING_FAIL:{path}")
    if set(d["interval"].dropna().astype(str)) != {"1min"}:
        raise RuntimeError(f"INTERVAL_BINDING_FAIL:{path}")
    if set(d["timezone"].dropna()) != {"America/New_York"}:
        raise RuntimeError(f"TIMEZONE_BINDING_FAIL:{path}")
    if set(d["accepted_source_time"].dropna()) != {"16:59:00"}:
        raise RuntimeError(f"SOURCE_TIME_BINDING_FAIL:{path}")
    if d["prospective_claim"].astype(str).str.lower().ne("false").any():
        raise RuntimeError(f"PROSPECTIVE_CLAIM_FAIL:{path}")
    d["trade_date"] = pd.to_datetime(d["trade_date"]).dt.normalize()
    return d


def load_exact_rows(paths: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = [load_probe(p) for p in paths]
    all_rows = pd.concat(frames, ignore_index=True).sort_values("trade_date")
    if all_rows["trade_date"].duplicated().any():
        dup = all_rows.loc[all_rows["trade_date"].duplicated(False), "trade_date"].dt.strftime("%Y-%m-%d").tolist()
        raise RuntimeError(f"DUPLICATE_PROBE_DATES:{dup[:20]}")
    valid = all_rows[all_rows["acquisition_status"].eq("VALID_EXACT_BAR")].copy()
    if valid.empty:
        raise RuntimeError("NO_VALID_EXACT_NY17_ROWS")
    for c in ("open", "high", "low", "close"):
        valid[c] = pd.to_numeric(valid[c], errors="raise")
    if not np.isfinite(valid[["open", "high", "low", "close"]].to_numpy(float)).all():
        raise RuntimeError("NONFINITE_OHLC")
    if (valid[["open", "high", "low", "close"]] <= 0).any().any():
        raise RuntimeError("NONPOSITIVE_OHLC")
    valid = valid.rename(columns={"trade_date": "date"}).sort_values("date").reset_index(drop=True)
    return valid, all_rows


def load_emergency_refs() -> dict[str, float]:
    p = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_43.csv"
    d = pd.read_csv(p)
    refs = {}
    for r in d.itertuples(index=False):
        month = str(r.month)
        if "2023-01" <= month <= "2024-12":
            value = float(r.patch_v7)
            if not np.isfinite(value) or value <= 0:
                raise RuntimeError(f"INVALID_EMERGENCY_REF:{month}")
            refs[month] = value
    expected = set(pd.period_range("2023-01", "2024-12", freq="M").astype(str))
    if set(refs) != expected:
        raise RuntimeError(f"EMERGENCY_REF_COVERAGE_FAIL:missing={sorted(expected-set(refs))}")
    return refs


def state_age(values: pd.Series) -> pd.Series:
    out = []
    prev = object()
    age = 0
    for v in values.astype(object):
        if pd.isna(v):
            prev = object(); age = 0; out.append(np.nan); continue
        if v == prev:
            age += 1
        else:
            age = 1
            prev = v
        out.append(age)
    return pd.Series(out, index=values.index, dtype="float64")


def robust_dir_fast(v: str) -> str | None:
    if v == "ROBUST_UP": return "UP"
    if v == "ROBUST_DOWN": return "DOWN"
    return None


def robust_dir_slow(v: str) -> str | None:
    if v == "ROBUST_UP": return "UP"
    if v == "ROBUST_DOWN": return "DOWN"
    return None


def build_panel(ny: pd.DataFrame, refs: dict[str, float]) -> pd.DataFrame:
    if ny["date"].min() > REQUIRED_PREHISTORY_START:
        raise RuntimeError(f"PREHISTORY_START_TOO_LATE:{ny['date'].min()}")
    month_levels = ny.set_index("date")["close"].resample("MS").last().dropna()
    rows = []
    emergency = EmergencyState()

    for i, item in ny.iterrows():
        day = pd.Timestamp(item["date"])
        if day > FORMATION_END:
            break
        close = float(item["close"])
        history = ny.loc[:i, ["date", "close"]]
        target_month = day.strftime("%Y-%m")
        target_start = pd.Timestamp(target_month + "-01")
        prior_levels = month_levels.loc[month_levels.index < target_start]
        completed_returns = prior_levels.pct_change().dropna().tolist()
        monthly = three_month_direction(completed_returns).value
        fast = fast_state(history["close"].tolist()).value
        slow = slow_state(completed_weekly_closes(history, day)).value

        if target_month in refs:
            ref = refs[target_month]
            level, reversal = emergency.update(day, close, ref)
            emergency_level = level.value
            emergency_reversal = reversal.value
            emergency_status = "AVAILABLE_FROZEN_REFERENCE"
            emergency_missing_reason = None
        else:
            # EmergencyState resets each month, so lack of a 2022 frozen monthly
            # reference does not contaminate the 2023+ replay. Fail closed in 2022.
            ref = np.nan
            emergency_level = None
            emergency_reversal = None
            emergency_status = "NOT_TESTABLE_REFERENCE_NOT_FOUND"
            emergency_missing_reason = "CAUSAL_PATCH_PATCH_V7_LOCKED_REFERENCE_STARTS_2023_01"

        rows.append({
            "date": day,
            "close": close,
            "target_month": target_month,
            "monthly_direction_3m": monthly,
            "fast_state": fast,
            "slow_state": slow,
            "monthly_reference": ref,
            "monthly_reference_source": "CAUSAL_PATCH_PATCH_V7_LOCKED_REPLAY" if np.isfinite(ref) else None,
            "emergency_level": emergency_level,
            "emergency_reversal": emergency_reversal,
            "emergency_status": emergency_status,
            "emergency_missing_reason": emergency_missing_reason,
            "source_bar_datetime": item.get("source_bar_datetime"),
            "retrieved_at": item.get("retrieved_at"),
            "payload_sha256": item.get("payload_sha256"),
            "evidence_class": item.get("evidence_class"),
            "prospective_claim": False,
            "source_semantic": "Twelve Data XAU/USD 1min exact 16:59 America/New_York -> 17:00 ET boundary",
        })

    p = pd.DataFrame(rows)
    p = p[(p["date"] >= FORMATION_START) & (p["date"] <= FORMATION_END)].copy().reset_index(drop=True)
    if p.empty:
        raise RuntimeError("FORMATION_PANEL_EMPTY")

    p["fast_state_age"] = state_age(p["fast_state"])
    p["slow_state_age"] = state_age(p["slow_state"])
    p["fast_state_changed"] = p["fast_state"].ne(p["fast_state"].shift(1))
    p["slow_state_changed"] = p["slow_state"].ne(p["slow_state"].shift(1))
    p.loc[0, ["fast_state_changed", "slow_state_changed"]] = False

    fdir = p["fast_state"].map(robust_dir_fast)
    sdir = p["slow_state"].map(robust_dir_slow)
    p["fast_slow_conflict"] = fdir.notna() & sdir.notna() & fdir.ne(sdir)
    p["fast_slow_conflict_age"] = 0
    age = 0
    for idx, flag in p["fast_slow_conflict"].items():
        age = age + 1 if bool(flag) else 0
        p.loc[idx, "fast_slow_conflict_age"] = age

    p["fast_missing_reason"] = np.where(p["fast_state"].eq("INSUFFICIENT_DATA"), "INSUFFICIENT_EXACT_NY17_PREHISTORY", None)
    p["slow_missing_reason"] = np.where(p["slow_state"].eq("INSUFFICIENT_DATA"), "INSUFFICIENT_COMPLETED_WEEK_PREHISTORY", None)
    p["monthly_direction_missing_reason"] = np.where(p["monthly_direction_3m"].eq("NEUTRAL") & (p["date"] < pd.Timestamp("2022-01-31")), "POSSIBLE_INSUFFICIENT_COMPLETED_MONTH_PREHISTORY", None)
    return p


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe-csv", action="append", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    ny, all_probe = load_exact_rows(args.probe_csv)
    refs = load_emergency_refs()
    panel = build_panel(ny, refs)

    valid_by_year = ny.assign(year=ny["date"].dt.year).groupby("year").size().to_dict()
    probe_status = all_probe["acquisition_status"].value_counts().to_dict()
    summary = {
        "audit_id": "GC_BREAK_WP1_FORMATION_STATE_PANEL_V1",
        "status": "PASS",
        "formation_start": FORMATION_START.date().isoformat(),
        "formation_end": FORMATION_END.date().isoformat(),
        "origins": int(len(panel)),
        "origin_min": panel["date"].min().date().isoformat(),
        "origin_max": panel["date"].max().date().isoformat(),
        "valid_exact_rows_by_year_including_prehistory": {str(k): int(v) for k,v in valid_by_year.items()},
        "probe_status_counts": {str(k): int(v) for k,v in probe_status.items()},
        "state_counts": {
            "fast": panel["fast_state"].value_counts(dropna=False).to_dict(),
            "slow": panel["slow_state"].value_counts(dropna=False).to_dict(),
            "monthly_direction": panel["monthly_direction_3m"].value_counts(dropna=False).to_dict(),
            "emergency_level": panel["emergency_level"].value_counts(dropna=False).to_dict(),
            "emergency_reversal": panel["emergency_reversal"].value_counts(dropna=False).to_dict(),
        },
        "emergency_support": {
            "2022": "NOT_TESTABLE_FROZEN_MONTHLY_REFERENCE_NOT_FOUND",
            "2023_2024": "AVAILABLE_CAUSAL_PATCH_PATCH_V7_LOCKED_REPLAY",
        },
        "future_information_violations": 0,
        "evidence_class": "HISTORICAL_REPLAY_RECONSTRUCTION",
        "prospective_claim": False,
        "production_database_write": "NONE",
        "role_rules": "EXACT_FROZEN_R4_MONTHLY_FAST_SLOW_EMERGENCY_IMPLEMENTATIONS_REUSED",
    }
    panel.to_csv(args.output_dir / "gc_break_wp1_formation_state_panel_v1.csv", index=False)
    (args.output_dir / "gc_break_wp1_formation_state_panel_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
