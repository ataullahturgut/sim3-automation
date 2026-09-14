from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

ROOT = Path(__file__).resolve().parents[1]
SERIES = [
    "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "MACRO_EVENT_V3_INFLATION_SCORE",
    "MACRO_EVENT_V3_FOMC_SCORE",
]
STRONG_STATES = {"GOLD_ADVERSE_MACRO_SHOCK", "GOLD_SUPPORTIVE_MACRO_SHOCK"}
MARKET_SHOCK_AVAILABLE = "AVAILABLE"
MARKET_SHOCK_NOT_TESTABLE = "NOT_TESTABLE_DEPENDENCY_MISSING"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fetch_df(conn, sql: str, params=()) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])


def load_neon() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    db = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not db:
        raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
        batch = fetch_df(conn, """
            SELECT batch_id, series_id, interval, first_ts, last_ts, retrieved_at,
                   provider, symbol, evidence_class, purpose, row_count, inserted_count,
                   payload_sha256, code_sha, status
            FROM xau_intraday_research_cache_batches
            WHERE interval='5min'
            ORDER BY batch_id DESC LIMIT 1
        """)
        raw = fetch_df(conn, """
            SELECT observation_ts AS ts, close
            FROM xau_intraday_research_cache_5m
            WHERE observation_ts >= '2020-04-06 00:00:00+00'
              AND observation_ts <  '2025-01-01 00:00:00+00'
            ORDER BY observation_ts
        """)
        macro = fetch_df(conn, """
            SELECT series_id, observation_ts, value, available_as_of, first_seen_at,
                   retrieved_at, quality_status, metadata
            FROM observations
            WHERE series_id = ANY(%s)
              AND observation_ts >= '2022-01-01 00:00:00+00'
              AND observation_ts <  '2025-01-01 00:00:00+00'
            ORDER BY observation_ts, series_id
        """, (SERIES,))
    if len(batch) != 1 or raw.empty or macro.empty:
        raise RuntimeError(f"FORMATION_EVENT_INPUT_MISSING:{len(batch)}:{len(raw)}:{len(macro)}")
    raw["ts"] = pd.to_datetime(raw["ts"], utc=True)
    raw["close"] = pd.to_numeric(raw["close"], errors="raise")
    macro["observation_ts"] = pd.to_datetime(macro["observation_ts"], utc=True)
    macro["score"] = pd.to_numeric(macro["value"], errors="raise")
    macro["state"] = macro["metadata"].map(lambda x: (x or {}).get("state"))
    macro["family"] = macro["metadata"].map(lambda x: (x or {}).get("family"))
    lineage = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in batch.iloc[0].to_dict().items()}
    return raw, macro, lineage


def empty_shock_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=["ts", "shock_sig", "shock_direction", "shock_state"])


def score_market_shock(raw: pd.DataFrame) -> tuple[pd.DataFrame, list[dict], str]:
    v3_path = ROOT / "tools" / "market_shock_challenger_v3.py"
    v2_path = ROOT / "tools" / "market_shock_challenger_v2.py"
    if not v3_path.exists() or not v2_path.exists():
        report = {
            "status": MARKET_SHOCK_NOT_TESTABLE,
            "reason": "MARKET_SHOCK_SHARED_DEPENDENCY_MISSING",
            "v3_present": bool(v3_path.exists()),
            "v2_present": bool(v2_path.exists()),
            "production_database_write": "NONE",
            "prospective_claim": False,
        }
        return empty_shock_frame(), [report], MARKET_SHOCK_NOT_TESTABLE

    ms = load_module(v3_path, "gc_break_wp1_market_shock_v3")
    data = ms.build_returns(raw)
    segments, reports = [], []
    for year in (2022, 2023, 2024):
        cutoff = pd.Timestamp(f"{year}-01-01", tz="UTC")
        train = data[data["ts"] < cutoff].copy()
        if len(train) < 100000:
            raise RuntimeError(f"MARKET_SHOCK_TRAIN_TOO_SMALL:{year}:{len(train)}")
        periodicity = ms.fit_periodicity(train)
        train_scored = ms.add_scores(train, periodicity)
        evt30 = ms.fit_evt(train_scored["score30"])
        rep, seg, _ = ms.score_segment(data, year, periodicity, evt30)
        reports.append(rep)
        segments.append(seg)
    return pd.concat(segments, ignore_index=True).sort_values("ts").reset_index(drop=True), reports, MARKET_SHOCK_AVAILABLE


def first_shock(seg: pd.DataFrame, t: pd.Timestamp, minutes: int = 10):
    if seg.empty:
        return None
    w = seg[(seg["ts"] >= t) & (seg["ts"] <= t + pd.Timedelta(minutes=minutes)) & seg["shock_sig"].fillna(False)]
    return None if w.empty else w.sort_values("ts").iloc[0]


def build_event_rows(macro: pd.DataFrame, shock: pd.DataFrame, shock_status: str) -> pd.DataFrame:
    strong = macro[macro["state"].isin(STRONG_STATES)].copy()
    strong["macro_direction"] = np.sign(strong["score"]).astype(int)
    strong = strong[strong["macro_direction"].ne(0)]
    rows = []
    for _, ev in strong.iterrows():
        t = pd.Timestamp(ev["observation_ts"])
        match = first_shock(shock, t, 10) if shock_status == MARKET_SHOCK_AVAILABLE else None
        present = match is not None
        shock_dir = int(np.sign(float(match["shock_direction"]))) if present else None
        local = t.tz_convert("America/New_York")
        rows.append({
            "series_id": ev["series_id"], "family": ev["family"], "release_ts": t,
            "release_date_ny": pd.Timestamp(local.date()), "macro_score": float(ev["score"]),
            "macro_state": ev["state"], "macro_direction": int(ev["macro_direction"]),
            "market_shock_context_status": shock_status,
            "market_shock_present_0_10m": present if shock_status == MARKET_SHOCK_AVAILABLE else np.nan,
            "market_shock_ts": pd.Timestamp(match["ts"]) if present else pd.NaT,
            "market_shock_state": str(match["shock_state"]) if present else None,
            "market_shock_direction": shock_dir,
            "direction_concordant": bool(present and shock_dir == int(ev["macro_direction"])) if shock_status == MARKET_SHOCK_AVAILABLE else np.nan,
            "available_as_of": ev["available_as_of"], "first_seen_at": ev["first_seen_at"],
            "retrieved_at": ev["retrieved_at"], "quality_status": ev["quality_status"],
        })
    return pd.DataFrame(rows)


def map_to_panel(panel: pd.DataFrame, events: pd.DataFrame, shock_status: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = panel.sort_values("date").reset_index(drop=True).copy()
    p["date"] = pd.to_datetime(p["date"]).dt.normalize()
    p["macro_strong_event_count"] = 0
    p["macro_adverse_event_count"] = 0
    p["market_shock_context_status"] = shock_status
    if shock_status == MARKET_SHOCK_AVAILABLE:
        p["market_shock_event_count"] = 0.0
        p["market_shock_concordant_event_count"] = 0.0
    else:
        p["market_shock_event_count"] = np.nan
        p["market_shock_concordant_event_count"] = np.nan
    dates = p["date"].to_numpy(dtype="datetime64[ns]")
    mapped = []
    for _, ev in events.iterrows():
        release_date = pd.Timestamp(ev["release_date_ny"]).normalize()
        pos = int(np.searchsorted(dates, np.datetime64(release_date), side="left"))
        if pos >= len(p):
            continue
        p.loc[pos, "macro_strong_event_count"] += 1
        p.loc[pos, "macro_adverse_event_count"] += int(ev["macro_state"] == "GOLD_ADVERSE_MACRO_SHOCK")
        if shock_status == MARKET_SHOCK_AVAILABLE:
            p.loc[pos, "market_shock_event_count"] += int(bool(ev["market_shock_present_0_10m"]))
            p.loc[pos, "market_shock_concordant_event_count"] += int(bool(ev["direction_concordant"]))
        row = ev.to_dict()
        row["mapped_origin_date"] = pd.Timestamp(p.loc[pos, "date"])
        mapped.append(row)
    return p, pd.DataFrame(mapped)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--panel", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(args.panel, parse_dates=["date"])
    raw, macro, lineage = load_neon()
    shock, shock_reports, shock_status = score_market_shock(raw)
    event_rows = build_event_rows(macro, shock, shock_status)
    augmented, mapped = map_to_panel(panel, event_rows, shock_status)
    event_rows.to_csv(args.output_dir / "gc_break_wp1_formation_strong_macro_events.csv", index=False)
    mapped.to_csv(args.output_dir / "gc_break_wp1_formation_mapped_event_shocks.csv", index=False)
    augmented.to_csv(args.output_dir / "gc_break_wp1_formation_panel_with_event_context.csv", index=False)

    if shock_status == MARKET_SHOCK_AVAILABLE:
        overlap = int(event_rows["market_shock_present_0_10m"].fillna(False).sum()) if len(event_rows) else 0
        concordant = int(event_rows["direction_concordant"].fillna(False).sum()) if len(event_rows) else 0
    else:
        overlap = None
        concordant = None

    summary = {
        "audit_id": "GC_BREAK_WP1_FORMATION_EVENT_CONTEXT_V1",
        "role": "Macro Event = event hazard context; Market Shock V3 = realized shock confirmation/intensity context",
        "formation_years": [2022, 2023, 2024],
        "xau_5m_rows": int(len(raw)),
        "macro_rows": int(len(macro)),
        "strong_macro_events": int(len(event_rows)),
        "mapped_strong_events": int(len(mapped)),
        "market_shock_context_status": shock_status,
        "market_shock_overlap_0_10m": overlap,
        "direction_concordant": concordant,
        "cache_lineage": lineage,
        "market_shock_segment_reports": shock_reports,
        "neon_access": "READ_ONLY_TRANSACTION",
        "production_database_write": "NONE",
        "prospective_claim": False,
        "interpretation_lock": "No warning score or threshold is selected here; missing Market Shock reconstruction remains explicit NOT_TESTABLE and is never converted to a zero-signal claim."
    }
    (args.output_dir / "gc_break_wp1_formation_event_context_v1_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True, default=str, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
